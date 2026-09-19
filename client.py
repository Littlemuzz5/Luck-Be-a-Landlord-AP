import os
import shutil
from importlib import resources

from Utils import open_filename, messagebox
from worlds.LauncherComponents import Component, Type, components


GAME_EXE = "Luck be a Landlord.exe"
PCK_NAME = "Luck be a Landlord.pck"


def install_lbal_mod():
    # Ask the user to select the actual LBAL executable
    game_exe = open_filename(
        "Select Luck be a Landlord.exe",
        (
            ("Luck be a Landlord", (".exe",)),
        )
    )

    # User pressed Cancel
    if not game_exe:
        return

    # Make sure they selected the correct executable
    if os.path.basename(game_exe).lower() != GAME_EXE.lower():
        messagebox(
            "Wrong Executable",
            "Please select:\n\nLuck be a Landlord.exe",
            error=True
        )
        return

    # Automatically get the directory containing the EXE
    game_dir = os.path.dirname(game_exe)

    target_pck = os.path.join(
        game_dir,
        PCK_NAME
    )

    backup_pck = os.path.join(
        game_dir,
        "Luck be a Landlord.pck.original"
    )

    try:
        # Backup the original PCK the first time only
        if os.path.isfile(target_pck) and not os.path.isfile(backup_pck):
            shutil.copy2(
                target_pck,
                backup_pck
            )

        # Get the modded PCK stored inside the APWorld
        bundled_pck = (
            resources.files(__package__)
            .joinpath("installer")
            .joinpath(PCK_NAME)
        )

        # Copy the new PCK into the same directory as the EXE
        with bundled_pck.open("rb") as source:
            with open(target_pck, "wb") as destination:
                shutil.copyfileobj(
                    source,
                    destination
                )

        messagebox(
            "Luck be a Landlord Archipelago",
            "Archipelago mod installed successfully."
        )

    except PermissionError:
        messagebox(
            "Permission Error",
            "Could not modify the Luck be a Landlord folder.\n\n"
            "Make sure the game is closed and try running "
            "Archipelago as administrator.",
            error=True
        )

    except Exception as e:
        messagebox(
            "Installation Failed",
            f"Could not install Luck be a Landlord.pck:\n\n{e}",
            error=True
        )


components.append(
    Component(
        "Luck be a Landlord",
        component_type=Type.TOOL,
        func=install_lbal_mod,
    )
)