from __future__ import annotations

from dataclasses import dataclass
from Options import Choice, OptionSet, Range, Toggle, PerGameCommonOptions
from .Items import SYMBOLS, BUFF_ITEMS, TRAP_ITEMS


class ExtraFillerChecks(Range):
    """Extra generic AP Check locations.
Default is 50.
These are filled with Progressive Filler.
Max is 200."""
    display_name = "Extra Filler Checks"
    range_start = 0
    range_end = 200
    default = 50


class StartingSymbolMode(Choice):
    """How AP floors start while AP Check locations remain.
ap_checks = start each run with five AP Check symbols.
starting_symbols = start with Coin, Flower, Pearl, Cherry, Cat and find AP Check through symbol choices."""
    display_name = "Starting Symbol Mode"
    option_ap_checks = 0
    option_starting_symbols = 1
    default = 0


class GoalMode(Choice):
    """Choose the floor goal mode.
chosen_floor = one target floor.
chosen_floors = selected target floors."""
    display_name = "Goal Mode"
    option_chosen_floor = 0
    option_chosen_floors = 2
    default = 0


class ChosenFloor(Range):
    """The single floor used when Goal Mode is chosen_floor."""
    display_name = "Chosen Floor"
    range_start = 1
    range_end = 20
    default = 1


class ChosenFloors(OptionSet):
    """Floors used when goal_mode is chosen_floors.
Example:
chosen_floors: [1, 5, 12]"""
    display_name = "Chosen Floors"
    valid_keys = frozenset(str(i) for i in range(1, 21))
    default = frozenset({"1"})


class FloorsRequired(Range):
    """How many selected floors must be cleared.
0 = random amount.
Values above selected floor count are clamped."""
    display_name = "Floors Required"
    range_start = 0
    range_end = 20
    default = 1






class FloorUnlockMode(Choice):
    """How selected AP floors are available.
start_with_all = all selected floors start open.
unlock_through_items = first floor starts open, others need Unlock Floor items."""
    display_name = "Floor Unlock Mode"
    option_start_with_all = 0
    option_unlock_through_items = 1
    default = 1


class FloorPaymentChecks(Choice):
    """Payment check style.
shared = one Payment 1-12 chain for the slot.
per_floor = Floor X Payment Y checks for selected floors."""
    display_name = "Floor Payment Checks"
    option_shared = 0
    option_per_floor = 1
    default = 0

class ItemBundles(Choice):
    """Bundle multiple unlocks into one AP item.
The client unlocks everything listed inside the bundle."""
    display_name = "Item Bundles"
    option_off = 0
    option_on = 1
    default = 0


class ItemBundleSize(Range):
    """Maximum unlocks inside each bundle.
Only used when item_bundles is on.
Max is 10."""
    display_name = "Item Bundle Size"
    range_start = 2
    range_end = 10
    default = 10


class TwoItemBundles(Toggle):
    """Force bundles to contain 2 unlocks each.
The final leftover bundle may have 1."""
    display_name = "Two Item Bundles"
    default = 0


class ForceSphereOneSymbols(OptionSet):
    """Symbol unlocks forced into sphere 1.
Example:
force_sphere_one_symbols: [Crab]"""
    display_name = "Force Sphere One Symbols"
    valid_keys = frozenset(SYMBOLS)
    default = frozenset()


class RareChecks(Choice):
    """Include Rare First-Get checks.
off = rare content is not AP checks/items.
Use rare_very_rare_in_game_pool to keep them in-game."""
    display_name = "Rare Checks"
    option_off = 0
    option_on = 1
    default = 1


class VeryRareChecks(Choice):
    """Include Very Rare First-Get checks.
off = very rare content is not AP checks/items.
Use rare_very_rare_in_game_pool to keep them in-game."""
    display_name = "Very Rare Checks"
    option_off = 0
    option_on = 1
    default = 1


class RareVeryRareInGamePool(Choice):
    """Allow removed Rare/Very Rare checks in-game.
on = they can appear normally in LBAL at their regular rarity chance.
They still are not AP checks or AP unlock items."""
    display_name = "Rare/Very Rare In-Game Pool"
    option_off = 0
    option_on = 1
    default = 1


class ItemRandomizer(Choice):
    """Randomize normal items as AP unlocks/checks.
off = normal items are vanilla
and can appear without AP unlocks."""
    display_name = "Item Randomizer"
    option_off = 0
    option_on = 1
    default = 1


class EssenceRandomizer(Choice):
    """Randomize essences as AP unlocks/checks.
off = essences are vanilla
and can appear without AP unlocks."""
    display_name = "Essence Randomizer"
    option_off = 0
    option_on = 1
    default = 0




class ProgressiveAPChecks(Toggle):
    """Start with AP Check 1-10.
Each Progressive AP Checks item opens the next 10 checks.
Keeps sphere logic clean."""
    display_name = "Progressive AP Checks"
    default = 1

class UnlockableChanceBoost(Toggle):
    """Boost newly AP-unlocked content in-game.
off = normal LBAL rarity chances.
on = use unlockable_chance_boost_mode."""
    display_name = "Unlockable Chance Boost"
    default = 0


class UnlockableChanceBoostMode(Choice):
    """How boost mode works.
regular = normal LBAL rarity chances.
category = boost current symbol/item/essence category.
category_and_rarity = boost current category and matching rarity."""
    display_name = "Unlockable Chance Boost Mode"
    option_regular = 0
    option_category = 1
    option_category_and_rarity = 2
    default = 2


class RaspberryPool(Range):
    """Number of Raspberry AP items in the pool.
0 disables Raspberry goal mode.
Max is 50."""
    display_name = "Raspberry Pool"
    range_start = 0
    range_end = 50
    default = 20


class RaspberryRequired(Range):
    """Number of Raspberry items required to finish.
0 = require all Raspberry items in the pool.
Max is 50."""
    display_name = "Raspberry Required"
    range_start = 0
    range_end = 50
    default = 10



class Buffs(Toggle):
    """Replace a percentage of filler checks with enabled buff items."""
    display_name = "Buffs"
    default = 0


class BuffPercentage(Range):
    """Percentage of filler checks replaced by buff items when Buffs is on."""
    display_name = "Buff Percentage"
    range_start = 0
    range_end = 100
    default = 10


class EnabledBuffs(OptionSet):
    """Buff items that can replace filler checks."""
    display_name = "Enabled Buffs"
    valid_keys = frozenset(BUFF_ITEMS)
    default = frozenset(BUFF_ITEMS)


class Traps(Toggle):
    """Replace a percentage of filler checks with enabled trap items."""
    display_name = "Traps"
    default = 0


class TrapPercentage(Range):
    """Percentage of filler checks replaced by trap items when Traps is on."""
    display_name = "Trap Percentage"
    range_start = 0
    range_end = 100
    default = 10


class EnabledTraps(OptionSet):
    """Trap items that can replace filler checks."""
    display_name = "Enabled Traps"
    valid_keys = frozenset(TRAP_ITEMS)
    default = frozenset(TRAP_ITEMS)



class BuffTrapWeight(Choice):
    """Individual buff/trap frequency.
none = disabled.
low = low chance.
medium = normal chance.
high = high chance."""
    display_name = "Buff/Trap Weight"
    option_none = 0
    option_low = 1
    option_medium = 2
    option_high = 3
    default = 2



class StartDestroyTokenBuffWeight(BuffTrapWeight):
    display_name = "Start With a Destroy Token Buff Weight"


class Start5DollarsBuffWeight(BuffTrapWeight):
    display_name = "Start With $5 Buff Weight"


class StartRerollTokenBuffWeight(BuffTrapWeight):
    display_name = "Start With a Reroll Token Buff Weight"


class StartEssenceTokenBuffWeight(BuffTrapWeight):
    display_name = "Start With an Essence Token Buff Weight"


class ChoiceSymbolsBuffWeight(BuffTrapWeight):
    display_name = "Choice of Symbols Buff Weight"


class HalfMoneyTrapWeight(BuffTrapWeight):
    display_name = "Half Money Trap Weight"


class ForcePaymentTrapWeight(BuffTrapWeight):
    display_name = "Force Payment Trap Weight"


class AddDudSymbolTrapWeight(BuffTrapWeight):
    display_name = "Add Dud Symbol Trap Weight"



class LowChanceBuffs(OptionSet):
    """Buffs that should appear less often inside buff filler slots."""
    display_name = "Low Chance Buffs"
    valid_keys = frozenset(BUFF_ITEMS)
    default = frozenset()


class MediumChanceBuffs(OptionSet):
    """Buffs that should appear at normal weight inside buff filler slots."""
    display_name = "Medium Chance Buffs"
    valid_keys = frozenset(BUFF_ITEMS)
    default = frozenset(BUFF_ITEMS)


class HighChanceBuffs(OptionSet):
    """Buffs that should appear more often inside buff filler slots."""
    display_name = "High Chance Buffs"
    valid_keys = frozenset(BUFF_ITEMS)
    default = frozenset()


class LowChanceTraps(OptionSet):
    """Traps that should appear less often inside trap filler slots."""
    display_name = "Low Chance Traps"
    valid_keys = frozenset(TRAP_ITEMS)
    default = frozenset()


class MediumChanceTraps(OptionSet):
    """Traps that should appear at normal weight inside trap filler slots."""
    display_name = "Medium Chance Traps"
    valid_keys = frozenset(TRAP_ITEMS)
    default = frozenset(TRAP_ITEMS)


class HighChanceTraps(OptionSet):
    """Traps that should appear more often inside trap filler slots."""
    display_name = "High Chance Traps"
    valid_keys = frozenset(TRAP_ITEMS)
    default = frozenset()



class DeathLink(Toggle):
    """Enable DeathLink.
Incoming DeathLinks end the current run.
Failing to pay rent sends a DeathLink."""
    display_name = "DeathLink"
    default = 0


class DeathLinkReceiveChance(Range):
    """Chance that an incoming DeathLink ends your run.
100 = always."""
    display_name = "DeathLink Receive Chance"
    range_start = 0
    range_end = 100
    default = 100


class DeathLinkReceiveThreshold(Range):
    """Incoming DeathLinks needed before one is applied."""
    display_name = "DeathLink Receive Threshold"
    range_start = 1
    range_end = 20
    default = 1


class DeathLinkSendThreshold(Range):
    """Failed rent runs needed before sending DeathLink."""
    display_name = "DeathLink Send Threshold"
    range_start = 1
    range_end = 20
    default = 1


class ForcePaymentTrapCountsDeathLink(Toggle):
    """If enabled, a run ended by the Force Payment trap can count toward outgoing DeathLink.
If disabled, Force Payment trap failures are ignored for outgoing DeathLink."""
    display_name = "Force Payment Trap Counts For DeathLink"
    default = 1


@dataclass
class LuckOptions(PerGameCommonOptions):
    extra_filler_checks: ExtraFillerChecks
    starting_symbol_mode: StartingSymbolMode
    goal_mode: GoalMode
    chosen_floor: ChosenFloor
    chosen_floors: ChosenFloors
    floors_required: FloorsRequired
    floor_unlock_mode: FloorUnlockMode
    floor_payment_checks: FloorPaymentChecks
    item_bundles: ItemBundles
    item_bundle_size: ItemBundleSize
    two_item_bundles: TwoItemBundles
    force_sphere_one_symbols: ForceSphereOneSymbols
    rare_checks: RareChecks
    very_rare_checks: VeryRareChecks
    rare_very_rare_in_game_pool: RareVeryRareInGamePool
    item_randomizer: ItemRandomizer
    essence_randomizer: EssenceRandomizer
    progressive_ap_checks: ProgressiveAPChecks
    unlockable_chance_boost: UnlockableChanceBoost
    unlockable_chance_boost_mode: UnlockableChanceBoostMode
    deathlink: DeathLink
    deathlink_receive_chance: DeathLinkReceiveChance
    deathlink_receive_threshold: DeathLinkReceiveThreshold
    deathlink_send_threshold: DeathLinkSendThreshold
    force_payment_trap_counts_deathlink: ForcePaymentTrapCountsDeathLink
    raspberry_pool: RaspberryPool
    raspberry_required: RaspberryRequired
    buffs: Buffs
    buff_percentage: BuffPercentage
    start_destroy_token_buff_weight: StartDestroyTokenBuffWeight
    start_5_dollars_buff_weight: Start5DollarsBuffWeight
    start_reroll_token_buff_weight: StartRerollTokenBuffWeight
    start_essence_token_buff_weight: StartEssenceTokenBuffWeight
    choice_symbols_buff_weight: ChoiceSymbolsBuffWeight
    traps: Traps
    trap_percentage: TrapPercentage
    half_money_trap_weight: HalfMoneyTrapWeight
    force_payment_trap_weight: ForcePaymentTrapWeight
    add_dud_symbol_trap_weight: AddDudSymbolTrapWeight
