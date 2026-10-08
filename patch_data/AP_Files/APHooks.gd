extends Node

const APData = preload("res://APData.gd")
const APEffectData = preload("res://APEffectData.gd")

const AP_CHECK_TYPE = "ap_check"
const AP_CHECK_FIRST_LOCATION = 241
const AP_CHECK_LAST_LOCATION = 380
const AP_CHECK_RARITY = "common"
# Boost temporarily focuses each reward CATEGORY on currently in-logic unfinished
# Send/Effect checks, while leaving the five base starting symbols alone. Once a
# category is complete its full unlocked pool is restored. Keep only a modest AP
# Check weight so Common choices are not overwhelmed.
const AP_CHECK_BOOST_WEIGHT = 3

# These are LBAL's normal base starting symbols. They stay available even if
# their corresponding AP unlock item has not been received.
const BASE_STARTING_SYMBOLS = ["coin", "cherry", "pearl", "flower", "cat"]

var _pool_refresh_timer = 0.0
var _hook_bind_timer = 0.0
var _last_received_replay_count = -1
var _hooks_bound_logged = false
var _auto_hook_ready = false
var _ap_mode_active = false

# AP Check may exist more than once in the inventory, but only one Archipelago
# location is allowed to be sent per completed LBAL spin.
var _ap_check_last_sent_spin = -999999

# =============================================================================
# ARCHIPELAGO GAME HOOKS
# =============================================================================
# Edit THIS file when you want to hook Archipelago state into Luck be a Landlord.
#
# Every hook can be in one of three states:
#   LOCKED   = unavailable in the game
#   UNLOCKED = available, but not completed/used yet
#   DONE     = completed / sent / consumed / finished
#
# Supported hook groups:
#   checks, symbols, items, essences, abilities, floors
#
# Typical examples:
#   register_symbol("cat", 22)
#   unlock_symbol("cat")
#
#   register_check("floor_1_payment_1", 1)
#   unlock_check("floor_1_payment_1")
#   done_check("floor_1_payment_1", true) # true = send LocationChecks to AP
#
#   register_floor(5, 378)
#   lock_floor(5)
#   unlock_floor(5)
# =============================================================================

signal hook_changed(category, key, state, ap_id, data)
signal check_changed(key, state, ap_id, data)
signal symbol_changed(key, state, ap_id, data)
signal item_changed(key, state, ap_id, data)
signal essence_changed(key, state, ap_id, data)
signal ability_changed(key, state, ap_id, data)
signal floor_changed(key, state, ap_id, data)

const STATE_LOCKED = 0
const STATE_UNLOCKED = 1
const STATE_DONE = 2

const LOCKED = STATE_LOCKED
const UNLOCKED = STATE_UNLOCKED
const DONE = STATE_DONE

const CAT_CHECK = "checks"
const CAT_SYMBOL = "symbols"
const CAT_ITEM = "items"
const CAT_ESSENCE = "essences"
const CAT_ABILITY = "abilities"
const CAT_FLOOR = "floors"

# Your registered hooks live here.
var hooks = {
	CAT_CHECK: {},
	CAT_SYMBOL: {},
	CAT_ITEM: {},
	CAT_ESSENCE: {},
	CAT_ABILITY: {},
	CAT_FLOOR: {}
}

# Reverse lookup tables so AP item/location IDs can find your hook immediately.
var ap_item_index = {}
var ap_location_index = {}

var ap_client = null

# Routine hook tracing is intentionally silent. The detachable console's
# `hooks` command reads the live hook table directly when requested, so there is
# no need to flood the log while the game is running. Keep errors and real AP
# gameplay actions logged separately.
var hook_background_logging = false

func _hook_debug(message):
	if hook_background_logging and ap_client != null and ap_client.has_method("debug_log"):
		ap_client.debug_log(str(message))

# APWorld special items (394..401). Buffs 394..398 are permanent per AP slot:
# they apply immediately when received and are re-applied as starting bonuses on
# every new run. Traps 399..401 remain one-shot effects. Received indexes are
# tracked so reconnecting cannot replay the immediate effect in the same run.
const SPECIAL_EFFECT_STATE_PATH = "user://LBAL-AP-SpecialEffects.json"
# Once a seed/slot has finished every generated AP Check location, remember that
# fact locally as well as trusting the server's checked_locations. This prevents
# AP Check from briefly coming back on reconnect/new runs before every other AP
# state path has finished refreshing. The key includes server + seed + slot, so a
# different seed or slot starts clean.
const AP_CHECK_COMPLETION_STATE_PATH = "user://LBAL-AP-CompletedAPChecks.json"
var _processed_special_receive_indexes = {}
var _special_effect_state_loaded_key = ""
var _ap_check_completion_loaded_key = ""
var _ap_checks_permanently_complete = false

# How many permanent AP buffs have already been applied to the current LBAL run.
# These reset when a new run starts; received_items remains authoritative.
var _run_permanent_buff_counts = {394: 0, 395: 0, 396: 0, 397: 0, 398: 0, 411: 0}
var _run_buff_last_menu = ""
var _run_buff_last_spins = -1
var _run_buff_armed = true

func _ready():
	call_deferred("_bind_ap_client")
	_register_default_floor_hooks()
	call_deferred("_late_auto_setup")
	set_process(true)

func _process(delta):
	# Keep the AP hook node bound even if its original deferred bind happened before
	# the AP Client was ready.  This also repairs a lost signal connection at runtime.
	_hook_bind_timer += delta
	if _hook_bind_timer >= 0.5:
		_hook_bind_timer = 0.0
		_ensure_ap_client_bound()
		if ap_client != null and ap_client.has_method("is_connected_to_ap") and ap_client.is_connected_to_ap():
			if not _ap_mode_active:
				_activate_ap_mode()
			_replay_received_items_into_hook_states()

	# Never alter the normal LBAL pools while offline. AP restrictions only become
	# active after the Archipelago server has accepted our slot and sent Connected.
	_pool_refresh_timer += delta
	if _pool_refresh_timer >= 1.0:
		_pool_refresh_timer = 0.0
		if _auto_hook_ready and _ap_mode_active:
			_enforce_all_pool_states()

	# AP traps and LBAL's queued coin animation can overlap. Never allow the
	# displayed balance or its pending animation to settle below zero.
	if _ap_mode_active:
		_clamp_negative_money()
		_watch_permanent_run_buffs()

func _clamp_negative_money():
	var coins = get_node_or_null("/root/Main/Coins")
	if coins == null:
		return
	var changed = false
	if int(coins.coins) < 0:
		coins.coins = 0
		changed = true
	if coins.get("queued_increase") != null:
		var queued = int(coins.queued_increase)
		var base = max(0, int(coins.coins))
		if base + queued < 0:
			coins.queued_increase = -base
			changed = true
	if changed and ap_client != null and ap_client.has_method("debug_log"):
		ap_client.debug_log("AP MONEY SAFETY clamped negative balance to 0")

func _late_auto_setup():
	yield(get_tree(), "idle_frame")
	yield(get_tree(), "idle_frame")
	# Install the AP Check definition/artwork, but do NOT place it in the live pool
	# until an AP slot is actually authenticated.
	_install_ap_check_symbol()
	auto_hook_everything()
	_auto_hook_ready = true
	if ap_client != null and ap_client.has_method("is_connected_to_ap") and ap_client.is_connected_to_ap():
		_activate_ap_mode()
	_hook_debug("AUTO HOOK READY symbols=" + str(hooks[CAT_SYMBOL].size()) + " items=" + str(hooks[CAT_ITEM].size()) + " essences=" + str(hooks[CAT_ESSENCE].size()) + " abilities=" + str(hooks[CAT_ABILITY].size()) + " checks=" + str(hooks[CAT_CHECK].size()) + " floors=" + str(hooks[CAT_FLOOR].size()))

func _bind_ap_client():
	_ensure_ap_client_bound()

func _ensure_ap_client_bound():
	var client = get_node_or_null("/root/Main/AP Client")
	if client == null:
		return false
	ap_client = client

	if ap_client.has_signal("item_received") and not ap_client.is_connected("item_received", self, "_on_ap_item_received"):
		ap_client.connect("item_received", self, "_on_ap_item_received")
	if ap_client.has_signal("received_items_changed") and not ap_client.is_connected("received_items_changed", self, "_on_received_items_changed"):
		ap_client.connect("received_items_changed", self, "_on_received_items_changed")
	if ap_client.has_signal("locations_updated") and not ap_client.is_connected("locations_updated", self, "_on_ap_locations_updated"):
		ap_client.connect("locations_updated", self, "_on_ap_locations_updated")
	if ap_client.has_signal("location_check_sent") and not ap_client.is_connected("location_check_sent", self, "_on_location_check_sent"):
		ap_client.connect("location_check_sent", self, "_on_location_check_sent")
	if ap_client.has_signal("connected_to_ap") and not ap_client.is_connected("connected_to_ap", self, "_on_ap_connected"):
		ap_client.connect("connected_to_ap", self, "_on_ap_connected")
	if ap_client.has_signal("disconnected_from_ap") and not ap_client.is_connected("disconnected_from_ap", self, "_on_ap_disconnected"):
		ap_client.connect("disconnected_from_ap", self, "_on_ap_disconnected")
	if ap_client.has_signal("deathlink_received") and not ap_client.is_connected("deathlink_received", self, "_on_deathlink_received"):
		ap_client.connect("deathlink_received", self, "_on_deathlink_received")
	if ap_client.has_signal("ap_settings_changed") and not ap_client.is_connected("ap_settings_changed", self, "_on_ap_settings_changed"):
		ap_client.connect("ap_settings_changed", self, "_on_ap_settings_changed")

	if not _hooks_bound_logged:
		_hooks_bound_logged = true
		_hook_debug("HOOKS BOUND/READY categories=checks,symbols,items,essences,abilities,floors")

	if ap_client.has_method("is_connected_to_ap") and ap_client.is_connected_to_ap():
		if not _ap_mode_active:
			_activate_ap_mode()
		_replay_received_items_into_hook_states()
	return true

# =============================================================================
# AP MODE LIFECYCLE
# =============================================================================
# Offline/disconnected: Luck be a Landlord behaves completely normally.
# Authenticated Connected packet: AP pool restrictions become active.

func is_ap_mode_active():
	return _ap_mode_active and ap_client != null and ap_client.has_method("is_connected_to_ap") and ap_client.is_connected_to_ap()

# Reconcile the cached AP mode flag with the AP client's live authenticated
# state.  Title.floor_menu() calls this before deciding which floors to show so
# a missed/late connected_to_ap signal can never silently fall back to vanilla.
func refresh_ap_mode_from_client():
	var connected = ap_client != null and ap_client.has_method("is_connected_to_ap") and ap_client.is_connected_to_ap()
	if connected and not _ap_mode_active:
		_activate_ap_mode()
	elif not connected and _ap_mode_active:
		_deactivate_ap_mode()
	return connected and _ap_mode_active

func _on_ap_connected():
	# A Connected packet represents one authoritative AP slot. Start from the
	# registration defaults, then let this slot's ReceivedItems replay unlocks.
	_reset_hook_states_to_initial()
	_activate_ap_mode()
	_refresh_floor_menu_if_open()

func _on_ap_disconnected():
	_deactivate_ap_mode()
	_reset_hook_states_to_initial()
	# AP Check is not a vanilla LBAL symbol, so remove any copies that were still
	# sitting in the current run when AP was disconnected/switched.
	call_deferred("_remove_all_ap_check_symbols", "AP disconnected or slot switched")
	_refresh_floor_menu_if_open()

func _refresh_floor_menu_if_open():
	var main = get_node_or_null("/root/Main")
	var title = get_node_or_null("/root/Main/Title")
	if main == null or title == null or str(main.current_menu_path) != "floor_menu":
		return
	if title.has_method("reset_floor_menu"):
		title.reset_floor_menu()
	if title.has_method("floor_menu"):
		title.call_deferred("floor_menu")

func _reset_hook_states_to_initial():
	_reset_current_run_permanent_buff_counts()
	_run_buff_last_menu = ""
	_run_buff_last_spins = -1
	_run_buff_armed = true
	# Unlock/DONE state is session-local. Reverting every hook to the state it was
	# registered with prevents one AP slot leaking symbols/items/floors/checks into
	# the next slot.
	_last_received_replay_count = -1
	_ap_check_last_sent_spin = -999999
	_special_effect_state_loaded_key = ""
	_processed_special_receive_indexes.clear()
	# Completion is permanent only for the current server/seed/slot. Forget the
	# in-memory latch while switching sessions; _activate_ap_mode() reloads the
	# correct per-seed value immediately after authentication.
	_ap_check_completion_loaded_key = ""
	_ap_checks_permanently_complete = false
	for category in hooks.keys():
		for hook_key in hooks[category].keys():
			var entry = hooks[category][hook_key]
			entry.state = int(entry.get("initial_state", STATE_LOCKED))
			hooks[category][hook_key] = entry

# Archipelago sends the Connected packet before the full ReceivedItems history.
# If the player opens the floor screen during that gap it initially only knows
# about Floor 1.  Rebuild the individual AP floor unlock states when the item
# sync finishes and refresh the visible floor menu if it is currently open.
func _on_received_items_changed():
	_ensure_ap_client_bound()
	if not is_ap_mode_active():
		return
	_replay_received_items_into_hook_states(true)
	# Connected arrives before the full ReceivedItems history. If we are already
	# at the beginning of a run, apply the permanent starting bonuses after sync.
	_apply_missing_permanent_buffs_for_current_run()
	var unlocked_floors = get_unlocked_floor_numbers()
	_hook_debug("AP FLOOR SYNC ReceivedItems complete visible_floors=" + str(unlocked_floors))
	var main = get_node_or_null("/root/Main")
	var title = get_node_or_null("/root/Main/Title")
	if main != null and title != null and str(main.current_menu_path) == "floor_menu":
		if title.has_method("reset_floor_menu"):
			title.reset_floor_menu()
		if title.has_method("floor_menu"):
			title.call_deferred("floor_menu")

func _activate_ap_mode():
	if _ap_mode_active:
		return
	_ap_mode_active = true
	sync_floor_unlocks_from_received_items()
	_sync_ap_check_completion_state()
	_ensure_ap_check_in_pool()
	_enforce_all_pool_states()
	_hook_debug("AP MODE ACTIVE: authenticated; AP restrictions enabled and AP Check added to pool")

func _deactivate_ap_mode():
	if not _ap_mode_active:
		_remove_ap_check_from_pool()
		return
	_ap_mode_active = false
	_restore_normal_pools()
	_remove_ap_check_from_pool()
	_hook_debug("AP MODE INACTIVE: disconnected; restored normal LBAL pools")

func _restore_normal_pools():
	var main = get_node_or_null("/root/Main")
	if main == null:
		return
	# base_rarities is kept untouched by AP code and acts as the normal LBAL pool.
	if typeof(main.base_rarities) == TYPE_DICTIONARY and typeof(main.rarity_database) == TYPE_DICTIONARY:
		for group_name in ["symbols", "items"]:
			if main.base_rarities.has(group_name):
				main.rarity_database[group_name] = main.base_rarities[group_name].duplicate(true)

func _remove_ap_check_from_pool():
	var main = get_node_or_null("/root/Main")
	if main == null:
		return
	if main.rarity_database.has("symbols"):
		for rarity in main.rarity_database.symbols.keys():
			main.rarity_database.symbols[rarity].erase(AP_CHECK_TYPE)
	if main.base_rarities.has("symbols"):
		for rarity in main.base_rarities.symbols.keys():
			main.base_rarities.symbols[rarity].erase(AP_CHECK_TYPE)

# =============================================================================
# FLOOR-DEPENDENT SEND/EFFECT CHECKS
# =============================================================================
# When Floor Check sanity is enabled, the APWorld removes the global Send/Effect
# checks from the seed and creates one copy on every enabled floor:
#   Floor 5 - Send: Dog
#   Floor 5 - Effect: Dog boosts Toddler
# Payments and AP Checks remain global and are deliberately not remapped here.

func _floor_dependent_checks_enabled():
	if ap_client == null:
		return false
	var data = ap_client.get("slot_data")
	if typeof(data) != TYPE_DICTIONARY:
		return false
	return bool(data.get("FloorDependentChecks", false))

func _current_ap_floor_number():
	var popup = get_node_or_null("/root/Main/Pop-up Sprite/Pop-up")
	if popup != null and is_instance_valid(popup):
		var value = int(popup.current_floor)
		if value >= 1 and value <= 20:
			return value
	return 1

func _floor_variant_location_name(base_location_name):
	var base_name = APData.base_send_effect_name(str(base_location_name))
	if not _floor_dependent_checks_enabled():
		return base_name
	if not (base_name.begins_with("Send: ") or base_name.begins_with("Effect: ")):
		return base_name
	var floor_name = APData.floor_dependent_location_name(_current_ap_floor_number(), base_name)
	return floor_name if floor_name != "" else base_name

func _floor_variant_location_id(base_location_id, base_location_name = ""):
	if not _floor_dependent_checks_enabled():
		return int(base_location_id)
	var base_name = str(base_location_name)
	if base_name == "":
		base_name = APData.location_name(int(base_location_id))
	base_name = APData.base_send_effect_name(base_name)
	if not (base_name.begins_with("Send: ") or base_name.begins_with("Effect: ")):
		return int(base_location_id)
	var resolved = APData.floor_dependent_location_id(_current_ap_floor_number(), base_name)
	return resolved if resolved >= 0 else int(base_location_id)

func _floor_variant_location_id_by_name(base_location_name):
	var resolved_name = _floor_variant_location_name(base_location_name)
	return APData.location_id(resolved_name)

# =============================================================================
# AUTO HOOKING
# =============================================================================
# This discovers the real LBAL game keys from tile_database/item_database, then
# uses APData.gd to attach the matching AP item and location IDs automatically.
# You normally do not need to type register_symbol("gambler", 54), etc. anymore.

func auto_hook_everything():
	var main = get_node_or_null("/root/Main")
	if main == null:
		return

	for game_type in main.tile_database.keys():
		var game_key = str(game_type)
		if game_key == AP_CHECK_TYPE:
			continue
		var item_id = APData.first_item_id_for_game_type(game_key)
		if item_id >= 0:
			var initial_state = STATE_UNLOCKED if _is_base_starting_symbol(game_key) else STATE_LOCKED
			register_symbol(game_key, item_id, initial_state, {"game_type": game_key, "auto": true})
			_auto_register_send_checks_for_game_type(game_key, "symbol")

	for game_type in main.item_database.keys():
		var game_key = str(game_type)
		var item_id = APData.first_item_id_for_game_type(game_key)
		if item_id < 0:
			continue
		var data = main.item_database[game_type]
		if str(data.get("rarity", "")) == "essence" or APData.normalise_game_key(game_key).ends_with("_essence"):
			register_essence(game_key, item_id, STATE_LOCKED, {"game_type": game_key, "auto": true})
			_auto_register_send_checks_for_game_type(game_key, "essence")
		else:
			register_item(game_key, item_id, STATE_LOCKED, {"game_type": game_key, "auto": true})
			_auto_register_send_checks_for_game_type(game_key, "item")

	for ap_name in APData.ITEM_NAME_TO_ID.keys():
		var item_id = int(APData.ITEM_NAME_TO_ID[ap_name])
		if ap_item_index.has(item_id):
			continue
		if item_id >= 375 and item_id <= 393:
			continue
		var ability_key = _normalise_display_key(_strip_unlock_prefix(str(ap_name)))
		register_ability(ability_key, item_id, STATE_LOCKED, {"ap_name": str(ap_name), "auto": true})

	for location_name in APData.LOCATION_NAME_TO_ID.keys():
		var location_id = int(APData.LOCATION_NAME_TO_ID[location_name])
		if ap_location_index.has(location_id):
			continue
		var key = _normalise_display_key(str(location_name))
		register_check(key, location_id, STATE_UNLOCKED, {"ap_name": str(location_name), "auto": true})

func _auto_register_send_checks_for_game_type(game_type, source_category):
	var ids = APData.send_location_ids_for_game_type(game_type)
	for location_id in ids:
		location_id = int(location_id)
		if ap_location_index.has(location_id):
			continue
		var key = "send_" + APData.canonical_game_key_for_actual_type(game_type)
		if ids.size() > 1:
			key += "_" + str(location_id)
		register_check(key, location_id, STATE_UNLOCKED, {"game_type": str(game_type), "source_category": source_category, "auto": true})

func _strip_unlock_prefix(value):
	var s = str(value)
	if s.begins_with("Unlock: "):
		return s.substr(8, -1)
	return s

func _normalise_display_key(value):
	var s = str(value).to_lower()
	s = s.replace("&", "and")
	s = s.replace("'", "")
	s = s.replace("-", "_")
	s = s.replace(" ", "_")
	s = s.replace("/", "_")
	s = s.replace(".", "")
	s = s.replace(":", "")
	while s.find("__") != -1:
		s = s.replace("__", "_")
	return s.strip_edges()

# =============================================================================
# AP CHECK SYMBOL
# =============================================================================

func _install_ap_check_symbol():
	var main = get_node_or_null("/root/Main")
	if main == null:
		return

	# v14: AP Check is defined in the normal LBAL Symbols JSON so it goes
	# through exactly the same startup/database path as every vanilla symbol.
	# Do not create a late runtime-only symbol definition here.
	if not main.tile_database.has(AP_CHECK_TYPE):
		if ap_client != null and ap_client.has_method("debug_log"):
			ap_client.debug_log("AP CHECK ERROR: tile_database is missing ap_check; Symbols JSON patch did not load")
		return

	# Make sure the loaded entry has the normal fields LBAL's Card/Slot Icon code
	# expects even if another mod touched the database.
	var data = main.tile_database[AP_CHECK_TYPE]
	data["type"] = AP_CHECK_TYPE
	data["value"] = "3"
	data["values"] = []
	data["rarity"] = AP_CHECK_RARITY
	data["groups"] = []
	data["sfx"] = []
	data["modded"] = false

	# Load the user's artwork directly as an ImageTexture. This avoids relying
	# on Godot's import remap for a PNG that was added to the PCK after export.
	var image = Image.new()
	var err = image.load("res://ap_check.png")
	if err == OK:
		var texture = ImageTexture.new()
		texture.create_from_image(image, 0)
		main.icon_texture_database[AP_CHECK_TYPE] = texture
		_hook_debug("AP CHECK ART loaded size=" + str(image.get_size()) + " error=OK")
	else:
		# Keep the game alive if PNG loading ever fails. A visible coin fallback is
		# better than a null texture crashing Card.tscn at texture.get_size().
		if main.icon_texture_database.has("coin"):
			main.icon_texture_database[AP_CHECK_TYPE] = main.icon_texture_database["coin"]
		if ap_client != null and ap_client.has_method("debug_log"):
			ap_client.debug_log("AP CHECK ART load failed error=" + str(err) + "; using coin fallback")

	_add_ap_check_translation()

	# AP Check must never be offered in ordinary/offline LBAL. The JSON entry is
	# only there so LBAL knows how to instantiate/render the symbol safely.
	if is_ap_mode_active():
		_ensure_ap_check_in_pool()
	else:
		_remove_ap_check_from_pool()

	_hook_debug("AP CHECK SYMBOL ready via native Symbols JSON type=" + AP_CHECK_TYPE + " rarity=" + AP_CHECK_RARITY + " artwork=res://ap_check.png")

func _add_ap_check_translation():
	var translation = Translation.new()
	translation.set_locale("en")
	translation.add_message(AP_CHECK_TYPE, "AP Check")
	translation.add_message(AP_CHECK_TYPE + "_desc", "Gives 3 coins. Sends the next AP Check and destroys itself after being displayed in a spin.")
	TranslationServer.add_translation(translation)

func _ensure_ap_check_in_pool():
	if not is_ap_mode_active():
		return
	if _should_permanently_remove_ap_check():
		_remove_ap_check_from_pool()
		_purge_ap_check_saved_choices()
		_remove_all_ap_check_symbols("all AP Check locations completed permanently")
		return
	var main = get_node_or_null("/root/Main")
	if main == null or not main.tile_database.has(AP_CHECK_TYPE):
		return
	if main.rarity_database.has("symbols") and main.rarity_database.symbols.has(AP_CHECK_RARITY):
		if not main.rarity_database.symbols[AP_CHECK_RARITY].has(AP_CHECK_TYPE):
			main.rarity_database.symbols[AP_CHECK_RARITY].push_back(AP_CHECK_TYPE)

func trigger_ap_check_symbol(icon):
	# Called by Slot Icon's normal effect engine before the native capsule-style
	# shake/destroy effect runs. Each AP Check icon still destroys itself and gives
	# its normal 3 coins, but only ONE Archipelago location may be sent per spin.
	if icon == null or not is_instance_valid(icon):
		return false
	if ap_client == null or not ap_client.is_connected_to_ap():
		return false
	var popup = get_node_or_null("/root/Main/Pop-up Sprite/Pop-up")
	var current_spin = int(popup.spins) if popup != null else -999998

	# Slot Icon nodes can be reused by LBAL. The old boolean metadata guard stayed
	# on a reused node forever, so after enough AP Checks that node would keep
	# destroying future AP Checks without sending them. Track the spin number
	# instead, which makes the guard per AP Check activation rather than per node.
	if icon.has_meta("ap_check_sent_spin") and int(icon.get_meta("ap_check_sent_spin")) == current_spin:
		return false
	icon.set_meta("ap_check_sent_spin", current_spin)
	# Clear the legacy permanent boolean marker from older builds if this node was
	# reused after an in-place upgrade.
	if icon.has_meta("ap_check_sent"):
		icon.remove_meta("ap_check_sent")

	if _ap_check_last_sent_spin == current_spin:
		# Another AP Check on this same spin: animate/destroy it, but do not send
		# another AP location.
		return true
	_ap_check_last_sent_spin = current_spin

	var location_id = _next_unsent_ap_check_location()
	if location_id >= 0:
		var check_num = _ap_check_number_for_location(location_id)
		var key = "ap_check_" + str(check_num)
		if not ap_location_index.has(location_id):
			register_check(key, location_id, STATE_UNLOCKED, {"ap_name": "AP Check " + str(check_num), "auto": true})
		done_location_id(location_id, true)
		if ap_client.has_method("debug_log"):
			ap_client.debug_log("AP CHECK SYMBOL triggered check_num=" + str(check_num) + " location_id=" + str(location_id) + " coin_value=3 animation=capsule one_check_per_spin=true")
	else:
		if ap_client.has_method("debug_log"):
			ap_client.debug_log("AP CHECK SYMBOL no unfinished AP Check locations remain; capsule destroy animation only coin_value=3")

	_sync_ap_check_completion_state()
	return true

func reset_ap_check_run_guard():
	_ap_check_last_sent_spin = -999999

func process_ap_check_spin(displayed_icons):
	# Safety fallback. Normally res://Slot Icon.tscn triggers the AP check from
	# the regular symbol effect engine, which gives it the same shake/destroy
	# animation as a capsule. If a modded code path skipped those effects, do it
	# here so the check is never lost.
	if ap_client == null or not ap_client.is_connected_to_ap():
		return
	for row in displayed_icons:
		for icon in row:
			if icon != null and is_instance_valid(icon) and APData.normalise_game_key(str(icon.type)) == AP_CHECK_TYPE:
				var newly_sent = trigger_ap_check_symbol(icon)
				if newly_sent and str(icon.type) != "empty" and icon.has_method("destroy"):
					# Only a fallback path: native Slot Icon effects normally destroy it.
					icon.destroy()

func _ap_check_location_id_for_number(check_num):
	var location_name = "AP Check " + str(int(check_num))
	if APData.LOCATION_NAME_TO_ID.has(location_name):
		return int(APData.LOCATION_NAME_TO_ID[location_name])
	return -1

func _ap_check_number_for_location(location_id):
	location_id = int(location_id)
	for check_num in range(1, 151):
		if _ap_check_location_id_for_number(check_num) == location_id:
			return check_num
	return -1

func _next_unsent_ap_check_location():
	# Use the APWorld's name->ID table rather than assuming AP Check locations are
	# contiguous. The current APWorld deliberately moved AP Checks 140-150 to
	# 1118-1128 to remove duplicate location IDs.
	for check_num in range(1, 151):
		var location_id = _ap_check_location_id_for_number(check_num)
		if location_id >= 0 and ap_client.missing_locations.has(location_id):
			return location_id
	return -1

# =============================================================================
# POOL ENFORCEMENT
# =============================================================================

func _is_base_starting_symbol(game_type):
	return BASE_STARTING_SYMBOLS.has(APData.normalise_game_key(str(game_type)))

func _find_symbol_hook_for_game_type(game_type):
	var raw = str(game_type)
	if hooks[CAT_SYMBOL].has(raw):
		return hooks[CAT_SYMBOL][raw]
	var wanted = APData.normalise_game_key(raw)
	for hook_key in hooks[CAT_SYMBOL].keys():
		if APData.normalise_game_key(str(hook_key)) == wanted:
			return hooks[CAT_SYMBOL][hook_key]
	return null

func is_ap_check_boost_enabled():
	return ap_client != null and ap_client.ap_check_boost_enabled

func are_all_ap_checks_complete():
	if not is_ap_mode_active():
		return false
	# Only count AP Check locations that actually exist in this generated seed.
	# Disabled AP Check locations are in neither checked_locations nor
	# missing_locations and must not keep AP Check alive forever.
	var active_count = 0
	for check_num in range(1, 151):
		var location_id = _ap_check_location_id_for_number(check_num)
		if location_id < 0:
			continue
		var exists_in_seed = ap_client.checked_locations.has(location_id) or ap_client.missing_locations.has(location_id)
		if not exists_in_seed:
			continue
		active_count += 1
		if not ap_client.checked_locations.has(location_id):
			return false
	return active_count > 0

func _ap_check_completion_state_key():
	if ap_client == null:
		return "unknown"
	return str(ap_client.server_address) + "|" + str(ap_client.seed_name) + "|" + str(ap_client.slot_name)

func _load_ap_check_completion_state():
	var state_key = _ap_check_completion_state_key()
	if _ap_check_completion_loaded_key == state_key:
		return
	_ap_check_completion_loaded_key = state_key
	_ap_checks_permanently_complete = false
	# Do not persist/load an incomplete identity. In normal AP mode seed_name and
	# slot_name are already known from RoomInfo/Connected before this is called.
	if ap_client == null or str(ap_client.seed_name) == "" or str(ap_client.slot_name) == "":
		return
	var file = File.new()
	if not file.file_exists(AP_CHECK_COMPLETION_STATE_PATH):
		return
	if file.open(AP_CHECK_COMPLETION_STATE_PATH, File.READ) != OK:
		return
	var parsed = JSON.parse(file.get_as_text())
	file.close()
	if parsed.error != OK or typeof(parsed.result) != TYPE_DICTIONARY:
		return
	if parsed.result.has(state_key):
		_ap_checks_permanently_complete = bool(parsed.result[state_key])
		if _ap_checks_permanently_complete and ap_client.has_method("debug_log"):
			ap_client.debug_log("AP CHECK PERMANENT COMPLETE restored for this seed/slot; AP Check will stay removed")

func _save_ap_check_completion_state():
	if ap_client == null or str(ap_client.seed_name) == "" or str(ap_client.slot_name) == "":
		return
	var state_key = _ap_check_completion_state_key()
	var all_state = {}
	var file = File.new()
	if file.file_exists(AP_CHECK_COMPLETION_STATE_PATH) and file.open(AP_CHECK_COMPLETION_STATE_PATH, File.READ) == OK:
		var parsed = JSON.parse(file.get_as_text())
		file.close()
		if parsed.error == OK and typeof(parsed.result) == TYPE_DICTIONARY:
			all_state = parsed.result
	all_state[state_key] = true
	if file.open(AP_CHECK_COMPLETION_STATE_PATH, File.WRITE) == OK:
		file.store_string(JSON.print(all_state))
		file.close()

func _should_permanently_remove_ap_check():
	if not is_ap_mode_active():
		return false
	_load_ap_check_completion_state()
	if _ap_checks_permanently_complete:
		return true
	if are_all_ap_checks_complete():
		_ap_checks_permanently_complete = true
		_save_ap_check_completion_state()
		if ap_client != null and ap_client.has_method("debug_log"):
			ap_client.debug_log("AP CHECK PERMANENT COMPLETE latched; removing AP Check from pool/inventory for this seed/slot")
		return true
	return false

func _purge_ap_check_saved_choices():
	# A symbol-choice popup can have card types cached from before the final AP
	# Check completed. Clear that cache if it contains AP Check so the next choice
	# rebuild cannot resurrect it after the permanent-complete latch.
	var popup = get_node_or_null("/root/Main/Pop-up Sprite/Pop-up")
	if popup == null:
		return
	var saved = popup.get("saved_card_types")
	if typeof(saved) == TYPE_ARRAY and saved.has(AP_CHECK_TYPE):
		saved.clear()
		popup.set("saved_card_types", saved)
		if ap_client != null and ap_client.has_method("debug_log"):
			ap_client.debug_log("AP CHECK CLEANUP cleared cached symbol choices containing AP Check")

func _sync_ap_check_completion_state():
	if not is_ap_mode_active():
		return
	if _should_permanently_remove_ap_check():
		_remove_ap_check_from_pool()
		_purge_ap_check_saved_choices()
		call_deferred("_remove_all_ap_check_symbols", "all AP Check locations completed permanently")

func _remove_all_ap_check_symbols(reason = ""):
	_purge_ap_check_saved_choices()
	var reels = get_node_or_null("/root/Main/Reels")
	if reels == null:
		return 0
	var to_destroy = []
	for reel in reels.reels:
		for icon in reel.icons:
			if icon != null and is_instance_valid(icon) and str(icon.type) == AP_CHECK_TYPE:
				to_destroy.push_back(icon)
	for icon in to_destroy:
		if icon != null and is_instance_valid(icon) and icon.has_method("destroy"):
			icon.destroy()
	if to_destroy.size() > 0:
		reels.update_icon_types()
		if ap_client != null and ap_client.has_method("debug_log"):
			ap_client.debug_log("AP CHECK CLEANUP removed=" + str(to_destroy.size()) + " reason=" + str(reason))
	return to_destroy.size()

func _on_ap_settings_changed():
	_sync_ap_check_completion_state()

func is_symbol_allowed_in_pool(game_type):
	if not is_ap_mode_active():
		return true
	var raw = str(game_type)
	if raw == AP_CHECK_TYPE:
		return not _should_permanently_remove_ap_check()
	if _is_base_starting_symbol(raw):
		return true
	var entry = _find_symbol_hook_for_game_type(raw)
	if entry == null:
		# Anything that is not represented by the APWorld is blocked from random
		# symbol choices. Forced/direct additions can still add it explicitly.
		return false
	return int(entry.state) != STATE_LOCKED

func _ensure_base_starting_symbols_in_pool(pool):
	# These are LBAL's basic starting symbols and must never disappear because a
	# previous AP pool mutation or a reconnect left rarity_database stale.  Only
	# add them when their native rarity is part of this temporary choice pool.
	if typeof(pool) != TYPE_DICTIONARY:
		return pool
	var main = get_node_or_null("/root/Main")
	if main == null:
		return pool
	var out = pool.duplicate(true)
	for game_type in BASE_STARTING_SYMBOLS:
		if not main.tile_database.has(game_type):
			continue
		var rarity = str(main.tile_database[game_type].get("rarity", "common"))
		if out.has(rarity) and not out[rarity].has(game_type):
			out[rarity].push_back(game_type)
	return out

func _symbol_send_locations_in_seed(game_type):
	var result = []
	if ap_client == null:
		return result
	for raw_id in APData.send_location_ids_for_game_type(game_type):
		var location_id = _floor_variant_location_id(int(raw_id))
		# A disabled location is in neither list, so do not use it when deciding
		# whether this symbol is complete for Boost.
		if ap_client.checked_locations.has(location_id) or ap_client.missing_locations.has(location_id):
			result.push_back(location_id)
	return result

func _symbol_send_check_is_complete(game_type):
	var location_ids = _symbol_send_locations_in_seed(game_type)
	if location_ids.empty():
		return false
	for location_id in location_ids:
		if not ap_client.checked_locations.has(int(location_id)):
			return false
	return true

func _boost_pool_game_type(game_type):
	# Effect rules use AP/canonical names, while LBAL's actual pool has a few
	# stage/alias names. Resolve those to the symbol that can really appear.
	var key = APData.normalise_game_key(game_type)
	match key:
		"matryoshka_doll": return "matryoshka_doll_1"
	return key

func _boost_find_symbol_pool_key(game_type):
	# APData normalises several LBAL internal names (d3 -> three_sided_die, etc.).
	# Resolve back to the real tile_database key before checking availability/rarity.
	var main = get_node_or_null("/root/Main")
	if main == null:
		return ""
	var raw = str(game_type)
	# LBAL v1.2.24's internal capsule IDs are swapped relative to their public
	# names. Effect rules use the public/AP names, so resolve those two canonical
	# names to the real tile_database entries before the normal direct lookup.
	if raw == "lucky_capsule" and main.tile_database.has("rarity_capsule"):
		return "rarity_capsule"
	if raw == "wealthy_capsule" and main.tile_database.has("lucky_capsule"):
		return "lucky_capsule"
	if main.tile_database.has(raw):
		return raw
	var wanted = _boost_pool_game_type(raw)
	for candidate in main.tile_database.keys():
		if APData.canonical_game_key_for_actual_type(str(candidate)) == wanted:
			return str(candidate)
	return ""

func _boost_symbol_available(game_type):
	var pool_type = _boost_find_symbol_pool_key(game_type)
	if pool_type == "":
		return false
	return is_symbol_allowed_in_pool(pool_type)

func _boost_effect_is_unfinished(rule):
	if ap_client == null:
		return false
	var location_id = _floor_variant_location_id(int(rule.get("id", -1)), str(rule.get("name", "")))
	# missing_locations is authoritative here: disabled effect locations are not
	# in the generated seed and checked locations are already complete.
	return location_id >= 0 and ap_client.missing_locations.has(location_id)

func _boost_effect_targets_are_requirements(rule):
	# add/transform targets are outputs created by the source, not symbols that
	# have to be found first. Boost/destroy/position/wildcard targets are real
	# partners. Robin Hood's give checks also need the named arrow/thief.
	var kind = str(rule.get("kind", ""))
	if kind in ["boost", "destroy", "position", "wildcard"]:
		return true
	if kind == "give" and str(rule.get("source", "")) == "robin_hood":
		return true
	return false

func _boost_inventory_counts():
	# Count symbols already owned in this run so effect prerequisites that are
	# already satisfied stop occupying the boosted choice pool.
	var counts = {}
	var reels = get_node_or_null("/root/Main/Reels")
	if reels == null:
		return counts
	var symbols = reels.get("symbol_arr")
	if typeof(symbols) != TYPE_ARRAY:
		return counts
	for symbol in symbols:
		var raw = ""
		if typeof(symbol) == TYPE_OBJECT and symbol != null:
			var object_type = symbol.get("type")
			if object_type != null:
				raw = str(object_type)
		elif typeof(symbol) == TYPE_DICTIONARY and symbol.has("type"):
			raw = str(symbol.type)
		var game_type = APData.canonical_game_key_for_actual_type(raw)
		if game_type == "" or game_type == "empty" or game_type == "dud" or game_type == AP_CHECK_TYPE:
			continue
		counts[game_type] = int(counts.get(game_type, 0)) + 1
	return counts

func _boost_effect_required_counts(rule):
	# Number of each symbol needed to make the unfinished effect possible.
	var required = {}
	var source = _boost_pool_game_type(str(rule.get("source", "")))
	if source != "":
		required[source] = 1
	if _boost_effect_targets_are_requirements(rule):
		var targets = rule.get("targets", [])
		if typeof(targets) == TYPE_ARRAY:
			for target in targets:
				var target_type = _boost_pool_game_type(str(target))
				if target_type != "":
					required[target_type] = int(required.get(target_type, 0)) + 1
	# The Crab check needs two Crabs in the same row, not merely one Crab owned.
	if source == "crab" and str(rule.get("name", "")) == "Effect: Crab in same row":
		required["crab"] = max(2, int(required.get("crab", 0)))
	return required

func _boost_effect_is_actionable(rule):
	if not _boost_effect_is_unfinished(rule):
		return false
	var source = _boost_pool_game_type(str(rule.get("source", "")))
	if source == "" or not _boost_symbol_available(source):
		return false
	if source == "gambler":
		if not _boost_symbol_available("three_sided_die") and not _boost_symbol_available("five_sided_die"):
			return false
	if _boost_effect_targets_are_requirements(rule):
		var targets = rule.get("targets", [])
		if typeof(targets) == TYPE_ARRAY:
			for target in targets:
				var target_type = _boost_pool_game_type(str(target))
				if target_type != "" and not _boost_symbol_available(target_type):
					return false
	return true

func _boost_effect_missing_symbols(rule, inventory_counts):
	# Return only prerequisites still missing from the CURRENT inventory.
	var missing = []
	if not _boost_effect_is_actionable(rule):
		return missing
	var required = _boost_effect_required_counts(rule)
	for game_type in required.keys():
		var amount_missing = int(required[game_type]) - int(inventory_counts.get(game_type, 0))
		if amount_missing > 0 and _boost_symbol_available(game_type) and not missing.has(game_type):
			missing.append(game_type)

	# Gambler needs Gambler + either die. Once any die is already owned, stop
	# offering more dice for that effect. If none is owned, either unlocked die is
	# a valid boosted choice.
	var source = _boost_pool_game_type(str(rule.get("source", "")))
	if source == "gambler":
		var have_die = int(inventory_counts.get("three_sided_die", 0)) > 0 or int(inventory_counts.get("five_sided_die", 0)) > 0
		if not have_die:
			for die_type in ["three_sided_die", "five_sided_die"]:
				if _boost_symbol_available(die_type) and not missing.has(die_type):
					missing.append(die_type)
	return missing

func _symbol_has_unfinished_send_check(game_type):
	var location_ids = _symbol_send_locations_in_seed(game_type)
	if location_ids.empty():
		return false
	for location_id in location_ids:
		if ap_client.missing_locations.has(int(location_id)):
			return true
	return false

func _build_boost_needed_symbols():
	# Keep every symbol tied to an unfinished check that is CURRENTLY in logic.
	# A Send check is in logic once its symbol unlock is available. An Effect check
	# is in logic once its source and any true target requirements are unlocked.
	#
	# IMPORTANT: do not stop pruning just because the needed symbol is already in
	# the current inventory. The rarity/category stays focused until the actual
	# Send/Effect location is checked, then all other unlocked symbols come back.
	var needed = {}
	var main = get_node_or_null("/root/Main")
	if main == null:
		return needed

	# Unfinished Send: X checks for unlocked symbols.
	# The five vanilla starting symbols are always present/available, so their
	# unfinished Send checks must NEVER activate Boost by themselves.  This is
	# especially important when the tracker says only AP Check locations are in
	# logic: a missing Send: Cherry/Cat/etc. should not keep AP Check at boosted
	# weight or keep the symbol pool pruned.
	for game_type in main.tile_database.keys():
		var raw = str(game_type)
		if raw == AP_CHECK_TYPE or _is_base_starting_symbol(raw) or not is_symbol_allowed_in_pool(raw):
			continue
		if _symbol_has_unfinished_send_check(raw):
			needed[APData.canonical_game_key_for_actual_type(raw)] = true

	# Unfinished Effect: checks that are actually reachable with current unlocks.
	# Keep the source and any real partner/target requirements visible until the
	# effect check itself is completed. Add/transform outputs are not prerequisites.
	for source_key in APEffectData.EFFECT_RULES_BY_SOURCE.keys():
		for rule in APEffectData.rules_for_source(source_key):
			if not _boost_effect_is_actionable(rule):
				continue
			var source = _boost_pool_game_type(str(rule.get("source", "")))
			# Starting symbols are permanent exceptions to Boost. They stay in the
			# normal pool but do not count as work that keeps Boost active.
			if source != "" and not _is_base_starting_symbol(source) and _boost_symbol_available(source):
				needed[source] = true

			if _boost_effect_targets_are_requirements(rule):
				var targets = rule.get("targets", [])
				if typeof(targets) == TYPE_ARRAY:
					for target in targets:
						var target_type = _boost_pool_game_type(str(target))
						if target_type != "" and not _is_base_starting_symbol(target_type) and _boost_symbol_available(target_type):
							needed[target_type] = true

			# Gambler can use either die. Keep whichever die unlocks are currently
			# available so the check remains achievable without opening unrelated choices.
			if source == "gambler":
				for die_type in ["three_sided_die", "five_sided_die"]:
					if _boost_symbol_available(die_type):
						needed[_boost_pool_game_type(die_type)] = true
	return needed

func _has_non_ap_boost_work_in_logic():
	# AP Check locations themselves should never keep Boost active. Once there are
	# no currently actionable non-AP Send/Effect checks in any category, treat
	# Boost as idle and return to the normal unlocked pools / normal AP Check odds.
	if _build_boost_needed_symbols().size() > 0:
		return true
	if _build_boost_needed_item_entries(CAT_ITEM).size() > 0:
		return true
	if _build_boost_needed_item_entries(CAT_ESSENCE).size() > 0:
		return true
	return false

func get_boost_debug_text():
	var counts = _boost_inventory_counts()
	var needed = _build_boost_needed_symbols()
	var keys = needed.keys()
	keys.sort()
	var non_ap_work = _has_non_ap_boost_work_in_logic()
	return "AP CHECK BOOST=" + ("ON" if is_ap_check_boost_enabled() else "OFF") + " active=" + str(non_ap_work) + " inventory=" + str(counts) + " needed=" + str(keys)

func _rarity_has_unfinished_boost_goal(rarity_name, needed):
	var main = get_node_or_null("/root/Main")
	if main == null:
		return false
	# Compare using the REAL LBAL database keys so aliases such as d3/d5 still
	# activate the correct rarity bucket.
	for actual_key in main.tile_database.keys():
		var raw = str(actual_key)
		if not needed.has(APData.canonical_game_key_for_actual_type(raw)):
			continue
		if str(main.tile_database[actual_key].get("rarity", "none")) == str(rarity_name):
			return true
	return false

func _apply_ap_check_boost_symbol_pruning(pool):
	# Boost is CATEGORY-wide, not rarity-wide. If ANY unfinished Send/Effect
	# symbol check is currently actionable, every symbol rarity is focused on the
	# symbols needed for those checks. The five vanilla starting symbols are the
	# only permanent exceptions. When the symbol category has no unfinished
	# actionable Send/Effect checks, the full unlocked symbol pool comes back.
	if not is_ap_check_boost_enabled() or typeof(pool) != TYPE_DICTIONARY:
		return pool
	var out = pool.duplicate(true)
	var needed = _build_boost_needed_symbols()
	if needed.size() == 0:
		return out
	for rarity in out.keys():
		var symbols = out[rarity].duplicate()
		for game_type in symbols:
			var raw = str(game_type)
			if raw == AP_CHECK_TYPE or _is_base_starting_symbol(raw):
				continue
			if not needed.has(APData.canonical_game_key_for_actual_type(raw)):
				out[rarity].erase(game_type)
	return out

func _boost_entry_is_unlocked(category, game_type, entry):
	# Hook state is normally authoritative, but Essence Token rewards can be queued
	# immediately after AP history/new-item processing.  Fall back to the actual
	# ReceivedItems history so a just-received essence unlock cannot be missed by
	# Boost for one reward screen.
	if int(entry.get("state", STATE_LOCKED)) != STATE_LOCKED:
		return true
	var ap_id = int(entry.get("ap_id", -1))
	return ap_id >= 0 and _has_received_ap_item(ap_id)

func _build_boost_needed_item_entries(category):
	# Items/essences do not use APEffectData; their current AP checks are Send: X.
	# Only received/unlocked entries can be in logic, and disabled locations are
	# ignored by _symbol_send_locations_in_seed().
	var needed = {}
	if category != CAT_ITEM and category != CAT_ESSENCE:
		return needed
	for game_type in hooks[category].keys():
		var entry = hooks[category][game_type]
		if not _boost_entry_is_unlocked(category, game_type, entry):
			continue
		if _symbol_has_unfinished_send_check(str(game_type)):
			needed[APData.normalise_game_key(str(game_type))] = true
	return needed

func _apply_ap_check_boost_item_pruning(pool, essence_reward):
	# Items and essences are also CATEGORY-wide. If the selected category has at
	# least one unfinished Send check in logic, remove every unrelated unlocked
	# entry from that category across ALL rarities. When every Send check in the
	# category is complete, the full unlocked category is restored automatically.
	if not is_ap_check_boost_enabled() or typeof(pool) != TYPE_DICTIONARY:
		return pool
	var category = CAT_ESSENCE if essence_reward else CAT_ITEM
	var needed = _build_boost_needed_item_entries(category)
	var out = pool.duplicate(true)
	if needed.size() == 0:
		return out

	for rarity in out.keys():
		if essence_reward and str(rarity) != "essence":
			continue
		if not essence_reward and str(rarity) == "essence":
			continue
		var entries = out[rarity].duplicate()
		for game_type in entries:
			if not needed.has(APData.normalise_game_key(str(game_type))):
				out[rarity].erase(game_type)
	return out

func filter_essence_token_pool(card_pool):
	# Essence Tokens are a special LBAL reward path.  Handle them explicitly
	# instead of relying on forced_rarity inference in the normal item filter.
	# This is a hard final gate: only AP-unlocked essences with unfinished Send
	# checks remain while the essence category has work.
	if not is_ap_mode_active() or typeof(card_pool) != TYPE_DICTIONARY:
		return card_pool
	var out = card_pool.duplicate(true)
	for rarity_name in out.keys():
		if str(rarity_name) != "essence":
			out[rarity_name].clear()
	if not out.has("essence"):
		out["essence"] = []

	var unlocked_essences = []
	for game_type in out["essence"].duplicate():
		var key = str(game_type)
		if hooks[CAT_ESSENCE].has(key) and _boost_entry_is_unlocked(CAT_ESSENCE, key, hooks[CAT_ESSENCE][key]):
			unlocked_essences.push_back(game_type)
	out["essence"] = unlocked_essences

	var needed = _build_boost_needed_item_entries(CAT_ESSENCE)
	if is_ap_check_boost_enabled() and needed.size() > 0:
		# Older builds sometimes left rarity_database missing an unlocked essence.
		# Re-add a needed essence from item_database when it is genuinely available
		# and is not already owned/recently destroyed, then perform the hard prune.
		var main = get_node_or_null("/root/Main")
		if main != null:
			var blocked_types = []
			var items_node = get_node_or_null("/root/Main/Items")
			if items_node != null:
				for current_item in items_node.items:
					blocked_types.append(str(current_item.type))
				for destroyed_item in items_node.recently_destroyed_items:
					blocked_types.append(str(destroyed_item.type))
			for needed_key in needed.keys():
				for db_key in main.item_database.keys():
					if APData.normalise_game_key(str(db_key)) != str(needed_key):
						continue
					if str(main.item_database[db_key].get("rarity", "")) != "essence":
						continue
					if not blocked_types.has(str(db_key)) and not out["essence"].has(db_key):
						out["essence"].append(db_key)
					break
		for game_type in out["essence"].duplicate():
			if not needed.has(APData.normalise_game_key(str(game_type))):
				out["essence"].erase(game_type)

	if ap_client != null and ap_client.has_method("debug_log"):
		var needed_keys = needed.keys()
		needed_keys.sort()
		var allowed_keys = []
		for game_type in out["essence"]:
			allowed_keys.append(str(game_type))
		allowed_keys.sort()
		ap_client.debug_log("AP BOOST ESSENCE TOKEN FILTER category_active=" + str(needed_keys.size() > 0) + " needed=" + str(needed_keys) + " allowed=" + str(allowed_keys))
	return out

func filter_symbol_pool(card_pool):
	# Pop-up.tscn calls this immediately before drawing symbol-choice cards.
	# Until AP authentication succeeds, leave the game 100% vanilla/mod-normal.
	if not is_ap_mode_active():
		return card_pool
	# This is the final safety gate even if LBAL rebuilds rarity_database.
	if typeof(card_pool) != TYPE_DICTIONARY:
		return card_pool
	var out = card_pool.duplicate(true)


	var removed = []
	for rarity in out.keys():
		var original = out[rarity].duplicate()
		out[rarity].clear()
		for game_type in original:
			if is_symbol_allowed_in_pool(game_type):
				out[rarity].push_back(game_type)
			else:
				removed.push_back(str(game_type))
	# Reassert LBAL's base starters on the temporary pool.  This specifically
	# prevents Coin disappearing after reconnects/older pool mutations.
	out = _ensure_base_starting_symbols_in_pool(out)

	# Smart Boost uses unfinished Send checks plus missing prerequisites for
	# unfinished Effect checks. If that rarity has work, unrelated symbols are
	# pruned; when the rarity has no current goal, its unlocked pool is restored.
	out = _apply_ap_check_boost_symbol_pruning(out)
	if is_ap_check_boost_enabled() and ap_client != null and ap_client.has_method("debug_log"):
		var boost_needed = _build_boost_needed_symbols()
		var boost_keys = boost_needed.keys()
		boost_keys.sort()
		ap_client.debug_log("AP BOOST SYMBOL FILTER category_active=" + str(boost_keys.size() > 0) + " needed=" + str(boost_keys) + " common=" + str(out.get("common", [])))

	# AP Check disappears completely when every AP Check location is complete.
	# Boost keeps only a modest extra weight; the main boost comes from pruning.
	if out.has(AP_CHECK_RARITY):
		while out[AP_CHECK_RARITY].has(AP_CHECK_TYPE):
			out[AP_CHECK_RARITY].erase(AP_CHECK_TYPE)
		if not _should_permanently_remove_ap_check():
			# Do not boost AP Check just because AP Check locations are the only
			# locations currently in logic. With no non-AP Boost work left, this
			# goes back to the normal one-copy AP Check chance and the normal
			# unlocked symbol pool.
			var boost_has_non_ap_work = is_ap_check_boost_enabled() and _has_non_ap_boost_work_in_logic()
			var ap_check_weight = AP_CHECK_BOOST_WEIGHT if boost_has_non_ap_work else 1
			for _weight in range(ap_check_weight):
				out[AP_CHECK_RARITY].push_back(AP_CHECK_TYPE)
			if is_ap_check_boost_enabled() and not boost_has_non_ap_work and ap_client != null and ap_client.has_method("debug_log"):
				ap_client.debug_log("AP BOOST IDLE: only AP Checks/base starting-symbol checks remain; restored normal unlocked pools and AP Check weight=1")
	if hook_background_logging:
		var allowed_count = 0
		for rarity in out.keys():
			allowed_count += out[rarity].size()
		_hook_debug("AP SYMBOL POOL FILTER allowed=" + str(allowed_count) + " removed=" + str(removed.size()) + " common=" + str(out.get("common", [])))
	return out

func filter_item_pool(card_pool, extra_values = {}):
	# Pop-up.tscn calls this on its temporary item/essence choice pool.
	# Never destructively shrink LBAL's global item rarity database.
	if not is_ap_mode_active():
		return card_pool
	if typeof(card_pool) != TYPE_DICTIONARY:
		return card_pool
	var main = get_node_or_null("/root/Main")
	if main == null:
		return card_pool
	var out = card_pool.duplicate(true)

	# Normal item rewards must never fall through into LBAL's essence rarity.
	# Only an explicitly essence-forced reward may use the essence bucket.
	var essence_reward = false
	if typeof(extra_values) == TYPE_DICTIONARY and extra_values.has("forced_rarity"):
		for forced_rarity in extra_values.forced_rarity:
			if str(forced_rarity) == "essence":
				essence_reward = true
				break
	if essence_reward:
		for rarity_name in out.keys():
			if str(rarity_name) != "essence":
				out[rarity_name].clear()
	elif out.has("essence"):
		out["essence"].clear()

	var removed = []
	for rarity in out.keys():
		var original = out[rarity].duplicate()
		out[rarity].clear()
		for game_type in original:
			var key = str(game_type)
			var category = CAT_ITEM
			if str(rarity) == "essence" or key.ends_with("_essence"):
				category = CAT_ESSENCE
			if hooks[category].has(key) and _boost_entry_is_unlocked(category, key, hooks[category][key]):
				out[rarity].push_back(game_type)
			else:
				removed.push_back(key)

	# Boost pruning is intentionally last: first enforce AP unlocks, then focus
	# the temporary reward pool on unfinished Send checks currently in logic.
	out = _apply_ap_check_boost_item_pruning(out, essence_reward)
	if is_ap_check_boost_enabled() and ap_client != null and ap_client.has_method("debug_log"):
		var boost_category = CAT_ESSENCE if essence_reward else CAT_ITEM
		var boost_needed = _build_boost_needed_item_entries(boost_category)
		var boost_keys = boost_needed.keys()
		boost_keys.sort()
		var allowed_keys = []
		for rarity_name in out.keys():
			for allowed_key in out[rarity_name]:
				allowed_keys.append(str(allowed_key))
		allowed_keys.sort()
		ap_client.debug_log("AP BOOST " + ("ESSENCE" if essence_reward else "ITEM") + " FILTER category_active=" + str(boost_keys.size() > 0) + " needed=" + str(boost_keys) + " allowed=" + str(allowed_keys))

	if hook_background_logging:
		var allowed_count = 0
		for rarity in out.keys():
			allowed_count += out[rarity].size()
		_hook_debug("AP ITEM POOL FILTER mode=" + ("essence" if essence_reward else "item") + " allowed=" + str(allowed_count) + " removed=" + str(removed.size()) + " essence=" + str(out.get("essence", [])))
	return out

func count_item_pool_choices(card_pool, extra_values = {}):
	# Count unique choices that are actually legal for this reward.  This is used
	# to shrink a 3-card reward to 1 or 2 cards, and to safely skip a reward
	# when AP has not unlocked anything in the requested rarity.
	if typeof(card_pool) != TYPE_DICTIONARY:
		return 0
	var forced = []
	if typeof(extra_values) == TYPE_DICTIONARY and extra_values.has("forced_rarity"):
		forced = extra_values.forced_rarity
	var recognised_forced = false
	var allowed_rarities = []
	for r in forced:
		var rs = str(r)
		if rs in ["common", "uncommon", "rare", "very_rare", "essence"]:
			recognised_forced = true
			if not allowed_rarities.has(rs):
				allowed_rarities.push_back(rs)
	var total = 0
	if recognised_forced:
		for rarity in allowed_rarities:
			if card_pool.has(rarity):
				total += card_pool[rarity].size()
	else:
		for rarity in card_pool.keys():
			total += card_pool[rarity].size()
	return total

func _enforce_all_pool_states():
	if not is_ap_mode_active():
		return
	_ensure_ap_check_in_pool()
	# All AP reward pools are filtered only on temporary card_pool copies in
	# Pop-up.tscn.  Never destructively shrink LBAL's global rarity databases.
	_strict_filter_live_symbol_pools()

func _strict_filter_live_symbol_pools():
	# Kept for existing callers. Symbol filtering is intentionally non-destructive
	# now and happens only on Pop-up.tscn's temporary card pool.
	if is_ap_mode_active():
		_ensure_ap_check_in_pool()

func _set_pool_entry(category, key, unlocked):
	if not is_ap_mode_active():
		return
	var main = get_node_or_null("/root/Main")
	if main == null:
		return

	var db = null
	var rarity_groups = null
	if category == CAT_SYMBOL:
		db = main.tile_database
		rarity_groups = main.rarity_database["symbols"]
	else:
		db = main.item_database
		rarity_groups = main.rarity_database["items"]

	if not db.has(key):
		return
	var rarity = str(db[key].get("rarity", "none"))
	if not rarity_groups.has(rarity):
		return

	# Base starters are intentionally always present in the random symbol pool.
	# AP Check is present only until every generated AP Check is done; after that
	# its per-seed completion latch wins over any later generic pool refresh.
	if category == CAT_SYMBOL and _is_base_starting_symbol(key):
		unlocked = true
	elif category == CAT_SYMBOL and str(key) == AP_CHECK_TYPE:
		unlocked = not _should_permanently_remove_ap_check()

	if unlocked:
		if not rarity_groups[rarity].has(key):
			rarity_groups[rarity].push_back(key)
	else:
		rarity_groups[rarity].erase(key)

# =============================================================================
# REGISTRATION
# =============================================================================

func register_check(key, location_id, initial_state = STATE_LOCKED, data = {}):
	return register_hook(CAT_CHECK, key, location_id, initial_state, data)

func register_symbol(key, item_id, initial_state = STATE_LOCKED, data = {}):
	return register_hook(CAT_SYMBOL, key, item_id, initial_state, data)

func register_item(key, item_id, initial_state = STATE_LOCKED, data = {}):
	return register_hook(CAT_ITEM, key, item_id, initial_state, data)

func register_essence(key, item_id, initial_state = STATE_LOCKED, data = {}):
	return register_hook(CAT_ESSENCE, key, item_id, initial_state, data)

func register_ability(key, item_id = -1, initial_state = STATE_LOCKED, data = {}):
	return register_hook(CAT_ABILITY, key, item_id, initial_state, data)

func register_floor(floor_number, item_id = -1, initial_state = STATE_LOCKED, data = {}):
	return register_hook(CAT_FLOOR, str(int(floor_number)), item_id, initial_state, data)

func register_hook(category, key, ap_id = -1, initial_state = STATE_LOCKED, data = {}):
	category = _normalise_category(category)
	key = str(key)
	if not hooks.has(category):
		push_error("[AP HOOKS] Unknown hook category: " + category)
		return null

	var entry = {
		"key": key,
		"category": category,
		"state": int(initial_state),
		"initial_state": int(initial_state),
		"ap_id": int(ap_id),
		"data": data.duplicate(true) if typeof(data) == TYPE_DICTIONARY else {}
	}
	hooks[category][key] = entry

	if int(ap_id) >= 0:
		if category == CAT_CHECK:
			ap_location_index[int(ap_id)] = {"category": category, "key": key}
		else:
			ap_item_index[int(ap_id)] = {"category": category, "key": key}
	_hook_debug("HOOK REGISTER category=" + category + " key=" + key + " ap_id=" + str(ap_id) + " state=" + state_name(initial_state))
	return entry

# =============================================================================
# CHECKS
# =============================================================================

func lock_check(key):
	return set_state(CAT_CHECK, key, STATE_LOCKED)

func unlock_check(key):
	return set_state(CAT_CHECK, key, STATE_UNLOCKED)

func done_check(key, send_to_ap = false):
	var entry = set_state(CAT_CHECK, key, STATE_DONE)
	if entry != null and send_to_ap and ap_client != null and int(entry.ap_id) >= 0:
		ap_client.send_location_check(int(entry.ap_id))
	return entry

func done_location_id(location_id, send_to_ap = false):
	var location = int(location_id)
	if not ap_location_index.has(location):
		register_check("location_" + str(location), location, STATE_UNLOCKED)
	var ref = ap_location_index[location]
	return done_check(ref.key, send_to_ap)

# Send the AP "Send: X" location as soon as the player actually takes that
# symbol/item/essence from an LBAL reward card. This is deliberately separate
# from unlock receiving: receiving Unlock: Egg allows Egg into the pool; taking
# Egg from the pool completes Send: Egg.
func _send_named_ap_location_if_missing(location_name, debug_prefix = "AP LOCATION"):
	if not is_ap_mode_active() or ap_client == null:
		return false
	var resolved_name = _floor_variant_location_name(location_name)
	var location_id = APData.location_id(resolved_name)
	if location_id < 0:
		if ap_client.has_method("debug_log"):
			ap_client.debug_log(debug_prefix + " no mapping name=" + str(resolved_name))
		return false
	if ap_client.checked_locations.has(location_id):
		return false
	if ap_client.missing_locations.size() > 0 and not ap_client.missing_locations.has(location_id):
		return false
	# done_location_id marks the local hook DONE synchronously, so two dolls that
	# transform on the same frame cannot double-send while waiting for RoomUpdate.
	if ap_location_index.has(location_id):
		var ref = ap_location_index[location_id]
		if hooks.has(ref.category) and hooks[ref.category].has(ref.key):
			if int(hooks[ref.category][ref.key].state) == STATE_DONE:
				return false
	done_location_id(location_id, true)
	if ap_client.has_method("debug_log"):
		ap_client.debug_log(debug_prefix + " SENT name=" + str(resolved_name) + " location_id=" + str(location_id))
	return true


# =============================================================================
# UNIVERSAL SYMBOL EFFECT CHECKS
# =============================================================================
# Slot Icon calls notify_effect_applied() only after the native LBAL condition for
# an effect has passed. The table in APEffectData.gd then converts the exact
# source/target/action into the matching Archipelago Effect: location.
#
# This central hook means individual effects do not each need a hand-written AP
# call. Present, Crab and Matryoshka keep their dedicated hooks as safety paths.

func _effect_object_type(value):
	if value == null:
		return ""
	if typeof(value) == TYPE_OBJECT:
		var raw = value.get("type")
		if raw != null:
			return APData.canonical_game_key_for_actual_type(str(raw))
	elif typeof(value) == TYPE_STRING:
		return APData.canonical_game_key_for_actual_type(str(value))
	return ""

func _append_effect_candidate(arr, value):
	if value == null:
		return
	if typeof(value) != TYPE_STRING:
		return
	var key = APData.canonical_game_key_for_actual_type(str(value))
	if key == "" or arr.has(key):
		return
	arr.append(key)

func _effect_has_comparison(effect, key_name, wanted_value = null):
	if typeof(effect) != TYPE_DICTIONARY or not effect.has("comparisons"):
		return false
	for comp in effect.comparisons:
		if typeof(comp) != TYPE_DICTIONARY:
			continue
		if str(comp.get("a", "")) != str(key_name):
			continue
		if wanted_value == null or comp.get("b", null) == wanted_value:
			return true
	return false

func _effect_comparison_type_key(effect):
	if typeof(effect) != TYPE_DICTIONARY or not effect.has("comparisons"):
		return ""
	for comp in effect.comparisons:
		if typeof(comp) != TYPE_DICTIONARY:
			continue
		if str(comp.get("a", "")) == "type" and typeof(comp.get("b", null)) == TYPE_STRING:
			return APData.canonical_game_key_for_actual_type(str(comp.b))
	return ""

func _effect_is_value_change(vtc):
	return str(vtc) in [
		"value_bonus",
		"value_multiplier",
		"permanent_bonus",
		"permanent_multiplier",
		"flat_value_bonus",
		"bonus_values",
		"bonus_value_multipliers",
		"saved_value"
	]

func _effect_kind_matches(rule, effect, owner_key, target_key, giver_key):
	var kind = str(rule.get("kind", "any"))
	var vtc = str(effect.get("value_to_change", ""))
	var diff = effect.get("diff", null)
	var anim = str(effect.get("anim", ""))

	if rule.has("vtc") and vtc != str(rule.vtc):
		return false
	if rule.has("currency") and str(effect.get("currency", "")) != str(rule.currency):
		return false

	match kind:
		"destroy":
			return vtc == "destroyed" or vtc == "removed"
		"boost":
			return _effect_is_value_change(vtc)
		"add":
			return effect.has("tiles_to_add") or effect.has("items_to_add")
		"transform":
			if vtc == "type":
				return true
			return (effect.has("tiles_to_add") or effect.has("items_to_add")) and _effect_has_comparison(effect, "destroyed", true)
		"position":
			return _effect_is_value_change(vtc)
		"wildcard", "copy":
			return vtc == "wildcarded"
		"roll":
			return anim == "rand_texture_cycle" or _effect_is_value_change(vtc)
		"protect":
			return vtc == "indestructible" or _effect_has_comparison(effect, "dove_destroyed", true)
		"skip":
			return vtc == "hex_of_emptiness_trigger"
		"force":
			return vtc == "hex_of_hoarding_trigger"
		"lose":
			if not _effect_is_value_change(vtc):
				return false
			return (typeof(diff) == TYPE_INT or typeof(diff) == TYPE_REAL) and float(diff) < 0
		"give":
			return _effect_is_value_change(vtc) or effect.has("currency")
		"makes":
			return vtc != "achievement_value" and vtc != "saved_achievement_value"
		"remove_coin":
			return false # Thief uses a spin-level hook; this is not a normal conditional effect.
		_:
			return vtc != "achievement_value" and vtc != "saved_achievement_value"

func _effect_rule_target_matches(rule, candidates):
	var targets = rule.get("targets", [])
	if typeof(targets) != TYPE_ARRAY or targets.size() == 0:
		return true
	for wanted in targets:
		if not candidates.has(str(wanted)):
			return false
	return true

func _effect_location_for_rule(rule):
	if ap_client == null:
		return -1
	var preferred = _floor_variant_location_id(int(rule.get("id", -1)), str(rule.get("name", "")))
	if preferred >= 0 and ap_client.missing_locations.has(preferred):
		return preferred
	return -1

func notify_symbol_removed_by_removal_token(game_type):
	# LBAL handles manual Removal Token use in Hover Icon.tscn instead of the
	# normal conditional-effect engine. Jellyfish and Pufferfish still perform
	# their native reward when removed this way, so complete the matching AP
	# Effect check here as well. This is duplicate-safe through server state.
	if not is_ap_mode_active() or ap_client == null:
		return false
	var key = APData.canonical_game_key_for_actual_type(str(game_type))
	var location_name = ""
	match key:
		"jellyfish":
			location_name = "Effect: Jellyfish gives Removal Token"
		"pufferfish":
			location_name = "Effect: Pufferfish give 1 Reroll Token"
		_:
			return false
	var sent = _send_named_ap_location_if_missing(location_name, "AP REMOVAL TOKEN EFFECT")
	if ap_client.has_method("debug_log"):
		ap_client.debug_log("AP REMOVAL TOKEN SYMBOL key=" + key + " location=\"" + location_name + "\" sent=" + str(sent))
	return sent

func _send_effect_rule(rule, source_key, candidates, effect):
	var location_id = _effect_location_for_rule(rule)
	if location_id < 0:
		return false
	if ap_client.checked_locations.has(location_id):
		return false

	ap_client.send_location_check(location_id)
	if ap_location_index.has(location_id):
		var ref = ap_location_index[location_id]
		set_state(ref.category, ref.key, STATE_DONE)

	if ap_client.has_method("debug_log"):
		ap_client.debug_log(
			"AP EFFECT CHECK SENT location_id=" + str(location_id)
			+ " name=\"" + str(rule.get("name", APData.location_name(location_id))) + "\""
			+ " source=" + source_key
			+ " candidates=" + str(candidates)
			+ " vtc=" + str(effect.get("value_to_change", ""))
		)
	return true

func notify_effect_applied(owner, target, effect):
	# Called from the central LBAL effect engine after all comparisons succeeded.
	# Item/fine-print effects are deliberately ignored: these AP locations describe
	# native symbol effects, not an item coincidentally changing the same symbol.
	if not is_ap_mode_active() or ap_client == null:
		return false
	if typeof(effect) != TYPE_DICTIONARY:
		return false
	if effect.has("from_item"):
		return false

	var owner_key = _effect_object_type(owner)
	if owner_key == "":
		return false

	var target_key = _effect_object_type(target)
	if target_key == "":
		target_key = owner_key

	var giver_key = ""
	if effect.has("giver"):
		giver_key = _effect_object_type(effect.giver)
	var comparison_type_key = _effect_comparison_type_key(effect)

	# Reverse effects (Dog/Bee/Omelette style) are installed onto the source
	# symbol by the adjacent symbol. In every other normal adjacency effect,
	# giver is the source and owner is the target.
	var source_key = owner_key
	if giver_key != "" and not bool(effect.get("reverse_eff", false)):
		source_key = giver_key
	elif comparison_type_key != "" and (
		owner_key == ""
		or owner_key == "empty"
		or _effect_has_comparison(effect, "removed", true)
		or _effect_has_comparison(effect, "destroyed", true)
	):
		# Self-removal/self-destroy payout effects can run after the live icon has
		# already become Empty. Their type comparison still records the real source.
		source_key = comparison_type_key

	var candidates = []
	_append_effect_candidate(candidates, owner_key)
	_append_effect_candidate(candidates, target_key)
	_append_effect_candidate(candidates, giver_key)

	if effect.has("comparisons"):
		for comp in effect.comparisons:
			if typeof(comp) == TYPE_DICTIONARY and typeof(comp.get("b", null)) == TYPE_STRING:
				_append_effect_candidate(candidates, str(comp.b))

	if effect.has("tiles_to_add"):
		for added in effect.tiles_to_add:
			if typeof(added) == TYPE_DICTIONARY and added.has("type"):
				_append_effect_candidate(candidates, str(added.type))
			elif typeof(added) == TYPE_STRING and str(added) != "prev_destroyed_symbol":
				_append_effect_candidate(candidates, str(added))

	if effect.has("items_to_add"):
		for added in effect.items_to_add:
			if typeof(added) == TYPE_DICTIONARY and added.has("type"):
				_append_effect_candidate(candidates, str(added.type))

	if str(effect.get("value_to_change", "")) == "type" and typeof(effect.get("diff", null)) == TYPE_STRING:
		_append_effect_candidate(candidates, str(effect.diff))

	var matched = false

	# Pin ambiguous native effects to their exact LBAL conditions. These run in
	# addition to the generic matcher and are duplicate-safe through server state.
	var vtc = str(effect.get("value_to_change", ""))

	# Hex of Draining does not change value/value_bonus directly. LBAL marks the
	# randomly selected adjacent symbol with value_to_change="drained" and
	# hex_eff=true, then drained makes that symbol give 0 coins. The generic
	# "give" matcher intentionally ignores this non-numeric state change, so
	# send the exact AP check from the native drained effect itself.
	if source_key == "hex_of_draining" and vtc == "drained" and bool(effect.get("hex_eff", false)):
		if _send_named_ap_location_if_missing("Effect: Hex of Draining Makes a Symbol give 0", "AP HEX OF DRAINING"):
			matched = true

	if giver_key == "light_bulb" and (owner_key == "shiny_pebble" or target_key == "shiny_pebble") and vtc == "value_multiplier":
		if _send_named_ap_location_if_missing("Effect: Light Bulb Boosts Shiny Pebble", "AP LIGHT BULB SHINY PEBBLE"):
			matched = true

	if comparison_type_key in ["void_creature", "void_fruit", "void_stone"] and _effect_has_comparison(effect, "destroyed", true) and _effect_is_value_change(vtc):
		var void_payout_names = {
			"void_creature": "Effect: Void Creature Gives 8 Coins",
			"void_fruit": "Effect: Void Fruit Gives 8 Coins",
			"void_stone": "Effect: Void Stone Gives 8 Coins"
		}
		if _send_named_ap_location_if_missing(void_payout_names[comparison_type_key], "AP VOID 8 COIN"):
			matched = true

	# Most effect locations are owned by the symbol that caused the effect
	# (`source_key`). Amethyst and Pear are different: their AP locations describe
	# the target being boosted by another symbol. Include owner/target rule tables
	# too, then keep the normal source check for every non-target_boost rule.
	var rule_source_keys = []
	for key in [source_key, owner_key, target_key]:
		if key != "" and not rule_source_keys.has(key):
			rule_source_keys.append(key)

	for rule_source in rule_source_keys:
		for rule in APEffectData.rules_for_source(rule_source):
			var mode = str(rule.get("mode", "generic"))

			if mode == "manual" or mode == "thief_spin":
				continue

			# Amethyst/Pear gain their permanent bonus when another symbol boosts
			# them. The target itself identifies the AP location, not effect.giver.
			if mode == "target_boost":
				if owner_key != str(rule.source) and target_key != str(rule.source):
					continue
				if not _effect_is_value_change(str(effect.get("value_to_change", ""))):
					continue
				if effect.has("from_item"):
					continue
				if _send_effect_rule(rule, str(rule.source), candidates, effect):
					matched = true
				continue

			# Sand Dollar/Jellyfish/Pufferfish can reward normal removal OR native
			# destruction. The type comparison remains authoritative after the icon
			# itself has already become Empty.
			if mode == "removed_or_destroyed_reward":
				if comparison_type_key != str(rule.source):
					continue
				var was_removed = _effect_has_comparison(effect, "removed", true)
				var was_destroyed = _effect_has_comparison(effect, "destroyed", true)
				if not was_removed and not was_destroyed:
					continue
				if not _effect_kind_matches(rule, effect, owner_key, target_key, giver_key):
					continue
				if _send_effect_rule(rule, str(rule.source), candidates, effect):
					matched = true
				continue

			# Void symbols have two different checks with no named target:
			# boosting Empty, and the payout after they destroy themselves.
			if mode == "void_empty":
				if source_key != str(rule.source):
					continue
				if not candidates.has("empty"):
					continue
				if not _effect_is_value_change(str(effect.get("value_to_change", ""))):
					continue
				if _send_effect_rule(rule, source_key, candidates, effect):
					matched = true
				continue

			if mode == "void_destroy_bonus":
				# LBAL can already expose the destroyed Void icon as Empty when
				# the 8-coin payout effect runs. Its type comparison is authoritative.
				if comparison_type_key != str(rule.source):
					continue
				if not _effect_is_value_change(str(effect.get("value_to_change", ""))):
					continue
				if not _effect_has_comparison(effect, "destroyed", true):
					continue
				if _send_effect_rule(rule, str(rule.source), candidates, effect):
					matched = true
				continue

			if source_key != str(rule.source):
				continue
			if not _effect_rule_target_matches(rule, candidates):
				continue
			if not _effect_kind_matches(rule, effect, owner_key, target_key, giver_key):
				continue
			if _send_effect_rule(rule, source_key, candidates, effect):
				matched = true

	return matched


func notify_spawned_symbol_effect(source_type, spawned_type):
	# Some native effects choose a concrete symbol from a group only inside
	# do_diff(). Bartender is the important case: its effect dictionary says
	# "group: booze", but the AP checks distinguish Chemical Seven/Beer/Wine/
	# Martini. Report the actual symbol that LBAL selected.
	if not is_ap_mode_active() or ap_client == null:
		return false
	var source_key = APData.canonical_game_key_for_actual_type(str(source_type))
	var spawned_key = APData.canonical_game_key_for_actual_type(str(spawned_type))
	if source_key == "" or spawned_key == "":
		return false
	var candidates = [source_key, spawned_key]
	for rule in APEffectData.rules_for_source(source_key):
		if str(rule.get("mode", "generic")) == "manual":
			continue
		if str(rule.get("kind", "")) != "add":
			continue
		if not _effect_rule_target_matches(rule, candidates):
			continue
		var synthetic_effect = {
			"value_to_change": "",
			"tiles_to_add": [{"type": spawned_key}]
		}
		if _send_effect_rule(rule, source_key, candidates, synthetic_effect):
			return true
	return false

func notify_thief_spin():
	# Thief's "removes 1 coin" behavior is its base negative coin value rather than
	# a conditional effect, so it never enters notify_effect_applied().
	if not is_ap_mode_active() or ap_client == null:
		return false
	for rule in APEffectData.rules_for_source("thief"):
		if str(rule.get("mode", "")) == "thief_spin":
			return _send_effect_rule(rule, "thief", ["thief"], {"value_to_change": "base_coin_value"})
	return false

func get_effect_coverage_text():
	var duplicate_note = "APWorld warning: old seeds have Sun Seed Growth and Tedium Capsule sharing ID 850. New v42 APWorld moves Tedium Capsule to 857."
	return "Effect checks: " + str(APEffectData.EFFECT_RULE_COUNT) + " mapped across " + str(APEffectData.source_count()) + " source symbols. Central effect engine hook enabled; dedicated safety hooks: Crab, Present, Matryoshka, Thief. " + duplicate_note

func send_matryoshka_base_check(game_type = "matryoshka_doll"):
	# The first Matryoshka Send check is special because LBAL's actual symbol is
	# usually matryoshka_doll_1 while Archipelago calls the location simply
	# "Send: Matryoshka Doll". Send it from ANY observed Matryoshka stage as a
	# recovery path, so a missed reward-card callback can never leave the base
	# check stranded after the doll has already progressed.
	#
	# IMPORTANT: location 465 must use the AP server's checked/missing state as
	# the authority. Older builds could leave the local hook entry marked DONE
	# even though the server still reported 465 missing. The generic named helper
	# intentionally has a local-state duplicate guard, so using it here could
	# permanently strand only the first Matryoshka Send while stages 2-5 worked.
	if not is_ap_mode_active() or ap_client == null:
		return false
	var exact_key = APData.exact_game_key(game_type)
	if not exact_key in ["matryoshka_doll", "matryoshka_doll_1", "matryoshka_doll_2", "matryoshka_doll_3", "matryoshka_doll_4", "matryoshka_doll_5"]:
		return false
	var base_location_name = "Send: Matryoshka Doll"
	var resolved_location_name = _floor_variant_location_name(base_location_name)
	var location_id = APData.location_id(resolved_location_name)
	if location_id < 0:
		return false
	if ap_client.checked_locations.has(location_id):
		return false
	if ap_client.missing_locations.size() > 0 and not ap_client.missing_locations.has(location_id):
		return false

	# Network first. APClient immediately mirrors the ID into checked_locations
	# and removes it from missing_locations, which is the duplicate guard for any
	# other pickup/inventory/transition hook that runs in the same frame.
	if not ap_client.send_location_check(location_id):
		return false

	# Repair/synchronise the local hook state only AFTER the server-authoritative
	# send. Never use stale local state as a reason to suppress this check.
	if ap_location_index.has(location_id):
		var ref = ap_location_index[location_id]
		set_state(ref.category, ref.key, STATE_DONE)
	if ap_client.has_method("debug_log"):
		ap_client.debug_log("AP MATRYOSHKA BASE SEND SENT name=" + resolved_location_name + " location_id=" + str(location_id) + " source=" + exact_key + " server_authoritative=true")
	return true

func send_matryoshka_transition(from_type, to_type):
	# Each Matryoshka transform completes TWO locations at the same instant:
	# the Effect location and the Send location for the newly-created stage.
	# Use the server's checked/missing lists as the authority here; do not let a
	# stale local hook state suppress a real server-side missing location.
	if not is_ap_mode_active() or ap_client == null:
		return false
	# Also recover the base Send if the original reward-card callback was missed.
	var base_send_recovered = send_matryoshka_base_check(from_type)
	var from_key = APData.exact_game_key(from_type)
	var to_key = APData.exact_game_key(to_type)
	var pair_ids = []
	var pair_names = []
	match from_key:
		"matryoshka_doll_1":
			pair_ids = [786, 466]
			pair_names = ["Effect: Matryoshka Doll 1 turns into Matryoshka Doll 2", "Send: Matryoshka Doll 2"]
		"matryoshka_doll_2":
			pair_ids = [787, 467]
			pair_names = ["Effect: Matryoshka Doll 2 turn into Matryoshka Doll 3", "Send: Matryoshka Doll 3"]
		"matryoshka_doll_3":
			pair_ids = [788, 468]
			pair_names = ["Effect: Matryoshka Doll 3 turn into Matryoshka Doll 4", "Send: Matryoshka Doll 4"]
		"matryoshka_doll_4":
			pair_ids = [789, 469]
			pair_names = ["Effect: Matryoshka Doll 4 turn into Matryoshka Doll 5", "Send: Matryoshka Doll 5"]
		_:
			return base_send_recovered

	var location_ids = []
	var location_names = []
	for i in range(pair_ids.size()):
		var base_location_name = str(pair_names[i])
		var resolved_location_name = _floor_variant_location_name(base_location_name)
		var location_id = APData.location_id(resolved_location_name)
		if location_id < 0:
			continue
		# APClient updates checked_locations immediately when a packet is queued,
		# which also serves as the duplicate guard if LBAL evaluates this twice.
		if ap_client.checked_locations.has(location_id):
			continue
		# If the server supplied a missing list, only send locations that exist in
		# this seed. This prevents sending disabled locations in alternate YAMLs.
		if ap_client.missing_locations.size() > 0 and not ap_client.missing_locations.has(location_id):
			continue
		location_ids.append(location_id)
		location_names.append(resolved_location_name)

	if location_ids.size() == 0:
		if ap_client.has_method("debug_log"):
			ap_client.debug_log("AP MATRYOSHKA TRANSITION no missing pair from=" + from_key + " to=" + to_key + " expected=" + str(pair_ids))
		return base_send_recovered

	# One packet for both IDs, so Effect + Send complete at the same transform.
	if ap_client.has_method("send_location_checks"):
		ap_client.send_location_checks(location_ids)
	else:
		for location_id in location_ids:
			ap_client.send_location_check(int(location_id))

	# Keep local hook state in sync AFTER networking. Never use it as the gate.
	for location_id in location_ids:
		if ap_location_index.has(int(location_id)):
			var ref = ap_location_index[int(location_id)]
			set_state(ref.category, ref.key, STATE_DONE)

	if ap_client.has_method("debug_log"):
		ap_client.debug_log("AP MATRYOSHKA TRANSITION SENT from=" + from_key + " to=" + to_key + " locations=" + str(location_ids) + " names=" + str(location_names) + " batched=true")
	return true

func send_crab_same_row_check():
	# Crab's native effect gives its bonus when another Crab is displayed in the
	# same reel row. Complete the AP effect location at that exact condition.
	# The named-location helper also provides checked/missing and duplicate guards.
	return _send_named_ap_location_if_missing(
		"Effect: Crab in same row",
		"AP CRAB SAME ROW EFFECT"
	)

func send_present_self_destroy_check():
	# Present has a native timed self-destruction. Complete only that effect
	# location here; other ways of destroying Present (for example Toddler)
	# have their own AP effect checks.
	if not is_ap_mode_active() or ap_client == null:
		return false
	var base_location_name = "Effect: Present Destroys itself"
	var resolved_location_name = _floor_variant_location_name(base_location_name)
	var location_id = APData.location_id(resolved_location_name)
	if location_id < 0:
		return false
	if ap_client.checked_locations.has(location_id):
		return false
	if ap_client.missing_locations.size() > 0 and not ap_client.missing_locations.has(location_id):
		return false

	# Network first, then mirror the local check state. The server's checked/
	# missing lists are authoritative so a stale hook state cannot block it.
	ap_client.send_location_check(location_id)
	if ap_location_index.has(location_id):
		var ref = ap_location_index[location_id]
		set_state(ref.category, ref.key, STATE_DONE)
	if ap_client.has_method("debug_log"):
		ap_client.debug_log("AP PRESENT SELF-DESTROY CHECK SENT location_id=" + str(location_id) + " name=" + resolved_location_name)
	return true

func send_pickup_check(game_type, source_category = ""):
	if not is_ap_mode_active():
		return false
	if ap_client == null:
		return false

	# Matryoshka's first visible LBAL stage is matryoshka_doll_1, but its base AP
	# location is named "Send: Matryoshka Doll".  Send that named location first
	# and independently from the generic stage mapping.  This makes the base check
	# reliable even if the stage key has a Steam/mod suffix.
	var exact_game_type = APData.exact_game_key(game_type)
	var matryoshka_base_sent = false
	if exact_game_type in ["matryoshka_doll", "matryoshka_doll_1", "matryoshka_doll_2", "matryoshka_doll_3", "matryoshka_doll_4", "matryoshka_doll_5"]:
		matryoshka_base_sent = send_matryoshka_base_check(game_type)

	var location_ids = APData.send_location_ids_for_game_type(game_type)
	if location_ids.size() == 0:
		_hook_debug("AP PICKUP CHECK no Send mapping game_type=" + str(game_type) + " category=" + str(source_category))
		return false

	var sent_ids = []
	for raw_location_id in location_ids:
		var location_id = _floor_variant_location_id(int(raw_location_id))
		# Never resend a location the server already considers checked.
		if ap_client.checked_locations.has(location_id):
			continue
		# When the server supplied a missing-location set, only send checks that
		# actually belong to this slot's current seed.
		if ap_client.missing_locations.size() > 0 and not ap_client.missing_locations.has(location_id):
			continue
		done_location_id(location_id, true)
		sent_ids.append(location_id)

	var initial_matryoshka_effect_sent = false
	if exact_game_type == "matryoshka_doll_1":
		initial_matryoshka_effect_sent = _send_named_ap_location_if_missing(
			"Effect: Matryoshka Doll turns into Matryoshka Doll 1",
			"AP MATRYOSHKA EFFECT"
		)

	if sent_ids.size() > 0 and ap_client.has_method("debug_log"):
		ap_client.debug_log("AP PICKUP CHECK SENT game_type=" + str(game_type) + " category=" + str(source_category) + " locations=" + str(sent_ids))
	else:
		_hook_debug("AP PICKUP CHECK already complete/not missing game_type=" + str(game_type) + " category=" + str(source_category) + " mapped=" + str(location_ids))
	return sent_ids.size() > 0 or initial_matryoshka_effect_sent or matryoshka_base_sent

# Send the floor/payment location the moment rent is successfully paid.
# Payment numbers are 1-based and APData uses names such as
# "Floor 13 Payment 1".
func send_payment_check(floor_number, payment_number):
	if not is_ap_mode_active() or ap_client == null:
		return false
	# A Force Payment trap only suppresses DeathLink if it actually causes a loss.
	# Paying that forced rent successfully clears the one-shot suppression.
	if ap_client.has_method("clear_force_payment_deathlink_suppression"):
		ap_client.clear_force_payment_deathlink_suppression()
	var location_name = "Floor " + str(int(floor_number)) + " Payment " + str(int(payment_number))
	if not APData.LOCATION_NAME_TO_ID.has(location_name):
		if ap_client.has_method("debug_log"):
			ap_client.debug_log("AP PAYMENT CHECK no mapping name=" + location_name)
		return false
	var location_id = int(APData.LOCATION_NAME_TO_ID[location_name])
	if ap_client.checked_locations.has(location_id):
		return false
	if ap_client.missing_locations.size() > 0 and not ap_client.missing_locations.has(location_id):
		if ap_client.has_method("debug_log"):
			ap_client.debug_log("AP PAYMENT CHECK not missing name=" + location_name + " location_id=" + str(location_id))
		return false
	done_location_id(location_id, true)
	if ap_client.has_method("debug_log"):
		ap_client.debug_log("AP PAYMENT CHECK SENT floor=" + str(int(floor_number)) + " payment=" + str(int(payment_number)) + " location_id=" + str(location_id))
	return true

# =============================================================================
# SYMBOLS
# =============================================================================

func lock_symbol(key): return set_state(CAT_SYMBOL, key, STATE_LOCKED)
func unlock_symbol(key): return set_state(CAT_SYMBOL, key, STATE_UNLOCKED)
func done_symbol(key): return set_state(CAT_SYMBOL, key, STATE_DONE)

# =============================================================================
# ITEMS
# =============================================================================

func lock_item(key): return set_state(CAT_ITEM, key, STATE_LOCKED)
func unlock_item(key): return set_state(CAT_ITEM, key, STATE_UNLOCKED)
func done_item(key): return set_state(CAT_ITEM, key, STATE_DONE)

# =============================================================================
# ESSENCES
# =============================================================================

func lock_essence(key): return set_state(CAT_ESSENCE, key, STATE_LOCKED)
func unlock_essence(key): return set_state(CAT_ESSENCE, key, STATE_UNLOCKED)
func done_essence(key): return set_state(CAT_ESSENCE, key, STATE_DONE)

# =============================================================================
# ABILITIES
# =============================================================================

func lock_ability(key): return set_state(CAT_ABILITY, key, STATE_LOCKED)
func unlock_ability(key): return set_state(CAT_ABILITY, key, STATE_UNLOCKED)
func done_ability(key): return set_state(CAT_ABILITY, key, STATE_DONE)

# =============================================================================
# FLOORS
# =============================================================================

func lock_floor(floor_number): return set_state(CAT_FLOOR, str(int(floor_number)), STATE_LOCKED)
func unlock_floor(floor_number): return set_state(CAT_FLOOR, str(int(floor_number)), STATE_UNLOCKED)
func done_floor(floor_number): return set_state(CAT_FLOOR, str(int(floor_number)), STATE_DONE)

func _received_item_id(item):
	if typeof(item) == TYPE_DICTIONARY:
		return int(item.get("item", -1))
	if typeof(item) == TYPE_ARRAY and item.size() > 0:
		return int(item[0])
	return -1

func _has_received_ap_item(item_id):
	if ap_client == null:
		return false
	var received = ap_client.get("received_items")
	if typeof(received) != TYPE_ARRAY:
		return false
	for network_item in received:
		if _received_item_id(network_item) == int(item_id):
			return true
	return false

func _count_received_ap_item(item_id):
	if ap_client == null:
		return 0
	var count = 0
	var received = ap_client.get("received_items")
	if typeof(received) != TYPE_ARRAY:
		return 0
	for network_item in received:
		if _received_item_id(network_item) == int(item_id):
			count += 1
	return count

func sync_floor_unlocks_from_received_items():
	# Keep v16 hook states authoritative, but replay the AP client's actual item
	# history into them.  Never reset an already-unlocked floor back to LOCKED.
	_ensure_ap_client_bound()
	if not hooks[CAT_FLOOR].has("1"):
		register_floor(1, -1, STATE_UNLOCKED)
	else:
		set_state(CAT_FLOOR, "1", STATE_UNLOCKED)
	for floor_number in range(2, 21):
		if not hooks[CAT_FLOOR].has(str(floor_number)):
			register_floor(floor_number, 373 + floor_number, STATE_LOCKED)
	_replay_received_items_into_hook_states(true)
	return get_unlocked_floor_numbers()

func get_unlocked_floor_numbers():
	# v16 behavior: floor hook states are the source of truth.
	var result = [1]
	if not is_ap_mode_active():
		for floor_number in range(2, 21):
			result.push_back(floor_number)
		return result
	for floor_number in range(2, 21):
		if get_state(CAT_FLOOR, str(floor_number)) >= STATE_UNLOCKED:
			result.push_back(floor_number)
	return result

func is_floor_locked(floor_number):
	# Offline/disconnected: AP must not restrict normal LBAL floor progression.
	if not is_ap_mode_active():
		return false
	return get_state(CAT_FLOOR, str(int(floor_number))) == STATE_LOCKED

func is_floor_unlocked(floor_number):
	# v16 behavior: hook state is set directly when a floor AP item is received.
	if not is_ap_mode_active():
		return true
	if int(floor_number) == 1:
		return true
	return get_state(CAT_FLOOR, str(int(floor_number))) >= STATE_UNLOCKED

func is_floor_done(floor_number):
	if not is_ap_mode_active():
		return false
	return get_state(CAT_FLOOR, str(int(floor_number))) == STATE_DONE

func get_highest_contiguous_unlocked_floor():
	# The Title floor menu takes min(vanilla_highest, this value). Returning 20
	# offline means the AP layer has no effect at all until authentication.
	if not is_ap_mode_active():
		return 20
	var highest = 1
	for floor_number in range(2, 21):
		if is_floor_unlocked(floor_number):
			highest = floor_number
		else:
			break
	return highest

# =============================================================================
# GENERIC STATE HELPERS
# =============================================================================

func set_state(category, key, new_state):
	category = _normalise_category(category)
	key = str(key)
	if not hooks.has(category):
		return null
	if not hooks[category].has(key):
		# Allows quick hooks without registration. Add AP IDs later with register_*.
		register_hook(category, key, -1, STATE_LOCKED)

	var entry = hooks[category][key]
	new_state = int(clamp(int(new_state), STATE_LOCKED, STATE_DONE))
	if int(entry.state) == new_state:
		return entry

	entry.state = new_state
	hooks[category][key] = entry
	_apply_state_to_game(category, key, new_state, entry)
	emit_signal("hook_changed", category, key, new_state, int(entry.ap_id), entry.data)
	_emit_category_signal(category, key, new_state, entry)
	var hook_line = "HOOK STATE category=" + category + " key=" + key + " state=" + state_name(new_state) + " ap_id=" + str(entry.ap_id)
	_hook_debug(hook_line)
	return entry

func get_state(category, key):
	category = _normalise_category(category)
	key = str(key)
	if hooks.has(category) and hooks[category].has(key):
		return int(hooks[category][key].state)
	return STATE_LOCKED

func is_locked(category, key): return get_state(category, key) == STATE_LOCKED
func is_unlocked(category, key): return get_state(category, key) >= STATE_UNLOCKED
func is_done(category, key): return get_state(category, key) == STATE_DONE

func get_hook(category, key):
	category = _normalise_category(category)
	key = str(key)
	if hooks.has(category):
		return hooks[category].get(key, null)
	return null

func state_name(state):
	match int(state):
		STATE_LOCKED: return "LOCKED"
		STATE_UNLOCKED: return "UNLOCKED"
		STATE_DONE: return "DONE"
	return "UNKNOWN"

# Rebuild unlock state from APClient.received_items without replaying traps/buffs.
# This is deliberately independent of item_received signals so floor/symbol/item
# unlocks recover even if a signal was missed during startup or reconnect.
func _replay_received_items_into_hook_states(force = false):
	if ap_client == null:
		return
	var received = ap_client.get("received_items")
	if typeof(received) != TYPE_ARRAY:
		return
	if not force and received.size() == _last_received_replay_count:
		return
	_last_received_replay_count = received.size()
	var floor_ids = []
	for network_item in received:
		var item_id = _received_item_id(network_item)
		if item_id < 0:
			continue
		_apply_item_unlock_state_only(item_id)
		if item_id >= 375 and item_id <= 393:
			floor_ids.push_back(item_id)
	_hook_debug("HOOK REPLAY received_count=" + str(received.size()) + " floor_item_ids=" + str(floor_ids) + " visible_floors=" + str(get_unlocked_floor_numbers()))

func _apply_item_unlock_state_only(item_id):
	item_id = int(item_id)
	if item_id >= 375 and item_id <= 393:
		var floor_number = item_id - 373
		unlock_floor(floor_number)

	var matched = false
	for category in [CAT_SYMBOL, CAT_ITEM, CAT_ESSENCE, CAT_ABILITY, CAT_FLOOR]:
		for hook_key in hooks[category].keys():
			var hook_entry = hooks[category][hook_key]
			if int(hook_entry.ap_id) == item_id:
				set_state(category, hook_key, STATE_UNLOCKED)
				matched = true
	if not matched:
		var ref = _auto_register_ap_item(item_id)
		if ref != null:
			set_state(ref.category, ref.key, STATE_UNLOCKED)

# =============================================================================
# AP CLIENT -> HOOKS
# =============================================================================

func _on_ap_item_received(item_id, location_id = -1, player_id = -1, flags = 0, receive_index = -1):
	item_id = int(item_id)
	_hook_debug("HOOK ITEM EVENT item_id=" + str(item_id) + " location_id=" + str(location_id) + " player_id=" + str(player_id) + " flags=" + str(flags) + " receive_index=" + str(receive_index))

	# Unlock-state processing is done first and is intentionally independent from
	# consumable buff/trap effects.  A broken effect can no longer block floor/item
	# unlocks from being recorded.
	_apply_item_unlock_state_only(item_id)
	if item_id >= 375 and item_id <= 393:
		_hook_debug("AP FLOOR ITEM RECEIVED item_id=" + str(item_id) + " floor=" + str(item_id - 373) + " state=UNLOCKED")
	_apply_special_ap_item_effect(item_id, receive_index)

	_strict_filter_live_symbol_pools()
	_on_received_item_event(item_id, int(location_id), int(player_id), int(flags), int(receive_index))

func _permanent_buff_counts():
	var counts = {394: 0, 395: 0, 396: 0, 397: 0, 398: 0, 411: 0}
	if ap_client == null or not ap_client.has_method("is_connected_to_ap") or not ap_client.is_connected_to_ap():
		return counts
	# APClient.received_items is authoritative for the current slot.  v31 clears it
	# on disconnect/slot switch, so permanent bonuses cannot leak between slots.
	for entry in ap_client.received_items:
		var item_id = -1
		if typeof(entry) == TYPE_DICTIONARY:
			item_id = int(entry.get("item", -1))
		elif typeof(entry) == TYPE_ARRAY and entry.size() > 0:
			item_id = int(entry[0])
		if counts.has(item_id):
			counts[item_id] = int(counts[item_id]) + 1
	return counts

func _reset_current_run_permanent_buff_counts():
	_run_permanent_buff_counts = {394: 0, 395: 0, 396: 0, 397: 0, 398: 0, 411: 0}

func _mark_permanent_buff_applied_this_run(item_id):
	item_id = int(item_id)
	if not _run_permanent_buff_counts.has(item_id):
		return
	var main = get_node_or_null("/root/Main")
	if main == null or str(main.current_menu_path) != "slots":
		return
	_run_permanent_buff_counts[item_id] = int(_run_permanent_buff_counts[item_id]) + 1

func _watch_permanent_run_buffs():
	var main = get_node_or_null("/root/Main")
	var popup = get_node_or_null("/root/Main/Pop-up Sprite/Pop-up")
	if main == null or popup == null:
		return
	var menu = str(main.current_menu_path)
	var spins = int(popup.spins)

	# IMPORTANT: opening any normal email/popup changes current_menu_path away from
	# "slots".  v21 treated *every* non-slots menu as leaving the run, so resolving
	# a Starting Symbol choice at spin 0 immediately re-armed and re-applied every
	# permanent buff.  That created an endless symbol-choice loop and repeatedly
	# added permanent reroll/removal/essence tokens.
	#
	# Only arm after a real run boundary (title/floor menu), or when LBAL resets the
	# spin counter.  The email/inventory/options menus are part of the current run.
	if menu == "title" or menu == "floor_menu":
		_run_buff_armed = true
	if _run_buff_last_spins >= 0 and spins < _run_buff_last_spins:
		_run_buff_armed = true

	if menu == "slots" and spins == 0 and _run_buff_armed:
		_reset_current_run_permanent_buff_counts()
		if ap_client != null and ap_client.has_method("reset_deathlink_run_state"):
			ap_client.reset_deathlink_run_state()
		_run_buff_armed = false
		_apply_missing_permanent_buffs_for_current_run()

	_run_buff_last_menu = menu
	_run_buff_last_spins = spins

func _apply_missing_permanent_buffs_for_current_run():
	if ap_client == null or not ap_client.has_method("is_connected_to_ap") or not ap_client.is_connected_to_ap():
		return
	var main = get_node_or_null("/root/Main")
	var popup = get_node_or_null("/root/Main/Pop-up Sprite/Pop-up")
	var coins = get_node_or_null("/root/Main/Coins")
	if main == null or popup == null or str(main.current_menu_path) != "slots":
		return
	# These are starting bonuses, so only backfill them before the first spin.
	# Items received later still apply immediately and then persist next run.
	if int(popup.spins) != 0:
		return

	var totals = _permanent_buff_counts()
	var add_symbols = max(0, int(totals[394]) - int(_run_permanent_buff_counts[394]))
	var add_money = max(0, int(totals[395]) - int(_run_permanent_buff_counts[395]))
	var add_removal = max(0, int(totals[396]) - int(_run_permanent_buff_counts[396]))
	var add_reroll = max(0, int(totals[397]) - int(_run_permanent_buff_counts[397]))
	var add_essence = max(0, int(totals[398]) - int(_run_permanent_buff_counts[398]))
	var add_items = max(0, int(totals[411]) - int(_run_permanent_buff_counts[411]))

	for _i in range(add_symbols):
		popup.add_event("add_tile", {"forced_rarity": []})
	for _i in range(add_items):
		popup.add_event("add_item",        {})
	if coins != null and add_money > 0:
		coins.coins += 5 * add_money
	popup.removal_tokens += add_removal
	popup.reroll_tokens += add_reroll
	popup.essence_tokens += add_essence

	for item_id in [394, 395, 396, 397, 398, 411]:
		_run_permanent_buff_counts[item_id] = int(totals[item_id])

	if ap_client.has_method("debug_log") and (add_symbols + add_money + add_removal + add_reroll + add_essence + add_items) > 0:
		ap_client.debug_log("AP PERMANENT BUFFS run_start added_symbol_choices=" + str(add_symbols) + " starting_money=+" + str(5 * add_money) + " removal_tokens=+" + str(add_removal) + " reroll_tokens=+" + str(add_reroll) + " essence_tokens=+" + str(add_essence) + " starting_items=+" + str(add_items) + " totals=" + str(totals))

func apply_permanent_buffs_for_new_run():
	_apply_missing_permanent_buffs_for_current_run()

func _apply_special_ap_item_effect(item_id, receive_index):
	item_id = int(item_id)
	receive_index = int(receive_index)
	if not [394, 395, 396, 397, 398, 399, 400, 401, 403, 404, 410, 411].has(item_id):
		return
	_load_special_effect_state()
	if _processed_special_receive_indexes.has(receive_index):
		# Reconnect replays ReceivedItems to rebuild state. Keep this expected path
		# quiet unless explicit hook background logging is enabled.
		if hook_background_logging:
			_hook_debug("AP EFFECT skipped already applied item_id=" + str(item_id) + " receive_index=" + str(receive_index))
		return
	_processed_special_receive_indexes[receive_index] = true
	_save_special_effect_state()

	var main = get_node_or_null("/root/Main")
	var popup = get_node_or_null("/root/Main/Pop-up Sprite/Pop-up")
	var reels = get_node_or_null("/root/Main/Reels")
	var coins = get_node_or_null("/root/Main/Coins")
	if main == null or popup == null:
		return

	match item_id:
		394:
			# Buff: Starting Symbol (legacy name: Symbol Bomb) -- give a normal symbol choice.
			popup.add_event("add_tile", {"forced_rarity": []})
			_mark_permanent_buff_applied_this_run(item_id)
			_debug_special_effect("BUFF Starting Symbol -> queued symbol choice", item_id, receive_index)
		395:
			# Buff: +5 immediately and +5 starting money on every future run.
			if coins != null:
				coins.coins += 5
			_mark_permanent_buff_applied_this_run(item_id)
			_debug_special_effect("BUFF +5 coins", item_id, receive_index)
		396:
			popup.removal_tokens += 1
			_mark_permanent_buff_applied_this_run(item_id)
			_debug_special_effect("BUFF +1 removal token", item_id, receive_index)
		397:
			popup.reroll_tokens += 1
			_mark_permanent_buff_applied_this_run(item_id)
			_debug_special_effect("BUFF +1 reroll token", item_id, receive_index)
		398:
			popup.essence_tokens += 1
			_mark_permanent_buff_applied_this_run(item_id)
			_debug_special_effect("BUFF +1 essence token", item_id, receive_index)
		399:
			# Trap: halve the EFFECTIVE balance, including any coin animation that
			# is still queued. During rent payment LBAL can temporarily have e.g.
			# coins=122 and queued_increase=-88 while the real balance is 34.
			# Halving only coins would leave the -88 queued and drive the player
			# negative. Collapse the queue first, then apply the half-money result.
			if coins != null:
				var base_before = int(coins.coins)
				var queued_before = int(coins.queued_increase) if coins.get("queued_increase") != null else 0
				var effective_before = base_before + queued_before
				var effective_after = effective_before
				if effective_before > 0:
					effective_after = max(1, int(floor(float(effective_before) / 2.0)))
				coins.coins = effective_after
				if coins.get("queued_increase") != null:
					coins.queued_increase = 0
				_debug_special_effect("TRAP half money base_before=" + str(base_before) + " queued_before=" + str(queued_before) + " effective_before=" + str(effective_before) + " after=" + str(effective_after), item_id, receive_index)
		400:
			# Trap: make rent due at the next safe game update. If this forced
			# payment causes the run to fail, do NOT send a DeathLink back out.
			if ap_client != null and ap_client.has_method("arm_force_payment_deathlink_suppression"):
				ap_client.arm_force_payment_deathlink_suppression()
			popup.rent_values[1] = 0
			_debug_special_effect("TRAP force payment -> spins_remaining=0 deathlink_suppressed_if_loss=true", item_id, receive_index)
		401:
			# Trap: add one native Dud to the inventory.
			if reels != null:
				reels.add_tile(["dud"])
				reels.update_icon_types()
			_debug_special_effect("TRAP added Dud symbol", item_id, receive_index)
		403:
			# One-time filler reward: immediately add 1 coin.
			if coins != null:
				coins.coins += 1
			_debug_special_effect("FILLER +1 coin", item_id, receive_index)
		404:
			# One-time filler reward: immediately add 3 coins.
			if coins != null:
				coins.coins += 3
			_debug_special_effect("FILLER +3 coins", item_id, receive_index)
		410:
			# One-time filler reward: immediately add 5 coins.
			if coins != null:
				coins.coins += 5
			_debug_special_effect("FILLER +5 coins", item_id, receive_index)
		411:
			# Permanent buff: one extra item choice now and at the start of every future run.
			popup.add_event("add_item",        {})
			_mark_permanent_buff_applied_this_run(item_id)
			_debug_special_effect("BUFF Starting Item -> queued item choice", item_id, receive_index)

func _debug_special_effect(message, item_id, receive_index):
	if ap_client != null and ap_client.has_method("debug_log"):
		ap_client.debug_log("AP EFFECT " + str(message) + " item_id=" + str(item_id) + " receive_index=" + str(receive_index))

func _special_effect_state_key():
	if ap_client == null:
		return "unknown"
	return str(ap_client.server_address) + "|" + str(ap_client.seed_name) + "|" + str(ap_client.slot_name)

func _load_special_effect_state():
	var state_key = _special_effect_state_key()
	if _special_effect_state_loaded_key == state_key:
		return
	_special_effect_state_loaded_key = state_key
	_processed_special_receive_indexes.clear()
	var file = File.new()
	if not file.file_exists(SPECIAL_EFFECT_STATE_PATH):
		return
	if file.open(SPECIAL_EFFECT_STATE_PATH, File.READ) != OK:
		return
	var parsed = JSON.parse(file.get_as_text())
	file.close()
	if parsed.error != OK or typeof(parsed.result) != TYPE_DICTIONARY:
		return
	if not parsed.result.has(state_key) or typeof(parsed.result[state_key]) != TYPE_ARRAY:
		return
	for raw_index in parsed.result[state_key]:
		_processed_special_receive_indexes[int(raw_index)] = true

func _save_special_effect_state():
	var state_key = _special_effect_state_key()
	var all_state = {}
	var file = File.new()
	if file.file_exists(SPECIAL_EFFECT_STATE_PATH) and file.open(SPECIAL_EFFECT_STATE_PATH, File.READ) == OK:
		var parsed = JSON.parse(file.get_as_text())
		file.close()
		if parsed.error == OK and typeof(parsed.result) == TYPE_DICTIONARY:
			all_state = parsed.result
	var indexes = []
	for raw_index in _processed_special_receive_indexes.keys():
		indexes.push_back(int(raw_index))
	indexes.sort()
	all_state[state_key] = indexes
	if file.open(SPECIAL_EFFECT_STATE_PATH, File.WRITE) == OK:
		file.store_string(JSON.print(all_state))
		file.close()

func _on_ap_locations_updated(checked, missing):
	# Checked locations are definitely DONE.
	for location_id in checked:
		location_id = int(location_id)
		if not ap_location_index.has(location_id):
			register_check("location_" + str(location_id), location_id, STATE_LOCKED)
		var ref = ap_location_index[location_id]
		set_state(ref.category, ref.key, STATE_DONE)

	# IMPORTANT: AP's missing_locations means "not checked yet". It does NOT mean
	# the location is currently in logic. We therefore do not automatically call
	# unlock_check() for missing locations. Your gameplay hook should do that.
	_on_locations_sync_event(checked, missing)
	_sync_ap_check_completion_state()

func _on_location_check_sent(location_id):
	location_id = int(location_id)
	if not ap_location_index.has(location_id):
		register_check("location_" + str(location_id), location_id, STATE_UNLOCKED)
	var ref = ap_location_index[location_id]
	set_state(ref.category, ref.key, STATE_DONE)
	_sync_ap_check_completion_state()

func _on_deathlink_received(data):
	if ap_client == null or not ap_client.deathlink_enabled:
		return
	var main = get_node_or_null("/root/Main")
	var popup = get_node_or_null("/root/Main/Pop-up Sprite/Pop-up")
	if main == null or popup == null:
		return
	var menu_name = str(main.current_menu_path)
	if menu_name == "/root/Main/Title" or menu_name == "floor_menu":
		ap_client.debug_log("DEATHLINK received while no run is active; ignored")
		return

	var source = str(data.get("source", "Unknown")) if typeof(data) == TYPE_DICTIONARY else "Unknown"
	var cause = str(data.get("cause", "")) if typeof(data) == TYPE_DICTIONARY else ""
	if int(ap_client.deathlink_mode) == 0:
		# Same behavior as the Force Payment trap. Arm suppression first so a failed
		# forced payment cannot bounce the received DeathLink back to everyone.
		if ap_client.has_method("arm_force_payment_deathlink_suppression"):
			ap_client.arm_force_payment_deathlink_suppression()
		popup.rent_values[1] = 0
		ap_client.debug_log("DEATHLINK EFFECT Force Payment source=" + source + " cause=" + cause)
	else:
		# Native game-over event, without bouncing a second DeathLink back.
		if ap_client.has_method("suppress_next_deathlink_for_remote_loss"):
			ap_client.suppress_next_deathlink_for_remote_loss()
		popup.add_event("game_over", {"push_front": true})
		popup.delay_timer = 0
		popup.call_deferred("draw")
		ap_client.debug_log("DEATHLINK EFFECT End Run source=" + source + " cause=" + cause)

func _auto_register_ap_item(item_id):
	# These ranges come from the APWorld you supplied. They make raw AP item IDs
	# immediately useful even before you give them nicer game keys below.
	if item_id >= 1 and item_id <= 149:
		var key = "ap_symbol_" + str(item_id)
		register_symbol(key, item_id)
		return ap_item_index[item_id]
	elif (item_id >= 150 and item_id <= 262) or item_id == 408:
		var key = "ap_item_" + str(item_id)
		register_item(key, item_id)
		return ap_item_index[item_id]
	elif (item_id >= 263 and item_id <= 374) or item_id == 407 or item_id == 409:
		var key = "ap_essence_" + str(item_id)
		register_essence(key, item_id)
		return ap_item_index[item_id]
	elif item_id >= 375 and item_id <= 393:
		var floor_number = item_id - 373
		if not hooks[CAT_FLOOR].has(str(floor_number)):
			register_floor(floor_number, item_id)
		return ap_item_index[item_id]

	# Buffs/traps/progressive items and future APWorld additions are deliberately
	# left generic. Register them as abilities (or another group) yourself.
	return null

func _register_default_floor_hooks():
	# Floor 1 is the base game floor and has no AP unlock item in this APWorld.
	register_floor(1, -1, STATE_UNLOCKED)
	# APWorld IDs 375..393 are Floor 2..20 Unlock.
	for floor_number in range(2, 21):
		register_floor(floor_number, 373 + floor_number, STATE_LOCKED)

# =============================================================================
# EDIT THESE GAME CALLBACKS
# =============================================================================
# This is the section intended for your own game-side hooks.
# The state database above is already handled for you. Put the actual LBAL game
# changes in these functions (hide a symbol, block an item, enable a floor, etc.).
# =============================================================================

func _apply_state_to_game(category, key, state, entry):
	match category:
		CAT_CHECK: _apply_check_state(key, state, entry)
		CAT_SYMBOL: _apply_symbol_state(key, state, entry)
		CAT_ITEM: _apply_item_state(key, state, entry)
		CAT_ESSENCE: _apply_essence_state(key, state, entry)
		CAT_ABILITY: _apply_ability_state(key, state, entry)
		CAT_FLOOR: _apply_floor_state(key, state, entry)

func _apply_check_state(key, state, entry):
	# EDIT HERE: enable/disable the game event that is allowed to send this check.
	# When the event actually happens, call done_check(key, true).
	pass

func _apply_symbol_state(key, state, entry):
	# Symbol selection is enforced non-destructively by filter_symbol_pool().
	# Keeping the global rarity database intact prevents crashes in unrelated LBAL code.
	pass

func _apply_item_state(key, state, entry):
	# Item choices are enforced non-destructively by filter_item_pool().
	pass

func _apply_essence_state(key, state, entry):
	# Essence choices are enforced non-destructively by filter_item_pool().
	pass

func _apply_ability_state(key, state, entry):
	# EDIT HERE: toggle AP/mod abilities or gameplay effects.
	pass

func _apply_floor_state(key, state, entry):
	# EDIT HERE: key is the floor number as text, e.g. "5".
	# This is where you can hide/disable locked floor arrows and enable unlocked floors.
	pass

# Raw events are provided too, useful when you want to build custom behavior.
func _on_received_item_event(item_id, location_id, player_id, flags, receive_index):
	pass

func _on_locations_sync_event(checked, missing):
	pass

func _emit_category_signal(category, key, state, entry):
	match category:
		CAT_CHECK: emit_signal("check_changed", key, state, int(entry.ap_id), entry.data)
		CAT_SYMBOL: emit_signal("symbol_changed", key, state, int(entry.ap_id), entry.data)
		CAT_ITEM: emit_signal("item_changed", key, state, int(entry.ap_id), entry.data)
		CAT_ESSENCE: emit_signal("essence_changed", key, state, int(entry.ap_id), entry.data)
		CAT_ABILITY: emit_signal("ability_changed", key, state, int(entry.ap_id), entry.data)
		CAT_FLOOR: emit_signal("floor_changed", key, state, int(entry.ap_id), entry.data)

func _normalise_category(category):
	var c = str(category).to_lower()
	match c:
		"check", "checks": return CAT_CHECK
		"symbol", "symbols": return CAT_SYMBOL
		"item", "items": return CAT_ITEM
		"essence", "essences": return CAT_ESSENCE
		"ability", "abilities": return CAT_ABILITY
		"floor", "floors": return CAT_FLOOR
	return c
