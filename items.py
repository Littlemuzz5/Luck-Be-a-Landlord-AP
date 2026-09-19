from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

if TYPE_CHECKING:
    from .world import LBALWorld

# Every item must have a unique integer ID associated with it.
# We will have a lookup from item name to ID here that, in world.py, we will import and bind to the world class.
# Even if an item doesn't exist on specific options, it must be present in this lookup.
ITEM_NAME_TO_ID = {
    "Unlock: Amethyst": 1,
    "Unlock: Anchor": 2,
    "Unlock: Apple": 3, 
    "Unlock: Banana": 4,
    "Unlock: Banana Peel": 5,
    "Unlock: Bar of Soap": 6,
    "Unlock: Bartender": 7,
    "Unlock: Bear": 8, 
    "Unlock: Beastmaster": 9,
    "Unlock: Bee": 10,
    "Unlock: Beehive": 11,
    "Unlock: Beer": 12,
    "Unlock: Big Ore": 13,
    "Unlock: Big Urn": 14, 
    "Unlock: Billionaire": 15, 
    "Unlock: Bounty Hunter": 16,
    "Unlock: Bronze Arrow": 17, 
    "Unlock: Bubble": 18,
    "Unlock: Buffing Capsule": 19,
    "Unlock: Candy": 20, 
    "Unlock: Card Shark": 21,
    "Unlock: Cat": 22,
    "Unlock: Cheese": 23, 
    "Unlock: Chef": 24,
    "Unlock: Chemical Seven": 25, 
    "Unlock: Cherry": 26,
    "Unlock: Chick": 27, 
    "Unlock: Chicken": 28,
    "Unlock: Clubs": 29,
    "Unlock: Coal": 30,
    "Unlock: Coconut": 31,
    "Unlock: Coconut Half": 32,
    "Unlock: Coin": 33,
    "Unlock: Comedian": 34,
    "Unlock: Cow": 35,
    "Unlock: Crab": 36,
    "Unlock: Crow": 37,
    "Unlock: Cultist": 38, 
    "Unlock: Dame": 39,
    "Unlock: Diamond": 40,
    "Unlock: Diamonds": 41,
    "Unlock: Diver": 42,
    "Unlock: Dog": 43,
    "Unlock: Dove": 44,
    "Unlock: Dwarf": 45,
    "Unlock: Egg": 46,
    "Unlock: Eldritch Creature": 47,
    "Unlock: Emerald": 48,
    "Unlock: Essence Capsule": 49,
    "Unlock: Farmer": 50,
    "Unlock: Five-Sided Die": 51,
    "Unlock: Flower": 52,
    "Unlock: Frozen Fossil": 53,
    "Unlock: Gambler": 54,
    "Unlock: General Zaroff": 55,
    "Unlock: Geologist": 56,
    "Unlock: Golden Arrow": 57,
    "Unlock: Golden Egg": 58,
    "Unlock: Goldfish": 59,
    "Unlock: Golem": 60,
    "Unlock: Goose": 61,
    "Unlock: Hearts": 62,
    "Unlock: Hex of Destruction": 63,
    "Unlock: Hex of Draining": 64,
    "Unlock: Hex of Emptiness": 65,
    "Unlock: Hex of Hoarding": 66,
    "Unlock: Hex of Midas": 67,
    "Unlock: Hex of Tedium": 68,
    "Unlock: Hex of Thievery": 69,
    "Unlock: Highlander": 70,
    "Unlock: Honey": 71,
    "Unlock: Hooligan": 72,
    "Unlock: Hustling Capsule": 73, 
    "Unlock: Item Capsule": 74,
    "Unlock: Jellyfish": 75, 
    "Unlock: Joker": 76,
    "Unlock: Key": 77,
    "Unlock: King Midas": 78,
    "Unlock: Light Bulb": 79,
    "Unlock: Lockbox": 80,
    "Unlock: Lucky Capsule": 81,
    "Unlock: Magic Key": 82,
    "Unlock: Magpie": 83,
    "Unlock: Martini": 84,
    "Unlock: Matryoshka Doll": 85,
    "Unlock: Mega Chest": 90,
    "Unlock: Midas Bomb": 91,
    "Unlock: Milk": 92,
    "Unlock: Mine": 93,
    "Unlock: Miner": 94,
    "Unlock: Monkey": 95,
    "Unlock: Moon": 96,
    "Unlock: Mouse": 97,
    "Unlock: Mrs. Fruit": 98,
    "Unlock: Ninja": 99,
    "Unlock: Omelette": 100,
    "Unlock: Orange": 101,
    "Unlock: Ore": 102,
    "Unlock: Owl": 103,
    "Unlock: Oyster": 104,
    "Unlock: Peach": 105,
    "Unlock: Pear": 106,
    "Unlock: Pearl": 107,
    "Unlock: Pirate": 108,
    "Unlock: Pinata": 109,
    "Unlock: Present": 110,
    "Unlock: Pufferfish": 111,
    "Unlock: Rabbit": 112,
    "Unlock: Rabbit Fluff": 113, 
    "Unlock: Rain": 114,
    "Unlock: Removal Capsule": 115,
    "Unlock: Reroll Capsule": 116,
    "Unlock: Robin Hood": 117,
    "Unlock: Ruby": 118,
    "Unlock: Safe": 119,
    "Unlock: Sand Dollar": 120,
    "Unlock: Sapphire": 121,
    "Unlock: Seed": 122,
    "Unlock: Shiny Pebble": 123,
    "Unlock: Silver Arrow": 124,
    "Unlock: Sloth": 125,
    "Unlock: Snail": 126,
    "Unlock: Spades": 127,
    "Unlock: Spirit": 128,
    "Unlock: Strawberry": 129,
    "Unlock: Sun": 130,
    "Unlock: Target": 131,
    "Unlock: Tedium Capsule": 132,
    "Unlock: Thief": 133,
    "Unlock: Three-Sided Die": 134,
    "Unlock: Time Capsule": 135,
    "Unlock: Toddler": 136,
    "Unlock: Tomb": 137,
    "Unlock: Treasure Chest": 138,
    "Unlock: Turtle": 139,
    "Unlock: Urn": 140,
    "Unlock: Void Creature": 141,
    "Unlock: Void Fruit": 142,
    "Unlock: Void Stone": 143,
    "Unlock: Watermelon": 144,
    "Unlock: Wealthy Capsule": 145,
    "Unlock: Wildcard": 146,
    "Unlock: Wine": 147,
    "Unlock: Witch": 148,
    "Unlock: Wolf": 149,
    "Unlock: 5th Ace": 150,
    "Unlock: Adoption Papers": 151,
    "Unlock: Ancient Lizard Blade": 152,
    "Unlock: Anthropology Degree": 153,
    "Unlock: Barrel of Dwarves": 154,
    "Unlock: Big Symbol Bomb": 155,
    "Unlock: Birdhouse": 156,
    "Unlock: Black Cat": 157,
    "Unlock: Black Pepper": 158,
    "Unlock: Black Suits": 159,
    "Unlock: Blue Pepper": 160,
    "Unlock: Booster Pack": 161,
    "Unlock: Bowling Ball": 162,
    "Unlock: Brown Pepper": 163,
    "Unlock: Capsule Machine": 164,
    "Unlock: Cardboard Box": 165,
    "Unlock: Checkered Flag": 166,
    "Unlock: Chicken Coop": 167,
    "Unlock: Chili Powder": 168,
    "Unlock: Cleaning Rag": 169,
    "Unlock: Clear Sky": 170,
    "Unlock: Coffee": 171,
    "Unlock: Coin on a String": 172,
    "Unlock: Comfy Pillow": 173,
    "Unlock: Compost Heap": 174,
    "Unlock: Conveyor Belt": 175,
    "Unlock: Copycat": 176,
    "Unlock: Credit Card": 178,
    "Unlock: Cursed Katana": 179,
    "Unlock: Cyan Pepper": 180,
    "Unlock: Dark Humor": 181,
    "Unlock: Devil's Deal": 182,
    "Unlock: Dishwasher": 183,
    "Unlock: Dwarven Anvil": 184,
    "Unlock: Egg Carton": 185,
    "Unlock: Fertilizer": 186,
    "Unlock: Fish Tank": 187,
    "Unlock: Flush": 188,
    "Unlock: Four-leaf clover": 189,
    "Unlock: Frozen Pizza": 190,
    "Unlock: Fruit Basket": 191,
    "Unlock: Frying Pan": 192,
    "Unlock: Golden Carrot": 193,
    "Unlock: Goldilocks": 194,
    "Unlock: Grave Robber": 195,
    "Unlock: Gray Pepper": 196,
    "Unlock: Green Pepper": 197,
    "Unlock: Guillotine": 198,
    "Unlock: Happy Hour": 199,
    "Unlock: Holy Water": 200,
    "Unlock: Horseshoe": 201,
    "Unlock: Instant Ramen": 202,
    "Unlock: Jack-o'-lantern": 203,
    "Unlock: Kyle the Kernite": 204,
    "Unlock: Lefty the Rabbit": 205,
    "Unlock: Lemon": 206,
    "Unlock: Lime Pepper": 207,
    "Unlock: Lint Roller": 208,
    "Unlock: Lockpick": 209,
    "Unlock: Looting Glove": 210,
    "Unlock: Lucky Carrot": 211,
    "Unlock: Lucky Cat": 212,
    "Unlock: Lucky Dice": 213,
    "Unlock: Lucky Seven": 214,
    "Unlock: Lunchbox": 215,
    "Unlock: Maxwell the Bear": 216,
    "Unlock: Mining Pick": 217,
    "Unlock: Mobius Strip": 218,
    "Unlock: Ninja and Mouse": 219,
    "Unlock: Nori the Rabbit": 220,
    "Unlock: Oil Can": 221,
    "Unlock: Oswald the Monkey": 222,
    "Unlock: Piggy Bank": 223,
    "Unlock: Pink Pepper": 224,
    "Unlock: Pizza the Cat": 225,
    "Unlock: Pool Ball": 226,
    "Unlock: Popsicle": 227,
    "Unlock: Protractor": 228,
    "Unlock: Purple Pepper": 229,
    "Unlock: Quantum Symbol Bomb": 230,
    "Unlock: Quigley the Wolf": 408,
    "Unlock: Quiver": 231,
    "Unlock: Rain Cloud": 232,
    "Unlock: Recycling": 233,
    "Unlock: Red Pepper": 234,
    "Unlock: Red Suits": 235,
    "Unlock: Reroll": 236,
    "Unlock: Ricky the Banana": 237,
    "Unlock: Ritual Candle": 238,
    "Unlock: Rusty Gear": 239,
    "Unlock: Shattered Mirror": 240,
    "Unlock: Shedding Season": 241,
    "Unlock: Shrine": 242,
    "Unlock: Small Symbol Bomb": 243,
    "Unlock: Sunglasses": 244,
    "Unlock: Swapping Device": 245,
    "Unlock: Swear Jar": 246,
    "Unlock: Tax Evasion": 247,
    "Unlock: Telescope": 248,
    "Unlock: The Tortoise and the Hare": 249,
    "Unlock: Time Machine": 250,
    "Unlock: Treasure Map": 251,
    "Unlock: Triple Coins": 252,
    "Unlock: Undertaker": 253,
    "Unlock: Very Big Symbol Bomb": 254,
    "Unlock: Void Party": 255,
    "Unlock: Void Portal": 256,
    "Unlock: Wanted Poster": 257,
    "Unlock: Watering Can": 258,
    "Unlock: White Pepper": 259,
    "Unlock: X-ray Machine": 260,
    "Unlock: Yellow Pepper": 261,
    "Unlock: Zaroff's Contract": 262,
    "Unlock: 5th Ace Essence": 263,
    "Unlock: Adoption Papers Essence": 264,
    "Unlock: Ancient Lizard Blade Essence": 265,
    "Unlock: Anthropology Degree Essence": 266,
    "Unlock: Barrel of Dwarves Essence": 267,
    "Unlock: Big Symbol Bomb Essence": 268,
    "Unlock: Birdhouse Essence": 269,
    "Unlock: Black Cat Essence": 270,
    "Unlock: Black Pepper Essence": 271,
    "Unlock: Black Suits Essence": 272,
    "Unlock: Blue Pepper Essence": 273,
    "Unlock: Booster Pack Essence": 407,
    "Unlock: Bowling Ball Essence": 274,
    "Unlock: Brown Pepper Essence": 275,
    "Unlock: Capsule Machine Essence": 276,
    "Unlock: Cardboard Box Essence": 277,
    "Unlock: Checkered Flag Essence": 278,
    "Unlock: Chicken Coop Essence": 279,
    "Unlock: Chili Powder Essence": 280,
    "Unlock: Cleaning Rag Essence": 281,
    "Unlock: Clear Sky Essence": 282,
    "Unlock: Coffee Essence": 283,
    "Unlock: Coin on a String Essence": 284,
    "Unlock: Comfy Pillow Essence": 285,
    "Unlock: Compost Heap Essence": 286,
    "Unlock: Conveyor Belt Essence": 287,
    "Unlock: Copycat Essence": 288,
    "Unlock: Credit Card Essence": 289,
    "Unlock: Cursed Katana Essence": 290,
    "Unlock: Cyan Pepper Essence": 291,
    "Unlock: Dark Humor Essence": 292,
    "Unlock: Devil's Deal Essence": 293,
    "Unlock: Dishwasher Essence": 294,
    "Unlock: Dwarven Anvil Essence": 295,
    "Unlock: Egg Carton Essence": 296,
    "Unlock: Fertilizer Essence": 297,
    "Unlock: Fish Tank Essence": 298,
    "Unlock: Flush Essence": 299,
    "Unlock: Four-leaf clover Essence": 300,
    "Unlock: Frozen Pizza Essence": 301,
    "Unlock: Fruit Basket Essence": 302,
    "Unlock: Frying Pan Essence": 303,
    "Unlock: Golden Carrot Essence": 409,
    "Unlock: Goldilocks Essence": 305,
    "Unlock: Grave Robber Essence": 306,
    "Unlock: Gray Pepper Essence": 307,
    "Unlock: Green Pepper Essence": 308,
    "Unlock: Guillotine Essence": 309,
    "Unlock: Happy Hour Essence": 310,
    "Unlock: Holy Water Essence": 311,
    "Unlock: Horseshoe Essence": 312,
    "Unlock: Instant Ramen Essence": 313,
    "Unlock: Jack-o'-lantern Essence": 314,
    "Unlock: Kyle the Kernite Essence": 315,
    "Unlock: Lefty the Rabbit Essence": 316,
    "Unlock: Lemon Essence": 317,
    "Unlock: Lime Pepper Essence": 318,
    "Unlock: Lint Roller Essence": 319,
    "Unlock: Lockpick Essence": 320,
    "Unlock: Looting Glove Essence": 321,
    "Unlock: Lucky Carrot Essence": 322,
    "Unlock: Lucky Cat Essence": 323,
    "Unlock: Lucky Dice Essence": 324,
    "Unlock: Lucky Seven Essence": 325,
    "Unlock: Lunchbox Essence": 326,
    "Unlock: Maxwell the Bear Essence": 327,
    "Unlock: Mining Pick Essence": 328,
    "Unlock: Mobius Strip Essence": 329,
    "Unlock: Ninja and Mouse Essence": 330,
    "Unlock: Nori the Rabbit Essence": 331,
    "Unlock: Oil Can Essence": 332,
    "Unlock: Oswald the Monkey Essence": 333,
    "Unlock: Piggy Bank Essence": 334,
    "Unlock: Pink Pepper Essence": 335,
    "Unlock: Pizza the Cat Essence": 336,
    "Unlock: Pool Ball Essence": 337,
    "Unlock: Popsicle Essence": 338,
    "Unlock: Protractor Essence": 339,
    "Unlock: Purple Pepper Essence": 340,
    "Unlock: Quantum Symbol Bomb Essence": 341,
    "Unlock: Quigley the Wolf Essence": 342,
    "Unlock: Quiver Essence": 343,
    "Unlock: Rain Cloud Essence": 344,
    "Unlock: Recycling Essence": 345,
    "Unlock: Red Pepper Essence": 346,
    "Unlock: Red Suits Essence": 347,
    "Unlock: Reroll Essence": 348,
    "Unlock: Ricky the Banana Essence": 349,
    "Unlock: Ritual Candle Essence": 350,
    "Unlock: Rusty Gear Essence": 351,
    "Unlock: Shattered Mirror Essence": 352,
    "Unlock: Shedding Season Essence": 353,
    "Unlock: Shrine Essence": 354,
    "Unlock: Small Symbol Bomb Essence": 355,
    "Unlock: Sunglasses Essence": 356,
    "Unlock: Swapping Device Essence": 357,
    "Unlock: Swear Jar Essence": 358,
    "Unlock: Tax Evasion Essence": 359,
    "Unlock: Telescope Essence": 360,
    "Unlock: The Tortoise and the Hare Essence": 361,
    "Unlock: Time Machine Essence": 362,
    "Unlock: Treasure Map Essence": 363,
    "Unlock: Triple Coins Essence": 364,
    "Unlock: Undertaker Essence": 365,
    "Unlock: Very Big Symbol Bomb Essence": 366,
    "Unlock: Void Party Essence": 367,
    "Unlock: Void Portal Essence": 368,
    "Unlock: Wanted Poster Essence": 369,
    "Unlock: Watering Can Essence": 370,
    "Unlock: White Pepper Essence": 371,
    "Unlock: X-ray Machine Essence": 372,
    "Unlock: Yellow Pepper Essence": 373,
    "Unlock: Zaroff's Contract Essence": 374,

    "Floor 2 Unlock": 375,
    "Floor 3 Unlock": 376,
    "Floor 4 Unlock": 377,
    "Floor 5 Unlock": 378,
    "Floor 6 Unlock": 379,
    "Floor 7 Unlock": 380,
    "Floor 8 Unlock": 381,
    "Floor 9 Unlock": 382,
    "Floor 10 Unlock": 383,
    "Floor 11 Unlock": 384,
    "Floor 12 Unlock": 385,
    "Floor 13 Unlock": 386,
    "Floor 14 Unlock": 387,
    "Floor 15 Unlock": 388,
    "Floor 16 Unlock": 389,
    "Floor 17 Unlock": 390,
    "Floor 18 Unlock": 391,
    "Floor 19 Unlock": 392,
    "Floor 20 Unlock": 393,

    "Starting Symbol": 394,
    "$5 Starting Money": 395,
    "Removal Token": 396,
    "Reroll Token": 397,
    "Essence Token": 398,
    
    "Half Money": 399,
    "Force Payment": 400,
    "Dud Symbol": 401,

    "Progressive Nothing": 402,
    "Too Tiny to Resemble Something": 403,
    "A Really Really Small Coin": 404,

    "Shiny Coin": 405,

    "Progressive AP": 406,
}

# Items should have a defined default classification.
# In our case, we will make a dictionary from item name to classification.
DEFAULT_ITEM_CLASSIFICATIONS = {

    "Shiny Coin": ItemClassification.progression,

    "Progressive AP": ItemClassification.progression,

    "Starting Symbol": ItemClassification.useful,
    "$5 Starting Money": ItemClassification.useful,
    "Removal Token": ItemClassification.useful,
    "Reroll Token": ItemClassification.useful,
    "Essence Token": ItemClassification.useful,

    "Half Money": ItemClassification.trap,
    "Force Payment": ItemClassification.trap,
    "Dud Symbol": ItemClassification.trap,

    "Progressive Nothing": ItemClassification.filler,
    "Too Tiny to Resemble Something": ItemClassification.filler,
    "A Really Really Small Coin": ItemClassification.filler,

    "Floor 2 Unlock": ItemClassification.progression,
    "Floor 3 Unlock": ItemClassification.progression,
    "Floor 4 Unlock": ItemClassification.progression,
    "Floor 5 Unlock": ItemClassification.progression,
    "Floor 6 Unlock": ItemClassification.progression,
    "Floor 7 Unlock": ItemClassification.progression,
    "Floor 8 Unlock": ItemClassification.progression,
    "Floor 9 Unlock": ItemClassification.progression,
    "Floor 10 Unlock": ItemClassification.progression,
    "Floor 11 Unlock": ItemClassification.progression,
    "Floor 12 Unlock": ItemClassification.progression,
    "Floor 13 Unlock": ItemClassification.progression,
    "Floor 14 Unlock": ItemClassification.progression,
    "Floor 15 Unlock": ItemClassification.progression,
    "Floor 16 Unlock": ItemClassification.progression,
    "Floor 17 Unlock": ItemClassification.progression,
    "Floor 18 Unlock": ItemClassification.progression,
    "Floor 19 Unlock": ItemClassification.progression,
    "Floor 20 Unlock": ItemClassification.progression,

    "Unlock: Amethyst": ItemClassification.progression,
    "Unlock: Anchor": ItemClassification.progression,
    "Unlock: Apple": ItemClassification.progression,
    "Unlock: Banana": ItemClassification.progression,
    "Unlock: Banana Peel": ItemClassification.progression,
    "Unlock: Bar of Soap": ItemClassification.progression,
    "Unlock: Bartender": ItemClassification.progression,
    "Unlock: Bear": ItemClassification.progression,
    "Unlock: Beastmaster": ItemClassification.progression,
    "Unlock: Bee": ItemClassification.progression,
    "Unlock: Beehive": ItemClassification.progression,
    "Unlock: Beer": ItemClassification.progression,
    "Unlock: Big Ore": ItemClassification.progression,
    "Unlock: Big Urn": ItemClassification.progression,
    "Unlock: Billionaire": ItemClassification.progression,
    "Unlock: Bounty Hunter": ItemClassification.progression,
    "Unlock: Bronze Arrow": ItemClassification.progression,
    "Unlock: Bubble": ItemClassification.progression,
    "Unlock: Buffing Capsule": ItemClassification.progression,
    "Unlock: Candy": ItemClassification.progression,
    "Unlock: Card Shark": ItemClassification.progression,
    "Unlock: Cat": ItemClassification.progression,
    "Unlock: Cheese": ItemClassification.progression,
    "Unlock: Chef": ItemClassification.progression,
    "Unlock: Chemical Seven": ItemClassification.progression,
    "Unlock: Cherry": ItemClassification.progression,
    "Unlock: Chick": ItemClassification.progression,
    "Unlock: Chicken": ItemClassification.progression,
    "Unlock: Clubs": ItemClassification.progression,
    "Unlock: Coal": ItemClassification.progression,
    "Unlock: Coconut": ItemClassification.progression,
    "Unlock: Coconut Half": ItemClassification.progression,
    "Unlock: Coin": ItemClassification.progression,
    "Unlock: Comedian": ItemClassification.progression,
    "Unlock: Cow": ItemClassification.progression,
    "Unlock: Crab": ItemClassification.progression,
    "Unlock: Crow": ItemClassification.progression,
    "Unlock: Cultist": ItemClassification.progression,
    "Unlock: Dame": ItemClassification.progression,
    "Unlock: Diamond": ItemClassification.progression,
    "Unlock: Diamonds": ItemClassification.progression,
    "Unlock: Diver": ItemClassification.progression,
    "Unlock: Dog": ItemClassification.progression,
    "Unlock: Dove": ItemClassification.progression,
    "Unlock: Dwarf": ItemClassification.progression,
    "Unlock: Egg": ItemClassification.progression,
    "Unlock: Eldritch Creature": ItemClassification.progression,
    "Unlock: Emerald": ItemClassification.progression,
    "Unlock: Essence Capsule": ItemClassification.progression,
    "Unlock: Farmer": ItemClassification.progression,
    "Unlock: Five-Sided Die": ItemClassification.progression,
    "Unlock: Flower": ItemClassification.progression,
    "Unlock: Frozen Fossil": ItemClassification.progression,
    "Unlock: Gambler": ItemClassification.progression,
    "Unlock: General Zaroff": ItemClassification.progression,
    "Unlock: Geologist": ItemClassification.progression,
    "Unlock: Golden Arrow": ItemClassification.progression,
    "Unlock: Golden Egg": ItemClassification.progression,
    "Unlock: Goldfish": ItemClassification.progression,
    "Unlock: Golem": ItemClassification.progression,
    "Unlock: Goose": ItemClassification.progression,
    "Unlock: Hearts": ItemClassification.progression,
    "Unlock: Hex of Destruction": ItemClassification.progression,
    "Unlock: Hex of Draining": ItemClassification.progression,
    "Unlock: Hex of Emptiness": ItemClassification.progression,
    "Unlock: Hex of Hoarding": ItemClassification.progression,
    "Unlock: Hex of Midas": ItemClassification.progression,
    "Unlock: Hex of Tedium": ItemClassification.progression,
    "Unlock: Hex of Thievery": ItemClassification.progression,
    "Unlock: Highlander": ItemClassification.progression,
    "Unlock: Honey": ItemClassification.progression,
    "Unlock: Hooligan": ItemClassification.progression,
    "Unlock: Hustling Capsule":  ItemClassification.progression,
    "Unlock: Item Capsule": ItemClassification.progression,
    "Unlock: Jellyfish":  ItemClassification.progression,
    "Unlock: Joker": ItemClassification.progression,
    "Unlock: Key": ItemClassification.progression,
    "Unlock: King Midas": ItemClassification.progression,
    "Unlock: Light Bulb": ItemClassification.progression,
    "Unlock: Lockbox": ItemClassification.progression,
    "Unlock: Lucky Capsule": ItemClassification.progression,
    "Unlock: Magic Key": ItemClassification.progression,
    "Unlock: Magpie": ItemClassification.progression,
    "Unlock: Martini": ItemClassification.progression,
    "Unlock: Matryoshka Doll": ItemClassification.progression,
    "Unlock: Mega Chest": ItemClassification.progression,
    "Unlock: Midas Bomb": ItemClassification.progression,
    "Unlock: Milk": ItemClassification.progression,
    "Unlock: Mine": ItemClassification.progression,
    "Unlock: Miner": ItemClassification.progression,
    "Unlock: Monkey": ItemClassification.progression,
    "Unlock: Moon": ItemClassification.progression,
    "Unlock: Mouse": ItemClassification.progression,
    "Unlock: Mrs. Fruit": ItemClassification.progression,
    "Unlock: Ninja": ItemClassification.progression,
    "Unlock: Omelette": ItemClassification.progression,
    "Unlock: Orange": ItemClassification.progression,
    "Unlock: Ore": ItemClassification.progression,
    "Unlock: Owl": ItemClassification.progression,
    "Unlock: Oyster": ItemClassification.progression,
    "Unlock: Peach": ItemClassification.progression,
    "Unlock: Pear": ItemClassification.progression,
    "Unlock: Pearl": ItemClassification.progression,
    "Unlock: Pirate": ItemClassification.progression,
    "Unlock: Pinata": ItemClassification.progression,
    "Unlock: Present": ItemClassification.progression,
    "Unlock: Pufferfish": ItemClassification.progression,
    "Unlock: Rabbit": ItemClassification.progression,
    "Unlock: Rabbit Fluff":  ItemClassification.progression,
    "Unlock: Rain": ItemClassification.progression,
    "Unlock: Removal Capsule": ItemClassification.progression,
    "Unlock: Reroll Capsule": ItemClassification.progression,
    "Unlock: Robin Hood": ItemClassification.progression,
    "Unlock: Ruby": ItemClassification.progression,
    "Unlock: Safe": ItemClassification.progression,
    "Unlock: Sand Dollar": ItemClassification.progression,
    "Unlock: Sapphire": ItemClassification.progression,
    "Unlock: Seed": ItemClassification.progression,
    "Unlock: Shiny Pebble": ItemClassification.progression,
    "Unlock: Silver Arrow": ItemClassification.progression,
    "Unlock: Sloth": ItemClassification.progression,
    "Unlock: Snail": ItemClassification.progression,
    "Unlock: Spades": ItemClassification.progression,
    "Unlock: Spirit": ItemClassification.progression,
    "Unlock: Strawberry": ItemClassification.progression,
    "Unlock: Sun": ItemClassification.progression,
    "Unlock: Target": ItemClassification.progression,
    "Unlock: Tedium Capsule": ItemClassification.progression,
    "Unlock: Thief": ItemClassification.progression,
    "Unlock: Three-Sided Die": ItemClassification.progression,
    "Unlock: Time Capsule": ItemClassification.progression,
    "Unlock: Toddler": ItemClassification.progression,
    "Unlock: Tomb": ItemClassification.progression,
    "Unlock: Treasure Chest": ItemClassification.progression,
    "Unlock: Turtle": ItemClassification.progression,
    "Unlock: Urn": ItemClassification.progression,
    "Unlock: Void Creature": ItemClassification.progression,
    "Unlock: Void Fruit": ItemClassification.progression,
    "Unlock: Void Stone": ItemClassification.progression,
    "Unlock: Watermelon": ItemClassification.progression,
    "Unlock: Wealthy Capsule": ItemClassification.progression,
    "Unlock: Wildcard": ItemClassification.progression,
    "Unlock: Wine": ItemClassification.progression,
    "Unlock: Witch": ItemClassification.progression,
    "Unlock: Wolf": ItemClassification.progression,
    "Unlock: 5th Ace": ItemClassification.progression,
    "Unlock: Adoption Papers": ItemClassification.progression,
    "Unlock: Ancient Lizard Blade": ItemClassification.progression,
    "Unlock: Anthropology Degree": ItemClassification.progression,
    "Unlock: Barrel of Dwarves": ItemClassification.progression,
    "Unlock: Big Symbol Bomb": ItemClassification.progression,
    "Unlock: Birdhouse": ItemClassification.progression,
    "Unlock: Black Cat": ItemClassification.progression,
    "Unlock: Black Pepper": ItemClassification.progression,
    "Unlock: Black Suits": ItemClassification.progression,
    "Unlock: Blue Pepper": ItemClassification.progression,
    "Unlock: Booster Pack": ItemClassification.progression,
    "Unlock: Bowling Ball": ItemClassification.progression,
    "Unlock: Brown Pepper": ItemClassification.progression,
    "Unlock: Capsule Machine": ItemClassification.progression,
    "Unlock: Cardboard Box": ItemClassification.progression,
    "Unlock: Checkered Flag": ItemClassification.progression,
    "Unlock: Chicken Coop": ItemClassification.progression,
    "Unlock: Chili Powder": ItemClassification.progression,
    "Unlock: Cleaning Rag": ItemClassification.progression,
    "Unlock: Clear Sky": ItemClassification.progression,
    "Unlock: Coffee": ItemClassification.progression,
    "Unlock: Coin on a String": ItemClassification.progression,
    "Unlock: Comfy Pillow": ItemClassification.progression,
    "Unlock: Compost Heap": ItemClassification.progression,
    "Unlock: Conveyor Belt": ItemClassification.progression,
    "Unlock: Copycat": ItemClassification.progression,
    "Unlock: Credit Card": ItemClassification.progression,
    "Unlock: Cursed Katana": ItemClassification.progression,
    "Unlock: Cyan Pepper": ItemClassification.progression,
    "Unlock: Dark Humor": ItemClassification.progression,
    "Unlock: Devil's Deal": ItemClassification.progression,
    "Unlock: Dishwasher": ItemClassification.progression,
    "Unlock: Dwarven Anvil": ItemClassification.progression,
    "Unlock: Egg Carton": ItemClassification.progression,
    "Unlock: Fertilizer": ItemClassification.progression,
    "Unlock: Fish Tank": ItemClassification.progression,
    "Unlock: Flush": ItemClassification.progression,
    "Unlock: Four-leaf clover": ItemClassification.progression,
    "Unlock: Frozen Pizza": ItemClassification.progression,
    "Unlock: Fruit Basket": ItemClassification.progression,
    "Unlock: Frying Pan": ItemClassification.progression,
    "Unlock: Golden Carrot": ItemClassification.progression,
    "Unlock: Goldilocks": ItemClassification.progression,
    "Unlock: Grave Robber": ItemClassification.progression,
    "Unlock: Gray Pepper": ItemClassification.progression,
    "Unlock: Green Pepper": ItemClassification.progression,
    "Unlock: Guillotine": ItemClassification.progression,
    "Unlock: Happy Hour": ItemClassification.progression,
    "Unlock: Holy Water": ItemClassification.progression,
    "Unlock: Horseshoe": ItemClassification.progression,
    "Unlock: Instant Ramen": ItemClassification.progression,
    "Unlock: Jack-o'-lantern": ItemClassification.progression,
    "Unlock: Kyle the Kernite": ItemClassification.progression,
    "Unlock: Lefty the Rabbit": ItemClassification.progression,
    "Unlock: Lemon": ItemClassification.progression,
    "Unlock: Lime Pepper": ItemClassification.progression,
    "Unlock: Lint Roller": ItemClassification.progression,
    "Unlock: Lockpick": ItemClassification.progression,
    "Unlock: Looting Glove": ItemClassification.progression,
    "Unlock: Lucky Carrot": ItemClassification.progression,
    "Unlock: Lucky Cat": ItemClassification.progression,
    "Unlock: Lucky Dice": ItemClassification.progression,
    "Unlock: Lucky Seven": ItemClassification.progression,
    "Unlock: Lunchbox": ItemClassification.progression,
    "Unlock: Maxwell the Bear": ItemClassification.progression,
    "Unlock: Mining Pick": ItemClassification.progression,
    "Unlock: Mobius Strip": ItemClassification.progression,
    "Unlock: Ninja and Mouse": ItemClassification.progression,
    "Unlock: Nori the Rabbit": ItemClassification.progression,
    "Unlock: Oil Can": ItemClassification.progression,
    "Unlock: Oswald the Monkey": ItemClassification.progression,
    "Unlock: Piggy Bank": ItemClassification.progression,
    "Unlock: Pink Pepper": ItemClassification.progression,
    "Unlock: Pizza the Cat": ItemClassification.progression,
    "Unlock: Pool Ball": ItemClassification.progression,
    "Unlock: Popsicle": ItemClassification.progression,
    "Unlock: Protractor": ItemClassification.progression,
    "Unlock: Purple Pepper": ItemClassification.progression,
    "Unlock: Quantum Symbol Bomb": ItemClassification.progression,
    "Unlock: Quigley the Wolf": ItemClassification.progression,
    "Unlock: Quiver": ItemClassification.progression,
    "Unlock: Rain Cloud": ItemClassification.progression,
    "Unlock: Recycling": ItemClassification.progression,
    "Unlock: Red Pepper": ItemClassification.progression,
    "Unlock: Red Suits": ItemClassification.progression,
    "Unlock: Reroll": ItemClassification.progression,
    "Unlock: Ricky the Banana": ItemClassification.progression,
    "Unlock: Ritual Candle": ItemClassification.progression,
    "Unlock: Rusty Gear": ItemClassification.progression,
    "Unlock: Shattered Mirror": ItemClassification.progression,
    "Unlock: Shedding Season": ItemClassification.progression,
    "Unlock: Shrine": ItemClassification.progression,
    "Unlock: Small Symbol Bomb": ItemClassification.progression,
    "Unlock: Sunglasses": ItemClassification.progression,
    "Unlock: Swapping Device": ItemClassification.progression,
    "Unlock: Swear Jar": ItemClassification.progression,
    "Unlock: Tax Evasion": ItemClassification.progression,
    "Unlock: Telescope": ItemClassification.progression,
    "Unlock: The Tortoise and the Hare": ItemClassification.progression,
    "Unlock: Time Machine": ItemClassification.progression,
    "Unlock: Treasure Map": ItemClassification.progression,
    "Unlock: Triple Coins": ItemClassification.progression,
    "Unlock: Undertaker": ItemClassification.progression,
    "Unlock: Very Big Symbol Bomb": ItemClassification.progression,
    "Unlock: Void Party": ItemClassification.progression,
    "Unlock: Void Portal": ItemClassification.progression,
    "Unlock: Wanted Poster": ItemClassification.progression,
    "Unlock: Watering Can": ItemClassification.progression,
    "Unlock: White Pepper": ItemClassification.progression,
    "Unlock: X-ray Machine": ItemClassification.progression,
    "Unlock: Yellow Pepper": ItemClassification.progression,
    "Unlock: Zaroff's Contract": ItemClassification.progression,
    "Unlock: 5th Ace Essence": ItemClassification.progression,
    "Unlock: Adoption Papers Essence": ItemClassification.progression,
    "Unlock: Ancient Lizard Blade Essence": ItemClassification.progression,
    "Unlock: Anthropology Degree Essence": ItemClassification.progression,
    "Unlock: Barrel of Dwarves Essence": ItemClassification.progression,
    "Unlock: Big Symbol Bomb Essence": ItemClassification.progression,
    "Unlock: Birdhouse Essence": ItemClassification.progression,
    "Unlock: Black Cat Essence": ItemClassification.progression,
    "Unlock: Black Pepper Essence": ItemClassification.progression,
    "Unlock: Black Suits Essence": ItemClassification.progression,
    "Unlock: Blue Pepper Essence": ItemClassification.progression,
    "Unlock: Booster Pack Essence": ItemClassification.progression,
    "Unlock: Bowling Ball Essence": ItemClassification.progression,
    "Unlock: Brown Pepper Essence": ItemClassification.progression,
    "Unlock: Capsule Machine Essence": ItemClassification.progression,
    "Unlock: Cardboard Box Essence": ItemClassification.progression,
    "Unlock: Checkered Flag Essence": ItemClassification.progression,
    "Unlock: Chicken Coop Essence": ItemClassification.progression,
    "Unlock: Chili Powder Essence": ItemClassification.progression,
    "Unlock: Cleaning Rag Essence": ItemClassification.progression,
    "Unlock: Clear Sky Essence": ItemClassification.progression,
    "Unlock: Coffee Essence": ItemClassification.progression,
    "Unlock: Coin on a String Essence": ItemClassification.progression,
    "Unlock: Comfy Pillow Essence": ItemClassification.progression,
    "Unlock: Compost Heap Essence": ItemClassification.progression,
    "Unlock: Conveyor Belt Essence": ItemClassification.progression,
    "Unlock: Copycat Essence": ItemClassification.progression,
    "Unlock: Credit Card Essence": ItemClassification.progression,
    "Unlock: Cursed Katana Essence": ItemClassification.progression,
    "Unlock: Cyan Pepper Essence": ItemClassification.progression,
    "Unlock: Dark Humor Essence": ItemClassification.progression,
    "Unlock: Devil's Deal Essence": ItemClassification.progression,
    "Unlock: Dishwasher Essence": ItemClassification.progression,
    "Unlock: Dwarven Anvil Essence": ItemClassification.progression,
    "Unlock: Egg Carton Essence": ItemClassification.progression,
    "Unlock: Fertilizer Essence": ItemClassification.progression,
    "Unlock: Fish Tank Essence": ItemClassification.progression,
    "Unlock: Flush Essence": ItemClassification.progression,
    "Unlock: Four-leaf clover Essence": ItemClassification.progression,
    "Unlock: Frozen Pizza Essence": ItemClassification.progression,
    "Unlock: Fruit Basket Essence": ItemClassification.progression,
    "Unlock: Frying Pan Essence": ItemClassification.progression,
    "Unlock: Golden Carrot Essence": ItemClassification.progression,
    "Unlock: Goldilocks Essence": ItemClassification.progression,
    "Unlock: Grave Robber Essence": ItemClassification.progression,
    "Unlock: Gray Pepper Essence": ItemClassification.progression,
    "Unlock: Green Pepper Essence": ItemClassification.progression,
    "Unlock: Guillotine Essence": ItemClassification.progression,
    "Unlock: Happy Hour Essence": ItemClassification.progression,
    "Unlock: Holy Water Essence": ItemClassification.progression,
    "Unlock: Horseshoe Essence": ItemClassification.progression,
    "Unlock: Instant Ramen Essence": ItemClassification.progression,
    "Unlock: Jack-o'-lantern Essence": ItemClassification.progression,
    "Unlock: Kyle the Kernite Essence": ItemClassification.progression,
    "Unlock: Lefty the Rabbit Essence": ItemClassification.progression,
    "Unlock: Lemon Essence": ItemClassification.progression,
    "Unlock: Lime Pepper Essence": ItemClassification.progression,
    "Unlock: Lint Roller Essence": ItemClassification.progression,
    "Unlock: Lockpick Essence": ItemClassification.progression,
    "Unlock: Looting Glove Essence": ItemClassification.progression,
    "Unlock: Lucky Carrot Essence": ItemClassification.progression,
    "Unlock: Lucky Cat Essence": ItemClassification.progression,
    "Unlock: Lucky Dice Essence": ItemClassification.progression,
    "Unlock: Lucky Seven Essence": ItemClassification.progression,
    "Unlock: Lunchbox Essence": ItemClassification.progression,
    "Unlock: Maxwell the Bear Essence": ItemClassification.progression,
    "Unlock: Mining Pick Essence": ItemClassification.progression,
    "Unlock: Mobius Strip Essence": ItemClassification.progression,
    "Unlock: Ninja and Mouse Essence": ItemClassification.progression,
    "Unlock: Nori the Rabbit Essence": ItemClassification.progression,
    "Unlock: Oil Can Essence": ItemClassification.progression,
    "Unlock: Oswald the Monkey Essence": ItemClassification.progression,
    "Unlock: Piggy Bank Essence": ItemClassification.progression,
    "Unlock: Pink Pepper Essence": ItemClassification.progression,
    "Unlock: Pizza the Cat Essence": ItemClassification.progression,
    "Unlock: Pool Ball Essence": ItemClassification.progression,
    "Unlock: Popsicle Essence": ItemClassification.progression,
    "Unlock: Protractor Essence": ItemClassification.progression,
    "Unlock: Purple Pepper Essence": ItemClassification.progression,
    "Unlock: Quantum Symbol Bomb Essence": ItemClassification.progression,
    "Unlock: Quigley the Wolf Essence": ItemClassification.progression,
    "Unlock: Quiver Essence": ItemClassification.progression,
    "Unlock: Rain Cloud Essence": ItemClassification.progression,
    "Unlock: Recycling Essence": ItemClassification.progression,
    "Unlock: Red Pepper Essence": ItemClassification.progression,
    "Unlock: Red Suits Essence": ItemClassification.progression,
    "Unlock: Reroll Essence": ItemClassification.progression,
    "Unlock: Ricky the Banana Essence": ItemClassification.progression,
    "Unlock: Ritual Candle Essence": ItemClassification.progression,
    "Unlock: Rusty Gear Essence": ItemClassification.progression,
    "Unlock: Shattered Mirror Essence": ItemClassification.progression,
    "Unlock: Shedding Season Essence": ItemClassification.progression,
    "Unlock: Shrine Essence": ItemClassification.progression,
    "Unlock: Small Symbol Bomb Essence": ItemClassification.progression,
    "Unlock: Sunglasses Essence": ItemClassification.progression,
    "Unlock: Swapping Device Essence": ItemClassification.progression,
    "Unlock: Swear Jar Essence": ItemClassification.progression,
    "Unlock: Tax Evasion Essence": ItemClassification.progression,
    "Unlock: Telescope Essence": ItemClassification.progression,
    "Unlock: The Tortoise and the Hare Essence": ItemClassification.progression,
    "Unlock: Time Machine Essence": ItemClassification.progression,
    "Unlock: Treasure Map Essence": ItemClassification.progression,
    "Unlock: Triple Coins Essence": ItemClassification.progression,
    "Unlock: Undertaker Essence": ItemClassification.progression,
    "Unlock: Very Big Symbol Bomb Essence": ItemClassification.progression,
    "Unlock: Void Party Essence": ItemClassification.progression,
    "Unlock: Void Portal Essence": ItemClassification.progression,
    "Unlock: Wanted Poster Essence": ItemClassification.progression,
    "Unlock: Watering Can Essence": ItemClassification.progression,
    "Unlock: White Pepper Essence": ItemClassification.progression,
    "Unlock: X-ray Machine Essence": ItemClassification.progression,
    "Unlock: Yellow Pepper Essence": ItemClassification.progression,
    "Unlock: Zaroff's Contract Essence": ItemClassification.progression,

}



LOCAL_FILLER_BUFF_TRAP_ITEMS = {
    # Normal filler
    "Progressive Nothing",
    "Too Tiny to Resemble Something",
    "A Really Really Small Coin",

    # Buffs
    "Starting Symbol",
    "$5 Starting Money",
    "Removal Token",
    "Reroll Token",
    "Essence Token",

    # Traps
    "Half Money",
    "Force Payment",
    "Dud Symbol",
}

# Each Item instance must correctly report the "game" it belongs to.
# To make this simple, it is common practice to subclass the basic Item class and override the "game" field.
class LBALItem(Item):
    game = "Luck be a Landlord"



# Ontop of our regular itempool, our world must be able to create arbitrary amounts of filler as requested by core.
# To do this, it must define a function called world.get_filler_item_name(), which we will define in world.py later.
# For now, let's make a function that returns the name of a random filler item here in items.py.
def get_random_filler_item_name(world: LBALWorld) -> str:

    # -------------------------
    # Enabled traps
    # -------------------------
    traps = []

    if world.options.Forcepayment:
        traps.append("Force Payment")

    if world.options.Dud:
        traps.append("Dud Symbol")

    if world.options.HalfMoney:
        traps.append("Half Money")


    # -------------------------
    # Enabled buffs
    # -------------------------
    buffs = []

    if world.options.SymbolBomb:
        buffs.append("Starting Symbol")

    if world.options.StartMoney:
        buffs.append("$5 Starting Money")

    if world.options.RemovalToken:
        buffs.append("Removal Token")

    if world.options.RerollToken:
        buffs.append("Reroll Token")

    if world.options.EssenceToken:
        buffs.append("Essence Token")


    trap_chance = world.options.TrapChance.value
    buff_chance = world.options.BuffChance.value


    # One roll from 1-100
    roll = world.random.randint(1, 100)


    # -------------------------
    # Trap
    # -------------------------
    if traps and roll <= trap_chance:
        return world.random.choice(traps)


    # -------------------------
    # Buff
    # -------------------------
    if buffs and roll <= trap_chance + buff_chance:
        return world.random.choice(buffs)


    # -------------------------
    # Normal filler
    # -------------------------
    normal_filler = [
        "Progressive Nothing",
        "Too Tiny to Resemble Something",
        "A Really Really Small Coin",
    ]

    return world.random.choice(normal_filler)


def create_item_with_correct_classification(world: LBALWorld, name: str) -> LBALItem:
    # Our world class must have a create_item() function that can create any of our items by name at any time.
    # So, we make this helper function that creates the item by name with the correct classification.
    # Note: This function's content could just be the contents of world.create_item in world.py directly,
    # but it seemed nicer to have it in its own function over here in items.py.
    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]

    # It is perfectly normal and valid for an item's classification to differ based on the player's options.
    # In our case, Health Upgrades are only relevant to logic (and thus labeled as "progression") in hard mode.
    #if name == "Health Upgrade" and world.options.hard_mode:
        #classification = ItemClassification.progression

    return LBALItem(name, classification, ITEM_NAME_TO_ID[name], world.player)


# With those two helper functions defined, let's now get to actually creating and submitting our itempool.
def create_all_items(world: LBALWorld) -> None:
    # This is the function in which we will create all the items that this world submits to the multiworld item pool.
    # There must be exactly as many items as there are locations.
    # In our case, there are either six or seven locations.
    # We must make sure that when there are six locations, there are six items,
    # and when there are seven locations, there are seven items.

    # Creating items should generally be done via the world's create_item method.
    # First, we create a list containing all the items that always exist.

    itempool: list[Item] = [
        world.create_item("Unlock: Anchor"),
        world.create_item("Unlock: Banana"),
        world.create_item("Unlock: Banana Peel"),
        world.create_item("Unlock: Bar of Soap"),
        world.create_item("Unlock: Bear"),
        world.create_item("Unlock: Bee"),
        world.create_item("Unlock: Beer"),
        world.create_item("Unlock: Big Ore"),
        world.create_item("Unlock: Big Urn"),
        world.create_item("Unlock: Billionaire"),
        world.create_item("Unlock: Bounty Hunter"),
        world.create_item("Unlock: Bronze Arrow"),
        world.create_item("Unlock: Bubble"),
        world.create_item("Unlock: Buffing Capsule"),
        world.create_item("Unlock: Candy"),
        world.create_item("Unlock: Cat"),
        world.create_item("Unlock: Cheese"),
        world.create_item("Unlock: Chemical Seven"),
        world.create_item("Unlock: Cherry"),
        world.create_item("Unlock: Chick"),
        world.create_item("Unlock: Clubs"),
        world.create_item("Unlock: Coal"),
        world.create_item("Unlock: Coconut"),
        world.create_item("Unlock: Coconut Half"),
        world.create_item("Unlock: Coin"),
        world.create_item("Unlock: Crab"),
        world.create_item("Unlock: Crow"),
        world.create_item("Unlock: Cultist"),
        world.create_item("Unlock: Diamonds"),
        world.create_item("Unlock: Dog"),
        world.create_item("Unlock: Dwarf"),
        world.create_item("Unlock: Egg"),
        world.create_item("Unlock: Essence Capsule"),
        world.create_item("Unlock: Five-Sided Die"),
        world.create_item("Unlock: Flower"),
        world.create_item("Unlock: Gambler"),
        world.create_item("Unlock: Goldfish"),
        world.create_item("Unlock: Golem"),
        world.create_item("Unlock: Goose"),
        world.create_item("Unlock: Hearts"),
        world.create_item("Unlock: Hex of Destruction"),
        world.create_item("Unlock: Hex of Draining"),
        world.create_item("Unlock: Hex of Emptiness"),
        world.create_item("Unlock: Hex of Hoarding"),
        world.create_item("Unlock: Hex of Midas"),
        world.create_item("Unlock: Hex of Tedium"),
        world.create_item("Unlock: Hex of Thievery"),
        world.create_item("Unlock: Hooligan"),
        world.create_item("Unlock: Hustling Capsule"),
        world.create_item("Unlock: Item Capsule"),
        world.create_item("Unlock: Jellyfish"),
        world.create_item("Unlock: Key"),
        world.create_item("Unlock: Light Bulb"),
        world.create_item("Unlock: Lockbox"),
        world.create_item("Unlock: Lucky Capsule"),
        world.create_item("Unlock: Magpie"),
        world.create_item("Unlock: Matryoshka Doll"),
        world.create_item("Unlock: Milk"),
        world.create_item("Unlock: Miner"),
        world.create_item("Unlock: Monkey"),
        world.create_item("Unlock: Mouse"),
        world.create_item("Unlock: Ninja"),
        world.create_item("Unlock: Orange"),
        world.create_item("Unlock: Ore"),
        world.create_item("Unlock: Owl"),
        world.create_item("Unlock: Oyster"),
        world.create_item("Unlock: Peach"),
        world.create_item("Unlock: Pearl"),
        world.create_item("Unlock: Pinata"),
        world.create_item("Unlock: Present"),
        world.create_item("Unlock: Pufferfish"),
        world.create_item("Unlock: Rabbit"),
        world.create_item("Unlock: Rabbit Fluff"),
        world.create_item("Unlock: Rain"),
        world.create_item("Unlock: Removal Capsule"),
        world.create_item("Unlock: Reroll Capsule"),
        world.create_item("Unlock: Safe"),
        world.create_item("Unlock: Sand Dollar"),
        world.create_item("Unlock: Sapphire"),
        world.create_item("Unlock: Seed"),
        world.create_item("Unlock: Shiny Pebble"),
        world.create_item("Unlock: Sloth"),
        world.create_item("Unlock: Snail"),
        world.create_item("Unlock: Spades"),
        world.create_item("Unlock: Target"),
        world.create_item("Unlock: Tedium Capsule"),
        world.create_item("Unlock: Thief"),
        world.create_item("Unlock: Three-Sided Die"),
        world.create_item("Unlock: Time Capsule"),
        world.create_item("Unlock: Toddler"),
        world.create_item("Unlock: Turtle"),
        world.create_item("Unlock: Urn"),
        world.create_item("Unlock: Void Creature"),
        world.create_item("Unlock: Void Fruit"),
        world.create_item("Unlock: Void Stone"),
        world.create_item("Unlock: Wealthy Capsule"),
        world.create_item("Unlock: Wine"),
        world.create_item("Unlock: Wolf"),


        world.create_item("Unlock: 5th Ace"),
        world.create_item("Unlock: 5th Ace Essence"),
        world.create_item("Unlock: Adoption Papers"),
        world.create_item("Unlock: Adoption Papers Essence"),
        world.create_item("Unlock: Barrel of Dwarves"),
        world.create_item("Unlock: Barrel of Dwarves Essence"),
        world.create_item("Unlock: Big Symbol Bomb"),
        world.create_item("Unlock: Big Symbol Bomb Essence"),
        world.create_item("Unlock: Birdhouse"),
        world.create_item("Unlock: Birdhouse Essence"),
        world.create_item("Unlock: Black Cat"),
        world.create_item("Unlock: Black Cat Essence"),
        world.create_item("Unlock: Black Pepper"),
        world.create_item("Unlock: Black Pepper Essence"),
        world.create_item("Unlock: Black Suits"),
        world.create_item("Unlock: Black Suits Essence"),
        world.create_item("Unlock: Blue Pepper"),
        world.create_item("Unlock: Blue Pepper Essence"),
        world.create_item("Unlock: Brown Pepper"),
        world.create_item("Unlock: Brown Pepper Essence"),
        world.create_item("Unlock: Cardboard Box"),
        world.create_item("Unlock: Cardboard Box Essence"),
        world.create_item("Unlock: Checkered Flag"),
        world.create_item("Unlock: Checkered Flag Essence"),
        world.create_item("Unlock: Cleaning Rag"),
        world.create_item("Unlock: Cleaning Rag Essence"),
        world.create_item("Unlock: Coin on a String"),
        world.create_item("Unlock: Coin on a String Essence"),
        world.create_item("Unlock: Comfy Pillow"),
        world.create_item("Unlock: Comfy Pillow Essence"),
        world.create_item("Unlock: Compost Heap"),
        world.create_item("Unlock: Compost Heap Essence"),
        world.create_item("Unlock: Conveyor Belt"),
        world.create_item("Unlock: Conveyor Belt Essence"),
        world.create_item("Unlock: Cursed Katana"),
        world.create_item("Unlock: Cursed Katana Essence"),
        world.create_item("Unlock: Cyan Pepper"),
        world.create_item("Unlock: Cyan Pepper Essence"),
        world.create_item("Unlock: Dark Humor"),
        world.create_item("Unlock: Dark Humor Essence"),
        world.create_item("Unlock: Dwarven Anvil"),
        world.create_item("Unlock: Dwarven Anvil Essence"),
        world.create_item("Unlock: Egg Carton"),
        world.create_item("Unlock: Egg Carton Essence"),
        world.create_item("Unlock: Fertilizer"),
        world.create_item("Unlock: Fertilizer Essence"),
        world.create_item("Unlock: Fish Tank"),
        world.create_item("Unlock: Fish Tank Essence"),
        world.create_item("Unlock: Flush"),
        world.create_item("Unlock: Flush Essence"),
        world.create_item("Unlock: Fruit Basket"),
        world.create_item("Unlock: Fruit Basket Essence"),
        world.create_item("Unlock: Frying Pan"),
        world.create_item("Unlock: Frying Pan Essence"),
        world.create_item("Unlock: Goldilocks"),
        world.create_item("Unlock: Goldilocks Essence"),
        world.create_item("Unlock: Grave Robber"),
        world.create_item("Unlock: Grave Robber Essence"),
        world.create_item("Unlock: Gray Pepper"),
        world.create_item("Unlock: Gray Pepper Essence"),
        world.create_item("Unlock: Green Pepper"),
        world.create_item("Unlock: Green Pepper Essence"),
        world.create_item("Unlock: Guillotine"),
        world.create_item("Unlock: Guillotine Essence"),
        world.create_item("Unlock: Happy Hour"),
        world.create_item("Unlock: Happy Hour Essence"),
        world.create_item("Unlock: Horseshoe"),
        world.create_item("Unlock: Horseshoe Essence"),
        world.create_item("Unlock: Jack-o'-lantern"),
        world.create_item("Unlock: Jack-o'-lantern Essence"),
        world.create_item("Unlock: Kyle the Kernite"),
        world.create_item("Unlock: Kyle the Kernite Essence"),
        world.create_item("Unlock: Lefty the Rabbit"),
        world.create_item("Unlock: Lefty the Rabbit Essence"),
        world.create_item("Unlock: Lemon"),
        world.create_item("Unlock: Lemon Essence"),
        world.create_item("Unlock: Lime Pepper"),
        world.create_item("Unlock: Lime Pepper Essence"),
        world.create_item("Unlock: Lint Roller"),
        world.create_item("Unlock: Lint Roller Essence"),
        world.create_item("Unlock: Lockpick"),
        world.create_item("Unlock: Lockpick Essence"),
        world.create_item("Unlock: Looting Glove"),
        world.create_item("Unlock: Looting Glove Essence"),
        world.create_item("Unlock: Lucky Cat"),
        world.create_item("Unlock: Lucky Cat Essence"),
        world.create_item("Unlock: Lucky Seven"),
        world.create_item("Unlock: Lucky Seven Essence"),
        world.create_item("Unlock: Lunchbox"),
        world.create_item("Unlock: Lunchbox Essence"),
        world.create_item("Unlock: Maxwell the Bear"),
        world.create_item("Unlock: Maxwell the Bear Essence"),
        world.create_item("Unlock: Mining Pick"),
        world.create_item("Unlock: Mining Pick Essence"),
        world.create_item("Unlock: Ninja and Mouse"),
        world.create_item("Unlock: Ninja and Mouse Essence"),
        world.create_item("Unlock: Nori the Rabbit"),
        world.create_item("Unlock: Nori the Rabbit Essence"),
        world.create_item("Unlock: Oswald the Monkey"),
        world.create_item("Unlock: Oswald the Monkey Essence"),
        world.create_item("Unlock: Piggy Bank"),
        world.create_item("Unlock: Piggy Bank Essence"),
        world.create_item("Unlock: Pink Pepper"),
        world.create_item("Unlock: Pink Pepper Essence"),
        world.create_item("Unlock: Pizza the Cat"),
        world.create_item("Unlock: Pizza the Cat Essence"),
        world.create_item("Unlock: Pool Ball"),
        world.create_item("Unlock: Pool Ball Essence"),
        world.create_item("Unlock: Purple Pepper"),
        world.create_item("Unlock: Purple Pepper Essence"),
        world.create_item("Unlock: Quantum Symbol Bomb"),
        world.create_item("Unlock: Quantum Symbol Bomb Essence"),
        world.create_item("Unlock: Quigley the Wolf"),
        world.create_item("Unlock: Quigley the Wolf Essence"),
        world.create_item("Unlock: Rain Cloud"),
        world.create_item("Unlock: Rain Cloud Essence"),
        world.create_item("Unlock: Red Pepper"),
        world.create_item("Unlock: Red Pepper Essence"),
        world.create_item("Unlock: Red Suits"),
        world.create_item("Unlock: Red Suits Essence"),
        world.create_item("Unlock: Reroll"),
        world.create_item("Unlock: Reroll Essence"),
        world.create_item("Unlock: Ricky the Banana"),
        world.create_item("Unlock: Ricky the Banana Essence"),
        world.create_item("Unlock: Ritual Candle"),
        world.create_item("Unlock: Ritual Candle Essence"),
        world.create_item("Unlock: Rusty Gear"),
        world.create_item("Unlock: Rusty Gear Essence"),
        world.create_item("Unlock: Shattered Mirror"),
        world.create_item("Unlock: Shattered Mirror Essence"),
        world.create_item("Unlock: Shedding Season"),
        world.create_item("Unlock: Shedding Season Essence"),
        world.create_item("Unlock: Shrine"),
        world.create_item("Unlock: Shrine Essence"),
        world.create_item("Unlock: Small Symbol Bomb"),
        world.create_item("Unlock: Small Symbol Bomb Essence"),
        world.create_item("Unlock: Swear Jar"),
        world.create_item("Unlock: Swear Jar Essence"),
        world.create_item("Unlock: Tax Evasion"),
        world.create_item("Unlock: Tax Evasion Essence"),
        world.create_item("Unlock: The Tortoise and the Hare"),
        world.create_item("Unlock: The Tortoise and the Hare Essence"),
        world.create_item("Unlock: Time Machine"),
        world.create_item("Unlock: Time Machine Essence"),
        world.create_item("Unlock: Treasure Map"),
        world.create_item("Unlock: Treasure Map Essence"),
        world.create_item("Unlock: Triple Coins"),
        world.create_item("Unlock: Triple Coins Essence"),
        world.create_item("Unlock: Wanted Poster"),
        world.create_item("Unlock: Wanted Poster Essence"),
        world.create_item("Unlock: Watering Can"),
        world.create_item("Unlock: Watering Can Essence"),
        world.create_item("Unlock: White Pepper"),
        world.create_item("Unlock: White Pepper Essence"),
        world.create_item("Unlock: X-ray Machine"),
        world.create_item("Unlock: X-ray Machine Essence"),
        world.create_item("Unlock: Yellow Pepper"),
        world.create_item("Unlock: Yellow Pepper Essence"),
        world.create_item("Unlock: Zaroff's Contract"),
        world.create_item("Unlock: Zaroff's Contract Essence"),


    ]
    shiny_coin_count = world.options.HowmanyShinyCoins.value
    extra_coin_count = world.options.ExtraShinyCoins.value

    for _ in range(shiny_coin_count + extra_coin_count):
        itempool.append(world.create_item("Shiny Coin"))

    # Some items may only exist if the player enables certain options.
    # In our case, If the hammer option is enabled, the sixth item is the Hammer.
    # Otherwise, we add a filler Confetti Cannon.
    #if world.options.hammer:
        # Once again, it is important to stress that even though the Hammer doesn't always exist,
        # it must be present in the worlds item_name_to_id.
        # Whether it is actually in the itempool is determined purely by whether we create and add the item here.
        #itempool.append(world.create_item("Hammer"))

    if "2" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 2 Unlock"))
    
    if "3" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 3 Unlock"))
        
    if "4" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 4 Unlock"))

    if "5" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 5 Unlock"))

    if "6" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 6 Unlock"))

    if "7" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 7 Unlock"))
    
    if "8" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 8 Unlock"))
        
    if "9" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 9 Unlock"))

    if "10" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 10 Unlock"))

    if "11" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 11 Unlock"))

    if "12" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 12 Unlock"))
    
    if "13" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 13 Unlock"))
        
    if "14" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 14 Unlock"))

    if "15" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 15 Unlock"))

    if "16" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 16 Unlock"))

    if "17" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 17 Unlock"))

    if "18" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 18 Unlock"))
        
    if "19" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 19 Unlock"))

    if "20" in world.options.Floors.value:

        itempool.append(world.create_item("Floor 20 Unlock"))

    if world.options.Rare:

        itempool.append(world.create_item("Unlock: Amethyst")),
        itempool.append(world.create_item("Unlock: Apple")),
        itempool.append(world.create_item("Unlock: Bartender")),
        itempool.append(world.create_item("Unlock: Beastmaster")),
        itempool.append(world.create_item("Unlock: Beehive")),
        itempool.append(world.create_item("Unlock: Card Shark")),
        itempool.append(world.create_item("Unlock: Chef")),
        itempool.append(world.create_item("Unlock: Chicken")),
        itempool.append(world.create_item("Unlock: Comedian")),
        itempool.append(world.create_item("Unlock: Cow")),
        itempool.append(world.create_item("Unlock: Dame")),
        itempool.append(world.create_item("Unlock: Diver")),
        itempool.append(world.create_item("Unlock: Dove")),
        itempool.append(world.create_item("Unlock: Emerald")),
        itempool.append(world.create_item("Unlock: Farmer")),
        itempool.append(world.create_item("Unlock: Frozen Fossil")),
        itempool.append(world.create_item("Unlock: General Zaroff")),
        itempool.append(world.create_item("Unlock: Geologist")),
        itempool.append(world.create_item("Unlock: Golden Egg")),
        itempool.append(world.create_item("Unlock: Honey")),
        itempool.append(world.create_item("Unlock: Joker")),
        itempool.append(world.create_item("Unlock: King Midas")),
        itempool.append(world.create_item("Unlock: Magic Key")),
        itempool.append(world.create_item("Unlock: Martini")),
        itempool.append(world.create_item("Unlock: Mine")),
        itempool.append(world.create_item("Unlock: Moon")),
        itempool.append(world.create_item("Unlock: Mrs. Fruit")),
        itempool.append(world.create_item("Unlock: Omelette")),
        itempool.append(world.create_item("Unlock: Pear")),
        itempool.append(world.create_item("Unlock: Robin Hood")),
        itempool.append(world.create_item("Unlock: Ruby")),
        itempool.append(world.create_item("Unlock: Silver Arrow")),
        itempool.append(world.create_item("Unlock: Spirit")),
        itempool.append(world.create_item("Unlock: Strawberry")),
        itempool.append(world.create_item("Unlock: Sun")),
        itempool.append(world.create_item("Unlock: Tomb")),
        itempool.append(world.create_item("Unlock: Treasure Chest")),
        itempool.append(world.create_item("Unlock: Witch")),
        itempool.append(world.create_item("Unlock: Anthropology Degree")),
        itempool.append(world.create_item("Unlock: Anthropology Degree Essence")),
        itempool.append(world.create_item("Unlock: Booster Pack")),
        itempool.append(world.create_item("Unlock: Booster Pack Essence")),
        itempool.append(world.create_item("Unlock: Bowling Ball")),
        itempool.append(world.create_item("Unlock: Bowling Ball Essence")),
        itempool.append(world.create_item("Unlock: Capsule Machine")),
        itempool.append(world.create_item("Unlock: Capsule Machine Essence")),
        itempool.append(world.create_item("Unlock: Chicken Coop")),
        itempool.append(world.create_item("Unlock: Chicken Coop Essence")),
        itempool.append(world.create_item("Unlock: Chili Powder")),
        itempool.append(world.create_item("Unlock: Chili Powder Essence")),
        itempool.append(world.create_item("Unlock: Clear Sky")),
        itempool.append(world.create_item("Unlock: Clear Sky Essence")),
        itempool.append(world.create_item("Unlock: Coffee")),
        itempool.append(world.create_item("Unlock: Coffee Essence")),
        itempool.append(world.create_item("Unlock: Devil's Deal")),
        itempool.append(world.create_item("Unlock: Devil's Deal Essence")),
        itempool.append(world.create_item("Unlock: Dishwasher")),
        itempool.append(world.create_item("Unlock: Dishwasher Essence")),
        itempool.append(world.create_item("Unlock: Holy Water")),
        itempool.append(world.create_item("Unlock: Holy Water Essence")),
        itempool.append(world.create_item("Unlock: Instant Ramen")),
        itempool.append(world.create_item("Unlock: Instant Ramen Essence")),
        itempool.append(world.create_item("Unlock: Lucky Carrot")),
        itempool.append(world.create_item("Unlock: Lucky Carrot Essence")),
        itempool.append(world.create_item("Unlock: Lucky Dice")),
        itempool.append(world.create_item("Unlock: Lucky Dice Essence")),
        itempool.append(world.create_item("Unlock: Oil Can")),
        itempool.append(world.create_item("Unlock: Oil Can Essence")),
        itempool.append(world.create_item("Unlock: Protractor")),
        itempool.append(world.create_item("Unlock: Protractor Essence")),
        itempool.append(world.create_item("Unlock: Quiver")),
        itempool.append(world.create_item("Unlock: Quiver Essence")),
        itempool.append(world.create_item("Unlock: Sunglasses")),
        itempool.append(world.create_item("Unlock: Sunglasses Essence")),
        itempool.append(world.create_item("Unlock: Swapping Device")),
        itempool.append(world.create_item("Unlock: Swapping Device Essence")),
        itempool.append(world.create_item("Unlock: Undertaker")),
        itempool.append(world.create_item("Unlock: Undertaker Essence")),
        itempool.append(world.create_item("Unlock: Very Big Symbol Bomb")),
        itempool.append(world.create_item("Unlock: Very Big Symbol Bomb Essence")),
        itempool.append(world.create_item("Unlock: Void Party")),
        itempool.append(world.create_item("Unlock: Void Party Essence")),
        itempool.append(world.create_item("Unlock: Void Portal")),
        itempool.append(world.create_item("Unlock: Void Portal Essence")),

    if world.options.VeryRare:
        itempool.append(world.create_item("Unlock: Diamond")),
        itempool.append(world.create_item("Unlock: Eldritch Creature")),
        itempool.append(world.create_item("Unlock: Golden Arrow")),
        itempool.append(world.create_item("Unlock: Highlander")),
        itempool.append(world.create_item("Unlock: Mega Chest")),
        itempool.append(world.create_item("Unlock: Midas Bomb")),
        itempool.append(world.create_item("Unlock: Pirate")),
        itempool.append(world.create_item("Unlock: Watermelon")),
        itempool.append(world.create_item("Unlock: Wildcard")),
        itempool.append(world.create_item("Unlock: Ancient Lizard Blade")),
        itempool.append(world.create_item("Unlock: Ancient Lizard Blade Essence")),
        itempool.append(world.create_item("Unlock: Copycat")),
        itempool.append(world.create_item("Unlock: Copycat Essence")),
        itempool.append(world.create_item("Unlock: Credit Card")),
        itempool.append(world.create_item("Unlock: Credit Card Essence")),
        itempool.append(world.create_item("Unlock: Four-leaf clover")),
        itempool.append(world.create_item("Unlock: Four-leaf clover Essence")),
        itempool.append(world.create_item("Unlock: Frozen Pizza")),
        itempool.append(world.create_item("Unlock: Frozen Pizza Essence")),
        itempool.append(world.create_item("Unlock: Golden Carrot")),
        itempool.append(world.create_item("Unlock: Golden Carrot Essence")),
        itempool.append(world.create_item("Unlock: Mobius Strip")),
        itempool.append(world.create_item("Unlock: Mobius Strip Essence")),
        itempool.append(world.create_item("Unlock: Popsicle")),
        itempool.append(world.create_item("Unlock: Popsicle Essence")),
        itempool.append(world.create_item("Unlock: Recycling")),
        itempool.append(world.create_item("Unlock: Recycling Essence")),
        itempool.append(world.create_item("Unlock: Telescope")),
        itempool.append(world.create_item("Unlock: Telescope Essence")),


    # Archipelago requires that each world submits as many locations as it submits items.
    # This is where we can use our filler and trap items.
    # APQuest has two of these: The Confetti Cannon and the Math Trap.
    # (Unfortunately, Archipelago is a bit ambiguous about its terminology here:
    #  "filler" is an ItemClassification separate from "trap", but in a lot of its functions,
    #  Archipelago will use "filler" to just mean "an additional item created to fill out the itempool".
    #  "Filler" in this sense can technically have any ItemClassification,
    #  but most commonly ItemClassification.filler or ItemClassification.trap.
    #  Starting here, the word "filler" will be used to collectively refer to APQuest's Confetti Cannon and Math Trap,
    #  which are ItemClassification.filler and ItemClassification.trap respectively.)
    # Creating filler items works the same as any other item. But there is a question:
    # How many filler items do we actually need to create?
    # In regions.py, we created either six or seven locations depending on the "extra_starting_chest" option.
    # In this function, we have created five or six items depending on whether the "hammer" option is enabled.
    # We *could* have a really complicated if-else tree checking the options again, but there is a better way.
    # We can compare the size of our itempool so far to the number of locations in our world.

    # The length of our itempool is easy to determine, since we have it as a list.
    number_of_items = len(itempool)

    number_of_unfilled_locations = len(
        world.multiworld.get_unfilled_locations(world.player)
    )

    needed_number_of_filler_items = (
        number_of_unfilled_locations - number_of_items
    )

    if needed_number_of_filler_items < 0:
        raise Exception(
            f"LBAL ITEMPOOL OVERFLOW: "
            f"{number_of_items} items for "
            f"{number_of_unfilled_locations} locations "
            f"({-needed_number_of_filler_items} too many)"
        )

    # --------------------------------------------------
    # Fast floor-mode filler placement
    # --------------------------------------------------

    remaining_filler_count = needed_number_of_filler_items

    if (
        world.options.FloorDependentChecks
        and needed_number_of_filler_items > 0
    ):
        # 90% of all generated filler/buff/trap copies
        # are placed directly into this LBAL player's world.
        local_filler_count = (
            needed_number_of_filler_items * 90
        ) // 100

        local_locations = list(
            world.multiworld.get_unfilled_locations(
                world.player
            )
        )

        world.random.shuffle(local_locations)

        if len(local_locations) < local_filler_count:
            raise Exception(
                "LBAL LOCAL FILL ERROR: "
                f"Need {local_filler_count} local locations, "
                f"but only have {len(local_locations)}."
            )

        for _ in range(local_filler_count):

            filler_item = world.create_filler()

            location = local_locations.pop()

            location.place_locked_item(
                filler_item
            )

        remaining_filler_count -= (
            local_filler_count
        )


    # The remaining 10% goes through normal AP fill.
    itempool += [
        world.create_filler()
        for _ in range(remaining_filler_count)
    ]

    world.multiworld.itempool += itempool