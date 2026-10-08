extends Node

const APData = preload("res://APData.gd")

signal status_changed(status)
signal debug_changed()
signal connected_to_ap()
signal disconnected_from_ap()
signal received_items_changed()
signal checks_changed()
signal item_received(item_id, location_id, player_id, flags, receive_index)
signal locations_updated(checked_locations, missing_locations)
signal location_check_sent(location_id)
signal packet_received(cmd, packet)
signal packet_sent(cmd, packet)
signal ap_error(message)
signal ap_settings_changed()
signal deathlink_received(data)
signal shiny_coin_progress_changed(received, required, goal_sent)
signal goal_floor_progress_changed(completed, required)
signal text_client_changed()

const GAME_NAME = "Luck be a Landlord"
const LEGACY_GAME_NAME = "Luck_be_a_Landlord"
const AP_MAJOR = 0
const AP_MINOR = 6
const AP_BUILD = 7
const WORLD_VERSION = "1.0.0"
const MAX_DEBUG_LINES = 300
const DEBUG_LOG_PATH = "user://LBAL-AP-Debug.log"
const DEBUG_FLUSH_INTERVAL = 0.20
const SHINY_COIN_ITEM_ID = 405
const DEFAULT_SHINY_COIN_REQUIRED = -1
const DEFAULT_GOAL_FLOORS_REQUIRED = -1
const MAX_TEXT_CLIENT_LINES = 30

# Older / very large LBAL APWorlds can produce a Connected packet far larger
# than Godot 3.4's default 64 KiB WebSocket input buffer. If that packet does
# not fit, the AP server briefly sees the slot join and then leave while this
# client remains stuck on RoomInfo. Use an explicit large buffer for AP traffic.
const WS_INPUT_BUFFER_KB = 65536
const WS_INPUT_MAX_PACKETS = 8192
const WS_OUTPUT_BUFFER_KB = 1024
const WS_OUTPUT_MAX_PACKETS = 2048

var socket = null
var server_address = ""
var slot_name = ""
var password = ""
var status = "Disconnected"
var last_error = ""
var last_packet = ""
var seed_name = ""
var team_number = -1
var slot_number = -1
var authenticated = false
var socket_open = false
var received_items = []
var checked_locations = []
var missing_locations = []
var slot_data = {}
var debug_lines = []
var client_uuid = ""
var current_url = ""
var attempted_secure_fallback = false
var connection_started_msec = 0
var awaiting_auth = false
var auth_started_msec = 0
var legacy_connect_retry_sent = false
var legacy_game_retry_sent = false
var last_server_close_code = -1
var last_server_close_reason = ""
var connection_debug_item_baseline = -1
var pending_debug_file_lines = []
var debug_flush_timer = 0.0
var shiny_coin_enabled = true
var shiny_coin_required = DEFAULT_SHINY_COIN_REQUIRED
var shiny_coin_received = 0
var shiny_coin_goal_sent = false
var goal_floors_required = DEFAULT_GOAL_FLOORS_REQUIRED
var goal_floors_completed = 0
var handshake_stage = "Idle"
var handshake_detail = ""
var handshake_stage_started_msec = 0
var auth_wait_log_next_msec = 0

# Local display/debug preferences. Old configs/PCK rooms have no values for
# these and therefore keep the defaults below.
var auto_goal_enabled = true
var text_client_enabled = false
# Feed filter modes:
# 0 = everything, 1 = progression + useful, 2 = progression only,
# 3 = my items (items sent to this slot OR sent out from this slot's checks).
var text_client_filter_mode = 0
var text_client_lines = []
var text_client_rich_lines = []
var text_client_line_seqs = []
var text_client_line_meta = []
var text_client_next_seq = 0

# PrintJSON uses numeric player/item/location IDs. Keep enough of the AP room
# metadata to turn those IDs into the same readable names the normal TextClient
# shows. Data packages are requested lazily per game so large multiworlds do not
# download hundreds of game tables just to render the feed.
var player_names = {0: "Archipelago"}
var player_games = {0: "Archipelago"}
var item_names_by_game = {}
var location_names_by_game = {}
var requested_data_package_games = []
var pending_print_json = []
const MAX_PENDING_PRINT_JSON = 50

# Slot/YAML-backed session options. The in-game AP menu can override the two
# booleans for the current connection without changing the generated YAML.
var ap_check_boost_enabled = false
var deathlink_enabled = false
# 0 = Force Payment, 1 = End Run (matches options.py Payment Choice).
var deathlink_mode = 1

# DeathLink amnesty counts are local client options:
# - send: ignore this many local losses before sending one DeathLink.
# - receive: ignore this many incoming DeathLinks before applying one.
# Both reset to the configured count after a DeathLink is actually sent/applied.
var deathlink_send_amnesty = 0
var deathlink_receive_amnesty = 0
var deathlink_send_amnesty_remaining = 0
var deathlink_receive_amnesty_remaining = 0

# Runtime DeathLink state. LBAL may call its game-over path multiple times for a
# single failed rent payment, so only the first callback for a run may send.
var deathlink_send_handled_this_run = false
var deathlink_remote_end_run_active = false
var last_deathlink_received_time = -1.0
var last_deathlink_received_key = ""
var last_deathlink_sent_time = -1.0
var suppress_next_deathlink_send = false
var suppress_deathlink_for_force_payment_trap = false

func _ready():
	client_uuid = _load_or_make_uuid()
	_start_debug_session()
	_make_socket()
	set_process(true)

func _process(delta):
	if socket != null and socket.get_connection_status() != NetworkedMultiplayerPeer.CONNECTION_DISCONNECTED:
		socket.poll()
		# Some very large multiworld servers can queue the Connected packet without
		# Godot 3.4 emitting data_received reliably. Drain the peer after every poll
		# as a fallback. _on_data_received() is safe to call when the queue is empty.
		_on_data_received()

	# While authenticating, keep a low-frequency breadcrumb in the debug log so
	# a long wait can be distinguished from a frozen client or dead socket.
	if awaiting_auth and not authenticated and auth_started_msec > 0:
		var auth_elapsed = OS.get_ticks_msec() - auth_started_msec
		if auth_wait_log_next_msec <= 0:
			auth_wait_log_next_msec = 10000
		if auth_elapsed >= auth_wait_log_next_msec:
			_log("AUTH WAIT elapsed_ms=" + str(auth_elapsed) + " socket_state=" + _socket_state_name() + " last_packet=" + str(last_packet) + " stage=" + handshake_stage)
			auth_wait_log_next_msec += 10000

	# Do not send a second Connect packet while authentication is pending.
	# Large/older LBAL rooms can take several seconds to build the Connected
	# packet because they may contain many thousands of locations. A duplicate
	# Connect on the same WebSocket can make the server close the connection.
	# Keep waiting for Connected or ConnectionRefused instead.

	debug_flush_timer += delta
	if debug_flush_timer >= DEBUG_FLUSH_INTERVAL:
		debug_flush_timer = 0.0
		_flush_debug_file_buffer()

func _make_socket():
	socket = WebSocketClient.new()
	# Must be configured before connect_to_url(). 16 MiB leaves plenty of room
	# for Connected/RoomUpdate packets from older floor-dependent LBAL worlds.
	var buffer_err = socket.set_buffers(
		WS_INPUT_BUFFER_KB,
		WS_INPUT_MAX_PACKETS,
		WS_OUTPUT_BUFFER_KB,
		WS_OUTPUT_MAX_PACKETS
	)
	if buffer_err == OK:
		_log("WEBSOCKET BUFFERS input_kb=" + str(WS_INPUT_BUFFER_KB) + " input_packets=" + str(WS_INPUT_MAX_PACKETS) + " output_kb=" + str(WS_OUTPUT_BUFFER_KB) + " output_packets=" + str(WS_OUTPUT_MAX_PACKETS))
	else:
		_log("WARNING: WebSocket set_buffers failed error=" + str(buffer_err))
	socket.connect("connection_established", self, "_on_connection_established")
	socket.connect("connection_error", self, "_on_connection_error")
	socket.connect("connection_closed", self, "_on_connection_closed")
	socket.connect("data_received", self, "_on_data_received")
	socket.connect("server_close_request", self, "_on_server_close_request")

func _start_debug_session():
	var file = File.new()
	if file.open(DEBUG_LOG_PATH, File.READ_WRITE) != OK:
		file.open(DEBUG_LOG_PATH, File.WRITE)
	file.seek_end()
	file.store_line("")
	file.store_line("================ LBAL ARCHIPELAGO DEBUG SESSION " + _timestamp() + " ================")
	file.close()

# Start a fresh visible log only after the AP slot is actually authenticated.
# This keeps previous runs/pre-connect menu activity out of the detachable console.
func _start_connected_debug_session():
	_flush_debug_file_buffer()
	debug_lines.clear()
	last_error = ""
	last_packet = ""
	connection_debug_item_baseline = -1
	var file = File.new()
	if file.open(DEBUG_LOG_PATH, File.WRITE) == OK:
		# APDebugConsole.ps1 watches for this marker and clears its visible window.
		file.store_line("=== AP CONNECTED SESSION ===")
		file.close()
	emit_signal("debug_changed")

func _clear_ap_session_data(reset_options = true):
	# AP state belongs to exactly one authenticated slot. Never carry received
	# items/checks/options into another slot or leave them active while offline.
	received_items.clear()
	checked_locations.clear()
	missing_locations.clear()
	slot_data = {}
	player_names = {0: "Archipelago"}
	player_games = {0: "Archipelago"}
	item_names_by_game.clear()
	location_names_by_game.clear()
	requested_data_package_games.clear()
	pending_print_json.clear()
	seed_name = ""
	team_number = -1
	slot_number = -1
	connection_debug_item_baseline = -1
	awaiting_auth = false
	auth_started_msec = 0
	auth_wait_log_next_msec = 0
	handshake_stage = "Idle"
	handshake_detail = ""
	handshake_stage_started_msec = 0
	legacy_connect_retry_sent = false
	legacy_game_retry_sent = false
	last_deathlink_received_time = -1.0
	last_deathlink_received_key = ""
	last_deathlink_sent_time = -1.0
	deathlink_send_handled_this_run = false
	deathlink_remote_end_run_active = false
	deathlink_send_amnesty_remaining = deathlink_send_amnesty
	deathlink_receive_amnesty_remaining = deathlink_receive_amnesty
	suppress_next_deathlink_send = false
	suppress_deathlink_for_force_payment_trap = false
	shiny_coin_enabled = true
	shiny_coin_required = DEFAULT_SHINY_COIN_REQUIRED
	shiny_coin_received = 0
	shiny_coin_goal_sent = false
	goal_floors_required = DEFAULT_GOAL_FLOORS_REQUIRED
	goal_floors_completed = 0
	text_client_lines.clear()
	text_client_rich_lines.clear()
	text_client_line_seqs.clear()
	text_client_line_meta.clear()
	text_client_next_seq = 0
	if reset_options:
		ap_check_boost_enabled = false
		deathlink_enabled = false
		deathlink_mode = 1
		emit_signal("ap_settings_changed")
	emit_signal("received_items_changed")
	emit_signal("checks_changed")
	emit_signal("locations_updated", [], [])
	emit_signal("shiny_coin_progress_changed", shiny_coin_received, shiny_coin_required, shiny_coin_goal_sent)
	emit_signal("goal_floor_progress_changed", goal_floors_completed, goal_floors_required)
	emit_signal("text_client_changed")

func connect_to_server(address, name, room_password = ""):
	var next_server = str(address).strip_edges()
	var next_slot = str(name).strip_edges()
	var next_password = str(room_password)

	if next_server == "":
		_set_error("Server cannot be blank")
		return
	if next_slot == "":
		_set_error("Slot Name cannot be blank")
		return

	# Tear down the old slot *before* storing the new slot name. This makes every
	# reconnect behave like a fresh AP session even when the player switches slots
	# without restarting Luck be a Landlord.
	if socket != null and socket.get_connection_status() != NetworkedMultiplayerPeer.CONNECTION_DISCONNECTED:
		socket.disconnect_from_host(1000, "Reconnect")
		socket.poll()
	authenticated = false
	socket_open = false
	_clear_ap_session_data(true)
	emit_signal("disconnected_from_ap")

	server_address = next_server
	slot_name = next_slot
	password = next_password
	last_error = ""
	attempted_secure_fallback = false
	last_server_close_code = -1
	last_server_close_reason = ""
	awaiting_auth = false
	auth_started_msec = 0
	legacy_connect_retry_sent = false
	legacy_game_retry_sent = false
	_make_socket()

	var url = _normalise_url(server_address)
	_begin_connection(url)

func _begin_connection(url):
	current_url = str(url)
	connection_started_msec = OS.get_ticks_msec()
	_set_handshake_stage("Opening WebSocket", current_url)
	_log("CONNECT ATTEMPT url=" + current_url + " slot=" + slot_name + " game=" + GAME_NAME)
	_log("SOCKET STATE before connect=" + _socket_state_name())
	_set_status("Connecting...")
	var err = socket.connect_to_url(current_url, PoolStringArray(), false)
	_log("connect_to_url return=" + _error_name(err) + " (" + str(err) + ")")
	if err != OK:
		_set_error("WebSocket connect_to_url failed: " + _error_name(err) + " (" + str(err) + ") url=" + current_url)

func _retry_secure_connection():
	if attempted_secure_fallback:
		return
	attempted_secure_fallback = true
	var secure_url = current_url
	if secure_url.begins_with("ws://"):
		secure_url = "wss://" + secure_url.substr(5, secure_url.length() - 5)
	else:
		return
	_log("WS connection failed before RoomInfo; retrying with TLS as " + secure_url)
	_set_status("Retrying secure connection...")
	_make_socket()
	_begin_connection(secure_url)

func disconnect_from_server():
	if socket != null and socket.get_connection_status() != NetworkedMultiplayerPeer.CONNECTION_DISCONNECTED:
		socket.disconnect_from_host(1000, "User disconnected")
	authenticated = false
	socket_open = false
	_clear_ap_session_data(true)
	_set_status("Disconnected")
	_log("Disconnected; AP slot state cleared and vanilla state restored")
	emit_signal("disconnected_from_ap")

func reconnect():
	if server_address == "" or slot_name == "":
		_set_error("Enter a Server and Slot Name first")
		return
	connect_to_server(server_address, slot_name, password)

func is_connected_to_ap():
	return authenticated and socket_open

func send_sync():
	if not authenticated:
		_set_error("Not connected to Archipelago")
		return
	_send_packets([{"cmd": "Sync"}])
	_log("Sent Sync")

func send_location_check(location_id):
	if not authenticated:
		_set_error("Not connected to Archipelago")
		return false
	var check_id = int(location_id)
	_send_packets([{"cmd": "LocationChecks", "locations": [check_id]}])
	if not checked_locations.has(check_id):
		checked_locations.append(check_id)
	missing_locations.erase(check_id)
	_log("Sent LocationChecks ID=" + str(check_id))
	emit_signal("location_check_sent", check_id)
	emit_signal("checks_changed")
	_update_goal_floor_progress()
	return true

func send_location_checks(location_ids):
	if not authenticated:
		_set_error("Not connected to Archipelago")
		return false
	var ids = []
	for value in location_ids:
		ids.append(int(value))
	_send_packets([{"cmd": "LocationChecks", "locations": ids}])
	for check_id in ids:
		if not checked_locations.has(check_id):
			checked_locations.append(check_id)
		missing_locations.erase(check_id)
	_log("Sent LocationChecks IDs=" + str(ids))
	for check_id in ids:
		emit_signal("location_check_sent", check_id)
	emit_signal("checks_changed")
	_update_goal_floor_progress()
	return true

func send_goal():
	if not authenticated:
		_set_error("Not connected to Archipelago")
		return false
	if shiny_coin_goal_sent:
		return true
	_send_packets([{"cmd": "StatusUpdate", "status": 30}])
	shiny_coin_goal_sent = true
	_log("Sent goal status")
	emit_signal("shiny_coin_progress_changed", shiny_coin_received, shiny_coin_required, shiny_coin_goal_sent)
	return true

func send_say(message):
	if not authenticated:
		return false
	_send_packets([{"cmd": "Say", "text": str(message)}])
	return true

func clear_debug_log():
	pending_debug_file_lines.clear()
	debug_lines.clear()
	last_packet = ""
	last_error = ""
	var file = File.new()
	if file.open(DEBUG_LOG_PATH, File.WRITE) == OK:
		file.store_line("================ AP DEBUG LOG CLEARED " + _timestamp() + " ================")
		file.close()
	emit_signal("debug_changed")

func debug_log(value):
	_log(value)

func get_debug_text():
	var out = []
	out.append("APWorld: " + GAME_NAME + " v" + WORLD_VERSION)
	out.append("Protocol: " + str(AP_MAJOR) + "." + str(AP_MINOR) + "." + str(AP_BUILD))
	out.append("Status: " + status)
	out.append("Server: " + server_address)
	out.append("Slot: " + slot_name)
	out.append("Current URL: " + current_url)
	out.append("Socket state: " + _socket_state_name())
	if handshake_stage != "" and handshake_stage != "Idle":
		out.append("Handshake stage: " + handshake_stage)
		if handshake_detail != "":
			out.append("Handshake detail: " + handshake_detail)
	if seed_name != "":
		out.append("Seed: " + seed_name)
	out.append("Received items: " + str(received_items.size()))
	out.append("Checked locations: " + str(checked_locations.size()))
	out.append("Missing locations: " + str(missing_locations.size()))
	out.append("AP Check Boost: " + ("ON" if ap_check_boost_enabled else "OFF"))
	out.append("DeathLink: " + ("ON" if deathlink_enabled else "OFF") + " (" + get_deathlink_mode_name() + ")")
	out.append("DeathLink Amnesty: send=" + str(deathlink_send_amnesty) + " (remaining " + str(deathlink_send_amnesty_remaining) + "), receive=" + str(deathlink_receive_amnesty) + " (remaining " + str(deathlink_receive_amnesty_remaining) + ")")
	out.append("Auto Goal Send: " + ("ON" if auto_goal_enabled else "OFF"))
	out.append("Text Client Feed: " + ("ON" if text_client_enabled else "OFF"))
	out.append(get_goal_floor_progress_text())
	if last_error != "":
		out.append("Error: " + last_error)
	if last_server_close_code >= 0:
		out.append("Server close: code=" + str(last_server_close_code) + " reason=" + last_server_close_reason)
	if last_packet != "":
		out.append("Last packet: " + last_packet)
	if debug_lines.size() > 0:
		out.append("")
		out.append("Recent log:")
		var start = max(0, debug_lines.size() - 6)
		for i in range(start, debug_lines.size()):
			out.append(str(debug_lines[i]))
	return _join_lines(out)

func _set_handshake_stage(stage, detail = ""):
	handshake_stage = str(stage)
	handshake_detail = str(detail)
	handshake_stage_started_msec = OS.get_ticks_msec()

func get_connection_handshake_text():
	if handshake_stage == "" or handshake_stage == "Idle":
		return ""

	var out = []
	out.append("Handshake: " + handshake_stage)

	if handshake_detail != "":
		out.append("Detail: " + handshake_detail)

	if handshake_stage_started_msec > 0 and not authenticated:
		var elapsed_ms = OS.get_ticks_msec() - handshake_stage_started_msec
		var whole_seconds = int(elapsed_ms / 1000)
		var tenths = int((elapsed_ms % 1000) / 100)
		out.append("Waiting: " + str(whole_seconds) + "." + str(tenths) + "s")

	out.append("Socket: " + _socket_state_name())

	if last_packet != "":
		out.append("Last packet: " + str(last_packet))

	return _join_lines(out)

func _normalise_url(address):
	var url = str(address).strip_edges()
	if url.begins_with("archipelago://"):
		url = url.substr(14, url.length() - 14)
	if not url.begins_with("ws://") and not url.begins_with("wss://"):
		# Archipelago's public WebHost rooms normally require TLS. The official AP
		# client also retries ws:// as wss:// when the first handshake is encrypted.
		if url.to_lower().begins_with("archipelago.gg:") or url.to_lower() == "archipelago.gg":
			url = "wss://" + url
		else:
			url = "ws://" + url
	return url

func _on_connection_established(protocol = ""):
	socket_open = true
	var elapsed = OS.get_ticks_msec() - connection_started_msec
	_set_handshake_stage("WebSocket connected", "Waiting for RoomInfo")
	_set_status("Socket connected - waiting for RoomInfo")
	_log("WEBSOCKET CONNECTED url=" + current_url + " elapsed_ms=" + str(elapsed) + " host=" + socket.get_connected_host() + " port=" + str(socket.get_connected_port()))
	if protocol != "":
		_log("WebSocket subprotocol=" + protocol)

func _on_connection_error():
	socket_open = false
	authenticated = false
	var elapsed = OS.get_ticks_msec() - connection_started_msec
	var details = "WebSocket connection_error signal url=" + current_url + " elapsed_ms=" + str(elapsed) + " socket_state=" + _socket_state_name()
	_set_handshake_stage("Connection error", details)
	_log("ERROR DETAIL: " + details)

	# Match Archipelago CommonClient behavior: if a plaintext ws:// handshake fails
	# before receiving RoomInfo, retry the same host/port using wss://.
	if current_url.begins_with("ws://") and not attempted_secure_fallback:
		call_deferred("_retry_secure_connection")
		return

	_clear_ap_session_data(true)
	_set_handshake_stage("Connection error", details)
	_set_error("Connection failed: " + current_url + " (" + _socket_state_name() + "). Check host/port, firewall, and whether the room is still running.")
	emit_signal("disconnected_from_ap")

func _on_server_close_request(code, reason):
	last_server_close_code = int(code)
	last_server_close_reason = str(reason)
	_log("SERVER CLOSE REQUEST code=" + str(code) + " reason=" + str(reason))
	if reason != "":
		last_error = "Server requested close " + str(code) + ": " + str(reason)

func _on_connection_closed(was_clean = false):
	socket_open = false
	authenticated = false
	_clear_ap_session_data(true)
	var detail = "WebSocket closed clean=" + str(was_clean) + " url=" + current_url + " socket_state=" + _socket_state_name()
	_set_handshake_stage("Socket closed", detail)
	if last_server_close_code >= 0:
		detail += " close_code=" + str(last_server_close_code) + " close_reason=" + last_server_close_reason
	_log(detail)
	if was_clean:
		_set_status("Disconnected")
	else:
		_set_status("Connection closed")
	emit_signal("disconnected_from_ap")

func _on_data_received():
	var peer = socket.get_peer(1)
	if peer == null:
		_set_error("data_received fired but WebSocket peer was null")
		return
	while peer.get_available_packet_count() > 0:
		var raw = peer.get_packet().get_string_from_utf8()
		var parsed = JSON.parse(raw)
		if parsed.error != OK:
			_log("RAW <- " + raw)
			_set_error("Invalid JSON from server: " + parsed.error_string)
			continue
		var packets = parsed.result
		if typeof(packets) != TYPE_ARRAY:
			_log("RAW <- " + raw)
			_set_error("Server packet was not an array")
			continue
		# ReceivedItems index 0 is the server replaying item history. Do not dump
		# that entire old history into the live console; _handle_received_items()
		# will print only items that are new for this connected session.
		var only_received_items = packets.size() > 0
		for packet in packets:
			if typeof(packet) != TYPE_DICTIONARY or str(packet.get("cmd", "")) != "ReceivedItems":
				only_received_items = false
				break
		if not only_received_items:
			_log("RAW <- " + raw)
		for packet in packets:
			if typeof(packet) == TYPE_DICTIONARY:
				_handle_packet(packet)

func _handle_packet(packet):
	var cmd = str(packet.get("cmd", "Unknown"))
	last_packet = cmd
	# ReceivedItems can contain the entire historical item list and DataPackage
	# can contain thousands of names. Keep the live console concise.
	if cmd != "ReceivedItems" and cmd != "DataPackage":
		_log("<- " + cmd + " " + JSON.print(packet))
	elif cmd == "DataPackage":
		_log("<- DataPackage")
	emit_signal("packet_received", cmd, packet)

	match cmd:
		"RoomInfo":
			seed_name = str(packet.get("seed_name", ""))
			_log("ROOM INFO seed=" + seed_name + " password_required=" + str(packet.get("password", false)) + " tags=" + str(packet.get("tags", [])) + " server_version=" + str(packet.get("version", {})) + " generator_version=" + str(packet.get("generator_version", {})))
			awaiting_auth = true
			auth_started_msec = OS.get_ticks_msec()
			legacy_connect_retry_sent = false
			legacy_game_retry_sent = false
			_set_status("Authenticating...")
			_send_connect(true, GAME_NAME)
			_set_handshake_stage("Connect sent", "Waiting for Connected / ConnectionRefused")
			auth_wait_log_next_msec = 10000
		"Connected":
			authenticated = true
			awaiting_auth = false
			_parse_player_context(packet)
			# Load the exact LBAL name table from the room. This matters for older
			# APWorlds whose IDs differ from the bundled current metadata.
			_request_game_data(GAME_NAME)
			auth_wait_log_next_msec = 0
			_set_handshake_stage("Authenticated", "Server accepted the slot")
			# Everything before this point was connection/setup activity or from an
			# older run. Start the visible debug session here.
			_start_connected_debug_session()
			last_error = ""
			checked_locations = _to_int_array(packet.get("checked_locations", []))
			missing_locations = _to_int_array(packet.get("missing_locations", []))
			slot_data = packet.get("slot_data", {})
			_apply_slot_options()
			_update_shiny_coin_progress(false)
			_update_goal_floor_progress()
			_set_status("Connected")
			_update_deathlink_tags()
			_log("Authenticated as " + slot_name)
			_log("CHECKED LOCATIONS count=" + str(checked_locations.size()))
			_log("MISSING LOCATIONS count=" + str(missing_locations.size()))
			_log("SLOT DATA=" + JSON.print(slot_data))
			emit_signal("connected_to_ap")
			emit_signal("checks_changed")
			emit_signal("locations_updated", checked_locations.duplicate(), missing_locations.duplicate())
			# Ask the server for a clean item sync after authentication.
			send_sync()
		"ConnectionRefused":
			authenticated = false
			var errors = packet.get("errors", [])
			var error_text = _join_values(errors, ", ") if typeof(errors) == TYPE_ARRAY else str(errors)
			_set_handshake_stage("Connection refused", error_text)
			# A few very old LBAL test rooms used the underscored internal game name.
			# Retry that spelling only when the server explicitly reports a game/slot
			# mismatch; modern rooms keep the canonical spaced name.
			var lower_errors = error_text.to_lower()
			if not legacy_game_retry_sent and (lower_errors.find("invalidgame") >= 0 or lower_errors.find("invalid game") >= 0):
				legacy_game_retry_sent = true
				awaiting_auth = true
				auth_started_msec = OS.get_ticks_msec()
				_log("LEGACY GAME NAME retry using " + LEGACY_GAME_NAME)
				_set_status("Authenticating (legacy game name)...")
				_send_connect(false, LEGACY_GAME_NAME)
				_set_handshake_stage("Legacy game-name Connect sent", "Waiting for Connected / ConnectionRefused")
				auth_wait_log_next_msec = 10000
				return
			awaiting_auth = false
			var message = "Connection refused"
			if error_text != "":
				message += ": " + error_text
			_set_error(message)
		"ReceivedItems":
			_handle_received_items(packet)
		"RoomUpdate":
			if packet.has("players") or packet.has("slot_info"):
				_parse_player_context(packet, false)
			# RoomUpdate.checked_locations is a delta from the server, not a full
			# replacement list. Replacing the array discarded all older checks and
			# made AP progression state increasingly unreliable during a long run.
			if packet.has("checked_locations"):
				var newly_checked = _to_int_array(packet["checked_locations"])
				for location_id in newly_checked:
					if not checked_locations.has(location_id):
						checked_locations.append(location_id)
					missing_locations.erase(location_id)
				_log("ROOM UPDATE CHECKED IDS=" + str(newly_checked))
			if packet.has("missing_locations"):
				missing_locations = _to_int_array(packet["missing_locations"])
				_log("ROOM UPDATE MISSING IDS=" + str(missing_locations))
			emit_signal("checks_changed")
			emit_signal("locations_updated", checked_locations.duplicate(), missing_locations.duplicate())
			_update_goal_floor_progress()
		"Print":
			var plain_text = str(packet.get("text", "")).strip_edges()
			if plain_text != "":
				_log(plain_text)
				_append_text_client_message(plain_text, _bbcode_escape(plain_text))
		"PrintJSON":
			_handle_print_json(packet.get("data", []))
		"DataPackage":
			_consume_data_package(packet.get("data", {}))
			_flush_pending_print_json()
		"Bounced":
			_handle_bounced(packet)
		_:
			pass
	emit_signal("debug_changed")


func _slot_option_value(names, default_value):
	if typeof(slot_data) != TYPE_DICTIONARY:
		return default_value

	# Current LBAL APWorlds keep the generated options inside
	# slot_data["options"]. Older rooms/PCKs may expose keys directly at the
	# top level, so support both layouts for backwards compatibility.
	var sources = [slot_data]
	if slot_data.has("options") and typeof(slot_data["options"]) == TYPE_DICTIONARY:
		sources.append(slot_data["options"])

	for source in sources:
		for wanted in names:
			for actual in source.keys():
				if str(actual).to_lower() == str(wanted).to_lower():
					return source[actual]
	return default_value

func _slot_option_bool(names, default_value = false):
	var value = _slot_option_value(names, default_value)
	if typeof(value) == TYPE_BOOL:
		return value
	if typeof(value) == TYPE_INT or typeof(value) == TYPE_REAL:
		return int(value) != 0
	var s = str(value).to_lower().strip_edges()
	return s in ["1", "true", "yes", "on", "enabled"]

func _apply_slot_options():
	ap_check_boost_enabled = _slot_option_bool(["APCheckBoost", "ap_check_boost"], false)
	deathlink_enabled = _slot_option_bool(["Deathlink", "deathlink"], false)
	deathlink_mode = int(_slot_option_value(["Payment", "payment", "deathlink_mode"], 1))

	# New APWorlds can provide DeathLink amnesty directly through slot_data.
	# If these keys are absent (older APWorld/room), keep the locally saved
	# in-game values so this PCK remains backwards compatible.
	deathlink_send_amnesty = max(0, int(_slot_option_value(
		["DeathlinkSendAmnesty", "deathlink_send_amnesty"],
		deathlink_send_amnesty
	)))
	deathlink_receive_amnesty = max(0, int(_slot_option_value(
		["DeathlinkReceiveAmnesty", "deathlink_receive_amnesty"],
		deathlink_receive_amnesty
	)))

	# New APWorlds explicitly tell the client whether Shiny Coins are part of the goal.
	# Default to true for old rooms that predate this flag, preserving legacy behaviour.
	shiny_coin_enabled = _slot_option_bool(["ShinyCoin", "shiny_coin", "ShinyCoins", "shiny_coins"], true)

	# v14+ APWorlds send the exact McGuffin requirement in slot_data.
	# If Shiny Coins are disabled, force the requirement to 0 so they can never
	# block or independently trigger goal completion.
	shiny_coin_required = int(_slot_option_value(["HowmanyShinyCoins", "howmany_shiny_coins", "shiny_coin_required", "ShinyCoinRequired"], DEFAULT_SHINY_COIN_REQUIRED))
	if not shiny_coin_enabled:
		shiny_coin_required = 0
	elif shiny_coin_required < 0:
		_log("SHINY COIN requirement missing from slot_data; legacy room goal is unknown")

	# GoalFloors is optional so old APWorlds remain compatible. New APWorlds can
	# expose it through slot_data to show floor-goal progress in the client.
	goal_floors_required = int(_slot_option_value(
		["GoalFloors", "goal_floors", "FloorsToGoal", "floors_to_goal"],
		DEFAULT_GOAL_FLOORS_REQUIRED
	))
	if goal_floors_required < 0:
		_log("GOAL FLOORS requirement missing from slot_data; legacy room floor goal is unknown")
	if deathlink_mode != 0:
		deathlink_mode = 1
	last_deathlink_received_time = -1.0
	last_deathlink_received_key = ""
	last_deathlink_sent_time = -1.0
	deathlink_send_handled_this_run = false
	deathlink_remote_end_run_active = false
	deathlink_send_amnesty_remaining = deathlink_send_amnesty
	deathlink_receive_amnesty_remaining = deathlink_receive_amnesty
	suppress_next_deathlink_send = false
	suppress_deathlink_for_force_payment_trap = false
	_log("AP OPTIONS ap_check_boost=" + str(ap_check_boost_enabled) + " deathlink=" + str(deathlink_enabled) + " deathlink_mode=" + get_deathlink_mode_name() + " send_amnesty=" + str(deathlink_send_amnesty) + " receive_amnesty=" + str(deathlink_receive_amnesty) + " shiny_coins_enabled=" + str(shiny_coin_enabled) + " shiny_coins_required=" + str(shiny_coin_required) + " goal_floors_required=" + str(goal_floors_required))
	emit_signal("shiny_coin_progress_changed", shiny_coin_received, shiny_coin_required, shiny_coin_goal_sent)
	emit_signal("goal_floor_progress_changed", goal_floors_completed, goal_floors_required)
	emit_signal("ap_settings_changed")

func set_ap_check_boost_enabled(value):
	ap_check_boost_enabled = bool(value)
	_log("AP CHECK BOOST " + ("ON" if ap_check_boost_enabled else "OFF"))
	emit_signal("ap_settings_changed")

func toggle_ap_check_boost():
	set_ap_check_boost_enabled(not ap_check_boost_enabled)

func set_deathlink_enabled(value):
	deathlink_enabled = bool(value)
	_update_deathlink_tags()
	_log("DEATHLINK " + ("ON" if deathlink_enabled else "OFF") + " mode=" + get_deathlink_mode_name())
	emit_signal("ap_settings_changed")

func toggle_deathlink():
	set_deathlink_enabled(not deathlink_enabled)

func set_deathlink_send_amnesty(value):
	deathlink_send_amnesty = max(0, int(value))
	deathlink_send_amnesty_remaining = deathlink_send_amnesty
	_log("DEATHLINK SEND AMNESTY set=" + str(deathlink_send_amnesty))
	emit_signal("ap_settings_changed")

func set_deathlink_receive_amnesty(value):
	deathlink_receive_amnesty = max(0, int(value))
	deathlink_receive_amnesty_remaining = deathlink_receive_amnesty
	_log("DEATHLINK RECEIVE AMNESTY set=" + str(deathlink_receive_amnesty))
	emit_signal("ap_settings_changed")

func set_auto_goal_enabled(value):
	auto_goal_enabled = bool(value)
	_log("AUTO GOAL SEND " + ("ON" if auto_goal_enabled else "OFF"))
	emit_signal("ap_settings_changed")

func toggle_auto_goal_enabled():
	set_auto_goal_enabled(not auto_goal_enabled)

func set_text_client_enabled(value):
	text_client_enabled = bool(value)
	_log("TEXT CLIENT FEED " + ("ON" if text_client_enabled else "OFF"))
	emit_signal("text_client_changed")
	emit_signal("ap_settings_changed")

func toggle_text_client_enabled():
	set_text_client_enabled(not text_client_enabled)

func set_text_client_filter_mode(value):
	text_client_filter_mode = posmod(int(value), 4)
	_log("TEXT CLIENT FILTER " + get_text_client_filter_name())
	emit_signal("text_client_changed")
	emit_signal("ap_settings_changed")

func cycle_text_client_filter_mode():
	set_text_client_filter_mode(text_client_filter_mode + 1)

func get_text_client_filter_name():
	match int(text_client_filter_mode):
		1:
			return "PROG+USEFUL"
		2:
			return "PROGRESSION"
		3:
			return "MY ITEMS"
	return "ALL"

func get_deathlink_mode_name():
	return "Force Payment" if int(deathlink_mode) == 0 else "End Run"

func _update_deathlink_tags():
	if not authenticated:
		return
	var tags = ["AP"]
	if deathlink_enabled:
		tags.append("DeathLink")
	_send_packets([{"cmd": "ConnectUpdate", "tags": tags}])

func send_deathlink(cause = "Failed to pay rent in Luck be a Landlord"):
	if not authenticated or not deathlink_enabled:
		return false

	# A single failed payment can trigger game_over more than once. Treat the whole
	# run-ending sequence as one local death event.
	if deathlink_send_handled_this_run:
		_log("DEATHLINK duplicate local send suppressed for current run")
		return false
	deathlink_send_handled_this_run = true

	# A DeathLink received from another player, or a Force Payment trap, must never
	# bounce a fresh DeathLink back to the room. Keep suppression armed until the
	# next run so duplicate game_over callbacks cannot escape it.
	if suppress_next_deathlink_send:
		_log("DEATHLINK send suppressed for remote-triggered loss")
		return false
	if suppress_deathlink_for_force_payment_trap:
		_log("DEATHLINK send suppressed because loss was caused by Force Payment")
		return false

	# Send amnesty counts whole local losses, not duplicate callbacks. Example:
	# amnesty 2 = forgive two local losses, send on the third.
	if deathlink_send_amnesty_remaining > 0:
		deathlink_send_amnesty_remaining -= 1
		_log("DEATHLINK SEND AMNESTY used remaining=" + str(deathlink_send_amnesty_remaining))
		return false

	var event_time = float(OS.get_unix_time())
	last_deathlink_sent_time = event_time
	deathlink_send_amnesty_remaining = deathlink_send_amnesty
	var data = {
		"time": event_time,
		"source": slot_name,
		"cause": str(cause)
	}
	_send_packets([{"cmd": "Bounce", "tags": ["DeathLink"], "data": data}])
	_log("DEATHLINK SENT cause=" + str(cause) + " next_send_amnesty=" + str(deathlink_send_amnesty_remaining))
	return true

func reset_deathlink_run_state():
	deathlink_send_handled_this_run = false
	deathlink_remote_end_run_active = false
	suppress_next_deathlink_send = false
	suppress_deathlink_for_force_payment_trap = false
	_log("DEATHLINK run state reset")

func suppress_next_deathlink_for_remote_loss():
	suppress_next_deathlink_send = true
	deathlink_remote_end_run_active = true

func arm_force_payment_deathlink_suppression():
	suppress_deathlink_for_force_payment_trap = true
	_log("DEATHLINK suppression armed for Force Payment")

func clear_force_payment_deathlink_suppression():
	if suppress_deathlink_for_force_payment_trap:
		suppress_deathlink_for_force_payment_trap = false
		_log("DEATHLINK Force Payment suppression cleared after successful rent payment")

func _handle_bounced(packet):
	var tags = packet.get("tags", [])
	if typeof(tags) != TYPE_ARRAY or not tags.has("DeathLink"):
		return
	if not deathlink_enabled:
		return
	var data = packet.get("data", {})
	if typeof(data) != TYPE_DICTIONARY:
		return

	var source = str(data.get("source", "Unknown"))
	var cause = str(data.get("cause", ""))
	var event_time = float(data.get("time", 0))

	# Do not apply the Bounce we just sent ourselves.
	if source == slot_name:
		return

	# Suppress a literal duplicate packet without incorrectly discarding two
	# different players who happened to die in the same second.
	var event_key = source + "|" + str(event_time) + "|" + cause
	if event_key == last_deathlink_received_key:
		_log("DEATHLINK duplicate incoming packet suppressed source=" + source)
		return
	last_deathlink_received_key = event_key
	if event_time > 0:
		last_deathlink_received_time = event_time

	# Once an End Run DeathLink has been applied, ignore any additional incoming
	# DeathLinks until the next run starts. This prevents several simultaneous
	# DeathLinks from queueing several game-over events.
	if deathlink_remote_end_run_active and int(deathlink_mode) != 0:
		_log("DEATHLINK incoming ignored because remote End Run is already active")
		return

	# Receive amnesty counts incoming DeathLinks. Example: amnesty 2 = ignore two,
	# apply the third, then reset the counter back to 2.
	if deathlink_receive_amnesty_remaining > 0:
		deathlink_receive_amnesty_remaining -= 1
		_log("DEATHLINK RECEIVE AMNESTY used source=" + source + " remaining=" + str(deathlink_receive_amnesty_remaining))
		return

	deathlink_receive_amnesty_remaining = deathlink_receive_amnesty
	if int(deathlink_mode) != 0:
		deathlink_remote_end_run_active = true

	_log("DEATHLINK RECEIVED source=" + source + " cause=" + cause + " mode=" + get_deathlink_mode_name() + " next_receive_amnesty=" + str(deathlink_receive_amnesty_remaining))
	emit_signal("deathlink_received", data)

func _send_connect(request_slot_data = true, game_name = GAME_NAME):
	var payload = {
		"cmd": "Connect",
		"password": password,
		"game": str(game_name),
		"name": slot_name,
		"uuid": client_uuid,
		"version": {
			"major": AP_MAJOR,
			"minor": AP_MINOR,
			"build": AP_BUILD,
			"class": "Version"
		},
		"tags": ["AP"],
		"items_handling": 7,
		"slot_data": bool(request_slot_data)
	}
	_send_packets([payload])
	_log("-> Connect (game=" + str(game_name) + ", slot=" + slot_name + ", slot_data=" + str(bool(request_slot_data)) + ")")

func _send_packets(packets):
	if socket == null or socket.get_connection_status() == NetworkedMultiplayerPeer.CONNECTION_DISCONNECTED:
		return false
	var peer = socket.get_peer(1)
	if peer == null:
		return false
	var encoded = JSON.print(packets)
	var safe_encoded_packets = []
	for p in packets:
		if typeof(p) == TYPE_DICTIONARY:
			var safe_copy = p.duplicate(true)
			if safe_copy.has("password") and str(safe_copy["password"]) != "":
				safe_copy["password"] = "<redacted>"
			safe_encoded_packets.append(safe_copy)
		else:
			safe_encoded_packets.append(p)
	_log("RAW -> " + JSON.print(safe_encoded_packets))
	# Archipelago's server protocol expects JSON in WebSocket TEXT frames.
	# Godot's WebSocketPeer defaults to binary frames for put_packet(), which
	# makes Python websockets deliver bytes and breaks Archipelago NetUtils.decode.
	peer.set_write_mode(WebSocketPeer.WRITE_MODE_TEXT)
	_log("SEND FRAME type=TEXT bytes=" + str(encoded.to_utf8().size()))
	var err = peer.put_packet(encoded.to_utf8())
	if err != OK:
		_set_error("Send error " + str(err))
		return false
	for packet in packets:
		if typeof(packet) == TYPE_DICTIONARY:
			var safe_packet = packet.duplicate(true)
			if safe_packet.has("password") and str(safe_packet["password"]) != "":
				safe_packet["password"] = "<redacted>"
			var cmd = str(safe_packet.get("cmd", "Unknown"))
			_log("-> " + cmd + " " + JSON.print(safe_packet))
			emit_signal("packet_sent", cmd, safe_packet)
	return true

func _handle_received_items(packet):
	var index = int(packet.get("index", 0))
	var incoming = packet.get("items", [])
	if typeof(incoming) != TYPE_ARRAY:
		return

	var first_history_sync = connection_debug_item_baseline < 0 and index == 0
	var previous_baseline = connection_debug_item_baseline

	if index == 0:
		received_items.clear()
	elif index != received_items.size():
		_log("Item index mismatch: expected " + str(received_items.size()) + ", got " + str(index))
		# Archipelago recommends a Sync when item indexes do not line up.
		_send_packets([{"cmd": "Sync"}, {"cmd": "LocationChecks", "locations": checked_locations}])

	var receive_index = index
	var live_new_count = 0
	for item in incoming:
		received_items.append(item)
		var item_id = _network_item_value(item, "item", 0)
		var location_id = _network_item_value(item, "location", 1)
		var player_id = _network_item_value(item, "player", 2)
		var flags = _network_item_value(item, "flags", 3)

		# Always emit the signal so hooks can rebuild state from history, but only
		# print entries that arrived after this connection's initial history sync.
		var is_live_new = previous_baseline >= 0 and receive_index >= previous_baseline
		if is_live_new:
			_log("RECEIVED ITEM index=" + str(receive_index) + " item_id=" + str(item_id) + " location_id=" + str(location_id) + " player_id=" + str(player_id) + " flags=" + str(flags))
			live_new_count += 1
		emit_signal("item_received", item_id, location_id, player_id, flags, receive_index)
		receive_index += 1

	if first_history_sync:
		connection_debug_item_baseline = received_items.size()
		_log("AP state sync complete; existing_items=" + str(received_items.size()) + " (history hidden)")
	else:
		connection_debug_item_baseline = max(connection_debug_item_baseline, received_items.size())
		if live_new_count > 0:
			_log("Received " + str(live_new_count) + " new item(s); total=" + str(received_items.size()))
	_update_shiny_coin_progress(true)
	emit_signal("received_items_changed")

func _goal_requirements_met():
	# Shiny Coins only matter when the APWorld has them enabled.
	var shiny_ok = true
	if shiny_coin_enabled:
		if shiny_coin_required < 0:
			return false
		shiny_ok = shiny_coin_received >= shiny_coin_required

	# A GoalFloors value of 0 means there is no floor requirement. A negative
	# value means an old room did not provide this option, so do not guess.
	var floors_ok = true
	if goal_floors_required < 0:
		# Legacy rooms historically used the Shiny Coin goal only.
		floors_ok = shiny_coin_enabled
	elif goal_floors_required > 0:
		floors_ok = goal_floors_completed >= goal_floors_required

	return shiny_ok and floors_ok

func _maybe_send_goal():
	if not authenticated or shiny_coin_goal_sent or not auto_goal_enabled:
		return
	if _goal_requirements_met():
		_log("GOAL requirements met; sending StatusUpdate CLIENT_GOAL")
		send_goal()

func _update_shiny_coin_progress(allow_goal = true):
	var count = 0
	for item in received_items:
		if _network_item_value(item, "item", 0) == SHINY_COIN_ITEM_ID:
			count += 1
	var changed = count != shiny_coin_received
	shiny_coin_received = count
	if changed and shiny_coin_enabled:
		_log("SHINY COIN progress=" + str(shiny_coin_received) + "/" + str(shiny_coin_required))
	if allow_goal:
		_maybe_send_goal()
	emit_signal("shiny_coin_progress_changed", shiny_coin_received, shiny_coin_required, shiny_coin_goal_sent)

func _update_goal_floor_progress():
	var count = 0
	# In the current APWorld a floor is complete when its final Payment 12 check
	# has been sent. Looking the ID up by name keeps this compatible if IDs move.
	for floor_number in range(1, 21):
		var location_name = "Floor " + str(floor_number) + " Payment 12"
		if APData.LOCATION_NAME_TO_ID.has(location_name):
			var location_id = int(APData.LOCATION_NAME_TO_ID[location_name])
			if checked_locations.has(location_id):
				count += 1
	var changed = count != goal_floors_completed
	goal_floors_completed = count
	if changed:
		_log("GOAL FLOORS progress=" + str(goal_floors_completed) + "/" + ("?" if goal_floors_required < 0 else str(goal_floors_required)))
	_maybe_send_goal()
	emit_signal("goal_floor_progress_changed", goal_floors_completed, goal_floors_required)

func get_goal_floor_progress_text():
	if goal_floors_required < 0:
		return "Goal Floors: " + str(goal_floors_completed) + " / ?"
	if goal_floors_required == 0:
		return "Goal Floors: OFF"
	var left = max(0, goal_floors_required - goal_floors_completed)
	return "Goal Floors: " + str(goal_floors_completed) + " / " + str(goal_floors_required) + " (" + str(left) + " left)"

func _bbcode_escape(value):
	# RichTextLabel parses brackets as BBCode. Preserve normal AP text such as
	# [AP] without accidentally escaping the [lb]/[rb] tags themselves.
	var text = str(value)
	text = text.replace("[", "__AP_LBRACKET__")
	text = text.replace("]", "__AP_RBRACKET__")
	text = text.replace("__AP_LBRACKET__", "[lb]")
	text = text.replace("__AP_RBRACKET__", "[rb]")
	return text

func _next_text_client_seq():
	text_client_next_seq += 1
	return text_client_next_seq

func _should_skip_text_client_line(value):
	# The desktop TextClient has room for connection boilerplate. The in-game
	# feed is intentionally small, so keep it focused on actual room activity.
	var lower = str(value).strip_edges().to_lower()
	if lower.begins_with("now that you are connected"):
		return true
	if lower.begins_with("warning: your client does not support compressed websocket connections"):
		return true
	return false

func _append_text_client_message(value, rich_value = "", message_seq = -1, meta = {}):
	var line = str(value).replace("\r", " ").replace("\n", " ").strip_edges()
	if line == "" or _should_skip_text_client_line(line):
		return
	var rich_line = str(rich_value).replace("\r", " ").replace("\n", " ").strip_edges()
	if rich_line == "":
		rich_line = _bbcode_escape(line)

	var seq = int(message_seq)
	if seq < 0:
		seq = _next_text_client_seq()
	else:
		text_client_next_seq = max(text_client_next_seq, seq)

	var line_meta = meta.duplicate(true) if typeof(meta) == TYPE_DICTIONARY else {}

	# DataPackage lookups can finish out of order. Insert each resolved PrintJSON
	# line back into its original receive position rather than appending an old
	# message as if it just happened. This keeps the HUD feed truly real-time.
	var insert_at = text_client_line_seqs.size()
	for i in range(text_client_line_seqs.size()):
		if seq < int(text_client_line_seqs[i]):
			insert_at = i
			break
	text_client_lines.insert(insert_at, line)
	text_client_rich_lines.insert(insert_at, rich_line)
	text_client_line_seqs.insert(insert_at, seq)
	text_client_line_meta.insert(insert_at, line_meta)

	while text_client_lines.size() > MAX_TEXT_CLIENT_LINES:
		text_client_lines.remove(0)
		text_client_rich_lines.remove(0)
		text_client_line_seqs.remove(0)
		text_client_line_meta.remove(0)
	emit_signal("text_client_changed")

func _print_json_filter_meta(data):
	var meta = {
		"has_item": false,
		"flags": 0,
		"sender": -1,
		"receiver": -1,
		"own_item": false,
	}
	if typeof(data) != TYPE_ARRAY:
		return meta

	var seen_players = []
	for part in data:
		if typeof(part) != TYPE_DICTIONARY:
			continue
		var part_type = str(part.get("type", "text"))
		if part_type == "player_id":
			var pid = int(part.get("text", -1))
			if pid >= 0:
				seen_players.append(pid)
		elif part_type == "item_id" or part_type == "item_name":
			meta["has_item"] = true
			meta["flags"] = int(meta["flags"]) | int(part.get("flags", 0))
			var item_player = int(part.get("player", -1))
			if item_player >= 0:
				meta["receiver"] = item_player
		elif part_type == "location_id" or part_type == "location_name":
			var location_player = int(part.get("player", -1))
			if location_player >= 0:
				meta["sender"] = location_player

	# Standard ItemSend PrintJSON normally exposes sender through the location's
	# player and receiver through the item's player. Fall back to the displayed
	# player IDs so custom/older AP servers are still handled sensibly.
	if int(meta["sender"]) < 0 and seen_players.size() > 0:
		meta["sender"] = int(seen_players[0])
	if int(meta["receiver"]) < 0:
		if seen_players.size() > 1:
			meta["receiver"] = int(seen_players[seen_players.size() - 1])
		elif seen_players.size() == 1 and bool(meta["has_item"]):
			meta["receiver"] = int(seen_players[0])

	meta["own_item"] = bool(meta["has_item"]) and (
		int(meta["sender"]) == int(slot_number)
		or int(meta["receiver"]) == int(slot_number)
	)
	return meta

func _text_client_meta_visible(meta):
	var mode = int(text_client_filter_mode)
	if mode == 0:
		return true
	if typeof(meta) != TYPE_DICTIONARY or not bool(meta.get("has_item", false)):
		return false
	var flags = int(meta.get("flags", 0))
	match mode:
		1:
			# Archipelago item flags: bit 0 = progression, bit 1 = useful.
			return bool(flags & 1) or bool(flags & 2)
		2:
			return bool(flags & 1)
		3:
			return bool(meta.get("own_item", false))
	return true

func _visible_text_client_indices(max_lines):
	var indices = []
	var count = max(1, int(max_lines))
	for i in range(text_client_lines.size() - 1, -1, -1):
		var meta = text_client_line_meta[i] if i < text_client_line_meta.size() else {}
		if not _text_client_meta_visible(meta):
			continue
		indices.push_front(i)
		if indices.size() >= count:
			break
	return indices

func get_text_client_latest_text(max_chars = 58):
	var indices = _visible_text_client_indices(1)
	if indices.size() == 0:
		return "AP CHAT: no matching messages"
	var line = str(text_client_lines[int(indices[0])])
	var limit = max(16, int(max_chars))
	if line.length() > limit:
		line = line.substr(0, limit - 3) + "..."
	return "AP: " + line

func get_text_client_feed_text(max_lines = 5, max_chars_per_line = 110):
	var indices = _visible_text_client_indices(max_lines)
	if indices.size() == 0:
		return "No matching Archipelago messages..."
	var out = []
	var limit = max(24, int(max_chars_per_line))
	for idx in indices:
		var line = str(text_client_lines[int(idx)])
		if line.length() > limit:
			line = line.substr(0, limit - 3) + "..."
		out.append(line)
	return _join_lines(out)

func get_text_client_feed_bbcode(max_lines = 4):
	var indices = _visible_text_client_indices(max_lines)
	if indices.size() == 0:
		return "[color=#FFFFFF]No matching Archipelago messages...[/color]"
	var out = []
	for idx in indices:
		out.append(str(text_client_rich_lines[int(idx)]))
	return _join_lines(out)

func get_shiny_coin_progress_text():
	if not shiny_coin_enabled:
		return "Shiny Coins: OFF"
	if shiny_coin_required < 0:
		return "Shiny Coins: " + str(shiny_coin_received) + " / ?"
	if shiny_coin_required == 0:
		return "Shiny Coins: " + str(shiny_coin_received) + " / 0"
	var suffix = "  GOAL SENT" if shiny_coin_goal_sent else "  (" + str(max(0, shiny_coin_required - shiny_coin_received)) + " left)"
	return "Shiny Coins: " + str(shiny_coin_received) + " / " + str(shiny_coin_required) + suffix

func _network_item_value(item, key, array_index):
	if typeof(item) == TYPE_DICTIONARY:
		return int(item.get(key, -1))
	if typeof(item) == TYPE_ARRAY and item.size() > array_index:
		return int(item[array_index])
	return -1

func _set_status(value):
	status = str(value)
	emit_signal("status_changed", status)
	emit_signal("debug_changed")

func _set_error(value):
	last_error = str(value)
	status = str(value)
	_log("ERROR: " + str(value))
	emit_signal("status_changed", status)
	emit_signal("ap_error", last_error)
	emit_signal("debug_changed")

func _log(value):
	var line = str(value)
	debug_lines.append(line)
	while debug_lines.size() > MAX_DEBUG_LINES:
		debug_lines.remove(0)
	var stamped = "[" + _timestamp() + "] " + line
	print("[AP] " + line)
	_append_debug_file(stamped)
	emit_signal("debug_changed")

func _append_debug_file(line):
	pending_debug_file_lines.append(str(line))

func _flush_debug_file_buffer():
	if pending_debug_file_lines.empty():
		return
	var lines = pending_debug_file_lines.duplicate()
	pending_debug_file_lines.clear()
	var file = File.new()
	var err = file.open(DEBUG_LOG_PATH, File.READ_WRITE)
	if err != OK:
		err = file.open(DEBUG_LOG_PATH, File.WRITE)
	if err == OK:
		file.seek_end()
		for line in lines:
			file.store_line(str(line))
		file.close()

func _timestamp():
	var d = OS.get_datetime()
	return "%04d-%02d-%02d %02d:%02d:%02d" % [d.year, d.month, d.day, d.hour, d.minute, d.second]

func _socket_state_name():
	if socket == null:
		return "NULL"
	match socket.get_connection_status():
		NetworkedMultiplayerPeer.CONNECTION_DISCONNECTED:
			return "DISCONNECTED"
		NetworkedMultiplayerPeer.CONNECTION_CONNECTING:
			return "CONNECTING"
		NetworkedMultiplayerPeer.CONNECTION_CONNECTED:
			return "CONNECTED"
	return "UNKNOWN(" + str(socket.get_connection_status()) + ")"

func _error_name(code):
	if int(code) == OK:
		return "OK"
	return "ErrorCode_" + str(code)

func _to_int_array(values):
	var out = []
	if typeof(values) == TYPE_ARRAY:
		for value in values:
			out.append(int(value))
	return out

func _parse_player_context(packet, reset_existing = true):
	if reset_existing:
		player_names = {0: "Archipelago"}
		player_games = {0: "Archipelago"}

	var players = packet.get("players", [])
	if typeof(players) == TYPE_ARRAY:
		for p in players:
			var player_slot = -1
			var alias = ""
			var real_name = ""
			if typeof(p) == TYPE_DICTIONARY:
				player_slot = int(p.get("slot", -1))
				alias = str(p.get("alias", ""))
				real_name = str(p.get("name", ""))
			elif typeof(p) == TYPE_ARRAY and p.size() >= 4:
				player_slot = int(p[1])
				alias = str(p[2])
				real_name = str(p[3])
			if player_slot >= 0:
				player_names[player_slot] = alias if alias != "" else real_name

	var info = packet.get("slot_info", {})
	if typeof(info) == TYPE_DICTIONARY:
		for slot_key in info.keys():
			var player_slot = int(slot_key)
			var slot_info = info[slot_key]
			if typeof(slot_info) == TYPE_DICTIONARY:
				var game_name = str(slot_info.get("game", ""))
				var display_name = str(slot_info.get("name", ""))
				if game_name != "":
					player_games[player_slot] = game_name
				if not player_names.has(player_slot) and display_name != "":
					player_names[player_slot] = display_name
			elif typeof(slot_info) == TYPE_ARRAY and slot_info.size() >= 2:
				var display_name = str(slot_info[0])
				var game_name = str(slot_info[1])
				if game_name != "":
					player_games[player_slot] = game_name
				if not player_names.has(player_slot) and display_name != "":
					player_names[player_slot] = display_name

	var own_slot = int(packet.get("slot", slot_number))
	if packet.has("team"):
		team_number = int(packet.get("team", -1))
	if own_slot >= 0:
		slot_number = own_slot
		if not player_names.has(own_slot):
			player_names[own_slot] = slot_name
		if not player_games.has(own_slot):
			player_games[own_slot] = GAME_NAME

func _request_game_data(game_name):
	var game = str(game_name)
	if game == "" or item_names_by_game.has(game) or requested_data_package_games.has(game):
		return
	requested_data_package_games.append(game)
	_log("TEXT CLIENT requesting DataPackage game=" + game)
	_send_packets([{"cmd": "GetDataPackage", "games": [game]}])

func _consume_data_package(data):
	if typeof(data) != TYPE_DICTIONARY:
		return
	var games = data.get("games", {})
	if typeof(games) == TYPE_DICTIONARY:
		for game_key in games.keys():
			var game_name = str(game_key)
			var game_data = games[game_key]
			if typeof(game_data) != TYPE_DICTIONARY:
				continue
			var item_lookup = {}
			var item_name_to_id = game_data.get("item_name_to_id", {})
			if typeof(item_name_to_id) == TYPE_DICTIONARY:
				for item_name in item_name_to_id.keys():
					item_lookup[int(item_name_to_id[item_name])] = str(item_name)
			var location_lookup = {}
			var location_name_to_id = game_data.get("location_name_to_id", {})
			if typeof(location_name_to_id) == TYPE_DICTIONARY:
				for location_name in location_name_to_id.keys():
					location_lookup[int(location_name_to_id[location_name])] = str(location_name)
			item_names_by_game[game_name] = item_lookup
			location_names_by_game[game_name] = location_lookup
			requested_data_package_games.erase(game_name)
			_log("TEXT CLIENT DataPackage loaded game=" + game_name + " items=" + str(item_lookup.size()) + " locations=" + str(location_lookup.size()))

func _local_item_name(item_id):
	for item_name in APData.ITEM_NAME_TO_ID.keys():
		if int(APData.ITEM_NAME_TO_ID[item_name]) == int(item_id):
			return str(item_name)
	return ""

func _local_location_name(location_id):
	for location_name in APData.LOCATION_NAME_TO_ID.keys():
		if int(APData.LOCATION_NAME_TO_ID[location_name]) == int(location_id):
			return str(location_name)
	return ""

func _resolve_player_name(player_id):
	var pid = int(player_id)
	if player_names.has(pid):
		return str(player_names[pid])
	return str(pid)

func _resolve_item_name(item_id, player_id):
	var iid = int(item_id)
	var pid = int(player_id)
	var game = str(player_games.get(pid, GAME_NAME if pid == slot_number else ""))
	if game != "" and item_names_by_game.has(game):
		var lookup = item_names_by_game[game]
		if lookup.has(iid):
			return [str(lookup[iid]), true]
	if game != "":
		_request_game_data(game)
		# The bundled APData is only a temporary fallback; old APWorld rooms may
		# use different IDs, so wait for the server's exact DataPackage before
		# putting the line into the visible feed.
		var fallback = _local_item_name(iid) if game == GAME_NAME else str(iid)
		return [fallback if fallback != "" else str(iid), false]
	return [str(iid), true]

func _resolve_location_name(location_id, player_id):
	var lid = int(location_id)
	var pid = int(player_id)
	var game = str(player_games.get(pid, ""))
	if game != "" and location_names_by_game.has(game):
		var lookup = location_names_by_game[game]
		if lookup.has(lid):
			return [str(lookup[lid]), true]
	if game != "":
		_request_game_data(game)
		var fallback = _local_location_name(lid) if game == GAME_NAME else str(lid)
		return [fallback if fallback != "" else str(lid), false]
	return [str(lid), true]

func _ap_color_hex(color_name):
	match str(color_name).to_lower():
		"black": return "000000"
		"red": return "EE0000"
		"green": return "00FF7F"
		"yellow": return "FAFAD2"
		"blue": return "6495ED"
		"magenta": return "EE00EE"
		"cyan": return "00EEEE"
		"slateblue": return "6D8BE8"
		"plum": return "AF99EF"
		"salmon": return "FA8072"
		"white": return "FFFFFF"
		"orange": return "FF7700"
		_: return "FFFFFF"

func _item_color_name(flags):
	var item_flags = int(flags)
	if item_flags == 0:
		return "cyan"
	if item_flags & 1:
		return "plum"
	if item_flags & 2:
		return "slateblue"
	if item_flags & 4:
		return "salmon"
	return "cyan"

func _message_part_bbcode(part, display_text, part_type):
	var escaped = _bbcode_escape(display_text)
	var color_name = str(part.get("color", ""))
	var make_bold = false

	match part_type:
		"player_id":
			var player_id = int(part.get("text", -1))
			if player_id == slot_number:
				# The player whose client this is gets a bright purple highlight.
				# Bold + bright magenta gives a readable glow-like look in the PICO font.
				color_name = "magenta"
				make_bold = true
			else:
				color_name = "yellow"
		"player_name":
			color_name = "yellow"
		"item_id", "item_name":
			color_name = _item_color_name(part.get("flags", 0))
		"location_id", "location_name":
			# Archipelago TextClient renders checks/locations green.
			color_name = "green"
		"entrance_name":
			color_name = "blue"
		"hint_status":
			if color_name == "":
				color_name = "white"
		"color":
			pass
		_:
			pass

	if color_name == "":
		return escaped
	var code = _ap_color_hex(color_name)
	if make_bold:
		return "[color=#" + code + "][b]" + escaped + "[/b][/color]"
	return "[color=#" + code + "]" + escaped + "[/color]"

func _format_print_json(data):
	var plain_parts = []
	var rich_parts = []
	var fully_resolved = true
	if typeof(data) == TYPE_ARRAY:
		for part in data:
			if typeof(part) != TYPE_DICTIONARY:
				var raw = str(part)
				plain_parts.append(raw)
				rich_parts.append(_bbcode_escape(raw))
				continue
			var raw_text = str(part.get("text", ""))
			var part_type = str(part.get("type", "text"))
			var display_text = raw_text
			match part_type:
				"player_id":
					display_text = _resolve_player_name(int(raw_text))
				"item_id":
					var resolved_item = _resolve_item_name(int(raw_text), int(part.get("player", -1)))
					display_text = str(resolved_item[0])
					fully_resolved = fully_resolved and bool(resolved_item[1])
				"location_id":
					var resolved_location = _resolve_location_name(int(raw_text), int(part.get("player", -1)))
					display_text = str(resolved_location[0])
					fully_resolved = fully_resolved and bool(resolved_location[1])
				_:
					pass
			plain_parts.append(display_text)
			rich_parts.append(_message_part_bbcode(part, display_text, part_type))
	return [_join_values(plain_parts, ""), _join_values(rich_parts, ""), fully_resolved]

func _handle_print_json(data):
	var message_seq = _next_text_client_seq()
	var filter_meta = _print_json_filter_meta(data)
	var formatted = _format_print_json(data)
	var text = str(formatted[0]).strip_edges()
	var rich_text = str(formatted[1]).strip_edges()
	if bool(formatted[2]):
		if text != "":
			_log(text)
			_append_text_client_message(text, rich_text, message_seq, filter_meta)
		return
	# Hold item/location messages briefly until the per-game DataPackage arrives,
	# so the feed shows names rather than raw numeric IDs. Keep the original
	# receive sequence so a delayed lookup can never jump ahead of newer messages.
	if typeof(data) == TYPE_ARRAY:
		pending_print_json.append({"data": data.duplicate(true), "seq": message_seq, "meta": filter_meta})
		while pending_print_json.size() > MAX_PENDING_PRINT_JSON:
			pending_print_json.remove(0)

func _flush_pending_print_json():
	if pending_print_json.size() == 0:
		return
	var remaining = []
	for pending in pending_print_json:
		var data = pending
		var message_seq = -1
		var filter_meta = {}
		if typeof(pending) == TYPE_DICTIONARY and pending.has("data"):
			data = pending.get("data", [])
			message_seq = int(pending.get("seq", -1))
			filter_meta = pending.get("meta", _print_json_filter_meta(data))
		else:
			filter_meta = _print_json_filter_meta(data)
		var formatted = _format_print_json(data)
		if bool(formatted[2]):
			var text = str(formatted[0]).strip_edges()
			var rich_text = str(formatted[1]).strip_edges()
			if text != "":
				_log(text)
				_append_text_client_message(text, rich_text, message_seq, filter_meta)
		else:
			remaining.append(pending)
	pending_print_json = remaining

func _join_values(values, separator):
	var out = ""
	for i in range(values.size()):
		if i > 0:
			out += separator
		out += str(values[i])
	return out

func _join_lines(values):
	return _join_values(values, "\n")

func _load_or_make_uuid():
	var path = "user://LBAL-AP-Client-ID.txt"
	var file = File.new()
	if file.file_exists(path):
		if file.open(path, File.READ) == OK:
			var saved = file.get_as_text().strip_edges()
			file.close()
			if saved != "":
				return saved

	randomize()
	var made = str(OS.get_unix_time()) + "-" + str(randi()) + "-" + str(randi())
	if file.open(path, File.WRITE) == OK:
		file.store_string(made)
		file.close()
	return made
