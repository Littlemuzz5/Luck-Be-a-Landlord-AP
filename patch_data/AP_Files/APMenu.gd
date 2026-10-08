extends Node

var main
var title
var options
var ap_client

var server = "archipelago.gg:38281"
var slot_name = ""
var password = ""

var current_screen = ""
var editing_field = ""
var edit_backup = ""
var edit_value = ""

var server_button
var slot_button
var password_button
var connect_button
var ap_check_boost_button
var deathlink_button
var deathlink_send_amnesty_button
var deathlink_receive_amnesty_button
var text_client_button
var text_client_filter_button
var back_button
var apworld_version_label = null
var apworld_version_label_last_text = ""
var apworld_version_label_last_state = ""

# Number of DeathLink events to forgive before the next one is sent/applied.
# Zero disables amnesty. These are local client settings and remain compatible
# with older APWorlds that do not provide amnesty in slot_data.
const DEATHLINK_AMNESTY_VALUES = [0, 1, 2, 3, 5, 10]

# Hidden developer console. F10 + R launches a separate Windows console window.
const DEBUG_LOG_PATH = "user://LBAL-AP-Debug.log"
const DEBUG_COMMAND_PATH = "user://LBAL-AP-Debug.commands"
const DEBUG_SCRIPT_SOURCE = "res://APDebugConsole.ps1"
const DEBUG_SCRIPT_COPY = "user://LBAL-AP-DebugConsole.ps1"
# Compact LBAL-style Shiny Coin counter shown above the normal Options button.
var shiny_coin_hud = null
var shiny_coin_hud_last_text = ""
var goal_floor_hud = null
var goal_floor_hud_last_text = ""
# Countdown of local run-ending deaths until this client next SENDS a DeathLink.
# This is amnesty_remaining + 1: with send amnesty 2 it shows DL 3, then DL 2,
# then DL 1, and the following local death sends and resets the counter.
var deathlink_send_hud = null
var deathlink_send_hud_last_text = ""
var text_client_hud = null
var text_client_hud_last_text = ""
var shiny_coin_hud_refresh_timer = 0.0
var connection_status_refresh_timer = 0.0

var debug_console_pid = -1
var debug_command_line = 0
var debug_poll_timer = 0.0

var saved_info_text_mod = 0
var saved_mod_text_mod = 0
var saved_info_scale_mod = 0
var saved_mod_scale_mod = 0

func _ready():
	main = get_parent()
	title = main.get_node("Title")
	options = main.get_node("Options Sprite/Options")
	ap_client = main.get_node("AP Client")
	ap_client.connect("status_changed", self, "_on_ap_status_changed")
	ap_client.connect("debug_changed", self, "_on_ap_debug_changed")
	if ap_client.has_signal("connected_to_ap"):
		ap_client.connect("connected_to_ap", self, "_on_ap_connected")
	if ap_client.has_signal("shiny_coin_progress_changed"):
		ap_client.connect("shiny_coin_progress_changed", self, "_on_shiny_coin_progress_changed")
	if ap_client.has_signal("goal_floor_progress_changed"):
		ap_client.connect("goal_floor_progress_changed", self, "_on_goal_floor_progress_changed")
	if ap_client.has_signal("text_client_changed"):
		ap_client.connect("text_client_changed", self, "_on_text_client_changed")
	if ap_client.has_signal("ap_settings_changed"):
		ap_client.connect("ap_settings_changed", self, "_on_ap_settings_changed")
	_load_settings()

	var info = title.get_node("Background/Info Text")
	var mod_text = title.get_node("Background/Mod Text")
	saved_info_text_mod = info.text_mod
	saved_mod_text_mod = mod_text.text_mod
	saved_info_scale_mod = info.scale_mod
	saved_mod_scale_mod = mod_text.scale_mod

	# Keep input enabled so F10 + R works from anywhere in the game.
	set_process_input(true)
	set_process(true)
	_reset_debug_command_file()
	call_deferred("_ensure_shiny_coin_hud")
	call_deferred("_ensure_goal_floor_hud")
	call_deferred("_ensure_deathlink_send_hud")
	call_deferred("_ensure_text_client_hud")
	call_deferred("_ensure_apworld_version_label")

func open():
	current_screen = "main"
	editing_field = ""
	_prepare_native_screen("ARCHIPELAGO")
	_build_main_screen()
	_refresh_main_screen()
	main.change_current_menu_path("/root/Main/Title")

func close():
	editing_field = ""
	current_screen = ""
	_save_settings()
	_restore_text_scaling()
	if apworld_version_label != null and is_instance_valid(apworld_version_label):
		apworld_version_label.visible = false
	title.draw()

func begin_edit(field):
	editing_field = str(field)
	edit_backup = _get_field_value(editing_field)
	edit_value = edit_backup
	_set_all_buttons_active(false)
	_refresh_main_screen()

func connect_or_disconnect():
	if ap_client.is_connected_to_ap():
		ap_client.disconnect_from_server()
	else:
		_save_settings()
		ap_client.connect_to_server(server, slot_name, password)
	_refresh_main_screen()

func toggle_ap_check_boost():
	if ap_client.has_method("toggle_ap_check_boost"):
		ap_client.toggle_ap_check_boost()
	_refresh_main_screen()

func toggle_deathlink():
	if ap_client.has_method("toggle_deathlink"):
		ap_client.toggle_deathlink()
	_refresh_main_screen()

func _next_deathlink_amnesty_value(current):
	var index = DEATHLINK_AMNESTY_VALUES.find(int(current))
	if index < 0:
		return 0
	return DEATHLINK_AMNESTY_VALUES[(index + 1) % DEATHLINK_AMNESTY_VALUES.size()]

func cycle_deathlink_send_amnesty():
	if ap_client.has_method("set_deathlink_send_amnesty"):
		ap_client.set_deathlink_send_amnesty(_next_deathlink_amnesty_value(ap_client.deathlink_send_amnesty))
	_save_settings()
	_refresh_main_screen()

func cycle_deathlink_receive_amnesty():
	if ap_client.has_method("set_deathlink_receive_amnesty"):
		ap_client.set_deathlink_receive_amnesty(_next_deathlink_amnesty_value(ap_client.deathlink_receive_amnesty))
	_save_settings()
	_refresh_main_screen()

func toggle_text_client():
	if ap_client.has_method("toggle_text_client_enabled"):
		ap_client.toggle_text_client_enabled()
	_save_settings()
	_refresh_main_screen()
	_refresh_text_client_hud()

func cycle_text_client_filter():
	if ap_client.has_method("cycle_text_client_filter_mode"):
		ap_client.cycle_text_client_filter_mode()
	_save_settings()
	_refresh_main_screen()
	_refresh_text_client_hud()

func _amnesty_text(value):
	return "OFF" if int(value) <= 0 else str(int(value))

func _input(event):
	if not (event is InputEventKey):
		return

	# Hidden debug console hotkey: hold F10 and press R, or hold R and press F10.
	if event.is_pressed() and not event.is_echo():
		var debug_hotkey = false
		if event.scancode == KEY_R and Input.is_key_pressed(KEY_F10):
			debug_hotkey = true
		elif event.scancode == KEY_F10 and Input.is_key_pressed(KEY_R):
			debug_hotkey = true
		if debug_hotkey:
			_open_external_debug_console()
			get_tree().set_input_as_handled()
			return

	if editing_field == "":
		return
	if not event.is_pressed() or event.is_echo():
		return

	if event.scancode == KEY_ENTER or event.scancode == KEY_KP_ENTER:
		_set_field_value(editing_field, edit_value)
		editing_field = ""
		_set_all_buttons_active(true)
		_save_settings()
		_refresh_main_screen()
		get_tree().set_input_as_handled()
		return
	elif event.scancode == KEY_ESCAPE:
		_set_field_value(editing_field, edit_backup)
		editing_field = ""
		_set_all_buttons_active(true)
		_refresh_main_screen()
		get_tree().set_input_as_handled()
		return
	elif event.scancode == KEY_BACKSPACE:
		if edit_value.length() > 0:
			edit_value = edit_value.substr(0, edit_value.length() - 1)
		_refresh_main_screen()
		get_tree().set_input_as_handled()
		return
	elif event.scancode == KEY_DELETE:
		edit_value = ""
		_refresh_main_screen()
		get_tree().set_input_as_handled()
		return

	if event.unicode >= 32 and event.unicode != 127:
		edit_value += char(event.unicode)
		_refresh_main_screen()
		get_tree().set_input_as_handled()

func _prepare_native_screen(heading):
	# Reuse the game's Title screen exactly like its own floor/stats submenus.
	title.remove()
	title.visible = true

	for child in main.get_node("Menus").buttons_menu.get_children():
		child.visible = false

	var info = title.get_node("Background/Info Text")
	var mod_text = title.get_node("Background/Mod Text")

	info.visible = true
	info.raw_string = heading
	info.rect_position = Vector2(24, 18)
	# Compact heading so the connection details have their own clear area.
	if options.resolution_y < 720:
		info.text_mod = -2
	else:
		info.text_mod = -1
	info.change_set_size(info.base_scale)
	info.force_update = true
	info.update()

	mod_text.visible = true
	mod_text.raw_string = ""
	mod_text.values = []
	mod_text.rect_position = Vector2(24, 70)
	mod_text.alignment_tags.dont = true
	# Keep the connection summary compact and readable without overlapping buttons.
	if options.resolution_y < 720:
		mod_text.text_mod = -3
	else:
		mod_text.text_mod = -2
	mod_text.change_set_size(mod_text.base_scale)
	mod_text.force_update = true
	mod_text.update()

	title.get_node("Background/Title Text").visible = false
	title.get_node("Background/Title Text 2").visible = false
	title.patch_text.visible = false
	if title.logo_button != null:
		title.logo_button.visible = false
	if title.merch_button != null:
		title.merch_button.visible = false
	if title.discord_button != null:
		title.discord_button.visible = false
	if title.twitter_button != null:
		title.twitter_button.visible = false

func _restore_text_scaling():
	var info = title.get_node("Background/Info Text")
	var mod_text = title.get_node("Background/Mod Text")
	info.text_mod = saved_info_text_mod
	info.scale_mod = saved_info_scale_mod
	info.change_set_size(info.base_scale)
	mod_text.text_mod = saved_mod_text_mod
	mod_text.scale_mod = saved_mod_scale_mod
	mod_text.change_set_size(mod_text.base_scale)

func _build_main_screen():
	# Keep button labels short. The actual values are displayed separately above.
	server_button = _make_button("SERVER", "begin_edit", ["server"], "button_color_continue")
	slot_button = _make_button("SLOT NAME", "begin_edit", ["slot"], "button_color_continue")
	password_button = _make_button("PASSWORD", "begin_edit", ["password"], "button_color_continue")
	connect_button = _make_button("CONNECT", "connect_or_disconnect", [], "button_color_start")
	ap_check_boost_button = _make_button("AP CHECK BOOST: OFF", "toggle_ap_check_boost", [], "button_color_continue")
	deathlink_button = _make_button("DEATHLINK: OFF", "toggle_deathlink", [], "button_color_continue")
	deathlink_send_amnesty_button = _make_button("SEND AMNESTY: OFF", "cycle_deathlink_send_amnesty", [], "button_color_continue")
	deathlink_receive_amnesty_button = _make_button("RECV AMNESTY: OFF", "cycle_deathlink_receive_amnesty", [], "button_color_continue")
	text_client_button = _make_button("TEXT CLIENT: OFF", "toggle_text_client", [], "button_color_continue")
	text_client_filter_button = _make_button("TEXT FILTER: ALL", "cycle_text_client_filter", [], "button_color_continue")
	back_button = _make_button(tr("back"), "close", [], "button_color_options")
	back_button.shortcuts = ["deny_cancel"]

func _make_button(text, call_name, args, color_type):
	var button = preload("res://TT Button.tscn").instance()
	button.button_text = text
	button.color = Color(options.colors3[color_type])
	button.color_type = color_type
	button.target = self
	button.call = call_name
	button.args = args
	button.toggle = false
	button.rect_size_mod = 0.25
	button.title_button = true
	button.alignment_tags.dont = true
	button.selector_alignment = "centered"

	# Match the physical button/text size of the 1680x900 layout. LBAL adds
	# another UI-size step around 1080p, so compensate with one extra
	# negative scale step there instead of letting labels grow taller.
	if options.resolution_y >= 1000 and options.resolution_y < 1440:
		button.scale_mod = -3
	elif options.resolution_y < 1000:
		button.scale_mod = -2
	else:
		button.scale_mod = -2

	title.add_child(button)
	title.buttons.push_back(button)
	return button

func _refresh_main_screen():
	if current_screen != "main":
		return

	_set_button_text(server_button, "SERVER")
	_set_button_text(slot_button, "SLOT NAME")
	_set_button_text(password_button, "PASSWORD")
	if ap_client.is_connected_to_ap():
		_set_button_text(connect_button, "DISCONNECT")
	else:
		_set_button_text(connect_button, "CONNECT")
	_set_button_text(ap_check_boost_button, "AP CHECK BOOST: " + ("ON" if ap_client.ap_check_boost_enabled else "OFF"))
	_set_button_text(deathlink_button, "DEATHLINK: " + ("ON" if ap_client.deathlink_enabled else "OFF"))
	if deathlink_send_amnesty_button != null and ap_client.get("deathlink_send_amnesty") != null:
		_set_button_text(deathlink_send_amnesty_button, "SEND AMNESTY: " + _amnesty_text(ap_client.deathlink_send_amnesty))
	if deathlink_receive_amnesty_button != null and ap_client.get("deathlink_receive_amnesty") != null:
		_set_button_text(deathlink_receive_amnesty_button, "RECV AMNESTY: " + _amnesty_text(ap_client.deathlink_receive_amnesty))
	if text_client_button != null and ap_client.get("text_client_enabled") != null:
		_set_button_text(text_client_button, "TEXT CLIENT: " + ("ON" if ap_client.text_client_enabled else "OFF"))
	if text_client_filter_button != null and ap_client.has_method("get_text_client_filter_name"):
		_set_button_text(text_client_filter_button, "TEXT FILTER: " + ap_client.get_text_client_filter_name())

	var shown_server = _display_value("server", server)
	var shown_slot = _display_value("slot", slot_name)
	var shown_password = _display_password()
	var text = "Status: " + ap_client.status
	if not ap_client.is_connected_to_ap() and ap_client.has_method("get_connection_handshake_text"):
		var handshake_text = ap_client.get_connection_handshake_text()
		if handshake_text != "":
			text += "\n" + handshake_text
	# Do not clutter old/offline rooms with 0/? rows. Once authenticated, show a
	# tracker only when that room actually supplied a requirement.
	if ap_client.is_connected_to_ap():
		if ap_client.has_method("get_shiny_coin_progress_text") and ap_client.get("shiny_coin_enabled") != null and bool(ap_client.shiny_coin_enabled) and int(ap_client.shiny_coin_required) >= 0:
			text += "\n" + ap_client.get_shiny_coin_progress_text()
		if ap_client.has_method("get_goal_floor_progress_text") and int(ap_client.goal_floors_required) >= 0:
			text += "\n" + ap_client.get_goal_floor_progress_text()
	text += "\nServer: " + shown_server
	text += "\nSlot: " + shown_slot
	text += "\nPassword: " + shown_password
	if editing_field != "":
		text += "\n\nENTER = save    ESC = cancel"
	_set_info_text(text)
	_layout_main_buttons()
	_refresh_apworld_version_label()

func _layout_main_buttons():
	# AP layout revision: exact 1680-style sizing/positioning at 1080p.
	# Connection controls stay in one compact centered stack. Gameplay toggles use
	# a two-column grid underneath so long amnesty labels never overlap.
	var connection_buttons = [server_button, slot_button, password_button, connect_button]
	var toggle_buttons = [ap_check_boost_button, deathlink_button, deathlink_send_amnesty_button, deathlink_receive_amnesty_button, text_client_button, text_client_filter_button]

	var connection_start_y = 190
	var connection_spacing = 32
	var toggle_gap = 14
	var toggle_row_spacing = 38
	var column_gap = 26
	if options.resolution_y >= 720:
		connection_start_y = int(round(options.resolution_y * 0.30))
		connection_spacing = 38
		toggle_gap = 18
		toggle_row_spacing = 42
		column_gap = 34

	for i in range(connection_buttons.size()):
		var button = connection_buttons[i]
		if button == null or not is_instance_valid(button):
			continue
		button.change_size()
		button.update_size()
		button.correct_size()
		button.rect_position = Vector2(
			round(options.resolution_x / 2 - button.rect_size.x / 2),
			connection_start_y + connection_spacing * i
		)
		button.base_x = button.rect_position.x
		# This position is already calculated for the current resolution.
		# Mark the current resolution as saved and do not rescale it again.
		button.saved_resolution = Vector2(options.resolution_x, options.resolution_y)
		button.aligned = false

	# Size toggles first so the two columns can be centered using the actual
	# widest label in each column. Text Client and Text Filter are centered on rows 3 and 4.
	for button in toggle_buttons:
		if button == null or not is_instance_valid(button):
			continue
		button.change_size()
		button.update_size()
		button.correct_size()

	var left_width = 0.0
	var right_width = 0.0
	for idx in [0, 2]:
		var b = toggle_buttons[idx]
		if b != null and is_instance_valid(b):
			left_width = max(left_width, b.rect_size.x)
	for idx in [1, 3]:
		var b = toggle_buttons[idx]
		if b != null and is_instance_valid(b):
			right_width = max(right_width, b.rect_size.x)
	var grid_width = left_width + column_gap + right_width
	var left_x = round(options.resolution_x / 2 - grid_width / 2)
	var right_x = left_x + left_width + column_gap
	var toggle_start_y = connection_start_y + connection_spacing * connection_buttons.size() + toggle_gap

	for i in range(4):
		var button = toggle_buttons[i]
		if button == null or not is_instance_valid(button):
			continue
		var row = int(i / 2)
		var x = left_x if i % 2 == 0 else right_x
		# Center each button inside its column rather than left-aligning mixed widths.
		var column_width = left_width if i % 2 == 0 else right_width
		button.rect_position = Vector2(
			round(x + (column_width - button.rect_size.x) / 2),
			toggle_start_y + toggle_row_spacing * row
		)
		button.base_x = button.rect_position.x
		# This position is already calculated for the current resolution.
		# Mark the current resolution as saved and do not rescale it again.
		button.saved_resolution = Vector2(options.resolution_x, options.resolution_y)
		button.aligned = false

	if text_client_button != null and is_instance_valid(text_client_button):
		text_client_button.rect_position = Vector2(
			round(options.resolution_x / 2 - text_client_button.rect_size.x / 2),
			toggle_start_y + toggle_row_spacing * 2
		)
		text_client_button.base_x = text_client_button.rect_position.x
		text_client_button.saved_resolution = Vector2(options.resolution_x, options.resolution_y)
		text_client_button.aligned = false

	if text_client_filter_button != null and is_instance_valid(text_client_filter_button):
		text_client_filter_button.rect_position = Vector2(
			round(options.resolution_x / 2 - text_client_filter_button.rect_size.x / 2),
			toggle_start_y + toggle_row_spacing * 3
		)
		text_client_filter_button.base_x = text_client_filter_button.rect_position.x
		text_client_filter_button.saved_resolution = Vector2(options.resolution_x, options.resolution_y)
		text_client_filter_button.aligned = false

	if back_button != null and is_instance_valid(back_button):
		back_button.change_size()
		back_button.update_size()
		back_button.correct_size()
		back_button.rect_position = Vector2(options.resolution_x - 8 - back_button.rect_size.x, options.resolution_y - 8 - back_button.rect_size.y)
		back_button.base_x = back_button.rect_position.x
		back_button.saved_resolution = Vector2(options.resolution_x, options.resolution_y)
		back_button.aligned = false

func _set_button_text(button, text):
	if button == null or not is_instance_valid(button):
		return
	button.button_text = text
	# TT Button restores saved_raw_string when the click animation unpresses.
	# Keep it in sync so toggle labels change immediately instead of reverting
	# until the next menu redraw.
	button.saved_raw_string = text
	button.text_node.raw_string = text
	button.text_node.force_update = true
	button.text_node.update()
	button.update_size()

func _set_info_text(text):
	var mod_text = title.get_node("Background/Mod Text")
	mod_text.raw_string = text
	mod_text.force_update = true
	mod_text.update()
	mod_text.rect_position = Vector2(24, 70)

func _display_value(field, normal_value):
	if editing_field == field:
		return ">" + edit_value + "_"
	if str(normal_value) == "":
		return "<not set>"
	return str(normal_value)

func _display_password():
	var value = password
	if editing_field == "password":
		value = edit_value
		return ">" + _mask(value) + "_"
	if value == "":
		return "<none>"
	return _mask(value)

func _mask(value):
	var out = ""
	for _i in range(str(value).length()):
		out += "*"
	return out

func _set_all_buttons_active(value):
	for button in title.buttons:
		if is_instance_valid(button):
			button.active = value

func _get_field_value(field):
	match field:
		"server":
			return server
		"slot":
			return slot_name
		"password":
			return password
	return ""

func _set_field_value(field, value):
	match field:
		"server":
			server = str(value)
		"slot":
			slot_name = str(value)
		"password":
			password = str(value)

# -----------------------------------------------------------------------------
# Connected APWorld version status
# -----------------------------------------------------------------------------

func _ensure_apworld_version_label():
	if title == null or not is_instance_valid(title):
		return null
	if apworld_version_label != null and is_instance_valid(apworld_version_label):
		return apworld_version_label
	if title.has_node("AP World Version Status"):
		apworld_version_label = title.get_node("AP World Version Status")
		return apworld_version_label

	var label = preload("res://Outline Label.tscn").instance()
	label.name = "AP World Version Status"
	label.raw_string = ""
	label.scale_mod = -2
	label.aligned = false
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	title.add_child(label)
	apworld_version_label = label
	apworld_version_label_last_text = ""
	apworld_version_label_last_state = ""
	_refresh_apworld_version_label()
	return apworld_version_label

func _slot_data_has_any_version_key(names):
	if ap_client == null or ap_client.get("slot_data") == null:
		return false
	var data = ap_client.slot_data
	if typeof(data) != TYPE_DICTIONARY:
		return false

	# Current LBAL APWorlds store their option fields under
	# slot_data["options"]. Keep checking the top level too so rooms made with
	# older APWorlds remain detectable.
	var sources = [data]
	if data.has("options") and typeof(data["options"]) == TYPE_DICTIONARY:
		sources.append(data["options"])

	for source in sources:
		for actual in source.keys():
			var actual_lower = str(actual).to_lower()
			for wanted in names:
				if actual_lower == str(wanted).to_lower():
					return true
	return false

func _connected_apworld_version_state():
	if ap_client == null or not ap_client.has_method("is_connected_to_ap") or not ap_client.is_connected_to_ap():
		return "disconnected"

	# Any connection that required one of the legacy authentication fallbacks is
	# definitely an older room/APWorld.
	if bool(ap_client.get("legacy_connect_retry_sent")) or bool(ap_client.get("legacy_game_retry_sent")):
		return "legacy"

	# An explicit version marker wins if a future APWorld supplies one. For the
	# current generation, the three newest slot_data features together are our
	# compatibility marker. Older APWorlds do not provide all three.
	var has_explicit_version = _slot_data_has_any_version_key([
		"APWorldVersion", "apworld_version", "WorldVersion", "world_version"
	])
	if has_explicit_version:
		return "current"

	var has_goal_floors = _slot_data_has_any_version_key([
		"GoalFloors", "goal_floors", "FloorsToGoal", "floors_to_goal"
	])
	var has_send_amnesty = _slot_data_has_any_version_key([
		"DeathlinkSendAmnesty", "deathlink_send_amnesty"
	])
	var has_receive_amnesty = _slot_data_has_any_version_key([
		"DeathlinkReceiveAmnesty", "deathlink_receive_amnesty"
	])

	if has_goal_floors and has_send_amnesty and has_receive_amnesty:
		return "current"
	return "legacy"

func _refresh_apworld_version_label():
	var label = _ensure_apworld_version_label()
	if label == null or not is_instance_valid(label):
		return

	var state = _connected_apworld_version_state()
	if current_screen != "main" or state == "disconnected":
		label.visible = false
		return

	var text = ""
	var tint = Color("FFFFFF")
	if state == "current":
		text = "APWORLD: CURRENT VERSION"
		tint = Color("00E436")
	else:
		text = "APWORLD: OLDER VERSION"
		tint = Color("FF004D")

	if text != apworld_version_label_last_text or state != apworld_version_label_last_state:
		apworld_version_label_last_text = text
		apworld_version_label_last_state = state
		label.raw_string = text
		label.modulate = tint
		label.force_update = true
		label.update()
		label.change_set_size(label.base_scale)

	# Bottom-left of the Archipelago title screen, opposite the Back button.
	label.rect_position = Vector2(16, options.resolution_y - 42)
	label.base_x = label.rect_position.x
	label.visible = true

# -----------------------------------------------------------------------------
# Hidden F10 + R external debug command prompt
# -----------------------------------------------------------------------------

func _process(delta):
	connection_status_refresh_timer += delta
	if connection_status_refresh_timer >= 0.25:
		connection_status_refresh_timer = 0.0
		if current_screen == "main" and ap_client != null and not ap_client.is_connected_to_ap() and str(ap_client.status) != "Disconnected":
			_refresh_main_screen()

	debug_poll_timer += delta
	if debug_poll_timer >= 0.10:
		debug_poll_timer = 0.0
		_poll_external_debug_commands()

	shiny_coin_hud_refresh_timer += delta
	if shiny_coin_hud_refresh_timer >= 0.20:
		shiny_coin_hud_refresh_timer = 0.0
		_refresh_shiny_coin_hud()
		_refresh_goal_floor_hud()
		_refresh_deathlink_send_hud()
		_refresh_text_client_hud()

# -----------------------------------------------------------------------------
# Persistent in-game AP counters / text feed
# -----------------------------------------------------------------------------

func _get_buttons_menu():
	if main == null or not is_instance_valid(main):
		return null
	var menus = main.get_node_or_null("Menus")
	if menus == null:
		return null
	var buttons_menu = menus.get("buttons_menu")
	if buttons_menu != null and is_instance_valid(buttons_menu):
		return buttons_menu
	return menus.get_node_or_null("Buttons")

func _ensure_shiny_coin_hud():
	var buttons_menu = _get_buttons_menu()
	if buttons_menu == null:
		return null

	if shiny_coin_hud != null and is_instance_valid(shiny_coin_hud):
		if shiny_coin_hud.get_parent() == buttons_menu:
			return shiny_coin_hud
		shiny_coin_hud = null

	if buttons_menu.has_node("AP Shiny Coin Tracker"):
		shiny_coin_hud = buttons_menu.get_node("AP Shiny Coin Tracker")
		return shiny_coin_hud

	# Reuse LBAL's own TT Button presentation so the tracker uses the same
	# pixel font, thick outline and UI scaling as Options/Inventory. It is made
	# non-interactive, so it behaves as a status panel rather than a button.
	var tracker = preload("res://TT Button.tscn").instance()
	tracker.name = "AP Shiny Coin Tracker"
	tracker.button_text = "SC 0/0"
	tracker.color = Color(options.colors3["button_color_options"])
	tracker.color_type = "button_color_options"
	tracker.toggle = false
	tracker.alignment_tags["dont"] = true
	tracker.scale_mod = -2
	tracker.active = false
	tracker.selectable = false
	tracker.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tracker.focus_mode = Control.FOCUS_NONE

	buttons_menu.add_child(tracker)
	tracker.text_node.force_update = true
	tracker.text_node.update()
	tracker.button_text = tracker.text_node.raw_string
	tracker.update_size()
	tracker.correct_size()
	shiny_coin_hud = tracker
	shiny_coin_hud_last_text = ""
	_refresh_shiny_coin_hud()
	return shiny_coin_hud

func _refresh_shiny_coin_hud():
	var tracker = _ensure_shiny_coin_hud()
	if tracker == null or not is_instance_valid(tracker):
		return

	var buttons_menu = _get_buttons_menu()
	if buttons_menu == null:
		tracker.visible = false
		return

	var connected = ap_client != null and ap_client.has_method("is_connected_to_ap") and ap_client.is_connected_to_ap()
	var options_button = buttons_menu.get("options_button")
	var shiny_enabled = ap_client != null and ap_client.get("shiny_coin_enabled") != null and bool(ap_client.shiny_coin_enabled)
	if not connected or not shiny_enabled or options_button == null or not is_instance_valid(options_button):
		tracker.visible = false
		return

	var received = max(0, int(ap_client.shiny_coin_received))
	var required = int(ap_client.shiny_coin_required)
	var required_text = "?" if required < 0 else str(required)
	var text = "SC " + str(received) + "/" + required_text

	if text != shiny_coin_hud_last_text:
		shiny_coin_hud_last_text = text
		tracker.button_text = text
		tracker.saved_raw_string = text
		tracker.text_node.raw_string = text
		tracker.text_node.force_update = true
		tracker.text_node.update()
		tracker.update_size()
		tracker.correct_size()

	# Keep it locked immediately above the normal Options button and align their
	# right edges. Recalculate every refresh so resolution/UI-scale changes are
	# handled automatically by the game.
	tracker.rect_position = Vector2(
		options_button.rect_position.x + options_button.rect_size.x - tracker.rect_size.x,
		options_button.rect_position.y - tracker.rect_size.y - 8
	)
	tracker.base_x = tracker.rect_position.x
	tracker.visible = options_button.visible

func _ensure_goal_floor_hud():
	var buttons_menu = _get_buttons_menu()
	if buttons_menu == null:
		return null
	if goal_floor_hud != null and is_instance_valid(goal_floor_hud):
		if goal_floor_hud.get_parent() == buttons_menu:
			return goal_floor_hud
		goal_floor_hud = null
	if buttons_menu.has_node("AP Goal Floor Tracker"):
		goal_floor_hud = buttons_menu.get_node("AP Goal Floor Tracker")
		return goal_floor_hud
	var tracker = preload("res://TT Button.tscn").instance()
	tracker.name = "AP Goal Floor Tracker"
	tracker.button_text = "GF ?"
	tracker.color = Color(options.colors3["button_color_options"])
	tracker.color_type = "button_color_options"
	tracker.toggle = false
	tracker.alignment_tags["dont"] = true
	tracker.scale_mod = -2
	tracker.active = false
	tracker.selectable = false
	tracker.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tracker.focus_mode = Control.FOCUS_NONE
	buttons_menu.add_child(tracker)
	tracker.text_node.force_update = true
	tracker.text_node.update()
	tracker.update_size()
	tracker.correct_size()
	goal_floor_hud = tracker
	goal_floor_hud_last_text = ""
	_refresh_goal_floor_hud()
	return goal_floor_hud

func _refresh_goal_floor_hud():
	var tracker = _ensure_goal_floor_hud()
	if tracker == null or not is_instance_valid(tracker):
		return
	var buttons_menu = _get_buttons_menu()
	if buttons_menu == null:
		tracker.visible = false
		return
	var connected = ap_client != null and ap_client.has_method("is_connected_to_ap") and ap_client.is_connected_to_ap()
	var required = int(ap_client.goal_floors_required) if ap_client.get("goal_floors_required") != null else -1
	if not connected or required <= 0:
		tracker.visible = false
		return
	var completed = max(0, int(ap_client.goal_floors_completed))
	var text = "GF " + str(completed) + "/" + str(required)
	if text != goal_floor_hud_last_text:
		goal_floor_hud_last_text = text
		tracker.button_text = text
		tracker.saved_raw_string = text
		tracker.text_node.raw_string = text
		tracker.text_node.force_update = true
		tracker.text_node.update()
		tracker.update_size()
		tracker.correct_size()
	var options_button = buttons_menu.get("options_button")
	if options_button == null or not is_instance_valid(options_button):
		tracker.visible = false
		return
	var anchor_y = options_button.rect_position.y
	if shiny_coin_hud != null and is_instance_valid(shiny_coin_hud) and shiny_coin_hud.visible:
		anchor_y = shiny_coin_hud.rect_position.y
	tracker.rect_position = Vector2(
		options_button.rect_position.x + options_button.rect_size.x - tracker.rect_size.x,
		anchor_y - tracker.rect_size.y - 6
	)
	tracker.base_x = tracker.rect_position.x
	tracker.visible = options_button.visible

func _ensure_deathlink_send_hud():
	var buttons_menu = _get_buttons_menu()
	if buttons_menu == null:
		return null
	if deathlink_send_hud != null and is_instance_valid(deathlink_send_hud):
		if deathlink_send_hud.get_parent() == buttons_menu:
			return deathlink_send_hud
		deathlink_send_hud = null
	if buttons_menu.has_node("AP DeathLink Send Counter"):
		deathlink_send_hud = buttons_menu.get_node("AP DeathLink Send Counter")
		return deathlink_send_hud

	# Use the normal LBAL button frame/font so the counter looks native, but make
	# it non-interactive.  "DL 1" means the NEXT local death sends a DeathLink.
	var tracker = preload("res://TT Button.tscn").instance()
	tracker.name = "AP DeathLink Send Counter"
	tracker.button_text = "DL 1"
	tracker.color = Color(options.colors3["button_color_options"])
	tracker.color_type = "button_color_options"
	tracker.toggle = false
	tracker.alignment_tags["dont"] = true
	tracker.scale_mod = -2
	tracker.active = false
	tracker.selectable = false
	tracker.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tracker.focus_mode = Control.FOCUS_NONE
	buttons_menu.add_child(tracker)
	tracker.text_node.force_update = true
	tracker.text_node.update()
	tracker.button_text = tracker.text_node.raw_string
	tracker.update_size()
	tracker.correct_size()
	deathlink_send_hud = tracker
	deathlink_send_hud_last_text = ""
	_refresh_deathlink_send_hud()
	return deathlink_send_hud

func _refresh_deathlink_send_hud():
	var tracker = _ensure_deathlink_send_hud()
	if tracker == null or not is_instance_valid(tracker):
		return
	var buttons_menu = _get_buttons_menu()
	if buttons_menu == null:
		tracker.visible = false
		return
	var connected = ap_client != null and ap_client.has_method("is_connected_to_ap") and ap_client.is_connected_to_ap()
	var dl_enabled = ap_client != null and ap_client.get("deathlink_enabled") != null and bool(ap_client.deathlink_enabled)
	if not connected or not dl_enabled:
		tracker.visible = false
		return

	# deathlink_send_amnesty_remaining is how many local deaths will still be
	# forgiven. The actual DeathLink goes out on the following death.
	var forgiven_left = max(0, int(ap_client.deathlink_send_amnesty_remaining)) if ap_client.get("deathlink_send_amnesty_remaining") != null else 0
	var deaths_until_send = forgiven_left + 1
	var text = "DL " + str(deaths_until_send)
	if text != deathlink_send_hud_last_text:
		deathlink_send_hud_last_text = text
		tracker.button_text = text
		tracker.saved_raw_string = text
		tracker.text_node.raw_string = text
		tracker.text_node.force_update = true
		tracker.text_node.update()
		tracker.update_size()
		tracker.correct_size()

	# Put the countdown immediately to the LEFT of LBAL's removal/destroy-token
	# button.  Use its real position even when that button is temporarily hidden,
	# so the DeathLink counter never jumps around as token count changes.
	var removal_button = buttons_menu.get("removal_button")
	var deck_button = buttons_menu.get("deck_button")
	var anchor_x = -1.0
	var anchor_y = -1.0
	if removal_button != null and is_instance_valid(removal_button):
		anchor_x = removal_button.rect_position.x
		anchor_y = removal_button.rect_position.y
	elif deck_button != null and is_instance_valid(deck_button):
		anchor_x = deck_button.rect_position.x - tracker.rect_size.x - 12
		anchor_y = deck_button.rect_position.y
	if anchor_x < 0 or anchor_y < 0:
		tracker.visible = false
		return
	tracker.rect_position = Vector2(anchor_x - tracker.rect_size.x - 8, anchor_y)
	tracker.base_x = tracker.rect_position.x
	tracker.visible = true

func _ensure_text_client_hud():
	var buttons_menu = _get_buttons_menu()
	if buttons_menu == null:
		return null
	if text_client_hud != null and is_instance_valid(text_client_hud):
		if text_client_hud.get_parent() == buttons_menu:
			return text_client_hud
		text_client_hud = null
	if buttons_menu.has_node("AP Text Client Feed"):
		text_client_hud = buttons_menu.get_node("AP Text Client Feed")
		return text_client_hud

	var feed = Panel.new()
	feed.name = "AP Text Client Feed"
	feed.mouse_filter = Control.MOUSE_FILTER_IGNORE
	feed.focus_mode = Control.FOCUS_NONE

	var style = StyleBoxFlat.new()
	style.bg_color = Color(0.02, 0.02, 0.02, 0.92)
	style.border_color = Color(0, 0, 0, 1)
	style.border_width_left = 4
	style.border_width_top = 4
	style.border_width_right = 4
	style.border_width_bottom = 4
	feed.add_stylebox_override("panel", style)

	var label = RichTextLabel.new()
	label.name = "Feed Text"
	label.bbcode_enabled = true
	# Keep the HUD pinned to the newest AP message when the text is taller than
	# the small feed box. Without this, RichTextLabel stays at the top and the
	# newest lines are clipped below the panel, making the feed look delayed.
	label.scroll_active = true
	label.scroll_following = true
	label.selection_enabled = false
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var feed_font = preload("res://PICO-8.tres").duplicate()
	feed_font.size = 24
	# Keep the pixel font readable over the dark translucent feed panel.
	feed_font.outline_size = 2
	feed_font.outline_color = Color(0, 0, 0, 1)
	label.add_font_override("normal_font", feed_font)
	label.add_font_override("bold_font", feed_font)
	label.add_font_override("italics_font", feed_font)
	label.add_font_override("bold_italics_font", feed_font)
	label.add_font_override("mono_font", feed_font)
	label.add_color_override("default_color", Color(1, 1, 1, 1))
	feed.add_child(label)

	buttons_menu.add_child(feed)
	text_client_hud = feed
	text_client_hud_last_text = ""
	_refresh_text_client_hud()
	return text_client_hud

func _refresh_text_client_hud():
	var feed = _ensure_text_client_hud()
	if feed == null or not is_instance_valid(feed):
		return
	var buttons_menu = _get_buttons_menu()
	if buttons_menu == null:
		feed.visible = false
		return
	var connected = ap_client != null and ap_client.has_method("is_connected_to_ap") and ap_client.is_connected_to_ap()
	var enabled = ap_client != null and ap_client.get("text_client_enabled") != null and bool(ap_client.text_client_enabled)
	if not connected or not enabled:
		feed.visible = false
		return

	var view_size = get_viewport().get_visible_rect().size
	# Put the feed in the bottom HUD gap: after the money counter and before SPIN.
	# The LBAL buttons menu is scaled, so use a substantially larger font above to
	# keep the AP feed readable at normal 1600x900 / 1920x1080 window sizes.
	# Leave a wider money-safe area on the left.  The old fixed position could
	# overlap LBAL's money counter once it reached four or more digits.
	# Keep the feed's right edge before the centred SPIN button as the window
	# changes size instead of simply shifting a wide box to the right.
	var box_x = clamp(view_size.x * 0.125, 180.0, 230.0)
	# Make the feed narrower but taller.  Clamp its right edge against the actual
	# SPIN button instead of a percentage so it cannot grow under that button.
	var spin_button = buttons_menu.get("spin_button")
	var feed_right_limit = view_size.x * 0.43
	if spin_button != null and is_instance_valid(spin_button):
		feed_right_limit = spin_button.rect_position.x - 12
	var box_width = clamp(feed_right_limit - box_x, 230.0, 480.0)
	var box_height = clamp(view_size.y * 0.145, 112.0, 150.0)
	var bottom_gap = 5.0
	feed.rect_size = Vector2(box_width, box_height)
	feed.rect_position = Vector2(box_x, max(8, view_size.y - box_height - bottom_gap))

	var label = feed.get_node_or_null("Feed Text")
	if label == null:
		feed.visible = false
		return
	label.rect_position = Vector2(10, 8)
	label.rect_size = Vector2(max(1, feed.rect_size.x - 20), max(1, feed.rect_size.y - 16))

	var text = ap_client.get_text_client_feed_bbcode(4) if ap_client.has_method("get_text_client_feed_bbcode") else "[color=#FFFFFF]Waiting for Archipelago messages...[/color]"
	if text != text_client_hud_last_text:
		text_client_hud_last_text = text
		label.bbcode_text = text
		# scroll_following normally handles this, but explicitly jump to the last
		# rendered line as well so wrapped item/location messages cannot leave the
		# newest event hidden below the panel.
		if label.has_method("get_line_count") and label.has_method("scroll_to_line"):
			label.call_deferred("scroll_to_line", max(0, int(label.get_line_count()) - 1))
	feed.visible = true

func _open_external_debug_console():
	if OS.get_name() != "Windows":
		ap_client.debug_log("DEBUG WINDOW ERROR: detachable command prompt is currently Windows-only")
		return

	if debug_console_pid > 0 and OS.is_process_running(debug_console_pid):
		ap_client.debug_log("DEBUG WINDOW: already open (PID " + str(debug_console_pid) + ")")
		return

	if not _copy_debug_script_to_user_dir():
		ap_client.debug_log("DEBUG WINDOW ERROR: could not copy APDebugConsole.ps1")
		return

	var script_path = ProjectSettings.globalize_path(DEBUG_SCRIPT_COPY)
	var log_path = ProjectSettings.globalize_path(DEBUG_LOG_PATH)
	var command_path = ProjectSettings.globalize_path(DEBUG_COMMAND_PATH)
	var args = PoolStringArray([
		"-NoProfile",
		"-ExecutionPolicy", "Bypass",
		"-File", script_path,
		"-LogPath", log_path,
		"-CommandPath", command_path
	])
	# open_console=true is what makes this an independent, movable Windows console.
	debug_console_pid = OS.execute("powershell.exe", args, false, [], true, true)
	if debug_console_pid <= 0:
		ap_client.debug_log("DEBUG WINDOW ERROR: powershell.exe failed to start; PID=" + str(debug_console_pid))
	else:
		ap_client.debug_log("DEBUG WINDOW: opened detachable console PID=" + str(debug_console_pid))

func _copy_debug_script_to_user_dir():
	var source = File.new()
	var err = source.open(DEBUG_SCRIPT_SOURCE, File.READ)
	if err != OK:
		return false
	var data = source.get_buffer(source.get_len())
	source.close()

	var target = File.new()
	err = target.open(DEBUG_SCRIPT_COPY, File.WRITE)
	if err != OK:
		return false
	target.store_buffer(data)
	target.close()
	return true

func _reset_debug_command_file():
	var file = File.new()
	if file.open(DEBUG_COMMAND_PATH, File.WRITE) == OK:
		file.store_string("")
		file.close()
	debug_command_line = 0

func _poll_external_debug_commands():
	var file = File.new()
	if not file.file_exists(DEBUG_COMMAND_PATH):
		return
	if file.open(DEBUG_COMMAND_PATH, File.READ) != OK:
		return
	var commands = []
	while not file.eof_reached():
		var line = file.get_line()
		if line.strip_edges() != "":
			commands.append(line)
	file.close()

	# The PowerShell console only appends, so process lines we have not seen yet.
	if commands.size() < debug_command_line:
		debug_command_line = 0
	while debug_command_line < commands.size():
		var raw = str(commands[debug_command_line]).strip_edges()
		debug_command_line += 1
		if raw != "":
			_execute_debug_command(raw)

func _execute_debug_command(raw):
	ap_client.debug_log("DEBUG COMMAND > " + raw)
	var cmd = raw
	var arg = ""
	var space_pos = raw.find(" ")
	if space_pos != -1:
		cmd = raw.substr(0, space_pos)
		arg = raw.substr(space_pos + 1, raw.length() - space_pos - 1).strip_edges()
	cmd = cmd.to_lower()

	match cmd:
		"help", "?":
			_debug_reply("Commands:")
			_debug_reply("  status                    full AP connection status")
			_debug_reply("  connect                   connect using menu settings")
			_debug_reply("  disconnect                disconnect from AP")
			_debug_reply("  reconnect                 reconnect using current settings")
			_debug_reply("  sync                      request AP Sync")
			_debug_reply("  check <location_id>       manually send LocationChecks ID")
			_debug_reply("  checks                    print ALL checked/missing location IDs")
			_debug_reply("  items                     print ALL received item/location/player IDs")
			_debug_reply("  hooks                     print all registered hook states and AP IDs")
			_debug_reply("  effects                   show effect-hook coverage/status")
			_debug_reply("  snapshot                  dump current floor/spin/symbol/item IDs")
			_debug_reply("  say <message>             send chat text to AP room")
			_debug_reply("  goal                      send AP goal status")
			_debug_reply("  autogoal [on|off|toggle]  automatic goal message sending")
			_debug_reply("  textclient [on|off]       bottom AP text feed")
			_debug_reply("  server <address>          view/change server")
			_debug_reply("  slot <name>               view/change slot name")
			_debug_reply("  password <password>       change password (not saved)")
			_debug_reply("  logfile                   print AP log file path")
			_debug_reply("  clear                     clear AP debug log")
			_debug_reply("  close                     closes this console window")
		"status":
			_debug_reply(ap_client.get_debug_text())
		"connect":
			_save_settings()
			ap_client.connect_to_server(server, slot_name, password)
			_debug_reply("Connecting to " + server + " as " + slot_name)
		"disconnect":
			ap_client.disconnect_from_server()
			_debug_reply("Disconnect requested")
		"reconnect":
			_save_settings()
			ap_client.connect_to_server(server, slot_name, password)
			_debug_reply("Reconnect requested")
		"sync":
			ap_client.send_sync()
			_debug_reply("Sync requested")
		"check":
			if arg == "" or not arg.is_valid_integer():
				_debug_reply("Usage: check <location_id>")
			elif ap_client.send_location_check(int(arg)):
				_debug_reply("Sent location check ID=" + arg)
			else:
				_debug_reply("Could not send check; see AP ERROR lines")
		"checks":
			_debug_reply("CHECKED LOCATION IDS (" + str(ap_client.checked_locations.size()) + "): " + _all_values(ap_client.checked_locations))
			_debug_reply("MISSING LOCATION IDS (" + str(ap_client.missing_locations.size()) + "): " + _all_values(ap_client.missing_locations))
		"items":
			_debug_reply("RECEIVED ITEMS total=" + str(ap_client.received_items.size()))
			for i in range(ap_client.received_items.size()):
				var item = ap_client.received_items[i]
				_debug_reply(_format_received_item(i, item))
		"hooks":
			_print_all_hooks()
		"effects":
			var effect_hooks = main.get_node_or_null("AP Hooks")
			if effect_hooks == null or not effect_hooks.has_method("get_effect_coverage_text"):
				_debug_reply("Effect hook status unavailable")
			else:
				_debug_reply(effect_hooks.get_effect_coverage_text())
		"snapshot", "game":
			var game_debug = main.get_node_or_null("AP Gameplay Debug")
			if game_debug == null:
				_debug_reply("AP Gameplay Debug node not found")
			else:
				game_debug.dump_snapshot("console")
				_debug_reply("Gameplay snapshot written to log")
		"say":
			if arg == "":
				_debug_reply("Usage: say <message>")
			elif ap_client.send_say(arg):
				_debug_reply("Sent chat message")
			else:
				_debug_reply("Not connected")
		"goal":
			if ap_client.send_goal():
				_debug_reply("Goal status sent")
			else:
				_debug_reply("Not connected")
		"autogoal":
			var auto_goal_value = arg.to_lower()
			if auto_goal_value == "on":
				ap_client.set_auto_goal_enabled(true)
			elif auto_goal_value == "off":
				ap_client.set_auto_goal_enabled(false)
			elif auto_goal_value == "toggle":
				ap_client.toggle_auto_goal_enabled()
			elif auto_goal_value != "":
				_debug_reply("Usage: autogoal [on|off|toggle]")
			_save_settings()
			_debug_reply("Auto goal sending: " + ("ON" if ap_client.auto_goal_enabled else "OFF"))
		"textclient":
			var text_client_value = arg.to_lower()
			if text_client_value == "on":
				ap_client.set_text_client_enabled(true)
			elif text_client_value == "off":
				ap_client.set_text_client_enabled(false)
			elif text_client_value == "toggle":
				ap_client.toggle_text_client_enabled()
			elif text_client_value != "":
				_debug_reply("Usage: textclient [on|off|toggle]")
			_save_settings()
			_debug_reply("Text client feed: " + ("ON" if ap_client.text_client_enabled else "OFF"))
		"server":
			if arg == "":
				_debug_reply("Server: " + server)
			else:
				server = arg
				_save_settings()
				_debug_reply("Server set to " + server)
		"slot":
			if arg == "":
				_debug_reply("Slot: " + slot_name)
			else:
				slot_name = arg
				_save_settings()
				_debug_reply("Slot set to " + slot_name)
		"password":
			password = arg
			if password == "":
				_debug_reply("Password cleared")
			else:
				_debug_reply("Password set (" + str(password.length()) + " characters)")
		"logfile":
			_debug_reply("Log file: " + ProjectSettings.globalize_path(DEBUG_LOG_PATH))
		"clear":
			ap_client.clear_debug_log()
			_debug_reply("Debug log cleared")
		"close", "exit":
			_debug_reply("Debug console close requested")
		_:
			_debug_reply("Unknown command: " + cmd + ". Type help.")

	_refresh_main_screen()

func _debug_reply(value):
	for piece in str(value).split("\n", true):
		ap_client.debug_log("CONSOLE: " + str(piece))

func _all_values(values):
	if values.size() == 0:
		return "<none>"
	var out = ""
	for i in range(values.size()):
		if i > 0:
			out += ", "
		out += str(values[i])
	return out

func _format_received_item(index, item):
	if typeof(item) == TYPE_DICTIONARY:
		return "  index=" + str(index) + " item_id=" + str(item.get("item", -1)) + " location_id=" + str(item.get("location", -1)) + " player_id=" + str(item.get("player", -1)) + " flags=" + str(item.get("flags", 0))
	if typeof(item) == TYPE_ARRAY:
		var item_id = item[0] if item.size() > 0 else -1
		var location_id = item[1] if item.size() > 1 else -1
		var player_id = item[2] if item.size() > 2 else -1
		var flags = item[3] if item.size() > 3 else 0
		return "  index=" + str(index) + " item_id=" + str(item_id) + " location_id=" + str(location_id) + " player_id=" + str(player_id) + " flags=" + str(flags)
	return "  index=" + str(index) + " raw=" + str(item)

func _print_all_hooks():
	var hook_node = main.get_node_or_null("AP Hooks")
	if hook_node == null:
		_debug_reply("AP Hooks node not found")
		return
	for category in ["checks", "symbols", "items", "essences", "abilities", "floors"]:
		var entries = hook_node.hooks.get(category, {})
		_debug_reply("HOOK CATEGORY " + category + " count=" + str(entries.size()))
		for key in entries.keys():
			var entry = entries[key]
			_debug_reply("  " + str(key) + " state=" + hook_node.state_name(int(entry.state)) + " ap_id=" + str(entry.ap_id))


func _on_ap_connected():
	_refresh_main_screen()
	_refresh_shiny_coin_hud()
	_refresh_goal_floor_hud()
	_refresh_deathlink_send_hud()
	_refresh_text_client_hud()

func _on_shiny_coin_progress_changed(_received, _required, _goal_sent):
	_refresh_main_screen()
	_refresh_shiny_coin_hud()

func _on_goal_floor_progress_changed(_completed, _required):
	_refresh_main_screen()
	_refresh_goal_floor_hud()

func _on_text_client_changed():
	_refresh_text_client_hud()

func _on_ap_status_changed(_status):
	_refresh_main_screen()
	_refresh_shiny_coin_hud()
	_refresh_goal_floor_hud()
	_refresh_deathlink_send_hud()
	_refresh_text_client_hud()

func _on_ap_settings_changed():
	_refresh_main_screen()
	_refresh_shiny_coin_hud()
	_refresh_goal_floor_hud()
	_refresh_deathlink_send_hud()
	_refresh_text_client_hud()

func _on_ap_debug_changed():
	# The external console tails APClient's log file, so no in-game refresh is needed.
	pass

func _save_settings():
	var cfg = ConfigFile.new()
	cfg.set_value("connection", "server", server)
	cfg.set_value("connection", "slot", slot_name)
	if ap_client != null:
		cfg.set_value("deathlink", "send_amnesty", int(ap_client.deathlink_send_amnesty) if ap_client.get("deathlink_send_amnesty") != null else 0)
		cfg.set_value("deathlink", "receive_amnesty", int(ap_client.deathlink_receive_amnesty) if ap_client.get("deathlink_receive_amnesty") != null else 0)
		cfg.set_value("debug", "auto_goal", bool(ap_client.auto_goal_enabled) if ap_client.get("auto_goal_enabled") != null else true)
		cfg.set_value("display", "text_client", bool(ap_client.text_client_enabled) if ap_client.get("text_client_enabled") != null else false)
		cfg.set_value("display", "text_client_filter", int(ap_client.text_client_filter_mode) if ap_client.get("text_client_filter_mode") != null else 0)
	# Password is deliberately not written to disk.
	cfg.save("user://LBAL-Archipelago.cfg")

func _load_settings():
	var cfg = ConfigFile.new()
	if cfg.load("user://LBAL-Archipelago.cfg") == OK:
		server = str(cfg.get_value("connection", "server", server))
		slot_name = str(cfg.get_value("connection", "slot", slot_name))
		# Old config files do not contain these keys; zero keeps old behavior.
		var send_amnesty = int(cfg.get_value("deathlink", "send_amnesty", 0))
		var receive_amnesty = int(cfg.get_value("deathlink", "receive_amnesty", 0))
		var auto_goal = bool(cfg.get_value("debug", "auto_goal", true))
		var text_client = bool(cfg.get_value("display", "text_client", false))
		var text_client_filter = int(cfg.get_value("display", "text_client_filter", 0))
		if ap_client != null and ap_client.has_method("set_deathlink_send_amnesty"):
			ap_client.set_deathlink_send_amnesty(send_amnesty)
		if ap_client != null and ap_client.has_method("set_deathlink_receive_amnesty"):
			ap_client.set_deathlink_receive_amnesty(receive_amnesty)
		if ap_client != null and ap_client.has_method("set_auto_goal_enabled"):
			ap_client.set_auto_goal_enabled(auto_goal)
		if ap_client != null and ap_client.has_method("set_text_client_enabled"):
			ap_client.set_text_client_enabled(text_client)
		if ap_client != null and ap_client.has_method("set_text_client_filter_mode"):
			ap_client.set_text_client_filter_mode(text_client_filter)
