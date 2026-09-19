from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle, OptionSet, DefaultOnToggle, Visibility

# In this file, we define the options the player can pick.
# The most common types of options are Toggle, Range and Choice.

# Options will be in the game's template yaml.
# They will be represented by checkboxes, sliders etc. on the game's options page on the website.
# (Note: Options can also be made invisible from either of these places by overriding Option.visibility.
#  APQuest doesn't have an example of this, but this can be used for secret / hidden / advanced options.)

# For further reading on options, you can also read the Options API Document:
# https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/options%20api.md


# The first type of Option we'll discuss is the Toggle.
# A toggle is an option that can either be on or off. This will be represented by a checkbox on the website.
# The default for a toggle is "off".
# If you want a toggle to be on by default, you can use the "DefaultOnToggle" class instead of the "Toggle" class.

class Rare(Toggle):
    """
    If Rare Rarity Symbols, Items and Essence will be in the pool to be able to send checks from
    """

    display_name = "Rare"

class VeryRare(Toggle):
    """
    If Very Rare Symbols, Items and Essence will be in the pool to be able to send checks from
    """

    display_name = "Very Rare"

class ShinyCoin(DefaultOnToggle):
    """
    This will decide if Shiny Coins (McGuffins) will be added into the pool over Filler
    """

    display_name = "Shiny Coins"

class HowmanyShinyCoins(Range):
    """
    This will decide percentage of Filler become Shiny Coin before goaling
    """

    range_start = 0
    range_end = 100

    default = 10

class ExtraShinyCoins(Range):
    """
    This will decide percentage of Filler become Extra Shiny Coins 
    """

    range_start = 0 
    range_end = 100

    default = 5


class Deathlink(Toggle):
    """
    This will be a toggle to see if deathlink will be sent or recieved

    Togglable in game
    """

    display_name = "Deathlink"

class Payment(Choice):
    """
    If deathlink is on this will decide what type of deathlink it will be

    Force Payment will send you to next payment screen

    End Run will give you the game over screen
    """

    display_name = "Deathlink Options"

    option_Forcepayment = 0
    option_Endrun = 1

    default = option_Endrun

class Boost(Toggle):
    """
    This is if you want to have it removes symbols that have done all the checks for it
    Its Togglable in game if you change your mind later
    """

    display_name = "Boost"

class TrapChance(Range):
    """
    Percentage chance that any given Filler will be replaced with Traps.
    """

    display_name = "Trap Chance"

    range_start = 0
    range_end = 100
    default = 0

class Forcepayment(Toggle):

    """
    This Trap will send you to the next payment screen 
    """

    display_name = "Force Payment Trap"

class Dud(Toggle):

    """
    This Trap will add a Dud Symbol into your inventory
    """

    display_name = "Dud Symbol Trap"

class HalfMoney(Toggle):
    """
    This Trap will half the amount of money you have
    """

class BuffChance(Range):
    """
    Percentage chance that any give Filler will be Replaced with Buffs.
    """
    display_name = "Buff Chance"

    range_start = 0
    range_end = 100
    default = 20

class SymbolBomb(DefaultOnToggle):
    """
    Start with 1 more symbol choice
    """

    display_name = "Starting Symbol"

class StartMoney(DefaultOnToggle):
    """
    This will start you with $5 more money each time
    """

    display_name = "$5 Buff"

class RemovalToken(Toggle):
    """
    This will give you a Removal token start of each run
    """

    display_name = "Removal Token Buff"

class RerollToken(Toggle):
    """
    This will give you a Reroll token start of each run
    """

    display_name = "Reroll Token Buff"

class EssenceToken(DefaultOnToggle):
    """
    This will give you a Essence token start of each run
    """

    display_name = "Essence Token Buff"

class Workshopmods(Toggle):
    """
    This will need to be able to send checks out because there is a chance it wont work
    """

    Display_name = "Worshop Mods"
    visibility = Visibility.none

class WorkshopmodsAbility(Toggle):
    """
    Higher Chance this will not work so if the host is ok with sending out alot of checks manually then turn it on if not leave this off 
    """

    display_name = "Workshop Mods Ability"
    visibility = Visibility.none

class Floors(OptionSet):
    """Floors that are enabled for this seed."""

    display_name = "Floors"

    valid_keys = {
        "2", "3", "4", "5", "6", "7", "8", "9", "10",
        "11", "12", "13", "14", "15", "16", "17",
        "18", "19", "20"
    }

    default = {"2", "3"}
    


class FloorDependentChecks(Toggle):
    """
    This was built with Ai use if you want

    Send and Effect checks are across all enabled floors.

    This forces an 90% local Fill

    Only for Asyncs with permission or Syncs byourself

    If your reading this your looking at the code
    I made it for a joke with warnings built in
    so it doesn't ruin anyones sync or async

    At the end of the day be reasonable
    """

    display_name = "Floor Check sanity"
    visibility = Visibility.none



# We must now define a dataclass inheriting from PerGameCommonOptions that we put all our options in.
# This is in the format "option_name_in_snake_case: OptionClassName".
@dataclass

class LBALOptions(PerGameCommonOptions):
    Rare: Rare
    VeryRare: VeryRare
    ShinyCoin: ShinyCoin
    HowmanyShinyCoins: HowmanyShinyCoins
    ExtraShinyCoins: ExtraShinyCoins
    Deathlink: Deathlink
    Payment: Payment
    TrapChance: TrapChance
    Forcepayment: Forcepayment
    Dud: Dud
    HalfMoney: HalfMoney
    BuffChance: BuffChance
    SymbolBomb: SymbolBomb
    StartMoney: StartMoney
    RemovalToken: RemovalToken
    RerollToken: RerollToken
    EssenceToken: EssenceToken
    Workshopmods: Workshopmods
    WorkshopmodsAbility: WorkshopmodsAbility
    Floors: Floors
    Boost: Boost
    FloorDependentChecks: FloorDependentChecks







# If we want to group our options by similar type, we can do so as well. This looks nice on the website.
option_groups = [
    OptionGroup(
        "Gameplay Options",
        [Rare, VeryRare, Boost, ShinyCoin, HowmanyShinyCoins, ExtraShinyCoins],
    ),
    OptionGroup(
        "Floors",
        [Floors],
    ),
    OptionGroup(
        "Traps Options",
        [TrapChance, Dud, Forcepayment, HalfMoney],
    ),
    OptionGroup(
        "Buff Options",
        [BuffChance, SymbolBomb, StartMoney, RemovalToken, RerollToken, EssenceToken],
    ),
    OptionGroup(
        "Deathlink",
        [Deathlink, Payment],
    ),
    OptionGroup(
        "Doesn't Work",
        [Workshopmods, WorkshopmodsAbility],
    ),
    OptionGroup(
        "Ai made Sanitys",
        [FloorDependentChecks],
    )
]

