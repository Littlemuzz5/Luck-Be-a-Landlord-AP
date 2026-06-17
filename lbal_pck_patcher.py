from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import struct
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

PATCH_MARKER = "AP_LIVE_POOL_PATCH_V165"
OLD_PATCH_MARKERS = ["AP_LIVE_POOL_PATCH_V158", "AP_LIVE_POOL_PATCH_V155", "AP_LIVE_POOL_PATCH_V1", "AP_LIVE_POOL_PATCH_V2", "AP_LIVE_POOL_PATCH_V3", "AP_LIVE_POOL_PATCH_V4", "AP_LIVE_POOL_PATCH_V5", "AP_LIVE_POOL_PATCH_V6", "AP_LIVE_POOL_PATCH_V7", "AP_LIVE_POOL_PATCH_V8", "AP_LIVE_POOL_PATCH_V9", "AP_LIVE_POOL_PATCH_V10", "AP_LIVE_POOL_PATCH_V11", "AP_LIVE_POOL_PATCH_V12", "AP_LIVE_POOL_PATCH_V13", "AP_LIVE_POOL_PATCH_V14", "AP_LIVE_POOL_PATCH_V15", "AP_LIVE_POOL_PATCH_V16", "AP_LIVE_POOL_PATCH_V17", "AP_LIVE_POOL_PATCH_V18", "AP_LIVE_POOL_PATCH_V19", "AP_LIVE_POOL_PATCH_V20", "AP_LIVE_POOL_PATCH_V21", "AP_LIVE_POOL_PATCH_V22", "AP_LIVE_POOL_PATCH_V23", "AP_LIVE_POOL_PATCH_V24", "AP_LIVE_POOL_PATCH_V25", "AP_LIVE_POOL_PATCH_V26", "AP_LIVE_POOL_PATCH_V27", "AP_LIVE_POOL_PATCH_V28", "AP_LIVE_POOL_PATCH_V70", "AP_LIVE_POOL_PATCH_V71", "AP_LIVE_POOL_PATCH_V72", "AP_LIVE_POOL_PATCH_V75", "AP_LIVE_POOL_PATCH_V76", "AP_LIVE_POOL_PATCH_V77", "AP_LIVE_POOL_PATCH_V78", "AP_LIVE_POOL_PATCH_V79", "AP_LIVE_POOL_PATCH_V80", "AP_LIVE_POOL_PATCH_V81", "AP_LIVE_POOL_PATCH_V82", "AP_LIVE_POOL_PATCH_V83", "AP_LIVE_POOL_PATCH_V84", "AP_LIVE_POOL_PATCH_V85", "AP_LIVE_POOL_PATCH_V86", "AP_LIVE_POOL_PATCH_V87", "AP_LIVE_POOL_PATCH_V88", "AP_LIVE_POOL_PATCH_V89", "AP_LIVE_POOL_PATCH_V90", "AP_LIVE_POOL_PATCH_V91", "AP_LIVE_POOL_PATCH_V92", "AP_LIVE_POOL_PATCH_V93", "AP_LIVE_POOL_PATCH_V94", "AP_LIVE_POOL_PATCH_V95", "AP_LIVE_POOL_PATCH_V96", "AP_LIVE_POOL_PATCH_V97", "AP_LIVE_POOL_PATCH_V98", "AP_LIVE_POOL_PATCH_V99", "AP_LIVE_POOL_PATCH_V100", "AP_LIVE_POOL_PATCH_V101", "AP_LIVE_POOL_PATCH_V102", "AP_LIVE_POOL_PATCH_V103", "AP_LIVE_POOL_PATCH_V104", "AP_LIVE_POOL_PATCH_V105", "AP_LIVE_POOL_PATCH_V106", "AP_LIVE_POOL_PATCH_V107", "AP_LIVE_POOL_PATCH_V108", "AP_LIVE_POOL_PATCH_V109", "AP_LIVE_POOL_PATCH_V110", "AP_LIVE_POOL_PATCH_V111", "AP_LIVE_POOL_PATCH_V112", "AP_LIVE_POOL_PATCH_V113", "AP_LIVE_POOL_PATCH_V114", "AP_LIVE_POOL_PATCH_V115", "AP_LIVE_POOL_PATCH_V116", "AP_LIVE_POOL_PATCH_V117", "AP_LIVE_POOL_PATCH_V118", "AP_LIVE_POOL_PATCH_V119", "AP_LIVE_POOL_PATCH_V120", "AP_LIVE_POOL_PATCH_V121", "AP_LIVE_POOL_PATCH_V122", "AP_LIVE_POOL_PATCH_V123", "AP_LIVE_POOL_PATCH_V124", "AP_LIVE_POOL_PATCH_V125", "AP_LIVE_POOL_PATCH_V126", "AP_LIVE_POOL_PATCH_V127", "AP_LIVE_POOL_PATCH_V128", "AP_LIVE_POOL_PATCH_V129", "AP_LIVE_POOL_PATCH_V130", "AP_LIVE_POOL_PATCH_V131", "AP_LIVE_POOL_PATCH_V132", "AP_LIVE_POOL_PATCH_V133", "AP_LIVE_POOL_PATCH_V134", "AP_LIVE_POOL_PATCH_V135", "AP_LIVE_POOL_PATCH_V136", "AP_LIVE_POOL_PATCH_V137", "AP_LIVE_POOL_PATCH_V138", "AP_LIVE_POOL_PATCH_V139", "AP_LIVE_POOL_PATCH_V140", "AP_LIVE_POOL_PATCH_V141", "AP_LIVE_POOL_PATCH_V142", "AP_LIVE_POOL_PATCH_V143", "AP_LIVE_POOL_PATCH_V144", "AP_LIVE_POOL_PATCH_V145", "AP_LIVE_POOL_PATCH_V146", "AP_LIVE_POOL_PATCH_V147", "AP_LIVE_POOL_PATCH_V148", "AP_LIVE_POOL_PATCH_V149", "AP_LIVE_POOL_PATCH_V150", "AP_LIVE_POOL_PATCH_V151", "AP_LIVE_POOL_PATCH_V152", "AP_LIVE_POOL_PATCH_V153", "AP_LIVE_POOL_PATCH_V154", "AP_LIVE_POOL_PATCH_V156", "AP_LIVE_POOL_PATCH_V157", "AP_LIVE_POOL_PATCH_V159", "AP_LIVE_POOL_PATCH_V160", "AP_LIVE_POOL_PATCH_V161", "AP_LIVE_POOL_PATCH_V162", "AP_LIVE_POOL_PATCH_V163", "AP_LIVE_POOL_PATCH_V164"]
AP_CHECK_MARKER = "AP_CHECK_SYMBOL_PATCH_V2"
OLD_AP_CHECK_MARKERS = ["AP_CHECK_SYMBOL_PATCH_V1"]
AP_CHECK_SEND_MARKER = "AP_CHECK_SEND_PATCH_V165"
DEATHLINK_PATCH_MARKER = "AP_DEATHLINK_PATCH_V12"
DEATHLINK_HOOK_MARKER = "AP_DEATHLINK_HOOK_PATCH_V12"
MAIN_DEATHLINK_PATCH_MARKER = "AP_DEATHLINK_MAIN_PATCH_V74"

EMPTY_ITEM_POOL_MARKER_V65 = "AP_EMPTY_ITEM_POOL_FIX_V65"
OVERFLOW_GUARD_MARKER_V64 = "AP_WORKSHOP_ID_OVERFLOW_GUARD_V64"
POPUP_SAFE_NODE_MARKER_V64 = "AP_POPUP_SAFE_NODE_PATCH_V64"
PCK_NAME = "Luck be a Landlord.pck"
BACKUP_FOLDER_NAME = "LBAL.Pck"
BACKUP_FILE_NAME = "Luck be a Landlord.original.pck"
PATCHED_COPY_NAME = "Luck be a Landlord.ap-live-patched.pck"

# V41: embedded user red-X missing textures.
# 12x12 replaces res://.import/missing.png-*.stex, which is used by inline <icon_?> descriptions.
# 22x22 replaces res://.import/item_missing.png-*.stex, which is used by missing item/card art.
AP_MISSING_STEX_12_B64 = 'R0RTVAwAAAAMAAAAAAAAAAAAIAcBAAAAbAAAAFdFQlBSSUZGYAAAAFdFQlBWUDhMUwAAAC8LwAIQdTCIJCnO+UMDhkAhInBBPgc3k49MwGIRdHRKpIVoIhAJQLjhhTMWGCK5ZVv/JyAvDaCujMoyGgAXQwOYzgJQ4Jj1BWi2C+z5L4tM1bwUAA=='
AP_MISSING_STEX_22_B64 = 'R0RTVBYAAAAWAAAAAAAAAAAAIAcBAAAAegAAAFdFQlBSSUZGbgAAAFdFQlBWUDhMYQAAAC8VQAUQCgaRJDVaf2jAEChEBCo+BwEzhdpIUhsadO1diYCU+gRNJKlB0tqgQwEVsiGx0v8J4O8jcfgCDbT8ATTAMyM7OJxR67Fgq8r2T7TqBodt/uVzgfaVgAY8BnjI3wMA'



@dataclass
class PckEntry:
    path: str
    raw_path: bytes
    offset: int
    size: int
    md5: bytes


def _align16(value: int) -> int:
    return (value + 15) & ~15


def _decode_path(raw_path: bytes) -> str:
    return raw_path.decode("utf-8", errors="replace").rstrip("\x00")


def _parse_pck(data: bytes) -> Tuple[bytes, List[PckEntry]]:
    if len(data) < 88 or data[:4] != b"GDPC":
        raise ValueError("Not a Godot PCK file: missing GDPC header")

    pos = 4 + 16 + 64
    count = struct.unpack_from("<I", data, pos)[0]
    header = data[:pos]
    pos += 4

    entries: List[PckEntry] = []
    for _ in range(count):
        path_len = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        raw_path = data[pos:pos + path_len]
        pos += path_len
        offset, size = struct.unpack_from("<QQ", data, pos)
        pos += 16
        md5 = data[pos:pos + 16]
        pos += 16
        entries.append(PckEntry(_decode_path(raw_path), raw_path, offset, size, md5))

    return header, entries


def _extract_entry(data: bytes, entries: Iterable[PckEntry], wanted_path: str) -> bytes:
    for entry in entries:
        if entry.path == wanted_path:
            return data[entry.offset:entry.offset + entry.size]
    raise KeyError(f"{wanted_path} not found in PCK")


def _replace_entry_and_repack(data: bytes, replacements: Dict[str, bytes]) -> bytes:
    header, entries = _parse_pck(data)

    table_size = len(header) + 4
    for entry in entries:
        table_size += 4 + len(entry.raw_path) + 8 + 8 + 16

    offset = _align16(table_size)
    blobs: List[Tuple[PckEntry, bytes, int]] = []
    for entry in entries:
        blob = replacements.get(entry.path)
        if blob is None:
            blob = data[entry.offset:entry.offset + entry.size]
        blobs.append((entry, blob, offset))
        offset = _align16(offset + len(blob))

    out = bytearray()
    out += header
    out += struct.pack("<I", len(entries))
    for entry, blob, blob_offset in blobs:
        out += struct.pack("<I", len(entry.raw_path))
        out += entry.raw_path
        out += struct.pack("<QQ", blob_offset, len(blob))
        out += hashlib.md5(blob).digest()

    if len(out) > blobs[0][2]:
        raise ValueError("Internal patcher error: rebuilt PCK table overlaps file data")
    out += b"\x00" * (blobs[0][2] - len(out))

    for _entry, blob, blob_offset in blobs:
        if len(out) < blob_offset:
            out += b"\x00" * (blob_offset - len(out))
        out += blob
        aligned = _align16(len(out))
        if aligned > len(out):
            out += b"\x00" * (aligned - len(out))

    return bytes(out)


def _escaped_gd(code: str) -> str:
    # Pop-up.tscn embeds GDScript inside a quoted TSCN string. Newlines are real
    # newlines in the file, but inner quotes/backslashes need escaping.
    return code.replace("\\", "\\\\").replace('"', '\\"')


QUEUE_GAME_CHECKS_GDSCRIPT_V161 = r'''
func _ap_lbal_queue_game_checks(location_names):
	# V161: merge with any existing bridge file instead of overwriting it.
	# This lets multiple AP Check symbols destroy in one spin and still send
	# AP Check 32, 33, 34... instead of only the last file write surviving.
	var clean = []
	var ap_next_count = 0
	if typeof(location_names) == TYPE_ARRAY:
		for location_name in location_names:
			var s = str(location_name)
			if s.to_lower() in ["ap_check_next", "next_ap_check", "ap check next", "ap check", "ap_check"]:
				ap_next_count += 1
			else:
				if not clean.has(s):
					clean.push_back(s)
	else:
		var single = str(location_names)
		if single.to_lower() in ["ap_check_next", "next_ap_check", "ap check next", "ap check", "ap_check"]:
			ap_next_count += 1
		else:
			clean.push_back(single)

	var paths = ["user://checks_to_send.json", _ap_lbal_bridge_file_path("checks_to_send.json")]
	var file = File.new()
	for path in paths:
		if not file.file_exists(path):
			continue
		var err = file.open(path, File.READ)
		if err != OK:
			continue
		var old_text = file.get_as_text()
		file.close()
		var old_data = parse_json(old_text)
		if typeof(old_data) == TYPE_DICTIONARY:
			if old_data.has("locations") and typeof(old_data["locations"]) == TYPE_ARRAY:
				for old_location in old_data["locations"]:
					var old_s = str(old_location)
					if old_s.to_lower() in ["ap_check_next", "next_ap_check", "ap check next", "ap check", "ap_check"]:
						ap_next_count += 1
					elif not clean.has(old_s):
						clean.push_back(old_s)
			if old_data.has("ap_check_next_count"):
				ap_next_count += int(old_data.get("ap_check_next_count", 0))
		elif typeof(old_data) == TYPE_ARRAY:
			for old_location2 in old_data:
				var old_s2 = str(old_location2)
				if old_s2.to_lower() in ["ap_check_next", "next_ap_check", "ap check next", "ap check", "ap_check"]:
					ap_next_count += 1
				elif not clean.has(old_s2):
					clean.push_back(old_s2)

	var nonce = str(OS.get_unix_time()) + "_" + str(randi())
	var payload = JSON.print({"locations": clean, "ap_check_next_count": ap_next_count, "source": "lbal_game", "nonce": nonce})
	_ap_lbal_write_file_text("user://checks_to_send.json", payload)
	_ap_lbal_write_file_text(_ap_lbal_bridge_file_path("checks_to_send.json"), payload)

'''

LIVE_GDSCRIPT = r'''
# AP_LIVE_POOL_PATCH_V165
var ap_live_enabled = true
var ap_live_loaded = false
var ap_live_last_text = ""
var ap_live_lock_symbols = true
var ap_live_lock_normal_items = true
var ap_live_lock_essences = true
var ap_live_symbol_boost_pool_empty = false
var ap_live_item_boost_pool_empty = false
var ap_live_essence_boost_pool_empty = false
var ap_live_boost_pool_mode_v136 = false
var ap_live_has_ap_checks = false
var ap_live_ap_check_symbol_pool_active = false
var ap_allowed_symbols = {}
var ap_allowed_items = {}
var ap_allowed_essences = {}
var ap_priority_symbols = {}
var ap_priority_items = {}
var ap_priority_essences = {}
var ap_live_has_symbol_targets_v92 = false
var ap_live_has_item_targets_v92 = false
var ap_live_has_essence_targets_v92 = false
var ap_live_symbol_received_fallback_v108 = false
var ap_goal_floors = []
var ap_one_per_run_items = {}
var ap_default_starting_symbol_types = ["coin", "flower", "pearl", "cherry", "cat"]
var ap_deathlink_enabled = false
var ap_deathlink_last_nonce = ""
var ap_live_next_poll_msec = 0
var ap_live_poll_interval_msec = 350
var ap_deathlink_next_poll_msec = 0
var ap_deathlink_poll_interval_msec = 250

func _ap_lbal_add_values_to_set(values, target):
	if typeof(values) == TYPE_ARRAY:
		for value in values:
			target[str(value)] = true
	elif typeof(values) == TYPE_DICTIONARY:
		for key in values.keys():
			if values[key] == true or values[key] == 1 or typeof(values[key]) == TYPE_DICTIONARY:
				target[str(key)] = true

func _ap_lbal_possible_state_paths():
	var paths = ["user://ap_state.json"]
	if OS.has_environment("LOCALAPPDATA"):
		paths.push_back(OS.get_environment("LOCALAPPDATA").replace("\\", "/") + "/LuckBeALandlordAP/ap_state.json")
	return paths

func _ap_lbal_update_state(force = false):
	if not ap_live_enabled:
		return false
	if not force and ap_live_loaded:
		var now = OS.get_ticks_msec()
		if now < ap_live_next_poll_msec:
			return false
		ap_live_next_poll_msec = now + ap_live_poll_interval_msec
	var file = File.new()
	var text = null
	for path in _ap_lbal_possible_state_paths():
		if file.file_exists(path):
			var err = file.open(path, File.READ)
			if err == OK:
				text = file.get_as_text()
				file.close()
				break
	if text == null:
		return false
	if text == ap_live_last_text:
		return false
	ap_live_last_text = text
	var data = parse_json(text)
	if typeof(data) != TYPE_DICTIONARY:
		return false
	ap_allowed_symbols.clear()
	ap_allowed_items.clear()
	ap_allowed_essences.clear()
	ap_one_per_run_items.clear()
	ap_goal_floors = []
	ap_live_has_symbol_targets_v92 = false
	ap_live_has_item_targets_v92 = false
	ap_live_has_essence_targets_v92 = false
	ap_live_symbol_received_fallback_v108 = false
	_ap_lbal_add_values_to_set(ap_default_starting_symbol_types, ap_allowed_symbols)
	ap_live_lock_symbols = true
	ap_live_lock_normal_items = true
	ap_live_lock_essences = true
	ap_live_symbol_boost_pool_empty = false
	ap_live_item_boost_pool_empty = false
	ap_live_essence_boost_pool_empty = false
	ap_live_boost_pool_mode_v136 = false
	ap_deathlink_enabled = false
	if data.has("deathlink") and typeof(data["deathlink"]) == TYPE_DICTIONARY:
		ap_deathlink_enabled = bool(data["deathlink"].get("enabled", false))
	elif data.has("deathlink_enabled"):
		ap_deathlink_enabled = bool(data["deathlink_enabled"])
	if data.has("mod_control") and typeof(data["mod_control"]) == TYPE_DICTIONARY:
		if data["mod_control"].has("enabled"):
			ap_live_enabled = bool(data["mod_control"]["enabled"])
		if data["mod_control"].has("lock_symbols"):
			ap_live_lock_symbols = bool(data["mod_control"]["lock_symbols"])
		if data["mod_control"].has("lock_normal_items"):
			ap_live_lock_normal_items = bool(data["mod_control"]["lock_normal_items"])
		if data["mod_control"].has("lock_essences"):
			ap_live_lock_essences = bool(data["mod_control"]["lock_essences"])
		if data["mod_control"].has("symbol_boost_pool_empty"):
			ap_live_symbol_boost_pool_empty = bool(data["mod_control"]["symbol_boost_pool_empty"])
		if data["mod_control"].has("item_boost_pool_empty"):
			ap_live_item_boost_pool_empty = bool(data["mod_control"]["item_boost_pool_empty"])
		if data["mod_control"].has("essence_boost_pool_empty"):
			ap_live_essence_boost_pool_empty = bool(data["mod_control"]["essence_boost_pool_empty"])
		if data["mod_control"].has("boost_pool_mode"):
			ap_live_boost_pool_mode_v136 = bool(data["mod_control"]["boost_pool_mode"])
		if data["mod_control"].has("has_ap_checks"):
			ap_live_has_ap_checks = bool(data["mod_control"]["has_ap_checks"])
		if data["mod_control"].has("ap_check_symbol_pool_active"):
			ap_live_ap_check_symbol_pool_active = bool(data["mod_control"]["ap_check_symbol_pool_active"])
		elif data["mod_control"].has("ap_check_priority"):
			ap_live_ap_check_symbol_pool_active = bool(data["mod_control"]["ap_check_priority"])
		if data["mod_control"].has("ap_check_symbol_pool_active"):
			ap_live_ap_check_symbol_pool_active = bool(data["mod_control"]["ap_check_symbol_pool_active"])
		elif data["mod_control"].has("ap_check_priority"):
			ap_live_ap_check_symbol_pool_active = bool(data["mod_control"]["ap_check_priority"])
	if data.has("live_pool") and typeof(data["live_pool"]) == TYPE_DICTIONARY:
		var live_pool = data["live_pool"]
		if live_pool.has("goal_floors") and typeof(live_pool["goal_floors"]) == TYPE_ARRAY:
			ap_goal_floors = live_pool["goal_floors"].duplicate(true)
		elif data.has("goal_floors") and typeof(data["goal_floors"]) == TYPE_ARRAY:
			ap_goal_floors = data["goal_floors"].duplicate(true)
		_ap_lbal_add_values_to_set(live_pool.get("symbol_types", []), ap_allowed_symbols)
		_ap_lbal_add_values_to_set(live_pool.get("starting_symbol_types", []), ap_allowed_symbols)
		_ap_lbal_add_values_to_set(live_pool.get("always_allowed_symbol_types", []), ap_allowed_symbols)
		_ap_lbal_add_values_to_set(live_pool.get("priority_symbol_types", []), ap_priority_symbols)
		if live_pool.has("has_symbol_targets"):
			ap_live_has_symbol_targets_v92 = bool(live_pool["has_symbol_targets"])
		else:
			ap_live_has_symbol_targets_v92 = live_pool.get("priority_symbol_types", []).size() > 0
		if live_pool.has("symbol_targets_are_received_fallback_v108"):
			ap_live_symbol_received_fallback_v108 = bool(live_pool["symbol_targets_are_received_fallback_v108"])
		elif live_pool.has("symbol_targets_are_received_fallback_v106"):
			ap_live_symbol_received_fallback_v108 = bool(live_pool["symbol_targets_are_received_fallback_v106"])
		if live_pool.has("has_item_targets"):
			ap_live_has_item_targets_v92 = bool(live_pool["has_item_targets"])
		else:
			ap_live_has_item_targets_v92 = live_pool.get("priority_item_types", []).size() > 0
		if live_pool.has("has_essence_targets"):
			ap_live_has_essence_targets_v92 = bool(live_pool["has_essence_targets"])
		else:
			ap_live_has_essence_targets_v92 = live_pool.get("priority_essence_types", []).size() > 0
		_ap_lbal_add_values_to_set(live_pool.get("item_types", []), ap_allowed_items)
		_ap_lbal_add_values_to_set(live_pool.get("always_allowed_item_types", []), ap_allowed_items)
		_ap_lbal_add_values_to_set(live_pool.get("priority_item_types", []), ap_priority_items)
		_ap_lbal_add_values_to_set(live_pool.get("one_per_run_item_types", []), ap_one_per_run_items)
		_ap_lbal_add_values_to_set(live_pool.get("essence_types", []), ap_allowed_essences)
		_ap_lbal_add_values_to_set(live_pool.get("priority_essence_types", []), ap_priority_essences)
		if live_pool.has("lock_symbols"):
			ap_live_lock_symbols = bool(live_pool["lock_symbols"])
		if live_pool.has("lock_normal_items"):
			ap_live_lock_normal_items = bool(live_pool["lock_normal_items"])
		if live_pool.has("lock_essences"):
			ap_live_lock_essences = bool(live_pool["lock_essences"])
		if live_pool.has("symbol_boost_pool_empty"):
			ap_live_symbol_boost_pool_empty = bool(live_pool["symbol_boost_pool_empty"])
		if live_pool.has("item_boost_pool_empty"):
			ap_live_item_boost_pool_empty = bool(live_pool["item_boost_pool_empty"])
		if live_pool.has("essence_boost_pool_empty"):
			ap_live_essence_boost_pool_empty = bool(live_pool["essence_boost_pool_empty"])
		if live_pool.has("boost_pool_mode"):
			ap_live_boost_pool_mode_v136 = bool(live_pool["boost_pool_mode"])
		if live_pool.has("has_ap_checks"):
			ap_live_has_ap_checks = bool(live_pool["has_ap_checks"])
		if live_pool.has("ap_check_symbol_pool_active"):
			ap_live_ap_check_symbol_pool_active = bool(live_pool["ap_check_symbol_pool_active"])
		elif live_pool.has("ap_check_priority"):
			ap_live_ap_check_symbol_pool_active = bool(live_pool["ap_check_priority"])
		if live_pool.has("ap_check_symbol_pool_active"):
			ap_live_ap_check_symbol_pool_active = bool(live_pool["ap_check_symbol_pool_active"])
		elif live_pool.has("ap_check_priority"):
			ap_live_ap_check_symbol_pool_active = bool(live_pool["ap_check_priority"])
	else:
		_ap_lbal_add_values_to_set(data.get("symbols_to_give", []), ap_allowed_symbols)
		_ap_lbal_add_values_to_set(data.get("normal_items_to_give", []), ap_allowed_items)
		_ap_lbal_add_values_to_set(data.get("essences_to_give", []), ap_allowed_essences)
	var live_pool_has_explicit_ap_check_state = data.has("live_pool") and typeof(data["live_pool"]) == TYPE_DICTIONARY and data["live_pool"].has("has_ap_checks")
	if data.has("next_ap_check") and data["next_ap_check"] != null and str(data["next_ap_check"]) != "":
		# V82: only old state files use next_ap_check to turn AP Check on. If the
		# live_pool explicitly says has_ap_checks=false, trust that and keep AP Check out.
		if not live_pool_has_explicit_ap_check_state:
			ap_live_has_ap_checks = true
			if not (data.has("live_pool") and typeof(data["live_pool"]) == TYPE_DICTIONARY and (data["live_pool"].has("ap_check_symbol_pool_active") or data["live_pool"].has("ap_check_priority"))):
				ap_live_ap_check_symbol_pool_active = true
	# V80/V82: when AP Check locations remain, always whitelist regular AP Check.
	if ap_live_has_ap_checks and ap_live_ap_check_symbol_pool_active:
		ap_allowed_symbols["ap_check"] = true
		_ap_lbal_ensure_ap_check_database_entry_v80()
	ap_live_loaded = true
	_ap_lbal_restore_original_descriptions_v59()
	# AP live pool updated; print disabled to avoid log spam
	return true

func _ap_lbal_ends_with(text, suffix):
	text = str(text)
	if text.length() < suffix.length():
		return false
	return text.substr(text.length() - suffix.length(), suffix.length()) == suffix

func _ap_lbal_canonical_item_type_v81(item_type):
	var t = str(item_type)
	match t:
		"piggybank", "piggy_bank_item", "item_piggy_bank":
			return "piggy_bank"
		"katana", "cursed_sword", "item_cursed_katana":
			return "cursed_katana"
		"soap", "soap_bar", "item_bar_of_soap":
			return "bar_of_soap"
		"capsule_removal", "remove_capsule", "capsule_remove":
			return "removal_capsule"
		"capsule_lucky":
			return "lucky_capsule"
	return t

func _ap_lbal_canonical_essence_type_v81(item_type):
	var t = str(item_type)
	match t:
		"essence_cursed_katana", "katana_essence", "cursed_sword_essence", "essence_katana":
			return "cursed_katana_essence"
		"essence_piggy_bank", "piggybank_essence", "piggy_bank_item_essence":
			return "piggy_bank_essence"
		"essence_guillotine":
			return "guillotine_essence"
		"nori_essence", "essence_nori_the_rabbit", "essence_nori":
			return "nori_the_rabbit_essence"
		"oswald_essence", "essence_oswald_the_monkey", "essence_oswald":
			return "oswald_the_monkey_essence"
	return t

func _ap_lbal_alias_candidates_for_kind_v83(kind, type_id):
	var raw = str(type_id)
	var out = [raw]
	if kind == "items":
		var c = _ap_lbal_canonical_item_type_v81(raw)
		if not out.has(c):
			out.push_back(c)
		match c:
			"piggy_bank":
				for v in ["piggybank", "piggy_bank_item", "item_piggy_bank"]:
					if not out.has(v):
						out.push_back(v)
			"cursed_katana":
				for v in ["katana", "cursed_sword", "item_cursed_katana"]:
					if not out.has(v):
						out.push_back(v)
			"bar_of_soap":
				for v in ["soap", "soap_bar", "item_bar_of_soap"]:
					if not out.has(v):
						out.push_back(v)
			"removal_capsule":
				for v in ["capsule_removal", "remove_capsule", "capsule_remove"]:
					if not out.has(v):
						out.push_back(v)
			"lucky_capsule":
				for v in ["capsule_lucky"]:
					if not out.has(v):
						out.push_back(v)
	elif kind == "essences":
		var c = _ap_lbal_canonical_essence_type_v81(raw)
		if not out.has(c):
			out.push_back(c)
		match c:
			"cursed_katana_essence":
				for v in ["essence_cursed_katana", "katana_essence", "cursed_sword_essence", "essence_katana"]:
					if not out.has(v):
						out.push_back(v)
			"piggy_bank_essence":
				for v in ["essence_piggy_bank", "piggybank_essence", "piggy_bank_item_essence"]:
					if not out.has(v):
						out.push_back(v)
			"guillotine_essence":
				for v in ["essence_guillotine"]:
					if not out.has(v):
						out.push_back(v)
			"nori_the_rabbit_essence":
				for v in ["nori_essence", "essence_nori_the_rabbit", "essence_nori"]:
					if not out.has(v):
						out.push_back(v)
			"oswald_the_monkey_essence":
				for v in ["oswald_essence", "essence_oswald_the_monkey", "essence_oswald"]:
					if not out.has(v):
						out.push_back(v)
	return out

func _ap_lbal_set_has_alias_v83(values, kind, type_id):
	if typeof(values) != TYPE_DICTIONARY:
		return false
	for t in _ap_lbal_alias_candidates_for_kind_v83(kind, type_id):
		if values.has(t):
			return true
	return false

func _ap_lbal_database_type_for_kind_v83(kind, type_id):
	var database = _ap_lbal_database_for_kind(kind)
	for t in _ap_lbal_alias_candidates_for_kind_v83(kind, type_id):
		if typeof(database) == TYPE_DICTIONARY and database.has(t):
			return t
	return str(type_id)

func _ap_lbal_canonical_item_or_essence_type_v81(item_type):
	var t = str(item_type)
	if _ap_lbal_ends_with(t, "_essence") or t.begins_with("essence_"):
		return _ap_lbal_canonical_essence_type_v81(t)
	return _ap_lbal_canonical_item_type_v81(t)

func _ap_lbal_item_kind(item_type):
	var t = str(item_type)
	if _ap_lbal_ends_with(t, "_essence") or t.begins_with("essence_"):
		return "essences"
	return "items"

func _ap_lbal_should_filter(kind):
	if not ap_live_enabled or not ap_live_loaded:
		return false
	match kind:
		"symbols":
			return ap_live_lock_symbols
		"items":
			return ap_live_lock_normal_items
		"essences":
			return ap_live_lock_essences
	return false

func _ap_lbal_boost_pool_empty_for_kind(kind):
	# V80: Never bypass filtering because a tracker category is empty.
	# Symbols use default/start symbols + AP Check/tracker symbols.
	# Items and Essences use Missing AP Item/Essence placeholders.
	return false


func _ap_lbal_target_rarities_for_kind_v136(kind):
	var out = {}
	var database = _ap_lbal_database_for_kind(kind)
	if typeof(database) != TYPE_DICTIONARY:
		return out
	var source = _ap_lbal_priority_set_for_kind(kind)
	if typeof(source) != TYPE_DICTIONARY or source.size() <= 0:
		source = _ap_lbal_allowed_set_for_kind(kind)
	for type_id in source.keys():
		var t = str(type_id)
		if kind == "symbols":
			t = _ap_lbal_canonical_symbol_type_v55(t)
			if t == "ap_check" or ap_default_starting_symbol_types.has(t) or t == "base" or t == "empty" or t == "dud":
				continue
		elif kind == "items":
			t = _ap_lbal_database_type_for_kind_v83("items", t)
			if _ap_lbal_item_kind(t) == "essences":
				continue
		elif kind == "essences":
			t = _ap_lbal_database_type_for_kind_v83("essences", t)
			if _ap_lbal_item_kind(t) != "essences":
				continue
		if not database.has(t):
			continue
		var r = _ap_lbal_rarity_for_database_entry(database[t])
		if kind == "essences":
			r = "essence"
		out[str(r)] = true
	return out

func _ap_lbal_only_high_rarity_targets_v136(kind):
	# Boost mode should not turn common/uncommon rolls into rare/very rare checks.
	# If the tracker currently only has Rare/Very Rare checks for a category, leave
	# common/uncommon rarity buckets vanilla and only boost/filter the high buckets.
	if not ap_live_boost_pool_mode_v136:
		return false
	if not _ap_lbal_should_filter(kind):
		return false
	var rarities = _ap_lbal_target_rarities_for_kind_v136(kind)
	if rarities.size() <= 0:
		return false
	for r in rarities.keys():
		if str(r) != "rare" and str(r) != "very_rare":
			return false
	return true

func _ap_lbal_should_leave_rarity_vanilla_v136(kind, rarity):
	var r = str(rarity)
	if r != "common" and r != "uncommon":
		return false
	return _ap_lbal_only_high_rarity_targets_v136(kind)

func _ap_lbal_ap_check_pool_active():
	# V75: AP Check remains available while AP Check locations remain, even if
	# real tracker symbols are also possible. Pool filtering still limits other
	# choices to default starting symbols plus tracker-possible symbols.
	return ap_live_has_ap_checks and ap_live_ap_check_symbol_pool_active


func _ap_lbal_keep_dice_face_textures_v58():
	var main = get_node_or_null("/root/Main")
	if main == null:
		return
	if not "icon_texture_database" in main:
		return
	# Touching the entries keeps Godot from treating them like AP-filtered symbols.
	# d5/d3 themselves stay the real rolling symbols; dice1..5/d3_1..3 are only textures.
	var faces = ["dice1", "dice2", "dice3", "dice4", "dice5", "d3_1", "d3_2", "d3_3"]
	for f in faces:
		if main.icon_texture_database.has(f):
			main.icon_texture_database[f] = main.icon_texture_database[f]


func _ap_lbal_canonical_symbol_type_v55(type_id):
	var t = str(type_id)
	match t:
		"three_sided_die", "three_sided_dice", "three_sided_die_symbol":
			return "d3"
		"five_sided_die", "five_sided_dice", "five_sided_die_symbol", "dice", "die":
			return "d5"
	return t

func _ap_lbal_has_item_in_run(type_id):
	var t = str(type_id)
	var items_node = get_node_or_null("/root/Main/Items")
	if items_node == null:
		return false
	if items_node.has_method("has_unmodded_item"):
		return items_node.has_unmodded_item(t)
	if "item_types" in items_node:
		return items_node.item_types.has(t)
	return false

func _ap_lbal_is_allowed(kind, type_id):
	var t = str(type_id)
	if kind == "symbols":
		t = _ap_lbal_canonical_symbol_type_v55(t)
		if t == "ap_check" and not _ap_lbal_ap_check_pool_active():
			return false
	elif kind == "items":
		t = _ap_lbal_canonical_item_type_v81(t)
	elif kind == "essences":
		t = _ap_lbal_canonical_essence_type_v81(t)
	if kind == "items" and ap_one_per_run_items.has(t) and _ap_lbal_has_item_in_run(t):
		return false
	if not _ap_lbal_should_filter(kind):
		return true
	match kind:
		"symbols":
			return ap_allowed_symbols.has(t)
		"items":
			return ap_allowed_items.has(t) or _ap_lbal_set_has_alias_v83(ap_allowed_items, "items", t)
		"essences":
			return ap_allowed_essences.has(t) or _ap_lbal_set_has_alias_v83(ap_allowed_essences, "essences", t)
	return true

func _ap_lbal_is_metadata_only_locked_v116(kind, type_id):
	# True means: keep this database entry around for default name/description/icon,
	# but do not let it enter Add Symbol/Add Item/Add Essence choice pools.
	if not _ap_lbal_should_filter(kind):
		return false
	var t = str(type_id)
	if kind == "symbols":
		t = _ap_lbal_canonical_symbol_type_v55(t)
		if t == "ap_check" and _ap_lbal_ap_check_pool_active():
			return false
	elif kind == "items":
		t = _ap_lbal_canonical_item_type_v81(t)
	elif kind == "essences":
		t = _ap_lbal_canonical_essence_type_v81(t)
	return not _ap_lbal_is_allowed(kind, t)

func _ap_lbal_mark_metadata_only_descriptions_v116(database, kind):
	# V116: metadata-only layer. Every existing vanilla database entry can keep
	# its real LBAL description, but locked entries are flagged and skipped by
	# database backfills so they do not become selectable.
	if typeof(database) != TYPE_DICTIONARY:
		return
	for key in database.keys():
		if typeof(database[key]) != TYPE_DICTIONARY:
			continue
		var t = str(key)
		if kind == "items" and _ap_lbal_item_kind(t) == "essences":
			continue
		if kind == "essences" and _ap_lbal_item_kind(t) != "essences":
			continue
		database[key]["ap_metadata_only_v116"] = _ap_lbal_is_metadata_only_locked_v116(kind, t)

func _ap_lbal_database_entry_metadata_locked_v116(kind, type_id, entry):
	if typeof(entry) == TYPE_DICTIONARY and entry.has("ap_metadata_only_v116") and bool(entry["ap_metadata_only_v116"]):
		return true
	if _ap_lbal_should_filter(kind) and not _ap_lbal_is_allowed(kind, type_id):
		return true
	return false

func _ap_lbal_symbol_can_appear_in_rarity_v119(type_id, rarity):
	# V119: metadata-only symbols can be loaded for icons/descriptions, but
	# Add Symbol still must obey the vanilla rarity table. Very Rare symbols
	# like Diamond should not appear on early payments where Very Rare cannot roll.
	var symbol_type = _ap_lbal_canonical_symbol_type_v55(type_id)
	if symbol_type == "ap_check":
		return _ap_lbal_ap_check_pool_active()
	var database = _ap_lbal_database_for_kind("symbols")
	if typeof(database) == TYPE_DICTIONARY and database.has(symbol_type):
		return _ap_lbal_rarity_matches(database[symbol_type], rarity)
	return true

func _ap_lbal_database_for_kind(kind):
	var main = get_node_or_null("/root/Main")
	if main == null:
		return {}
	if kind == "symbols":
		return main.tile_database
	return main.item_database

func _ap_lbal_is_placeholder_type_v68(type_id):
	var t = str(type_id)
	return t.find("ap_missing_") == 0 or t == "missing" or t == "question_mark" or t == "unknown" or t == "symbol_missing" or t == "missing_symbol" or t == "item_missing" or t == "missing_item" or t == "ap_locked" or t == "locked"

func _ap_lbal_backfill_type_array_from_database_v68(result, kind, wanted_rarity = null, forced_group = null):
	if kind == "symbols" and _ap_lbal_no_real_tracker_symbols_v89():
		var strict = []
		var database_default = _ap_lbal_database_for_kind("symbols")
		for t in ap_default_starting_symbol_types:
			if typeof(database_default) == TYPE_DICTIONARY and database_default.has(t) and not strict.has(t):
				strict.push_back(t)
		if _ap_lbal_ap_check_pool_active() and typeof(database_default) == TYPE_DICTIONARY and database_default.has("ap_check"):
			strict.push_back("ap_check")
		return strict
	if typeof(result) != TYPE_ARRAY:
		result = []
	var database = _ap_lbal_database_for_kind(kind)
	if typeof(database) != TYPE_DICTIONARY:
		return result
	for type_id in database.keys():
		var t = str(type_id)
		if _ap_lbal_is_placeholder_type_v68(t):
			continue
		if kind == "items" and _ap_lbal_item_kind(t) == "essences":
			continue
		if kind == "essences" and _ap_lbal_item_kind(t) != "essences":
			continue
		if kind == "symbols":
			t = _ap_lbal_canonical_symbol_type_v55(t)
			if t == "ap_check" and not _ap_lbal_ap_check_pool_active():
				continue
			if not _ap_lbal_symbol_matches_forced_group(t, forced_group):
				continue
		if _ap_lbal_database_entry_metadata_locked_v116(kind, t, database[type_id]):
			continue
		if wanted_rarity != null and not _ap_lbal_rarity_matches(database[type_id], wanted_rarity):
			continue
		if not result.has(t):
			result.push_back(t)
	return result

func _ap_lbal_backfill_card_pool_from_database_v68(card_pool, kind, forced_group = null):
	if typeof(card_pool) != TYPE_DICTIONARY:
		card_pool = {}
	var database = _ap_lbal_database_for_kind(kind)
	var values = _ap_lbal_backfill_type_array_from_database_v68([], kind, null, forced_group)
	for t in values:
		if not database.has(t):
			continue
		var rarity = _ap_lbal_rarity_for_database_entry(database[t])
		if not card_pool.has(rarity) or typeof(card_pool[rarity]) != TYPE_ARRAY:
			card_pool[rarity] = []
		if not card_pool[rarity].has(t):
			card_pool[rarity].push_back(t)
	return card_pool

func _ap_lbal_rarity_for_database_entry(entry):
	if entry == null:
		return "common"
	if typeof(entry) == TYPE_DICTIONARY:
		return str(entry.get("rarity", "common"))
	return str(entry.rarity)

func _ap_lbal_rarity_matches(entry, wanted_rarity):
	if wanted_rarity == null:
		return true
	return _ap_lbal_rarity_for_database_entry(entry) == str(wanted_rarity)

func _ap_lbal_allowed_set_for_kind(kind):
	match kind:
		"symbols":
			return ap_allowed_symbols
		"items":
			return ap_allowed_items
		"essences":
			return ap_allowed_essences
	return {}

func _ap_lbal_priority_set_for_kind(kind):
	match kind:
		"symbols":
			return ap_priority_symbols
		"items":
			return ap_priority_items
		"essences":
			return ap_priority_essences
	return {}

func _ap_lbal_card_pool_count(card_pool):
	var total = 0
	if typeof(card_pool) != TYPE_DICTIONARY:
		return 0
	for rarity in card_pool.keys():
		if typeof(card_pool[rarity]) == TYPE_ARRAY:
			total += card_pool[rarity].size()
	return total

func _ap_lbal_effective_symbol_group(forced_group):
	if forced_group == null:
		return null
	var g = str(forced_group)
	if g == "":
		return null
	if g == "food":
		return "fruit"
	return g

func _ap_lbal_symbol_matches_forced_group(type_id, forced_group):
	var g = _ap_lbal_effective_symbol_group(forced_group)
	if g == null:
		return true
	var main = get_node_or_null("/root/Main")
	if main == null:
		return true
	if not main.group_database.has("symbols"):
		return true
	if not main.group_database["symbols"].has(g):
		return true
	return main.group_database["symbols"][g].has(str(type_id))

func _ap_lbal_extra_forces_essence(extra_values):
	# AP_ITEM_ESSENCE_SPLIT_PATCH_V21
	# Only treat the screen as an Essence screen if every forced rarity is essence.
	# Some LBAL screens include a single essence rarity alongside normal items; those
	# caused mixed Item/Essence cards. Keep those as normal item screens.
	if typeof(extra_values) != TYPE_DICTIONARY:
		return false
	if not extra_values.has("forced_rarity"):
		return false
	if typeof(extra_values.forced_rarity) != TYPE_ARRAY:
		return false
	if extra_values.forced_rarity.size() <= 0:
		return false
	for r in extra_values.forced_rarity:
		if str(r) != "essence":
			return false
	return true

func _ap_lbal_first_nonempty_rarity(card_pool, essence_only = false):
	# AP_ITEM_RARITY_FALLBACK_PATCH_V26
	if typeof(card_pool) != TYPE_DICTIONARY:
		return null
	if essence_only:
		if card_pool.has("essence") and typeof(card_pool["essence"]) == TYPE_ARRAY and card_pool["essence"].size() > 0:
			return "essence"
		return null
	var rarity_order = ["common", "uncommon", "rare", "very_rare", "none"]
	for rarity in rarity_order:
		if card_pool.has(rarity) and typeof(card_pool[rarity]) == TYPE_ARRAY and card_pool[rarity].size() > 0:
			return rarity
	for rarity in card_pool.keys():
		if rarity == "essence":
			continue
		if typeof(card_pool[rarity]) == TYPE_ARRAY and card_pool[rarity].size() > 0:
			return rarity
	return null

func _ap_lbal_vanilla_rarity_for_current_screen(choosing_items):
	# AP_VANILLA_RARITY_TABLE_V47
	var paid = int(times_rent_paid)
	var common = 1000
	var uncommon = 0
	var rare = 0
	var very_rare = 0
	if choosing_items:
		if paid <= 0:
			common = 1000; uncommon = 0; rare = 0; very_rare = 0
		elif paid == 1:
			common = 900; uncommon = 100; rare = 0; very_rare = 0
		elif paid == 2:
			common = 790; uncommon = 200; rare = 10; very_rare = 0
		elif paid == 3:
			common = 740; uncommon = 250; rare = 10; very_rare = 0
		elif paid == 4:
			common = 690; uncommon = 290; rare = 15; very_rare = 5
		else:
			common = 680; uncommon = 300; rare = 15; very_rare = 5
	else:
		if paid <= 0:
			common = 1000; uncommon = 0; rare = 0; very_rare = 0
		elif paid == 1:
			common = 900; uncommon = 100; rare = 0; very_rare = 0
		elif paid == 2:
			common = 790; uncommon = 200; rare = 10; very_rare = 0
		elif paid == 3:
			common = 740; uncommon = 250; rare = 10; very_rare = 0
		elif paid == 4:
			common = 690; uncommon = 290; rare = 15; very_rare = 5
		elif paid == 5:
			common = 680; uncommon = 300; rare = 15; very_rare = 5
		else:
			common = 600; uncommon = 350; rare = 35; very_rare = 15
	var roll = randi() % 1000
	if roll < common:
		return "common"
	roll -= common
	if roll < uncommon:
		return "uncommon"
	roll -= uncommon
	if roll < rare:
		return "rare"
	return "very_rare"

func _ap_lbal_missing_placeholder_type(choosing_items, essence_only, rarity):
	return _ap_lbal_missing_placeholder_type_v107(choosing_items, essence_only, rarity, 1)

func _ap_lbal_missing_placeholder_type_v107(choosing_items, essence_only, rarity, index = 1):
	var r = str(rarity)
	var i = int(index)
	if i < 1:
		i = 1
	if i > 3:
		i = 3
	if essence_only or r == "essence":
		return "ap_missing_item_essence_" + str(i)
	if r != "common" and r != "uncommon" and r != "rare" and r != "very_rare":
		r = "common"
	if choosing_items:
		return "ap_missing_item_" + r + "_" + str(i)
	# V76: Missing AP Symbol should not appear in Add Symbol choices.
	return ""


func _ap_lbal_placeholder_display_name_v56(type_id):
	var t = str(type_id)
	if t.find("essence") != -1:
		return "Missing AP Essence"
	if t.find("item") != -1:
		return "Missing AP Item"
	return "Missing AP Symbol"

func _ap_lbal_placeholder_description_v56(type_id):
	var t = str(type_id)
	if t.find("essence") != -1:
		return "No possible AP Essence exists for this reward yet. Find more AP unlocks to fill this choice."
	if t.find("item") != -1:
		return "No possible AP Item exists for this rarity yet. Find more AP unlocks to fill this choice."
	return "No possible AP Symbol exists for this rarity yet. Find more AP unlocks to fill this choice."

func _ap_lbal_placeholder_rarity_v56(type_id):
	var t = str(type_id)
	if t.find("very_rare") != -1:
		return "very_rare"
	if t.find("rare") != -1:
		return "rare"
	if t.find("uncommon") != -1:
		return "uncommon"
	if t.find("essence") != -1:
		return "essence"
	return "common"

func _ap_lbal_make_placeholder_data_v56(type_id, kind):
	var name = _ap_lbal_placeholder_display_name_v56(type_id)
	var desc = _ap_lbal_placeholder_description_v56(type_id)
	return {
		"type": str(type_id),
		"display_name": name,
		"name": name,
		"rarity": _ap_lbal_placeholder_rarity_v56(type_id),
		"groups": [],
		"values": [],
		"value": 0,
		"value_text": {"value": "0"},
		"description": desc,
		"text": desc,
		"localized_names": {"en": name},
		"localized_descriptions": {"en": desc},
		"localized_text": {"en": desc},
		"modded": true,
		"inherit_description": false,
		"inherit_effects": false
	}


func _ap_lbal_original_desc_for_type_v59(type_id):
	var base_type = str(type_id)
	if base_type.find("_STEAM_ID_") != -1:
		base_type = base_type.substr(0, base_type.find("_STEAM_ID_"))
	var desc_key = base_type + "_desc"
	var desc = tr(desc_key)
	if desc == desc_key:
		return ""
	return desc

func _ap_lbal_original_name_for_type_v59(type_id):
	var base_type = str(type_id)
	if base_type.find("_STEAM_ID_") != -1:
		base_type = base_type.substr(0, base_type.find("_STEAM_ID_"))
	var name_key = base_type
	var name = tr(name_key)
	if name == name_key:
		return ""
	return name

func _ap_lbal_apply_original_description_to_database_v59(database):
	# V86: force every vanilla symbol/item/essence database entry back to the
	# exact name/description from the game localization files, even if the AP mod
	# has that content locked/excluded right now. This stops generated AP text like
	# "locked by Archipelago" from replacing real LBAL descriptions.
	if typeof(database) != TYPE_DICTIONARY:
		return
	var locale = TranslationServer.get_locale()
	for key in database.keys():
		if typeof(database[key]) != TYPE_DICTIONARY:
			continue
		var desc = _ap_lbal_original_desc_for_type_v59(key)
		if desc != "":
			database[key].description = desc
			database[key].text = desc
			if not database[key].has("localized_descriptions") or typeof(database[key].localized_descriptions) != TYPE_DICTIONARY:
				database[key].localized_descriptions = {}
			database[key].localized_descriptions[locale] = desc
			database[key].localized_descriptions["en"] = desc
			if not database[key].has("localized_text") or typeof(database[key].localized_text) != TYPE_DICTIONARY:
				database[key].localized_text = {}
			database[key].localized_text[locale] = desc
			database[key].localized_text["en"] = desc
			# Keep inheritance on so if LBAL rebuilds the entry later it still pulls
			# the base-game description instead of an AP placeholder description.
			database[key].inherit_description = true
		var name = _ap_lbal_original_name_for_type_v59(key)
		if name != "":
			database[key].display_name = name
			database[key].name = name
			if not database[key].has("localized_names") or typeof(database[key].localized_names) != TYPE_DICTIONARY:
				database[key].localized_names = {}
			database[key].localized_names[locale] = name
			database[key].localized_names["en"] = name

func _ap_lbal_restore_original_descriptions_v59():
	var main = get_node_or_null("/root/Main")
	if main == null:
		return
	if "tile_database" in main:
		_ap_lbal_apply_original_description_to_database_v59(main.tile_database)
		_ap_lbal_mark_metadata_only_descriptions_v116(main.tile_database, "symbols")
	if "item_database" in main:
		_ap_lbal_apply_original_description_to_database_v59(main.item_database)
		_ap_lbal_mark_metadata_only_descriptions_v116(main.item_database, "items")
		_ap_lbal_mark_metadata_only_descriptions_v116(main.item_database, "essences")
	# V94/V116: leave icon texture database intact. Item descriptions can
	# reference locked symbols by icon while those symbols remain metadata-only.
	if "icon_texture_database" in main:
		for k in main.icon_texture_database.keys():
			main.icon_texture_database[k] = main.icon_texture_database[k]


func _ap_lbal_install_missing_placeholder_descriptions_v56():
	var main = get_node_or_null("/root/Main")
	if main == null:
		return
	# V79: Missing AP Symbol should never be a selectable symbol. Only install
	# item/essence placeholders for empty AP item/essence reward buckets.
	var item_types = ["ap_missing_item_common", "ap_missing_item_uncommon", "ap_missing_item_rare", "ap_missing_item_very_rare", "ap_missing_item_essence", "item_missing", "missing_item", "ap_locked", "locked"]
	for t in item_types:
		if not main.item_database.has(t):
			main.item_database[t] = _ap_lbal_make_placeholder_data_v56(t, "items")
		else:
			main.item_database[t].display_name = _ap_lbal_placeholder_display_name_v56(t)
			main.item_database[t].description = _ap_lbal_placeholder_description_v56(t)
			main.item_database[t].text = _ap_lbal_placeholder_description_v56(t)
			main.item_database[t].localized_names = {"en": main.item_database[t].display_name}
			main.item_database[t].localized_descriptions = {"en": main.item_database[t].description}
			main.item_database[t].localized_text = {"en": main.item_database[t].description}
			main.item_database[t].modded = true
			main.item_database[t].inherit_description = false
			main.item_database[t].inherit_effects = false


# AP_EMPTY_ITEM_POOL_FIX_V65
func _ap_lbal_ensure_placeholder_database_entry_v65(kind, placeholder):
	var database = _ap_lbal_database_for_kind(kind)
	if typeof(database) != TYPE_DICTIONARY:
		return false
	if database.has(placeholder):
		return true
	var data = _ap_lbal_make_placeholder_data_v56(placeholder, kind)
	database[placeholder] = data
	return database.has(placeholder)

func _ap_lbal_safe_item_fallback_v65(database, wanted_rarity):
	var r = str(wanted_rarity)
	if r == "" or r == "null" or r == "essence":
		r = "common"
	var placeholder = _ap_lbal_missing_placeholder_type(true, false, r)
	_ap_lbal_ensure_placeholder_database_entry_v65("items", placeholder)
	if typeof(database) == TYPE_DICTIONARY and database.has(placeholder):
		return database[placeholder]
	if typeof(database) == TYPE_DICTIONARY and database.has("item_missing"):
		return database["item_missing"]
	if typeof(database) == TYPE_DICTIONARY and database.has("pool_ball"):
		return database["pool_ball"]
	return {}


func _ap_lbal_add_missing_placeholder_to_rarity(card_pool, choosing_items, essence_only, rarity):
	_ap_lbal_restore_original_descriptions_v59()
	_ap_lbal_install_missing_placeholder_descriptions_v56()
	if typeof(card_pool) != TYPE_DICTIONARY:
		return card_pool
	var r = str(rarity)
	if r == "" or r == "null":
		r = _ap_lbal_vanilla_rarity_for_current_screen(choosing_items)
	if not card_pool.has(r) or typeof(card_pool[r]) != TYPE_ARRAY:
		card_pool[r] = []
	if card_pool[r].size() > 0:
		return card_pool
	var kind = "symbols"
	if choosing_items:
		if essence_only or r == "essence":
			kind = "essences"
		else:
			kind = "items"
	if _ap_lbal_should_leave_rarity_vanilla_v136(kind, r):
		return card_pool
	if not _ap_lbal_should_filter(kind) or _ap_lbal_boost_pool_empty_for_kind(kind):
		return card_pool
	var database = _ap_lbal_database_for_kind(kind)
	if choosing_items:
		for i in range(1, 4):
			var placeholder = _ap_lbal_missing_placeholder_type_v107(choosing_items, essence_only, r, i)
			if not database.has(placeholder):
				_ap_lbal_ensure_placeholder_database_entry_v65(kind, placeholder)
			if database.has(placeholder):
				card_pool[r].push_back(placeholder)
	else:
		var placeholder = _ap_lbal_missing_placeholder_type(choosing_items, essence_only, r)
		if not database.has(placeholder):
			_ap_lbal_ensure_placeholder_database_entry_v65(kind, placeholder)
		if database.has(placeholder):
			card_pool[r].push_back(placeholder)
	return card_pool

func _ap_lbal_fill_empty_rarities_with_placeholders(card_pool, choosing_items, essence_only):
	if essence_only:
		return _ap_lbal_add_missing_placeholder_to_rarity(card_pool, choosing_items, true, "essence")
	var rarity_order = ["common", "uncommon", "rare", "very_rare"]
	for r in rarity_order:
		card_pool = _ap_lbal_add_missing_placeholder_to_rarity(card_pool, choosing_items, false, r)
	return card_pool


func _ap_lbal_backfill_symbol_pool_if_needed(card_pool, forced_group = null):
	if typeof(card_pool) != TYPE_DICTIONARY:
		return card_pool
	if _ap_lbal_card_pool_count(card_pool) > 0:
		return card_pool
	var database = _ap_lbal_database_for_kind("symbols")
	for t in ap_default_starting_symbol_types:
		if not database.has(t):
			continue
		if not _ap_lbal_symbol_matches_forced_group(t, forced_group):
			continue
		var rarity = _ap_lbal_rarity_for_database_entry(database[t])
		if not card_pool.has(rarity):
			card_pool[rarity] = []
		if not card_pool[rarity].has(t):
			card_pool[rarity].push_back(t)
	return card_pool

func _ap_lbal_fill_empty_symbol_rarities_v76(card_pool, forced_group = null):
	# V80: Missing AP Symbol is never used. AP Check is allowed in every symbol
	# rarity bucket while AP Check locations remain. Other symbols still respect
	# native rarity.
	if typeof(card_pool) != TYPE_DICTIONARY:
		card_pool = {}
	var database = _ap_lbal_database_for_kind("symbols")
	if _ap_lbal_ap_check_pool_active():
		_ap_lbal_ensure_ap_check_database_entry_v80()
		ap_allowed_symbols["ap_check"] = true
		database = _ap_lbal_database_for_kind("symbols")
	var allowed_set = _ap_lbal_allowed_set_for_kind("symbols")
	var rarity_order = ["common", "uncommon", "rare", "very_rare", "none"]
	for r in rarity_order:
		if not card_pool.has(r) or typeof(card_pool[r]) != TYPE_ARRAY:
			card_pool[r] = []
		var fallback = []
		if _ap_lbal_ap_check_pool_active() and database.has("ap_check"):
			fallback.push_back("ap_check")
		for type_id in allowed_set.keys():
			var t = _ap_lbal_canonical_symbol_type_v55(type_id)
			if t == "ap_check":
				continue
			if not database.has(t):
				continue
			if not _ap_lbal_symbol_matches_forced_group(t, forced_group):
				continue
			if _ap_lbal_rarity_matches(database[t], r) and not fallback.has(t):
				fallback.push_back(t)
		if fallback.size() <= 0:
			for t in ap_default_starting_symbol_types:
				if database.has(t) and _ap_lbal_symbol_matches_forced_group(t, forced_group) and not fallback.has(t):
					fallback.push_back(t)
		for t in fallback:
			if not card_pool[r].has(t):
				card_pool[r].push_back(t)
	return card_pool

func _ap_lbal_push_allowed_types_into_card_pool(card_pool, kind, forced_group = null):
	if typeof(card_pool) != TYPE_DICTIONARY:
		return card_pool
	if not ap_live_enabled or not ap_live_loaded:
		return card_pool
	var database = _ap_lbal_database_for_kind(kind)
	var allowed_set = _ap_lbal_allowed_set_for_kind(kind)
	var priority_set = _ap_lbal_priority_set_for_kind(kind)
	var existing_rarities = []
	for rarity_key in card_pool.keys():
		if typeof(card_pool[rarity_key]) == TYPE_ARRAY:
			existing_rarities.push_back(rarity_key)
	if existing_rarities.size() <= 0:
		if kind == "essences":
			existing_rarities = ["essence"]
		else:
			existing_rarities = ["common", "uncommon", "rare", "very_rare"]
	for type_id in allowed_set.keys():
		var t = str(type_id)
		if kind == "symbols":
			t = _ap_lbal_canonical_symbol_type_v55(t)
		elif kind == "items":
			t = _ap_lbal_database_type_for_kind_v83("items", t)
		elif kind == "essences":
			t = _ap_lbal_database_type_for_kind_v83("essences", t)
		if not database.has(t):
			continue
		if kind == "symbols" and not _ap_lbal_symbol_matches_forced_group(t, forced_group):
			continue
		# V78/V108: keep normal Symbol targets in their native LBAL rarity so Very Rare
		# symbols like Diamond do not flood common rolls. But when there are no symbol
		# Send checks in the tracker, already-unlocked AP symbols are a fallback pool;
		# inject those into the active choice buckets so they actually show.
		if kind == "symbols" and ap_live_symbol_received_fallback_v108 and not ap_default_starting_symbol_types.has(t) and t != "ap_check" and t != "base" and t != "empty" and t != "dud":
			var native_rarity_v119 = _ap_lbal_rarity_for_database_entry(database[t])
			if not card_pool.has(native_rarity_v119) or typeof(card_pool[native_rarity_v119]) != TYPE_ARRAY:
				card_pool[native_rarity_v119] = []
			if not card_pool[native_rarity_v119].has(t):
				card_pool[native_rarity_v119].push_back(t)
			continue
		if kind == "items" and t == "pool_ball" and (allowed_set.has("pool_ball") or priority_set.has("pool_ball") or _ap_lbal_set_has_alias_v83(priority_set, kind, t)):
			if not card_pool.has("common") or typeof(card_pool["common"]) != TYPE_ARRAY:
				card_pool["common"] = []
			if not card_pool["common"].has("pool_ball"):
				card_pool["common"].push_front("pool_ball")
			continue
		if kind != "symbols" and ap_live_boost_pool_mode_v136 and (priority_set.has(t) or _ap_lbal_set_has_alias_v83(priority_set, kind, t)):
			var inject_rarities = existing_rarities
			if kind == "essences":
				inject_rarities = ["essence"]
			for inject_rarity in inject_rarities:
				if str(inject_rarity) == "essence" and kind != "essences":
					continue
				if not card_pool.has(inject_rarity) or typeof(card_pool[inject_rarity]) != TYPE_ARRAY:
					card_pool[inject_rarity] = []
				if not card_pool[inject_rarity].has(t):
					card_pool[inject_rarity].push_front(t)
			continue
		var native_rarity = _ap_lbal_rarity_for_database_entry(database[t])
		if kind == "essences":
			native_rarity = "essence"
		if not card_pool.has(native_rarity):
			card_pool[native_rarity] = []
		if not card_pool[native_rarity].has(t):
			card_pool[native_rarity].push_back(t)
	return card_pool

func _ap_lbal_push_allowed_types_into_type_array(arr, kind, wanted_rarity):
	var result = arr.duplicate(true)
	if not ap_live_enabled or not ap_live_loaded:
		return result
	var database = _ap_lbal_database_for_kind(kind)
	var allowed_set = _ap_lbal_allowed_set_for_kind(kind)
	var priority_set = _ap_lbal_priority_set_for_kind(kind)
	for type_id in allowed_set.keys():
		var t = str(type_id)
		if kind == "symbols":
			t = _ap_lbal_canonical_symbol_type_v55(t)
		elif kind == "items":
			t = _ap_lbal_canonical_item_type_v81(t)
		elif kind == "essences":
			t = _ap_lbal_canonical_essence_type_v81(t)
		if result.has(t) or not database.has(t):
			continue
		# V78/V108: fallback symbols should be eligible on the active Add Symbol screen
		# when there are no symbol checks in the tracker.
		if kind == "symbols" and ap_live_symbol_received_fallback_v108 and not ap_default_starting_symbol_types.has(t) and t != "ap_check" and t != "base" and t != "empty" and t != "dud":
			if _ap_lbal_rarity_matches(database[t], wanted_rarity):
				result.push_back(t)
		elif kind != "symbols" and ap_live_boost_pool_mode_v136 and (priority_set.has(t) or _ap_lbal_set_has_alias_v83(priority_set, kind, t)):
			result.push_back(t)
		elif kind == "essences" and str(wanted_rarity) == "essence" and _ap_lbal_is_allowed(kind, t):
			result.push_back(t)
		elif _ap_lbal_rarity_matches(database[t], wanted_rarity):
			result.push_back(t)
	return result

func _ap_lbal_no_real_tracker_content_v91(kind):
	# V92: Trust explicit tracker-category flags from the Python client. The AP
	# state may still have stale/allowed item IDs from older builds, but if the
	# tracker currently has no item/essence target, Add Item/Add Essence must show
	# Missing AP Item/Essence only.
	match kind:
		"items":
			return not ap_live_has_item_targets_v92
		"essences":
			return not ap_live_has_essence_targets_v92
	return false

func _ap_lbal_only_placeholder_array_v91(kind, wanted_rarity = null):
	var out = []
	if kind == "essences":
		for i in range(1, 4):
			var placeholder = _ap_lbal_missing_placeholder_type_v107(true, true, "essence", i)
			_ap_lbal_ensure_placeholder_database_entry_v65("items", placeholder)
			if placeholder != null and str(placeholder) != "":
				out.push_back(placeholder)
	else:
		for i in range(1, 4):
			var placeholder = _ap_lbal_missing_placeholder_type_v107(true, false, wanted_rarity, i)
			_ap_lbal_ensure_placeholder_database_entry_v65("items", placeholder)
			if placeholder != null and str(placeholder) != "":
				out.push_back(placeholder)
	return out

func _ap_lbal_strip_items_to_tracker_or_placeholder_v91(card_pool, target_kind, essence_only_screen):
	if typeof(card_pool) != TYPE_DICTIONARY:
		card_pool = {}
	if not _ap_lbal_no_real_tracker_content_v91(target_kind):
		return card_pool
	# No AP item/essence is possible right now, so remove every vanilla item in the
	# rolled card pool and replace with the proper Missing AP Item/Essence cards.
	for rarity in card_pool.keys():
		if typeof(card_pool[rarity]) == TYPE_ARRAY:
			card_pool[rarity] = []
	if target_kind == "essences" or essence_only_screen:
		var p = _ap_lbal_missing_placeholder_type(true, true, "essence")
		_ap_lbal_ensure_placeholder_database_entry_v65("essences", p)
		if not card_pool.has("essence") or typeof(card_pool["essence"]) != TYPE_ARRAY:
			card_pool["essence"] = []
		if p != null and str(p) != "" and not card_pool["essence"].has(p):
			card_pool["essence"].push_back(p)
	else:
		for r in ["common", "uncommon", "rare", "very_rare"]:
			var p = _ap_lbal_missing_placeholder_type(true, false, r)
			_ap_lbal_ensure_placeholder_database_entry_v65("items", p)
			if not card_pool.has(r) or typeof(card_pool[r]) != TYPE_ARRAY:
				card_pool[r] = []
			if p != null and str(p) != "" and not card_pool[r].has(p):
				card_pool[r].push_back(p)
	return card_pool

func _ap_lbal_filter_item_type_array(arr, wanted_rarity = null):
	_ap_lbal_update_state(true)
	_ap_lbal_restore_original_descriptions_v59()
	var expanded = []
	if typeof(arr) == TYPE_ARRAY:
		expanded = arr.duplicate(true)
	var want_essence = str(wanted_rarity) == "essence"
	var target_kind = "items"
	if want_essence:
		target_kind = "essences"
	if not want_essence and _ap_lbal_should_filter("items") and _ap_lbal_should_leave_rarity_vanilla_v136("items", wanted_rarity):
		return expanded
	if want_essence and _ap_lbal_should_filter("essences") and _ap_lbal_should_leave_rarity_vanilla_v136("essences", wanted_rarity):
		return expanded
	if not want_essence and _ap_lbal_should_filter("items") and not ap_live_has_item_targets_v92:
		return _ap_lbal_only_placeholder_array_v91("items", wanted_rarity)
	if want_essence and _ap_lbal_should_filter("essences") and not ap_live_has_essence_targets_v92:
		return _ap_lbal_only_placeholder_array_v91("essences", wanted_rarity)
	if _ap_lbal_should_filter(target_kind) and _ap_lbal_no_real_tracker_content_v91(target_kind):
		return _ap_lbal_only_placeholder_array_v91(target_kind, wanted_rarity)
	if want_essence:
		expanded = _ap_lbal_push_allowed_types_into_type_array(expanded, "essences", wanted_rarity)
	else:
		expanded = _ap_lbal_push_allowed_types_into_type_array(expanded, "items", wanted_rarity)
	var result = []
	for type_id in expanded:
		var kind = _ap_lbal_item_kind(type_id)
		if want_essence and kind != "essences":
			continue
		if not want_essence and kind == "essences":
			continue
		if _ap_lbal_is_allowed(kind, type_id):
			result.push_back(type_id)
	if result.size() <= 0:
		if not _ap_lbal_should_filter(target_kind) or _ap_lbal_boost_pool_empty_for_kind(target_kind):
			return _ap_lbal_backfill_type_array_from_database_v68(result, target_kind, wanted_rarity)
		var placeholder = _ap_lbal_missing_placeholder_type(true, want_essence, wanted_rarity)
		if placeholder != null and placeholder != "":
			if want_essence:
				_ap_lbal_ensure_placeholder_database_entry_v65("essences", placeholder)
			else:
				_ap_lbal_ensure_placeholder_database_entry_v65("items", placeholder)
			result.push_back(placeholder)
	return result


func _ap_lbal_remove_ap_check_from_card_pool_v70(card_pool):
	if typeof(card_pool) != TYPE_DICTIONARY:
		return card_pool
	for rarity in card_pool.keys():
		if typeof(card_pool[rarity]) != TYPE_ARRAY:
			continue
		while card_pool[rarity].has("ap_check"):
			card_pool[rarity].erase("ap_check")
	return card_pool


func _ap_lbal_remove_missing_symbol_cards_v79(card_pool):
	# Hard safety: old generated mod files or older PCK patches may leave
	# ap_missing_symbol_* in the symbol database/card pool. Strip them from Add
	# Symbol pools; missing placeholders are only for items/essences now.
	if typeof(card_pool) != TYPE_DICTIONARY:
		return card_pool
	for rarity in card_pool.keys():
		if typeof(card_pool[rarity]) != TYPE_ARRAY:
			continue
		if _ap_lbal_should_leave_rarity_vanilla_v136("symbols", rarity):
			continue
		var filtered = []
		for type_id in card_pool[rarity]:
			var t = _ap_lbal_canonical_symbol_type_v55(type_id)
			if t.find("ap_missing_symbol") == 0 or t == "symbol_missing" or t == "missing_symbol" or t == "ap_missing":
				continue
			filtered.push_back(type_id)
		card_pool[rarity] = filtered
	return card_pool


func _ap_lbal_ensure_ap_check_database_entry_v80():
	# V80: AP Check is a real AP symbol, not a Missing AP Symbol placeholder.
	# Make sure it exists and can be injected while AP Check locations remain.
	var main = get_node_or_null("/root/Main")
	if main == null:
		return false
	if not "tile_database" in main:
		return false
	if main.tile_database.has("ap_check"):
		return true
	main.tile_database["ap_check"] = {
		"type": "ap_check",
		"display_name": "AP Check",
		"name": "AP Check",
		"rarity": "common",
		"groups": [],
		"values": [],
		"value": 3,
		"value_text": {"value": "3"},
		"description": "Gives <icon_coin>3, then destroys itself and sends the next <color_800080>AP Check<end>.",
		"text": "Gives <icon_coin>3, then destroys itself and sends the next <color_800080>AP Check<end>.",
		"localized_names": {"en": "AP Check"},
		"localized_descriptions": {"en": "Gives <icon_coin>3, then destroys itself and sends the next <color_800080>AP Check<end>."},
		"localized_text": {"en": "Gives <icon_coin>3, then destroys itself and sends the next <color_800080>AP Check<end>."},
		"modded": true,
		"inherit_description": false,
		"inherit_effects": false,
		"inherit_art": false
	}
	return main.tile_database.has("ap_check")


func _ap_lbal_apply_ap_check_priority_v71(card_pool, forced_group = null):
	# V80: AP Check stays available until every AP Check location is done.
	# Do not hide it because of vanilla forced_group filters.
	if not _ap_lbal_ap_check_pool_active():
		return card_pool
	var database = _ap_lbal_database_for_kind("symbols")
	if typeof(database) != TYPE_DICTIONARY:
		return card_pool
	if not database.has("ap_check"):
		_ap_lbal_ensure_ap_check_database_entry_v80()
		database = _ap_lbal_database_for_kind("symbols")
	if not database.has("ap_check"):
		return card_pool
	ap_allowed_symbols["ap_check"] = true
	var rarities = ["common", "uncommon", "rare", "very_rare", "none"]
	for rarity in rarities:
		if not card_pool.has(rarity) or typeof(card_pool[rarity]) != TYPE_ARRAY:
			card_pool[rarity] = []
		if not card_pool[rarity].has("ap_check"):
			card_pool[rarity].push_front("ap_check")
		for i in range(2):
			card_pool[rarity].push_back("ap_check")
	return card_pool


func _ap_lbal_symbol_only_default_or_apcheck_v89(type_id):
	var t = _ap_lbal_canonical_symbol_type_v55(type_id)
	if t == "ap_check":
		return _ap_lbal_ap_check_pool_active()
	return ap_default_starting_symbol_types.has(t)

func _ap_lbal_no_real_tracker_symbols_v89():
	# V107: already-unlocked AP symbols used as the no-tracker-symbol fallback
	# count as valid symbol targets and must not be stripped back to defaults.
	if ap_live_has_symbol_targets_v92:
		return false
	for t in ap_allowed_symbols.keys():
		var sym = _ap_lbal_canonical_symbol_type_v55(t)
		if sym != "ap_check" and not ap_default_starting_symbol_types.has(sym) and sym != "base" and sym != "empty" and sym != "dud":
			return false
	return true

func _ap_lbal_strip_to_default_and_apcheck_v89(card_pool):
	if typeof(card_pool) != TYPE_DICTIONARY:
		return card_pool
	for rarity in card_pool.keys():
		if typeof(card_pool[rarity]) != TYPE_ARRAY:
			continue
		var filtered = []
		for type_id in card_pool[rarity]:
			var t = _ap_lbal_canonical_symbol_type_v55(type_id)
			if _ap_lbal_symbol_only_default_or_apcheck_v89(t) and not filtered.has(t):
				filtered.push_back(t)
		card_pool[rarity] = filtered
	return card_pool

func _ap_lbal_guess_choosing_items_v93(email_type, card_pool):
	var e = str(email_type)
	if e.find("item") >= 0 or e.find("essence") >= 0:
		return true
	# Some LBAL builds call the Add Item screen with a different email_type.
	# Detect it from the card pool contents instead: if the pool contains item
	# database entries, it must be an item choice, not an Add Symbol choice.
	var main = get_node_or_null("/root/Main")
	if main == null or not "item_database" in main:
		return false
	if typeof(card_pool) != TYPE_DICTIONARY:
		return false
	for rarity in card_pool.keys():
		if typeof(card_pool[rarity]) != TYPE_ARRAY:
			continue
		for type_id in card_pool[rarity]:
			var t = str(type_id)
			if main.item_database.has(t):
				return true
	return false

func _ap_lbal_force_missing_item_pool_v93(card_pool, essence_only_screen = false):
	if typeof(card_pool) != TYPE_DICTIONARY:
		card_pool = {}
	for rarity in card_pool.keys():
		if typeof(card_pool[rarity]) == TYPE_ARRAY:
			card_pool[rarity] = []
	if essence_only_screen:
		var ep = _ap_lbal_missing_placeholder_type(true, true, "essence")
		_ap_lbal_ensure_placeholder_database_entry_v65("essences", ep)
		card_pool["essence"] = []
		if ep != null and str(ep) != "":
			card_pool["essence"].push_back(ep)
	else:
		var common = _ap_lbal_missing_placeholder_type(true, false, "common")
		_ap_lbal_ensure_placeholder_database_entry_v65("items", common)
		card_pool["common"] = []
		if common != null and str(common) != "":
			card_pool["common"].push_back(common)
	return card_pool

func _ap_lbal_missing_item_type_for_screen_v94(email, rarity):
	var essence_only = false
	if email != null and "extra_values" in email:
		essence_only = _ap_lbal_extra_forces_essence(email.extra_values)
	if essence_only:
		var ep = _ap_lbal_missing_placeholder_type(true, true, "essence")
		_ap_lbal_ensure_placeholder_database_entry_v65("essences", ep)
		return ep
	var r = str(rarity)
	if r == "" or r == "null" or r == "essence":
		r = "common"
	var p = _ap_lbal_missing_placeholder_type(true, false, r)
	_ap_lbal_ensure_placeholder_database_entry_v65("items", p)
	return p

func _ap_lbal_should_force_missing_item_card_v94(email, rarity):
	# V97: direct and reliable. The Pop-up email is an object in LBAL, so use
	# email.type directly instead of Dictionary-style checks.
	_ap_lbal_update_state(true)
	if email == null:
		return false
	var e = str(email.type)
	if e.find("item") == -1 and e.find("essence") == -1:
		return false
	var essence_only = false
	if "extra_values" in email:
		essence_only = _ap_lbal_extra_forces_essence(email.extra_values)
	if essence_only:
		return _ap_lbal_should_filter("essences") and not ap_live_has_essence_targets_v92
	return _ap_lbal_should_filter("items") and not ap_live_has_item_targets_v92

func _ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity):
	var database = _ap_lbal_database_for_kind("items")
	var p = _ap_lbal_missing_item_type_for_screen_v94(email, rarity)
	if typeof(database) == TYPE_DICTIONARY and p != null and str(p) != "" and database.has(p):
		card.data = database[p]
		return true
	if typeof(database) == TYPE_DICTIONARY and database.has("item_missing"):
		card.data = database["item_missing"]
		return true
	return false

func _ap_lbal_card_pool_has_missing_item_v98(card_pool):
	if typeof(card_pool) != TYPE_DICTIONARY:
		return false
	for rarity in card_pool.keys():
		if typeof(card_pool[rarity]) != TYPE_ARRAY:
			continue
		for type_id in card_pool[rarity]:
			var t = str(type_id)
			if t.begins_with("ap_missing_item") or t == "item_missing" or t == "missing_item":
				return true
	return false

func _ap_lbal_force_missing_item_choice_pool_v98(card_pool, rarity = "common", essence_only_screen = false):
	if typeof(card_pool) != TYPE_DICTIONARY:
		card_pool = {}
	for r in card_pool.keys():
		if typeof(card_pool[r]) == TYPE_ARRAY:
			card_pool[r] = []
	if essence_only_screen:
		card_pool["essence"] = []
		for i in range(1, 4):
			var ep = _ap_lbal_missing_placeholder_type_v107(true, true, "essence", i)
			_ap_lbal_ensure_placeholder_database_entry_v65("items", ep)
			if ep != null and str(ep) != "":
				card_pool["essence"].push_back(ep)
	else:
		# V107: exactly 3 unique Missing AP Item IDs for every rarity.
		for r in ["common", "uncommon", "rare", "very_rare"]:
			card_pool[r] = []
			for i in range(1, 4):
				var p = _ap_lbal_missing_placeholder_type_v107(true, false, r, i)
				_ap_lbal_ensure_placeholder_database_entry_v65("items", p)
				if p != null and str(p) != "":
					card_pool[r].push_back(p)
	return card_pool

func _ap_lbal_type_is_missing_item_v103(type_id):
	var t = str(type_id)
	return t.begins_with("ap_missing_item") or t == "item_missing" or t == "missing_item" or t == "ap_locked" or t == "locked"

func _ap_lbal_card_is_missing_item_v103(card):
	if card == null:
		return false
	if not "data" in card:
		return false
	if card.data == null:
		return false
	if typeof(card.data) == TYPE_DICTIONARY and card.data.has("type"):
		return _ap_lbal_type_is_missing_item_v103(card.data.type)
	return false

func _ap_lbal_force_all_visible_item_cards_missing_v103(cards, email, rarity = "common"):
	if typeof(cards) != TYPE_ARRAY:
		return false
	if email == null:
		return false
	var e = str(email.type)
	if e.find("item") < 0:
		return false

	var force_missing = false
	if _ap_lbal_should_filter("items") and not ap_live_has_item_targets_v92:
		force_missing = true

	for c in cards:
		if _ap_lbal_card_is_missing_item_v103(c):
			force_missing = true
			break

	if not force_missing:
		return false

	var use_rarity = str(rarity)
	if use_rarity == "" or use_rarity == "null" or use_rarity == "essence":
		use_rarity = "common"
	for c in cards:
		_ap_lbal_apply_forced_missing_item_card_v94(c, email, use_rarity)
	return true

func _ap_lbal_card_data_type_v104(data):
	if data == null:
		return ""
	if typeof(data) == TYPE_DICTIONARY:
		if data.has("type"):
			return str(data.type)
		if data.has("id"):
			return str(data.id)
		return ""
	if "type" in data:
		return str(data.type)
	if "id" in data:
		return str(data.id)
	return ""

func _ap_lbal_card_data_name_v104(data):
	if data == null:
		return ""
	if typeof(data) == TYPE_DICTIONARY:
		if data.has("display_name"):
			return str(data.display_name)
		if data.has("name"):
			return str(data.name)
		return ""
	if "display_name" in data:
		return str(data.display_name)
	if "name" in data:
		return str(data.name)
	return ""

func _ap_lbal_card_is_missing_item_v104(card):
	if card == null:
		return false
	if not "data" in card:
		return false
	var t = _ap_lbal_card_data_type_v104(card.data)
	if _ap_lbal_type_is_missing_item_v103(t):
		return true
	var n = _ap_lbal_card_data_name_v104(card.data).to_lower()
	return n.find("missing ap item") >= 0 or n.find("no possible ap item") >= 0 or n.find("missing item") >= 0

func _ap_lbal_force_all_visible_item_cards_missing_v104(cards, email, rarity = "common"):
	if typeof(cards) != TYPE_ARRAY:
		return false
	if email == null:
		return false
	var e = str(email.type)
	if e.find("item") < 0:
		return false

	var force_missing = false
	if _ap_lbal_should_filter("items") and not ap_live_has_item_targets_v92:
		force_missing = true

	for c in cards:
		if _ap_lbal_card_is_missing_item_v104(c):
			force_missing = true
			break

	if not force_missing:
		return false

	var use_rarity = str(rarity)
	if use_rarity == "" or use_rarity == "null" or use_rarity == "essence":
		use_rarity = "common"
	for c in cards:
		_ap_lbal_apply_forced_missing_item_card_v94(c, email, use_rarity)
	return true

func _ap_lbal_card_data_type_v105(card):
	if card == null:
		return ""
	var data = card.data
	if data == null:
		return ""
	if typeof(data) == TYPE_DICTIONARY:
		if data.has("type"):
			return str(data.type)
		if data.has("id"):
			return str(data.id)
		return ""
	# LBAL card.data normally exposes .type. Use direct access instead of
	# '"data" in card' because Object property checks were missing real cards.
	return str(data.type)

func _ap_lbal_card_data_label_v105(card):
	if card == null:
		return ""
	var data = card.data
	if data == null:
		return ""
	if typeof(data) == TYPE_DICTIONARY:
		if data.has("display_name"):
			return str(data.display_name)
		if data.has("name"):
			return str(data.name)
		if data.has("type"):
			return str(data.type)
		return ""
	var label = ""
	if "display_name" in data:
		label = str(data.display_name)
	elif "name" in data:
		label = str(data.name)
	else:
		label = str(data.type)
	return label

func _ap_lbal_card_is_missing_item_v105(card):
	var t = _ap_lbal_card_data_type_v105(card)
	if _ap_lbal_type_is_missing_item_v103(t):
		return true
	var label = _ap_lbal_card_data_label_v105(card).to_lower()
	return label.find("missing ap item") >= 0 or label.find("no possible ap item") >= 0 or label.find("missing item") >= 0

func _ap_lbal_force_cards_from_visible_missing_item_v105(cards, email, rarity = "common"):
	if typeof(cards) != TYPE_ARRAY:
		return false
	if email == null:
		return false
	if str(email.type).find("item") < 0:
		return false

	var missing_data = null
	for c in cards:
		if _ap_lbal_card_is_missing_item_v105(c):
			missing_data = c.data
			break

	if missing_data != null:
		for c in cards:
			c.data = missing_data
		return true

	# If the state definitely says no AP item target, create the placeholder even
	# if the visible Missing card was not detected for some reason.
	if _ap_lbal_should_filter("items") and not ap_live_has_item_targets_v92:
		var use_rarity = str(rarity)
		if use_rarity == "" or use_rarity == "null" or use_rarity == "essence":
			use_rarity = "common"
		for c in cards:
			_ap_lbal_apply_forced_missing_item_card_v94(c, email, use_rarity)
		return true

	return false

func _ap_lbal_force_exact_three_missing_item_cards_v106(cards, email, rarity = "common"):
	if typeof(cards) != TYPE_ARRAY:
		return false
	if email == null:
		return false
	if str(email.type).find("item") < 0:
		return false
	if not _ap_lbal_should_filter("items") or ap_live_has_item_targets_v92:
		return false
	var use_rarity = str(rarity)
	if use_rarity == "" or use_rarity == "null" or use_rarity == "essence":
		use_rarity = "common"
	var count = 0
	for c in cards:
		if count >= 3:
			break
		_ap_lbal_apply_forced_missing_item_card_variant_v107(c, email, use_rarity, count + 1)
		count += 1
	return true

func _ap_lbal_apply_forced_missing_item_card_variant_v107(card, email, rarity, index):
	var database = _ap_lbal_database_for_kind("items")
	var essence_only = false
	if email != null and "extra_values" in email:
		essence_only = _ap_lbal_extra_forces_essence(email.extra_values)
	var p = _ap_lbal_missing_placeholder_type_v107(true, essence_only, rarity, index)
	_ap_lbal_ensure_placeholder_database_entry_v65("items", p)
	if typeof(database) == TYPE_DICTIONARY and p != null and str(p) != "" and database.has(p):
		card.data = database[p]
		return true
	return _ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity)

func _ap_lbal_apply_forced_missing_item_card_variant_v109(card, email, rarity, index):
	var database = _ap_lbal_database_for_kind("items")
	var essence_only = false
	if email != null and "extra_values" in email:
		essence_only = _ap_lbal_extra_forces_essence(email.extra_values)
	var p = _ap_lbal_missing_placeholder_type_v107(true, essence_only, rarity, index)
	_ap_lbal_ensure_placeholder_database_entry_v65("items", p)
	if typeof(database) == TYPE_DICTIONARY and p != null and str(p) != "" and database.has(p):
		card.data = database[p]
		return true
	return _ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity)

func _ap_lbal_force_three_missing_item_cards_v109(cards, email, rarity = "common"):
	if typeof(cards) != TYPE_ARRAY:
		return false
	if email == null:
		return false
	if str(email.type).find("item") < 0:
		return false
	if not _ap_lbal_should_filter("items") or ap_live_has_item_targets_v92:
		return false
	var use_rarity = str(rarity)
	if use_rarity == "" or use_rarity == "null" or use_rarity == "essence":
		use_rarity = "common"
	var idx = 1
	for c in cards:
		if idx > 3:
			break
		_ap_lbal_apply_forced_missing_item_card_variant_v109(c, email, use_rarity, idx)
		idx += 1
	return true

func _ap_lbal_filter_card_pool(card_pool, email_type, extra_values = null):
	_ap_lbal_update_state(true)
	_ap_lbal_restore_original_descriptions_v59()
	if typeof(card_pool) != TYPE_DICTIONARY:
		return card_pool
	var choosing_items = _ap_lbal_guess_choosing_items_v93(email_type, card_pool)
	var forced_group = null
	if typeof(extra_values) == TYPE_DICTIONARY and extra_values.has("forced_group"):
		forced_group = extra_values.forced_group
	var essence_only_screen = choosing_items and _ap_lbal_extra_forces_essence(extra_values)
	var target_kind = "symbols"
	if choosing_items:
		target_kind = "items"
		if essence_only_screen:
			target_kind = "essences"
	# V93 hard gate: if this is an Add Item screen and the tracker has no item
	# target, do not allow the vanilla item pool at all. Essence targets do not
	# count for normal Add Item.
	if choosing_items and not essence_only_screen and _ap_lbal_should_filter("items") and not ap_live_has_item_targets_v92:
		return _ap_lbal_force_missing_item_pool_v93(card_pool, false)
	if choosing_items and essence_only_screen and _ap_lbal_should_filter("essences") and not ap_live_has_essence_targets_v92:
		return _ap_lbal_force_missing_item_pool_v93(card_pool, true)
	if choosing_items and _ap_lbal_should_filter(target_kind) and _ap_lbal_no_real_tracker_content_v91(target_kind):
		card_pool = _ap_lbal_strip_items_to_tracker_or_placeholder_v91(card_pool, target_kind, essence_only_screen)
		return card_pool
	if target_kind == "symbols" and _ap_lbal_no_real_tracker_symbols_v89():
		card_pool = _ap_lbal_strip_to_default_and_apcheck_v89(card_pool)
	if target_kind == "symbols" and not _ap_lbal_ap_check_pool_active():
		card_pool = _ap_lbal_remove_ap_check_from_card_pool_v70(card_pool)
	if not _ap_lbal_should_filter(target_kind) or _ap_lbal_boost_pool_empty_for_kind(target_kind):
		if _ap_lbal_card_pool_count(card_pool) <= 0:
			card_pool = _ap_lbal_backfill_card_pool_from_database_v68(card_pool, target_kind, forced_group)
		if target_kind == "symbols":
			if not _ap_lbal_ap_check_pool_active():
				card_pool = _ap_lbal_remove_ap_check_from_card_pool_v70(card_pool)
			else:
				card_pool = _ap_lbal_apply_ap_check_priority_v71(card_pool, forced_group)
			card_pool = _ap_lbal_fill_empty_symbol_rarities_v76(card_pool, forced_group)
			if _ap_lbal_no_real_tracker_symbols_v89():
				card_pool = _ap_lbal_strip_to_default_and_apcheck_v89(card_pool)
		if choosing_items:
			card_pool = _ap_lbal_strip_items_to_tracker_or_placeholder_v91(card_pool, target_kind, essence_only_screen)
		card_pool = _ap_lbal_remove_missing_symbol_cards_v79(card_pool)
		return card_pool
	if choosing_items:
		if essence_only_screen:
			card_pool = _ap_lbal_strip_items_to_tracker_or_placeholder_v91(card_pool, "essences", true)
			if not _ap_lbal_no_real_tracker_content_v91("essences"):
				card_pool = _ap_lbal_push_allowed_types_into_card_pool(card_pool, "essences")
			if _ap_lbal_card_pool_has_missing_item_v98(card_pool):
				card_pool = _ap_lbal_force_missing_item_choice_pool_v98(card_pool, "essence", true)
		else:
			card_pool = _ap_lbal_strip_items_to_tracker_or_placeholder_v91(card_pool, "items", false)
			if not _ap_lbal_no_real_tracker_content_v91("items"):
				card_pool = _ap_lbal_push_allowed_types_into_card_pool(card_pool, "items")
			# V98: source of truth. If Missing AP Item is present at all, this screen
			# has no possible AP item, so remove every vanilla item from every rarity.
			if _ap_lbal_card_pool_has_missing_item_v98(card_pool):
				card_pool = _ap_lbal_force_missing_item_choice_pool_v98(card_pool, "common", false)
	else:
		card_pool = _ap_lbal_push_allowed_types_into_card_pool(card_pool, "symbols", forced_group)
	if choosing_items and _ap_lbal_should_filter(target_kind) and _ap_lbal_no_real_tracker_content_v91(target_kind):
		return _ap_lbal_strip_items_to_tracker_or_placeholder_v91(card_pool, target_kind, essence_only_screen)
	for rarity in card_pool.keys():
		if typeof(card_pool[rarity]) != TYPE_ARRAY:
			continue
		var filtered = []
		for type_id in card_pool[rarity]:
			if choosing_items:
				var kind = _ap_lbal_item_kind(type_id)
				if essence_only_screen:
					if kind == "essences" and _ap_lbal_is_allowed("essences", type_id):
						filtered.push_back(_ap_lbal_database_type_for_kind_v83("essences", type_id))
				else:
					if kind != "essences" and _ap_lbal_is_allowed(kind, type_id):
						filtered.push_back(_ap_lbal_database_type_for_kind_v83("items", type_id))
			else:
				var symbol_type = _ap_lbal_canonical_symbol_type_v55(type_id)
				if symbol_type == "ap_check":
					if _ap_lbal_ap_check_pool_active() and not filtered.has("ap_check"):
						filtered.push_back("ap_check")
				elif _ap_lbal_symbol_matches_forced_group(symbol_type, forced_group) and _ap_lbal_is_allowed("symbols", symbol_type) and _ap_lbal_symbol_can_appear_in_rarity_v119(symbol_type, rarity):
					if not filtered.has(symbol_type):
						filtered.push_back(symbol_type)
		if essence_only_screen and str(rarity) != "essence":
			card_pool[rarity] = []
		else:
			card_pool[rarity] = filtered
	if target_kind == "symbols":
		if not _ap_lbal_ap_check_pool_active():
			card_pool = _ap_lbal_remove_ap_check_from_card_pool_v70(card_pool)
		else:
			card_pool = _ap_lbal_apply_ap_check_priority_v71(card_pool, forced_group)
		card_pool = _ap_lbal_fill_empty_symbol_rarities_v76(card_pool, forced_group)
		card_pool = _ap_lbal_remove_missing_symbol_cards_v79(card_pool)
		# V89: If tracker has no real symbol target and only AP Checks are open, the
		# Add Symbol screen must be exactly default symbols + AP Check. This removes
		# leaked common symbols such as Crab from old slot starting_symbols/card_pool.
		if _ap_lbal_no_real_tracker_symbols_v89():
			card_pool = _ap_lbal_strip_to_default_and_apcheck_v89(card_pool)
		return card_pool
	card_pool = _ap_lbal_fill_empty_rarities_with_placeholders(card_pool, choosing_items, essence_only_screen)
	return card_pool


# AP_DEATHLINK_PATCH_V12
func _ap_lbal_bridge_file_path(file_name):
	if OS.has_environment("LOCALAPPDATA"):
		return OS.get_environment("LOCALAPPDATA").replace("\\", "/") + "/LuckBeALandlordAP/" + str(file_name)
	return "user://" + str(file_name)

func _ap_lbal_write_file_text(path, text):
	var file = File.new()
	var err = file.open(path, File.WRITE)
	if err == OK:
		file.store_string(text)
		file.close()
		return true
	return false

func _ap_lbal_read_json_first(file_name):
	var paths = ["user://" + str(file_name), _ap_lbal_bridge_file_path(file_name)]
	var file = File.new()
	for path in paths:
		if not file.file_exists(path):
			continue
		var err = file.open(path, File.READ)
		if err != OK:
			continue
		var text = file.get_as_text()
		file.close()
		var data = parse_json(text)
		if typeof(data) == TYPE_DICTIONARY:
			return data
	return {}

# AP_PAYMENT_SEND_PATCH_V2
func _ap_lbal_queue_game_checks(location_names):
	# V161: merge with any existing bridge file instead of overwriting it.
	# This lets multiple AP Check symbols destroy in one spin and still send
	# AP Check 32, 33, 34... instead of only the last file write surviving.
	var clean = []
	var ap_next_count = 0
	if typeof(location_names) == TYPE_ARRAY:
		for location_name in location_names:
			var s = str(location_name)
			if s.to_lower() in ["ap_check_next", "next_ap_check", "ap check next", "ap check", "ap_check"]:
				ap_next_count += 1
			else:
				if not clean.has(s):
					clean.push_back(s)
	else:
		var single = str(location_names)
		if single.to_lower() in ["ap_check_next", "next_ap_check", "ap check next", "ap check", "ap_check"]:
			ap_next_count += 1
		else:
			clean.push_back(single)

	var paths = ["user://checks_to_send.json", _ap_lbal_bridge_file_path("checks_to_send.json")]
	var file = File.new()
	for path in paths:
		if not file.file_exists(path):
			continue
		var err = file.open(path, File.READ)
		if err != OK:
			continue
		var old_text = file.get_as_text()
		file.close()
		var old_data = parse_json(old_text)
		if typeof(old_data) == TYPE_DICTIONARY:
			if old_data.has("locations") and typeof(old_data["locations"]) == TYPE_ARRAY:
				for old_location in old_data["locations"]:
					var old_s = str(old_location)
					if old_s.to_lower() in ["ap_check_next", "next_ap_check", "ap check next", "ap check", "ap_check"]:
						ap_next_count += 1
					elif not clean.has(old_s):
						clean.push_back(old_s)
			if old_data.has("ap_check_next_count"):
				ap_next_count += int(old_data.get("ap_check_next_count", 0))
		elif typeof(old_data) == TYPE_ARRAY:
			for old_location2 in old_data:
				var old_s2 = str(old_location2)
				if old_s2.to_lower() in ["ap_check_next", "next_ap_check", "ap check next", "ap check", "ap_check"]:
					ap_next_count += 1
				elif not clean.has(old_s2):
					clean.push_back(old_s2)

	var nonce = str(OS.get_unix_time()) + "_" + str(randi())
	var payload = JSON.print({"locations": clean, "ap_check_next_count": ap_next_count, "source": "lbal_game", "nonce": nonce})
	_ap_lbal_write_file_text("user://checks_to_send.json", payload)
	_ap_lbal_write_file_text(_ap_lbal_bridge_file_path("checks_to_send.json"), payload)

func _ap_lbal_queue_game_check(location_name):
	_ap_lbal_queue_game_checks([str(location_name)])

func _ap_lbal_current_floor_for_payment():
	var floor_num = int(current_floor)
	if current_modded_floor != null and typeof(current_modded_floor) != TYPE_STRING:
		floor_num = int(current_modded_floor.floor_num)
	if floor_num < 1:
		floor_num = 1
	if floor_num > 20:
		floor_num = 20
	return floor_num

func _ap_lbal_write_run_state():
	var floor_num = _ap_lbal_current_floor_for_payment()
	var rent_due = 0
	if typeof(rent_values) == TYPE_ARRAY and rent_values.size() > 0:
		rent_due = int(rent_values[0])
	var payload = JSON.print({"floor": floor_num, "payment": int(times_rent_paid), "payments_paid": int(times_rent_paid), "spins_left": int(spins), "rent_due": rent_due, "source": "lbal_game", "nonce": str(OS.get_unix_time()) + "_" + str(randi())})
	_ap_lbal_write_file_text("user://lbal_run_state.json", payload)
	_ap_lbal_write_file_text(_ap_lbal_bridge_file_path("lbal_run_state.json"), payload)

func _ap_lbal_queue_payment_check(payment_num):
	var n = int(payment_num)
	if n >= 1 and n <= 12:
		var floor_num = _ap_lbal_current_floor_for_payment()
		_ap_lbal_write_run_state()
		var checks = ["Payment " + str(n)]
		# V87: only include the per-floor check if the AP state says that floor is
		# unlocked. This prevents locked floors from being queued every poll and
		# flooding the client with ignored-payment messages.
		var include_floor_check = true
		if typeof(ap_goal_floors) == TYPE_ARRAY and ap_goal_floors.size() > 0:
			include_floor_check = ap_goal_floors.has(floor_num) or ap_goal_floors.has(str(floor_num))
		if include_floor_check:
			checks.push_back("Floor " + str(floor_num) + " Payment " + str(n))
		_ap_lbal_queue_game_checks(checks)

func _ap_lbal_write_deathlink_send(cause):
	# Always write the request file. The AP client decides whether DeathLink is enabled.
	# This avoids stale ap_state blocking outgoing DeathLinks.
	_ap_lbal_update_state()
	var nonce = str(OS.get_unix_time()) + "_" + str(randi())
	var payload = JSON.print({"enabled": true, "cause": str(cause), "source": "lbal_game", "nonce": nonce, "enabled_in_game_state": ap_deathlink_enabled})
	_ap_lbal_write_file_text("user://deathlink_send.json", payload)
	_ap_lbal_write_file_text(_ap_lbal_bridge_file_path("deathlink_send.json"), payload)
	print("AP DeathLink send queued: " + str(cause))

func _ap_lbal_ack_deathlink(nonce):
	var payload = JSON.print({"nonce": str(nonce), "acknowledged_at": OS.get_unix_time()})
	_ap_lbal_write_file_text("user://deathlink_ack.json", payload)
	_ap_lbal_write_file_text(_ap_lbal_bridge_file_path("deathlink_ack.json"), payload)

func _ap_lbal_clear_popup_for_deathlink():
	for b in buttons:
		if is_instance_valid(b):
			if b.get_parent() != null:
				b.get_parent().remove_child(b)
			b.queue_free()
	buttons.clear()
	for c in cards:
		if is_instance_valid(c):
			if c.get_parent() != null:
				c.get_parent().remove_child(c)
			c.queue_free()
	cards.clear()
	emails.clear()
	saved_card_types.clear()
	visible = false
	border.visible = false
	container.visible = false
	sender_container.visible = false
	rent_container.visible = false
	label_text.visible = false
	scroll_bar.visible = false
	label_text.raw_string = ""
	displaying_inventory = false
	inv_open = false
	closed = false
	delay_timer = 0
	offset_y = $"/root/Main/Options Sprite/Options".resolution_y + 448

func _ap_lbal_force_deathlink_game_over(cause):
	if $"/root/Main/Title".visible:
		return false
	var main_v130 = get_node_or_null("/root/Main")
	if main_v130 != null and main_v130.has_method("_ap_lbal_main_mark_received_deathlink_gameover_v130"):
		main_v130._ap_lbal_main_mark_received_deathlink_gameover_v130()
	_ap_lbal_clear_popup_for_deathlink()
	$"/root/Main".write_log("GAME OVER - DeathLink: " + str(cause))
	$"/root/Main".save_log()
	add_event("game_over", {"push_front": true})
	delay_timer = 0
	if not visible:
		display()
	return true

func _ap_lbal_check_deathlink_receive():
	var now = OS.get_ticks_msec()
	if now < ap_deathlink_next_poll_msec:
		return false
	ap_deathlink_next_poll_msec = now + ap_deathlink_poll_interval_msec
	var data = _ap_lbal_read_json_first("deathlink_receive.json")
	if data.empty() or not bool(data.get("enabled", false)):
		return false
	var nonce = str(data.get("nonce", ""))
	if nonce == "" or nonce == ap_deathlink_last_nonce:
		return false
	ap_deathlink_last_nonce = nonce
	_ap_lbal_ack_deathlink(nonce)
	var cause = str(data.get("cause", "DeathLink received"))
	return _ap_lbal_force_deathlink_game_over(cause)

'''

MAIN_DEATHLINK_GDSCRIPT = r"""
# AP_DEATHLINK_MAIN_PATCH_V74
var ap_main_deathlink_last_nonce = ""
var ap_main_deathlink_poll_timer = 0.0
# AP_FAILED_PAYMENT_DEATHLINK_POLL_V130
var ap_main_failed_payment_sent_v130 = false
var ap_main_received_deathlink_suppress_until_v130 = 0
var ap_main_deathlink_last_write_msec_v131 = 0

func _ap_lbal_main_get_popup_email_type_v130(popup_node):
	if popup_node == null:
		return ""
	if not "emails" in popup_node:
		return ""
	if typeof(popup_node.emails) != TYPE_ARRAY or popup_node.emails.size() <= 0:
		return ""
	var email = popup_node.emails[0]
	if typeof(email) == TYPE_DICTIONARY:
		return str(email.get("type", ""))
	if "type" in email:
		return str(email.type)
	return ""

func _ap_lbal_main_mark_received_deathlink_gameover_v130():
	ap_main_received_deathlink_suppress_until_v130 = OS.get_ticks_msec() + 5000
	ap_main_failed_payment_sent_v130 = true

func _ap_lbal_main_poll_failed_payment_deathlink_v130(delta):
	if $"Title".visible:
		ap_main_failed_payment_sent_v130 = false
		return false
	var popup_node = get_node_or_null("Pop-up Sprite/Pop-up")
	if popup_node == null:
		ap_main_failed_payment_sent_v130 = false
		return false
	var email_type = _ap_lbal_main_get_popup_email_type_v130(popup_node)
	if email_type != "game_over" and email_type != "out_of_money":
		ap_main_failed_payment_sent_v130 = false
		return false
	if ap_main_failed_payment_sent_v130:
		return false
	if OS.get_ticks_msec() < ap_main_received_deathlink_suppress_until_v130:
		return false
	var rent_due = 0
	if "rent_values" in popup_node and typeof(popup_node.rent_values) == TYPE_ARRAY and popup_node.rent_values.size() > 0:
		rent_due = int(popup_node.rent_values[0])
	var money = 0
	if has_node("Coins"):
		money += int($"Coins".coins) + int($"Coins".queued_increase)
	if has_node("Sums/Coin Sum"):
		money += int($"Sums/Coin Sum".value)
	var spins_left = 999
	if "spins" in popup_node:
		spins_left = int(popup_node.spins)
	var is_failed_payment = email_type == "out_of_money" or spins_left <= 0 or (rent_due > 0 and money < rent_due)
	if not is_failed_payment:
		ap_main_failed_payment_sent_v130 = false
		return false
	ap_main_failed_payment_sent_v130 = true
	_ap_lbal_main_write_deathlink_send("Failed to pay rent in Luck be a Landlord")
	return true

func _ap_lbal_main_bridge_file_path(file_name):
	if OS.has_environment("LOCALAPPDATA"):
		return OS.get_environment("LOCALAPPDATA").replace("\\", "/") + "/LuckBeALandlordAP/" + str(file_name)
	return "user://" + str(file_name)

func _ap_lbal_main_write_file_text(path, text):
	var file = File.new()
	var err = file.open(path, File.WRITE)
	if err == OK:
		file.store_string(text)
		file.close()
		return true
	return false

func _ap_lbal_main_write_deathlink_send(cause):
	# V131: two-second buffer/debounce so multiple failure hooks do not rewrite
	# deathlink_send.json several times for one failed-payment screen.
	var now_msec_v131 = OS.get_ticks_msec()
	if now_msec_v131 - ap_main_deathlink_last_write_msec_v131 < 2000:
		return false
	ap_main_deathlink_last_write_msec_v131 = now_msec_v131
	var nonce = str(OS.get_unix_time()) + "_" + str(randi())
	var payload = JSON.print({"enabled": true, "cause": str(cause), "source": "main_game_over", "nonce": nonce})
	_ap_lbal_main_write_file_text("user://deathlink_send.json", payload)
	_ap_lbal_main_write_file_text(_ap_lbal_main_bridge_file_path("deathlink_send.json"), payload)
	print("AP DeathLink send queued from Main: " + str(cause))
	return true

func _ap_lbal_main_read_json_first(file_name):
	# Prefer bridge path first because the AP client writes there first.
	var paths = [_ap_lbal_main_bridge_file_path(file_name), "user://" + str(file_name)]
	var file = File.new()
	for path in paths:
		if not file.file_exists(path):
			continue
		var err = file.open(path, File.READ)
		if err != OK:
			continue
		var text = file.get_as_text()
		file.close()
		var data = parse_json(text)
		if typeof(data) == TYPE_DICTIONARY:
			return data
	return {}

func _ap_lbal_main_ack_deathlink(nonce):
	var payload = JSON.print({"nonce": str(nonce), "acknowledged_at": OS.get_unix_time(), "source": "main_process_v74"})
	_ap_lbal_main_write_file_text("user://deathlink_ack.json", payload)
	_ap_lbal_main_write_file_text(_ap_lbal_main_bridge_file_path("deathlink_ack.json"), payload)

func _ap_lbal_main_force_game_over_from_deathlink(cause):
	if $"Title".visible:
		return false
	_ap_lbal_main_mark_received_deathlink_gameover_v130()
	var popup = get_node_or_null("Pop-up Sprite/Pop-up")
	if popup == null:
		return false
	write_log("GAME OVER - DeathLink: " + str(cause))
	save_log()
	if popup.has_method("_ap_lbal_force_deathlink_game_over"):
		var ok = popup.call("_ap_lbal_force_deathlink_game_over", cause)
		if ok:
			return true
	# Fallback: force a game-over popup/event directly.
	popup.emails.clear()
	popup.cards.clear()
	popup.saved_card_types.clear()
	popup.add_event("game_over", {"push_front": true})
	popup.delay_timer = 0
	popup.closed = false
	popup.visible = true
	if popup.has_method("display"):
		popup.display()
	return true

func _ap_lbal_main_check_deathlink_receive():
	var data = _ap_lbal_main_read_json_first("deathlink_receive.json")
	if data.empty():
		return false
	var nonce = str(data.get("nonce", ""))
	if nonce == "" or nonce == ap_main_deathlink_last_nonce:
		return false
	var cause = str(data.get("cause", "DeathLink received"))
	if not _ap_lbal_main_force_game_over_from_deathlink(cause):
		return false
	ap_main_deathlink_last_nonce = nonce
	_ap_lbal_main_ack_deathlink(nonce)
	print("AP DeathLink applied from Main process: " + cause)
	return true

func _ap_lbal_main_poll_deathlink(delta):
	ap_main_deathlink_poll_timer += delta
	if ap_main_deathlink_poll_timer < 0.25:
		return
	ap_main_deathlink_poll_timer = 0.0
	_ap_lbal_main_check_deathlink_receive()
"""

MAIN_SAFE_ICON_GDSCRIPT_V60 = r"""
# AP_SAFE_ICON_LOAD_PATCH_V60
func _ap_lbal_has_large_numeric_suffix_v60(value):
	var clean = str(value).replace(".png", "").replace(".webp", "")
	var parts = clean.split("_")
	for part in parts:
		if part.length() >= 10:
			var all_digits = true
			for i in range(part.length()):
				var c = part[i]
				if c < "0" or c > "9":
					all_digits = false
					break
			if all_digits:
				return true
	return false

func _ap_lbal_safe_icon_load_v60(path, fallback_path):
	var p = str(path)
	var fallback = str(fallback_path)
	if _ap_lbal_has_large_numeric_suffix_v60(p):
		if ResourceLoader.exists(fallback):
			return load(fallback)
		return null
	if ResourceLoader.exists(p):
		var tex = load(p)
		if tex != null:
			return tex
	if ResourceLoader.exists(fallback):
		return load(fallback)
	return null

"""
MAIN_AP_OVERLAY_GDSCRIPT_V149 = r"""
# AP_INGAME_OVERLAY_PATCH_V158
var ap_main_overlay_poll_timer_v149 = 0.0
var ap_main_overlay_root_v149 = null
var ap_main_overlay_left_bg_v149 = null
var ap_main_overlay_right_bg_v149 = null
var ap_main_overlay_left_label_v149 = null
var ap_main_overlay_right_label_v149 = null

func _ap_lbal_overlay_nl_v158():
	return char(10)

func _ap_lbal_main_overlay_make_label_v149(label_name, bg, x, y, w, h):
	bg.name = label_name + " Background"
	bg.color = Color(0, 0, 0, 0.62)
	bg.rect_position = Vector2(x, y)
	bg.rect_size = Vector2(w, h)
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ap_main_overlay_root_v149.add_child(bg)

	var label = Label.new()
	label.name = label_name
	label.rect_position = Vector2(x + 8, y + 6)
	label.rect_size = Vector2(w - 16, h - 12)
	label.autowrap = true
	label.clip_text = true
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_color_override("font_color", Color(1, 1, 1, 1))
	label.add_color_override("font_color_shadow", Color(0, 0, 0, 1))
	label.add_constant_override("shadow_offset_x", 2)
	label.add_constant_override("shadow_offset_y", 2)
	ap_main_overlay_root_v149.add_child(label)
	return label

func _ap_lbal_main_overlay_ensure_v149():
	if ap_main_overlay_root_v149 != null and is_instance_valid(ap_main_overlay_root_v149):
		return

	ap_main_overlay_root_v149 = Control.new()
	ap_main_overlay_root_v149.name = "Archipelago In-Game Overlay"
	ap_main_overlay_root_v149.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(ap_main_overlay_root_v149)

	ap_main_overlay_left_bg_v149 = ColorRect.new()
	ap_main_overlay_right_bg_v149 = ColorRect.new()
	ap_main_overlay_left_label_v149 = _ap_lbal_main_overlay_make_label_v149("AP Client Text", ap_main_overlay_left_bg_v149, 8, 320, 330, 178)
	ap_main_overlay_right_label_v149 = _ap_lbal_main_overlay_make_label_v149("AP Stats Text", ap_main_overlay_right_bg_v149, 934, 320, 330, 246)
	_ap_lbal_main_overlay_layout_v149()

func _ap_lbal_main_overlay_layout_v149():
	if ap_main_overlay_root_v149 == null or not is_instance_valid(ap_main_overlay_root_v149):
		return
	var vp = get_viewport_rect().size
	var left_w = 330
	var left_h = 178
	var right_w = 330
	var right_h = 246
	var gap_above_bottom_ui = 72
	var left_x = 8
	var right_x = max(8, int(vp.x) - right_w - 8)
	var left_y = max(16, int(vp.y) - left_h - gap_above_bottom_ui)
	var right_y = max(16, int(vp.y) - right_h - gap_above_bottom_ui)

	ap_main_overlay_left_bg_v149.rect_position = Vector2(left_x, left_y)
	ap_main_overlay_left_bg_v149.rect_size = Vector2(left_w, left_h)
	ap_main_overlay_left_label_v149.rect_position = Vector2(left_x + 8, left_y + 6)
	ap_main_overlay_left_label_v149.rect_size = Vector2(left_w - 16, left_h - 12)

	ap_main_overlay_right_bg_v149.rect_position = Vector2(right_x, right_y)
	ap_main_overlay_right_bg_v149.rect_size = Vector2(right_w, right_h)
	ap_main_overlay_right_label_v149.rect_position = Vector2(right_x + 8, right_y + 6)
	ap_main_overlay_right_label_v149.rect_size = Vector2(right_w - 16, right_h - 12)

func _ap_lbal_fix_multiline_text_v157(value):
	var text = str(value)
	text = text.replace("\n", _ap_lbal_overlay_nl_v158())
	return text

func _ap_lbal_join_string_lines_v149(lines):
	var out = []
	if typeof(lines) == TYPE_ARRAY:
		for line in lines:
			var s = str(line)
			if s.begins_with("Queued check:"):
				continue
			out.push_back(s)
	return _ap_lbal_fix_multiline_text_v157(PoolStringArray(out).join(_ap_lbal_overlay_nl_v158()))

func _ap_lbal_main_poll_overlay_v149(delta):
	ap_main_overlay_poll_timer_v149 += delta
	if ap_main_overlay_poll_timer_v149 < 0.35:
		return
	ap_main_overlay_poll_timer_v149 = 0.0
	_ap_lbal_main_overlay_ensure_v149()
	_ap_lbal_main_overlay_layout_v149()

	var state = _ap_lbal_main_read_json_first("ap_state.json")
	if typeof(state) != TYPE_DICTIONARY:
		ap_main_overlay_left_label_v149.text = "Archipelago" + _ap_lbal_overlay_nl_v158() + "Waiting for client..."
		ap_main_overlay_right_label_v149.text = "AP Stats" + _ap_lbal_overlay_nl_v158() + "DeathLink in: ?" + _ap_lbal_overlay_nl_v158() + "Floors done: ?"
		return

	var overlay = state.get("overlay", {})
	if typeof(overlay) != TYPE_DICTIONARY or not bool(overlay.get("enabled", true)):
		ap_main_overlay_root_v149.visible = false
		return
	ap_main_overlay_root_v149.visible = true

	var left_lines = overlay.get("client_lines", [])
	var right_lines = overlay.get("right_lines", [])
	if typeof(left_lines) != TYPE_ARRAY:
		left_lines = []
	if typeof(right_lines) != TYPE_ARRAY:
		right_lines = []

	ap_main_overlay_left_label_v149.text = "Archipelago" + _ap_lbal_overlay_nl_v158() + _ap_lbal_join_string_lines_v149(left_lines)
	ap_main_overlay_right_label_v149.text = "AP Stats" + _ap_lbal_overlay_nl_v158() + _ap_lbal_join_string_lines_v149(right_lines)

"""





MAIN_AP_EFFECTS_GDSCRIPT_V139 = r"""
# AP_AP_EFFECTS_PATCH_V162
var ap_main_effect_poll_timer_v139 = 0.0
var ap_main_start_buffs_run_key_v160 = ""

func _ap_lbal_main_effect_applied_path_v139():
	return _ap_lbal_main_bridge_file_path("ap_effects_applied.json")

func _ap_lbal_main_read_applied_effects_v139():
	var file = File.new()
	var paths = [_ap_lbal_main_effect_applied_path_v139(), "user://ap_effects_applied.json"]
	for path in paths:
		if not file.file_exists(path):
			continue
		var err = file.open(path, File.READ)
		if err != OK:
			continue
		var text = file.get_as_text()
		file.close()
		var data = parse_json(text)
		if typeof(data) == TYPE_DICTIONARY:
			return data
	return {}

func _ap_lbal_main_write_applied_effects_v139(data):
	var text = JSON.print(data)
	_ap_lbal_main_write_file_text("user://ap_effects_applied.json", text)
	_ap_lbal_main_write_file_text(_ap_lbal_main_effect_applied_path_v139(), text)

func _ap_lbal_main_mark_force_payment_trap_v162():
	var payload = JSON.print({"source": "force_payment_trap", "created_at": OS.get_unix_time(), "nonce": str(OS.get_unix_time()) + "_" + str(randi())})
	_ap_lbal_main_write_file_text("user://force_payment_trap_active.json", payload)
	_ap_lbal_main_write_file_text(_ap_lbal_main_bridge_file_path("force_payment_trap_active.json"), payload)

func _ap_lbal_main_update_token_display_v160():
	var popup = get_node_or_null("Pop-up Sprite/Pop-up")
	if popup != null and popup.has_method("set_tip_values"):
		popup.set_tip_values()

func _ap_lbal_main_add_token_v160(kind, amount):
	var popup = get_node_or_null("Pop-up Sprite/Pop-up")
	if popup == null:
		return false
	var amt = max(0, int(amount))
	if amt <= 0:
		return true
	match str(kind):
		"reroll":
			if "reroll_tokens" in popup:
				popup.reroll_tokens += amt
				if has_node("Sums/Extra Sum"):
					$"Sums/Extra Sum".add_value(amt, 0, 0)
					$"Sums/Extra Sum".adding = true
				_ap_lbal_main_update_token_display_v160()
				return true
		"removal":
			if "removal_tokens" in popup:
				popup.removal_tokens += amt
				if has_node("Sums/Extra Sum"):
					$"Sums/Extra Sum".add_value(0, amt, 0)
					$"Sums/Extra Sum".adding = true
				_ap_lbal_main_update_token_display_v160()
				return true
		"essence":
			if "essence_tokens" in popup:
				popup.essence_tokens += amt
				if has_node("Sums/Extra Sum"):
					$"Sums/Extra Sum".add_value(0, 0, amt)
					$"Sums/Extra Sum".adding = true
				_ap_lbal_main_update_token_display_v160()
				return true
	return false

func _ap_lbal_main_apply_ap_effect_v139(effect_name, item_name):
	var popup = get_node_or_null("Pop-up Sprite/Pop-up")
	var coins_node = get_node_or_null("Coins")
	var items_node = get_node_or_null("Items")
	var reels_node = get_node_or_null("Reels")
	match str(effect_name):
		"start_destroy_token", "permanent_extra_destroy_token":
			if _ap_lbal_main_add_token_v160("removal", 1):
				print("AP Buff applied now: destroy token")
				return true
		"start_reroll_token", "permanent_extra_spin_token":
			if _ap_lbal_main_add_token_v160("reroll", 1):
				print("AP Buff applied now: reroll token")
				return true
		"start_essence_token":
			if _ap_lbal_main_add_token_v160("essence", 1):
				print("AP Buff applied now: essence token")
				return true
		"start_5_dollars":
			if coins_node != null and "coins" in coins_node:
				coins_node.coins += 5
				if "queued_increase" in coins_node:
					coins_node.queued_increase = 0
				if has_node("Sums/Coin Sum"):
					$"Sums/Coin Sum".value = 0
					$"Sums/Coin Sum".raw_string = ""
				print("AP Buff applied now: +5 coins")
				save_game()
				return true
		"choice_symbols":
			if items_node != null and items_node.has_method("add_item"):
				items_node.add_item("symbol_bomb_big")
				print("AP Buff applied now: Big Symbol Bomb")
				save_game()
				return true
			if popup != null:
				if "symbols_to_choose_from" in popup:
					popup.symbols_to_choose_from = max(int(popup.symbols_to_choose_from), 20)
				if "symbols_to_choose_from_from_mods" in popup:
					popup.symbols_to_choose_from_from_mods = max(int(popup.symbols_to_choose_from_from_mods), 17)
				print("AP Buff applied now: choice of symbols")
				return true
		"half_money":
			if coins_node != null and "coins" in coins_node:
				coins_node.coins = int(round(float(coins_node.coins) / 2.0))
				if has_node("Sums/Coin Sum"):
					$"Sums/Coin Sum".value = 0
					$"Sums/Coin Sum".raw_string = ""
				print("AP Trap applied: half money")
				save_game()
				return true
		"force_payment":
			if popup != null and "rent_values" in popup and typeof(popup.rent_values) == TYPE_ARRAY and popup.rent_values.size() > 1:
				popup.rent_values[1] = 0
				print("AP Trap applied: force payment")
				return true
		"add_dud_symbol":
			if has_node("Title") and $"Title".visible:
				print("AP Trap ignored: Dud trap received outside a run")
				return true
			if reels_node != null:
				if reels_node.has_method("add_tile"):
					reels_node.add_tile(["dud"])
					print("AP Trap applied: added Dud to current run")
					save_game()
					return true
				if "symbols" in reels_node and typeof(reels_node.symbols) == TYPE_ARRAY:
					reels_node.symbols.append("dud")
					print("AP Trap applied: appended Dud to current run")
					save_game()
					return true
			if popup != null:
				if "queued_symbols" in popup:
					popup.queued_symbols.push_back("dud")
				if popup.has_method("add_event"):
					popup.add_event("add_tile", {"after_spin": false})
				popup.delay_timer = 0
				print("AP Trap queued: Dud for current run")
				return true
			print("AP Trap ignored: could not find current run to add Dud")
			return true
		"set_money_to_1":
			if coins_node != null and "coins" in coins_node:
				coins_node.coins = 1
				save_game()
				return true
		"no_score_next_spin":
			if popup != null and "rent_values" in popup and typeof(popup.rent_values) == TYPE_ARRAY and popup.rent_values.size() > 1:
				popup.rent_values[1] = 0
				return true
	return false

func _ap_lbal_main_popup_email_type_v160(popup_node):
	if popup_node == null:
		return ""
	if has_method("_ap_lbal_main_get_popup_email_type_v130"):
		return str(_ap_lbal_main_get_popup_email_type_v130(popup_node))
	if not "emails" in popup_node:
		return ""
	if typeof(popup_node.emails) != TYPE_ARRAY or popup_node.emails.size() <= 0:
		return ""
	var email = popup_node.emails[0]
	if typeof(email) == TYPE_DICTIONARY:
		return str(email.get("type", ""))
	if "type" in email:
		return str(email.type)
	return ""

func _ap_lbal_main_current_run_key_v160(popup_node):
	if popup_node == null:
		return ""
	var key = ""
	if "total_runs" in popup_node:
		key += str(popup_node.total_runs)
	key += ":"
	if "run_timestamp" in popup_node:
		key += str(popup_node.run_timestamp)
	if key == ":":
		key = str(OS.get_ticks_msec())
	return key

func _ap_lbal_main_apply_persistent_start_buffs_v160(state):
	if has_node("Title") and $"Title".visible:
		ap_main_start_buffs_run_key_v160 = ""
		return false
	var popup = get_node_or_null("Pop-up Sprite/Pop-up")
	if popup == null:
		ap_main_start_buffs_run_key_v160 = ""
		return false
	var email_type = _ap_lbal_main_popup_email_type_v160(popup)
	if email_type == "game_over" or email_type == "out_of_money":
		ap_main_start_buffs_run_key_v160 = ""
		return false
	var run_key = _ap_lbal_main_current_run_key_v160(popup)
	if run_key == "" or run_key == ap_main_start_buffs_run_key_v160:
		return false
	var counts = state.get("ap_effect_counts", {})
	if typeof(counts) != TYPE_DICTIONARY:
		counts = {}
	var persistent = [
		["Buff: Start With a Destroy Token", "start_destroy_token"],
		["Buff: Start With $5", "start_5_dollars"],
		["Buff: Start With a Reroll Token", "start_reroll_token"],
		["Buff: Start With an Essence Token", "start_essence_token"],
		["Buff: Choice of Symbols", "choice_symbols"],
	]
	for entry in persistent:
		var item_name = str(entry[0])
		var effect_name = str(entry[1])
		var copies = int(counts.get(item_name, 0))
		for _i in range(max(copies, 0)):
			_ap_lbal_main_apply_ap_effect_v139(effect_name, item_name)
	ap_main_start_buffs_run_key_v160 = run_key
	return true

func _ap_lbal_main_poll_ap_effects_v139(delta):
	ap_main_effect_poll_timer_v139 += delta
	if ap_main_effect_poll_timer_v139 < 0.25:
		return
	ap_main_effect_poll_timer_v139 = 0.0
	var state = _ap_lbal_main_read_json_first("ap_state.json")
	if typeof(state) != TYPE_DICTIONARY:
		if has_node("Title") and $"Title".visible:
			ap_main_start_buffs_run_key_v160 = ""
		return
	_ap_lbal_main_apply_persistent_start_buffs_v160(state)
	if not state.has("ap_effects"):
		return
	var effects = state["ap_effects"]
	if typeof(effects) != TYPE_ARRAY:
		return
	var applied = _ap_lbal_main_read_applied_effects_v139()
	var changed = false
	for effect_data in effects:
		if typeof(effect_data) != TYPE_DICTIONARY:
			continue
		var idx = str(effect_data.get("index", ""))
		if idx == "" or applied.has(idx):
			continue
		var effect_name = str(effect_data.get("effect", ""))
		var item_name = str(effect_data.get("item_name", effect_name))
		if _ap_lbal_main_apply_ap_effect_v139(effect_name, item_name):
			applied[idx] = {"effect": effect_name, "item_name": item_name, "applied_at": OS.get_unix_time()}
			changed = true
	if changed:
		_ap_lbal_main_write_applied_effects_v139(applied)

"""




MAIN_AP_CHECK_GDSCRIPT = r"""
# AP_CHECK_SYMBOL_PATCH_V2
func _ap_lbal_bridge_file_path(file_name):
	if OS.has_environment("LOCALAPPDATA"):
		return OS.get_environment("LOCALAPPDATA").replace("\\", "/") + "/LuckBeALandlordAP/" + str(file_name)
	return "user://" + str(file_name)

func _ap_lbal_load_png_texture(path):
	var img = Image.new()
	var err = img.load(path)
	if err != OK:
		return null
	var texture = ImageTexture.new()
	texture.create_from_image(img)
	texture.set_flags(2)
	return texture

func _ap_lbal_register_ap_check_symbol():
	var ap_data = {}
	if tile_database.has("ap_check"):
		ap_data = tile_database["ap_check"].duplicate(true)
	ap_data["value"] = "3"
	ap_data["values"] = []
	ap_data["rarity"] = "common"
	ap_data["groups"] = []
	ap_data["sfx"] = []
	ap_data["modded"] = true
	ap_data["type"] = "ap_check"
	ap_data["display_name"] = "AP Check"
	ap_data["description"] = "Gives <icon_coin>3, then destroys itself and sends the next <color_800080>AP Check<end>."
	ap_data["localized_names"] = {}
	ap_data["localized_descriptions"] = {}
	ap_data["inherit_description"] = false
	ap_data["inherit_effects"] = true
	ap_data["inherit_art"] = false
	ap_data["inherit_groups"] = false
	ap_data["can_be_destroyed_before_rent"] = true
	ap_data["manually_destroyable"] = false
	tile_database["ap_check"] = ap_data
	if rarity_database.has("symbols") and rarity_database["symbols"].has("common") and not rarity_database["symbols"]["common"].has("ap_check"):
		rarity_database["symbols"]["common"].push_back("ap_check")
	if not base_types.symbols.has("ap_check"):
		base_types.symbols.push_back("ap_check")
	if not existing_symbols.has("ap_check"):
		existing_symbols["ap_check"] = "ap_check"
	var ap_texture = _ap_lbal_load_png_texture(_ap_lbal_bridge_file_path("ap_check.png"))
	if ap_texture == null:
		ap_texture = _ap_lbal_load_png_texture("user://ap_check.png")
	if ap_texture == null and icon_texture_database.has("missing"):
		ap_texture = icon_texture_database["missing"]
	if ap_texture != null:
		icon_texture_database["ap_check"] = ap_texture
"""

SLOT_AP_CHECK_GDSCRIPT = r"""
				# AP_CHECK_SYMBOL_PATCH_V2
				"ap_check":
					add_effect({"comparisons": [{"a": "type", "b": "ap_check"}], "anim": "shake", "anim_targets": [self], "value_to_change": "destroyed", "diff": true, "unconditional": true})
"""

SLOT_AP_CHECK_SEND_GDSCRIPT = r"""
# AP_CHECK_SEND_PATCH_V165
func _ap_lbal_ap_bridge_file_path(file_name):
	if OS.has_environment("LOCALAPPDATA"):
		return OS.get_environment("LOCALAPPDATA").replace("\\", "/") + "/LuckBeALandlordAP/" + str(file_name)
	return "user://" + str(file_name)

func _ap_lbal_write_file_text(path, text):
	var file = File.new()
	var err = file.open(path, File.WRITE)
	if err == OK:
		file.store_string(text)
		file.close()
		return true
	return false

func _ap_lbal_queue_next_ap_check():
	# V163: merge AP Check destroys instead of overwriting checks_to_send.json.
	# If 8 AP Check symbols destroy in one spin, the client receives
	# ap_check_next_count = 8 and sends AP Check N through N+7.
	var bridge_path = _ap_lbal_ap_bridge_file_path("checks_to_send.json")
	var target_path = bridge_path
	if str(target_path).begins_with("user://"):
		target_path = "user://checks_to_send.json"

	var clean = []
	var ap_next_count = 1
	var file = File.new()
	if file.file_exists(target_path):
		var err = file.open(target_path, File.READ)
		if err == OK:
			var old_text = file.get_as_text()
			file.close()
			var old_data = parse_json(old_text)
			if typeof(old_data) == TYPE_DICTIONARY:
				if old_data.has("locations") and typeof(old_data["locations"]) == TYPE_ARRAY:
					for old_location in old_data["locations"]:
						var old_s = str(old_location)
						if old_s.to_lower() in ["ap_check_next", "next_ap_check", "ap check next", "ap check", "ap_check", "ap_check_next"]:
							ap_next_count += 1
						elif not clean.has(old_s):
							clean.push_back(old_s)
				if old_data.has("ap_check_next_count"):
					ap_next_count += int(old_data.get("ap_check_next_count", 0))
			elif typeof(old_data) == TYPE_ARRAY:
				for old_location2 in old_data:
					var old_s2 = str(old_location2)
					if old_s2.to_lower() in ["ap_check_next", "next_ap_check", "ap check next", "ap check", "ap_check", "ap_check_next"]:
						ap_next_count += 1
					elif not clean.has(old_s2):
						clean.push_back(old_s2)

	var nonce = str(OS.get_unix_time()) + "_" + str(randi())
	var payload = JSON.print({"locations": clean, "ap_check_next_count": ap_next_count, "source": "ap_check", "nonce": nonce})
	_ap_lbal_write_file_text(target_path, payload)
"""


def _nl(text: str) -> str:
    # Some LBAL TSCN files have mixed newlines. The embedded script source is
    # usually LF inside Main.tscn, while Pop-up/Slot Icon are CRLF. Use the
    # dominant style so anchors match the script body we are patching.
    crlf = text.count("\r\n")
    lf = text.count("\n")
    return "\r\n" if crlf and crlf == lf else "\n"


def _with_nl(s: str, newline: str) -> str:
    return s.replace("\n", newline)




def _replace_gd_func(text: str, func_name: str, replacement: str, stop_before: str) -> str:
    start = text.find(f"func {func_name}(")
    if start == -1:
        return text
    end = text.find(stop_before, start)
    if end == -1:
        return text
    return text[:start] + replacement + text[end:]



def _upgrade_per_floor_payment_bridge_v23(text: str) -> str:
    """V23: queue both shared Payment N and Floor X Payment N using actual current_floor."""
    if "AP_PAYMENT_SEND_PATCH_V2" in text:
        return text
    replacement = """# AP_PAYMENT_SEND_PATCH_V2
func _ap_lbal_queue_game_checks(location_names):
\tvar clean = []
\tif typeof(location_names) == TYPE_ARRAY:
\t\tfor location_name in location_names:
\t\t\tif not clean.has(str(location_name)):
\t\t\t\tclean.push_back(str(location_name))
\telse:
\t\tclean.push_back(str(location_names))
\tvar nonce = str(OS.get_unix_time()) + "_" + str(randi())
\tvar payload = JSON.print({"locations": clean, "source": "lbal_game", "nonce": nonce})
\t_ap_lbal_write_file_text("user://checks_to_send.json", payload)
\t_ap_lbal_write_file_text(_ap_lbal_bridge_file_path("checks_to_send.json"), payload)

func _ap_lbal_queue_game_check(location_name):
\t_ap_lbal_queue_game_checks([str(location_name)])

func _ap_lbal_current_floor_for_payment():
\tvar floor_num = int(current_floor)
\tif current_modded_floor != null and typeof(current_modded_floor) != TYPE_STRING:
\t\tfloor_num = int(current_modded_floor.floor_num)
\tif floor_num < 1:
\t\tfloor_num = 1
\tif floor_num > 20:
\t\tfloor_num = 20
\treturn floor_num

func _ap_lbal_write_run_state():
\tvar floor_num = _ap_lbal_current_floor_for_payment()
\tvar rent_due = 0
\tif typeof(rent_values) == TYPE_ARRAY and rent_values.size() > 0:
\t\trent_due = int(rent_values[0])
\tvar payload = JSON.print({"floor": floor_num, "payment": int(times_rent_paid), "payments_paid": int(times_rent_paid), "spins_left": int(spins), "rent_due": rent_due, "source": "lbal_game", "nonce": str(OS.get_unix_time()) + "_" + str(randi())})
\t_ap_lbal_write_file_text("user://lbal_run_state.json", payload)
\t_ap_lbal_write_file_text(_ap_lbal_bridge_file_path("lbal_run_state.json"), payload)

func _ap_lbal_queue_payment_check(payment_num):
\tvar n = int(payment_num)
\tif n >= 1 and n <= 12:
\t\tvar floor_num = _ap_lbal_current_floor_for_payment()
\t\t_ap_lbal_write_run_state()
\t\t_ap_lbal_queue_game_checks(["Payment " + str(n), "Floor " + str(floor_num) + " Payment " + str(n)])

"""
    return _replace_gd_func(text, "_ap_lbal_queue_game_check", replacement, "func _ap_lbal_write_deathlink_send")


def _upgrade_deathlink_v1_popup_text(text: str) -> str:
    text = text.replace("AP_DEATHLINK_PATCH_V1", "AP_DEATHLINK_PATCH_V12")
    text = text.replace("AP_DEATHLINK_PATCH_V2", "AP_DEATHLINK_PATCH_V12")
    text = text.replace("AP_DEATHLINK_HOOK_PATCH_V1", "AP_DEATHLINK_HOOK_PATCH_V12")
    text = text.replace("AP_DEATHLINK_HOOK_PATCH_V2", "AP_DEATHLINK_HOOK_PATCH_V12")
    writer = '# AP_PAYMENT_SEND_PATCH_V1\nfunc _ap_lbal_queue_game_check(location_name):\n\tvar nonce = str(OS.get_unix_time()) + "_" + str(randi())\n\tvar payload = JSON.print({"locations": [str(location_name)], "source": "lbal_game", "nonce": nonce})\n\t_ap_lbal_write_file_text("user://checks_to_send.json", payload)\n\t_ap_lbal_write_file_text(_ap_lbal_bridge_file_path("checks_to_send.json"), payload)\n\nfunc _ap_lbal_queue_payment_check(payment_num):\n\tvar n = int(payment_num)\n\tif n >= 1 and n <= 12:\n\t\t_ap_lbal_queue_game_check("Payment " + str(n))\n\nfunc _ap_lbal_write_deathlink_send(cause):\n\t# Always write the request file. The AP client still decides whether to\n\t# actually send it based on the slot\'s DeathLink option. This fixes cases\n\t# where the game did not reload ap_state.json before the failure branch.\n\t_ap_lbal_update_state()\n\tvar nonce = str(OS.get_unix_time()) + "_" + str(randi())\n\tvar payload = JSON.print({"enabled": true, "cause": str(cause), "source": "lbal_game", "nonce": nonce, "enabled_in_game_state": ap_deathlink_enabled})\n\t_ap_lbal_write_file_text("user://deathlink_send.json", payload)\n\t_ap_lbal_write_file_text(_ap_lbal_bridge_file_path("deathlink_send.json"), payload)\n\tprint("AP DeathLink send queued: " + str(cause))\n\n'
    if "AP_PAYMENT_SEND_PATCH_V1" not in text:
        text = _replace_gd_func(text, "_ap_lbal_write_deathlink_send", writer, "func _ap_lbal_ack_deathlink")
    receiver = 'func _ap_lbal_clear_popup_for_deathlink():\n\tfor b in buttons:\n\t\tif is_instance_valid(b):\n\t\t\tif b.get_parent() != null:\n\t\t\t\tb.get_parent().remove_child(b)\n\t\t\tb.queue_free()\n\tbuttons.clear()\n\tfor c in cards:\n\t\tif is_instance_valid(c):\n\t\t\tif c.get_parent() != null:\n\t\t\t\tc.get_parent().remove_child(c)\n\t\t\tc.queue_free()\n\tcards.clear()\n\temails.clear()\n\tsaved_card_types.clear()\n\tvisible = false\n\tborder.visible = false\n\tcontainer.visible = false\n\tsender_container.visible = false\n\trent_container.visible = false\n\tlabel_text.visible = false\n\tscroll_bar.visible = false\n\tlabel_text.raw_string = ""\n\tdisplaying_inventory = false\n\tinv_open = false\n\tclosed = false\n\tdelay_timer = 0\n\toffset_y = $"/root/Main/Options Sprite/Options".resolution_y + 448\n\nfunc _ap_lbal_force_deathlink_game_over(cause):\n\tif $"/root/Main/Title".visible:\n\t\treturn false\n\t_ap_lbal_clear_popup_for_deathlink()\n\t$"/root/Main".write_log("GAME OVER - DeathLink: " + str(cause))\n\t$"/root/Main".save_log()\n\tadd_event("game_over", {"push_front": true})\n\tdelay_timer = 0\n\tif not visible:\n\t\tdisplay()\n\treturn true\n\nfunc _ap_lbal_check_deathlink_receive():\n\t_ap_lbal_update_state()\n\tif not ap_deathlink_enabled:\n\t\treturn false\n\tvar data = _ap_lbal_read_json_first("deathlink_receive.json")\n\tif data.empty() or not bool(data.get("enabled", false)):\n\t\treturn false\n\tvar nonce = str(data.get("nonce", ""))\n\tif nonce == "" or nonce == ap_deathlink_last_nonce:\n\t\treturn false\n\tap_deathlink_last_nonce = nonce\n\t_ap_lbal_ack_deathlink(nonce)\n\tvar cause = str(data.get("cause", "DeathLink received"))\n\treturn _ap_lbal_force_deathlink_game_over(cause)\n\n'
    if "_ap_lbal_force_deathlink_game_over" not in text:
        text = _replace_gd_func(text, "_ap_lbal_check_deathlink_receive", receiver, "var delay_timer = 0")
    payment_anchor_lf = "\t\t\t\t\t\ttimes_rent_paid += 1\n"
    payment_anchor_crlf = "\t\t\t\t\t\ttimes_rent_paid += 1\r\n"
    if "AP_PAYMENT_SEND_PATCH_V1" in text and "_ap_lbal_queue_payment_check(times_rent_paid)" not in text:
        if payment_anchor_crlf in text:
            text = text.replace(payment_anchor_crlf, payment_anchor_crlf + "\t\t\t\t\t\t_ap_lbal_queue_payment_check(times_rent_paid)\r\n", 1)
        elif payment_anchor_lf in text:
            text = text.replace(payment_anchor_lf, payment_anchor_lf + "\t\t\t\t\t\t_ap_lbal_queue_payment_check(times_rent_paid)\n", 1)
    return text

def _upgrade_item_choice_fallback_v18(text: str) -> str:
    """Upgrade already-patched PCKs so AP item choices do not fall through to item_missing
    and normal item screens do not pull essences into the same pool."""
    newline = _nl(text)

    # V18 pool-separation upgrades for already-patched embedded scene text.
    old_filter_type = _with_nl('\texpanded = _ap_lbal_push_allowed_types_into_type_array(expanded, \"items\", wanted_rarity)\n\texpanded = _ap_lbal_push_allowed_types_into_type_array(expanded, \"essences\", wanted_rarity)\n', newline)
    new_filter_type = _with_nl('\texpanded = _ap_lbal_push_allowed_types_into_type_array(expanded, \"items\", wanted_rarity)\n\tif str(wanted_rarity) == \"essence\":\n\t\texpanded = _ap_lbal_push_allowed_types_into_type_array(expanded, \"essences\", wanted_rarity)\n', newline)
    text = text.replace(old_filter_type, new_filter_type)

    old_filter_card = _with_nl('\tif choosing_items:\n\t\tcard_pool = _ap_lbal_push_allowed_types_into_card_pool(card_pool, \"items\")\n\t\tcard_pool = _ap_lbal_push_allowed_types_into_card_pool(card_pool, \"essences\")\n', newline)
    new_filter_card = _with_nl('\tif choosing_items:\n\t\tcard_pool = _ap_lbal_push_allowed_types_into_card_pool(card_pool, \"items\")\n', newline)
    text = text.replace(old_filter_card, new_filter_card)

    helper_anchor_old = 'func _ap_lbal_first_nonempty_rarity(card_pool):'
    helper_anchor_new = 'func _ap_lbal_first_nonempty_rarity(card_pool, include_essence = true):'
    if helper_anchor_old in text:
        text = text.replace(helper_anchor_old, helper_anchor_new)
    text = text.replace('\tvar rarity_order = [\"common\", \"uncommon\", \"rare\", \"very_rare\", \"essence\", \"none\"]\n\tfor rarity in rarity_order:\n\t\tif card_pool.has(rarity) and typeof(card_pool[rarity]) == TYPE_ARRAY and card_pool[rarity].size() > 0:\n\t\t\treturn rarity\n\tfor rarity in card_pool.keys():\n\t\tif typeof(card_pool[rarity]) == TYPE_ARRAY and card_pool[rarity].size() > 0:\n\t\t\treturn rarity\n',
                        '\tvar rarity_order = [\"common\", \"uncommon\", \"rare\", \"very_rare\", \"essence\", \"none\"]\n\tfor rarity in rarity_order:\n\t\tif rarity == \"essence\" and not include_essence:\n\t\t\tcontinue\n\t\tif card_pool.has(rarity) and typeof(card_pool[rarity]) == TYPE_ARRAY and card_pool[rarity].size() > 0:\n\t\t\treturn rarity\n\tfor rarity in card_pool.keys():\n\t\tif rarity == \"essence\" and not include_essence:\n\t\t\tcontinue\n\t\tif typeof(card_pool[rarity]) == TYPE_ARRAY and card_pool[rarity].size() > 0:\n\t\t\treturn rarity\n')

    if 'AP_ITEM_RARITY_FALLBACK_PATCH_V18' not in text:
        helper_gd = 'func _ap_lbal_first_nonempty_rarity(card_pool, include_essence = true):\n\t# AP_ITEM_RARITY_FALLBACK_PATCH_V18\n\t# LBAL normally rolls a rarity first. If the AP filter leaves only rare/uncommon\n\t# items and the normal roll lands on common, vanilla falls through to item_missing.\n\t# Pick any non-empty AP-filtered rarity instead so unlocks like Lemon/Triple Coins appear,\n\t# but keep essences out of normal add-item screens.\n\tif typeof(card_pool) != TYPE_DICTIONARY:\n\t\treturn null\n\tvar rarity_order = [\"common\", \"uncommon\", \"rare\", \"very_rare\", \"essence\", \"none\"]\n\tfor rarity in rarity_order:\n\t\tif rarity == \"essence\" and not include_essence:\n\t\t\tcontinue\n\t\tif card_pool.has(rarity) and typeof(card_pool[rarity]) == TYPE_ARRAY and card_pool[rarity].size() > 0:\n\t\t\treturn rarity\n\tfor rarity in card_pool.keys():\n\t\tif rarity == \"essence\" and not include_essence:\n\t\t\tcontinue\n\t\tif typeof(card_pool[rarity]) == TYPE_ARRAY and card_pool[rarity].size() > 0:\n\t\t\treturn rarity\n\treturn null\n\n'
        helper_text = _with_nl(_escaped_gd(helper_gd), newline)
        helper_anchor = _with_nl('func _ap_lbal_backfill_symbol_pool_if_needed(card_pool):\n', newline)
        if helper_anchor in text:
            text = text.replace(helper_anchor, helper_text + helper_anchor, 1)

    # Replace any older V16-style fallback block with the V18 version.
    old_block = _with_nl('\t\t\t\t# AP_ITEM_RARITY_SELECT_PATCH_V16\n\t\t\t\tif email.type == \"add_item\":\n\t\t\t\t\tif rarity == null or not card_pool.has(rarity) or card_pool[rarity].size() == 0:\n\t\t\t\t\t\trarity = _ap_lbal_first_nonempty_rarity(card_pool)\n', newline)
    new_block = _with_nl('\t\t\t\t# AP_ITEM_RARITY_SELECT_PATCH_V18\n\t\t\t\tif email.type == \"add_item\":\n\t\t\t\t\tvar ap_allow_essence_fallback = false\n\t\t\t\t\tif c < forced_rarity_arr.size() and str(forced_rarity_arr[c]) == \\\"essence\\\":\n\t\t\t\t\t\tap_allow_essence_fallback = true\n\t\t\t\t\tif rarity == null or not card_pool.has(rarity) or card_pool[rarity].size() == 0:\n\t\t\t\t\t\trarity = _ap_lbal_first_nonempty_rarity(card_pool, ap_allow_essence_fallback)\n', newline)
    text = text.replace(old_block, new_block)

    if 'AP_ITEM_RARITY_SELECT_PATCH_V18' not in text:
        randomize_anchor = _with_nl('\t\t\t\tif c < forced_rarity_arr.size() and email.extra_values.has(\"or_better\") and email.extra_values.or_better:\n\t\t\t\t\tvar rarity_order = [\"common\", \"uncommon\", \"rare\", \"very_rare\"]\n\t\t\t\t\tif rarity_order.find(forced_rarity_arr[c]) > rarity_order.find(rarity):\n\t\t\t\t\t\trarity = forced_rarity_arr[c]\n\t\t\t\trandomize()\n', newline)
        item_fallback = _with_nl('\t\t\t\tif c < forced_rarity_arr.size() and email.extra_values.has(\"or_better\") and email.extra_values.or_better:\n\t\t\t\t\tvar rarity_order = [\"common\", \"uncommon\", \"rare\", \"very_rare\"]\n\t\t\t\t\tif rarity_order.find(forced_rarity_arr[c]) > rarity_order.find(rarity):\n\t\t\t\t\t\trarity = forced_rarity_arr[c]\n\t\t\t\t# AP_ITEM_RARITY_SELECT_PATCH_V18\n\t\t\t\tif email.type == \"add_item\":\n\t\t\t\t\tvar ap_allow_essence_fallback = false\n\t\t\t\t\tif c < forced_rarity_arr.size() and str(forced_rarity_arr[c]) == \\\"essence\\\":\n\t\t\t\t\t\tap_allow_essence_fallback = true\n\t\t\t\t\tif rarity == null or not card_pool.has(rarity) or card_pool[rarity].size() == 0:\n\t\t\t\t\t\trarity = _ap_lbal_first_nonempty_rarity(card_pool, ap_allow_essence_fallback)\n\t\t\t\trandomize()\n', newline)
        if randomize_anchor in text:
            text = text.replace(randomize_anchor, item_fallback, 1)
    return text


def _replace_popup_live_block_v19(text: str) -> str:
    newline = _nl(text)
    gd = _with_nl(_escaped_gd(LIVE_GDSCRIPT), newline)
    pattern = r"# AP_LIVE_POOL_PATCH_V\d+.*?func _ap_lbal_check_deathlink_receive\(\):.*?\r?\n\treturn _ap_lbal_force_deathlink_game_over\(cause\)\r?\n"
    text, _count = re.subn(pattern, lambda _m: gd, text, count=1, flags=re.S)
    return text


def _upgrade_v19_popup_text(text: str) -> str:
    newline = _nl(text)
    text = _replace_popup_live_block_v19(text)
    # V21: split Item and Essence choice screens completely. If the generated
    # PCK already has the V19 fallback block, upgrade it here.
    old_v19_block = _with_nl('\t\t\t\t# AP_ITEM_RARITY_SELECT_PATCH_V21\n\t\t\t\tif email.type == \"add_item\":\n\t\t\t\t\tvar ap_allow_essence_fallback = false\n\t\t\t\t\tif c < forced_rarity_arr.size() and str(forced_rarity_arr[c]) == \\\"essence\\\":\n\t\t\t\t\t\tap_allow_essence_fallback = true\n\t\t\t\t\tif rarity == null or not card_pool.has(rarity) or card_pool[rarity].size() == 0:\n\t\t\t\t\t\trarity = _ap_lbal_first_nonempty_rarity(card_pool, ap_allow_essence_fallback)\n', newline)
    new_v21_block = _with_nl('\t\t\t\t# AP_ITEM_RARITY_SELECT_PATCH_V21\n\t\t\t\tif email.type == \"add_item\":\n\t\t\t\t\tvar ap_allow_essence_fallback = _ap_lbal_extra_forces_essence(email.extra_values)\n\t\t\t\t\tif rarity == null or not card_pool.has(rarity) or card_pool[rarity].size() == 0:\n\t\t\t\t\t\trarity = _ap_lbal_first_nonempty_rarity(card_pool, ap_allow_essence_fallback)\n', newline)
    text = text.replace(old_v19_block, new_v21_block)
    text = text.replace(
        _with_nl('\t\tcard_pool = _ap_lbal_filter_card_pool(card_pool, email.type)\n', newline),
        _with_nl('\t\tcard_pool = _ap_lbal_filter_card_pool(card_pool, email.type, email.extra_values)\n', newline),
    )
    for marker in ("V16", "V18"):
        old = _with_nl(f'\t\t\t\t# AP_ITEM_RARITY_SELECT_PATCH_{marker}\n\t\t\t\tif email.type == \\"add_item\\":\n\t\t\t\t\tif rarity == null or not card_pool.has(rarity) or card_pool[rarity].size() == 0:\n\t\t\t\t\t\trarity = _ap_lbal_first_nonempty_rarity(card_pool)\n', newline)
        new = _with_nl('\t\t\t\t# AP_ITEM_RARITY_SELECT_PATCH_V21\n\t\t\t\tif email.type == \\"add_item\\":\n\t\t\t\t\tvar ap_allow_essence_fallback = false\n\t\t\t\t\tif c < forced_rarity_arr.size() and str(forced_rarity_arr[c]) == \\"essence\\":\n\t\t\t\t\t\tap_allow_essence_fallback = true\n\t\t\t\t\tif rarity == null or not card_pool.has(rarity) or card_pool[rarity].size() == 0:\n\t\t\t\t\t\trarity = _ap_lbal_first_nonempty_rarity(card_pool, ap_allow_essence_fallback)\n', newline)
        text = text.replace(old, new)
    if "AP_ITEM_RARITY_SELECT_PATCH_V21" not in text:
        randomize_anchor = _with_nl('\t\t\t\tif c < forced_rarity_arr.size() and email.extra_values.has(\\"or_better\\") and email.extra_values.or_better:\n\t\t\t\t\tvar rarity_order = [\\"common\\", \\"uncommon\\", \\"rare\\", \\"very_rare\\"]\n\t\t\t\t\tif rarity_order.find(forced_rarity_arr[c]) > rarity_order.find(rarity):\n\t\t\t\t\t\trarity = forced_rarity_arr[c]\n\t\t\t\trandomize()\n', newline)
        item_fallback = _with_nl('\t\t\t\tif c < forced_rarity_arr.size() and email.extra_values.has(\\"or_better\\") and email.extra_values.or_better:\n\t\t\t\t\tvar rarity_order = [\\"common\\", \\"uncommon\\", \\"rare\\", \\"very_rare\\"]\n\t\t\t\t\tif rarity_order.find(forced_rarity_arr[c]) > rarity_order.find(rarity):\n\t\t\t\t\t\trarity = forced_rarity_arr[c]\n\t\t\t\t# AP_ITEM_RARITY_SELECT_PATCH_V21\n\t\t\t\tif email.type == \\"add_item\\":\n\t\t\t\t\tvar ap_allow_essence_fallback = false\n\t\t\t\t\tif c < forced_rarity_arr.size() and str(forced_rarity_arr[c]) == \\"essence\\":\n\t\t\t\t\t\tap_allow_essence_fallback = true\n\t\t\t\t\tif rarity == null or not card_pool.has(rarity) or card_pool[rarity].size() == 0:\n\t\t\t\t\t\trarity = _ap_lbal_first_nonempty_rarity(card_pool, ap_allow_essence_fallback)\n\t\t\t\trandomize()\n', newline)
        text = text.replace(randomize_anchor, item_fallback, 1)
    return text

def _force_v21_essence_fallback_text(text: str) -> str:
    newline = _nl(text)
    # Replace the old per-card check. It let a mixed forced_rarity array pull one
    # Essence card into a normal Add Item screen. V21 only allows essence fallback
    # when _all_ forced rarities are essence.
    old_escaped = _with_nl('\t\t\t\t\tvar ap_allow_essence_fallback = false\n\t\t\t\t\tif c < forced_rarity_arr.size() and str(forced_rarity_arr[c]) == \\\"essence\\\":\n\t\t\t\t\t\tap_allow_essence_fallback = true\n', newline)
    new_escaped = _with_nl('\t\t\t\t\tvar ap_allow_essence_fallback = _ap_lbal_extra_forces_essence(email.extra_values)\n', newline)
    text = text.replace(old_escaped, new_escaped)
    old_plain = _with_nl('\t\t\t\t\tvar ap_allow_essence_fallback = false\n\t\t\t\t\tif c < forced_rarity_arr.size() and str(forced_rarity_arr[c]) == "essence":\n\t\t\t\t\t\tap_allow_essence_fallback = true\n', newline)
    new_plain = _with_nl('\t\t\t\t\tvar ap_allow_essence_fallback = _ap_lbal_extra_forces_essence(email.extra_values)\n', newline)
    text = text.replace(old_plain, new_plain)
    return text


def _upgrade_vanilla_effect_references_v22(text: str) -> str:
    """V22: keep vanilla effect descriptions and effect lookup IDs using the real vanilla IDs.

    AP unlock display names may contain spaces/capital letters, but LBAL effect text and
    destroy-target lookups need the internal symbol IDs. This fixes cards like Dwarven
    Anvil showing a question mark target even when Ore is unlocked, and restores vanilla
    destroy pair wording such as Dwarf + Wine.
    """
    newline = _nl(text)

    # Fix any accidental AP display-name substitutions that can break vanilla effect text.
    replacements = {
        "Wine": "wine",
        "Beer": "beer",
        "Ore": "ore",
        "Big Ore": "big_ore",
        "Dwarf": "dwarf",
        "Dwarven Anvil": "dwarven_anvil",
        "Dwarven Anvil Essence": "dwarven_anvil_essence",
    }

    for pretty, internal in replacements.items():
        # Only replace inside common symbolic lookup patterns, not card titles.
        text = text.replace(f'has(\\"{pretty}\\")', f'has(\\"{internal}\\")')
        text = text.replace(f'has("{pretty}")', f'has("{internal}")')
        text = text.replace(f'[\\"{pretty}\\"]', f'[\\"{internal}\\"]')
        text = text.replace(f'["{pretty}"]', f'["{internal}"]')
        text = text.replace(f'type == \\"{pretty}\\"', f'type == \\"{internal}\\"')
        text = text.replace(f'type == "{pretty}"', f'type == "{internal}"')
        text = text.replace(f'type != \\"{pretty}\\"', f'type != \\"{internal}\\"')
        text = text.replace(f'type != "{pretty}"', f'type != "{internal}"')

    # Some previous experimental patches could turn AP's question-mark placeholder into
    # a real effect target in descriptions. Force known vanilla Dwarven Anvil targets.
    text = text.replace('\\"dwarven_anvil\\", \\"?\\")', '\\"dwarven_anvil\\", \\"ore\\")')
    text = text.replace('"dwarven_anvil", "?")', '"dwarven_anvil", "ore")')
    text = text.replace('\\"dwarven_anvil_essence\\", \\"?\\")', '\\"dwarven_anvil_essence\\", \\"ore\\")')
    text = text.replace('"dwarven_anvil_essence", "?")', '"dwarven_anvil_essence", "ore")')

    return text


def _upgrade_essence_only_selection_v26(text: str) -> str:
    """V26: forced Essence reward screens must never mix normal items."""
    newline = _nl(text)

    helper_gd = """func _ap_lbal_first_nonempty_rarity(card_pool, essence_only = false):
	# AP_ITEM_RARITY_FALLBACK_PATCH_V26
	if typeof(card_pool) != TYPE_DICTIONARY:
		return null
	if essence_only:
		if card_pool.has("essence") and typeof(card_pool["essence"]) == TYPE_ARRAY and card_pool["essence"].size() > 0:
			return "essence"
		return null
	var rarity_order = ["common", "uncommon", "rare", "very_rare", "none"]
	for rarity in rarity_order:
		if card_pool.has(rarity) and typeof(card_pool[rarity]) == TYPE_ARRAY and card_pool[rarity].size() > 0:
			return rarity
	for rarity in card_pool.keys():
		if rarity == "essence":
			continue
		if typeof(card_pool[rarity]) == TYPE_ARRAY and card_pool[rarity].size() > 0:
			return rarity
	return null

func _ap_lbal_vanilla_rarity_for_current_screen(choosing_items):
	# AP_VANILLA_RARITY_TABLE_V47
	var paid = int(times_rent_paid)
	var common = 1000
	var uncommon = 0
	var rare = 0
	var very_rare = 0
	if choosing_items:
		if paid <= 0:
			common = 1000; uncommon = 0; rare = 0; very_rare = 0
		elif paid == 1:
			common = 900; uncommon = 100; rare = 0; very_rare = 0
		elif paid == 2:
			common = 790; uncommon = 200; rare = 10; very_rare = 0
		elif paid == 3:
			common = 740; uncommon = 250; rare = 10; very_rare = 0
		elif paid == 4:
			common = 690; uncommon = 290; rare = 15; very_rare = 5
		else:
			common = 680; uncommon = 300; rare = 15; very_rare = 5
	else:
		if paid <= 0:
			common = 1000; uncommon = 0; rare = 0; very_rare = 0
		elif paid == 1:
			common = 900; uncommon = 100; rare = 0; very_rare = 0
		elif paid == 2:
			common = 790; uncommon = 200; rare = 10; very_rare = 0
		elif paid == 3:
			common = 740; uncommon = 250; rare = 10; very_rare = 0
		elif paid == 4:
			common = 690; uncommon = 290; rare = 15; very_rare = 5
		elif paid == 5:
			common = 680; uncommon = 300; rare = 15; very_rare = 5
		else:
			common = 600; uncommon = 350; rare = 35; very_rare = 15
	var roll = randi() % 1000
	if roll < common:
		return "common"
	roll -= common
	if roll < uncommon:
		return "uncommon"
	roll -= uncommon
	if roll < rare:
		return "rare"
	return "very_rare"

func _ap_lbal_missing_placeholder_type(choosing_items, essence_only, rarity):
	var r = str(rarity)
	if essence_only or r == "essence":
		return "ap_missing_item_essence"
	if r != "common" and r != "uncommon" and r != "rare" and r != "very_rare":
		r = "common"
	if choosing_items:
		return "ap_missing_item_" + r
	# V76: Missing AP Symbol should not appear in Add Symbol choices.
	return ""

func _ap_lbal_add_missing_placeholder_to_rarity(card_pool, choosing_items, essence_only, rarity):
	if typeof(card_pool) != TYPE_DICTIONARY:
		return card_pool
	var r = str(rarity)
	if r == "" or r == "null":
		r = _ap_lbal_vanilla_rarity_for_current_screen(choosing_items)
	if not card_pool.has(r) or typeof(card_pool[r]) != TYPE_ARRAY:
		card_pool[r] = []
	if card_pool[r].size() > 0:
		return card_pool
	var kind = "symbols"
	if choosing_items:
		if essence_only or r == "essence":
			kind = "essences"
		else:
			kind = "items"
	if not _ap_lbal_should_filter(kind) or _ap_lbal_boost_pool_empty_for_kind(kind):
		return card_pool
	var database = _ap_lbal_database_for_kind(kind)
	var placeholder = _ap_lbal_missing_placeholder_type(choosing_items, essence_only, r)
	if database.has(placeholder):
		card_pool[r].push_back(placeholder)
	return card_pool

func _ap_lbal_fill_empty_rarities_with_placeholders(card_pool, choosing_items, essence_only):
	if essence_only:
		return _ap_lbal_add_missing_placeholder_to_rarity(card_pool, choosing_items, true, "essence")
	var rarity_order = ["common", "uncommon", "rare", "very_rare"]
	for r in rarity_order:
		card_pool = _ap_lbal_add_missing_placeholder_to_rarity(card_pool, choosing_items, false, r)
	return card_pool

"""
    text, _ = re.subn(
        r"func _ap_lbal_first_nonempty_rarity\(card_pool, (?:include_essence|essence_only) = (?:true|false)\):.*?\r?\n\treturn null\r?\n",
        _with_nl(_escaped_gd(helper_gd), newline),
        text,
        count=1,
        flags=re.S,
    )

    filter_gd = """func _ap_lbal_filter_card_pool(card_pool, email_type, extra_values = null):
	_ap_lbal_update_state(true)
	if typeof(card_pool) != TYPE_DICTIONARY:
		return card_pool
	var choosing_items = _ap_lbal_guess_choosing_items_v93(email_type, card_pool)
	var forced_group = null
	if typeof(extra_values) == TYPE_DICTIONARY and extra_values.has("forced_group"):
		forced_group = extra_values.forced_group
	var essence_only_screen = choosing_items and _ap_lbal_extra_forces_essence(extra_values)
	var target_kind = "symbols"
	if choosing_items:
		target_kind = "items"
		if essence_only_screen:
			target_kind = "essences"
	if choosing_items and not essence_only_screen and _ap_lbal_should_filter("items") and not ap_live_has_item_targets_v92:
		return _ap_lbal_force_missing_item_pool_v93(card_pool, false)
	if choosing_items and essence_only_screen and _ap_lbal_should_filter("essences") and not ap_live_has_essence_targets_v92:
		return _ap_lbal_force_missing_item_pool_v93(card_pool, true)
	if not _ap_lbal_should_filter(target_kind) or _ap_lbal_boost_pool_empty_for_kind(target_kind):
		if _ap_lbal_card_pool_count(card_pool) <= 0:
			card_pool = _ap_lbal_backfill_card_pool_from_database_v68(card_pool, target_kind, forced_group)
		return card_pool
	if choosing_items:
		if essence_only_screen:
			card_pool = _ap_lbal_push_allowed_types_into_card_pool(card_pool, "essences")
		else:
			card_pool = _ap_lbal_push_allowed_types_into_card_pool(card_pool, "items")
	else:
		card_pool = _ap_lbal_push_allowed_types_into_card_pool(card_pool, "symbols", forced_group)
	for rarity in card_pool.keys():
		if typeof(card_pool[rarity]) != TYPE_ARRAY:
			continue
		var filtered = []
		for type_id in card_pool[rarity]:
			if choosing_items:
				var kind = _ap_lbal_item_kind(type_id)
				if essence_only_screen:
					if kind == "essences" and _ap_lbal_is_allowed("essences", type_id):
						filtered.push_back(type_id)
				else:
					if kind != "essences" and _ap_lbal_is_allowed(kind, type_id):
						filtered.push_back(type_id)
			else:
				if _ap_lbal_symbol_matches_forced_group(type_id, forced_group) and _ap_lbal_is_allowed("symbols", type_id):
					filtered.push_back(type_id)
		if essence_only_screen and str(rarity) != "essence":
			card_pool[rarity] = []
		else:
			card_pool[rarity] = filtered
	if target_kind == "symbols":
		if not _ap_lbal_ap_check_pool_active():
			card_pool = _ap_lbal_remove_ap_check_from_card_pool_v70(card_pool)
		else:
			card_pool = _ap_lbal_apply_ap_check_priority_v71(card_pool, forced_group)
		card_pool = _ap_lbal_fill_empty_symbol_rarities_v76(card_pool, forced_group)
		card_pool = _ap_lbal_remove_missing_symbol_cards_v79(card_pool)
		return card_pool
	card_pool = _ap_lbal_fill_empty_rarities_with_placeholders(card_pool, choosing_items, essence_only_screen)
	return card_pool

"""
    text, _ = re.subn(
        r"func _ap_lbal_filter_card_pool\(card_pool, email_type, extra_values = null\):.*?\r?\n\treturn card_pool\r?\n",
        _with_nl(_escaped_gd(filter_gd), newline),
        text,
        count=1,
        flags=re.S,
    )

    text = text.replace(
        _with_nl('\t\tcard_pool = _ap_lbal_filter_card_pool(card_pool, email.type)\n', newline),
        _with_nl('\t\tcard_pool = _ap_lbal_filter_card_pool(card_pool, email.type, email.extra_values)\n', newline),
    )

    if "AP_ITEM_RARITY_SELECT_PATCH_V47" not in text:
        select_insert = _with_nl('\t\t\t\t# AP_ITEM_RARITY_SELECT_PATCH_V47\n\t\t\t\tif email.type == \\"add_item\\":\n\t\t\t\t\tvar ap_essence_only_screen = _ap_lbal_extra_forces_essence(email.extra_values)\n\t\t\t\t\tif ap_essence_only_screen:\n\t\t\t\t\t\trarity = \\"essence\\"\n\t\t\t\t\telse:\n\t\t\t\t\t\tif rarity == null or str(rarity) == \\"essence\\":\n\t\t\t\t\t\t\trarity = _ap_lbal_vanilla_rarity_for_current_screen(true)\n\t\t\t\t\t\tcard_pool = _ap_lbal_add_missing_placeholder_to_rarity(card_pool, true, false, rarity)\n', newline)
        text, _ = re.subn(
            r'(\t\t\t\trandomize\(\)\r?\n)(\t\t\t\tif rarity != null and card_pool\.has\(rarity\) and card_pool\[rarity\]\.size\(\) > 0:)',
            lambda m: m.group(1) + select_insert + m.group(2),
            text,
            count=1,
        )

    if "AP_ESSENCE_ONLY_FALLBACK_PATCH_V26" not in text:
        fallback_insert = _with_nl('\t\t\t\t\t# AP_ESSENCE_ONLY_FALLBACK_PATCH_V26\n\t\t\t\t\tif _ap_lbal_extra_forces_essence(email.extra_values):\n\t\t\t\t\t\tif database.has(\\"pool_ball_essence\\"):\n\t\t\t\t\t\t\tcard.data = database[\\"pool_ball_essence\\"]\n\t\t\t\t\t\telif database.has(\\"item_missing\\"):\n\t\t\t\t\t\t\tcard.data = database[\\"item_missing\\"]\n\t\t\t\t\t\tcontinue\n', newline)
        text, _ = re.subn(
            r'(\t\t\t\telif email.type == \\"add_item\\":\r?\n\t\t\t\t\tif c < forced_rarity_arr\.size\(\) and \(\(email\.extra_values\.has\(\\"or_better\\"\) and not email\.extra_values\.or_better\) or \(not email\.extra_values\.has\(\\"or_better\\"\)\)\):\r?\n\t\t\t\t\t\trarity = forced_rarity_arr\[c\]\r?\n)',
            lambda m: m.group(1) + fallback_insert,
            text,
            count=1,
        )


    select_v47_gd = """				# AP_ITEM_RARITY_SELECT_PATCH_V47
				if email.type == "add_item":
					var ap_essence_only_screen = _ap_lbal_extra_forces_essence(email.extra_values)
					if ap_essence_only_screen:
						rarity = "essence"
					else:
						if rarity == null or str(rarity) == "essence":
							rarity = _ap_lbal_vanilla_rarity_for_current_screen(true)
						card_pool = _ap_lbal_add_missing_placeholder_to_rarity(card_pool, true, false, rarity)
"""
    text, _ = re.subn(
        r'\t\t\t\t# AP_ITEM_RARITY_SELECT_PATCH_V47\r?\n\t\t\t\tif email\.type == \\"add_item\\":.*?_ap_lbal_first_nonempty_rarity\(card_pool, false\)\r?\n',
        _with_nl(_escaped_gd(select_v47_gd), newline),
        text,
        count=1,
        flags=re.S,
    )


    return text





def _upgrade_empty_item_pool_v65(text: str) -> str:
    newline = _nl(text)

    robust_select = """				# AP_ITEM_RARITY_SELECT_PATCH_V65
				if email.type == "add_item":
					var ap_essence_only_screen = _ap_lbal_extra_forces_essence(email.extra_values)
					if ap_essence_only_screen:
						rarity = "essence"
					else:
						if rarity == null or str(rarity) == "essence":
							rarity = _ap_lbal_vanilla_rarity_for_current_screen(true)
						card_pool = _ap_lbal_add_missing_placeholder_to_rarity(card_pool, true, false, rarity)
						if not card_pool.has(rarity) or typeof(card_pool[rarity]) != TYPE_ARRAY or card_pool[rarity].size() <= 0:
							rarity = _ap_lbal_first_nonempty_rarity(card_pool, false)
						if rarity == null:
							rarity = "common"
							card_pool = _ap_lbal_add_missing_placeholder_to_rarity(card_pool, true, false, rarity)
"""
    robust_select_esc = _with_nl(_escaped_gd(robust_select), newline)

    # Upgrade any older AP item rarity select block.
    text, _ = re.subn(
        r'\t\t\t\t# AP_ITEM_RARITY_SELECT_PATCH_V(?:16|18|21|47|65)\r?\n\t\t\t\tif email\.type == \\"add_item\\":.*?(?=\t\t\t\tif rarity != null and card_pool\.has\(rarity\) and card_pool\[rarity\]\.size\(\) > 0:)',
        robust_select_esc,
        text,
        count=1,
        flags=re.S,
    )

    # Make the vanilla add-item fallback safe when rarity_database[items][rarity] is empty/missing.
    safe_fallback = """							# AP_EMPTY_ITEM_POOL_FIX_V65
							if not $"/root/Main/".rarity_database["items"].has(rarity):
								$"/root/Main/".rarity_database["items"][rarity] = []
							card_pool = $"/root/Main/".rarity_database["items"][rarity].duplicate(true)
							card_pool = _ap_lbal_filter_item_type_array(card_pool, rarity)
							for d in cards:
								if d.data != null and typeof(d.data) == TYPE_DICTIONARY and d.data.has("type"):
									card_pool.erase(d.data.type)
							if card_pool.size() <= 0:
								var ap_placeholder_v65 = _ap_lbal_missing_placeholder_type(true, false, rarity)
								_ap_lbal_ensure_placeholder_database_entry_v65("items", ap_placeholder_v65)
								card_pool.push_back(ap_placeholder_v65)
							var ap_pick_v65 = card_pool[floor(rand_range(0, card_pool.size()))]
							if database.has(ap_pick_v65):
								card.data = database[ap_pick_v65]
							else:
								card.data = _ap_lbal_safe_item_fallback_v65(database, rarity)
"""
    safe_fallback_esc = _with_nl(_escaped_gd(safe_fallback), newline)

    text, _ = re.subn(
        r'\t\t\t\t\t\t\tcard_pool = \$\\"/root/Main/\\"\.rarity_database\[\\"items\\"\]\[rarity\]\.duplicate\(true\)\r?\n'
        r'\t\t\t\t\t\t\tcard_pool = _ap_lbal_filter_item_type_array\(card_pool, rarity\)\r?\n'
        r'\t\t\t\t\t\t\tfor d in cards:\r?\n'
        r'(?:\t\t\t\t\t\t\t\t.*?\r?\n){1,3}'
        r'\t\t\t\t\t\t\tif card_pool\.size\(\) > 0:\r?\n'
        r'\t\t\t\t\t\t\t\tcard\.data = database\[card_pool\[floor\(rand_range\(0, card_pool\.size\(\)\)\)\]\]\r?\n'
        r'(?:\t\t\t\t\t\t\telif database\.has\(\\"item_missing\\"\):\r?\n\t\t\t\t\t\t\t\tcard\.data = database\[\\"item_missing\\"\]\r?\n)?'
        r'(?:\t\t\t\t\t\t\telif database\.has\(\\"pool_ball\\"\):\r?\n\t\t\t\t\t\t\t\tcard\.data = database\[\\"pool_ball\\"\]\r?\n)?',
        safe_fallback_esc,
        text,
        count=1,
        flags=re.S,
    )
    return text


def _fix_one_per_run_indentation_v53(text: str) -> str:
    """Fix V52 malformed no-tab one-per-run line inside _ap_lbal_update_state()."""
    text = text.replace(
        "\tap_allowed_essences.clear()\nap_one_per_run_items.clear()",
        "\tap_allowed_essences.clear()\n\tap_one_per_run_items.clear()",
    )
    text = text.replace(
        "\\tap_allowed_essences.clear()\\nap_one_per_run_items.clear()",
        "\\tap_allowed_essences.clear()\\n\\tap_one_per_run_items.clear()",
    )
    return text


def _dedupe_gd_functions_v51(text: str, function_names: Iterable[str]) -> str:
    """Remove duplicate embedded GDScript functions, keeping the first copy.

    Older V47-V50 patchers could insert the rarity helper block twice when
    upgrading an already-patched PCK. Godot then fails with:
    "The function ... already exists in this class".
    """
    for fn in function_names:
        pattern = re.compile(
            rf"func {re.escape(fn)}\([^)]*\):.*?(?=\r?\nfunc |\r?\n# |\Z)",
            flags=re.S,
        )
        matches = list(pattern.finditer(text))
        if len(matches) <= 1:
            continue
        keep = matches[0].group(0)
        # Remove later duplicates from the end so indexes stay valid.
        for match in reversed(matches[1:]):
            text = text[:match.start()] + text[match.end():]
        # Make sure the first match remains untouched.
    return text


def _repair_target_kind_scope_v138(text: str) -> str:
    """Fix V137 parse error in _ap_lbal_remove_missing_symbol_cards_v79.

    That helper is only for symbols, so it must not reference target_kind, which
    is declared only inside _ap_lbal_filter_card_pool().
    """
    text = text.replace(
        '_ap_lbal_should_leave_rarity_vanilla_v136(target_kind, rarity)',
        '_ap_lbal_should_leave_rarity_vanilla_v136(\"symbols\", rarity)',
    )
    return text


def _upgrade_boost_off_disables_priority_v137(text: str) -> str:
    """Make /boost off actually stop AP priority injection on already-patched Pop-up.tscn."""
    text = text.replace(
        'if kind != \\"symbols\\" and (priority_set.has(t) or _ap_lbal_set_has_alias_v83(priority_set, kind, t)):',
        'if kind != \\"symbols\\" and ap_live_boost_pool_mode_v136 and (priority_set.has(t) or _ap_lbal_set_has_alias_v83(priority_set, kind, t)):',
    )
    text = text.replace(
        'elif kind != \\"symbols\\" and (priority_set.has(t) or _ap_lbal_set_has_alias_v83(priority_set, kind, t)):',
        'elif kind != \\"symbols\\" and ap_live_boost_pool_mode_v136 and (priority_set.has(t) or _ap_lbal_set_has_alias_v83(priority_set, kind, t)):',
    )
    return text


def _fix_popup_patch_text(text: str) -> str:
    # Fix broken embedded GDScript strings caused by using re.sub with a raw
    # replacement string. In .tscn source, the GDScript line must become:
    #   replace("\\", "/")
    # not:
    #   replace("\", "/")
    plain_broken = 'replace("\\", "/")'
    plain_fixed = 'replace("\\\\", "/")'
    tscn_broken = 'replace(\\"\\\\\\", \\"/\\")'
    tscn_fixed = 'replace(\\"\\\\\\\\\\", \\"/\\")'

    def repair_backslash_strings(value: str) -> str:
        return value.replace(plain_broken, plain_fixed).replace(tscn_broken, tscn_fixed)

    text = _upgrade_boost_off_disables_priority_v137(text)
    text = _repair_target_kind_scope_v138(text)
    text = repair_backslash_strings(text)
    text = _upgrade_deathlink_v1_popup_text(text)
    text = _upgrade_deathlink_send_all_gameover_v71(text)
    text = _upgrade_per_floor_payment_bridge_v23(text)
    text = _upgrade_v19_popup_text(text)
    text = _force_v21_essence_fallback_text(text)
    text = _upgrade_essence_only_selection_v26(text)
    text = _upgrade_empty_item_pool_v65(text)
    text = _upgrade_ap_check_priority_v28(text)
    text = _upgrade_ap_check_remove_done_v70(text)
    text = _dedupe_gd_functions_v51(text, [
        "_ap_lbal_vanilla_rarity_for_current_screen",
        "_ap_lbal_missing_placeholder_type",
        "_ap_lbal_add_missing_placeholder_to_rarity",
        "_ap_lbal_fill_empty_rarities_with_placeholders",
        "_ap_lbal_first_nonempty_rarity",
        "_ap_lbal_filter_card_pool",
        "_ap_lbal_filter_item_type_array",
        "_ap_lbal_apply_ap_check_priority_v71",
        "_ap_lbal_remove_ap_check_from_card_pool_v70",
    ])
    text = _fix_one_per_run_indentation_v53(text)
    text = _upgrade_popup_safe_node_v64(text)
    text = _upgrade_force_missing_item_cards_v94(text)
    text = _upgrade_force_missing_item_rarity_branch_v95(text)
    text = _upgrade_force_missing_item_main_branch_v97(text)
    text = _upgrade_force_missing_item_pool_branch_v98(text)
    text = _upgrade_force_missing_item_pool_branch_v99(text)
    text = _upgrade_force_missing_when_no_item_targets_v101(text)
    text = _upgrade_final_no_mixed_item_cards_v103(text)
    text = _upgrade_final_missing_item_pass_v104(text)
    text = _upgrade_visible_missing_item_final_v105(text)
    text = _upgrade_exact_three_missing_items_v106(text)
    text = _upgrade_three_unique_missing_items_v107(text)
    text = _upgrade_three_missing_items_final_v109(text)
    text = _repair_bad_v100_item_indent_v112(text)
    text = _repair_unescaped_dictionary_literals_v113(text)
    text = _repair_final_pass_rarity_scope_v115(text)
    text = _repair_single_check_file_writers_v117(text)
    text = _undo_pool_ball_safe_fallback_v124(text)
    text = _upgrade_pool_ball_unlocked_common_v126(text)
    text = _upgrade_popup_received_deathlink_no_reflect_v130(text)
    text = _upgrade_symbol_rarity_gate_v120(text)
    text = _upgrade_symbol_rarity_gate_all_filters_v121(text)
    text = repair_backslash_strings(text)
    # V139: always normalize the live marker to the current patch marker.
    text = re.sub(r"AP_LIVE_POOL_PATCH_V\d+", PATCH_MARKER, text, count=1)
    return text


def _upgrade_symbol_rarity_gate_v120(text: str) -> str:
    """Upgrade already-patched Pop-up.tscn to V120 symbol rarity gating."""
    newline = "\r\n" if "\r\n" in text else "\n"

    helper = """func _ap_lbal_symbol_can_appear_in_rarity_v119(type_id, rarity):
\t# V119/V120: metadata-only symbols can be loaded for icons/descriptions, but
\t# Add Symbol still must obey the vanilla rarity table.
\tvar symbol_type = _ap_lbal_canonical_symbol_type_v55(type_id)
\tif symbol_type == \\"ap_check\\":
\t\treturn _ap_lbal_ap_check_pool_active()
\tvar database = _ap_lbal_database_for_kind(\\"symbols\\")
\tif typeof(database) == TYPE_DICTIONARY and database.has(symbol_type):
\t\treturn _ap_lbal_rarity_matches(database[symbol_type], rarity)
\treturn true

"""
    if "_ap_lbal_symbol_can_appear_in_rarity_v119" not in text:
        marker = "func _ap_lbal_database_for_kind(kind):"
        if marker in text:
            text = text.replace(marker, _with_nl(helper, newline) + marker, 1)

    old_card = """\t\tif kind == \\"symbols\\" and ap_live_symbol_received_fallback_v108 and not ap_default_starting_symbol_types.has(t) and t != \\"ap_check\\" and t != \\"base\\" and t != \\"empty\\" and t != \\"dud\\":
\t\t\tfor inject_rarity in existing_rarities:
\t\t\t\tif not card_pool.has(inject_rarity) or typeof(card_pool[inject_rarity]) != TYPE_ARRAY:
\t\t\t\t\tcard_pool[inject_rarity] = []
\t\t\t\tif not card_pool[inject_rarity].has(t):
\t\t\t\t\tcard_pool[inject_rarity].push_front(t)
\t\t\tcontinue
"""
    new_card = """\t\tif kind == \\"symbols\\" and ap_live_symbol_received_fallback_v108 and not ap_default_starting_symbol_types.has(t) and t != \\"ap_check\\" and t != \\"base\\" and t != \\"empty\\" and t != \\"dud\\":
\t\t\tvar native_rarity_v119 = _ap_lbal_rarity_for_database_entry(database[t])
\t\t\tif not card_pool.has(native_rarity_v119) or typeof(card_pool[native_rarity_v119]) != TYPE_ARRAY:
\t\t\t\tcard_pool[native_rarity_v119] = []
\t\t\tif not card_pool[native_rarity_v119].has(t):
\t\t\t\tcard_pool[native_rarity_v119].push_back(t)
\t\t\tcontinue
"""
    text = text.replace(_with_nl(old_card, newline), _with_nl(new_card, newline))

    old_type = """\t\tif kind == \\"symbols\\" and ap_live_symbol_received_fallback_v108 and not ap_default_starting_symbol_types.has(t) and t != \\"ap_check\\" and t != \\"base\\" and t != \\"empty\\" and t != \\"dud\\":
\t\t\tresult.push_back(t)
"""
    new_type = """\t\tif kind == \\"symbols\\" and ap_live_symbol_received_fallback_v108 and not ap_default_starting_symbol_types.has(t) and t != \\"ap_check\\" and t != \\"base\\" and t != \\"empty\\" and t != \\"dud\\":
\t\t\tif _ap_lbal_rarity_matches(database[t], wanted_rarity):
\t\t\t\tresult.push_back(t)
"""
    text = text.replace(_with_nl(old_type, newline), _with_nl(new_type, newline))

    old_filter = 'elif _ap_lbal_symbol_matches_forced_group(symbol_type, forced_group) and _ap_lbal_is_allowed(\\"symbols\\", symbol_type):'
    new_filter = 'elif _ap_lbal_symbol_matches_forced_group(symbol_type, forced_group) and _ap_lbal_is_allowed(\\"symbols\\", symbol_type) and _ap_lbal_symbol_can_appear_in_rarity_v119(symbol_type, rarity):'
    text = text.replace(old_filter, new_filter)
    return text


def _upgrade_symbol_rarity_gate_all_filters_v121(text: str) -> str:
    """Apply the V119/V120 rarity gate to both old filter shapes."""
    if "_ap_lbal_symbol_can_appear_in_rarity_v119" not in text:
        text = _upgrade_symbol_rarity_gate_v120(text)
    old_if = 'if _ap_lbal_symbol_matches_forced_group(symbol_type, forced_group) and _ap_lbal_is_allowed(\\"symbols\\", symbol_type):'
    new_if = 'if _ap_lbal_symbol_matches_forced_group(symbol_type, forced_group) and _ap_lbal_is_allowed(\\"symbols\\", symbol_type) and _ap_lbal_symbol_can_appear_in_rarity_v119(symbol_type, rarity):'
    text = text.replace(old_if, new_if)
    old_elif = 'elif _ap_lbal_symbol_matches_forced_group(symbol_type, forced_group) and _ap_lbal_is_allowed(\\"symbols\\", symbol_type):'
    new_elif = 'elif _ap_lbal_symbol_matches_forced_group(symbol_type, forced_group) and _ap_lbal_is_allowed(\\"symbols\\", symbol_type) and _ap_lbal_symbol_can_appear_in_rarity_v119(symbol_type, rarity):'
    text = text.replace(old_elif, new_elif)
    return text


def _upgrade_pool_ball_unlocked_common_v126(text: str) -> str:
    """Make Pool Ball appear only when it is allowed by AP, not as a no-target safe fallback."""
    old = 'if kind == \\"items\\" and t == \\"pool_ball\\" and (priority_set.has(\\"pool_ball\\") or _ap_lbal_set_has_alias_v83(priority_set, kind, t)):'
    new = 'if kind == \\"items\\" and t == \\"pool_ball\\" and (allowed_set.has(\\"pool_ball\\") or priority_set.has(\\"pool_ball\\") or _ap_lbal_set_has_alias_v83(priority_set, kind, t)):'
    text = text.replace(old, new)
    return text


def _undo_pool_ball_safe_fallback_v124(text: str) -> str:
    """Remove V123's Pool Ball safe fallback from already-patched Pop-up.tscn.

    Pool Ball should only be selectable when AP says Pool Ball is currently a real
    item target. When no AP item target exists, the fallback remains Missing AP Item.
    """
    text = text.replace(
        "\t# V123: Pool Ball is the safe/default LBAL item option when no AP item target exists.\n"
        "\tif not essence_only and int(index) == 1 and typeof(database) == TYPE_DICTIONARY and database.has(\\\"pool_ball\\\"):\n"
        "\t\tcard.data = database[\\\"pool_ball\\\"]\n"
        "\t\treturn true\n",
        "",
    )
    text = text.replace(
        "\t# V123: Pool Ball is the safe/default LBAL item option. When no AP item\n"
        "\t# target exists, show Pool Ball as one option and keep the remaining choices\n"
        "\t# as Missing AP Item placeholders.\n"
        "\tif not essence_only and int(index) == 1 and typeof(database) == TYPE_DICTIONARY and database.has(\\\"pool_ball\\\"):\n"
        "\t\tcard.data = database[\\\"pool_ball\\\"]\n"
        "\t\treturn true\n",
        "",
    )
    text = text.replace(
        "\t\tvar database_v123 = _ap_lbal_database_for_kind(\\\"items\\\")\n"
        "\t\tif typeof(database_v123) == TYPE_DICTIONARY and database_v123.has(\\\"pool_ball\\\"):\n"
        "\t\t\tcard_pool[\\\"common\\\"].push_back(\\\"pool_ball\\\")\n",
        "",
    )
    text = text.replace(
        "\t\t\tif r == \\\"common\\\":\n"
        "\t\t\t\tvar database_v123 = _ap_lbal_database_for_kind(\\\"items\\\")\n"
        "\t\t\t\tif typeof(database_v123) == TYPE_DICTIONARY and database_v123.has(\\\"pool_ball\\\"):\n"
        "\t\t\t\t\tcard_pool[r].push_back(\\\"pool_ball\\\")\n",
        "",
    )
    return text


def _upgrade_pool_ball_fallback_v123(text: str) -> str:
    """Upgrade already-patched Pop-up.tscn so no-item-target screens keep Pool Ball."""
    old = """func _ap_lbal_apply_forced_missing_item_card_variant_v109(card, email, rarity, index):
\tvar database = _ap_lbal_database_for_kind(\\"items\\")
\tvar essence_only = false
\tif email != null and \\"extra_values\\" in email:
\t\tessence_only = _ap_lbal_extra_forces_essence(email.extra_values)
\tvar p = _ap_lbal_missing_placeholder_type_v107(true, essence_only, rarity, index)
\t_ap_lbal_ensure_placeholder_database_entry_v65(\\"items\\", p)
\tif typeof(database) == TYPE_DICTIONARY and p != null and str(p) != \\"\\" and database.has(p):
\t\tcard.data = database[p]
\t\treturn true
\treturn _ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity)

"""
    new = """func _ap_lbal_apply_forced_missing_item_card_variant_v109(card, email, rarity, index):
\tvar database = _ap_lbal_database_for_kind(\\"items\\")
\tvar essence_only = false
\tif email != null and \\"extra_values\\" in email:
\t\tessence_only = _ap_lbal_extra_forces_essence(email.extra_values)
\t# V123: Pool Ball is the safe/default LBAL item option when no AP item target exists.
\tif not essence_only and int(index) == 1 and typeof(database) == TYPE_DICTIONARY and database.has(\\"pool_ball\\"):
\t\tcard.data = database[\\"pool_ball\\"]
\t\treturn true
\tvar p = _ap_lbal_missing_placeholder_type_v107(true, essence_only, rarity, index)
\t_ap_lbal_ensure_placeholder_database_entry_v65(\\"items\\", p)
\tif typeof(database) == TYPE_DICTIONARY and p != null and str(p) != \\"\\" and database.has(p):
\t\tcard.data = database[p]
\t\treturn true
\treturn _ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity)

"""
    if old in text:
        text = text.replace(old, new, 1)
    return text


def _repair_single_check_file_writers_v117(text: str) -> str:
    """V117: one in-game check event must create one checks_to_send file.

    Older patches wrote the same payload to both user:// and LOCALAPPDATA. The
    client watches both paths, so AP_CHECK_NEXT was processed twice and became
    AP Check N and AP Check N+1. This normalizes both AP Check and payment check
    writers to choose bridge OR user path, never both.
    """
    newline = "\r\n" if "\r\n" in text else "\n"

    old_ap = _with_nl(
        "func _ap_lbal_queue_next_ap_check():\n"
        "\tvar nonce = str(OS.get_unix_time()) + \"_\" + str(randi())\n"
        "\tvar payload = JSON.print({\"locations\": [\"AP_CHECK_NEXT\"], \"source\": \"ap_check\", \"nonce\": nonce})\n"
        "\t_ap_lbal_write_file_text(\"user://checks_to_send.json\", payload)\n"
        "\t_ap_lbal_write_file_text(_ap_lbal_ap_bridge_file_path(\"checks_to_send.json\"), payload)\n",
        newline,
    )
    new_ap = _with_nl(
        "func _ap_lbal_queue_next_ap_check():\n"
        "\tvar nonce = str(OS.get_unix_time()) + \"_\" + str(randi())\n"
        "\tvar payload = JSON.print({\"locations\": [\"AP_CHECK_NEXT\"], \"source\": \"ap_check\", \"nonce\": nonce})\n"
        "\tvar bridge_path = _ap_lbal_ap_bridge_file_path(\"checks_to_send.json\")\n"
        "\tif str(bridge_path).begins_with(\"user://\"):\n"
        "\t\t_ap_lbal_write_file_text(\"user://checks_to_send.json\", payload)\n"
        "\telse:\n"
        "\t\t_ap_lbal_write_file_text(bridge_path, payload)\n",
        newline,
    )
    text = text.replace(_escaped_gd(old_ap), _escaped_gd(new_ap))
    text = text.replace(old_ap, new_ap)

    old_game = _with_nl(
        "\t_ap_lbal_write_file_text(\"user://checks_to_send.json\", payload)\n"
        "\t_ap_lbal_write_file_text(_ap_lbal_bridge_file_path(\"checks_to_send.json\"), payload)\n",
        newline,
    )
    new_game = _with_nl(
        "\tvar bridge_path = _ap_lbal_bridge_file_path(\"checks_to_send.json\")\n"
        "\tif str(bridge_path).begins_with(\"user://\"):\n"
        "\t\t_ap_lbal_write_file_text(\"user://checks_to_send.json\", payload)\n"
        "\telse:\n"
        "\t\t_ap_lbal_write_file_text(bridge_path, payload)\n",
        newline,
    )
    text = text.replace(_escaped_gd(old_game), _escaped_gd(new_game))
    text = text.replace(old_game, new_game)
    return text


def _repair_final_pass_rarity_scope_v115(text: str) -> str:
    """Remove out-of-scope rarity references from final Add Item passes.

    The final V103-V109 passes run after card generation, outside the original
    rarity variable's scope. Use common for fallback Missing AP Item cards.
    """
    calls = [
        "_ap_lbal_force_all_visible_item_cards_missing_v103",
        "_ap_lbal_force_all_visible_item_cards_missing_v104",
        "_ap_lbal_force_cards_from_visible_missing_item_v105",
        "_ap_lbal_force_exact_three_missing_item_cards_v106",
        "_ap_lbal_force_three_missing_item_cards_v109",
    ]
    for fn in calls:
        text = text.replace(fn + "(cards, email, rarity)", fn + '(cards, email, \\"common\\")')
    return text


def _repair_unescaped_dictionary_literals_v113(text: str) -> str:
    """Repair raw dictionary quotes inside the TSCN source string.

    V98 inserted:
        {"common": card_pool, ...}
    into Pop-up.tscn without escaping the quotes for the outer TSCN source string.
    Godot then parsed the .tscn script source incorrectly and reported
    'Unterminated dictionary'. This repair escapes that dictionary literal.
    """
    raw = '{"common": card_pool, "uncommon": card_pool, "rare": card_pool, "very_rare": card_pool}'
    escaped = '{\\"common\\": card_pool, \\"uncommon\\": card_pool, \\"rare\\": card_pool, \\"very_rare\\": card_pool}'
    text = text.replace(raw, escaped)
    return text


def _repair_bad_v100_item_indent_v112(text: str) -> str:
    """Repair the malformed V100 branch inside Pop-up.tscn.

    One older injection placed the body of:
        if ap_force_missing_item_pool_v100:
    back at the outer Add Item indentation. Godot then sees an empty if block.
    This pass normalizes that block to the correct indentation inside match rarity "_:".
    """
    newline = "\r\n" if "\r\n" in text else "\n"
    bad = _with_nl(
        "\t\t\t\t\t\t\tif ap_force_missing_item_pool_v100:\n"
        "\t\t\t\t\t_ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity)\n"
        "\t\t\t\telif _ap_lbal_should_force_missing_item_card_v94(email, rarity):\n"
        "\t\t\t\t\t\t\t\tif _ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity):\n"
        "\t\t\t\t\t\t\t\t\tcontinue\n",
        newline,
    )
    good = _with_nl(
        "\t\t\t\t\t\t\tif ap_force_missing_item_pool_v100:\n"
        "\t\t\t\t\t\t\t\t_ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity)\n"
        "\t\t\t\t\t\t\telif _ap_lbal_should_force_missing_item_card_v94(email, rarity):\n"
        "\t\t\t\t\t\t\t\tif _ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity):\n"
        "\t\t\t\t\t\t\t\t\tcontinue\n",
        newline,
    )
    if bad in text:
        text = text.replace(bad, good, 1)

    # Regex fallback for already-modified line endings/spaces.
    text = re.sub(
        r'(\t{7}if ap_force_missing_item_pool_v100:\r?\n)'
        r'\t{4}_ap_lbal_apply_forced_missing_item_card_v94\(card, email, rarity\)\r?\n'
        r'\t{4}elif _ap_lbal_should_force_missing_item_card_v94\(email, rarity\):\r?\n'
        r'\t{8}if _ap_lbal_apply_forced_missing_item_card_v94\(card, email, rarity\):\r?\n'
        r'\t{9}continue\r?\n',
        lambda _m: _with_nl(
            "\t\t\t\t\t\t\tif ap_force_missing_item_pool_v100:\n"
            "\t\t\t\t\t\t\t\t_ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity)\n"
            "\t\t\t\t\t\t\telif _ap_lbal_should_force_missing_item_card_v94(email, rarity):\n"
            "\t\t\t\t\t\t\t\tif _ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity):\n"
            "\t\t\t\t\t\t\t\t\tcontinue\n",
            newline,
        ),
        text,
        count=1,
    )
    return text


def _upgrade_force_missing_item_cards_v94(text: str) -> str:
    """Force Missing AP Item/Essence at the final card.data assignment.

    This catches the LBAL branch that recreates rarity_database["items"][rarity]
    after the main card_pool filter ran, which was why Mining Pick/Pink Pepper/etc.
    could still appear even when the tracker had no item targets.
    """
    newline = _nl(text)

    # Ensure helper functions exist in already-patched PCK text.
    if "func _ap_lbal_should_force_missing_item_card_v94" not in text:
        helper_gd = """func _ap_lbal_missing_item_type_for_screen_v94(email, rarity):
	var essence_only = false
	if email != null and "extra_values" in email:
		essence_only = _ap_lbal_extra_forces_essence(email.extra_values)
	if essence_only:
		var ep = _ap_lbal_missing_placeholder_type(true, true, "essence")
		_ap_lbal_ensure_placeholder_database_entry_v65("essences", ep)
		return ep
	var r = str(rarity)
	if r == "" or r == "null" or r == "essence":
		r = "common"
	var p = _ap_lbal_missing_placeholder_type(true, false, r)
	_ap_lbal_ensure_placeholder_database_entry_v65("items", p)
	return p

func _ap_lbal_should_force_missing_item_card_v94(email, rarity):
	# V97: direct and reliable. The Pop-up email is an object in LBAL, so use
	# email.type directly instead of Dictionary-style checks.
	_ap_lbal_update_state(true)
	if email == null:
		return false
	var e = str(email.type)
	if e.find("item") == -1 and e.find("essence") == -1:
		return false
	var essence_only = false
	if "extra_values" in email:
		essence_only = _ap_lbal_extra_forces_essence(email.extra_values)
	if essence_only:
		return _ap_lbal_should_filter("essences") and not ap_live_has_essence_targets_v92
	return _ap_lbal_should_filter("items") and not ap_live_has_item_targets_v92

func _ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity):
	var database = _ap_lbal_database_for_kind("items")
	var p = _ap_lbal_missing_item_type_for_screen_v94(email, rarity)
	if typeof(database) == TYPE_DICTIONARY and p != null and str(p) != "" and database.has(p):
		card.data = database[p]
		return true
	if typeof(database) == TYPE_DICTIONARY and database.has("item_missing"):
		card.data = database["item_missing"]
		return true
	return false

"""
        anchor = _with_nl("func _ap_lbal_filter_card_pool(card_pool, email_type, extra_values = null):\n", newline)
        if anchor in text:
            text = text.replace(anchor, _with_nl(_escaped_gd(helper_gd), newline) + anchor, 1)

    # Replace the main fallback block used when LBAL assigns item cards.
    old = _with_nl('\t\t\t\t\t\t\tcard_pool = $"/root/Main/".rarity_database["items"][rarity].duplicate(true)\n\t\t\t\t\t\t\tcard_pool = _ap_lbal_filter_item_type_array(card_pool, rarity)\n\t\t\t\t\t\t\tfor d in cards:\n\t\t\t\t\t\t\t\tcard_pool.erase(d.data.type)\n\t\t\t\t\t\t\tif card_pool.size() > 0:\n\t\t\t\t\t\t\t\tcard.data = database[card_pool[floor(rand_range(0, card_pool.size()))]]\n\t\t\t\t\t\t\telif database.has("item_missing"):\n\t\t\t\t\t\t\t\tcard.data = database["item_missing"]\n\t\t\t\t\t\t\telif database.has("pool_ball"):\n\t\t\t\t\t\t\t\tcard.data = database["pool_ball"]\n', newline)
    new = _with_nl('\t\t\t\t\t\t\tif _ap_lbal_should_force_missing_item_card_v94(email, rarity):\n\t\t\t\t\t\t\t\tif _ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity):\n\t\t\t\t\t\t\t\t\tcontinue\n\t\t\t\t\t\t\tcard_pool = $"/root/Main/".rarity_database["items"][rarity].duplicate(true)\n\t\t\t\t\t\t\tcard_pool = _ap_lbal_filter_item_type_array(card_pool, rarity)\n\t\t\t\t\t\t\tfor d in cards:\n\t\t\t\t\t\t\t\t# Do not erase Missing AP Item/Essence placeholders. We want all three\n\t\t\t\t\t\t\t\t# choices to be Missing AP Item when no AP item is possible.\n\t\t\t\t\t\t\t\tif not str(d.data.type).begins_with("ap_missing_item") and str(d.data.type) != "item_missing" and str(d.data.type) != "missing_item":\n\t\t\t\t\t\t\t\t\tcard_pool.erase(d.data.type)\n\t\t\t\t\t\t\tif card_pool.size() > 0:\n\t\t\t\t\t\t\t\tcard.data = database[card_pool[floor(rand_range(0, card_pool.size()))]]\n\t\t\t\t\t\t\telif database.has("item_missing"):\n\t\t\t\t\t\t\t\tcard.data = database["item_missing"]\n\t\t\t\t\t\t\telif database.has("pool_ball"):\n\t\t\t\t\t\t\t\tcard.data = database["pool_ball"]\n', newline)
    if old in text:
        text = text.replace(old, new, 1)

    # Escaped .tscn-string form inside older patch injections.
    old_esc = _with_nl('\t\t\t\t\t\t\tcard_pool = $\\\\"/root/Main/\\\\".rarity_database[\\\\"items\\\\"][rarity].duplicate(true)\n\t\t\t\t\t\t\tcard_pool = _ap_lbal_filter_item_type_array(card_pool, rarity)\n\t\t\t\t\t\t\tfor d in cards:\n\t\t\t\t\t\t\t\tcard_pool.erase(d.data.type)\n\t\t\t\t\t\t\tif card_pool.size() > 0:\n\t\t\t\t\t\t\t\tcard.data = database[card_pool[floor(rand_range(0, card_pool.size()))]]\n\t\t\t\t\t\t\telif database.has(\\\\"item_missing\\\\"):\n\t\t\t\t\t\t\t\tcard.data = database[\\\\"item_missing\\\\"]\n\t\t\t\t\t\t\telif database.has(\\\\"pool_ball\\\\"):\n\t\t\t\t\t\t\t\tcard.data = database[\\\\"pool_ball\\\\"]\n', newline)
    new_esc = _with_nl('\t\t\t\t\t\t\tif _ap_lbal_should_force_missing_item_card_v94(email, rarity):\n\t\t\t\t\t\t\t\tif _ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity):\n\t\t\t\t\t\t\t\t\tcontinue\n\t\t\t\t\t\t\tcard_pool = $\\\\"/root/Main/\\\\".rarity_database[\\\\"items\\\\"][rarity].duplicate(true)\n\t\t\t\t\t\t\tcard_pool = _ap_lbal_filter_item_type_array(card_pool, rarity)\n\t\t\t\t\t\t\tfor d in cards:\n\t\t\t\t\t\t\t\tif not str(d.data.type).begins_with("ap_missing_item") and str(d.data.type) != "item_missing" and str(d.data.type) != "missing_item":\n\t\t\t\t\t\t\t\t\tcard_pool.erase(d.data.type)\n\t\t\t\t\t\t\tif card_pool.size() > 0:\n\t\t\t\t\t\t\t\tcard.data = database[card_pool[floor(rand_range(0, card_pool.size()))]]\n\t\t\t\t\t\t\telif database.has(\\\\"item_missing\\\\"):\n\t\t\t\t\t\t\t\tcard.data = database[\\\\"item_missing\\\\"]\n\t\t\t\t\t\t\telif database.has(\\\\"pool_ball\\\\"):\n\t\t\t\t\t\t\t\tcard.data = database[\\\\"pool_ball\\\\"]\n', newline)
    if old_esc in text:
        text = text.replace(old_esc, new_esc, 1)

    return text


def _upgrade_force_missing_item_rarity_branch_v95(text: str) -> str:
    """Patch the main choice branch so Add Item cannot fall back to vanilla items.

    The original LBAL code first uses card_pool[rarity] if non-empty, then later
    rebuilds rarity_database["items"][rarity]. V94 patched the later fallback,
    but after the first Missing AP Item was chosen it could be erased and the next
    cards still rebuilt vanilla choices. V95 intercepts before both paths.
    """
    if "AP_FORCE_MISSING_ITEM_CARD_V95" in text:
        return text
    newline = _nl(text)
    forced_gd = """				# AP_FORCE_MISSING_ITEM_CARD_V95
				if email.type == "add_item" and _ap_lbal_should_force_missing_item_card_v94(email, rarity):
					_ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity)
				elif rarity != null and card_pool.has(rarity) and card_pool[rarity].size() > 0:
"""
    forced_text = _with_nl(_escaped_gd(forced_gd), newline)
    pattern = (
        r'(\t\t\t\trandomize\(\)\r?\n)'
        r'\t\t\t\tif rarity != null and card_pool\.has\(rarity\) and card_pool\[rarity\]\.size\(\) > 0:\r?\n'
    )
    text, count = re.subn(
        pattern,
        lambda m: m.group(1) + forced_text,
        text,
        count=1,
        flags=re.S,
    )
    return text


def _upgrade_force_missing_item_main_branch_v97(text: str) -> str:
    """Intercept Add Item before either card_pool or vanilla item fallback can pick real items."""
    if "AP_FORCE_MISSING_ITEM_CARD_V97" in text:
        return text
    newline = _nl(text)
    marker = _with_nl(_escaped_gd("""				# AP_FORCE_MISSING_ITEM_CARD_V97
				if _ap_lbal_should_force_missing_item_card_v94(email, rarity):
					_ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity)
				elif rarity != null and card_pool.has(rarity) and card_pool[rarity].size() > 0:
"""), newline)

    # The unescaped GDScript line inside a .tscn script/source string.
    raw_line = _with_nl('\t\t\t\tif rarity != null and card_pool.has(rarity) and card_pool[rarity].size() > 0:\n', newline)
    if raw_line in text:
        text = text.replace(raw_line, marker, 1)

    # Some paths have CRLF or already had V47 inserted just before this line.
    text, _ = re.subn(
        r'\t\t\t\tif rarity != null and card_pool\.has\(rarity\) and card_pool\[rarity\]\.size\(\) > 0:\r?\n',
        marker,
        text,
        count=1,
    )

    return text


def _upgrade_force_missing_item_pool_branch_v98(text: str) -> str:
    """If Missing AP Item is in the card_pool, force Missing AP Item for every item card."""
    if "AP_FORCE_MISSING_ITEM_POOL_V98" in text:
        return text
    newline = _nl(text)

    # Insert after card_pool is filtered, before cards are selected.
    old = _with_nl('\t\tcard_pool = _ap_lbal_filter_card_pool(card_pool, email.type, email.extra_values)\n', newline)
    new = _with_nl('\t\tcard_pool = _ap_lbal_filter_card_pool(card_pool, email.type, email.extra_values)\n\t\t# AP_FORCE_MISSING_ITEM_POOL_V98\n\t\tif email.type == "add_item" and _ap_lbal_card_pool_has_missing_item_v98(card_pool):\n\t\t\tcard_pool = _ap_lbal_force_missing_item_choice_pool_v98(card_pool, "common", _ap_lbal_extra_forces_essence(email.extra_values))\n', newline)
    if old in text:
        text = text.replace(old, new, 1)

    # Also harden the main rarity branch. This catches any path where the pool
    # gets rebuilt later before the card is assigned.
    line = _with_nl('\t\t\t\tif _ap_lbal_should_force_missing_item_card_v94(email, rarity):\n', newline)
    repl = _with_nl('\t\t\t\tif email.type == "add_item" and _ap_lbal_card_pool_has_missing_item_v98(card_pool):\n\t\t\t\t\t_ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity)\n\t\t\t\telif _ap_lbal_should_force_missing_item_card_v94(email, rarity):\n', newline)
    if line in text:
        text = text.replace(line, repl, 1)

    # If the later fallback is reached, make sure it cannot erase the only missing placeholder then pick vanilla.
    later = _with_nl('\t\t\t\t\t\t\tcard_pool = _ap_lbal_filter_item_type_array(card_pool, rarity)\n', newline)
    later_repl = _with_nl('\t\t\t\t\t\t\tcard_pool = _ap_lbal_filter_item_type_array(card_pool, rarity)\n\t\t\t\t\t\t\tif _ap_lbal_card_pool_has_missing_item_v98({"common": card_pool, "uncommon": card_pool, "rare": card_pool, "very_rare": card_pool}):\n\t\t\t\t\t\t\t\tcard_pool = [_ap_lbal_missing_placeholder_type(true, false, rarity)]\n', newline)
    if later in text:
        text = text.replace(later, later_repl, 1)

    return text


def _upgrade_force_missing_item_pool_branch_v99(text: str) -> str:
    """Force all Add Item/Add Item Prompt cards to Missing AP Item once the filtered pool contains Missing AP Item.

    V100 fixes V99's two remaining issues:
    1) the generated TSCN insertion is escaped correctly, so the patched script is valid;
    2) add_item_prompt is treated the same as add_item, so prompt paths cannot leak items.
    """
    if "AP_FORCE_MISSING_ITEM_POOL_V100" in text:
        return text

    newline = "\r\n" if "\r\n" in text else "\n"

    # Add a persistent local flag immediately after the AP card_pool filter.
    insert_gd = """		# AP_FORCE_MISSING_ITEM_POOL_V100
		var ap_force_missing_item_pool_v100 = false
		if str(email.type).find("item") >= 0 and _ap_lbal_card_pool_has_missing_item_v98(card_pool):
			ap_force_missing_item_pool_v100 = true
			card_pool = _ap_lbal_force_missing_item_choice_pool_v98(card_pool, "common", _ap_lbal_extra_forces_essence(email.extra_values))
"""
    insert_text = _with_nl(_escaped_gd(insert_gd), newline)
    text, inserted = re.subn(
        r'(\t\tcard_pool = _ap_lbal_filter_card_pool\(card_pool, email\.type, email\.extra_values\)\r?\n)',
        lambda match: match.group(1) + insert_text,
        text,
        count=1,
    )

    if inserted <= 0:
        return text

    # Main rarity-card branch. Use the persistent bool, not the current pool,
    # because the pool gets modified/erased after each card.
    branch_gd = """				if ap_force_missing_item_pool_v100:
					_ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity)
				elif _ap_lbal_should_force_missing_item_card_v94(email, rarity):
"""
    branch_text = _with_nl(_escaped_gd(branch_gd), newline)

    text, replaced = re.subn(
        r'\t\t\t\t# AP_FORCE_MISSING_ITEM_CARD_V97\r?\n'
        r'\t\t\t\tif _ap_lbal_should_force_missing_item_card_v94\(email, rarity\):\r?\n',
        _with_nl(_escaped_gd("\t\t\t\t# AP_FORCE_MISSING_ITEM_CARD_V97\n"), newline) + branch_text,
        text,
        count=1,
    )

    if replaced <= 0:
        text, _ = re.subn(
            r'\t\t\t\tif _ap_lbal_should_force_missing_item_card_v94\(email, rarity\):\r?\n',
            branch_text,
            text,
            count=1,
        )

    return text


def _upgrade_force_missing_when_no_item_targets_v101(text: str) -> str:
    """After card_pool filtering, force all rarities to Missing AP Item whenever no AP item targets exist."""
    if "AP_FORCE_NO_ITEM_TARGETS_V101" in text:
        return text
    insert_gd = """		# AP_FORCE_NO_ITEM_TARGETS_V101
		if str(email.type).find("item") >= 0 and _ap_lbal_should_filter("items") and not ap_live_has_item_targets_v92:
			card_pool = _ap_lbal_force_missing_item_choice_pool_v98(card_pool, "common", _ap_lbal_extra_forces_essence(email.extra_values))
"""
    insert_text = _escaped_gd(insert_gd).replace("\n", "\r\n" if "\r\n" in text else "\n")
    text, _ = re.subn(
        r'(\t\tcard_pool = _ap_lbal_filter_card_pool\(card_pool, email\.type, email\.extra_values\)\r?\n)',
        lambda m: m.group(1) + insert_text,
        text,
        count=1,
    )
    return text


def _upgrade_final_no_mixed_item_cards_v103(text: str) -> str:
    """Final safety pass: if any Add Item card is Missing AP Item, make every Add Item card Missing AP Item.

    This is placed after LBAL has generated all cards, so it catches every path:
    card_pool rarity branch, item fallback branch, saved_card_types reuse, and prompts.
    """
    if "AP_FINAL_NO_MIXED_ITEM_CARDS_V103" in text:
        return text

    newline = "\r\n" if "\r\n" in text else "\n"
    inject_gd = """		# AP_FINAL_NO_MIXED_ITEM_CARDS_V103
		if str(email.type).find("item") >= 0:
			if _ap_lbal_force_all_visible_item_cards_missing_v103(cards, email, rarity):
				saved_card_types.clear()
				for ap_card_v103 in cards:
					if ap_card_v103 != null and ap_card_v103.data != null and typeof(ap_card_v103.data) == TYPE_DICTIONARY and ap_card_v103.data.has("type"):
						saved_card_types.push_back(ap_card_v103.data.type)
"""
    inject_text = _with_nl(_escaped_gd(inject_gd), newline)

    # Insert right before LBAL marks card data as loaded, after the card generation loop.
    text, count = re.subn(
        r'(\t\tif typeof\(email\.extra_values\) == TYPE_DICTIONARY:\r?\n)',
        lambda match: inject_text + match.group(1),
        text,
        count=1,
    )
    return text


def _upgrade_final_missing_item_pass_v104(text: str) -> str:
    """Final Add Item pass using robust card.data detection.

    V103 could miss Missing AP Item if card.data was not a plain Dictionary in the
    running game. V104 checks Dictionary, Object-style properties, and display name.
    """
    newline = "\r\n" if "\r\n" in text else "\n"

    if "func _ap_lbal_force_all_visible_item_cards_missing_v104" not in text:
        helper_gd = """func _ap_lbal_card_data_type_v104(data):
	if data == null:
		return ""
	if typeof(data) == TYPE_DICTIONARY:
		if data.has("type"):
			return str(data.type)
		if data.has("id"):
			return str(data.id)
		return ""
	if "type" in data:
		return str(data.type)
	if "id" in data:
		return str(data.id)
	return ""

func _ap_lbal_card_data_name_v104(data):
	if data == null:
		return ""
	if typeof(data) == TYPE_DICTIONARY:
		if data.has("display_name"):
			return str(data.display_name)
		if data.has("name"):
			return str(data.name)
		return ""
	if "display_name" in data:
		return str(data.display_name)
	if "name" in data:
		return str(data.name)
	return ""

func _ap_lbal_card_is_missing_item_v104(card):
	if card == null:
		return false
	if not "data" in card:
		return false
	var t = _ap_lbal_card_data_type_v104(card.data)
	if _ap_lbal_type_is_missing_item_v103(t):
		return true
	var n = _ap_lbal_card_data_name_v104(card.data).to_lower()
	return n.find("missing ap item") >= 0 or n.find("no possible ap item") >= 0 or n.find("missing item") >= 0

func _ap_lbal_force_all_visible_item_cards_missing_v104(cards, email, rarity = "common"):
	if typeof(cards) != TYPE_ARRAY:
		return false
	if email == null:
		return false
	var e = str(email.type)
	if e.find("item") < 0:
		return false
	var force_missing = false
	if _ap_lbal_should_filter("items") and not ap_live_has_item_targets_v92:
		force_missing = true
	for c in cards:
		if _ap_lbal_card_is_missing_item_v104(c):
			force_missing = true
			break
	if not force_missing:
		return false
	var use_rarity = str(rarity)
	if use_rarity == "" or use_rarity == "null" or use_rarity == "essence":
		use_rarity = "common"
	for c in cards:
		_ap_lbal_apply_forced_missing_item_card_v94(c, email, use_rarity)
	return true

"""
        anchor = _with_nl("func _ap_lbal_filter_card_pool(card_pool, email_type, extra_values = null):\n", newline)
        if anchor in text:
            text = text.replace(anchor, _with_nl(_escaped_gd(helper_gd), newline) + anchor, 1)

    if "AP_FINAL_MISSING_ITEM_PASS_V104" in text:
        return text

    inject_gd = """		# AP_FINAL_MISSING_ITEM_PASS_V104
		if str(email.type).find("item") >= 0:
			if _ap_lbal_force_all_visible_item_cards_missing_v104(cards, email, rarity):
				saved_card_types.clear()
				for ap_card_v104 in cards:
					if ap_card_v104 != null and ap_card_v104.data != null:
						saved_card_types.push_back(_ap_lbal_card_data_type_v104(ap_card_v104.data))
"""
    inject_text = _with_nl(_escaped_gd(inject_gd), newline)

    text, count = re.subn(
        r'(\t\tif typeof\(email\.extra_values\) == TYPE_DICTIONARY:\r?\n)',
        lambda match: inject_text + match.group(1),
        text,
        count=1,
    )
    return text


def _upgrade_visible_missing_item_final_v105(text: str) -> str:
    """Use any visible Missing AP Item card as source of truth and copy it to all item cards."""
    if "AP_VISIBLE_MISSING_ITEM_FINAL_V105" in text:
        return text
    newline = "\r\n" if "\r\n" in text else "\n"
    inject_gd = """		# AP_VISIBLE_MISSING_ITEM_FINAL_V105
		if str(email.type).find("item") >= 0:
			if _ap_lbal_force_cards_from_visible_missing_item_v105(cards, email, rarity):
				saved_card_types.clear()
				for ap_card_v105 in cards:
					if ap_card_v105 != null and ap_card_v105.data != null:
						saved_card_types.push_back(_ap_lbal_card_data_type_v105(ap_card_v105))
"""
    inject_text = _with_nl(_escaped_gd(inject_gd), newline)
    text, count = re.subn(
        r'(\t\tif typeof\(email\.extra_values\) == TYPE_DICTIONARY:\r?\n)',
        lambda match: inject_text + match.group(1),
        text,
        count=1,
    )
    return text


def _upgrade_exact_three_missing_items_v106(text: str) -> str:
    """Final Add Item pass: no AP item targets means exactly the first three visible cards are Missing AP Item."""
    if "AP_EXACT_THREE_MISSING_ITEMS_V106" in text:
        return text
    newline = "\r\n" if "\r\n" in text else "\n"
    inject_gd = """\t\t# AP_EXACT_THREE_MISSING_ITEMS_V106
\t\tif str(email.type).find("item") >= 0 and _ap_lbal_should_filter("items") and not ap_live_has_item_targets_v92:
\t\t\tif _ap_lbal_force_exact_three_missing_item_cards_v106(cards, email, rarity):
\t\t\t\tsaved_card_types.clear()
\t\t\t\tvar ap_saved_count_v106 = 0
\t\t\t\tfor ap_card_v106 in cards:
\t\t\t\t\tif ap_saved_count_v106 >= 3:
\t\t\t\t\t\tbreak
\t\t\t\t\tif ap_card_v106 != null and ap_card_v106.data != null:
\t\t\t\t\t\tsaved_card_types.push_back(_ap_lbal_card_data_type_v105(ap_card_v106))
\t\t\t\t\t\tap_saved_count_v106 += 1
"""
    inject_text = _with_nl(_escaped_gd(inject_gd), newline)
    text, _ = re.subn(
        r'(\t\tif typeof\(email\.extra_values\) == TYPE_DICTIONARY:\r?\n)',
        lambda match: inject_text + match.group(1),
        text,
        count=1,
    )
    return text


def _upgrade_three_unique_missing_items_v107(text: str) -> str:
    if "AP_THREE_UNIQUE_MISSING_ITEMS_V107" in text:
        return text
    newline = "\r\n" if "\r\n" in text else "\n"
    inject_gd = """\t\t# AP_THREE_UNIQUE_MISSING_ITEMS_V107
\t\tif str(email.type).find("item") >= 0 and _ap_lbal_should_filter("items") and not ap_live_has_item_targets_v92:
\t\t\tif _ap_lbal_force_exact_three_missing_item_cards_v106(cards, email, rarity):
\t\t\t\tsaved_card_types.clear()
\t\t\t\tvar ap_saved_count_v107 = 0
\t\t\t\tfor ap_card_v107 in cards:
\t\t\t\t\tif ap_saved_count_v107 >= 3:
\t\t\t\t\t\tbreak
\t\t\t\t\tif ap_card_v107 != null and ap_card_v107.data != null:
\t\t\t\t\t\tsaved_card_types.push_back(_ap_lbal_card_data_type_v105(ap_card_v107))
\t\t\t\t\t\tap_saved_count_v107 += 1
"""
    inject_text = _with_nl(_escaped_gd(inject_gd), newline)
    text, _ = re.subn(
        r'(\t\tif typeof\(email\.extra_values\) == TYPE_DICTIONARY:\r?\n)',
        lambda match: inject_text + match.group(1),
        text,
        count=1,
    )
    return text


def _upgrade_three_missing_items_final_v109(text: str) -> str:
    """Final Add Item pass: no item targets means cards 1/2/3 become ap_missing_item_<rarity>_1/2/3."""
    if "AP_THREE_MISSING_ITEMS_FINAL_V109" in text:
        return text
    newline = "\r\n" if "\r\n" in text else "\n"
    inject_gd = """		# AP_THREE_MISSING_ITEMS_FINAL_V109
		if str(email.type).find("item") >= 0 and _ap_lbal_should_filter("items") and not ap_live_has_item_targets_v92:
			if _ap_lbal_force_three_missing_item_cards_v109(cards, email, rarity):
				saved_card_types.clear()
				var ap_saved_count_v109 = 0
				for ap_card_v109 in cards:
					if ap_saved_count_v109 >= 3:
						break
					if ap_card_v109 != null and ap_card_v109.data != null:
						saved_card_types.push_back(_ap_lbal_card_data_type_v105(ap_card_v109))
						ap_saved_count_v109 += 1
"""
    inject_text = _with_nl(_escaped_gd(inject_gd), newline)
    text, _ = re.subn(
        r'(\t\tif typeof\(email\.extra_values\) == TYPE_DICTIONARY:\r?\n)',
        lambda match: inject_text + match.group(1),
        text,
        count=1,
    )
    return text


def _upgrade_ap_check_priority_v28(text: str) -> str:
    """Upgrade already-patched Pop-up.tscn text to force AP Check symbol choices
    while AP Check locations remain."""
    newline = _nl(text)

    # New live state flag.
    if "var ap_live_has_ap_checks = false" not in text:
        text = text.replace(
            "var ap_live_essence_boost_pool_empty = false\n",
            "var ap_live_essence_boost_pool_empty = false\nvar ap_live_has_ap_checks = false\n",
            1,
        )
        text = text.replace(
            "var ap_live_essence_boost_pool_empty = false\r\n",
            "var ap_live_essence_boost_pool_empty = false\r\nvar ap_live_has_ap_checks = false\r\n",
            1,
        )

    if "ap_live_has_ap_checks = false" not in text:
        text = text.replace(
            "ap_live_essence_boost_pool_empty = false\nap_deathlink_enabled = false",
            "ap_live_essence_boost_pool_empty = false\nap_live_has_ap_checks = false\nap_deathlink_enabled = false",
            1,
        )

    if 'has(\\"has_ap_checks\\")' not in text and 'has("has_ap_checks")' not in text:
        text = text.replace(
            "\t\tif data[\"mod_control\"].has(\"essence_boost_pool_empty\"):\n\t\t\tap_live_essence_boost_pool_empty = bool(data[\"mod_control\"][\"essence_boost_pool_empty\"])\n",
            "\t\tif data[\"mod_control\"].has(\"essence_boost_pool_empty\"):\n\t\t\tap_live_essence_boost_pool_empty = bool(data[\"mod_control\"][\"essence_boost_pool_empty\"])\n\t\tif data[\"mod_control\"].has(\"has_ap_checks\"):\n\t\t\tap_live_has_ap_checks = bool(data[\"mod_control\"][\"has_ap_checks\"])\n",
            1,
        )
        text = text.replace(
            "\t\tif data[\\\"mod_control\\\"].has(\\\"essence_boost_pool_empty\\\"):\n\t\t\tap_live_essence_boost_pool_empty = bool(data[\\\"mod_control\\\"][\\\"essence_boost_pool_empty\\\"])\n",
            "\t\tif data[\\\"mod_control\\\"].has(\\\"essence_boost_pool_empty\\\"):\n\t\t\tap_live_essence_boost_pool_empty = bool(data[\\\"mod_control\\\"][\\\"essence_boost_pool_empty\\\"])\n\t\tif data[\\\"mod_control\\\"].has(\\\"has_ap_checks\\\"):\n\t\t\tap_live_has_ap_checks = bool(data[\\\"mod_control\\\"][\\\"has_ap_checks\\\"])\n",
            1,
        )
        text = text.replace(
            "\t\tif live_pool.has(\"essence_boost_pool_empty\"):\n\t\t\tap_live_essence_boost_pool_empty = bool(live_pool[\"essence_boost_pool_empty\"])\n",
            "\t\tif live_pool.has(\"essence_boost_pool_empty\"):\n\t\t\tap_live_essence_boost_pool_empty = bool(live_pool[\"essence_boost_pool_empty\"])\n\t\tif live_pool.has(\"has_ap_checks\"):\n\t\t\tap_live_has_ap_checks = bool(live_pool[\"has_ap_checks\"])\n",
            1,
        )
        text = text.replace(
            "\t\tif live_pool.has(\\\"essence_boost_pool_empty\\\"):\n\t\t\tap_live_essence_boost_pool_empty = bool(live_pool[\\\"essence_boost_pool_empty\\\"])\n",
            "\t\tif live_pool.has(\\\"essence_boost_pool_empty\\\"):\n\t\t\tap_live_essence_boost_pool_empty = bool(live_pool[\\\"essence_boost_pool_empty\\\"])\n\t\tif live_pool.has(\\\"has_ap_checks\\\"):\n\t\t\tap_live_has_ap_checks = bool(live_pool[\\\"has_ap_checks\\\"])\n",
            1,
        )

    if "data.has(\\\"next_ap_check\\\")" not in text and 'data.has("next_ap_check")' not in text:
        text = text.replace(
            "\t\t_ap_lbal_add_values_to_set(data.get(\"essences_to_give\", []), ap_allowed_essences)\n\tap_live_loaded = true",
            "\t\t_ap_lbal_add_values_to_set(data.get(\"essences_to_give\", []), ap_allowed_essences)\n\tif data.has(\"next_ap_check\") and data[\"next_ap_check\"] != null and str(data[\"next_ap_check\"]) != \"\":\n\t\tap_live_has_ap_checks = true\n\tap_live_loaded = true",
            1,
        )
        text = text.replace(
            "\t\t_ap_lbal_add_values_to_set(data.get(\\\"essences_to_give\\\", []), ap_allowed_essences)\n\tap_live_loaded = true",
            "\t\t_ap_lbal_add_values_to_set(data.get(\\\"essences_to_give\\\", []), ap_allowed_essences)\n\tif data.has(\\\"next_ap_check\\\") and data[\\\"next_ap_check\\\"] != null and str(data[\\\"next_ap_check\\\"]) != \\\"\\\":\n\t\tap_live_has_ap_checks = true\n\tap_live_loaded = true",
            1,
        )

    helper_gd = """func _ap_lbal_apply_ap_check_priority_v71(card_pool, forced_group = null):
	# While AP Check locations remain, keep AP Check weighted in the Add Symbol pool
	# but do NOT replace/remove the other normal symbols.
	if not _ap_lbal_ap_check_pool_active():
		return card_pool
	if not _ap_lbal_symbol_matches_forced_group("ap_check", forced_group):
		return card_pool
	var database = _ap_lbal_database_for_kind("symbols")
	if typeof(database) != TYPE_DICTIONARY or not database.has("ap_check"):
		return card_pool
	var rarities = ["common", "uncommon", "rare", "very_rare", "none"]
	for rarity in rarities:
		if not card_pool.has(rarity) or typeof(card_pool[rarity]) != TYPE_ARRAY:
			card_pool[rarity] = []
		# One guaranteed entry makes AP Check available. Extra copies weight it higher,
		# while the rest of the pool remains selectable.
		if not card_pool[rarity].has("ap_check"):
			card_pool[rarity].push_front("ap_check")
		for i in range(2):
			card_pool[rarity].push_back("ap_check")
	return card_pool

"""
    if "func _ap_lbal_apply_ap_check_priority_v71" not in text:
        anchor = _with_nl("func _ap_lbal_filter_card_pool(card_pool, email_type, extra_values = null):\n", newline)
        if anchor in text:
            text = text.replace(anchor, _with_nl(_escaped_gd(helper_gd), newline) + anchor, 1)

    if False and "ap_check_pool_v28" not in text:
        old = _with_nl('\tif choosing_items:\n\t\ttarget_kind = \\"items\\"\n\t\tif essence_only_screen:\n\t\t\ttarget_kind = \\"essences\\"\n\tif not _ap_lbal_should_filter(target_kind) or _ap_lbal_boost_pool_empty_for_kind(target_kind):\n', newline)
        new = _with_nl('\tif choosing_items:\n\t\ttarget_kind = \\"items\\"\n\t\tif essence_only_screen:\n\t\t\ttarget_kind = \\"essences\\"\n\tif target_kind == \\"symbols\\":\n\t\tvar ap_check_pool_v28 = _ap_lbal_apply_ap_check_priority_v71(forced_group)\n\t\tif ap_check_pool_v28 != null:\n\t\t\treturn ap_check_pool_v28\n\tif not _ap_lbal_should_filter(target_kind) or _ap_lbal_boost_pool_empty_for_kind(target_kind):\n', newline)
        if old in text:
            text = text.replace(old, new, 1)
        else:
            old_plain = _with_nl('\tif choosing_items:\n\t\ttarget_kind = "items"\n\t\tif essence_only_screen:\n\t\t\ttarget_kind = "essences"\n\tif not _ap_lbal_should_filter(target_kind) or _ap_lbal_boost_pool_empty_for_kind(target_kind):\n', newline)
            new_plain = _with_nl('\tif choosing_items:\n\t\ttarget_kind = "items"\n\t\tif essence_only_screen:\n\t\t\ttarget_kind = "essences"\n\tif target_kind == "symbols":\n\t\tvar ap_check_pool_v28 = _ap_lbal_apply_ap_check_priority_v71(forced_group)\n\t\tif ap_check_pool_v28 != null:\n\t\t\treturn ap_check_pool_v28\n\tif not _ap_lbal_should_filter(target_kind) or _ap_lbal_boost_pool_empty_for_kind(target_kind):\n', newline)
            if old_plain in text:
                text = text.replace(old_plain, new_plain, 1)
    return text


def _upgrade_ap_check_remove_done_v70(text: str) -> str:
    """Upgrade already-patched Pop-up.tscn text so AP Check is removed from
    symbol pools once every AP Check location is pending/sent/checked."""
    newline = _nl(text)

    is_allowed_gd = """func _ap_lbal_is_allowed(kind, type_id):
	var t = str(type_id)
	if kind == "symbols":
		t = _ap_lbal_canonical_symbol_type_v55(t)
		if t == "ap_check" and not _ap_lbal_ap_check_pool_active():
			return false
	if kind == "items" and ap_one_per_run_items.has(t) and _ap_lbal_has_item_in_run(t):
		return false
	if not _ap_lbal_should_filter(kind):
		return true
	match kind:
		"symbols":
			return ap_allowed_symbols.has(t)
		"items":
			return ap_allowed_items.has(t)
		"essences":
			return ap_allowed_essences.has(t)
	return true

"""
    text, _ = re.subn(
        r"func _ap_lbal_is_allowed\(kind, type_id\):.*?\r?\n\treturn true\r?\n\r?\nfunc _ap_lbal_database_for_kind",
        _with_nl(_escaped_gd(is_allowed_gd), newline) + "func _ap_lbal_database_for_kind",
        text,
        count=1,
        flags=re.S,
    )

    backfill_gd = """func _ap_lbal_backfill_type_array_from_database_v68(result, kind, wanted_rarity = null, forced_group = null):
	if typeof(result) != TYPE_ARRAY:
		result = []
	var database = _ap_lbal_database_for_kind(kind)
	if typeof(database) != TYPE_DICTIONARY:
		return result
	for type_id in database.keys():
		var t = str(type_id)
		if _ap_lbal_is_placeholder_type_v68(t):
			continue
		if kind == "items" and _ap_lbal_item_kind(t) == "essences":
			continue
		if kind == "essences" and _ap_lbal_item_kind(t) != "essences":
			continue
		if kind == "symbols":
			t = _ap_lbal_canonical_symbol_type_v55(t)
			if t == "ap_check" and not _ap_lbal_ap_check_pool_active():
				continue
			if not _ap_lbal_symbol_matches_forced_group(t, forced_group):
				continue
		if wanted_rarity != null and not _ap_lbal_rarity_matches(database[type_id], wanted_rarity):
			continue
		if not result.has(t):
			result.push_back(t)
	return result

"""
    text, _ = re.subn(
        r"func _ap_lbal_backfill_type_array_from_database_v68\(result, kind, wanted_rarity = null, forced_group = null\):.*?\r?\n\treturn result\r?\n\r?\nfunc _ap_lbal_backfill_card_pool_from_database_v68",
        _with_nl(_escaped_gd(backfill_gd), newline) + "func _ap_lbal_backfill_card_pool_from_database_v68",
        text,
        count=1,
        flags=re.S,
    )

    helper_gd = """func _ap_lbal_remove_ap_check_from_card_pool_v70(card_pool):
	if typeof(card_pool) != TYPE_DICTIONARY:
		return card_pool
	for rarity in card_pool.keys():
		if typeof(card_pool[rarity]) != TYPE_ARRAY:
			continue
		while card_pool[rarity].has("ap_check"):
			card_pool[rarity].erase("ap_check")
	return card_pool

"""
    if "func _ap_lbal_remove_ap_check_from_card_pool_v70" not in text:
        anchor = _with_nl("func _ap_lbal_apply_ap_check_priority_v71(card_pool, forced_group = null):\n", newline)
        if anchor in text:
            text = text.replace(anchor, _with_nl(_escaped_gd(helper_gd), newline) + anchor, 1)

    filter_gd = """func _ap_lbal_filter_card_pool(card_pool, email_type, extra_values = null):
	_ap_lbal_update_state(true)
	if typeof(card_pool) != TYPE_DICTIONARY:
		return card_pool
	var choosing_items = _ap_lbal_guess_choosing_items_v93(email_type, card_pool)
	var forced_group = null
	if typeof(extra_values) == TYPE_DICTIONARY and extra_values.has("forced_group"):
		forced_group = extra_values.forced_group
	var essence_only_screen = choosing_items and _ap_lbal_extra_forces_essence(extra_values)
	var target_kind = "symbols"
	if choosing_items:
		target_kind = "items"
		if essence_only_screen:
			target_kind = "essences"
	if target_kind == "symbols" and not _ap_lbal_ap_check_pool_active():
		card_pool = _ap_lbal_remove_ap_check_from_card_pool_v70(card_pool)
	if not _ap_lbal_should_filter(target_kind) or _ap_lbal_boost_pool_empty_for_kind(target_kind):
		if _ap_lbal_card_pool_count(card_pool) <= 0:
			card_pool = _ap_lbal_backfill_card_pool_from_database_v68(card_pool, target_kind, forced_group)
		if target_kind == "symbols":
			if not _ap_lbal_ap_check_pool_active():
				card_pool = _ap_lbal_remove_ap_check_from_card_pool_v70(card_pool)
			else:
				card_pool = _ap_lbal_apply_ap_check_priority_v71(card_pool, forced_group)
			card_pool = _ap_lbal_fill_empty_symbol_rarities_v76(card_pool, forced_group)
		card_pool = _ap_lbal_remove_missing_symbol_cards_v79(card_pool)
		return card_pool
	if choosing_items:
		if essence_only_screen:
			card_pool = _ap_lbal_push_allowed_types_into_card_pool(card_pool, "essences")
		else:
			card_pool = _ap_lbal_push_allowed_types_into_card_pool(card_pool, "items")
	else:
		card_pool = _ap_lbal_push_allowed_types_into_card_pool(card_pool, "symbols", forced_group)
	for rarity in card_pool.keys():
		if typeof(card_pool[rarity]) != TYPE_ARRAY:
			continue
		var filtered = []
		for type_id in card_pool[rarity]:
			if choosing_items:
				var kind = _ap_lbal_item_kind(type_id)
				if essence_only_screen:
					if kind == "essences" and _ap_lbal_is_allowed("essences", type_id):
						filtered.push_back(type_id)
				else:
					if kind != "essences" and _ap_lbal_is_allowed(kind, type_id):
						filtered.push_back(type_id)
			else:
				var symbol_type = _ap_lbal_canonical_symbol_type_v55(type_id)
				if _ap_lbal_symbol_matches_forced_group(symbol_type, forced_group) and _ap_lbal_is_allowed("symbols", symbol_type) and _ap_lbal_symbol_can_appear_in_rarity_v119(symbol_type, rarity):
					if not filtered.has(symbol_type):
						filtered.push_back(symbol_type)
		if essence_only_screen and str(rarity) != "essence":
			card_pool[rarity] = []
		else:
			card_pool[rarity] = filtered
	if target_kind == "symbols":
		if not _ap_lbal_ap_check_pool_active():
			card_pool = _ap_lbal_remove_ap_check_from_card_pool_v70(card_pool)
		else:
			card_pool = _ap_lbal_apply_ap_check_priority_v71(card_pool, forced_group)
		card_pool = _ap_lbal_fill_empty_symbol_rarities_v76(card_pool, forced_group)
		card_pool = _ap_lbal_remove_missing_symbol_cards_v79(card_pool)
		return card_pool
	card_pool = _ap_lbal_fill_empty_rarities_with_placeholders(card_pool, choosing_items, essence_only_screen)
	return card_pool

"""
    text, _ = re.subn(
        r"func _ap_lbal_filter_card_pool\(card_pool, email_type, extra_values = null\):.*?\r?\n\treturn card_pool\r?\n",
        _with_nl(_escaped_gd(filter_gd), newline),
        text,
        count=1,
        flags=re.S,
    )
    return text



def _upgrade_deathlink_send_all_gameover_v71(text: str) -> str:
    """Write deathlink_send.json before any normal Pop-up game_over event.

    Older patch versions only hooked one exact failed-rent add_event("game_over", null)
    line. Some LBAL builds use a different game_over call, so outgoing DeathLink
    never reached the AP client. This line-based patch catches the other normal
    game_over paths while avoiding the DeathLink-receive helper to prevent loops.
    """
    if "_ap_lbal_write_deathlink_send" not in text:
        return text
    lines = text.splitlines(keepends=True)
    out = []
    current_func = ""
    for line in lines:
        stripped = line.lstrip("\t ")
        if stripped.startswith("func "):
            current_func = stripped.split("(", 1)[0].replace("func ", "").strip()
        is_game_over_call = ('add_event(\\"game_over\\"' in line) or ('add_event("game_over"' in line)
        if is_game_over_call and current_func != "_ap_lbal_force_deathlink_game_over":
            recent = "".join(out[-4:])
            if "_ap_lbal_write_deathlink_send" not in recent:
                indent = line[:len(line) - len(stripped)]
                quote = '\\"' if 'add_event(\\"game_over\\"' in line else '"'
                nl = "\r\n" if line.endswith("\r\n") else "\n"
                out.append(indent + "# AP_DEATHLINK_SEND_ALL_GAMEOVER_PATCH_V71" + nl)
                out.append(indent + "_ap_lbal_write_deathlink_send(" + quote + "Failed to pay rent in Luck be a Landlord" + quote + ")" + nl)
        out.append(line)
    return "".join(out)

def _upgrade_popup_safe_node_v64(text: str) -> str:
    helper = '# AP_POPUP_SAFE_NODE_PATCH_V64\nfunc _ap_lbal_main_node_v64():\n\tif not is_inside_tree():\n\t\treturn null\n\treturn get_node_or_null(\\"/root/Main\\")\n\nfunc _ap_lbal_items_node_v64():\n\tvar main = _ap_lbal_main_node_v64()\n\tif main == null:\n\t\treturn null\n\treturn main.get_node_or_null(\\"Items\\")\n\n'
    if "AP_POPUP_SAFE_NODE_PATCH_V64" not in text:
        anchor = "func _ap_lbal_keep_dice_face_textures_v58():"
        if anchor in text:
            text = text.replace(anchor, helper + anchor, 1)
        elif "func _ap_lbal_canonical_symbol_type_v55" in text:
            text = text.replace("func _ap_lbal_canonical_symbol_type_v55", helper + "func _ap_lbal_canonical_symbol_type_v55", 1)

    text = text.replace('var main = get_node_or_null(\\\\"/root/Main\\\\")', 'var main = _ap_lbal_main_node_v64()')
    text = text.replace('var items_node = get_node_or_null(\\\\"/root/Main/Items\\\\")', 'var items_node = _ap_lbal_items_node_v64()')
    return text



def _upgrade_queue_game_checks_v161(text: str) -> str:
    """Upgrade already-patched Pop-up.tscn to preserve multiple AP_CHECK_NEXT sends."""
    if "func _ap_lbal_queue_game_checks(location_names):" not in text:
        return text
    if "ap_check_next_count" in text and "merge with any existing bridge file" in text:
        return text
    newline = _nl(text)
    replacement = _with_nl(_escaped_gd(QUEUE_GAME_CHECKS_GDSCRIPT_V161), newline)
    pattern = r"func _ap_lbal_queue_game_checks\(location_names\):\r?\n\tvar clean = \[\]\r?\n.*?\t_ap_lbal_write_file_text\(_ap_lbal_bridge_file_path\(\"checks_to_send\.json\"\), payload\)\r?\n"
    text, _count = re.subn(pattern, lambda _m: replacement, text, count=1, flags=re.S)
    return text


def _patch_popup_tscn(text: str) -> str:
    text = _upgrade_queue_game_checks_v161(text)
    if PATCH_MARKER in text:
        text = _upgrade_vanilla_effect_references_v22(text)
        return _fix_popup_patch_text(text)
    if re.search(r"AP_LIVE_POOL_PATCH_V\d+", text):
        text = re.sub(r"AP_LIVE_POOL_PATCH_V\d+", PATCH_MARKER, text, count=1)
        return _fix_popup_patch_text(text)
    for old_marker in sorted(OLD_PATCH_MARKERS, key=len, reverse=True):
        if old_marker in text:
            return _fix_popup_patch_text(text.replace(old_marker, PATCH_MARKER))

    newline = _nl(text)
    gd = _with_nl(_escaped_gd(LIVE_GDSCRIPT), newline)
    anchor = _with_nl("var extra_item_choices = 0\n", newline)
    if anchor not in text:
        raise ValueError("Could not find Pop-up.tscn variable anchor for AP live patch")
    text = text.replace(anchor, anchor + gd + newline, 1)

    anchor2 = _with_nl("\t\tfor r in c_tbe.keys():\n\t\t\tfor c in c_tbe[r]:\n\t\t\t\tcard_pool[r].erase(c)\n", newline)
    inject2 = anchor2 + _with_nl("\t\tcard_pool = _ap_lbal_filter_card_pool(card_pool, email.type, email.extra_values)\n", newline)
    if anchor2 not in text:
        raise ValueError("Could not find Pop-up.tscn card_pool filtering anchor")
    text = text.replace(anchor2, inject2, 1)

    old = _with_nl('\t\t\t\t\t\t\tcard_pool = $\\"/root/Main/\\".rarity_database[\\"items\\"][rarity].duplicate(true)\n\t\t\t\t\t\t\tfor d in cards:\n\t\t\t\t\t\t\t\tcard_pool.erase(d.data.type)\n\t\t\t\t\t\t\tcard.data = database[card_pool[rand_range(0, card_pool.size())]]\n', newline)
    new = _with_nl('\t\t\t\t\t\t\tif _ap_lbal_should_force_missing_item_card_v94(email, rarity):\n\t\t\t\t\t\t\t\tif _ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity):\n\t\t\t\t\t\t\t\t\tcontinue\n\t\t\t\t\t\t\tcard_pool = $\\"/root/Main/\\".rarity_database[\\"items\\"][rarity].duplicate(true)\n\t\t\t\t\t\t\tcard_pool = _ap_lbal_filter_item_type_array(card_pool, rarity)\n\t\t\t\t\t\t\tfor d in cards:\n\t\t\t\t\t\t\t\tif not str(d.data.type).begins_with("ap_missing_item") and str(d.data.type) != "item_missing" and str(d.data.type) != "missing_item":\n\t\t\t\t\t\t\t\t\tcard_pool.erase(d.data.type)\n\t\t\t\t\t\t\tif card_pool.size() > 0:\n\t\t\t\t\t\t\t\tcard.data = database[card_pool[floor(rand_range(0, card_pool.size()))]]\n\t\t\t\t\t\t\telif database.has(\\"item_missing\\"):\n\t\t\t\t\t\t\t\tcard.data = database[\\"item_missing\\"]\n\t\t\t\t\t\t\telif database.has(\\"pool_ball\\"):\n\t\t\t\t\t\t\t\tcard.data = database[\\"pool_ball\\"]\n', newline)
    if old not in text:
        raise ValueError("Could not find Pop-up.tscn item fallback anchor")
    text = text.replace(old, new, 1)

    # V26 hard split: forced Essence screens are essence-only; normal Add Item screens are item-only.
    rarity_anchor = _with_nl('\t\t\t\trandomize()\n\t\t\t\tif rarity != null and card_pool.has(rarity) and card_pool[rarity].size() > 0:\n', newline)
    rarity_inject = _with_nl('\t\t\t\trandomize()\n\t\t\t\t# AP_ITEM_RARITY_SELECT_PATCH_V47\n\t\t\t\tif email.type == \\"add_item\\":\n\t\t\t\t\tvar ap_essence_only_screen = _ap_lbal_extra_forces_essence(email.extra_values)\n\t\t\t\t\tif ap_essence_only_screen:\n\t\t\t\t\t\trarity = \\"essence\\"\n\t\t\t\t\telse:\n\t\t\t\t\t\tif rarity == null or str(rarity) == \\"essence\\":\n\t\t\t\t\t\t\trarity = _ap_lbal_vanilla_rarity_for_current_screen(true)\n\t\t\t\t\t\tcard_pool = _ap_lbal_add_missing_placeholder_to_rarity(card_pool, true, false, rarity)\n\t\t\t\t# AP_FORCE_MISSING_ITEM_CARD_V97\n\t\t\t\tif ap_force_missing_item_pool_v100:\n\t\t\t\t\t_ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity)\n\t\t\t\telif _ap_lbal_should_force_missing_item_card_v94(email, rarity):\n\t\t\t\t\t_ap_lbal_apply_forced_missing_item_card_v94(card, email, rarity)\n\t\t\t\telif rarity != null and card_pool.has(rarity) and card_pool[rarity].size() > 0:\n', newline)
    if rarity_anchor not in text:
        raise ValueError("Could not find Pop-up.tscn rarity selection anchor for V26 essence-only fix")
    text = text.replace(rarity_anchor, rarity_inject, 1)

    fallback_anchor = _with_nl('\t\t\t\telif email.type == \\"add_item\\":\n\t\t\t\t\tif c < forced_rarity_arr.size() and ((email.extra_values.has(\\"or_better\\") and not email.extra_values.or_better) or (not email.extra_values.has(\\"or_better\\"))):\n\t\t\t\t\t\trarity = forced_rarity_arr[c]\n', newline)
    fallback_inject = fallback_anchor + _with_nl('\t\t\t\t\t# AP_ESSENCE_ONLY_FALLBACK_PATCH_V26\n\t\t\t\t\tif _ap_lbal_extra_forces_essence(email.extra_values):\n\t\t\t\t\t\tif database.has(\\"pool_ball_essence\\"):\n\t\t\t\t\t\t\tcard.data = database[\\"pool_ball_essence\\"]\n\t\t\t\t\t\telif database.has(\\"item_missing\\"):\n\t\t\t\t\t\t\tcard.data = database[\\"item_missing\\"]\n\t\t\t\t\t\tcontinue\n', newline)
    if fallback_anchor not in text:
        raise ValueError("Could not find Pop-up.tscn fallback branch anchor for V26 essence-only fix")
    text = text.replace(fallback_anchor, fallback_inject, 1)

    # V8 DeathLink: check for incoming DeathLinks every popup update, and
    # send DeathLink when LBAL reaches the cannot-pay-rent game_over branch.
    if DEATHLINK_HOOK_MARKER not in text:
        update_anchor = _with_nl("func update():\n", newline)
        update_inject = _with_nl("func update():\n\t# AP_DEATHLINK_HOOK_PATCH_V12\n\t_ap_lbal_check_deathlink_receive()\n", newline)
        if update_anchor not in text:
            raise ValueError("Could not find Pop-up.tscn update anchor for DeathLink receive patch")
        text = text.replace(update_anchor, update_inject, 1)

        game_over_anchor = _with_nl('\t\t\t\t\t\t\tadd_event(\\"game_over\\", null)\n', newline)
        game_over_inject = _with_nl('\t\t\t\t\t\t\t# AP_DEATHLINK_HOOK_PATCH_V12\n\t\t\t\t\t\t\t_ap_lbal_write_deathlink_send(\\"Failed to pay rent in Luck be a Landlord\\")\n\t\t\t\t\t\t\tadd_event(\\"game_over\\", null)\n', newline)
        if game_over_anchor not in text:
            raise ValueError("Could not find Pop-up.tscn game_over anchor for DeathLink send patch")
        text = text.replace(game_over_anchor, game_over_inject)
    # V11: send Payment locations directly from the successful rent branch.
    payment_anchor = _with_nl("\t\t\t\t\t\ttimes_rent_paid += 1\n", newline)
    payment_inject = payment_anchor + _with_nl("\t\t\t\t\t\t_ap_lbal_queue_payment_check(times_rent_paid)\n", newline)
    if "_ap_lbal_queue_payment_check(times_rent_paid)" not in text:
        if payment_anchor not in text:
            raise ValueError("Could not find Pop-up.tscn successful rent payment anchor for AP payment sender")
        text = text.replace(payment_anchor, payment_inject, 1)
    text = _upgrade_vanilla_effect_references_v22(text)
    return _fix_popup_patch_text(text)





def _upgrade_main_deathlink_receive_v61(text: str, newline: str, death_gd: str) -> str:
    # Replace old Main DeathLink helper blocks with V74 so already-patched PCKs receive and send reliably.
    if "AP_DEATHLINK_MAIN_PATCH_V74" in text:
        return text
    pattern = r"# AP_DEATHLINK_MAIN_PATCH_V\d+\r?\nvar ap_main_deathlink_last_nonce = \"\".*?(?=func _ap_lbal_has_large_numeric_suffix_v60|func _ap_lbal_bridge_file_path|func load_data\(save_ids, load_saved_ids, past_init\):)"
    text, count = re.subn(pattern, lambda _m: death_gd + newline, text, count=1, flags=re.S)
    return text


def _upgrade_workshop_id_texture_overflow_v62(text: str) -> str:
    """Guard vanilla modded extra-texture loops from huge Workshop numeric IDs."""
    main_pattern = (
        r'(\t\t\t\tfor i in texture_db:\r?\n)'
        r'\t\t\t\t\tvar digit_pos = s\.type\.find\(\\"_STEAM_ID_\\"\)\r?\n'
        r'\t\t\t\t\tif i\.substr\(0, digit_pos\) \+ i\.substr\(digit_pos \+ 1, -1\) == s\.type\.substr\(0, s\.type\.find\(\\"_PACK_\\"\)\):\r?\n'
        r'\t\t\t\t\t\tvar digit = int\(i\[i\.find\(\\"_STEAM_ID_\\"\) - 1\]\)\r?\n'
        r'\t\t\t\t\t\tif s\.extra_textures\.size\(\) < digit:\r?\n'
        r'\t\t\t\t\t\t\ts\.extra_textures\.resize\(digit\)\r?\n'
        r'\t\t\t\t\t\ts\.extra_textures\[digit - 1\] = texture_db\[i\]\r?\n'
    )
    main_new = (
        '\t\t\t\t# AP_WORKSHOP_ID_OVERFLOW_GUARD_V64\n'
        '\t\t\t\tfor i in texture_db:\n'
        '\t\t\t\t\tvar digit_pos = s.type.find(\\"_STEAM_ID_\\")\n'
        '\t\t\t\t\tvar pack_pos = s.type.find(\\"_PACK_\\")\n'
        '\t\t\t\t\tvar i_steam_pos = str(i).find(\\"_STEAM_ID_\\")\n'
        '\t\t\t\t\tif digit_pos != -1 and pack_pos != -1 and i_steam_pos > 0 and not _ap_lbal_has_large_numeric_suffix_v60(i):\n'
        '\t\t\t\t\t\tif i.substr(0, digit_pos) + i.substr(digit_pos + 1, -1) == s.type.substr(0, pack_pos):\n'
        '\t\t\t\t\t\t\tvar digit_char = str(i)[i_steam_pos - 1]\n'
        '\t\t\t\t\t\t\tif digit_char >= \\"1\\" and digit_char <= \\"9\\":\n'
        '\t\t\t\t\t\t\t\tvar digit = int(digit_char)\n'
        '\t\t\t\t\t\t\t\tif s.extra_textures.size() < digit:\n'
        '\t\t\t\t\t\t\t\t\ts.extra_textures.resize(digit)\n'
        '\t\t\t\t\t\t\t\ts.extra_textures[digit - 1] = texture_db[i]\n'
    )
    main_v62_pattern = (
        r'\t\t\t\tfor i in texture_db:\r?\n'
        r'\t\t\t\t\tvar digit_pos = s\.type\.find\(\\"_STEAM_ID_\\"\)\r?\n'
        r'\t\t\t\t\tvar pack_pos = s\.type\.find\(\\"_PACK_\\"\)\r?\n'
        r'\t\t\t\t\tvar i_steam_pos = str\(i\)\.find\(\\"_STEAM_ID_\\"\)\r?\n'
        r'\t\t\t\t\tif digit_pos != -1 and pack_pos != -1 and i_steam_pos > 0 and not _ap_lbal_has_large_numeric_suffix_v60\(i\):.*?'
        r'\t\t\t\t\t\t\t\ts\.extra_textures\[digit - 1\] = texture_db\[i\]\r?\n'
    )
    text = re.sub(main_pattern, lambda _m: main_new, text, count=1)
    text = re.sub(main_v62_pattern, lambda _m: main_new, text, count=1, flags=re.S)

    # Slot Icon: add local helper and patch its generic texture loop.
    slot_helper = (
        '# AP_WORKSHOP_ID_OVERFLOW_GUARD_V64\n'
        'func _ap_lbal_slot_has_large_numeric_suffix_v64(value):\n'
        '\tvar clean = str(value).replace(\\".png\\", \\"\\").replace(\\".webp\\", \\"\\")\n'
        '\tvar parts = clean.split(\\"_\\")\n'
        '\tfor part in parts:\n'
        '\t\tif part.length() >= 10:\n'
        '\t\t\tvar all_digits = true\n'
        '\t\t\tfor j in range(part.length()):\n'
        '\t\t\t\tvar c = part[j]\n'
        '\t\t\t\tif c < \\"0\\" or c > \\"9\\":\n'
        '\t\t\t\t\tall_digits = false\n'
        '\t\t\t\t\tbreak\n'
        '\t\t\tif all_digits:\n'
        '\t\t\t\treturn true\n'
        '\treturn false\n\n'
    )
    if "AP_WORKSHOP_ID_OVERFLOW_GUARD_V64" not in text and "var modded = false" in text and "func _init():" in text:
        text = text.replace("func _init():", slot_helper + "func _init():", 1)

    slot_pattern = (
        r'\t\t\t\tfor i in texture_db:\r?\n'
        r'\t\t\t\t\tvar digit_pos = type\.find\(\\"_STEAM_ID_\\"\)\r?\n'
        r'\t\t\t\t\tif i\.substr\(0, digit_pos\) \+ i\.substr\(digit_pos \+ 1, -1\) == type\.substr\(0, type\.find\(\\"_PACK_\\"\)\):\r?\n'
        r'\t\t\t\t\t\tvar digit = int\(i\[i\.find\(\\"_STEAM_ID_\\"\) - 1\]\)\r?\n'
        r'\t\t\t\t\t\tif extra_textures\.size\(\) < digit:\r?\n'
        r'\t\t\t\t\t\t\textra_textures\.resize\(digit\)\r?\n'
        r'\t\t\t\t\t\textra_textures\[digit - 1\] = texture_db\[i\]\r?\n'
    )
    slot_v62_pattern = (
        r'\t\t\t\tfor i in texture_db:\r?\n'
        r'\t\t\t\t\tvar digit_pos = type\.find\(\\"_STEAM_ID_\\"\)\r?\n'
        r'\t\t\t\t\tvar pack_pos = type\.find\(\\"_PACK_\\"\)\r?\n'
        r'\t\t\t\t\tvar i_steam_pos = str\(i\)\.find\(\\"_STEAM_ID_\\"\)\r?\n'
        r'\t\t\t\t\tif digit_pos != -1 and pack_pos != -1 and i_steam_pos > 0 and not \$\\"/root/Main\\"\._ap_lbal_has_large_numeric_suffix_v60\(i\):.*?'
        r'\t\t\t\t\t\t\t\textra_textures\[digit - 1\] = texture_db\[i\]\r?\n'
    )
    slot_new = (
        '\t\t\t\t# AP_WORKSHOP_ID_OVERFLOW_GUARD_V64\n'
        '\t\t\t\tfor i in texture_db:\n'
        '\t\t\t\t\tvar digit_pos = type.find(\\"_STEAM_ID_\\")\n'
        '\t\t\t\t\tvar pack_pos = type.find(\\"_PACK_\\")\n'
        '\t\t\t\t\tvar i_steam_pos = str(i).find(\\"_STEAM_ID_\\")\n'
        '\t\t\t\t\tif digit_pos != -1 and pack_pos != -1 and i_steam_pos > 0 and not _ap_lbal_slot_has_large_numeric_suffix_v64(i):\n'
        '\t\t\t\t\t\tif i.substr(0, digit_pos) + i.substr(digit_pos + 1, -1) == type.substr(0, pack_pos):\n'
        '\t\t\t\t\t\t\tvar digit_char = str(i)[i_steam_pos - 1]\n'
        '\t\t\t\t\t\t\tif digit_char >= \\"1\\" and digit_char <= \\"9\\":\n'
        '\t\t\t\t\t\t\t\tvar digit = int(digit_char)\n'
        '\t\t\t\t\t\t\t\tif extra_textures.size() < digit:\n'
        '\t\t\t\t\t\t\t\t\textra_textures.resize(digit)\n'
        '\t\t\t\t\t\t\t\textra_textures[digit - 1] = texture_db[i]\n'
    )
    text = re.sub(slot_pattern, lambda _m: slot_new, text, count=1)
    text = re.sub(slot_v62_pattern, lambda _m: slot_new, text, count=1, flags=re.S)
    return text



def _upgrade_main_failed_payment_repeat_v133(text: str) -> str:
    """Reset Main failed-payment DeathLink state after leaving the failure popup.

    V130 set ap_main_failed_payment_sent_v130 forever until Title was visible.
    Retry/new-run paths can avoid Title, so later failures stopped writing
    deathlink_send.json. Replace the whole poll function with the V133 version.
    """
    newline = _nl(text)
    new_func = """func _ap_lbal_main_poll_failed_payment_deathlink_v130(delta):
	if $\"Title\".visible:
		ap_main_failed_payment_sent_v130 = false
		return false
	var popup_node = get_node_or_null(\"Pop-up Sprite/Pop-up\")
	if popup_node == null:
		ap_main_failed_payment_sent_v130 = false
		return false
	var email_type = _ap_lbal_main_get_popup_email_type_v130(popup_node)
	if email_type != \"game_over\" and email_type != \"out_of_money\":
		ap_main_failed_payment_sent_v130 = false
		return false
	if ap_main_failed_payment_sent_v130:
		return false
	if OS.get_ticks_msec() < ap_main_received_deathlink_suppress_until_v130:
		return false
	var rent_due = 0
	if \"rent_values\" in popup_node and typeof(popup_node.rent_values) == TYPE_ARRAY and popup_node.rent_values.size() > 0:
		rent_due = int(popup_node.rent_values[0])
	var money = 0
	if has_node(\"Coins\"):
		money += int($\"Coins\".coins) + int($\"Coins\".queued_increase)
	if has_node(\"Sums/Coin Sum\"):
		money += int($\"Sums/Coin Sum\".value)
	var spins_left = 999
	if \"spins\" in popup_node:
		spins_left = int(popup_node.spins)
	var is_failed_payment = email_type == \"out_of_money\" or spins_left <= 0 or (rent_due > 0 and money < rent_due)
	if not is_failed_payment:
		ap_main_failed_payment_sent_v130 = false
		return false
	ap_main_failed_payment_sent_v130 = true
	_ap_lbal_main_write_deathlink_send(\"Failed to pay rent in Luck be a Landlord\")
	return true

"""
    pattern = r'func _ap_lbal_main_poll_failed_payment_deathlink_v130\(delta\):.*?(?=func _ap_lbal_main_bridge_file_path\(file_name\):)'
    text, _ = re.subn(pattern, lambda _m: _with_nl(_escaped_gd(new_func), newline), text, count=1, flags=re.S)
    return text


def _upgrade_main_failed_payment_poll_v130(text: str) -> str:
    """Install/upgrade Main.tscn reliable failed-payment DeathLink poll."""
    newline = _nl(text)
    helper = """# AP_FAILED_PAYMENT_DEATHLINK_POLL_V130
var ap_main_failed_payment_sent_v130 = false
var ap_main_received_deathlink_suppress_until_v130 = 0

func _ap_lbal_main_get_popup_email_type_v130(popup_node):
	if popup_node == null:
		return \"\"
	if not \"emails\" in popup_node:
		return \"\"
	if typeof(popup_node.emails) != TYPE_ARRAY or popup_node.emails.size() <= 0:
		return \"\"
	var email = popup_node.emails[0]
	if typeof(email) == TYPE_DICTIONARY:
		return str(email.get(\"type\", \"\"))
	if \"type\" in email:
		return str(email.type)
	return \"\"

func _ap_lbal_main_mark_received_deathlink_gameover_v130():
	ap_main_received_deathlink_suppress_until_v130 = OS.get_ticks_msec() + 5000
	ap_main_failed_payment_sent_v130 = true

func _ap_lbal_main_poll_failed_payment_deathlink_v130(delta):
	if $\"Title\".visible:
		ap_main_failed_payment_sent_v130 = false
		return false
	var popup_node = get_node_or_null(\"Pop-up Sprite/Pop-up\")
	if popup_node == null:
		ap_main_failed_payment_sent_v130 = false
		return false
	var email_type = _ap_lbal_main_get_popup_email_type_v130(popup_node)
	if email_type != \"game_over\" and email_type != \"out_of_money\":
		ap_main_failed_payment_sent_v130 = false
		return false
	if ap_main_failed_payment_sent_v130:
		return false
	if OS.get_ticks_msec() < ap_main_received_deathlink_suppress_until_v130:
		return false
	var rent_due = 0
	if \"rent_values\" in popup_node and typeof(popup_node.rent_values) == TYPE_ARRAY and popup_node.rent_values.size() > 0:
		rent_due = int(popup_node.rent_values[0])
	var money = 0
	if has_node(\"Coins\"):
		money += int($\"Coins\".coins) + int($\"Coins\".queued_increase)
	if has_node(\"Sums/Coin Sum\"):
		money += int($\"Sums/Coin Sum\".value)
	var spins_left = 999
	if \"spins\" in popup_node:
		spins_left = int(popup_node.spins)
	var is_failed_payment = email_type == \"out_of_money\" or spins_left <= 0 or (rent_due > 0 and money < rent_due)
	if not is_failed_payment:
		ap_main_failed_payment_sent_v130 = false
		return false
	ap_main_failed_payment_sent_v130 = true
	_ap_lbal_main_write_deathlink_send(\"Failed to pay rent in Luck be a Landlord\")
	return true

"""
    if "AP_FAILED_PAYMENT_DEATHLINK_POLL_V130" not in text:
        anchor = _with_nl("func _ap_lbal_main_bridge_file_path(file_name):\n", newline)
        if anchor in text:
            text = text.replace(anchor, _with_nl(helper, newline) + anchor, 1)
    old = _with_nl('func _ap_lbal_main_force_game_over_from_deathlink(cause):\n\tif $\"Title\".visible:\n\t\treturn false\n\tvar popup = get_node_or_null(\"Pop-up Sprite/Pop-up\")\n', newline)
    new = _with_nl('func _ap_lbal_main_force_game_over_from_deathlink(cause):\n\tif $\"Title\".visible:\n\t\treturn false\n\t_ap_lbal_main_mark_received_deathlink_gameover_v130()\n\tvar popup = get_node_or_null(\"Pop-up Sprite/Pop-up\")\n', newline)
    if old in text:
        text = text.replace(old, new, 1)
    if "\t_ap_lbal_main_poll_failed_payment_deathlink_v130(delta)" not in text:
        if "\t_ap_lbal_main_poll_deathlink(delta)" in text:
            text = text.replace("\t_ap_lbal_main_poll_deathlink(delta)", "\t_ap_lbal_main_poll_deathlink(delta)\n\t_ap_lbal_main_poll_failed_payment_deathlink_v130(delta)", 1)
        else:
            anchor = _with_nl("func _process(delta):\n", newline)
            if anchor in text:
                text = text.replace(anchor, _with_nl("func _process(delta):\n\t_ap_lbal_main_poll_failed_payment_deathlink_v130(delta)\n", newline), 1)
    return text


def _upgrade_popup_received_deathlink_no_reflect_v130(text: str) -> str:
    newline = _nl(text)
    old = _with_nl('func _ap_lbal_force_deathlink_game_over(cause):\n\tif $\"/root/Main/Title\".visible:\n\t\treturn false\n\t_ap_lbal_clear_popup_for_deathlink()\n', newline)
    new = _with_nl('func _ap_lbal_force_deathlink_game_over(cause):\n\tif $\"/root/Main/Title\".visible:\n\t\treturn false\n\tvar main_v130 = get_node_or_null(\"/root/Main\")\n\tif main_v130 != null and main_v130.has_method(\"_ap_lbal_main_mark_received_deathlink_gameover_v130\"):\n\t\tmain_v130._ap_lbal_main_mark_received_deathlink_gameover_v130()\n\t_ap_lbal_clear_popup_for_deathlink()\n', newline)
    if old in text:
        text = text.replace(old, new, 1)
    return text

def _upgrade_main_deathlink_send_all_gameover_v74(text: str) -> str:
    """Write deathlink_send.json before Main-level game_over calls too.

    This mirrors the receive-side Main polling patch. Some LBAL builds run game
    over from Main instead of Pop-up, so the Pop-up-only outgoing hook can miss a
    failed payment.
    """
    if "_ap_lbal_main_write_deathlink_send" not in text:
        return text
    lines = text.splitlines(keepends=True)
    out = []
    current_func = ""
    for line in lines:
        stripped = line.lstrip("\t ")
        if stripped.startswith("func "):
            current_func = stripped.split("(", 1)[0].replace("func ", "").strip()
        is_game_over_call = ('add_event(\\"game_over\\"' in line) or ('add_event("game_over"' in line)
        if is_game_over_call and current_func not in {"_ap_lbal_main_force_game_over_from_deathlink", "_ap_lbal_force_deathlink_game_over"}:
            recent = "".join(out[-5:])
            if "_ap_lbal_main_write_deathlink_send" not in recent:
                indent = line[:len(line) - len(stripped)]
                quote = '\\"' if 'add_event(\\"game_over\\"' in line else '"'
                nl = "\r\n" if line.endswith("\r\n") else "\n"
                out.append(indent + "# AP_DEATHLINK_MAIN_SEND_GAMEOVER_PATCH_V74" + nl)
                out.append(indent + "_ap_lbal_main_write_deathlink_send(" + quote + "Failed to pay rent in Luck be a Landlord" + quote + ")" + nl)
        out.append(line)
    return "".join(out)

def _upgrade_deathlink_2s_buffer_v131(text: str) -> str:
    """Add the V131 2-second DeathLink write buffer to already-patched Main.tscn."""
    newline = "\r\n" if "\r\n" in text else "\n"
    if "var ap_main_failed_payment_sent_v130 = false" in text and "ap_main_deathlink_last_write_msec_v131" not in text:
        text = text.replace(
            "var ap_main_failed_payment_sent_v130 = false\nvar ap_main_received_deathlink_suppress_until_v130 = 0\n",
            _with_nl("var ap_main_failed_payment_sent_v130 = false\nvar ap_main_received_deathlink_suppress_until_v130 = 0\nvar ap_main_deathlink_last_write_msec_v131 = 0\n", newline),
            1,
        )
    old = """func _ap_lbal_main_write_deathlink_send(cause):
	var nonce = str(OS.get_unix_time()) + \"_\" + str(randi())
	var payload = JSON.print({\"enabled\": true, \"cause\": str(cause), \"source\": \"main_game_over\", \"nonce\": nonce})
	_ap_lbal_main_write_file_text(\"user://deathlink_send.json\", payload)
	_ap_lbal_main_write_file_text(_ap_lbal_main_bridge_file_path(\"deathlink_send.json\"), payload)
	print(\"AP DeathLink send queued from Main: \" + str(cause))
"""
    new = """func _ap_lbal_main_write_deathlink_send(cause):
	# V131: two-second buffer/debounce so multiple failure hooks do not rewrite
	# deathlink_send.json several times for one failed-payment screen.
	var now_msec_v131 = OS.get_ticks_msec()
	if now_msec_v131 - ap_main_deathlink_last_write_msec_v131 < 2000:
		return false
	ap_main_deathlink_last_write_msec_v131 = now_msec_v131
	var nonce = str(OS.get_unix_time()) + \"_\" + str(randi())
	var payload = JSON.print({\"enabled\": true, \"cause\": str(cause), \"source\": \"main_game_over\", \"nonce\": nonce})
	_ap_lbal_main_write_file_text(\"user://deathlink_send.json\", payload)
	_ap_lbal_main_write_file_text(_ap_lbal_main_bridge_file_path(\"deathlink_send.json\"), payload)
	print(\"AP DeathLink send queued from Main: \" + str(cause))
	return true
"""
    if old in text:
        text = text.replace(old, new, 1)
    return text


def _patch_main_tscn(text: str) -> str:
    newline = _nl(text)
    gd = _with_nl(_escaped_gd(MAIN_AP_CHECK_GDSCRIPT), newline)
    death_gd = _with_nl(_escaped_gd(MAIN_DEATHLINK_GDSCRIPT), newline)
    effects_gd_v139 = _with_nl(_escaped_gd(MAIN_AP_EFFECTS_GDSCRIPT_V139), newline)
    overlay_gd_v149 = _with_nl(_escaped_gd(MAIN_AP_OVERLAY_GDSCRIPT_V149), newline)
    safe_icon_gd = _with_nl(_escaped_gd(MAIN_SAFE_ICON_GDSCRIPT_V60), newline)
    load_anchor = _with_nl("func load_data(save_ids, load_saved_ids, past_init):\n", newline)

    text = _upgrade_main_deathlink_receive_v61(text, newline, death_gd)
    text = _upgrade_main_failed_payment_poll_v130(text)

    text = _upgrade_workshop_id_texture_overflow_v62(text)

    if AP_CHECK_MARKER not in text:
        for old_marker in OLD_AP_CHECK_MARKERS:
            if old_marker in text:
                pattern = r"# " + re.escape(old_marker) + r"\r?\nfunc _ap_lbal_bridge_file_path\(file_name\):.*?\r?\n(?=func load_data\(save_ids, load_saved_ids, past_init\):)"
                text, count = re.subn(pattern, lambda _m: gd + newline, text, count=1, flags=re.S)
                if count == 0:
                    raise ValueError("Could not upgrade old Main.tscn AP Check patch")
                break

    if AP_CHECK_MARKER not in text:
        if load_anchor not in text:
            raise ValueError("Could not find Main.tscn load_data anchor for AP Check patch")
        text = text.replace(load_anchor, gd + newline + load_anchor, 1)

    # V152: refresh effect script for Choice of Symbols wording and Essence Token buff.
    if ("AP_AP_EFFECTS_PATCH_V139" in text) or ("AP_AP_EFFECTS_PATCH_V159" in text):
        pattern_effects_v152 = r"# AP_AP_EFFECTS_PATCH_V159\r?\nvar ap_main_effect_poll_timer_v139 = 0\.0.*?(?=\r?\n# AP_INGAME_OVERLAY_PATCH_V157|\r?\n# AP_SAFE_ICON_LOAD_PATCH_V60|\r?\nfunc load_data\(save_ids, load_saved_ids, past_init\):)"
        text, effects_count_v152 = re.subn(pattern_effects_v152, lambda _m: effects_gd_v139, text, count=1, flags=re.S)

    # V155: refresh already-patched AP effect/overlay scripts in old PCKs.
    if ("AP_AP_EFFECTS_PATCH_V139" in text) or ("AP_AP_EFFECTS_PATCH_V159" in text):
        pattern_effects_v155 = r"# AP_AP_EFFECTS_PATCH_V159\r?\nvar ap_main_effect_poll_timer_v139 = 0\.0.*?(?=\r?\n# AP_INGAME_OVERLAY_PATCH_V149|\r?\n# AP_INGAME_OVERLAY_PATCH_V150|\r?\n# AP_INGAME_OVERLAY_PATCH_V154|\r?\n# AP_INGAME_OVERLAY_PATCH_V157|\r?\n# AP_SAFE_ICON_LOAD_PATCH_V60|\r?\nfunc load_data\(save_ids, load_saved_ids, past_init\):)"
        text, effects_count_v155 = re.subn(pattern_effects_v155, lambda _m: effects_gd_v139, text, count=1, flags=re.S)
    if ("AP_INGAME_OVERLAY_PATCH_V149" in text or "AP_INGAME_OVERLAY_PATCH_V150" in text or "AP_INGAME_OVERLAY_PATCH_V154" in text) and "AP_INGAME_OVERLAY_PATCH_V157" not in text:
        pattern_overlay_v155 = r"# AP_INGAME_OVERLAY_PATCH_V(?:149|150|154)\r?\nvar ap_main_overlay_poll_timer_v149 = 0\.0.*?(?=\r?\n# AP_SAFE_ICON_LOAD_PATCH_V60|\r?\nfunc load_data\(save_ids, load_saved_ids, past_init\):)"
        text, overlay_count_v155 = re.subn(pattern_overlay_v155, lambda _m: overlay_gd_v149, text, count=1, flags=re.S)

    # V151: refresh the current-run-only Dud trap handler in already-patched PCKs.
    if ("AP_AP_EFFECTS_PATCH_V139" in text) or ("AP_AP_EFFECTS_PATCH_V159" in text):
        pattern_effects_v151 = r"# AP_AP_EFFECTS_PATCH_V159\r?\nvar ap_main_effect_poll_timer_v139 = 0\.0.*?(?=\r?\n# AP_INGAME_OVERLAY_PATCH_V157|\r?\n# AP_SAFE_ICON_LOAD_PATCH_V60|\r?\nfunc load_data\(save_ids, load_saved_ids, past_init\):)"
        text, effects_count_v151 = re.subn(pattern_effects_v151, lambda _m: effects_gd_v139, text, count=1, flags=re.S)

    # V150: refresh already-patched AP effect/overlay scripts in old PCKs.
    if ("AP_AP_EFFECTS_PATCH_V139" in text) or ("AP_AP_EFFECTS_PATCH_V159" in text):
        pattern_effects_v150 = r"# AP_AP_EFFECTS_PATCH_V159\r?\nvar ap_main_effect_poll_timer_v139 = 0\.0.*?(?=\r?\n# AP_INGAME_OVERLAY_PATCH_V149|\r?\n# AP_INGAME_OVERLAY_PATCH_V157|\r?\n# AP_SAFE_ICON_LOAD_PATCH_V60|\r?\nfunc load_data\(save_ids, load_saved_ids, past_init\):)"
        text, effects_count_v150 = re.subn(pattern_effects_v150, lambda _m: effects_gd_v139, text, count=1, flags=re.S)
    if "AP_INGAME_OVERLAY_PATCH_V149" in text and "AP_INGAME_OVERLAY_PATCH_V150" not in text:
        pattern_overlay_v150 = r"# AP_INGAME_OVERLAY_PATCH_V149\r?\nvar ap_main_overlay_poll_timer_v149 = 0\.0.*?(?=\r?\n# AP_SAFE_ICON_LOAD_PATCH_V60|\r?\nfunc load_data\(save_ids, load_saved_ids, past_init\):)"
        text, overlay_count_v150 = re.subn(pattern_overlay_v150, lambda _m: overlay_gd_v149, text, count=1, flags=re.S)

    if MAIN_DEATHLINK_PATCH_MARKER not in text:
        if load_anchor not in text:
            raise ValueError("Could not find Main.tscn load_data anchor for DeathLink main poll patch")
        text = text.replace(load_anchor, death_gd + newline + load_anchor, 1)

    if "AP_AP_EFFECTS_PATCH_V162" not in text:
        if load_anchor not in text:
            raise ValueError("Could not find Main.tscn load_data anchor for AP effects patch")
        text = text.replace(load_anchor, effects_gd_v139 + newline + load_anchor, 1)

    # V158: refresh any older overlay patch. This version avoids string-newline parse errors.
    if ("AP_INGAME_OVERLAY_PATCH_V149" in text or "AP_INGAME_OVERLAY_PATCH_V150" in text or "AP_INGAME_OVERLAY_PATCH_V154" in text or "AP_INGAME_OVERLAY_PATCH_V155" in text or "AP_INGAME_OVERLAY_PATCH_V156" in text or "AP_INGAME_OVERLAY_PATCH_V157" in text) and "AP_INGAME_OVERLAY_PATCH_V158" not in text:
        pattern_overlay_v158 = r"# AP_INGAME_OVERLAY_PATCH_V(?:149|150|154|155|156|157)\r?\nvar ap_main_overlay_poll_timer_v149 = 0\.0.*?(?=\r?\n# AP_SAFE_ICON_LOAD_PATCH_V60|\r?\nfunc load_data\(save_ids, load_saved_ids, past_init\):)"
        text, overlay_count_v158 = re.subn(pattern_overlay_v158, lambda _m: overlay_gd_v149, text, count=1, flags=re.S)

    # V160: refresh any old effects patch. This fixes start buffs double-applying and token buffs not showing.
    if ("AP_AP_EFFECTS_PATCH_V139" in text or "AP_AP_EFFECTS_PATCH_V159" in text) and "AP_AP_EFFECTS_PATCH_V160" not in text:
        pattern_effects_v160 = r"# AP_AP_EFFECTS_PATCH_V(?:139|159)\r?\nvar ap_main_effect_poll_timer_v139 = 0\.0.*?(?=\r?\n# AP_INGAME_OVERLAY_PATCH_V158|\r?\n# AP_INGAME_OVERLAY_PATCH_V157|\r?\n# AP_SAFE_ICON_LOAD_PATCH_V60|\r?\nfunc load_data\(save_ids, load_saved_ids, past_init\):)"
        text, effects_count_v160 = re.subn(pattern_effects_v160, lambda _m: effects_gd_v139, text, count=1, flags=re.S)

    # V162: refresh effects patch so Force Payment trap writes a marker for DeathLink suppression.
    if "AP_AP_EFFECTS_PATCH_V160" in text and "AP_AP_EFFECTS_PATCH_V162" not in text:
        pattern_effects_v162 = r"# AP_AP_EFFECTS_PATCH_V160\r?\nvar ap_main_effect_poll_timer_v139 = 0\.0.*?(?=\r?\n# AP_INGAME_OVERLAY_PATCH_V158|\r?\n# AP_INGAME_OVERLAY_PATCH_V157|\r?\n# AP_SAFE_ICON_LOAD_PATCH_V60|\r?\nfunc load_data\(save_ids, load_saved_ids, past_init\):)"
        text, effects_count_v162 = re.subn(pattern_effects_v162, lambda _m: effects_gd_v139, text, count=1, flags=re.S)

    if "AP_INGAME_OVERLAY_PATCH_V158" not in text:
        if load_anchor not in text:
            raise ValueError("Could not find Main.tscn load_data anchor for AP overlay patch")
        text = text.replace(load_anchor, overlay_gd_v149 + newline + load_anchor, 1)

    text = _upgrade_main_deathlink_send_all_gameover_v74(text)
    text = _upgrade_main_failed_payment_poll_v130(text)
    text = _upgrade_main_failed_payment_repeat_v133(text)

    if "AP_SAFE_ICON_LOAD_PATCH_V60" not in text:
        if load_anchor not in text:
            raise ValueError("Could not find Main.tscn load_data anchor for safe icon loader patch")
        text = text.replace(load_anchor, safe_icon_gd + newline + load_anchor, 1)

    # Avoid Godot ResourceLoader errors/overflow from Workshop-style icon names
    # like golem_2895537308.png. Missing icons fall back to missing/item_missing.
    text = text.replace('load(\\"res://icons/%s.png\\" % str(t))', '_ap_lbal_safe_icon_load_v60(\\"res://icons/%s.png\\" % str(t), \\"res://icons/missing.png\\")')
    text = text.replace('load(\\"res://icons/%s.png\\" % str(i))', '_ap_lbal_safe_icon_load_v60(\\"res://icons/%s.png\\" % str(i), \\"res://icons/item_missing.png\\")')
    text = text.replace('load(\\"res://icons/%s.png\\" % str(m))', '_ap_lbal_safe_icon_load_v60(\\"res://icons/%s.png\\" % str(m), \\"res://icons/missing.png\\")')

    process_anchor = _with_nl("func _process(delta):\n", newline)
    process_inject = _with_nl("func _process(delta):\n\t_ap_lbal_main_poll_deathlink(delta)\n", newline)
    if "\t_ap_lbal_main_poll_deathlink(delta)" not in text:
        if process_anchor not in text:
            raise ValueError("Could not find Main.tscn _process anchor for DeathLink main poll patch")
        text = text.replace(process_anchor, process_inject, 1)

    if "\t_ap_lbal_main_poll_ap_effects_v139(delta)" not in text:
        if "\t_ap_lbal_main_poll_deathlink(delta)" in text:
            text = text.replace(
                "\t_ap_lbal_main_poll_deathlink(delta)\n",
                "\t_ap_lbal_main_poll_deathlink(delta)\n\t_ap_lbal_main_poll_ap_effects_v139(delta)\n",
                1,
            )
        elif process_anchor in text:
            text = text.replace(process_anchor, "func _process(delta):\n\t_ap_lbal_main_poll_ap_effects_v139(delta)\n", 1)
        else:
            raise ValueError("Could not find Main.tscn _process anchor for AP effects patch")

    if "\t_ap_lbal_main_poll_overlay_v149(delta)" not in text:
        if "\t_ap_lbal_main_poll_ap_effects_v139(delta)" in text:
            text = text.replace(
                "\t_ap_lbal_main_poll_ap_effects_v139(delta)\n",
                "\t_ap_lbal_main_poll_ap_effects_v139(delta)\n\t_ap_lbal_main_poll_overlay_v149(delta)\n",
                1,
            )
        elif "\t_ap_lbal_main_poll_deathlink(delta)" in text:
            text = text.replace(
                "\t_ap_lbal_main_poll_deathlink(delta)\n",
                "\t_ap_lbal_main_poll_deathlink(delta)\n\t_ap_lbal_main_poll_overlay_v149(delta)\n",
                1,
            )
        elif process_anchor in text:
            text = text.replace(process_anchor, "func _process(delta):\n\t_ap_lbal_main_poll_overlay_v149(delta)\n", 1)
        else:
            raise ValueError("Could not find Main.tscn _process anchor for AP overlay patch")

    call_line = _with_nl("\t_ap_lbal_register_ap_check_symbol()\n", newline)
    if call_line not in text:
        anchor = _with_nl("\tif not group_database[\\\"symbols\\\"].has(\\\"spawner1\\\"):\n", newline)
        if anchor not in text:
            raise ValueError("Could not find Main.tscn spawner1 anchor for AP Check registration")
        text = text.replace(anchor, call_line + anchor, 1)
    text = _upgrade_deathlink_2s_buffer_v131(text)
    return text




def _repair_slot_bad_backslash_v165(text: str) -> str:
    # Repair already-patched Slot Icon.tscn text from v163/v164 where the
    # embedded GDScript contained replace("\", "/"), causing Unexpected EOL at String.
    text = text.replace('replace(\\"\\\\\\", \\"/\\")', 'replace(\\"\\\\\\\\\\", \\"/\\")')
    text = text.replace('replace("\\", "/")', 'replace("\\\\", "/")')
    return text

def _upgrade_slot_ap_check_queue_v163(text: str) -> str:
    """Upgrade Slot Icon AP Check sender to merge same-spin AP Check destroys."""
    if "func _ap_lbal_queue_next_ap_check():" not in text:
        return text
    if "ap_check_next_count" in text and "merge AP Check destroys" in text and "AP_CHECK_SEND_PATCH_V165" in text:
        return text
    newline = _nl(text)
    replacement = _with_nl(_escaped_gd(SLOT_AP_CHECK_SEND_GDSCRIPT), newline)
    pattern = r"# AP_CHECK_SEND_PATCH_V(?:1|163|164|165)\r?\nfunc _ap_lbal_ap_bridge_file_path\(file_name\):.*?(?=\r?\nfunc destroy\(\):)"
    text, count = re.subn(pattern, lambda _m: replacement + newline, text, count=1, flags=re.S)
    if count == 0:
        pattern2 = r"func _ap_lbal_queue_next_ap_check\(\):\r?\n\tvar nonce = str\(OS\.get_unix_time\(\)\).*?(?:\r?\n\t\t_ap_lbal_write_file_text\(bridge_path, payload\)\r?\n|\r?\n\t_ap_lbal_write_file_text\(_ap_lbal_ap_bridge_file_path\(\"checks_to_send\.json\"\), payload\)\r?\n)"
        queue_replacement = _with_nl(_escaped_gd(SLOT_AP_CHECK_SEND_GDSCRIPT.split('func _ap_lbal_queue_next_ap_check():', 1)[1]), newline)
        queue_replacement = "func _ap_lbal_queue_next_ap_check():" + queue_replacement
        text, _count2 = re.subn(pattern2, lambda _m: queue_replacement, text, count=1, flags=re.S)
    return text

def _patch_slot_icon_tscn(text: str) -> str:
    text = _repair_slot_bad_backslash_v165(text)
    text = _upgrade_slot_ap_check_queue_v163(text)
    newline = _nl(text)
    text = _upgrade_workshop_id_texture_overflow_v62(text)

    if AP_CHECK_MARKER not in text:
        for old_marker in OLD_AP_CHECK_MARKERS:
            if old_marker in text:
                text = text.replace(old_marker, AP_CHECK_MARKER)
                break

    if AP_CHECK_MARKER not in text:
        gd = _with_nl(_escaped_gd(SLOT_AP_CHECK_GDSCRIPT), newline)
        anchor = _with_nl("\t\tif not modded or (modded and inherit_effects):\n\t\t\tmatch t:\n", newline)
        if anchor not in text:
            raise ValueError("Could not find Slot Icon.tscn match anchor for AP Check effect")
        text = text.replace(anchor, anchor + gd, 1)

    if AP_CHECK_SEND_MARKER not in text:
        gd_send = _with_nl(_escaped_gd(SLOT_AP_CHECK_SEND_GDSCRIPT), newline)
        destroy_anchor = _with_nl("func destroy():\n\tvar target = self\n", newline)
        if destroy_anchor not in text:
            raise ValueError("Could not find Slot Icon.tscn destroy anchor for AP Check sender")
        text = text.replace(destroy_anchor, gd_send + newline + destroy_anchor, 1)

        destroy_body_anchor = destroy_anchor + _with_nl('\tif not target.destroyed and target.type != \\"empty\\":\n', newline)
        inject = destroy_body_anchor + _with_nl('\t\tif target.type == \\"ap_check\\":\n\t\t\t_ap_lbal_queue_next_ap_check()\n', newline)
        if destroy_body_anchor not in text:
            raise ValueError("Could not find Slot Icon.tscn destroy body anchor for AP Check sender")
        text = text.replace(destroy_body_anchor, inject, 1)

    text = _repair_single_check_file_writers_v117(text)
    text = _repair_slot_bad_backslash_v165(text)
    text = _upgrade_slot_ap_check_queue_v163(text)
    text = _repair_slot_bad_backslash_v165(text)
    return text

def _missing_texture_replacements(data: bytes, entries: Iterable[PckEntry]) -> Dict[str, bytes]:
    """Replace only the real PCK missing texture files with the red-X STEX files.

    This does not add every symbol/item as a mod. It only swaps the base missing
    image used when LBAL renders a ? icon.
    """
    replacements: Dict[str, bytes] = {}
    try:
        missing_12 = base64.b64decode(AP_MISSING_STEX_12_B64)
        missing_22 = base64.b64decode(AP_MISSING_STEX_22_B64)
    except Exception:
        return replacements

    for entry in entries:
        path = str(entry.path)
        blob: Optional[bytes] = None

        if path.startswith("res://.import/missing.png-") and path.endswith(".stex"):
            # Inline description icons, e.g. the pink ? inside item descriptions.
            blob = missing_12
        elif path.startswith("res://.import/item_missing.png-") and path.endswith(".stex"):
            # Missing item/card art.
            blob = missing_22

        if blob is not None:
            current = data[entry.offset:entry.offset + entry.size]
            if current != blob:
                replacements[path] = blob

    return replacements

def patch_pck_bytes(data: bytes) -> Tuple[bytes, bool]:
    _header, entries = _parse_pck(data)
    replacements: Dict[str, bytes] = {}

    popup = _extract_entry(data, entries, "res://Pop-up.tscn")
    popup_text = popup.decode("utf-8")
    patched_popup_text = _patch_popup_tscn(popup_text)
    if patched_popup_text != popup_text:
        replacements["res://Pop-up.tscn"] = patched_popup_text.encode("utf-8")

    main = _extract_entry(data, entries, "res://Main.tscn")
    main_text = main.decode("utf-8")
    patched_main_text = _upgrade_vanilla_effect_references_v22(_patch_main_tscn(main_text))
    if patched_main_text != main_text:
        replacements["res://Main.tscn"] = patched_main_text.encode("utf-8")

    slot = _extract_entry(data, entries, "res://Slot Icon.tscn")
    slot_text = slot.decode("utf-8")
    patched_slot_text = _upgrade_vanilla_effect_references_v22(_patch_slot_icon_tscn(slot_text))
    if patched_slot_text != slot_text:
        replacements["res://Slot Icon.tscn"] = patched_slot_text.encode("utf-8")

    # V41: patch the actual base PCK missing textures so inline <icon_?> question
    # marks use the uploaded red-X image without adding every symbol/item as a mod.
    replacements.update(_missing_texture_replacements(data, entries))

    if not replacements:
        return data, False

    new_data = _replace_entry_and_repack(data, replacements)
    _, new_entries = _parse_pck(new_data)
    new_popup = _extract_entry(new_data, new_entries, "res://Pop-up.tscn").decode("utf-8")
    new_main = _extract_entry(new_data, new_entries, "res://Main.tscn").decode("utf-8")
    new_slot = _extract_entry(new_data, new_entries, "res://Slot Icon.tscn").decode("utf-8")
    if 'replace(\\"\\\\\", \\"/\\")' in new_popup:
        raise ValueError("Patch verification failed: broken backslash string remains after repack")
    if PATCH_MARKER not in new_popup:
        raise ValueError("Patch verification failed: live marker missing after repack")
    if "AP_ITEM_RARITY_FALLBACK_PATCH_V26" not in new_popup or ("AP_ITEM_RARITY_SELECT_PATCH_V47" not in new_popup and "AP_ITEM_RARITY_SELECT_PATCH_V65" not in new_popup):
        raise ValueError("Patch verification failed: V26/V65 item rarity marker missing after repack")
    if DEATHLINK_PATCH_MARKER not in new_popup or "AP_PAYMENT_SEND_PATCH_V2" not in new_popup:
        raise ValueError("Patch verification failed: DeathLink marker missing after repack")
    if DEATHLINK_HOOK_MARKER not in new_popup:
        raise ValueError("Patch verification failed: DeathLink hook marker missing after repack")
    if AP_CHECK_MARKER not in new_main or AP_CHECK_MARKER not in new_slot:
        raise ValueError("Patch verification failed: AP Check marker missing after repack")
    if OVERFLOW_GUARD_MARKER_V64 not in new_main or OVERFLOW_GUARD_MARKER_V64 not in new_slot:
        raise ValueError("Patch verification failed: V64 overflow guard marker missing after repack")
    if POPUP_SAFE_NODE_MARKER_V64 not in new_popup:
        raise ValueError("Patch verification failed: V64 popup safe-node marker missing after repack")
    if EMPTY_ITEM_POOL_MARKER_V65 not in new_popup:
        raise ValueError("Patch verification failed: V65 empty item pool marker missing after repack")
    if MAIN_DEATHLINK_PATCH_MARKER not in new_main or "	_ap_lbal_main_poll_deathlink(delta)" not in new_main:
        raise ValueError("Patch verification failed: Main DeathLink poll marker missing after repack")
    if "_ap_lbal_main_write_deathlink_send" not in new_main:
        raise ValueError("Patch verification failed: Main DeathLink send helper missing after repack")
    if AP_CHECK_SEND_MARKER not in new_slot:
        raise ValueError("Patch verification failed: AP Check sender marker missing after repack")
    return new_data, True


def _steam_library_roots() -> List[Path]:
    roots: List[Path] = []
    if os.name != "nt":
        return roots

    candidates = [
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Steam",
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Steam",
    ]

    def add(root: Path) -> None:
        if root.exists() and root not in roots:
            roots.append(root)

    for steam_root in candidates:
        add(steam_root)
        vdf = steam_root / "steamapps" / "libraryfolders.vdf"
        if vdf.exists():
            try:
                text = vdf.read_text(encoding="utf-8", errors="ignore")
                for match in re.finditer(r'"path"\s+"([^"]+)"', text):
                    add(Path(match.group(1).replace("\\\\", "\\")))
            except OSError:
                pass

    return roots


def _candidate_pck_paths_from_base(base: Path) -> List[Path]:
    out: List[Path] = []
    try:
        base = base.resolve()
    except Exception:
        pass
    for root in [base] + list(base.parents):
        out.append(root / PCK_NAME)
        out.append(root / "Luck be a Landlord" / PCK_NAME)
        out.append(root / "steamapps" / "common" / "Luck be a Landlord" / PCK_NAME)
    return out

def _configured_pck_path(bridge_path: Optional[Path] = None) -> Optional[Path]:
    # Priority 1: environment variable.
    env_path = os.environ.get("LBAL_PCK_PATH")
    if env_path:
        p = Path(env_path.strip().strip('"'))
        if p.is_file():
            return p

    # Priority 2: config file written by /setpckpath.
    config_files: List[Path] = []
    if bridge_path is not None:
        config_files.append(Path(bridge_path) / "lbal_pck_path.txt")
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        config_files.append(Path(os.environ["LOCALAPPDATA"]) / "LuckBeALandlordAP" / "lbal_pck_path.txt")
    for cfg in config_files:
        try:
            if cfg.is_file():
                p = Path(cfg.read_text(encoding="utf-8", errors="ignore").strip().strip('"'))
                if p.is_file():
                    return p
        except OSError:
            pass
    return None

def find_lbal_pck(bridge_path: Optional[Path] = None) -> Optional[Path]:
    configured = _configured_pck_path(bridge_path)
    if configured is not None:
        return configured

    # V111: also search beside the running client/exe and current working dir.
    # This catches copied/non-Steam LBAL folders like the one in the screenshot.
    seen: Set[Path] = set()
    bases: List[Path] = []
    try:
        bases.append(Path.cwd())
    except Exception:
        pass
    try:
        bases.append(Path(sys.executable).resolve().parent)
    except Exception:
        pass
    try:
        bases.append(Path(__file__).resolve().parent)
    except Exception:
        pass

    for base in bases:
        for candidate in _candidate_pck_paths_from_base(base):
            if candidate in seen:
                continue
            seen.add(candidate)
            if candidate.is_file():
                return candidate

    for root in _steam_library_roots():
        direct = root / "steamapps" / "common" / "Luck be a Landlord" / PCK_NAME
        if direct.is_file():
            return direct
        common = root / "steamapps" / "common"
        if common.is_dir():
            for candidate in common.glob("Luck*Landlord*/Luck be a Landlord.pck"):
                if candidate.is_file():
                    return candidate
    return None


def _pck_has_current_patch(data: bytes) -> bool:
    try:
        _, entries = _parse_pck(data)
        popup = _extract_entry(data, entries, "res://Pop-up.tscn").decode("utf-8", errors="ignore")
        main = _extract_entry(data, entries, "res://Main.tscn").decode("utf-8", errors="ignore")
        slot = _extract_entry(data, entries, "res://Slot Icon.tscn").decode("utf-8", errors="ignore")
        return (
            PATCH_MARKER in popup
            and AP_CHECK_MARKER in main
            and MAIN_DEATHLINK_PATCH_MARKER in main
            and "\t_ap_lbal_main_poll_deathlink(delta)" in main
            and AP_CHECK_MARKER in slot
            and AP_CHECK_SEND_MARKER in slot
            and DEATHLINK_PATCH_MARKER in popup
            and DEATHLINK_HOOK_MARKER in popup
            and OVERFLOW_GUARD_MARKER_V64 in main
            and OVERFLOW_GUARD_MARKER_V64 in slot
            and POPUP_SAFE_NODE_MARKER_V64 in popup
            and EMPTY_ITEM_POOL_MARKER_V65 in popup
        )
    except Exception:
        return False


def _pck_has_any_ap_patch(data: bytes) -> bool:
    try:
        _, entries = _parse_pck(data)
        popup = _extract_entry(data, entries, "res://Pop-up.tscn").decode("utf-8", errors="ignore")
        main = _extract_entry(data, entries, "res://Main.tscn").decode("utf-8", errors="ignore")
        slot = _extract_entry(data, entries, "res://Slot Icon.tscn").decode("utf-8", errors="ignore")
        return (PATCH_MARKER in popup or any(m in popup for m in OLD_PATCH_MARKERS) or DEATHLINK_PATCH_MARKER in popup or AP_CHECK_MARKER in main or AP_CHECK_MARKER in slot or any(m in main for m in OLD_AP_CHECK_MARKERS) or any(m in slot for m in OLD_AP_CHECK_MARKERS) or AP_CHECK_SEND_MARKER in slot)
    except Exception:
        return False


def auto_patch_lbal_pck(bridge_path: Path) -> Dict[str, object]:
    status: Dict[str, object] = {"patched": False, "already_patched": False, "pck_path": None, "backup_path": None, "backup_created": False, "error": None}
    pck_path = find_lbal_pck(bridge_path)
    if pck_path is None:
        status["error"] = "Could not find Luck be a Landlord.pck. Use /setpckpath with the full path to Luck be a Landlord.pck, or set LBAL_PCK_PATH."
        return status

    status["pck_path"] = str(pck_path)

    # V9: keep the backup beside the installed game PCK instead of only in AppData.
    # For the default Steam install this becomes:
    #   C:\Program Files (x86)\Steam\steamapps\common\Luck be a Landlord\LBAL.Pck\
    # This makes it easier to find and restore manually.
    backup_dir = pck_path.parent / BACKUP_FOLDER_NAME
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / BACKUP_FILE_NAME
    patched_copy_path = backup_dir / PATCHED_COPY_NAME
    installed_snapshot_path = backup_dir / "Luck be a Landlord.installed-before-v9.pck"
    legacy_backup_path = bridge_path / BACKUP_FOLDER_NAME / BACKUP_FILE_NAME
    status["backup_path"] = str(backup_path)
    status["backup_folder"] = str(backup_dir)
    status["legacy_backup_path"] = str(legacy_backup_path)

    data = pck_path.read_bytes()
    installed_has_any_patch = _pck_has_any_ap_patch(data)

    # If an older build already made a clean backup in AppData, migrate/copy it
    # into the game folder so the user always sees LBAL.Pck next to the PCK.
    if not backup_path.exists() and legacy_backup_path.exists():
        shutil.copy2(legacy_backup_path, backup_path)
        status["backup_migrated_from"] = str(legacy_backup_path)

    # If the installed PCK is still vanilla/unpatched, this is the real original.
    # Save it before writing any patched copy.
    if not backup_path.exists() and not installed_has_any_patch:
        shutil.copy2(pck_path, backup_path)
        status["backup_created"] = True

    # If the installed PCK is already patched and the original backup is missing,
    # do not pretend we have the original. Save the current installed file as a
    # snapshot so the user still has something to restore, but tell them Steam
    # verification is needed to recover a clean original.
    if not backup_path.exists() and installed_has_any_patch:
        shutil.copy2(pck_path, installed_snapshot_path)
        status["installed_snapshot_path"] = str(installed_snapshot_path)
        status["backup_warning"] = "Installed PCK was already AP-patched before a clean original backup existed. I saved the current installed PCK beside the game PCK, but use Steam Verify Files if you need a true clean original."

    if _pck_has_current_patch(data):
        status["already_patched"] = True
        status_path = backup_dir / "patch_status.json"
        try:
            status_path.write_text(json.dumps({**status, "updated_at": time.time()}, indent=2), encoding="utf-8")
        except OSError:
            pass
        return status

    # Prefer the clean original backup if available, otherwise patch the currently
    # installed PCK. Patching the current file can recover from the broken V3 parse
    # error because old AP markers are replaced/updated to V5.
    source_data = backup_path.read_bytes() if backup_path.exists() else data
    new_data, changed = patch_pck_bytes(source_data)
    if changed:
        tmp = pck_path.with_suffix(pck_path.suffix + f".aplive.{os.getpid()}.tmp")
        tmp.write_bytes(new_data)
        os.replace(tmp, pck_path)
        patched_copy_path.write_bytes(new_data)
        status["patched"] = True
        status["patched_copy_path"] = str(patched_copy_path)
    else:
        status["already_patched"] = True

    status_path = backup_dir / "patch_status.json"
    try:
        status_path.write_text(json.dumps({**status, "updated_at": time.time()}, indent=2), encoding="utf-8")
    except OSError:
        pass
    return status


def restore_original_lbal_pck(bridge_path: Path) -> Dict[str, object]:
    status: Dict[str, object] = {"restored": False, "error": None}
    pck_path = find_lbal_pck(bridge_path)
    if pck_path is None:
        status["error"] = "Could not find installed PCK."
        return status

    backup_path = pck_path.parent / BACKUP_FOLDER_NAME / BACKUP_FILE_NAME
    legacy_backup_path = bridge_path / BACKUP_FOLDER_NAME / BACKUP_FILE_NAME
    if not backup_path.exists() and legacy_backup_path.exists():
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(legacy_backup_path, backup_path)
        status["backup_migrated_from"] = str(legacy_backup_path)

    if not backup_path.exists():
        status["error"] = f"Backup does not exist: {backup_path}"
        return status
    shutil.copy2(backup_path, pck_path)
    status["restored"] = True
    status["pck_path"] = str(pck_path)
    status["backup_path"] = str(backup_path)
    return status
