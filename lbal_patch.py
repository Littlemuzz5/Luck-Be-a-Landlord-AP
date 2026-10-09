import json
import os
import pkgutil
from worlds.Files import APProcedurePatch, APPatchExtension
from tkinter import Tk, filedialog
from pathlib import Path
import tempfile
import shutil

_PACKAGE = __package__

class LBALContentPatch(APProcedurePatch):
    
    game = "Luck be a Landlord"
    patch_file_ending = ".aplbal"
    result_file_ending = ".pck"
    hash = None

    procedure = [("patch_lbal", ["manifest.json"])]
    def __init__(self, *args, slot_data=None, seed_name=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.slot_data = slot_data if slot_data is not None else {}
        self.seed_name = str(seed_name or "")

    def patch(self, target: str) -> None:
        """Install patched PCK into selected game folder, never into Downloads."""
        cls = type(self)
        if hasattr(cls, "source_data"):
            delattr(cls, "source_data")
        cls.selected_pck_path = None
        staged = None
        try:
            original_data = cls.get_source_data_with_cache()
            original_path = cls.selected_pck_path
            if original_path.name.casefold() != "luck be a landlord.pck":
                raise ValueError("Select Luck be a Landlord.pck from the game directory.")
            if not (original_path.parent / "Luck be a Landlord.exe").is_file():
                raise ValueError("Selected PCK is not beside Luck be a Landlord.exe.")
            backup = original_path.with_name(original_path.name + ".bak")
            if backup.exists():
                raise FileExistsError("Backup already exists: " + str(backup) + ". Restore/remove it manually before patching again.")
            import tempfile
            with tempfile.NamedTemporaryFile(prefix=".lbal_pending_", suffix=".pck", dir=original_path.parent, delete=False) as f: staged = Path(f.name)
            super().patch(str(staged))
            if not staged.is_file() or staged.stat().st_size < 1024:
                raise RuntimeError("Patch did not produce a valid-sized PCK.")
            import hashlib
            if hashlib.sha256(original_path.read_bytes()).digest() != hashlib.sha256(original_data).digest():
                raise RuntimeError("Original PCK changed while patching; no files replaced.")
            import shutil
            shutil.copy2(original_path, backup)
            try:
                import os
                os.replace(staged, original_path)
                staged = None
            except Exception:
                raise
            print("LBAL patched game installed: " + str(original_path))
            print("Original backed up to: " + str(backup))
        finally:
            if staged is not None:
                staged.unlink(missing_ok=True)
            if hasattr(cls, "source_data"):
                delattr(cls, "source_data")
            cls.selected_pck_path = None

    def write_contents(self, opened_zipfile):
        super().write_contents(opened_zipfile)
        payload = {"seed_name": self.seed_name, "slot_data": self.slot_data}
        opened_zipfile.writestr("slot_data.json", json.dumps(payload, default=str))
        manifest_data = pkgutil.get_data(_PACKAGE, "patch_data/manifest.json")
        if manifest_data is None:
            raise FileNotFoundError("patch_data/manifest.json missing from APWorld")
        opened_zipfile.writestr("manifest.json", manifest_data)
        manifest = json.loads(manifest_data)
        file_names = {item["file"] for item in manifest["added"].values()}
        file_names |= {item["delta"] for item in manifest["modified"].values()}
        for name in sorted(file_names):
            content = pkgutil.get_data(_PACKAGE, "patch_data/" + name)
            if content is None:
                raise FileNotFoundError("Missing AP patch payload: " + name)
            opened_zipfile.writestr(name, content)

    selected_pck_path = None

    @classmethod
    def get_source_data(cls):
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        try:
            path = filedialog.askopenfilename(title="Select original Luck Be a Landlord PCK", filetypes=[("Godot PCK files", "*.pck")])
        finally:
            root.destroy()

        if not path:
            raise FileNotFoundError("No Luck Be a Landlord PCK selected.")

        cls.selected_pck_path = Path(path).resolve()
        with open(path, "rb") as f:
            return f.read()

def write_lbal_patch(world, output_directory):
    patch = LBALContentPatch(player=world.player, player_name=world.multiworld.player_name[world.player], seed_name=world.multiworld.seed_name, slot_data=world.fill_slot_data(),)
    name = (world.multiworld.get_out_file_name_base(world.player) + LBALContentPatch.patch_file_ending)
    patch.write(os.path.join(output_directory, name))


class LBALPatchExtension(APPatchExtension):
    # The game name must match LBALContentPatch.game exactly.
    game = "Luck be a Landlord"

    @staticmethod
    def patch_lbal(caller, original_pck, manifest_name):
        """Build the patched PCK using only files inside this .aplbal."""
        from . import pck_patch_engine as engine

        with tempfile.TemporaryDirectory(prefix="lbal_ap_patch_") as temp_dir:
            temp = Path(temp_dir)
            input_path = temp / "original.pck"
            output_path = temp / "patched.pck"
            input_path.write_bytes(original_pck)

            manifest_bytes = caller.get_file(manifest_name)
            manifest = json.loads(manifest_bytes)
            (temp / "manifest.json").write_bytes(manifest_bytes)
            payloads = {
                *(item["file"] for item in manifest.get("added", {}).values()),
                *(item["delta"] for item in manifest.get("modified", {}).values()),
            }
            for item_path in payloads:
                destination = (temp / item_path).resolve()
                if not destination.is_relative_to(temp.resolve()):
                    raise ValueError("Unsafe patch payload path: " + item_path)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(caller.get_file(item_path))

            engine.ROOT = temp
            engine.MANIFEST = manifest
            engine.patch(input_path, output_path)
            result = output_path.read_bytes()
        return result
