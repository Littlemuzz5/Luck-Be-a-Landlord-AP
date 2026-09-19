from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.options import OptionFilter
from rule_builder.rules import Has, HasAll, Rule
from . import locations
import re




if TYPE_CHECKING:
    from .world import LBALWorld

HAS_KEY = Has("Key")  # Hmm, what could this be? A little foreshadowing perhaps? :) You'll find out if you keep reading!


def get_check_variants(
    world: LBALWorld,
    base_location_name: str,
):
    if world.options.FloorDependentChecks:
        enabled_floors = [1] + sorted(
            int(floor)
            for floor in world.options.Floors.value
        )

        for floor_number in enabled_floors:
            location_name = (
                f"Floor {floor_number} - "
                f"{base_location_name}"
            )

            try:
                yield world.get_location(location_name)
            except KeyError:
                continue

    else:
        try:
            yield world.get_location(base_location_name)
        except KeyError:
            return

def set_all_rules(world: LBALWorld) -> None:
    # In order for AP to generate an item layout that is actually possible for the player to complete,
    # we need to define rules for our Entrances and Locations.
    # Note: Regions do not have rules, the Entrances connecting them do!
    # We'll do entrances first, then locations, and then finally we set our victory condition.

    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world: LBALWorld) -> None:
    # First, we need to actually grab our entrances. Luckily, there is a helper method for this.
    #overworld_to_bottom_right_room = world.get_entrance("Overworld to Bottom Right Room")
    #overworld_to_top_left_room = world.get_entrance("Overworld to Top Left Room")
    #right_room_to_final_boss_room = world.get_entrance("Right Room to Final Boss Room")

    # Now, let's make some rules!
    # First, let's handle the transition from the overworld to the bottom right room,
    # which requires slashing a bush with the Sword.
    # For this, we need a rule that says "player has a Sword".
    # We can use a "Has"-type rule from the rule_builder module for this.
    #can_destroy_bush = Has("Sword")

    # Now we can set our "can_destroy_bush" rule to the entrance which requires slashing a bush to clear the path.
    # The easiest way to do this is by calling world.set_rule, which works for both Locations and Entrances.
    #world.set_rule(overworld_to_bottom_right_room, can_destroy_bush)

    # Conditions can also depend on event items.
    #button_pressed = Has("Top Left Room Button Pressed")
    #world.set_rule(right_room_to_final_boss_room, button_pressed)

    # Some entrance rules may only apply if the player enabled certain options.
    # In our case, if the hammer option is enabled, we need to add the Hammer requirement to the Entrance from
    # Overworld to the Top Middle Room.
    #if world.options.hammer:
       # overworld_to_top_middle_room = world.get_entrance("Overworld to Top Middle Room")
       # can_smash_brick = Has("Hammer")
       # world.set_rule(overworld_to_top_middle_room, can_smash_brick)

    if "2" in world.options.Floors.value:
        Floor_2 = world.get_entrance("Floor 1 to Floor 2")
        can_choose_floor2 = Has("Floor 2 Unlock")
        world.set_rule(Floor_2, can_choose_floor2)

    if "3" in world.options.Floors.value:
        Floor_3 = world.get_entrance("Floor 1 to Floor 3")
        can_choose_floor3 = Has("Floor 3 Unlock")
        world.set_rule(Floor_3, can_choose_floor3)
    
    if "4" in world.options.Floors.value:
        Floor_4 = world.get_entrance("Floor 1 to Floor 4")
        can_choose_floor4 = Has("Floor 4 Unlock")
        world.set_rule(Floor_4, can_choose_floor4)

    if "5" in world.options.Floors.value:
        Floor_5 = world.get_entrance("Floor 1 to Floor 5")
        can_choose_floor5 = Has("Floor 5 Unlock")
        world.set_rule(Floor_5, can_choose_floor5)

    if "6" in world.options.Floors.value:
        Floor_6 = world.get_entrance("Floor 1 to Floor 6")
        can_choose_floor6 = Has("Floor 6 Unlock")
        world.set_rule(Floor_6, can_choose_floor6)

    if "7" in world.options.Floors.value:
        Floor_7 = world.get_entrance("Floor 1 to Floor 7")
        can_choose_floor7 = Has("Floor 7 Unlock")
        world.set_rule(Floor_7, can_choose_floor7)

    if "8" in world.options.Floors.value:
        Floor_8 = world.get_entrance("Floor 1 to Floor 8")
        can_choose_floor8 = Has("Floor 8 Unlock")
        world.set_rule(Floor_8, can_choose_floor8)

    if "9" in world.options.Floors.value:
        Floor_9 = world.get_entrance("Floor 1 to Floor 9")
        can_choose_floor9 = Has("Floor 9 Unlock")
        world.set_rule(Floor_9, can_choose_floor9)

    if "10" in world.options.Floors.value:
        Floor_10 = world.get_entrance("Floor 1 to Floor 10")
        can_choose_floor10 = Has("Floor 10 Unlock")
        world.set_rule(Floor_10, can_choose_floor10)

    if "11" in world.options.Floors.value:
        Floor_11 = world.get_entrance("Floor 1 to Floor 11")
        can_choose_floor11 = Has("Floor 11 Unlock")
        world.set_rule(Floor_11, can_choose_floor11)

    if "12" in world.options.Floors.value:
        Floor_12 = world.get_entrance("Floor 1 to Floor 12")
        can_choose_floor12 = Has("Floor 12 Unlock")
        world.set_rule(Floor_12, can_choose_floor12)

    if "13" in world.options.Floors.value:
        Floor_13 = world.get_entrance("Floor 1 to Floor 13")
        can_choose_floor13 = Has("Floor 13 Unlock")
        world.set_rule(Floor_13, can_choose_floor13)

    if "14" in world.options.Floors.value:
        Floor_14 = world.get_entrance("Floor 1 to Floor 14")
        can_choose_floor14 = Has("Floor 14 Unlock")
        world.set_rule(Floor_14, can_choose_floor14)

    if "15" in world.options.Floors.value:
        Floor_15 = world.get_entrance("Floor 1 to Floor 15")
        can_choose_floor15 = Has("Floor 15 Unlock")
        world.set_rule(Floor_15, can_choose_floor15)

    if "16" in world.options.Floors.value:
        Floor_16 = world.get_entrance("Floor 1 to Floor 16")
        can_choose_floor16 = Has("Floor 16 Unlock")
        world.set_rule(Floor_16, can_choose_floor16)

    if "17" in world.options.Floors.value:
        Floor_17 = world.get_entrance("Floor 1 to Floor 17")
        can_choose_floor17 = Has("Floor 17 Unlock")
        world.set_rule(Floor_17, can_choose_floor17)

    if "18" in world.options.Floors.value:
        Floor_18 = world.get_entrance("Floor 1 to Floor 18")
        can_choose_floor18 = Has("Floor 18 Unlock")
        world.set_rule(Floor_18, can_choose_floor18)

    if "19" in world.options.Floors.value:
        Floor_19 = world.get_entrance("Floor 1 to Floor 19")
        can_choose_floor19 = Has("Floor 19 Unlock")
        world.set_rule(Floor_19, can_choose_floor19)

    if "20" in world.options.Floors.value:
        Floor_20 = world.get_entrance("Floor 1 to Floor 20")
        can_choose_floor20 = Has("Floor 20 Unlock")
        world.set_rule(Floor_20, can_choose_floor20)        

    # So far, we've been using "Has" from the Rule Builder to make our rules.
    # There is another way to make rules that you will see in a lot of older worlds.
    # A rule can just be a function that takes a "state" argument and returns a bool.
    # As a demonstration of what that looks like, let's do it with our final Entrance rule:
    #world.set_rule(overworld_to_top_left_room, lambda state: state.has("Key", world.player))
    # This style is not really recommended anymore, though.
    # Notice how you have to explicitly capture world.player here so that the rule applies to the correct player?
    # Well, Rule Builder does this part for you, inside of world.set_rule.
    # This doesn't just result in shorter code, it also means you can define rules statically (at the module level).
    # APQuest opts to create its Rule objects locally, but just to show what this would look like,
    # we'll re-set the "Overworld to Top Left Room" rule to a constant defined at the top of this file:
    #world.set_rule(overworld_to_top_left_room, HAS_KEY)

    # Beyond these structural advantages,
    # Rule Builder also allows the core AP code to do a lot of under-the-hood optimizations.
    # Rule Builder is quite comprehensive, and even if you have really esoteric rules,
    # you can make custom rules by subclassing CustomRule.

def set_all_location_rules(world: LBALWorld) -> None:
    # Location rules work no differently from Entrance rules.
    # Most of our locations are chests that can simply be opened by walking up to them.
    # Thus, their logical requirements are covered by the Entrance rules of the Entrances that were required to
    # reach the region that the chest sits in.
    # However, our two enemies work differently.
    # Entering the room with the enemy is not enough, you also need to have enough combat items to be able to defeat it.
    # So, we need to set requirements on the Locations themselves.
    # Since combat is a bit more complicated, we'll use this chance to cover some advanced access rule concepts.

    # In "set_all_entrance_rules", we had a rule for a location that doesn't always exist.
    # In this case, we had to check for its existence (by checking the player's chosen options) before setting the rule.
    # Other times, you may have a situation where a location can have two different rules depending on the options.
    # In our case, the enemy in the right room has more health if hard mode is selected,
    # so ontop of the Sword, the player will either need one more health or a Shield in hard mode.
    # First, let's make our sword condition.
    #can_defeat_basic_enemy: Rule = Has("Sword")

    floor_1_payment_1: Rule = Has("Progressive AP", count=1)
    floor_1_payment_2: Rule = Has("Progressive AP", count=2)
    floor_1_payment_3: Rule = Has("Progressive AP", count=3)
    floor_1_payment_4: Rule = Has("Progressive AP", count=4)
    floor_1_payment_5: Rule = Has("Progressive AP", count=5)
    floor_1_payment_6: Rule = Has("Progressive AP", count=6)
    floor_1_payment_7: Rule = Has("Progressive AP", count=7)
    floor_1_payment_8: Rule = Has("Progressive AP", count=8)
    floor_1_payment_9: Rule = Has("Progressive AP", count=9)
    floor_1_payment_10: Rule = Has("Progressive AP", count=10)
    floor_1_payment_11: Rule = Has("Progressive AP", count=11)
    floor_1_payment_12: Rule = Has("Progressive AP", count=12)

    floor_2_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 2 Unlock")
    floor_2_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 2 Unlock")
    floor_2_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 2 Unlock")
    floor_2_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 2 Unlock")
    floor_2_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 2 Unlock")
    floor_2_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 2 Unlock")
    floor_2_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 2 Unlock")
    floor_2_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 2 Unlock")
    floor_2_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 2 Unlock")
    floor_2_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 2 Unlock")
    floor_2_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 2 Unlock")
    floor_2_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 2 Unlock")

    floor_3_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 3 Unlock")
    floor_3_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 3 Unlock")
    floor_3_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 3 Unlock")
    floor_3_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 3 Unlock")
    floor_3_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 3 Unlock")
    floor_3_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 3 Unlock")
    floor_3_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 3 Unlock")
    floor_3_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 3 Unlock")
    floor_3_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 3 Unlock")
    floor_3_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 3 Unlock")
    floor_3_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 3 Unlock")
    floor_3_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 3 Unlock")

    floor_4_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 4 Unlock")
    floor_4_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 4 Unlock")
    floor_4_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 4 Unlock")
    floor_4_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 4 Unlock")
    floor_4_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 4 Unlock")
    floor_4_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 4 Unlock")
    floor_4_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 4 Unlock")
    floor_4_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 4 Unlock")
    floor_4_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 4 Unlock")
    floor_4_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 4 Unlock")
    floor_4_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 4 Unlock")
    floor_4_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 4 Unlock")

    floor_5_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 5 Unlock")
    floor_5_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 5 Unlock")
    floor_5_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 5 Unlock")
    floor_5_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 5 Unlock")
    floor_5_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 5 Unlock")
    floor_5_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 5 Unlock")
    floor_5_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 5 Unlock")
    floor_5_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 5 Unlock")
    floor_5_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 5 Unlock")
    floor_5_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 5 Unlock")
    floor_5_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 5 Unlock")
    floor_5_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 5 Unlock")

    floor_6_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 6 Unlock")
    floor_6_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 6 Unlock")
    floor_6_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 6 Unlock")
    floor_6_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 6 Unlock")
    floor_6_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 6 Unlock")
    floor_6_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 6 Unlock")
    floor_6_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 6 Unlock")
    floor_6_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 6 Unlock")
    floor_6_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 6 Unlock")
    floor_6_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 6 Unlock")
    floor_6_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 6 Unlock")
    floor_6_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 6 Unlock")

    floor_7_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 7 Unlock")
    floor_7_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 7 Unlock")
    floor_7_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 7 Unlock")
    floor_7_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 7 Unlock")
    floor_7_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 7 Unlock")
    floor_7_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 7 Unlock")
    floor_7_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 7 Unlock")
    floor_7_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 7 Unlock")
    floor_7_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 7 Unlock")
    floor_7_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 7 Unlock")
    floor_7_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 7 Unlock")
    floor_7_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 7 Unlock")

    floor_8_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 8 Unlock")
    floor_8_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 8 Unlock")
    floor_8_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 8 Unlock")
    floor_8_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 8 Unlock")
    floor_8_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 8 Unlock")
    floor_8_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 8 Unlock")
    floor_8_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 8 Unlock")
    floor_8_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 8 Unlock")
    floor_8_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 8 Unlock")
    floor_8_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 8 Unlock")
    floor_8_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 8 Unlock")
    floor_8_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 8 Unlock")

    floor_9_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 9 Unlock")
    floor_9_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 9 Unlock")
    floor_9_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 9 Unlock")
    floor_9_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 9 Unlock")
    floor_9_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 9 Unlock")
    floor_9_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 9 Unlock")
    floor_9_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 9 Unlock")
    floor_9_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 9 Unlock")
    floor_9_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 9 Unlock")
    floor_9_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 9 Unlock")
    floor_9_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 9 Unlock")
    floor_9_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 9 Unlock")

    floor_10_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 10 Unlock")
    floor_10_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 10 Unlock")
    floor_10_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 10 Unlock")
    floor_10_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 10 Unlock")
    floor_10_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 10 Unlock")
    floor_10_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 10 Unlock")
    floor_10_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 10 Unlock")
    floor_10_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 10 Unlock")
    floor_10_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 10 Unlock")
    floor_10_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 10 Unlock")
    floor_10_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 10 Unlock")
    floor_10_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 10 Unlock")

    floor_11_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 11 Unlock")
    floor_11_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 11 Unlock")
    floor_11_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 11 Unlock")
    floor_11_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 11 Unlock")
    floor_11_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 11 Unlock")
    floor_11_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 11 Unlock")
    floor_11_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 11 Unlock")
    floor_11_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 11 Unlock")
    floor_11_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 11 Unlock")
    floor_11_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 11 Unlock")
    floor_11_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 11 Unlock")
    floor_11_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 11 Unlock")

    floor_12_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 12 Unlock")
    floor_12_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 12 Unlock")
    floor_12_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 12 Unlock")
    floor_12_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 12 Unlock")
    floor_12_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 12 Unlock")
    floor_12_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 12 Unlock")
    floor_12_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 12 Unlock")
    floor_12_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 12 Unlock")
    floor_12_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 12 Unlock")
    floor_12_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 12 Unlock")
    floor_12_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 12 Unlock")
    floor_12_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 12 Unlock")

    floor_13_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 13 Unlock")
    floor_13_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 13 Unlock")
    floor_13_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 13 Unlock")
    floor_13_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 13 Unlock")
    floor_13_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 13 Unlock")
    floor_13_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 13 Unlock")
    floor_13_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 13 Unlock")
    floor_13_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 13 Unlock")
    floor_13_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 13 Unlock")
    floor_13_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 13 Unlock")
    floor_13_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 13 Unlock")
    floor_13_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 13 Unlock")

    floor_14_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 14 Unlock")
    floor_14_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 14 Unlock")
    floor_14_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 14 Unlock")
    floor_14_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 14 Unlock")
    floor_14_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 14 Unlock")
    floor_14_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 14 Unlock")
    floor_14_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 14 Unlock")
    floor_14_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 14 Unlock")
    floor_14_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 14 Unlock")
    floor_14_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 14 Unlock")
    floor_14_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 14 Unlock")
    floor_14_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 14 Unlock")

    floor_15_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 15 Unlock")
    floor_15_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 15 Unlock")
    floor_15_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 15 Unlock")
    floor_15_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 15 Unlock")
    floor_15_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 15 Unlock")
    floor_15_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 15 Unlock")
    floor_15_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 15 Unlock")
    floor_15_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 15 Unlock")
    floor_15_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 15 Unlock")
    floor_15_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 15 Unlock")
    floor_15_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 15 Unlock")
    floor_15_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 15 Unlock")

    floor_16_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 16 Unlock")
    floor_16_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 16 Unlock")
    floor_16_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 16 Unlock")
    floor_16_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 16 Unlock")
    floor_16_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 16 Unlock")
    floor_16_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 16 Unlock")
    floor_16_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 16 Unlock")
    floor_16_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 16 Unlock")
    floor_16_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 16 Unlock")
    floor_16_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 16 Unlock")
    floor_16_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 16 Unlock")
    floor_16_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 16 Unlock")

    floor_17_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 17 Unlock")
    floor_17_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 17 Unlock")
    floor_17_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 17 Unlock")
    floor_17_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 17 Unlock")
    floor_17_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 17 Unlock")
    floor_17_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 17 Unlock")
    floor_17_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 17 Unlock")
    floor_17_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 17 Unlock")
    floor_17_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 17 Unlock")
    floor_17_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 17 Unlock")
    floor_17_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 17 Unlock")
    floor_17_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 17 Unlock")

    floor_18_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 18 Unlock")
    floor_18_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 18 Unlock")
    floor_18_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 18 Unlock")
    floor_18_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 18 Unlock")
    floor_18_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 18 Unlock")
    floor_18_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 18 Unlock")
    floor_18_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 18 Unlock")
    floor_18_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 18 Unlock")
    floor_18_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 18 Unlock")
    floor_18_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 18 Unlock")
    floor_18_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 18 Unlock")
    floor_18_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 18 Unlock")

    floor_19_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 19 Unlock")
    floor_19_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 19 Unlock")
    floor_19_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 19 Unlock")
    floor_19_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 19 Unlock")
    floor_19_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 19 Unlock")
    floor_19_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 19 Unlock")
    floor_19_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 19 Unlock")
    floor_19_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 19 Unlock")
    floor_19_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 19 Unlock")
    floor_19_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 19 Unlock")
    floor_19_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 19 Unlock")
    floor_19_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 19 Unlock")

    floor_20_payment_1: Rule = Has("Progressive AP", count=1) & Has("Floor 20 Unlock")
    floor_20_payment_2: Rule = Has("Progressive AP", count=2) & Has("Floor 20 Unlock")
    floor_20_payment_3: Rule = Has("Progressive AP", count=3) & Has("Floor 20 Unlock")
    floor_20_payment_4: Rule = Has("Progressive AP", count=4) & Has("Floor 20 Unlock")
    floor_20_payment_5: Rule = Has("Progressive AP", count=5) & Has("Floor 20 Unlock")
    floor_20_payment_6: Rule = Has("Progressive AP", count=6) & Has("Floor 20 Unlock")
    floor_20_payment_7: Rule = Has("Progressive AP", count=7) & Has("Floor 20 Unlock")
    floor_20_payment_8: Rule = Has("Progressive AP", count=8) & Has("Floor 20 Unlock")
    floor_20_payment_9: Rule = Has("Progressive AP", count=9) & Has("Floor 20 Unlock")
    floor_20_payment_10: Rule = Has("Progressive AP", count=10) & Has("Floor 20 Unlock")
    floor_20_payment_11: Rule = Has("Progressive AP", count=11) & Has("Floor 20 Unlock")
    floor_20_payment_12: Rule = Has("Progressive AP", count=12) & Has("Floor 20 Unlock")

    payment_1: Rule = Has("Progressive AP", count=1)
    payment_2: Rule = Has("Progressive AP", count=2)
    payment_3: Rule = Has("Progressive AP", count=3)
    payment_4: Rule = Has("Progressive AP", count=4)
    payment_5: Rule = Has("Progressive AP", count=5)
    payment_6: Rule = Has("Progressive AP", count=6)
    payment_7: Rule = Has("Progressive AP", count=7)
    payment_8: Rule = Has("Progressive AP", count=8)
    payment_9: Rule = Has("Progressive AP", count=9)
    payment_10: Rule = Has("Progressive AP", count=10)
    payment_11: Rule = Has("Progressive AP", count=11)
    payment_12: Rule = Has("Progressive AP", count=12)



    # Next, we'll check whether hard mode has been chosen in the player options.
    #if world.options.hard_mode:
        # We'll make the condition for "Has a Shield or a Health Upgrade".
        # We can chain two "Has" conditions together with the | operator to make "Has Shield or has Health Upgrade".
        #can_withstand_a_hit = Has("Shield") | Has("Health Upgrade")

        # Now, we chain this rule to our Sword rule.
        # Since we want both conditions to be true, in this case, we have to chain them in an "and" way.
        # For this, we can use the & operator.
        #can_defeat_basic_enemy = can_defeat_basic_enemy & can_withstand_a_hit

    if "2" in world.options.Floors.value:
        floor_2_payment = Has("Floor 2 Unlock")
        floor_2_payment_1 = floor_2_payment & payment_1

    if "2" in world.options.Floors.value:
        floor_2_payment = Has("Floor 2 Unlock")
        floor_2_payment_2 = floor_2_payment & payment_2

    if "2" in world.options.Floors.value:
        floor_2_payment = Has("Floor 2 Unlock")
        floor_2_payment_3 = floor_2_payment & payment_3

    if "2" in world.options.Floors.value:
        floor_2_payment = Has("Floor 2 Unlock")
        floor_2_payment_4 = floor_2_payment & payment_4

    if "2" in world.options.Floors.value:
        floor_2_payment = Has("Floor 2 Unlock")
        floor_2_payment_5 = floor_2_payment & payment_5

    if "2" in world.options.Floors.value:
        floor_2_payment = Has("Floor 2 Unlock")
        floor_2_payment_6 = floor_2_payment & payment_6

    if "2" in world.options.Floors.value:
        floor_2_payment = Has("Floor 2 Unlock")
        floor_2_payment_7 = floor_2_payment & payment_7

    if "2" in world.options.Floors.value:
        floor_2_payment = Has("Floor 2 Unlock")
        floor_2_payment_8 = floor_2_payment & payment_8

    if "2" in world.options.Floors.value:
        floor_2_payment = Has("Floor 2 Unlock")
        floor_2_payment_9 = floor_2_payment & payment_9

    if "2" in world.options.Floors.value:
        floor_2_payment = Has("Floor 2 Unlock")
        floor_2_payment_10 = floor_2_payment & payment_10

    if "2" in world.options.Floors.value:
        floor_2_payment = Has("Floor 2 Unlock")
        floor_2_payment_11 = floor_2_payment & payment_11

    if "2" in world.options.Floors.value:
        floor_2_payment = Has("Floor 2 Unlock")
        floor_2_payment_12 = floor_2_payment & payment_12

    if "3" in world.options.Floors.value:
        floor_3_payment = Has("Floor 3 Unlock")
        floor_3_payment_1 = floor_3_payment & payment_1

    if "3" in world.options.Floors.value:
        floor_3_payment = Has("Floor 3 Unlock")
        floor_3_payment_2 = floor_3_payment & payment_2

    if "3" in world.options.Floors.value:
        floor_3_payment = Has("Floor 3 Unlock")
        floor_3_payment_3 = floor_3_payment & payment_3

    if "3" in world.options.Floors.value:
        floor_3_payment = Has("Floor 3 Unlock")
        floor_3_payment_4 = floor_3_payment & payment_4

    if "3" in world.options.Floors.value:
        floor_3_payment = Has("Floor 3 Unlock")
        floor_3_payment_5 = floor_3_payment & payment_5

    if "3" in world.options.Floors.value:
        floor_3_payment = Has("Floor 3 Unlock")
        floor_3_payment_6 = floor_3_payment & payment_6

    if "3" in world.options.Floors.value:
        floor_3_payment = Has("Floor 3 Unlock")
        floor_3_payment_7 = floor_3_payment & payment_7

    if "3" in world.options.Floors.value:
        floor_3_payment = Has("Floor 3 Unlock")
        floor_3_payment_8 = floor_3_payment & payment_8

    if "3" in world.options.Floors.value:
        floor_3_payment = Has("Floor 3 Unlock")
        floor_3_payment_9 = floor_3_payment & payment_9

    if "3" in world.options.Floors.value:
        floor_3_payment = Has("Floor 3 Unlock")
        floor_3_payment_10 = floor_3_payment & payment_10

    if "3" in world.options.Floors.value:
        floor_3_payment = Has("Floor 3 Unlock")
        floor_3_payment_11 = floor_3_payment & payment_11

    if "3" in world.options.Floors.value:
        floor_3_payment = Has("Floor 3 Unlock")
        floor_3_payment_12 = floor_3_payment & payment_12


    if "4" in world.options.Floors.value:
        floor_4_payment = Has("Floor 4 Unlock")
        floor_4_payment_1 = floor_4_payment & payment_1

    if "4" in world.options.Floors.value:
        floor_4_payment = Has("Floor 4 Unlock")
        floor_4_payment_2 = floor_4_payment & payment_2

    if "4" in world.options.Floors.value:
        floor_4_payment = Has("Floor 4 Unlock")
        floor_4_payment_3 = floor_4_payment & payment_3

    if "4" in world.options.Floors.value:
        floor_4_payment = Has("Floor 4 Unlock")
        floor_4_payment_4 = floor_4_payment & payment_4

    if "4" in world.options.Floors.value:
        floor_4_payment = Has("Floor 4 Unlock")
        floor_4_payment_5 = floor_4_payment & payment_5

    if "4" in world.options.Floors.value:
        floor_4_payment = Has("Floor 4 Unlock")
        floor_4_payment_6 = floor_4_payment & payment_6

    if "4" in world.options.Floors.value:
        floor_4_payment = Has("Floor 4 Unlock")
        floor_4_payment_7 = floor_4_payment & payment_7

    if "4" in world.options.Floors.value:
        floor_4_payment = Has("Floor 4 Unlock")
        floor_4_payment_8 = floor_4_payment & payment_8

    if "4" in world.options.Floors.value:
        floor_4_payment = Has("Floor 4 Unlock")
        floor_4_payment_9 = floor_4_payment & payment_9

    if "4" in world.options.Floors.value:
        floor_4_payment = Has("Floor 4 Unlock")
        floor_4_payment_10 = floor_4_payment & payment_10

    if "4" in world.options.Floors.value:
        floor_4_payment = Has("Floor 4 Unlock")
        floor_4_payment_11 = floor_4_payment & payment_11

    if "4" in world.options.Floors.value:
        floor_4_payment = Has("Floor 4 Unlock")
        floor_4_payment_12 = floor_4_payment & payment_12


    if "5" in world.options.Floors.value:
        floor_5_payment = Has("Floor 5 Unlock")
        floor_5_payment_1 = floor_5_payment & payment_1

    if "5" in world.options.Floors.value:
        floor_5_payment = Has("Floor 5 Unlock")
        floor_5_payment_2 = floor_5_payment & payment_2

    if "5" in world.options.Floors.value:
        floor_5_payment = Has("Floor 5 Unlock")
        floor_5_payment_3 = floor_5_payment & payment_3

    if "5" in world.options.Floors.value:
        floor_5_payment = Has("Floor 5 Unlock")
        floor_5_payment_4 = floor_5_payment & payment_4

    if "5" in world.options.Floors.value:
        floor_5_payment = Has("Floor 5 Unlock")
        floor_5_payment_5 = floor_5_payment & payment_5

    if "5" in world.options.Floors.value:
        floor_5_payment = Has("Floor 5 Unlock")
        floor_5_payment_6 = floor_5_payment & payment_6

    if "5" in world.options.Floors.value:
        floor_5_payment = Has("Floor 5 Unlock")
        floor_5_payment_7 = floor_5_payment & payment_7

    if "5" in world.options.Floors.value:
        floor_5_payment = Has("Floor 5 Unlock")
        floor_5_payment_8 = floor_5_payment & payment_8

    if "5" in world.options.Floors.value:
        floor_5_payment = Has("Floor 5 Unlock")
        floor_5_payment_9 = floor_5_payment & payment_9

    if "5" in world.options.Floors.value:
        floor_5_payment = Has("Floor 5 Unlock")
        floor_5_payment_10 = floor_5_payment & payment_10

    if "5" in world.options.Floors.value:
        floor_5_payment = Has("Floor 5 Unlock")
        floor_5_payment_11 = floor_5_payment & payment_11

    if "5" in world.options.Floors.value:
        floor_5_payment = Has("Floor 5 Unlock")
        floor_5_payment_12 = floor_5_payment & payment_12


    if "6" in world.options.Floors.value:
        floor_6_payment = Has("Floor 6 Unlock")
        floor_6_payment_1 = floor_6_payment & payment_1

    if "6" in world.options.Floors.value:
        floor_6_payment = Has("Floor 6 Unlock")
        floor_6_payment_2 = floor_6_payment & payment_2

    if "6" in world.options.Floors.value:
        floor_6_payment = Has("Floor 6 Unlock")
        floor_6_payment_3 = floor_6_payment & payment_3

    if "6" in world.options.Floors.value:
        floor_6_payment = Has("Floor 6 Unlock")
        floor_6_payment_4 = floor_6_payment & payment_4

    if "6" in world.options.Floors.value:
        floor_6_payment = Has("Floor 6 Unlock")
        floor_6_payment_5 = floor_6_payment & payment_5

    if "6" in world.options.Floors.value:
        floor_6_payment = Has("Floor 6 Unlock")
        floor_6_payment_6 = floor_6_payment & payment_6

    if "6" in world.options.Floors.value:
        floor_6_payment = Has("Floor 6 Unlock")
        floor_6_payment_7 = floor_6_payment & payment_7

    if "6" in world.options.Floors.value:
        floor_6_payment = Has("Floor 6 Unlock")
        floor_6_payment_8 = floor_6_payment & payment_8

    if "6" in world.options.Floors.value:
        floor_6_payment = Has("Floor 6 Unlock")
        floor_6_payment_9 = floor_6_payment & payment_9

    if "6" in world.options.Floors.value:
        floor_6_payment = Has("Floor 6 Unlock")
        floor_6_payment_10 = floor_6_payment & payment_10

    if "6" in world.options.Floors.value:
        floor_6_payment = Has("Floor 6 Unlock")
        floor_6_payment_11 = floor_6_payment & payment_11

    if "6" in world.options.Floors.value:
        floor_6_payment = Has("Floor 6 Unlock")
        floor_6_payment_12 = floor_6_payment & payment_12


    if "7" in world.options.Floors.value:
        floor_7_payment = Has("Floor 7 Unlock")
        floor_7_payment_1 = floor_7_payment & payment_1

    if "7" in world.options.Floors.value:
        floor_7_payment = Has("Floor 7 Unlock")
        floor_7_payment_2 = floor_7_payment & payment_2

    if "7" in world.options.Floors.value:
        floor_7_payment = Has("Floor 7 Unlock")
        floor_7_payment_3 = floor_7_payment & payment_3

    if "7" in world.options.Floors.value:
        floor_7_payment = Has("Floor 7 Unlock")
        floor_7_payment_4 = floor_7_payment & payment_4

    if "7" in world.options.Floors.value:
        floor_7_payment = Has("Floor 7 Unlock")
        floor_7_payment_5 = floor_7_payment & payment_5

    if "7" in world.options.Floors.value:
        floor_7_payment = Has("Floor 7 Unlock")
        floor_7_payment_6 = floor_7_payment & payment_6

    if "7" in world.options.Floors.value:
        floor_7_payment = Has("Floor 7 Unlock")
        floor_7_payment_7 = floor_7_payment & payment_7

    if "7" in world.options.Floors.value:
        floor_7_payment = Has("Floor 7 Unlock")
        floor_7_payment_8 = floor_7_payment & payment_8

    if "7" in world.options.Floors.value:
        floor_7_payment = Has("Floor 7 Unlock")
        floor_7_payment_9 = floor_7_payment & payment_9

    if "7" in world.options.Floors.value:
        floor_7_payment = Has("Floor 7 Unlock")
        floor_7_payment_10 = floor_7_payment & payment_10

    if "7" in world.options.Floors.value:
        floor_7_payment = Has("Floor 7 Unlock")
        floor_7_payment_11 = floor_7_payment & payment_11

    if "7" in world.options.Floors.value:
        floor_7_payment = Has("Floor 7 Unlock")
        floor_7_payment_12 = floor_7_payment & payment_12


    if "8" in world.options.Floors.value:
        floor_8_payment = Has("Floor 8 Unlock")
        floor_8_payment_1 = floor_8_payment & payment_1

    if "8" in world.options.Floors.value:
        floor_8_payment = Has("Floor 8 Unlock")
        floor_8_payment_2 = floor_8_payment & payment_2

    if "8" in world.options.Floors.value:
        floor_8_payment = Has("Floor 8 Unlock")
        floor_8_payment_3 = floor_8_payment & payment_3

    if "8" in world.options.Floors.value:
        floor_8_payment = Has("Floor 8 Unlock")
        floor_8_payment_4 = floor_8_payment & payment_4

    if "8" in world.options.Floors.value:
        floor_8_payment = Has("Floor 8 Unlock")
        floor_8_payment_5 = floor_8_payment & payment_5

    if "8" in world.options.Floors.value:
        floor_8_payment = Has("Floor 8 Unlock")
        floor_8_payment_6 = floor_8_payment & payment_6

    if "8" in world.options.Floors.value:
        floor_8_payment = Has("Floor 8 Unlock")
        floor_8_payment_7 = floor_8_payment & payment_7

    if "8" in world.options.Floors.value:
        floor_8_payment = Has("Floor 8 Unlock")
        floor_8_payment_8 = floor_8_payment & payment_8

    if "8" in world.options.Floors.value:
        floor_8_payment = Has("Floor 8 Unlock")
        floor_8_payment_9 = floor_8_payment & payment_9

    if "8" in world.options.Floors.value:
        floor_8_payment = Has("Floor 8 Unlock")
        floor_8_payment_10 = floor_8_payment & payment_10

    if "8" in world.options.Floors.value:
        floor_8_payment = Has("Floor 8 Unlock")
        floor_8_payment_11 = floor_8_payment & payment_11

    if "8" in world.options.Floors.value:
        floor_8_payment = Has("Floor 8 Unlock")
        floor_8_payment_12 = floor_8_payment & payment_12


    if "9" in world.options.Floors.value:
        floor_9_payment = Has("Floor 9 Unlock")
        floor_9_payment_1 = floor_9_payment & payment_1

    if "9" in world.options.Floors.value:
        floor_9_payment = Has("Floor 9 Unlock")
        floor_9_payment_2 = floor_9_payment & payment_2

    if "9" in world.options.Floors.value:
        floor_9_payment = Has("Floor 9 Unlock")
        floor_9_payment_3 = floor_9_payment & payment_3

    if "9" in world.options.Floors.value:
        floor_9_payment = Has("Floor 9 Unlock")
        floor_9_payment_4 = floor_9_payment & payment_4

    if "9" in world.options.Floors.value:
        floor_9_payment = Has("Floor 9 Unlock")
        floor_9_payment_5 = floor_9_payment & payment_5

    if "9" in world.options.Floors.value:
        floor_9_payment = Has("Floor 9 Unlock")
        floor_9_payment_6 = floor_9_payment & payment_6

    if "9" in world.options.Floors.value:
        floor_9_payment = Has("Floor 9 Unlock")
        floor_9_payment_7 = floor_9_payment & payment_7

    if "9" in world.options.Floors.value:
        floor_9_payment = Has("Floor 9 Unlock")
        floor_9_payment_8 = floor_9_payment & payment_8

    if "9" in world.options.Floors.value:
        floor_9_payment = Has("Floor 9 Unlock")
        floor_9_payment_9 = floor_9_payment & payment_9

    if "9" in world.options.Floors.value:
        floor_9_payment = Has("Floor 9 Unlock")
        floor_9_payment_10 = floor_9_payment & payment_10

    if "9" in world.options.Floors.value:
        floor_9_payment = Has("Floor 9 Unlock")
        floor_9_payment_11 = floor_9_payment & payment_11

    if "9" in world.options.Floors.value:
        floor_9_payment = Has("Floor 9 Unlock")
        floor_9_payment_12 = floor_9_payment & payment_12


    if "10" in world.options.Floors.value:
        floor_10_payment = Has("Floor 10 Unlock")
        floor_10_payment_1 = floor_10_payment & payment_1

    if "10" in world.options.Floors.value:
        floor_10_payment = Has("Floor 10 Unlock")
        floor_10_payment_2 = floor_10_payment & payment_2

    if "10" in world.options.Floors.value:
        floor_10_payment = Has("Floor 10 Unlock")
        floor_10_payment_3 = floor_10_payment & payment_3

    if "10" in world.options.Floors.value:
        floor_10_payment = Has("Floor 10 Unlock")
        floor_10_payment_4 = floor_10_payment & payment_4

    if "10" in world.options.Floors.value:
        floor_10_payment = Has("Floor 10 Unlock")
        floor_10_payment_5 = floor_10_payment & payment_5

    if "10" in world.options.Floors.value:
        floor_10_payment = Has("Floor 10 Unlock")
        floor_10_payment_6 = floor_10_payment & payment_6

    if "10" in world.options.Floors.value:
        floor_10_payment = Has("Floor 10 Unlock")
        floor_10_payment_7 = floor_10_payment & payment_7

    if "10" in world.options.Floors.value:
        floor_10_payment = Has("Floor 10 Unlock")
        floor_10_payment_8 = floor_10_payment & payment_8

    if "10" in world.options.Floors.value:
        floor_10_payment = Has("Floor 10 Unlock")
        floor_10_payment_9 = floor_10_payment & payment_9

    if "10" in world.options.Floors.value:
        floor_10_payment = Has("Floor 10 Unlock")
        floor_10_payment_10 = floor_10_payment & payment_10

    if "10" in world.options.Floors.value:
        floor_10_payment = Has("Floor 10 Unlock")
        floor_10_payment_11 = floor_10_payment & payment_11

    if "10" in world.options.Floors.value:
        floor_10_payment = Has("Floor 10 Unlock")
        floor_10_payment_12 = floor_10_payment & payment_12


    if "11" in world.options.Floors.value:
        floor_11_payment = Has("Floor 11 Unlock")
        floor_11_payment_1 = floor_11_payment & payment_1

    if "11" in world.options.Floors.value:
        floor_11_payment = Has("Floor 11 Unlock")
        floor_11_payment_2 = floor_11_payment & payment_2

    if "11" in world.options.Floors.value:
        floor_11_payment = Has("Floor 11 Unlock")
        floor_11_payment_3 = floor_11_payment & payment_3

    if "11" in world.options.Floors.value:
        floor_11_payment = Has("Floor 11 Unlock")
        floor_11_payment_4 = floor_11_payment & payment_4

    if "11" in world.options.Floors.value:
        floor_11_payment = Has("Floor 11 Unlock")
        floor_11_payment_5 = floor_11_payment & payment_5

    if "11" in world.options.Floors.value:
        floor_11_payment = Has("Floor 11 Unlock")
        floor_11_payment_6 = floor_11_payment & payment_6

    if "11" in world.options.Floors.value:
        floor_11_payment = Has("Floor 11 Unlock")
        floor_11_payment_7 = floor_11_payment & payment_7

    if "11" in world.options.Floors.value:
        floor_11_payment = Has("Floor 11 Unlock")
        floor_11_payment_8 = floor_11_payment & payment_8

    if "11" in world.options.Floors.value:
        floor_11_payment = Has("Floor 11 Unlock")
        floor_11_payment_9 = floor_11_payment & payment_9

    if "11" in world.options.Floors.value:
        floor_11_payment = Has("Floor 11 Unlock")
        floor_11_payment_10 = floor_11_payment & payment_10

    if "11" in world.options.Floors.value:
        floor_11_payment = Has("Floor 11 Unlock")
        floor_11_payment_11 = floor_11_payment & payment_11

    if "11" in world.options.Floors.value:
        floor_11_payment = Has("Floor 11 Unlock")
        floor_11_payment_12 = floor_11_payment & payment_12


    if "12" in world.options.Floors.value:
        floor_12_payment = Has("Floor 12 Unlock")
        floor_12_payment_1 = floor_12_payment & payment_1

    if "12" in world.options.Floors.value:
        floor_12_payment = Has("Floor 12 Unlock")
        floor_12_payment_2 = floor_12_payment & payment_2

    if "12" in world.options.Floors.value:
        floor_12_payment = Has("Floor 12 Unlock")
        floor_12_payment_3 = floor_12_payment & payment_3

    if "12" in world.options.Floors.value:
        floor_12_payment = Has("Floor 12 Unlock")
        floor_12_payment_4 = floor_12_payment & payment_4

    if "12" in world.options.Floors.value:
        floor_12_payment = Has("Floor 12 Unlock")
        floor_12_payment_5 = floor_12_payment & payment_5

    if "12" in world.options.Floors.value:
        floor_12_payment = Has("Floor 12 Unlock")
        floor_12_payment_6 = floor_12_payment & payment_6

    if "12" in world.options.Floors.value:
        floor_12_payment = Has("Floor 12 Unlock")
        floor_12_payment_7 = floor_12_payment & payment_7

    if "12" in world.options.Floors.value:
        floor_12_payment = Has("Floor 12 Unlock")
        floor_12_payment_8 = floor_12_payment & payment_8

    if "12" in world.options.Floors.value:
        floor_12_payment = Has("Floor 12 Unlock")
        floor_12_payment_9 = floor_12_payment & payment_9

    if "12" in world.options.Floors.value:
        floor_12_payment = Has("Floor 12 Unlock")
        floor_12_payment_10 = floor_12_payment & payment_10

    if "12" in world.options.Floors.value:
        floor_12_payment = Has("Floor 12 Unlock")
        floor_12_payment_11 = floor_12_payment & payment_11

    if "12" in world.options.Floors.value:
        floor_12_payment = Has("Floor 12 Unlock")
        floor_12_payment_12 = floor_12_payment & payment_12


    if "13" in world.options.Floors.value:
        floor_13_payment = Has("Floor 13 Unlock")
        floor_13_payment_1 = floor_13_payment & payment_1

    if "13" in world.options.Floors.value:
        floor_13_payment = Has("Floor 13 Unlock")
        floor_13_payment_2 = floor_13_payment & payment_2

    if "13" in world.options.Floors.value:
        floor_13_payment = Has("Floor 13 Unlock")
        floor_13_payment_3 = floor_13_payment & payment_3

    if "13" in world.options.Floors.value:
        floor_13_payment = Has("Floor 13 Unlock")
        floor_13_payment_4 = floor_13_payment & payment_4

    if "13" in world.options.Floors.value:
        floor_13_payment = Has("Floor 13 Unlock")
        floor_13_payment_5 = floor_13_payment & payment_5

    if "13" in world.options.Floors.value:
        floor_13_payment = Has("Floor 13 Unlock")
        floor_13_payment_6 = floor_13_payment & payment_6

    if "13" in world.options.Floors.value:
        floor_13_payment = Has("Floor 13 Unlock")
        floor_13_payment_7 = floor_13_payment & payment_7

    if "13" in world.options.Floors.value:
        floor_13_payment = Has("Floor 13 Unlock")
        floor_13_payment_8 = floor_13_payment & payment_8

    if "13" in world.options.Floors.value:
        floor_13_payment = Has("Floor 13 Unlock")
        floor_13_payment_9 = floor_13_payment & payment_9

    if "13" in world.options.Floors.value:
        floor_13_payment = Has("Floor 13 Unlock")
        floor_13_payment_10 = floor_13_payment & payment_10

    if "13" in world.options.Floors.value:
        floor_13_payment = Has("Floor 13 Unlock")
        floor_13_payment_11 = floor_13_payment & payment_11

    if "13" in world.options.Floors.value:
        floor_13_payment = Has("Floor 13 Unlock")
        floor_13_payment_12 = floor_13_payment & payment_12


    if "14" in world.options.Floors.value:
        floor_14_payment = Has("Floor 14 Unlock")
        floor_14_payment_1 = floor_14_payment & payment_1

    if "14" in world.options.Floors.value:
        floor_14_payment = Has("Floor 14 Unlock")
        floor_14_payment_2 = floor_14_payment & payment_2

    if "14" in world.options.Floors.value:
        floor_14_payment = Has("Floor 14 Unlock")
        floor_14_payment_3 = floor_14_payment & payment_3

    if "14" in world.options.Floors.value:
        floor_14_payment = Has("Floor 14 Unlock")
        floor_14_payment_4 = floor_14_payment & payment_4

    if "14" in world.options.Floors.value:
        floor_14_payment = Has("Floor 14 Unlock")
        floor_14_payment_5 = floor_14_payment & payment_5

    if "14" in world.options.Floors.value:
        floor_14_payment = Has("Floor 14 Unlock")
        floor_14_payment_6 = floor_14_payment & payment_6

    if "14" in world.options.Floors.value:
        floor_14_payment = Has("Floor 14 Unlock")
        floor_14_payment_7 = floor_14_payment & payment_7

    if "14" in world.options.Floors.value:
        floor_14_payment = Has("Floor 14 Unlock")
        floor_14_payment_8 = floor_14_payment & payment_8

    if "14" in world.options.Floors.value:
        floor_14_payment = Has("Floor 14 Unlock")
        floor_14_payment_9 = floor_14_payment & payment_9

    if "14" in world.options.Floors.value:
        floor_14_payment = Has("Floor 14 Unlock")
        floor_14_payment_10 = floor_14_payment & payment_10

    if "14" in world.options.Floors.value:
        floor_14_payment = Has("Floor 14 Unlock")
        floor_14_payment_11 = floor_14_payment & payment_11

    if "14" in world.options.Floors.value:
        floor_14_payment = Has("Floor 14 Unlock")
        floor_14_payment_12 = floor_14_payment & payment_12


    if "15" in world.options.Floors.value:
        floor_15_payment = Has("Floor 15 Unlock")
        floor_15_payment_1 = floor_15_payment & payment_1

    if "15" in world.options.Floors.value:
        floor_15_payment = Has("Floor 15 Unlock")
        floor_15_payment_2 = floor_15_payment & payment_2

    if "15" in world.options.Floors.value:
        floor_15_payment = Has("Floor 15 Unlock")
        floor_15_payment_3 = floor_15_payment & payment_3

    if "15" in world.options.Floors.value:
        floor_15_payment = Has("Floor 15 Unlock")
        floor_15_payment_4 = floor_15_payment & payment_4

    if "15" in world.options.Floors.value:
        floor_15_payment = Has("Floor 15 Unlock")
        floor_15_payment_5 = floor_15_payment & payment_5

    if "15" in world.options.Floors.value:
        floor_15_payment = Has("Floor 15 Unlock")
        floor_15_payment_6 = floor_15_payment & payment_6

    if "15" in world.options.Floors.value:
        floor_15_payment = Has("Floor 15 Unlock")
        floor_15_payment_7 = floor_15_payment & payment_7

    if "15" in world.options.Floors.value:
        floor_15_payment = Has("Floor 15 Unlock")
        floor_15_payment_8 = floor_15_payment & payment_8

    if "15" in world.options.Floors.value:
        floor_15_payment = Has("Floor 15 Unlock")
        floor_15_payment_9 = floor_15_payment & payment_9

    if "15" in world.options.Floors.value:
        floor_15_payment = Has("Floor 15 Unlock")
        floor_15_payment_10 = floor_15_payment & payment_10

    if "15" in world.options.Floors.value:
        floor_15_payment = Has("Floor 15 Unlock")
        floor_15_payment_11 = floor_15_payment & payment_11

    if "15" in world.options.Floors.value:
        floor_15_payment = Has("Floor 15 Unlock")
        floor_15_payment_12 = floor_15_payment & payment_12



    if "16" in world.options.Floors.value:
        floor_16_payment = Has("Floor 16 Unlock")
        floor_16_payment_1 = floor_16_payment & payment_1

    if "16" in world.options.Floors.value:
        floor_16_payment = Has("Floor 16 Unlock")
        floor_16_payment_2 = floor_16_payment & payment_2

    if "16" in world.options.Floors.value:
        floor_16_payment = Has("Floor 16 Unlock")
        floor_16_payment_3 = floor_16_payment & payment_3

    if "16" in world.options.Floors.value:
        floor_16_payment = Has("Floor 16 Unlock")
        floor_16_payment_4 = floor_16_payment & payment_4

    if "16" in world.options.Floors.value:
        floor_16_payment = Has("Floor 16 Unlock")
        floor_16_payment_5 = floor_16_payment & payment_5

    if "16" in world.options.Floors.value:
        floor_16_payment = Has("Floor 16 Unlock")
        floor_16_payment_6 = floor_16_payment & payment_6

    if "16" in world.options.Floors.value:
        floor_16_payment = Has("Floor 16 Unlock")
        floor_16_payment_7 = floor_16_payment & payment_7

    if "16" in world.options.Floors.value:
        floor_16_payment = Has("Floor 16 Unlock")
        floor_16_payment_8 = floor_16_payment & payment_8

    if "16" in world.options.Floors.value:
        floor_16_payment = Has("Floor 16 Unlock")
        floor_16_payment_9 = floor_16_payment & payment_9

    if "16" in world.options.Floors.value:
        floor_16_payment = Has("Floor 16 Unlock")
        floor_16_payment_10 = floor_16_payment & payment_10

    if "16" in world.options.Floors.value:
        floor_16_payment = Has("Floor 16 Unlock")
        floor_16_payment_11 = floor_16_payment & payment_11

    if "16" in world.options.Floors.value:
        floor_16_payment = Has("Floor 16 Unlock")
        floor_16_payment_12 = floor_16_payment & payment_12


    if "17" in world.options.Floors.value:
        floor_17_payment = Has("Floor 17 Unlock")
        floor_17_payment_1 = floor_17_payment & payment_1

    if "17" in world.options.Floors.value:
        floor_17_payment = Has("Floor 17 Unlock")
        floor_17_payment_2 = floor_17_payment & payment_2

    if "17" in world.options.Floors.value:
        floor_17_payment = Has("Floor 17 Unlock")
        floor_17_payment_3 = floor_17_payment & payment_3

    if "17" in world.options.Floors.value:
        floor_17_payment = Has("Floor 17 Unlock")
        floor_17_payment_4 = floor_17_payment & payment_4

    if "17" in world.options.Floors.value:
        floor_17_payment = Has("Floor 17 Unlock")
        floor_17_payment_5 = floor_17_payment & payment_5

    if "17" in world.options.Floors.value:
        floor_17_payment = Has("Floor 17 Unlock")
        floor_17_payment_6 = floor_17_payment & payment_6

    if "17" in world.options.Floors.value:
        floor_17_payment = Has("Floor 17 Unlock")
        floor_17_payment_7 = floor_17_payment & payment_7

    if "17" in world.options.Floors.value:
        floor_17_payment = Has("Floor 17 Unlock")
        floor_17_payment_8 = floor_17_payment & payment_8

    if "17" in world.options.Floors.value:
        floor_17_payment = Has("Floor 17 Unlock")
        floor_17_payment_9 = floor_17_payment & payment_9

    if "17" in world.options.Floors.value:
        floor_17_payment = Has("Floor 17 Unlock")
        floor_17_payment_10 = floor_17_payment & payment_10

    if "17" in world.options.Floors.value:
        floor_17_payment = Has("Floor 17 Unlock")
        floor_17_payment_11 = floor_17_payment & payment_11

    if "17" in world.options.Floors.value:
        floor_17_payment = Has("Floor 17 Unlock")
        floor_17_payment_12 = floor_17_payment & payment_12



    if "18" in world.options.Floors.value:
        floor_18_payment = Has("Floor 18 Unlock")
        floor_18_payment_1 = floor_18_payment & payment_1

    if "18" in world.options.Floors.value:
        floor_18_payment = Has("Floor 18 Unlock")
        floor_18_payment_2 = floor_18_payment & payment_2

    if "18" in world.options.Floors.value:
        floor_18_payment = Has("Floor 18 Unlock")
        floor_18_payment_3 = floor_18_payment & payment_3

    if "18" in world.options.Floors.value:
        floor_18_payment = Has("Floor 18 Unlock")
        floor_18_payment_4 = floor_18_payment & payment_4

    if "18" in world.options.Floors.value:
        floor_18_payment = Has("Floor 18 Unlock")
        floor_18_payment_5 = floor_18_payment & payment_5

    if "18" in world.options.Floors.value:
        floor_18_payment = Has("Floor 18 Unlock")
        floor_18_payment_6 = floor_18_payment & payment_6

    if "18" in world.options.Floors.value:
        floor_18_payment = Has("Floor 18 Unlock")
        floor_18_payment_7 = floor_18_payment & payment_7

    if "18" in world.options.Floors.value:
        floor_18_payment = Has("Floor 18 Unlock")
        floor_18_payment_8 = floor_18_payment & payment_8

    if "18" in world.options.Floors.value:
        floor_18_payment = Has("Floor 18 Unlock")
        floor_18_payment_9 = floor_18_payment & payment_9

    if "18" in world.options.Floors.value:
        floor_18_payment = Has("Floor 18 Unlock")
        floor_18_payment_10 = floor_18_payment & payment_10

    if "18" in world.options.Floors.value:
        floor_18_payment = Has("Floor 18 Unlock")
        floor_18_payment_11 = floor_18_payment & payment_11

    if "18" in world.options.Floors.value:
        floor_18_payment = Has("Floor 18 Unlock")
        floor_18_payment_12 = floor_18_payment & payment_12


    if "19" in world.options.Floors.value:
        floor_19_payment = Has("Floor 19 Unlock")
        floor_19_payment_1 = floor_19_payment & payment_1

    if "19" in world.options.Floors.value:
        floor_19_payment = Has("Floor 19 Unlock")
        floor_19_payment_2 = floor_19_payment & payment_2

    if "19" in world.options.Floors.value:
        floor_19_payment = Has("Floor 19 Unlock")
        floor_19_payment_3 = floor_19_payment & payment_3

    if "19" in world.options.Floors.value:
        floor_19_payment = Has("Floor 19 Unlock")
        floor_19_payment_4 = floor_19_payment & payment_4

    if "19" in world.options.Floors.value:
        floor_19_payment = Has("Floor 19 Unlock")
        floor_19_payment_5 = floor_19_payment & payment_5

    if "19" in world.options.Floors.value:
        floor_19_payment = Has("Floor 19 Unlock")
        floor_19_payment_6 = floor_19_payment & payment_6

    if "19" in world.options.Floors.value:
        floor_19_payment = Has("Floor 19 Unlock")
        floor_19_payment_7 = floor_19_payment & payment_7

    if "19" in world.options.Floors.value:
        floor_19_payment = Has("Floor 19 Unlock")
        floor_19_payment_8 = floor_19_payment & payment_8

    if "19" in world.options.Floors.value:
        floor_19_payment = Has("Floor 19 Unlock")
        floor_19_payment_9 = floor_19_payment & payment_9

    if "19" in world.options.Floors.value:
        floor_19_payment = Has("Floor 19 Unlock")
        floor_19_payment_10 = floor_19_payment & payment_10

    if "19" in world.options.Floors.value:
        floor_19_payment = Has("Floor 19 Unlock")
        floor_19_payment_11 = floor_19_payment & payment_11

    if "19" in world.options.Floors.value:
        floor_19_payment = Has("Floor 19 Unlock")
        floor_19_payment_12 = floor_19_payment & payment_12



    if "20" in world.options.Floors.value:
        floor_20_payment = Has("Floor 20 Unlock")
        floor_20_payment_1 = floor_20_payment & payment_1

    if "20" in world.options.Floors.value:
        floor_20_payment = Has("Floor 20 Unlock")
        floor_20_payment_2 = floor_20_payment & payment_2

    if "20" in world.options.Floors.value:
        floor_20_payment = Has("Floor 20 Unlock")
        floor_20_payment_3 = floor_20_payment & payment_3

    if "20" in world.options.Floors.value:
        floor_20_payment = Has("Floor 20 Unlock")
        floor_20_payment_4 = floor_20_payment & payment_4

    if "20" in world.options.Floors.value:
        floor_20_payment = Has("Floor 20 Unlock")
        floor_20_payment_5 = floor_20_payment & payment_5

    if "20" in world.options.Floors.value:
        floor_20_payment = Has("Floor 20 Unlock")
        floor_20_payment_6 = floor_20_payment & payment_6

    if "20" in world.options.Floors.value:
        floor_20_payment = Has("Floor 20 Unlock")
        floor_20_payment_7 = floor_20_payment & payment_7

    if "20" in world.options.Floors.value:
        floor_20_payment = Has("Floor 20 Unlock")
        floor_20_payment_8 = floor_20_payment & payment_8

    if "20" in world.options.Floors.value:
        floor_20_payment = Has("Floor 20 Unlock")
        floor_20_payment_9 = floor_20_payment & payment_9

    if "20" in world.options.Floors.value:
        floor_20_payment = Has("Floor 20 Unlock")
        floor_20_payment_10 = floor_20_payment & payment_10

    if "20" in world.options.Floors.value:
        floor_20_payment = Has("Floor 20 Unlock")
        floor_20_payment_11 = floor_20_payment & payment_11

    if "20" in world.options.Floors.value:
        floor_20_payment = Has("Floor 20 Unlock")
        floor_20_payment_12 = floor_20_payment & payment_12


    # Finally, we set our rule onto the Right Room Eney Drop location.
    #right_room_enemy = world.get_location("Right Room Enemy Drop")
    #world.set_rule(right_room_enemy, can_defeat_basic_enemy)

    floor1_payment1 = world.get_location("Floor 1 Payment 1")
    world.set_rule(floor1_payment1, floor_1_payment_1)

    floor1_payment2 = world.get_location("Floor 1 Payment 2")
    world.set_rule(floor1_payment2, floor_1_payment_2)

    floor1_payment3 = world.get_location("Floor 1 Payment 3")
    world.set_rule(floor1_payment3, floor_1_payment_3)

    floor1_payment4 = world.get_location("Floor 1 Payment 4")
    world.set_rule(floor1_payment4, floor_1_payment_4)

    floor1_payment5 = world.get_location("Floor 1 Payment 5")
    world.set_rule(floor1_payment5, floor_1_payment_5)

    floor1_payment6 = world.get_location("Floor 1 Payment 6")
    world.set_rule(floor1_payment6, floor_1_payment_6)

    floor1_payment7 = world.get_location("Floor 1 Payment 7")
    world.set_rule(floor1_payment7, floor_1_payment_7)

    floor1_payment8 = world.get_location("Floor 1 Payment 8")
    world.set_rule(floor1_payment8, floor_1_payment_8)

    floor1_payment9 = world.get_location("Floor 1 Payment 9")
    world.set_rule(floor1_payment9, floor_1_payment_9)

    floor1_payment10 = world.get_location("Floor 1 Payment 10")
    world.set_rule(floor1_payment10, floor_1_payment_10)

    floor1_payment11 = world.get_location("Floor 1 Payment 11")
    world.set_rule(floor1_payment11, floor_1_payment_11)
    floor1_payment12 = world.get_location("Floor 1 Payment 12")
    world.set_rule(floor1_payment12, floor_1_payment_12)
    if "2" in world.options.Floors.value:
        floor2_payment1 = world.get_location("Floor 2 Payment 1")
        world.set_rule(floor2_payment1, floor_2_payment_1)

        floor2_payment2 = world.get_location("Floor 2 Payment 2")
        world.set_rule(floor2_payment2, floor_2_payment_2)

        floor2_payment3 = world.get_location("Floor 2 Payment 3")
        world.set_rule(floor2_payment3, floor_2_payment_3)

        floor2_payment4 = world.get_location("Floor 2 Payment 4")
        world.set_rule(floor2_payment4, floor_2_payment_4)

        floor2_payment5 = world.get_location("Floor 2 Payment 5")
        world.set_rule(floor2_payment5, floor_2_payment_5)

        floor2_payment6 = world.get_location("Floor 2 Payment 6")
        world.set_rule(floor2_payment6, floor_2_payment_6)

        floor2_payment7 = world.get_location("Floor 2 Payment 7")
        world.set_rule(floor2_payment7, floor_2_payment_7)

        floor2_payment8 = world.get_location("Floor 2 Payment 8")
        world.set_rule(floor2_payment8, floor_2_payment_8)

        floor2_payment9 = world.get_location("Floor 2 Payment 9")
        world.set_rule(floor2_payment9, floor_2_payment_9)

        floor2_payment10 = world.get_location("Floor 2 Payment 10")
        world.set_rule(floor2_payment10, floor_2_payment_10)

        floor2_payment11 = world.get_location("Floor 2 Payment 11")
        world.set_rule(floor2_payment11, floor_2_payment_11)

        floor2_payment12 = world.get_location("Floor 2 Payment 12")
        world.set_rule(floor2_payment12, floor_2_payment_12)
    if "3" in world.options.Floors.value:    
        floor3_payment1 = world.get_location("Floor 3 Payment 1")
        world.set_rule(floor3_payment1, floor_3_payment_1)

        floor3_payment2 = world.get_location("Floor 3 Payment 2")
        world.set_rule(floor3_payment2, floor_3_payment_2)

        floor3_payment3 = world.get_location("Floor 3 Payment 3")
        world.set_rule(floor3_payment3, floor_3_payment_3)

        floor3_payment4 = world.get_location("Floor 3 Payment 4")
        world.set_rule(floor3_payment4, floor_3_payment_4)

        floor3_payment5 = world.get_location("Floor 3 Payment 5")
        world.set_rule(floor3_payment5, floor_3_payment_5)

        floor3_payment6 = world.get_location("Floor 3 Payment 6")
        world.set_rule(floor3_payment6, floor_3_payment_6)

        floor3_payment7 = world.get_location("Floor 3 Payment 7")
        world.set_rule(floor3_payment7, floor_3_payment_7)

        floor3_payment8 = world.get_location("Floor 3 Payment 8")
        world.set_rule(floor3_payment8, floor_3_payment_8)

        floor3_payment9 = world.get_location("Floor 3 Payment 9")
        world.set_rule(floor3_payment9, floor_3_payment_9)

        floor3_payment10 = world.get_location("Floor 3 Payment 10")
        world.set_rule(floor3_payment10, floor_3_payment_10)

        floor3_payment11 = world.get_location("Floor 3 Payment 11")
        world.set_rule(floor3_payment11, floor_3_payment_11)

        floor3_payment12 = world.get_location("Floor 3 Payment 12")
        world.set_rule(floor3_payment12, floor_3_payment_12)
    if "4" in world.options.Floors.value:
        floor4_payment1 = world.get_location("Floor 4 Payment 1")
        world.set_rule(floor4_payment1, floor_4_payment_1)

        floor4_payment2 = world.get_location("Floor 4 Payment 2")
        world.set_rule(floor4_payment2, floor_4_payment_2)

        floor4_payment3 = world.get_location("Floor 4 Payment 3")
        world.set_rule(floor4_payment3, floor_4_payment_3)

        floor4_payment4 = world.get_location("Floor 4 Payment 4")
        world.set_rule(floor4_payment4, floor_4_payment_4)

        floor4_payment5 = world.get_location("Floor 4 Payment 5")
        world.set_rule(floor4_payment5, floor_4_payment_5)

        floor4_payment6 = world.get_location("Floor 4 Payment 6")
        world.set_rule(floor4_payment6, floor_4_payment_6)

        floor4_payment7 = world.get_location("Floor 4 Payment 7")
        world.set_rule(floor4_payment7, floor_4_payment_7)

        floor4_payment8 = world.get_location("Floor 4 Payment 8")
        world.set_rule(floor4_payment8, floor_4_payment_8)

        floor4_payment9 = world.get_location("Floor 4 Payment 9")
        world.set_rule(floor4_payment9, floor_4_payment_9)

        floor4_payment10 = world.get_location("Floor 4 Payment 10")
        world.set_rule(floor4_payment10, floor_4_payment_10)

        floor4_payment11 = world.get_location("Floor 4 Payment 11")
        world.set_rule(floor4_payment11, floor_4_payment_11)

        floor4_payment12 = world.get_location("Floor 4 Payment 12")
        world.set_rule(floor4_payment12, floor_4_payment_12)
    if "5" in world.options.Floors.value:
        floor5_payment1 = world.get_location("Floor 5 Payment 1")
        world.set_rule(floor5_payment1, floor_5_payment_1)

        floor5_payment2 = world.get_location("Floor 5 Payment 2")
        world.set_rule(floor5_payment2, floor_5_payment_2)

        floor5_payment3 = world.get_location("Floor 5 Payment 3")
        world.set_rule(floor5_payment3, floor_5_payment_3)

        floor5_payment4 = world.get_location("Floor 5 Payment 4")
        world.set_rule(floor5_payment4, floor_5_payment_4)

        floor5_payment5 = world.get_location("Floor 5 Payment 5")
        world.set_rule(floor5_payment5, floor_5_payment_5)

        floor5_payment6 = world.get_location("Floor 5 Payment 6")
        world.set_rule(floor5_payment6, floor_5_payment_6)

        floor5_payment7 = world.get_location("Floor 5 Payment 7")
        world.set_rule(floor5_payment7, floor_5_payment_7)

        floor5_payment8 = world.get_location("Floor 5 Payment 8")
        world.set_rule(floor5_payment8, floor_5_payment_8)

        floor5_payment9 = world.get_location("Floor 5 Payment 9")
        world.set_rule(floor5_payment9, floor_5_payment_9)

        floor5_payment10 = world.get_location("Floor 5 Payment 10")
        world.set_rule(floor5_payment10, floor_5_payment_10)

        floor5_payment11 = world.get_location("Floor 5 Payment 11")
        world.set_rule(floor5_payment11, floor_5_payment_11)

        floor5_payment12 = world.get_location("Floor 5 Payment 12")
        world.set_rule(floor5_payment12, floor_5_payment_12)
    if "6" in world.options.Floors.value:
        floor6_payment1 = world.get_location("Floor 6 Payment 1")
        world.set_rule(floor6_payment1, floor_6_payment_1)

        floor6_payment2 = world.get_location("Floor 6 Payment 2")
        world.set_rule(floor6_payment2, floor_6_payment_2)

        floor6_payment3 = world.get_location("Floor 6 Payment 3")
        world.set_rule(floor6_payment3, floor_6_payment_3)

        floor6_payment4 = world.get_location("Floor 6 Payment 4")
        world.set_rule(floor6_payment4, floor_6_payment_4)

        floor6_payment5 = world.get_location("Floor 6 Payment 5")
        world.set_rule(floor6_payment5, floor_6_payment_5)

        floor6_payment6 = world.get_location("Floor 6 Payment 6")
        world.set_rule(floor6_payment6, floor_6_payment_6)

        floor6_payment7 = world.get_location("Floor 6 Payment 7")
        world.set_rule(floor6_payment7, floor_6_payment_7)

        floor6_payment8 = world.get_location("Floor 6 Payment 8")
        world.set_rule(floor6_payment8, floor_6_payment_8)

        floor6_payment9 = world.get_location("Floor 6 Payment 9")
        world.set_rule(floor6_payment9, floor_6_payment_9)

        floor6_payment10 = world.get_location("Floor 6 Payment 10")
        world.set_rule(floor6_payment10, floor_6_payment_10)

        floor6_payment11 = world.get_location("Floor 6 Payment 11")
        world.set_rule(floor6_payment11, floor_6_payment_11)

        floor6_payment12 = world.get_location("Floor 6 Payment 12")
        world.set_rule(floor6_payment12, floor_6_payment_12)
    if "7" in world.options.Floors.value:
        floor7_payment1 = world.get_location("Floor 7 Payment 1")
        world.set_rule(floor7_payment1, floor_7_payment_1)

        floor7_payment2 = world.get_location("Floor 7 Payment 2")
        world.set_rule(floor7_payment2, floor_7_payment_2)

        floor7_payment3 = world.get_location("Floor 7 Payment 3")
        world.set_rule(floor7_payment3, floor_7_payment_3)

        floor7_payment4 = world.get_location("Floor 7 Payment 4")
        world.set_rule(floor7_payment4, floor_7_payment_4)

        floor7_payment5 = world.get_location("Floor 7 Payment 5")
        world.set_rule(floor7_payment5, floor_7_payment_5)

        floor7_payment6 = world.get_location("Floor 7 Payment 6")
        world.set_rule(floor7_payment6, floor_7_payment_6)

        floor7_payment7 = world.get_location("Floor 7 Payment 7")
        world.set_rule(floor7_payment7, floor_7_payment_7)

        floor7_payment8 = world.get_location("Floor 7 Payment 8")
        world.set_rule(floor7_payment8, floor_7_payment_8)

        floor7_payment9 = world.get_location("Floor 7 Payment 9")
        world.set_rule(floor7_payment9, floor_7_payment_9)

        floor7_payment10 = world.get_location("Floor 7 Payment 10")
        world.set_rule(floor7_payment10, floor_7_payment_10)

        floor7_payment11 = world.get_location("Floor 7 Payment 11")
        world.set_rule(floor7_payment11, floor_7_payment_11)

        floor7_payment12 = world.get_location("Floor 7 Payment 12")
        world.set_rule(floor7_payment12, floor_7_payment_12)
    if "8" in world.options.Floors.value:
        floor8_payment1 = world.get_location("Floor 8 Payment 1")
        world.set_rule(floor8_payment1, floor_8_payment_1)

        floor8_payment2 = world.get_location("Floor 8 Payment 2")
        world.set_rule(floor8_payment2, floor_8_payment_2)

        floor8_payment3 = world.get_location("Floor 8 Payment 3")
        world.set_rule(floor8_payment3, floor_8_payment_3)

        floor8_payment4 = world.get_location("Floor 8 Payment 4")
        world.set_rule(floor8_payment4, floor_8_payment_4)

        floor8_payment5 = world.get_location("Floor 8 Payment 5")
        world.set_rule(floor8_payment5, floor_8_payment_5)

        floor8_payment6 = world.get_location("Floor 8 Payment 6")
        world.set_rule(floor8_payment6, floor_8_payment_6)

        floor8_payment7 = world.get_location("Floor 8 Payment 7")
        world.set_rule(floor8_payment7, floor_8_payment_7)

        floor8_payment8 = world.get_location("Floor 8 Payment 8")
        world.set_rule(floor8_payment8, floor_8_payment_8)

        floor8_payment9 = world.get_location("Floor 8 Payment 9")
        world.set_rule(floor8_payment9, floor_8_payment_9)

        floor8_payment10 = world.get_location("Floor 8 Payment 10")
        world.set_rule(floor8_payment10, floor_8_payment_10)

        floor8_payment11 = world.get_location("Floor 8 Payment 11")
        world.set_rule(floor8_payment11, floor_8_payment_11)

        floor8_payment12 = world.get_location("Floor 8 Payment 12")
        world.set_rule(floor8_payment12, floor_8_payment_12)
    if "9" in world.options.Floors.value:
        floor9_payment1 = world.get_location("Floor 9 Payment 1")
        world.set_rule(floor9_payment1, floor_9_payment_1)

        floor9_payment2 = world.get_location("Floor 9 Payment 2")
        world.set_rule(floor9_payment2, floor_9_payment_2)

        floor9_payment3 = world.get_location("Floor 9 Payment 3")
        world.set_rule(floor9_payment3, floor_9_payment_3)

        floor9_payment4 = world.get_location("Floor 9 Payment 4")
        world.set_rule(floor9_payment4, floor_9_payment_4)

        floor9_payment5 = world.get_location("Floor 9 Payment 5")
        world.set_rule(floor9_payment5, floor_9_payment_5)

        floor9_payment6 = world.get_location("Floor 9 Payment 6")
        world.set_rule(floor9_payment6, floor_9_payment_6)

        floor9_payment7 = world.get_location("Floor 9 Payment 7")
        world.set_rule(floor9_payment7, floor_9_payment_7)

        floor9_payment8 = world.get_location("Floor 9 Payment 8")
        world.set_rule(floor9_payment8, floor_9_payment_8)

        floor9_payment9 = world.get_location("Floor 9 Payment 9")
        world.set_rule(floor9_payment9, floor_9_payment_9)

        floor9_payment10 = world.get_location("Floor 9 Payment 10")
        world.set_rule(floor9_payment10, floor_9_payment_10)

        floor9_payment11 = world.get_location("Floor 9 Payment 11")
        world.set_rule(floor9_payment11, floor_9_payment_11)

        floor9_payment12 = world.get_location("Floor 9 Payment 12")
        world.set_rule(floor9_payment12, floor_9_payment_12)
    if "10" in world.options.Floors.value:
        floor10_payment1 = world.get_location("Floor 10 Payment 1")
        world.set_rule(floor10_payment1, floor_10_payment_1)

        floor10_payment2 = world.get_location("Floor 10 Payment 2")
        world.set_rule(floor10_payment2, floor_10_payment_2)

        floor10_payment3 = world.get_location("Floor 10 Payment 3")
        world.set_rule(floor10_payment3, floor_10_payment_3)

        floor10_payment4 = world.get_location("Floor 10 Payment 4")
        world.set_rule(floor10_payment4, floor_10_payment_4)

        floor10_payment5 = world.get_location("Floor 10 Payment 5")
        world.set_rule(floor10_payment5, floor_10_payment_5)

        floor10_payment6 = world.get_location("Floor 10 Payment 6")
        world.set_rule(floor10_payment6, floor_10_payment_6)

        floor10_payment7 = world.get_location("Floor 10 Payment 7")
        world.set_rule(floor10_payment7, floor_10_payment_7)

        floor10_payment8 = world.get_location("Floor 10 Payment 8")
        world.set_rule(floor10_payment8, floor_10_payment_8)

        floor10_payment9 = world.get_location("Floor 10 Payment 9")
        world.set_rule(floor10_payment9, floor_10_payment_9)

        floor10_payment10 = world.get_location("Floor 10 Payment 10")
        world.set_rule(floor10_payment10, floor_10_payment_10)

        floor10_payment11 = world.get_location("Floor 10 Payment 11")
        world.set_rule(floor10_payment11, floor_10_payment_11)

        floor10_payment12 = world.get_location("Floor 10 Payment 12")
        world.set_rule(floor10_payment12, floor_10_payment_12)
    if "11" in world.options.Floors.value:
        floor11_payment1 = world.get_location("Floor 11 Payment 1")
        world.set_rule(floor11_payment1, floor_11_payment_1)

        floor11_payment2 = world.get_location("Floor 11 Payment 2")
        world.set_rule(floor11_payment2, floor_11_payment_2)

        floor11_payment3 = world.get_location("Floor 11 Payment 3")
        world.set_rule(floor11_payment3, floor_11_payment_3)

        floor11_payment4 = world.get_location("Floor 11 Payment 4")
        world.set_rule(floor11_payment4, floor_11_payment_4)

        floor11_payment5 = world.get_location("Floor 11 Payment 5")
        world.set_rule(floor11_payment5, floor_11_payment_5)

        floor11_payment6 = world.get_location("Floor 11 Payment 6")
        world.set_rule(floor11_payment6, floor_11_payment_6)

        floor11_payment7 = world.get_location("Floor 11 Payment 7")
        world.set_rule(floor11_payment7, floor_11_payment_7)

        floor11_payment8 = world.get_location("Floor 11 Payment 8")
        world.set_rule(floor11_payment8, floor_11_payment_8)

        floor11_payment9 = world.get_location("Floor 11 Payment 9")
        world.set_rule(floor11_payment9, floor_11_payment_9)

        floor11_payment10 = world.get_location("Floor 11 Payment 10")
        world.set_rule(floor11_payment10, floor_11_payment_10)

        floor11_payment11 = world.get_location("Floor 11 Payment 11")
        world.set_rule(floor11_payment11, floor_11_payment_11)

        floor11_payment12 = world.get_location("Floor 11 Payment 12")
        world.set_rule(floor11_payment12, floor_11_payment_12)
    if "12" in world.options.Floors.value:
        floor12_payment1 = world.get_location("Floor 12 Payment 1")
        world.set_rule(floor12_payment1, floor_12_payment_1)

        floor12_payment2 = world.get_location("Floor 12 Payment 2")
        world.set_rule(floor12_payment2, floor_12_payment_2)

        floor12_payment3 = world.get_location("Floor 12 Payment 3")
        world.set_rule(floor12_payment3, floor_12_payment_3)

        floor12_payment4 = world.get_location("Floor 12 Payment 4")
        world.set_rule(floor12_payment4, floor_12_payment_4)

        floor12_payment5 = world.get_location("Floor 12 Payment 5")
        world.set_rule(floor12_payment5, floor_12_payment_5)

        floor12_payment6 = world.get_location("Floor 12 Payment 6")
        world.set_rule(floor12_payment6, floor_12_payment_6)

        floor12_payment7 = world.get_location("Floor 12 Payment 7")
        world.set_rule(floor12_payment7, floor_12_payment_7)

        floor12_payment8 = world.get_location("Floor 12 Payment 8")
        world.set_rule(floor12_payment8, floor_12_payment_8)

        floor12_payment9 = world.get_location("Floor 12 Payment 9")
        world.set_rule(floor12_payment9, floor_12_payment_9)

        floor12_payment10 = world.get_location("Floor 12 Payment 10")
        world.set_rule(floor12_payment10, floor_12_payment_10)

        floor12_payment11 = world.get_location("Floor 12 Payment 11")
        world.set_rule(floor12_payment11, floor_12_payment_11)

        floor12_payment12 = world.get_location("Floor 12 Payment 12")
        world.set_rule(floor12_payment12, floor_12_payment_12)
    if "13" in world.options.Floors.value:
        floor13_payment1 = world.get_location("Floor 13 Payment 1")
        world.set_rule(floor13_payment1, floor_13_payment_1)

        floor13_payment2 = world.get_location("Floor 13 Payment 2")
        world.set_rule(floor13_payment2, floor_13_payment_2)

        floor13_payment3 = world.get_location("Floor 13 Payment 3")
        world.set_rule(floor13_payment3, floor_13_payment_3)

        floor13_payment4 = world.get_location("Floor 13 Payment 4")
        world.set_rule(floor13_payment4, floor_13_payment_4)

        floor13_payment5 = world.get_location("Floor 13 Payment 5")
        world.set_rule(floor13_payment5, floor_13_payment_5)

        floor13_payment6 = world.get_location("Floor 13 Payment 6")
        world.set_rule(floor13_payment6, floor_13_payment_6)

        floor13_payment7 = world.get_location("Floor 13 Payment 7")
        world.set_rule(floor13_payment7, floor_13_payment_7)

        floor13_payment8 = world.get_location("Floor 13 Payment 8")
        world.set_rule(floor13_payment8, floor_13_payment_8)

        floor13_payment9 = world.get_location("Floor 13 Payment 9")
        world.set_rule(floor13_payment9, floor_13_payment_9)

        floor13_payment10 = world.get_location("Floor 13 Payment 10")
        world.set_rule(floor13_payment10, floor_13_payment_10)

        floor13_payment11 = world.get_location("Floor 13 Payment 11")
        world.set_rule(floor13_payment11, floor_13_payment_11)

        floor13_payment12 = world.get_location("Floor 13 Payment 12")
        world.set_rule(floor13_payment12, floor_13_payment_12)
    if "14" in world.options.Floors.value:
        floor14_payment1 = world.get_location("Floor 14 Payment 1")
        world.set_rule(floor14_payment1, floor_14_payment_1)

        floor14_payment2 = world.get_location("Floor 14 Payment 2")
        world.set_rule(floor14_payment2, floor_14_payment_2)

        floor14_payment3 = world.get_location("Floor 14 Payment 3")
        world.set_rule(floor14_payment3, floor_14_payment_3)

        floor14_payment4 = world.get_location("Floor 14 Payment 4")
        world.set_rule(floor14_payment4, floor_14_payment_4)

        floor14_payment5 = world.get_location("Floor 14 Payment 5")
        world.set_rule(floor14_payment5, floor_14_payment_5)

        floor14_payment6 = world.get_location("Floor 14 Payment 6")
        world.set_rule(floor14_payment6, floor_14_payment_6)

        floor14_payment7 = world.get_location("Floor 14 Payment 7")
        world.set_rule(floor14_payment7, floor_14_payment_7)

        floor14_payment8 = world.get_location("Floor 14 Payment 8")
        world.set_rule(floor14_payment8, floor_14_payment_8)

        floor14_payment9 = world.get_location("Floor 14 Payment 9")
        world.set_rule(floor14_payment9, floor_14_payment_9)

        floor14_payment10 = world.get_location("Floor 14 Payment 10")
        world.set_rule(floor14_payment10, floor_14_payment_10)

        floor14_payment11 = world.get_location("Floor 14 Payment 11")
        world.set_rule(floor14_payment11, floor_14_payment_11)

        floor14_payment12 = world.get_location("Floor 14 Payment 12")
        world.set_rule(floor14_payment12, floor_14_payment_12)
    if "15" in world.options.Floors.value:
        floor15_payment1 = world.get_location("Floor 15 Payment 1")
        world.set_rule(floor15_payment1, floor_15_payment_1)

        floor15_payment2 = world.get_location("Floor 15 Payment 2")
        world.set_rule(floor15_payment2, floor_15_payment_2)

        floor15_payment3 = world.get_location("Floor 15 Payment 3")
        world.set_rule(floor15_payment3, floor_15_payment_3)

        floor15_payment4 = world.get_location("Floor 15 Payment 4")
        world.set_rule(floor15_payment4, floor_15_payment_4)

        floor15_payment5 = world.get_location("Floor 15 Payment 5")
        world.set_rule(floor15_payment5, floor_15_payment_5)

        floor15_payment6 = world.get_location("Floor 15 Payment 6")
        world.set_rule(floor15_payment6, floor_15_payment_6)

        floor15_payment7 = world.get_location("Floor 15 Payment 7")
        world.set_rule(floor15_payment7, floor_15_payment_7)

        floor15_payment8 = world.get_location("Floor 15 Payment 8")
        world.set_rule(floor15_payment8, floor_15_payment_8)

        floor15_payment9 = world.get_location("Floor 15 Payment 9")
        world.set_rule(floor15_payment9, floor_15_payment_9)

        floor15_payment10 = world.get_location("Floor 15 Payment 10")
        world.set_rule(floor15_payment10, floor_15_payment_10)

        floor15_payment11 = world.get_location("Floor 15 Payment 11")
        world.set_rule(floor15_payment11, floor_15_payment_11)

        floor15_payment12 = world.get_location("Floor 15 Payment 12")
        world.set_rule(floor15_payment12, floor_15_payment_12)
    if "16" in world.options.Floors.value:
        floor16_payment1 = world.get_location("Floor 16 Payment 1")
        world.set_rule(floor16_payment1, floor_16_payment_1)

        floor16_payment2 = world.get_location("Floor 16 Payment 2")
        world.set_rule(floor16_payment2, floor_16_payment_2)

        floor16_payment3 = world.get_location("Floor 16 Payment 3")
        world.set_rule(floor16_payment3, floor_16_payment_3)

        floor16_payment4 = world.get_location("Floor 16 Payment 4")
        world.set_rule(floor16_payment4, floor_16_payment_4)

        floor16_payment5 = world.get_location("Floor 16 Payment 5")
        world.set_rule(floor16_payment5, floor_16_payment_5)

        floor16_payment6 = world.get_location("Floor 16 Payment 6")
        world.set_rule(floor16_payment6, floor_16_payment_6)

        floor16_payment7 = world.get_location("Floor 16 Payment 7")
        world.set_rule(floor16_payment7, floor_16_payment_7)

        floor16_payment8 = world.get_location("Floor 16 Payment 8")
        world.set_rule(floor16_payment8, floor_16_payment_8)

        floor16_payment9 = world.get_location("Floor 16 Payment 9")
        world.set_rule(floor16_payment9, floor_16_payment_9)

        floor16_payment10 = world.get_location("Floor 16 Payment 10")
        world.set_rule(floor16_payment10, floor_16_payment_10)

        floor16_payment11 = world.get_location("Floor 16 Payment 11")
        world.set_rule(floor16_payment11, floor_16_payment_11)

        floor16_payment12 = world.get_location("Floor 16 Payment 12")
        world.set_rule(floor16_payment12, floor_16_payment_12)
    if "17" in world.options.Floors.value:
        floor17_payment1 = world.get_location("Floor 17 Payment 1")
        world.set_rule(floor17_payment1, floor_17_payment_1)

        floor17_payment2 = world.get_location("Floor 17 Payment 2")
        world.set_rule(floor17_payment2, floor_17_payment_2)

        floor17_payment3 = world.get_location("Floor 17 Payment 3")
        world.set_rule(floor17_payment3, floor_17_payment_3)

        floor17_payment4 = world.get_location("Floor 17 Payment 4")
        world.set_rule(floor17_payment4, floor_17_payment_4)

        floor17_payment5 = world.get_location("Floor 17 Payment 5")
        world.set_rule(floor17_payment5, floor_17_payment_5)

        floor17_payment6 = world.get_location("Floor 17 Payment 6")
        world.set_rule(floor17_payment6, floor_17_payment_6)

        floor17_payment7 = world.get_location("Floor 17 Payment 7")
        world.set_rule(floor17_payment7, floor_17_payment_7)

        floor17_payment8 = world.get_location("Floor 17 Payment 8")
        world.set_rule(floor17_payment8, floor_17_payment_8)

        floor17_payment9 = world.get_location("Floor 17 Payment 9")
        world.set_rule(floor17_payment9, floor_17_payment_9)

        floor17_payment10 = world.get_location("Floor 17 Payment 10")
        world.set_rule(floor17_payment10, floor_17_payment_10)

        floor17_payment11 = world.get_location("Floor 17 Payment 11")
        world.set_rule(floor17_payment11, floor_17_payment_11)

        floor17_payment12 = world.get_location("Floor 17 Payment 12")
        world.set_rule(floor17_payment12, floor_17_payment_12)
    if "18" in world.options.Floors.value:
        floor18_payment1 = world.get_location("Floor 18 Payment 1")
        world.set_rule(floor18_payment1, floor_18_payment_1)

        floor18_payment2 = world.get_location("Floor 18 Payment 2")
        world.set_rule(floor18_payment2, floor_18_payment_2)

        floor18_payment3 = world.get_location("Floor 18 Payment 3")
        world.set_rule(floor18_payment3, floor_18_payment_3)

        floor18_payment4 = world.get_location("Floor 18 Payment 4")
        world.set_rule(floor18_payment4, floor_18_payment_4)

        floor18_payment5 = world.get_location("Floor 18 Payment 5")
        world.set_rule(floor18_payment5, floor_18_payment_5)

        floor18_payment6 = world.get_location("Floor 18 Payment 6")
        world.set_rule(floor18_payment6, floor_18_payment_6)

        floor18_payment7 = world.get_location("Floor 18 Payment 7")
        world.set_rule(floor18_payment7, floor_18_payment_7)

        floor18_payment8 = world.get_location("Floor 18 Payment 8")
        world.set_rule(floor18_payment8, floor_18_payment_8)

        floor18_payment9 = world.get_location("Floor 18 Payment 9")
        world.set_rule(floor18_payment9, floor_18_payment_9)

        floor18_payment10 = world.get_location("Floor 18 Payment 10")
        world.set_rule(floor18_payment10, floor_18_payment_10)

        floor18_payment11 = world.get_location("Floor 18 Payment 11")
        world.set_rule(floor18_payment11, floor_18_payment_11)

        floor18_payment12 = world.get_location("Floor 18 Payment 12")
        world.set_rule(floor18_payment12, floor_18_payment_12)
    if "19" in world.options.Floors.value:
        floor19_payment1 = world.get_location("Floor 19 Payment 1")
        world.set_rule(floor19_payment1, floor_19_payment_1)

        floor19_payment2 = world.get_location("Floor 19 Payment 2")
        world.set_rule(floor19_payment2, floor_19_payment_2)

        floor19_payment3 = world.get_location("Floor 19 Payment 3")
        world.set_rule(floor19_payment3, floor_19_payment_3)

        floor19_payment4 = world.get_location("Floor 19 Payment 4")
        world.set_rule(floor19_payment4, floor_19_payment_4)

        floor19_payment5 = world.get_location("Floor 19 Payment 5")
        world.set_rule(floor19_payment5, floor_19_payment_5)

        floor19_payment6 = world.get_location("Floor 19 Payment 6")
        world.set_rule(floor19_payment6, floor_19_payment_6)

        floor19_payment7 = world.get_location("Floor 19 Payment 7")
        world.set_rule(floor19_payment7, floor_19_payment_7)

        floor19_payment8 = world.get_location("Floor 19 Payment 8")
        world.set_rule(floor19_payment8, floor_19_payment_8)

        floor19_payment9 = world.get_location("Floor 19 Payment 9")
        world.set_rule(floor19_payment9, floor_19_payment_9)

        floor19_payment10 = world.get_location("Floor 19 Payment 10")
        world.set_rule(floor19_payment10, floor_19_payment_10)

        floor19_payment11 = world.get_location("Floor 19 Payment 11")
        world.set_rule(floor19_payment11, floor_19_payment_11)

        floor19_payment12 = world.get_location("Floor 19 Payment 12")
        world.set_rule(floor19_payment12, floor_19_payment_12)
    if "20" in world.options.Floors.value:
        floor20_payment1 = world.get_location("Floor 20 Payment 1")
        world.set_rule(floor20_payment1, floor_20_payment_1)

        floor20_payment2 = world.get_location("Floor 20 Payment 2")
        world.set_rule(floor20_payment2, floor_20_payment_2)

        floor20_payment3 = world.get_location("Floor 20 Payment 3")
        world.set_rule(floor20_payment3, floor_20_payment_3)

        floor20_payment4 = world.get_location("Floor 20 Payment 4")
        world.set_rule(floor20_payment4, floor_20_payment_4)

        floor20_payment5 = world.get_location("Floor 20 Payment 5")
        world.set_rule(floor20_payment5, floor_20_payment_5)

        floor20_payment6 = world.get_location("Floor 20 Payment 6")
        world.set_rule(floor20_payment6, floor_20_payment_6)

        floor20_payment7 = world.get_location("Floor 20 Payment 7")
        world.set_rule(floor20_payment7, floor_20_payment_7)

        floor20_payment8 = world.get_location("Floor 20 Payment 8")
        world.set_rule(floor20_payment8, floor_20_payment_8)

        floor20_payment9 = world.get_location("Floor 20 Payment 9")
        world.set_rule(floor20_payment9, floor_20_payment_9)

        floor20_payment10 = world.get_location("Floor 20 Payment 10")
        world.set_rule(floor20_payment10, floor_20_payment_10)

        floor20_payment11 = world.get_location("Floor 20 Payment 11")
        world.set_rule(floor20_payment11, floor_20_payment_11)

        floor20_payment12 = world.get_location("Floor 20 Payment 12")
        world.set_rule(floor20_payment12, floor_20_payment_12)


    for base_location_name in world.location_name_to_id:

        if not base_location_name.startswith("Effect: "):
            continue

        effect_text = base_location_name.removeprefix(
            "Effect: "
        )

        required_unlocks = []

        for item_name in world.item_name_to_id:

            if not item_name.startswith("Unlock: "):
                continue

            base_name = item_name.removeprefix("Unlock: ")

            if re.search(rf"(?<!\w){re.escape(base_name)}(?!\w)", effect_text, re.IGNORECASE,):
                required_unlocks.append(item_name)

        if not required_unlocks:
            continue

        rule = Has(required_unlocks[0])

        for item_name in required_unlocks[1:]:
            rule = rule & Has(item_name)

        if locations.is_rare_or_very_rare(effect_text):
            rule = rule & payment_4

        for location in get_check_variants(world, base_location_name,):
            world.set_rule(location, rule)


    for item_name in world.item_name_to_id:

        if not item_name.startswith("Unlock: "):
            continue

        base_name = item_name.removeprefix("Unlock: ")

        base_location_name = (f"Send: {base_name}")

        rule = Has(item_name)

        if base_name.endswith(" Essence"):
            rule = rule & payment_4
        
        if locations.is_rare_or_very_rare(base_name):
            rule = rule & payment_4

        for location in get_check_variants(world, base_location_name,):
            world.set_rule(location, rule,)
            location.item_rule = (lambda item, required_item=item_name: not (item.player == world.player and item.name == required_item))


    matryoshka_rule = Has("Unlock: Matryoshka Doll")

    for number in range(2, 6):

        base_location_name = (f"Send: Matryoshka Doll {number}")

        for location in get_check_variants(world, base_location_name,):
            world.set_rule(location, matryoshka_rule,)


    # For the final boss, we also need to chain multiple conditions.
    # First of all, you always need a Sword and a Shield.
    # So far, we used the | and & operators to chain "Has" rules.
    # Instead, we can also use HasAny for an or-chain of items, or HasAll for an and-chain of items.
    #has_sword_and_shield: Rule = HasAll("Sword", "Shield")

    # In hard mode, the player also needs both Health Upgrades to survive long enough to defeat the boss.
    # For this, we can use the optional "count" parameter for "Has".
    #has_both_health_upgrades = Has("Health Upgrade", count=2)

    # Previously, we used an "if world.options.hard_mode" condition to check if we should apply the extra requirement.
    # However, if you're comfortable with boolean logic, there is another way.
    # OptionFilter is a rule component which isn't a "Rule" on its own, but when used in a boolean expression with
    # rules, it acts like True if the option has the specified value, and acts like False otherwise.
    #hard_mode_is_off = OptionFilter(HardMode, False)

    # So with this option-checking rule component in hand, we can write our boss condition like this:
    #can_defeat_final_boss = has_sword_and_shield & (hard_mode_is_off | has_both_health_upgrades)
    # If you're not as comfortable with boolean logic, it might be somewhat confusing why this is correct.
    # There is nothing wrong with using "if" conditions to check for options, if you find that easier to understand.

    # Finally, we apply the rule to our "Final Boss Defeated" event location.
    #final_boss = world.get_location("Final Boss Defeated")
    #world.set_rule(final_boss, can_defeat_final_boss)


def set_completion_condition(world: LBALWorld) -> None:
    # Finally, we need to set a completion condition for our world, defining what the player needs to win the game.
    # For this, we can use world.set_completion_rule.
    # You can just set a completion condition directly like any other condition, referencing items the player receives:
    #world.set_completion_rule(HasAll("Sword", "Shield"))
    world.set_completion_rule(Has("Shiny Coin", count=world.options.HowmanyShinyCoins.value,))

    # In our case, we went for the Victory event design pattern (see create_events() in locations.py).
    # So lets undo what we just did, and instead set the completion condition to:
    #world.set_completion_rule(Has("Victory"))


# One final comment about rules:
# If your world exclusively uses Rule Builder rules (like APQuest), it's worth trying CachedRuleBuilderWorld.
# CachedRuleBuilderWorld is a subclass of World that has a bunch of caching magic to make rules faster.
# Just have your world class subclass CachedRuleBuilderWorld instead of World:
#   class APQuestWorld(CachedRuleBuilderWorld): ...
# This may speed up your world, or it may make it slower.
# The exact factors are complex and not well understood, but there is no harm in trying it.
# Generate a few seeds and see if there is a noticeable difference!
# If you're wondering, author has checked: APQuest is too simple to see any benefits, so we'll stick with "World".
