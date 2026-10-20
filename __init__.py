from .world import LBALWorld
from .lbal_patch import LBALContentPatch, LBALPatchExtension
from Patch import create_rom_file
from worlds.LauncherComponents import (Component, Type, SuffixIdentifier, components,)
from os.path import isfile
from Utils import open_filename, messagebox
from worlds.LauncherComponents import (components as registered_components, SuffixIdentifier, Type, identify, get_exe,)
from Launcher import launch as launch_exe
import traceback

def open_lbal_patch(patch_path=None):
    try:
        if not patch_path:
            from Utils import open_filename
            patch_path = open_filename("Select LBAL Patch", (("LBAL Patch", (".aplbal",)),))
        if not patch_path:
            return
        print("LBAL: Starting patch:", patch_path, flush=True)
        metadata, output = create_rom_file(patch_path)
        print("LBAL: Patch completed:", output, flush=True)
    except Exception:
        print("LBAL: PATCH FAILED", flush=True)
        traceback.print_exc()



lbal_component = Component(display_name="Luck be a Landlord", component_type=Type.HIDDEN, func=open_lbal_patch,file_identifier=SuffixIdentifier(".aplbal"),)
components.append(lbal_component)

def open_patch_with_lbal():
    suffixes = []
    for component in registered_components:
        if component.type == Type.CLIENT and isinstance(component.file_identifier, SuffixIdentifier):
            if component.script_name is None or isfile(get_exe(component)[-1]):
                suffixes.extend(component.file_identifier.suffixes)
    suffixes.append(".aplbal")

    try:
        path = open_filename("Select patch", (("Patches", suffixes),))
    except Exception as exc:
        messagebox("Error", str(exc), error=True)
        return
    if not path:
        return

    if str(path).lower().endswith(".aplbal"):
        open_lbal_patch(path)
        return

    file_path, component = identify(path)
    if not file_path or not component:
        print("No registered patch handler for:", path, flush=True)
        return

    executable = get_exe(component)
    if executable is None or not isfile(executable[-1]):
        executable = get_exe("Launcher")
    launch_exe([*executable, file_path], component.cli)


for component in components:
    if component.display_name == "Open Patch":
        component.func = open_patch_with_lbal
        break
