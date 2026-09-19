from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Entrance, Region

if TYPE_CHECKING:
    from .world import LBALWorld

# A region is a container for locations ("checks"), which connects to other regions via "Entrance" objects.
# Many games will model their Regions after physical in-game places, but you can also have more abstract regions.
# For a location to be in logic, its containing region must be reachable.
# The Entrances connecting regions can have rules - more on that in rules.py.
# This makes regions especially useful for traversal logic ("Can the player reach this part of the map?")

# Every location must be inside a region, and you must have at least one region.
# This is why we create regions first, and then later we create the locations (in locations.py).


def create_and_connect_regions(world: LBALWorld) -> None:
    create_all_regions(world)
    connect_regions(world)

def create_all_regions(world: LBALWorld) -> None:
    Floor_1 = Region("Floor 1", world.player, world.multiworld)

    Progressive_AP_1_10 = Region("Progressive AP 1-10", world.player, world.multiworld)
    Progressive_AP_11_20 = Region("Progressive AP 11-20", world.player, world.multiworld)
    Progressive_AP_21_30 = Region("Progressive AP 21-30", world.player, world.multiworld)
    Progressive_AP_31_40 = Region("Progressive AP 31-40", world.player, world.multiworld)
    Progressive_AP_41_50 = Region("Progressive AP 41-50", world.player, world.multiworld)
    Progressive_AP_51_60 = Region("Progressive AP 51-60", world.player, world.multiworld)
    Progressive_AP_61_70 = Region("Progressive AP 61-70", world.player, world.multiworld)
    Progressive_AP_71_80 = Region("Progressive AP 71-80", world.player, world.multiworld)
    Progressive_AP_81_90 = Region("Progressive AP 81-90", world.player, world.multiworld)
    Progressive_AP_91_100 = Region("Progressive AP 91-100", world.player, world.multiworld)
    Progressive_AP_101_110 = Region("Progressive AP 101-110", world.player, world.multiworld)
    Progressive_AP_111_120 = Region("Progressive AP 111-120", world.player, world.multiworld)
    Progressive_AP_121_130 = Region("Progressive AP 121-130", world.player, world.multiworld)
    Progressive_AP_131_140 = Region("Progressive AP 131-140", world.player, world.multiworld)
    Progressive_AP_141_150 = Region("Progressive AP 141-150", world.player, world.multiworld)

    Symbol_Send = Region("Symbol Send", world.player, world.multiworld)

    regions = [
        Floor_1,
        Progressive_AP_1_10,
        Progressive_AP_11_20,
        Progressive_AP_21_30,
        Progressive_AP_31_40,
        Progressive_AP_41_50,
        Progressive_AP_51_60,
        Progressive_AP_61_70,
        Progressive_AP_71_80,
        Progressive_AP_81_90,
        Progressive_AP_91_100,
        Progressive_AP_101_110,
        Progressive_AP_111_120,
        Progressive_AP_121_130,
        Progressive_AP_131_140,
        Progressive_AP_141_150,
        Symbol_Send,
    ]

    if world.options.Rare:
        regions.append(
            Region("Rare", world.player, world.multiworld)
        )

    if world.options.VeryRare:
        regions.append(
            Region("Very Rare", world.player, world.multiworld)
        )

    for floor_number in range(2, 21):
        if str(floor_number) in world.options.Floors.value:
            regions.append(
                Region(
                    f"Floor {floor_number}",
                    world.player,
                    world.multiworld
                )
            )

    world.multiworld.regions += regions


def connect_regions(world: LBALWorld) -> None:
    # We have regions now, but still need to connect them to each other.
    # But wait, we no longer have access to the region variables we created in create_all_regions()!
    # Luckily, once you've submitted your regions to multiworld.regions,
    # you can get them at any time using world.get_region(...).
    Floor_1 = world.get_region("Floor 1")
    Progressive_AP_1_10 = world.get_region("Progressive AP 1-10")
    Progressive_AP_11_20 = world.get_region("Progressive AP 11-20")
    Progressive_AP_21_30 = world.get_region("Progressive AP 21-30")
    Progressive_AP_31_40 = world.get_region("Progressive AP 31-40")
    Progressive_AP_41_50 = world.get_region("Progressive AP 41-50")
    Progressive_AP_51_60 = world.get_region("Progressive AP 51-60")
    Progressive_AP_61_70 = world.get_region("Progressive AP 61-70")
    Progressive_AP_71_80 = world.get_region("Progressive AP 71-80")
    Progressive_AP_81_90 = world.get_region("Progressive AP 81-90")
    Progressive_AP_91_100 = world.get_region("Progressive AP 91-100")
    Progressive_AP_101_110 = world.get_region("Progressive AP 101-110")
    Progressive_AP_111_120 = world.get_region("Progressive AP 111-120")
    Progressive_AP_121_130 = world.get_region("Progressive AP 121-130")
    Progressive_AP_131_140 = world.get_region("Progressive AP 131-140")
    Progressive_AP_141_150 = world.get_region("Progressive AP 141-150")
    Symbol_Send = world.get_region("Symbol Send")

    


    # Okay, now we can get connecting. For this, we need to create Entrances.
    # Entrances are inherently one-way, but crucially, AP assumes you can always return to the origin region.
    # One way to create an Entrance is by calling the Entrance constructor.
    #overworld_to_bottom_right_room = Entrance(world.player, "Overworld to Bottom Right Room", parent=overworld)
    #overworld.exits.append(overworld_to_bottom_right_room)

    
    # You can then connect the Entrance to the target region.
    #overworld_to_bottom_right_room.connect(bottom_right_room)

    # An even easier way is to use the region.connect helper.
    #overworld.connect(right_room, "Overworld to Right Room")
    #right_room.connect(final_boss_room, "Right Room to Final Boss Room")
    Floor_1.connect(Progressive_AP_1_10, "Floor 1 to Progressive AP")
    Floor_1.connect(Symbol_Send, "Floor 1 to Symbol_Send")
    Progressive_AP_1_10.connect(Progressive_AP_11_20, "Progressive AP to Progressive AP 2", lambda state: state.has("Progressive AP", world.player, 1))
    Progressive_AP_11_20.connect(Progressive_AP_21_30, "Progressive AP 2 to Progressive AP 3", lambda state: state.has("Progressive AP", world.player, 2))
    Progressive_AP_21_30.connect(Progressive_AP_31_40, "Progressive AP 3 to Progressive AP 4", lambda state: state.has("Progressive AP", world.player, 3))
    Progressive_AP_31_40.connect(Progressive_AP_41_50, "Progressive AP 4 to Progressive AP 5", lambda state: state.has("Progressive AP", world.player, 4))
    Progressive_AP_41_50.connect(Progressive_AP_51_60, "Progressive AP 5 to Progressive AP 6", lambda state: state.has("Progressive AP", world.player, 5))
    Progressive_AP_51_60.connect(Progressive_AP_61_70, "Progressive AP 6 to Progressive AP 7", lambda state: state.has("Progressive AP", world.player, 6))
    Progressive_AP_61_70.connect(Progressive_AP_71_80, "Progressive AP 7 to Progressive AP 8", lambda state: state.has("Progressive AP", world.player, 7))
    Progressive_AP_71_80.connect(Progressive_AP_81_90, "Progressive AP 8 to Progressive AP 9", lambda state: state.has("Progressive AP", world.player, 8))
    Progressive_AP_81_90.connect(Progressive_AP_91_100, "Progressive AP 9 to Progressive AP 10", lambda state: state.has("Progressive AP", world.player, 9))
    Progressive_AP_91_100.connect(Progressive_AP_101_110, "Progressive AP 10 to Progressive AP 11", lambda state: state.has("Progressive AP", world.player, 10))
    Progressive_AP_101_110.connect(Progressive_AP_111_120, "Progressive AP 11 to Progressive AP 12", lambda state: state.has("Progressive AP", world.player, 11))
    Progressive_AP_111_120.connect(Progressive_AP_121_130, "Progressive AP 12 to Progressive AP 13", lambda state: state.has("Progressive AP", world.player, 12))
    Progressive_AP_121_130.connect(Progressive_AP_131_140, "Progressive AP 13 to Progressive AP 14", lambda state: state.has("Progressive AP", world.player, 13))
    Progressive_AP_131_140.connect(Progressive_AP_141_150, "Progressive AP 14 to Progressive AP 15", lambda state: state.has("Progressive AP", world.player, 14)) 

    # The region.connect helper even allows adding a rule immediately.
    # We'll talk more about rule creation in the set_all_rules() function in rules.py.
    #overworld.connect(top_left_room, "Overworld to Top Left Room", lambda state: state.has("Key", world.player))

    # Some Entrances may only exist if the player enables certain options.
    # In our case, the Hammer locks the top middle chest in its own room if the hammer option is enabled.
    # In this case, we previously created an extra "Top Middle Room" region that we now need to connect to Overworld.
    
    if "2" in world.options.Floors.value:
        Floor_2 = world.get_region("Floor 2")
        Floor_1.connect(Floor_2, "Floor 1 to Floor 2")

    if "3" in world.options.Floors.value:
        Floor_3 = world.get_region("Floor 3")
        Floor_1.connect(Floor_3, "Floor 1 to Floor 3")

    if "4" in world.options.Floors.value:
        Floor_4 = world.get_region("Floor 4")
        Floor_1.connect(Floor_4, "Floor 1 to Floor 4")    
    
    if "5" in world.options.Floors.value:
        Floor_5 = world.get_region("Floor 5")
        Floor_1.connect(Floor_5, "Floor 1 to Floor 5")

    if "6" in world.options.Floors.value:
        Floor_6 = world.get_region("Floor 6")
        Floor_1.connect(Floor_6, "Floor 1 to Floor 6")

    if "7" in world.options.Floors.value:
        Floor_7 = world.get_region("Floor 7")
        Floor_1.connect(Floor_7, "Floor 1 to Floor 7")

    if "8" in world.options.Floors.value:
        Floor_8 = world.get_region("Floor 8")
        Floor_1.connect(Floor_8, "Floor 1 to Floor 8")

    if "9" in world.options.Floors.value:
        Floor_9 = world.get_region("Floor 9")
        Floor_1.connect(Floor_9, "Floor 1 to Floor 9")

    if "10" in world.options.Floors.value:
        Floor_10 = world.get_region("Floor 10")
        Floor_1.connect(Floor_10, "Floor 1 to Floor 10")

    if "11" in world.options.Floors.value:
        Floor_11 = world.get_region("Floor 11")
        Floor_1.connect(Floor_11, "Floor 1 to Floor 11")

    if "12" in world.options.Floors.value:
        Floor_12 = world.get_region("Floor 12")
        Floor_1.connect(Floor_12, "Floor 1 to Floor 12")

    if "13" in world.options.Floors.value:
        Floor_13 = world.get_region("Floor 13")
        Floor_1.connect(Floor_13, "Floor 1 to Floor 13")

    if "14" in world.options.Floors.value:
        Floor_14 = world.get_region("Floor 14")
        Floor_1.connect(Floor_14, "Floor 1 to Floor 14")

    if "15" in world.options.Floors.value:
        Floor_15 = world.get_region("Floor 15")
        Floor_1.connect(Floor_15, "Floor 1 to Floor 15")

    if "16" in world.options.Floors.value:
        Floor_16 = world.get_region("Floor 16")
        Floor_1.connect(Floor_16, "Floor 1 to Floor 16")

    if "17" in world.options.Floors.value:
        Floor_17 = world.get_region("Floor 17")
        Floor_1.connect(Floor_17, "Floor 1 to Floor 17")

    if "18" in world.options.Floors.value:
        Floor_18 = world.get_region("Floor 18")
        Floor_1.connect(Floor_18, "Floor 1 to Floor 18")

    if "19" in world.options.Floors.value:
        Floor_19 = world.get_region("Floor 19")
        Floor_1.connect(Floor_19, "Floor 1 to Floor 19")

    if "20" in world.options.Floors.value:
        Floor_20 = world.get_region("Floor 20")
        Floor_1.connect(Floor_20, "Floor 1 to Floor 20")
