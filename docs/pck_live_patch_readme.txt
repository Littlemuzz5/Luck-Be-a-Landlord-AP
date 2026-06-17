Luck be a Landlord AP live PCK patch
======================================

This APWorld/client bundle adds a local PCK patcher.

What it does when the AP client starts on Windows:
1. Finds your installed Steam PCK:
   Steam/steamapps/common/Luck be a Landlord/Luck be a Landlord.pck
2. Creates this backup folder:
   Steam/steamapps/common/Luck be a Landlord/LBAL.Pck/
3. Copies the original PCK there as:
   Luck be a Landlord.original.pck
4. Rebuilds your installed PCK with a small patch inside Pop-up.tscn.

The patch makes LBAL read ap_state.json while the game is open and filter the
Add Symbol / Add Item / Add Essence choices from the AP live pool.

If Steam is installed somewhere unusual, set this environment variable before
starting the AP client:
   LBAL_PCK_PATH=C:\full\path\to\Luck be a Landlord.pck

To restore manually:
- Close the game.
- Copy Steam/steamapps/common/Luck be a Landlord/LBAL.Pck/Luck be a Landlord.original.pck
  back over your installed Luck be a Landlord.pck.

You still need to restart the game once after the PCK patch is first installed.
After that, AP unlocks should update the next symbol/item/essence choice without
restarting the game.


V2 note: the PCK patcher now patches three places:
- Pop-up.tscn for live symbol/item/essence filtering.
- Main.tscn to register the ap_check symbol in the game database and load ap_check.png from the AP bridge folder.
- Slot Icon.tscn so ap_check destroys itself after giving its value.

The AP client also writes ap_check.png into the bridge/userdata folders before patching.

V4 fix notes:
- Fixes the Godot parse error caused by a bad escaped backslash in the V3 LOCALAPPDATA path line.
- Creates the LBAL.Pck backup folder before checking whether the PCK is already patched.
- If the installed PCK is clean, saves it as Luck be a Landlord.original.pck before patching.
- If the installed PCK was already AP-patched and no clean backup exists, saves Luck be a Landlord.installed-before-v4.pck as a snapshot and recommends Steam Verify Files for a clean original.

V5 fix notes:
- AP Check is now registered as a modded symbol with display_name = AP Check.
- AP Check description now matches the pre-live-update version.
- Older V1 AP Check PCK patches are upgraded instead of being skipped.
- V5 also uses a safe regex replacement so upgraded V4 PCKs keep the escaped backslash path intact.


V9 fix notes:
- The backup folder is now created beside the installed PCK instead of only in AppData.
- Default Steam path: C:\Program Files (x86)\Steam\steamapps\common\Luck be a Landlord\LBAL.Pck\
- If an older AppData backup exists, the patcher copies it into the new game-folder backup location.


V10 generation fix: unlock rewards are now classified as Progression+Useful, not Useful-only, so AP generation can place all symbol/item/essence unlocks without FillError while still showing them as useful-tagged unlocks.
