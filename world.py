from collections.abc import Mapping
from typing import Any
from worlds.AutoWorld import World
from . import items, locations, regions, rules, web_world
from . import options as LBAL_options
import os
import logging
from .lbal_patch import write_lbal_patch




# The world class is the heart and soul of an apworld implementation.
# It holds all the data and functions required to build the world and submit it to the multiworld generator.
# You could have all your world code in just this one class, but for readability and better structure,
# it is common to split up world functionality into multiple files.
# This implementation in particular has the following additional files, each covering one topic:
# regions.py, locations.py, rules.py, items.py, options.py and web_world.py.
# It is recommended that you read these in that specific order, then come back to the world class.
class LBALWorld(World):
    """
    Luck be a Landlord is a slot machine gambling game where you need to earn enough money to pay your Landlord
    """

    # The docstring should contain a description of the game, to be displayed on the WebHost.

    # You must override the "game" field to say the name of the game.
    game = "Luck be a Landlord"

    # The WebWorld is a definition class that governs how this world will be displayed on the website.
    web = web_world.LBALWebWorld()

    # This is how we associate the options defined in our options.py with our world.
    # (Note: options.py has been imported as "apquest_options" at the top of this file to avoid a name conflict)
    options_dataclass = LBAL_options.LBALOptions
    options: LBAL_options.LBALOptions  # Common mistake: This has to be a colon (:), not an equals sign (=).

    # Our world class must have a static location_name_to_id and item_name_to_id defined.
    # We define these in regions.py and items.py respectively, so we just set them here.
    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    # There is always one region that the generator starts from & assumes you can always go back to.
    # This defaults to "Menu", but you can change it by overriding origin_region_name.
    origin_region_name = "Floor 1"

    ut_can_gen_without_yaml = True

    # Our world class must have certain functions ("steps") that get called during generation.
    # The main ones are: create_regions, set_rules, create_items.
    # For better structure and readability, we put each of these in their own file.
    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)
        
        unfilled_locations = self.multiworld.get_unfilled_locations(self.player)

        logging.info("========== ACTUAL LBAL LOCATIONS ==========")
        logging.info(f"Total unfilled locations: {len(unfilled_locations)}")

        for region in self.multiworld.get_regions(self.player):
            count = sum(1 for location in region.locations if location.item is None)
            if count:
                logging.info(f"{region.name}: {count}")
        logging.info("===========================================")


    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    # Our world class must also have a create_item function that can create any one of our items by name at any time.
    # We also put this in a different file, the same one that create_items is in.
    def create_item(self, name: str) -> items.LBALItem:
        return items.create_item_with_correct_classification(self, name)

    # For features such as item links and panic-method start inventory, AP may ask your world to create extra filler.
    # The way it does this is by calling get_filler_item_name.
    # For this purpose, your world *must* have at least one infinitely repeatable item (usually filler).
    # You must override this function and return this infinitely repeatable item's name.
    # In our case, we defined a function called get_random_filler_item_name for this purpose in our items.py.
    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)


    # There may be data that the game client will need to modify the behavior of the game.
    # This is what slot_data exists for. Upon every client connection, the slot's slot_data is sent to the client.
    # slot_data is just a dictionary using basic types, that will be converted to json when sent to the client.
    def fill_slot_data(self) -> Mapping[str, Any]:
        # If you need access to the player's chosen options on the client side, there is a helper for that.
        return {
                    "options":{
                        "APCheckBoost": bool(self.options.Boost.value), 
                        "Deathlink": bool(self.options.Deathlink.value), 
                        "Payment": int(self.options.Payment.value),
                        "ShinyCoin": bool(self.options.ShinyCoin.value),
                        "HowmanyShinyCoins": int(self.options.HowmanyShinyCoins.value),
                        "ExtraShinyCoins": int(self.options.ExtraShinyCoins.value),
                        "EnabledFloors": [1, *sorted( int(floor) for floor in self.options.Floors.value),],
                        "DeathlinkSendAmnesty": int(self.options.DeathlinkSendAmnesty.value),
                        "DeathlinkReceiveAmnesty": int(self.options.DeathlinkReceiveAmnesty.value),
                        "Rare": int(self.options.Rare.value),
                        "VeryRare": int(self.options.VeryRare.value),
                        "GoalFloors": rules.get_required_goal_floors(self),
                    }
        }

    def generate_output(self, output_directory: str):
        write_lbal_patch(self, output_directory)

    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        return slot_data


    def generate_early(self) -> None:
        selected_floors = [1, *sorted(int(floor) for floor in self.options.Floors.value)]
        payment_checks = sum(1 for floor in selected_floors for payment in range(1, 13) if f"Floor {floor} Payment {payment}" in self.location_name_to_id)
        ap_checks = sum(1 for name in self.location_name_to_id if name.startswith("AP Check "))
        total_checks = len(self.multiworld.get_locations(self.player))
        logging.info("========== LBAL DEBUG ==========")
        logging.info(f"Player: {self.player} - "f"{self.multiworld.player_name[self.player]}")
        logging.info(f"Selected floors: {selected_floors}")
        logging.info(f"Payment checks: {payment_checks:,}")
        logging.info(f"AP Checks: {ap_checks:,}")
        logging.info(f"Calculated total checks: {total_checks:,}")
        logging.info("================================")