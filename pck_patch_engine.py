import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import sys
import tempfile

ROOT = None 
MANIFEST = None
MAGIC = 0x43504447 


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_index(f):
    f.seek(0)
    header = f.read(84)
    if len(header) != 84:
        raise ValueError('Not a valid PCK: header too short.')
    magic, fmt = struct.unpack_from('<II', header)
    if magic != MAGIC or fmt != 1:
        raise ValueError('Expected a Godot 3 format-1 .pck file.')
    count = struct.unpack('<I', f.read(4))[0]
    if count > 200000:
        raise ValueError('Unexpected PCK file count.')
    entries = []
    for _ in range(count):
        size_bytes = f.read(4)
        if len(size_bytes) != 4:
            raise ValueError('Truncated PCK index.')
        length = struct.unpack('<I', size_bytes)[0]
        if not 0 < length < 100000:
            raise ValueError('Bad PCK resource path length.')
        path = f.read(length).rstrip(b'\0').decode('utf-8')
        offset, size = struct.unpack('<QQ', f.read(16))
        checksum = f.read(16)
        entries.append((path, offset, size, checksum))
    return header, entries


def read_resource(f, entry):
    f.seek(entry[1]); data = f.read(entry[2])
    if len(data) != entry[2]:
        raise ValueError('Truncated resource: ' + entry[0])
    return data


def build_changes(source, indexed):
    changes = {}
    for name, record in MANIFEST['modified'].items():
        if name not in indexed:
            raise ValueError('Missing original game resource: ' + name)
        original = read_resource(source, indexed[name])
        if digest(original) != record['original_sha256']:
            raise ValueError('Original resource differs: ' + name)
        lines = original.decode('utf-8').splitlines(keepends=True)
        operations = json.loads((ROOT / record['delta']).read_text(encoding='utf-8'))['operations']
        for start, end, replacement in reversed(operations):
            lines[start:end] = replacement.splitlines(keepends=True)
        updated = ''.join(lines).encode('utf-8')
        if digest(updated) != record['patched_sha256']:
            raise ValueError('Patched resource verification failed: ' + name)
        changes[name] = updated
    for name, record in MANIFEST['added'].items():
        if name in indexed:
            raise ValueError('AP-only resource already exists in source: ' + name)
        data = (ROOT / record['file']).read_bytes()
        if digest(data) != record['sha256']:
            raise ValueError('AP content checksum failed: ' + name)
        changes[name] = data
    if MANIFEST['removed']:
        raise ValueError('This patcher does not support removing existing game resources.')
    return changes


def write_aligned(f):
    remainder = f.tell() % 16
    if remainder:
        f.write(b'\0' * (16 - remainder))


def write_pck(source, target, header, entries, changes):
    order = [item[0] for item in entries]
    all_names = order + sorted(set(changes) - set(order))
    old = {entry[0]: entry for entry in entries}
    index_size = 84 + 4
    encoded = {}
    for name in all_names:
        data = name.encode('utf-8')
        data += b'\0' * ((-len(data)) % 4)
        encoded[name] = data
        index_size += 4 + len(data) + 8 + 8 + 16
    data_start = (index_size + 15) // 16 * 16
    records = []
    with target.open('wb') as f:
        f.write(b'\0' * data_start)
        for name in all_names:
            write_aligned(f)
            offset = f.tell()
            if name in changes:
                blob = changes[name]
                f.write(blob)
                checksum = hashlib.md5(blob).digest()
                length = len(blob)
            else:
                old_entry = old[name]
                source.seek(old_entry[1])
                length = old_entry[2]
                remaining = length
                while remaining:
                    chunk = source.read(min(1024 * 1024, remaining))
                    if not chunk:
                        raise ValueError('Truncated source resource: ' + name)
                    f.write(chunk)
                    remaining -= len(chunk)
                checksum = old_entry[3]
            records.append((name, offset, length, checksum))
        f.seek(0)
        f.write(header)
        f.write(struct.pack('<I', len(records)))
        for name, offset, length, checksum in records:
            data = encoded[name]
            f.write(struct.pack('<I', len(data)))
            f.write(data)
            f.write(struct.pack('<QQ', offset, length))
            f.write(checksum)
        assert f.tell() <= data_start
    return records


def patch(original_path, output_path):
    original_path = Path(original_path).resolve()
    output_path = Path(output_path).resolve()
    if not original_path.is_file() or original_path.suffix.lower() != '.pck':
        raise ValueError('Select an existing .pck file.')
    if output_path == original_path:
        raise ValueError('Save to a different path to protect your original PCK.')
    with original_path.open('rb') as source:
        header, entries = read_index(source)
        indexed = {entry[0]: entry for entry in entries}
        changes = build_changes(source, indexed)
        fd, temp_name = tempfile.mkstemp(prefix='lbal_patch_', suffix='.pck', dir=output_path.parent)
        os.close(fd)
        temp = Path(temp_name)
        try:
            records = write_pck(source, temp, header, entries, changes)
            with temp.open('rb') as f:
                _, new_entries = read_index(f)
                new_index = {x[0]: x for x in new_entries}
                for name, data in changes.items():
                    if digest(read_resource(f, new_index[name])) != digest(data):
                        raise ValueError('Output verification failed: ' + name)
            os.replace(temp, output_path)
        finally:
            if temp.exists():
                temp.unlink()
    return len(changes), len(records)

