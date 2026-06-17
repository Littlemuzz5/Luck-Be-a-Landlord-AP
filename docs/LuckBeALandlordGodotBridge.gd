# Luck be a Landlord Archipelago live pool bridge
# Godot 3.x / LBAL PCK-patch helper.
#
# IMPORTANT:
# A normal LBAL Workshop/user mod cannot attach this Node and run _process().
# This file is for a PCK patch/custom loader that adds this script as an Autoload
# named APLivePoolBridge, or attaches it to a node that always exists.
#
# Hook the real LBAL choice builders like this:
#   symbols_to_choose_from = APLivePoolBridge.filter_symbol_list(symbols_to_choose_from)
#   items_to_choose_from = APLivePoolBridge.filter_item_list(items_to_choose_from)
#   essences_to_choose_from = APLivePoolBridge.filter_essence_list(essences_to_choose_from)
#
# The Archipelago client writes user://ap_state.json and refreshes it whenever
# AP items/checks change. This bridge polls that JSON while the game is running,
# so the next opened Add Symbol/Add Item/Add Essence screen can change without
# restarting the game.

extends Node

signal ap_state_changed

const POLL_SECONDS := 0.25

var ap_state_path := ""
var checks_path := ""
var state := {}

var symbol_types := {}
var item_types := {}
var essence_types := {}
var always_symbol_types := {}
var always_item_types := {}

var lock_symbols := true
var lock_normal_items := true
var lock_essences := false
var has_ap_checks := false

var _last_text := ""
var _timer := 0.0

func _ready() -> void:
	var local_appdata := OS.get_environment("LOCALAPPDATA")
	if local_appdata != "":
		ap_state_path = local_appdata.plus_file("LuckBeALandlordAP").plus_file("ap_state.json")
		checks_path = local_appdata.plus_file("LuckBeALandlordAP").plus_file("checks_to_send.json")
	else:
		ap_state_path = "user://ap_state.json"
		checks_path = "user://checks_to_send.json"

	load_ap_state(true)
	set_process(true)

func _process(delta: float) -> void:
	_timer += delta
	if _timer < POLL_SECONDS:
		return
	_timer = 0.0
	load_ap_state(false)

func load_ap_state(force_emit: bool = false) -> void:
	var file := File.new()
	if not file.file_exists(ap_state_path):
		return
	if file.open(ap_state_path, File.READ) != OK:
		return
	var text := file.get_as_text()
	file.close()

	if text == _last_text and not force_emit:
		return
	_last_text = text

	var parsed = parse_json(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		return

	state = parsed
	_rebuild_sets()
	emit_signal("ap_state_changed")

func _rebuild_sets() -> void:
	symbol_types.clear()
	item_types.clear()
	essence_types.clear()
	always_symbol_types.clear()
	always_item_types.clear()

	var live_pool = state.get("live_pool", {})
	if typeof(live_pool) != TYPE_DICTIONARY:
		live_pool = {}

	lock_symbols = bool(live_pool.get("lock_symbols", state.get("mod_control", {}).get("lock_symbols", true)))
	lock_normal_items = bool(live_pool.get("lock_normal_items", state.get("mod_control", {}).get("lock_normal_items", true)))
	lock_essences = bool(live_pool.get("lock_essences", state.get("mod_control", {}).get("lock_essences", false)))
	has_ap_checks = bool(live_pool.get("has_ap_checks", state.get("next_ap_check", null) != null))

	_add_all(symbol_types, live_pool.get("symbol_types", []))
	_add_all(item_types, live_pool.get("item_types", []))
	_add_all(essence_types, live_pool.get("essence_types", []))
	_add_all(always_symbol_types, live_pool.get("always_allowed_symbol_types", []))
	_add_all(always_item_types, live_pool.get("always_allowed_item_types", []))

	# Safe fallbacks for older AP client builds that do not write live_pool yet.
	if symbol_types.empty():
		_add_display_names_as_types(symbol_types, state.get("unlocked_symbols", []))
	if item_types.empty():
		_add_display_names_as_types(item_types, state.get("unlocked_items", []))
	if essence_types.empty():
		_add_display_names_as_types(essence_types, state.get("unlocked_essences", []))

	# Vanilla safe/start symbols should never disappear from the board.
	_add_all(always_symbol_types, ["base", "empty", "dud", "coin", "cherry", "pearl", "flower", "cat", "seed"])
	_add_all(always_item_types, ["comfy_pillow"])
	if has_ap_checks:
		always_symbol_types["ap_check"] = true

func _add_all(target: Dictionary, values) -> void:
	if typeof(values) != TYPE_ARRAY:
		return
	for value in values:
		var key := str(value)
		if key != "":
			target[key] = true

func _add_display_names_as_types(target: Dictionary, values) -> void:
	if typeof(values) != TYPE_ARRAY:
		return
	for value in values:
		var key := _display_name_to_type(str(value))
		if key != "":
			target[key] = true

func _display_name_to_type(value: String) -> String:
	var result := value.to_lower()
	result = result.replace("'", "")
	result = result.replace("-", "_")
	result = result.replace(" ", "_")
	result = result.replace(".", "")
	result = result.replace(",", "")
	result = result.replace("/", "_")
	while result.find("__") != -1:
		result = result.replace("__", "_")
	result = result.strip_edges()
	while result.begins_with("_") and result.length() > 0:
		result = result.substr(1, result.length() - 1)
	while result.ends_with("_") and result.length() > 0:
		result = result.substr(0, result.length() - 1)
	return result

func is_symbol_allowed(type_name: String) -> bool:
	if not lock_symbols:
		return true
	if always_symbol_types.has(type_name):
		return true
	return symbol_types.has(type_name)

func is_item_allowed(type_name: String) -> bool:
	if not lock_normal_items:
		return true
	if always_item_types.has(type_name):
		return true
	return item_types.has(type_name)

func is_essence_allowed(type_name: String) -> bool:
	if not lock_essences:
		return true
	return essence_types.has(type_name)

func filter_symbol_list(values: Array) -> Array:
	var output := []
	for value in values:
		var type_name := _get_type_name(value)
		if type_name == "" or is_symbol_allowed(type_name):
			output.append(value)
	return output

func filter_item_list(values: Array) -> Array:
	var output := []
	for value in values:
		var type_name := _get_type_name(value)
		if type_name == "" or is_item_allowed(type_name):
			output.append(value)
	return output

func filter_essence_list(values: Array) -> Array:
	var output := []
	for value in values:
		var type_name := _get_type_name(value)
		if type_name == "" or is_essence_allowed(type_name):
			output.append(value)
	return output

func _get_type_name(value) -> String:
	if typeof(value) == TYPE_STRING:
		return str(value)
	if typeof(value) == TYPE_DICTIONARY:
		return str(value.get("type", ""))
	if typeof(value) == TYPE_OBJECT:
		if value.has_method("get_type"):
			return str(value.call("get_type"))
		var object_type = value.get("type")
		if object_type != null:
			return str(object_type)
	return ""

func send_check(location_name: String) -> void:
	var data = _read_json(checks_path)
	if typeof(data) != TYPE_DICTIONARY:
		data = {"locations": []}
	if not data.has("locations") or typeof(data["locations"]) != TYPE_ARRAY:
		data["locations"] = []
	if not data["locations"].has(location_name):
		data["locations"].append(location_name)
	_write_json(checks_path, data)

func _read_json(path: String):
	var file := File.new()
	if not file.file_exists(path):
		return null
	if file.open(path, File.READ) != OK:
		return null
	var text := file.get_as_text()
	file.close()
	return parse_json(text)

func _write_json(path: String, data) -> void:
	var dir := Directory.new()
	var folder := path.get_base_dir()
	if not dir.dir_exists(folder):
		dir.make_dir_recursive(folder)
	var file := File.new()
	if file.open(path, File.WRITE) != OK:
		return
	file.store_string(to_json(data))
	file.close()
