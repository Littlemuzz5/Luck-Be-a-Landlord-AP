from .world import LBALWorld as LBALWorld

from .world import LBALWorld
from .lbal_patch import LBALContentPatch, LBALPatchExtension


from worlds.LauncherComponents import (
    Component,
    Type,
    SuffixIdentifier,
    components,
)


def open_lbal_patch(patch_path=None):
    import traceback
    from Patch import create_rom_file

    try:
        if not patch_path:
            from Utils import open_filename

            patch_path = open_filename(
                "Select LBAL Patch",
                (("LBAL Patch", (".aplbal",)),)
            )

        if not patch_path:
            print("LBAL: No patch selected", flush=True)
            return

        print("LBAL: Starting patch", flush=True)
        print("LBAL: File:", patch_path, flush=True)

        metadata, output = create_rom_file(patch_path)

        print("LBAL: Patch completed!", flush=True)
        print("LBAL: Output:", output, flush=True)

    except Exception:
        print("LBAL: PATCH FAILED", flush=True)
        traceback.print_exc()


lbal_component = Component("Luck be a Landlord Patch Handler", component_type=Type.HIDDEN, func=open_lbal_patch, file_identifier=SuffixIdentifier(".aplbal"),)

components.append(lbal_component)

# Let Open Patch discover the hidden LBAL extension.
for component in components:
    if component.display_name == "Open Patch":
        original_open_patch = component.func

        def open_patch_with_lbal():
            lbal_component.type = Type.CLIENT
            try:
                return original_open_patch()
            finally:
                lbal_component.type = Type.HIDDEN

        component.func = open_patch_with_lbal
        break




