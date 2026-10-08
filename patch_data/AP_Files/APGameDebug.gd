extends Node

# Gameplay-side debugger for Luck be a Landlord.
# This complements APClient.gd:
#   APClient.gd     = Archipelago/network packets
#   APGameDebug.gd  = what the GAME is doing
#
# Everything writes into the same user://LBAL-AP-Debug.log file, so the
# detachable PowerShell console can show network + gameplay activity together.

const APData = preload("res://APData.gd")

const POLL_INTERVAL = 0.08
# Keep gameplay tracing enabled. APClient batches file writes so detailed spin
# logging stays available without reopening the debug log for every event.
const VERBOSE_GAMEPLAY_DEBUG = true

var main = null
var ap_client = null
var popup = null
var reels = null
var items_node = null
var coins_node = null

var event_sequence = 0
var spin_sequence = 0
var poll_timer = 0.0

var last_spinning = false
var last_floor = -999999
var last_payments_paid = -999999
var last_game_spin_count = -999999
var last_menu_path = "__unset__"
var last_symbol_counts = {}
var last_item_counts = {}
var last_coin_total = null
var initial_snapshot_done = false

func _ready():
	if not VERBOSE_GAMEPLAY_DEBUG:
		set_process(false)
		set_process_input(false)
		return
	set_process(true)
	set_process_input(true)
	call_deferred("_bind_nodes")

func _bind_nodes():
	main = get_node_or_null("/root/Main")
	if main == null:
		return

	ap_client = main.get_node_or_null("AP Client")
	popup = main.get_node_or_null("Pop-up Sprite/Pop-up")
	reels = main.get_node_or_null("Reels")
	items_node = main.get_node_or_null("Items")
	coins_node = main.get_node_or_null("Coins")

	_log("TRACE READY", "node_id=" + str(get_instance_id()) + " path=" + str(get_path()))
	_log("TRACE MAP", "AP item_names=" + str(APData.ITEM_NAME_TO_ID.size()) + " AP locations=" + str(APData.LOCATION_NAME_TO_ID.size()))
	dump_snapshot("ready")

func _process(delta):
	if main == null or not is_instance_valid(main):
		_bind_nodes()
		return

	poll_timer += delta
	if poll_timer < POLL_INTERVAL:
		return
	poll_timer = 0.0

	_watch_menu()
	_watch_floor()
	_watch_payment()
	_watch_spin()
	_watch_symbol_inventory()
	_watch_item_inventory()
	_watch_coin_total()

func _input(event):
	# TT Button activations are logged separately at the point where the game
	# actually calls the button's target. This is only a raw input breadcrumb.
	if event is InputEventMouseButton and event.is_pressed():
		var selected = _selected_node_text()
		_log(
			"MOUSE",
			"button=" + str(event.button_index)
			+ " pos=" + str(event.position)
			+ " menu=" + _menu_path()
			+ " selected=" + selected
			+ " " + _context_ids()
		)

func log_button_activation(button):
	if not VERBOSE_GAMEPLAY_DEBUG:
		return
	if button == null or not is_instance_valid(button):
		return

	var target = button.get("target")
	var call_name = str(button.get("call"))
	var args = button.get("args")
	var button_text = str(button.get("button_text"))
	var saved_raw = str(button.get("saved_raw_string"))
	var target_path = "<null>"
	var target_id = -1
	if target != null and is_instance_valid(target):
		target_id = int(target.get_instance_id())
		if target is Node:
			target_path = str(target.get_path())

	var details = "button_node_id=" + str(button.get_instance_id())
	details += " button_path=" + str(button.get_path())
	details += " text=" + _q(button_text)
	if saved_raw != "" and saved_raw != button_text:
		details += " raw=" + _q(saved_raw)
	details += " target_node_id=" + str(target_id)
	details += " target_path=" + target_path
	details += " call=" + call_name
	details += " args=" + str(args)
	details += " " + _context_ids()

	# If a button argument looks like a symbol/item/essence game key, show both
	# its AP unlock item ID and its "Send: ..." AP location ID.
	if typeof(args) == TYPE_ARRAY:
		for value in args:
			if typeof(value) == TYPE_STRING:
				var ap_item_id = _ap_item_id_for_game_type(value)
				var send_location_id = APData.first_send_location_id_for_game_type(value)
				if ap_item_id >= 0 or send_location_id >= 0:
					details += " arg_game_type=" + str(value)
					details += " arg_ap_item_id=" + str(ap_item_id)
					if ap_item_id >= 0:
						details += " arg_ap_item_name=" + _q(APData.item_name(ap_item_id))
					details += " arg_send_location_id=" + str(send_location_id)
					if send_location_id >= 0:
						details += " arg_send_location_name=" + _q(APData.location_name(send_location_id))

	_log("CLICK", details)

func log_game_log(message):
	if not VERBOSE_GAMEPLAY_DEBUG:
		return
	# Forward LBAL's own very detailed run log. The base game already records
	# spin layouts, item changes, coin totals, destroyed symbols, etc.
	_log("LBAL LOG", _context_ids() + " :: " + str(message))

func log_game_error(message):
	if not VERBOSE_GAMEPLAY_DEBUG:
		return
	_log("LBAL ERROR", _context_ids() + " :: " + str(message))

func dump_snapshot(reason = "manual"):
	if not VERBOSE_GAMEPLAY_DEBUG:
		return
	if main == null or not is_instance_valid(main):
		_bind_nodes()
	if main == null:
		return

	_log("SNAPSHOT", "reason=" + str(reason) + " " + _context_ids() + " menu=" + _menu_path() + " coins=" + str(_coin_total()))
	_log_symbol_inventory_snapshot(reason)
	_log_item_inventory_snapshot(reason)
	_log_displayed_symbols("snapshot:" + str(reason))

func _watch_menu():
	var value = _menu_path()
	if value != last_menu_path:
		var old = last_menu_path
		last_menu_path = value
		_log("MENU", "from=" + old + " to=" + value + " " + _context_ids())

func _watch_floor():
	if popup == null or not is_instance_valid(popup):
		return
	var floor_num = int(popup.current_floor)
	if floor_num == last_floor:
		return
	var old = last_floor
	last_floor = floor_num
	var floor_ap_item_id = APData.floor_unlock_item_id(floor_num)
	var details = "from=" + str(old) + " to=" + str(floor_num)
	details += " floor_id=" + str(floor_num)
	details += " floor_unlock_ap_item_id=" + str(floor_ap_item_id)
	if floor_ap_item_id >= 0:
		details += " floor_unlock_ap_item_name=" + _q(APData.item_name(floor_ap_item_id))
	details += " payments_paid=" + str(_payments_paid())
	details += " next_payment_location_id=" + str(_next_payment_location_id())
	_log("FLOOR", details)

func _watch_payment():
	if popup == null or not is_instance_valid(popup):
		return
	var paid = _payments_paid()
	if paid == last_payments_paid:
		return
	var old = last_payments_paid
	last_payments_paid = paid
	var next_payment = paid + 1
	var next_location_id = APData.payment_location_id(_floor_num(), next_payment)
	var completed_location_id = APData.payment_location_id(_floor_num(), paid)

	var details = "from_paid=" + str(old) + " to_paid=" + str(paid)
	details += " floor_id=" + str(_floor_num())
	details += " completed_payment=" + str(paid)
	details += " completed_location_id=" + str(completed_location_id)
	if completed_location_id >= 0:
		details += " completed_location_name=" + _q(APData.location_name(completed_location_id))
	details += " next_payment=" + str(next_payment)
	details += " next_location_id=" + str(next_location_id)
	if next_location_id >= 0:
		details += " next_location_name=" + _q(APData.location_name(next_location_id))
	if popup.get("rent_values") != null:
		details += " rent_values=" + str(popup.rent_values)
	_log("PAYMENT", details)

func _watch_spin():
	if reels == null or not is_instance_valid(reels):
		return

	var game_spin_count = _game_spin_count()
	if game_spin_count != last_game_spin_count:
		last_game_spin_count = game_spin_count
		_log("SPIN COUNTER", "game_spin=" + str(game_spin_count) + " " + _context_ids())

	var spinning_now = bool(reels.spinning)
	if spinning_now == last_spinning:
		return

	last_spinning = spinning_now
	if spinning_now:
		spin_sequence += 1
		_log(
			"SPIN START",
			"spin_id=" + str(spin_sequence)
			+ " game_spin=" + str(game_spin_count)
			+ " " + _context_ids()
			+ " coins_before=" + str(_coin_total())
		)
	else:
		var finished_spin = spin_sequence
		_log(
			"SPIN STOP",
			"spin_id=" + str(finished_spin)
			+ " game_spin=" + str(game_spin_count)
			+ " " + _context_ids()
			+ " coins_now=" + str(_coin_total())
		)
		call_deferred("_log_spin_result_deferred", finished_spin, game_spin_count)

func _log_spin_result_deferred(spin_id, game_spin_count):
	if reels == null or not is_instance_valid(reels):
		return

	var displayed = reels.get("displayed_icons")
	if typeof(displayed) != TYPE_ARRAY:
		_log("SPIN RESULT", "spin_id=" + str(spin_id) + " displayed_icons=<not array>")
		return

	var summary = []
	var symbol_count = 0
	for y in range(displayed.size()):
		var row = displayed[y]
		if typeof(row) != TYPE_ARRAY:
			continue
		for x in range(row.size()):
			var icon = row[x]
			if icon == null or not is_instance_valid(icon):
				continue
			symbol_count += 1
			var game_type = _game_type(icon)
			var ap_item_id = _ap_item_id_for_game_type(game_type)
			var send_location_id = APData.first_send_location_id_for_game_type(game_type)
			var rarity = str(icon.get("rarity"))
			var value = str(icon.get("value"))
			var grid_pos = icon.get("grid_position")

			var details = "spin_id=" + str(spin_id)
			details += " game_spin=" + str(game_spin_count)
			details += " reel=" + str(x) + " row=" + str(y)
			details += " grid_id=" + str(x) + "," + str(y)
			details += " symbol_node_id=" + str(icon.get_instance_id())
			details += " symbol_path=" + str(icon.get_path())
			details += " game_type=" + game_type
			details += " ap_item_id=" + str(ap_item_id)
			if ap_item_id >= 0:
				details += " ap_item_name=" + _q(APData.item_name(ap_item_id))
			details += " send_location_id=" + str(send_location_id)
			if send_location_id >= 0:
				details += " send_location_name=" + _q(APData.location_name(send_location_id))
			details += " rarity=" + rarity + " value=" + value + " grid_position=" + str(grid_pos)
			_log("SPIN SYMBOL", details)
			summary.append(game_type + "[APItem=" + str(ap_item_id) + ",SendLoc=" + str(send_location_id) + "]")

	_log(
		"SPIN RESULT",
		"spin_id=" + str(spin_id)
		+ " game_spin=" + str(game_spin_count)
		+ " symbol_count=" + str(symbol_count)
		+ " " + _context_ids()
		+ " symbols=" + str(summary)
	)

func _watch_symbol_inventory():
	if reels == null or not is_instance_valid(reels):
		return
	var current = _symbol_counts()

	# Recovery path for the base Matryoshka Send check.  If any Matryoshka stage
	# is already present while location 465 is still missing, send the base check.
	# This also repairs an in-progress run made with an older build where the
	# reward-card pickup callback was missed.
	if ap_client != null and ap_client.get("missing_locations") != null and ap_client.missing_locations.has(465):
		for current_key in current.keys():
			if int(current.get(current_key, 0)) <= 0:
				continue
			if APData.normalise_game_key(current_key) != "matryoshka_doll":
				continue
			var recovery_hooks = get_node_or_null("/root/Main/AP Hooks")
			if recovery_hooks != null and recovery_hooks.has_method("send_matryoshka_base_check"):
				recovery_hooks.send_matryoshka_base_check(current_key)
			break

	if last_symbol_counts.size() == 0:
		last_symbol_counts = current.duplicate(true)
		return

	var keys = []
	for key in last_symbol_counts.keys():
		if not keys.has(key):
			keys.append(key)
	for key in current.keys():
		if not keys.has(key):
			keys.append(key)

	for key in keys:
		var before = int(last_symbol_counts.get(key, 0))
		var after = int(current.get(key, 0))
		if before == after:
			continue
		var delta = after - before
		var ap_item_id = _ap_item_id_for_game_type(key)
		var send_location_id = APData.first_send_location_id_for_game_type(key)
		var details = "game_type=" + str(key)
		details += " before=" + str(before) + " after=" + str(after) + " delta=" + str(delta)
		details += " ap_item_id=" + str(ap_item_id)
		if ap_item_id >= 0:
			details += " ap_item_name=" + _q(APData.item_name(ap_item_id))
		details += " send_location_id=" + str(send_location_id)
		if send_location_id >= 0:
			details += " send_location_name=" + _q(APData.location_name(send_location_id))
		details += " " + _context_ids()
		if delta > 0:
			_log("SYMBOL ADD", details)
			# Backup for Matryoshka progression. The normal hook fires directly from
			# Slot Icon at the transform threshold; this inventory transition catches
			# the same event if LBAL's effect timing bypasses that callback. The AP
			# client immediately marks queued IDs checked, so this cannot double-send.
			var matryoshka_hooks = get_node_or_null("/root/Main/AP Hooks")
			if matryoshka_hooks != null:
				if matryoshka_hooks.has_method("send_matryoshka_base_check") and APData.normalise_game_key(key) == "matryoshka_doll":
					matryoshka_hooks.send_matryoshka_base_check(key)
				if matryoshka_hooks.has_method("send_matryoshka_transition"):
					match APData.exact_game_key(key):
						"matryoshka_doll_2":
							matryoshka_hooks.send_matryoshka_transition("matryoshka_doll_1", "matryoshka_doll_2")
						"matryoshka_doll_3":
							matryoshka_hooks.send_matryoshka_transition("matryoshka_doll_2", "matryoshka_doll_3")
						"matryoshka_doll_4":
							matryoshka_hooks.send_matryoshka_transition("matryoshka_doll_3", "matryoshka_doll_4")
						"matryoshka_doll_5":
							matryoshka_hooks.send_matryoshka_transition("matryoshka_doll_4", "matryoshka_doll_5")
		else:
			_log("SYMBOL REMOVE", details)

	last_symbol_counts = current.duplicate(true)

func _watch_item_inventory():
	if items_node == null or not is_instance_valid(items_node):
		return
	var current = _item_counts()
	if last_item_counts.size() == 0:
		last_item_counts = current.duplicate(true)
		return

	var keys = []
	for key in last_item_counts.keys():
		if not keys.has(key):
			keys.append(key)
	for key in current.keys():
		if not keys.has(key):
			keys.append(key)

	for key in keys:
		var before = int(last_item_counts.get(key, 0))
		var after = int(current.get(key, 0))
		if before == after:
			continue

		var delta = after - before
		var ap_item_id = _ap_item_id_for_game_type(key)
		var send_location_id = APData.first_send_location_id_for_game_type(key)
		var kind = "ITEM"
		if str(key).ends_with("_essence"):
			kind = "ESSENCE"

		var details = "game_type=" + str(key)
		details += " before=" + str(before) + " after=" + str(after) + " delta=" + str(delta)
		details += " ap_item_id=" + str(ap_item_id)
		if ap_item_id >= 0:
			details += " ap_item_name=" + _q(APData.item_name(ap_item_id))
		details += " send_location_id=" + str(send_location_id)
		if send_location_id >= 0:
			details += " send_location_name=" + _q(APData.location_name(send_location_id))
		details += " " + _context_ids()

		if delta > 0:
			_log(kind + " ADD", details)
		else:
			_log(kind + " REMOVE", details)

	last_item_counts = current.duplicate(true)

func _watch_coin_total():
	var total = _coin_total()
	if total == null:
		return
	if last_coin_total == null:
		last_coin_total = total
		return
	if total != last_coin_total:
		# Coins animate/count, so keep this compact. The base-game LBAL LOG lines
		# still give the detailed cause and per-spin totals.
		_log("COINS", "from=" + str(last_coin_total) + " to=" + str(total) + " " + _context_ids())
		last_coin_total = total

func _log_symbol_inventory_snapshot(reason):
	var counts = _symbol_counts()
	_log("SYMBOL SNAPSHOT", "reason=" + str(reason) + " counts=" + str(counts))
	last_symbol_counts = counts.duplicate(true)

func _log_item_inventory_snapshot(reason):
	var counts = _item_counts()
	_log("ITEM SNAPSHOT", "reason=" + str(reason) + " counts=" + str(counts))
	last_item_counts = counts.duplicate(true)

func _log_displayed_symbols(reason):
	if reels == null or not is_instance_valid(reels):
		return
	var displayed = reels.get("displayed_icons")
	if typeof(displayed) != TYPE_ARRAY:
		return
	for y in range(displayed.size()):
		var row = displayed[y]
		if typeof(row) != TYPE_ARRAY:
			continue
		for x in range(row.size()):
			var icon = row[x]
			if icon == null or not is_instance_valid(icon):
				continue
			var game_type = _game_type(icon)
			var ap_item_id = _ap_item_id_for_game_type(game_type)
			var send_location_id = APData.first_send_location_id_for_game_type(game_type)
			_log(
				"DISPLAYED SYMBOL",
				"reason=" + str(reason)
				+ " reel=" + str(x) + " row=" + str(y)
				+ " symbol_node_id=" + str(icon.get_instance_id())
				+ " game_type=" + game_type
				+ " ap_item_id=" + str(ap_item_id)
				+ " send_location_id=" + str(send_location_id)
			)

func _symbol_counts():
	var counts = {}
	if reels == null or not is_instance_valid(reels):
		return counts
	var symbols = reels.get("symbol_arr")
	if typeof(symbols) != TYPE_ARRAY:
		return counts
	for symbol in symbols:
		var game_type = _game_type(symbol)
		if game_type == "" or game_type == "Null":
			continue
		counts[game_type] = int(counts.get(game_type, 0)) + 1
	return counts

func _item_counts():
	var counts = {}
	if items_node == null or not is_instance_valid(items_node):
		return counts
	var game_items = items_node.get("items")
	if typeof(game_items) != TYPE_ARRAY:
		return counts
	for item in game_items:
		if item == null or not is_instance_valid(item):
			continue
		var game_type = _game_type(item)
		if game_type == "" or game_type == "Null":
			continue
		var count = 1
		if item.get("item_count") != null:
			count = int(item.item_count)
		counts[game_type] = int(counts.get(game_type, 0)) + count
	return counts

func _ap_item_id_for_game_type(game_type):
	var direct = APData.first_item_id_for_game_type(game_type)
	if direct >= 0:
		return direct

	# Use LBAL's own display_name as a fallback for internal-name differences.
	var base_type = str(game_type)
	var steam_pos = base_type.find("_STEAM_ID_")
	if steam_pos != -1:
		base_type = base_type.substr(0, steam_pos)
	if base_type.ends_with("_d"):
		base_type = base_type.substr(0, base_type.length() - 2)

	if main != null and main.get("tile_database") != null and main.tile_database.has(base_type):
		var data = main.tile_database[base_type]
		if typeof(data) == TYPE_DICTIONARY and data.has("display_name"):
			var key = APData.normalise_game_key(str(data.display_name))
			var ids = APData.GAME_KEY_TO_ITEM_IDS.get(key, [])
			if ids.size() > 0:
				return int(ids[0])

	if main != null and main.get("item_database") != null and main.item_database.has(base_type):
		var data2 = main.item_database[base_type]
		if typeof(data2) == TYPE_DICTIONARY and data2.has("display_name"):
			var display_name = str(data2.display_name)
			if base_type.ends_with("_essence") and not display_name.to_lower().ends_with("essence"):
				display_name += " Essence"
			var key2 = APData.normalise_game_key(display_name)
			var ids2 = APData.GAME_KEY_TO_ITEM_IDS.get(key2, [])
			if ids2.size() > 0:
				return int(ids2[0])

	return -1

func _game_type(value):
	if value == null:
		return ""
	if typeof(value) == TYPE_STRING:
		return str(value)
	if typeof(value) == TYPE_OBJECT:
		var t = value.get("type")
		if t != null:
			return str(t)
	return str(value)

func _floor_num():
	if popup != null and is_instance_valid(popup):
		return int(popup.current_floor)
	return -1

func _payments_paid():
	if popup != null and is_instance_valid(popup):
		return int(popup.times_rent_paid)
	return -1

func _game_spin_count():
	if popup != null and is_instance_valid(popup):
		return int(popup.spins)
	return -1

func _next_payment_location_id():
	var paid = _payments_paid()
	if paid < 0:
		return -1
	return APData.payment_location_id(_floor_num(), paid + 1)

func _context_ids():
	var floor_num = _floor_num()
	var paid = _payments_paid()
	var next_payment = paid + 1
	var floor_unlock_id = APData.floor_unlock_item_id(floor_num)
	var next_location_id = APData.payment_location_id(floor_num, next_payment)
	var out = "floor_id=" + str(floor_num)
	out += " floor_unlock_ap_item_id=" + str(floor_unlock_id)
	out += " payments_paid=" + str(paid)
	out += " next_payment=" + str(next_payment)
	out += " next_payment_location_id=" + str(next_location_id)
	out += " game_spin=" + str(_game_spin_count())
	return out

func _coin_total():
	if coins_node == null or not is_instance_valid(coins_node):
		return null
	var base = coins_node.get("coins")
	if base == null:
		return null
	var total = int(base)
	var queued = coins_node.get("queued_increase")
	if queued != null:
		total += int(queued)
	if main != null:
		var sum_node = main.get_node_or_null("Sums/Coin Sum")
		if sum_node != null and sum_node.get("value") != null:
			total += int(sum_node.value)
	return total

func _menu_path():
	if main != null and main.get("current_menu_path") != null:
		return str(main.current_menu_path)
	return "<unknown>"

func _selected_node_text():
	if main == null:
		return "<none>"
	var selected = main.get("selected_node")
	if selected == null or not is_instance_valid(selected):
		return "<none>"
	if selected is Node:
		return str(selected.get_path()) + "#" + str(selected.get_instance_id())
	return str(selected)

func _q(value):
	return "\"" + str(value).replace("\"", "\\\"").replace("\n", "\\n") + "\""

func _log(kind, details):
	if not VERBOSE_GAMEPLAY_DEBUG:
		return
	event_sequence += 1
	var line = "GAME " + str(kind) + " event_id=" + str(event_sequence) + " " + str(details)
	if ap_client != null and is_instance_valid(ap_client) and ap_client.has_method("debug_log"):
		ap_client.debug_log(line)
	else:
		print("[AP GAME DEBUG] " + line)
