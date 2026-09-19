from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location

from . import items
import re

if TYPE_CHECKING:
    from .world import LBALWorld

# Every location must have a unique integer ID associated with it.
# We will have a lookup from location name to ID here that, in world.py, we will import and bind to the world class.
# Even if a location doesn't exist on specific options, it must be present in this lookup.
LOCATION_NAME_TO_ID = {
    "Floor 1 Payment 1": 1,
    "Floor 1 Payment 2": 2,
    "Floor 1 Payment 3": 3,
    "Floor 1 Payment 4": 4,
    "Floor 1 Payment 5": 5,
    "Floor 1 Payment 6": 6,
    "Floor 1 Payment 7": 7,
    "Floor 1 Payment 8": 8,
    "Floor 1 Payment 9": 9,
    "Floor 1 Payment 10": 10,
    "Floor 1 Payment 11": 11,
    "Floor 1 Payment 12": 12,
    "Floor 2 Payment 1": 13,
    "Floor 2 Payment 2": 14,
    "Floor 2 Payment 3": 15,
    "Floor 2 Payment 4": 16,
    "Floor 2 Payment 5": 17,
    "Floor 2 Payment 6": 18,
    "Floor 2 Payment 7": 19,
    "Floor 2 Payment 8": 20,
    "Floor 2 Payment 9": 21,
    "Floor 2 Payment 10": 22,
    "Floor 2 Payment 11": 23,
    "Floor 2 Payment 12": 24,
    "Floor 3 Payment 1": 25,
    "Floor 3 Payment 2": 26,
    "Floor 3 Payment 3": 27,
    "Floor 3 Payment 4": 28,
    "Floor 3 Payment 5": 29,
    "Floor 3 Payment 6": 30,
    "Floor 3 Payment 7": 31,
    "Floor 3 Payment 8": 32,
    "Floor 3 Payment 9": 33,
    "Floor 3 Payment 10": 34,
    "Floor 3 Payment 11": 35,
    "Floor 3 Payment 12": 36,
    "Floor 4 Payment 1": 37,
    "Floor 4 Payment 2": 38,
    "Floor 4 Payment 3": 39,
    "Floor 4 Payment 4": 40,
    "Floor 4 Payment 5": 41,
    "Floor 4 Payment 6": 42,
    "Floor 4 Payment 7": 43,
    "Floor 4 Payment 8": 44,
    "Floor 4 Payment 9": 45,
    "Floor 4 Payment 10": 46,
    "Floor 4 Payment 11": 47,
    "Floor 4 Payment 12": 48,
    "Floor 5 Payment 1": 49,
    "Floor 5 Payment 2": 50,
    "Floor 5 Payment 3": 51,
    "Floor 5 Payment 4": 52,
    "Floor 5 Payment 5": 53,
    "Floor 5 Payment 6": 54,
    "Floor 5 Payment 7": 55,
    "Floor 5 Payment 8": 56,
    "Floor 5 Payment 9": 57,
    "Floor 5 Payment 10": 58,
    "Floor 5 Payment 11": 59,
    "Floor 5 Payment 12": 60,
    "Floor 6 Payment 1": 61,
    "Floor 6 Payment 2": 62,
    "Floor 6 Payment 3": 63,
    "Floor 6 Payment 4": 64,
    "Floor 6 Payment 5": 65,
    "Floor 6 Payment 6": 66,
    "Floor 6 Payment 7": 67,
    "Floor 6 Payment 8": 68,
    "Floor 6 Payment 9": 69,
    "Floor 6 Payment 10": 70,
    "Floor 6 Payment 11": 71,
    "Floor 6 Payment 12": 72,
    "Floor 7 Payment 1": 73,
    "Floor 7 Payment 2": 74,
    "Floor 7 Payment 3": 75,
    "Floor 7 Payment 4": 76,
    "Floor 7 Payment 5": 77,
    "Floor 7 Payment 6": 78,
    "Floor 7 Payment 7": 79,
    "Floor 7 Payment 8": 80,
    "Floor 7 Payment 9": 81,
    "Floor 7 Payment 10": 82,
    "Floor 7 Payment 11": 83,
    "Floor 7 Payment 12": 84,
    "Floor 8 Payment 1": 85,
    "Floor 8 Payment 2": 86,
    "Floor 8 Payment 3": 87,
    "Floor 8 Payment 4": 88,
    "Floor 8 Payment 5": 89,
    "Floor 8 Payment 6": 90,
    "Floor 8 Payment 7": 91,
    "Floor 8 Payment 8": 92,
    "Floor 8 Payment 9": 93,
    "Floor 8 Payment 10": 94,
    "Floor 8 Payment 11": 95,
    "Floor 8 Payment 12": 96,
    "Floor 9 Payment 1": 97,
    "Floor 9 Payment 2": 98,
    "Floor 9 Payment 3": 99,
    "Floor 9 Payment 4": 100,
    "Floor 9 Payment 5": 101,
    "Floor 9 Payment 6": 102,
    "Floor 9 Payment 7": 103,
    "Floor 9 Payment 8": 104,
    "Floor 9 Payment 9": 105,
    "Floor 9 Payment 10": 106,
    "Floor 9 Payment 11": 107,
    "Floor 9 Payment 12": 108,
    "Floor 10 Payment 1": 109,
    "Floor 10 Payment 2": 110,
    "Floor 10 Payment 3": 111,
    "Floor 10 Payment 4": 112,
    "Floor 10 Payment 5": 113,
    "Floor 10 Payment 6": 114,
    "Floor 10 Payment 7": 115,
    "Floor 10 Payment 8": 116,
    "Floor 10 Payment 9": 117,
    "Floor 10 Payment 10": 118,
    "Floor 10 Payment 11": 119,
    "Floor 10 Payment 12": 120,
    "Floor 11 Payment 1": 121,
    "Floor 11 Payment 2": 122,
    "Floor 11 Payment 3": 123,
    "Floor 11 Payment 4": 124,
    "Floor 11 Payment 5": 125,
    "Floor 11 Payment 6": 126,
    "Floor 11 Payment 7": 127,
    "Floor 11 Payment 8": 128,
    "Floor 11 Payment 9": 129,
    "Floor 11 Payment 10": 130,
    "Floor 11 Payment 11": 131,
    "Floor 11 Payment 12": 132,
    "Floor 12 Payment 1": 133,
    "Floor 12 Payment 2": 134,
    "Floor 12 Payment 3": 135,
    "Floor 12 Payment 4": 136,
    "Floor 12 Payment 5": 137,
    "Floor 12 Payment 6": 138,
    "Floor 12 Payment 7": 139,
    "Floor 12 Payment 8": 140,
    "Floor 12 Payment 9": 141,
    "Floor 12 Payment 10": 142,
    "Floor 12 Payment 11": 143,
    "Floor 12 Payment 12": 144,
    "Floor 13 Payment 1": 145,
    "Floor 13 Payment 2": 146,
    "Floor 13 Payment 3": 147,
    "Floor 13 Payment 4": 148,
    "Floor 13 Payment 5": 149,
    "Floor 13 Payment 6": 150,
    "Floor 13 Payment 7": 151,
    "Floor 13 Payment 8": 152,
    "Floor 13 Payment 9": 153,
    "Floor 13 Payment 10": 154,
    "Floor 13 Payment 11": 155,
    "Floor 13 Payment 12": 156,
    "Floor 14 Payment 1": 157,
    "Floor 14 Payment 2": 158,
    "Floor 14 Payment 3": 159,
    "Floor 14 Payment 4": 160,
    "Floor 14 Payment 5": 161,
    "Floor 14 Payment 6": 162,
    "Floor 14 Payment 7": 163,
    "Floor 14 Payment 8": 164,
    "Floor 14 Payment 9": 165,
    "Floor 14 Payment 10": 166,
    "Floor 14 Payment 11": 167,
    "Floor 14 Payment 12": 168,
    "Floor 15 Payment 1": 169,
    "Floor 15 Payment 2": 170,
    "Floor 15 Payment 3": 171,
    "Floor 15 Payment 4": 172,
    "Floor 15 Payment 5": 173,
    "Floor 15 Payment 6": 174,
    "Floor 15 Payment 7": 175,
    "Floor 15 Payment 8": 176,
    "Floor 15 Payment 9": 177,
    "Floor 15 Payment 10": 178,
    "Floor 15 Payment 11": 179,
    "Floor 15 Payment 12": 180,
    "Floor 16 Payment 1": 181,
    "Floor 16 Payment 2": 182,
    "Floor 16 Payment 3": 183,
    "Floor 16 Payment 4": 184,
    "Floor 16 Payment 5": 185,
    "Floor 16 Payment 6": 186,
    "Floor 16 Payment 7": 187,
    "Floor 16 Payment 8": 188,
    "Floor 16 Payment 9": 189,
    "Floor 16 Payment 10": 190,
    "Floor 16 Payment 11": 191,
    "Floor 16 Payment 12": 192,
    "Floor 17 Payment 1": 193,
    "Floor 17 Payment 2": 194,
    "Floor 17 Payment 3": 195,
    "Floor 17 Payment 4": 196,
    "Floor 17 Payment 5": 197,
    "Floor 17 Payment 6": 198,
    "Floor 17 Payment 7": 199,
    "Floor 17 Payment 8": 200,
    "Floor 17 Payment 9": 201,
    "Floor 17 Payment 10": 202,
    "Floor 17 Payment 11": 203,
    "Floor 17 Payment 12": 204,
    "Floor 18 Payment 1": 205,
    "Floor 18 Payment 2": 206,
    "Floor 18 Payment 3": 207,
    "Floor 18 Payment 4": 208,
    "Floor 18 Payment 5": 209,
    "Floor 18 Payment 6": 210,
    "Floor 18 Payment 7": 211,
    "Floor 18 Payment 8": 212,
    "Floor 18 Payment 9": 213,
    "Floor 18 Payment 10": 214,
    "Floor 18 Payment 11": 215,
    "Floor 18 Payment 12": 216,
    "Floor 19 Payment 1": 217,
    "Floor 19 Payment 2": 218,
    "Floor 19 Payment 3": 219,
    "Floor 19 Payment 4": 220,
    "Floor 19 Payment 5": 221,
    "Floor 19 Payment 6": 222,
    "Floor 19 Payment 7": 223,
    "Floor 19 Payment 8": 224,
    "Floor 19 Payment 9": 225,
    "Floor 19 Payment 10": 226,
    "Floor 19 Payment 11": 227,
    "Floor 19 Payment 12": 228,
    "Floor 20 Payment 1": 229,
    "Floor 20 Payment 2": 230,
    "Floor 20 Payment 3": 231,
    "Floor 20 Payment 4": 232,
    "Floor 20 Payment 5": 233,
    "Floor 20 Payment 6": 234,
    "Floor 20 Payment 7": 235,
    "Floor 20 Payment 8": 236,
    "Floor 20 Payment 9": 237,
    "Floor 20 Payment 10": 238,
    "Floor 20 Payment 11": 239,
    "Floor 20 Payment 12": 240,
    "AP Check 1": 241,
    "AP Check 2": 242,
    "AP Check 3": 243,
    "AP Check 4": 244,
    "AP Check 5": 245,
    "AP Check 6": 246,
    "AP Check 7": 247,
    "AP Check 8": 248,
    "AP Check 9": 249,
    "AP Check 10": 250,
    "AP Check 11": 251,
    "AP Check 12": 252,
    "AP Check 13": 253,
    "AP Check 14": 254,
    "AP Check 15": 255,
    "AP Check 16": 256,
    "AP Check 17": 257,
    "AP Check 18": 258,
    "AP Check 19": 259,
    "AP Check 20": 260,
    "AP Check 21": 261,
    "AP Check 22": 262,
    "AP Check 23": 263,
    "AP Check 24": 264,
    "AP Check 25": 265,
    "AP Check 26": 266,
    "AP Check 27": 267,
    "AP Check 28": 268,
    "AP Check 29": 269,
    "AP Check 30": 270,
    "AP Check 31": 271,
    "AP Check 32": 272,
    "AP Check 33": 273,
    "AP Check 34": 274,
    "AP Check 35": 275,
    "AP Check 36": 276,
    "AP Check 37": 277,
    "AP Check 38": 278,
    "AP Check 39": 279,
    "AP Check 40": 280,
    "AP Check 41": 281,
    "AP Check 42": 282,
    "AP Check 43": 283,
    "AP Check 44": 284,
    "AP Check 45": 285,
    "AP Check 46": 286,
    "AP Check 47": 287,
    "AP Check 48": 288,
    "AP Check 49": 289,
    "AP Check 50": 290,
    "AP Check 51": 291,
    "AP Check 52": 292,
    "AP Check 53": 293,
    "AP Check 54": 294,
    "AP Check 55": 295,
    "AP Check 56": 296,
    "AP Check 57": 297,
    "AP Check 58": 298,
    "AP Check 59": 299,
    "AP Check 60": 300,
    "AP Check 61": 301,
    "AP Check 62": 302,
    "AP Check 63": 303,
    "AP Check 64": 304,
    "AP Check 65": 305,
    "AP Check 66": 306,
    "AP Check 67": 307,
    "AP Check 68": 308,
    "AP Check 69": 309,
    "AP Check 70": 310,
    "AP Check 71": 311,
    "AP Check 72": 312,
    "AP Check 73": 313,
    "AP Check 74": 314,
    "AP Check 75": 315,
    "AP Check 76": 316,
    "AP Check 77": 317,
    "AP Check 78": 318,
    "AP Check 79": 319,
    "AP Check 80": 320,
    "AP Check 81": 321,
    "AP Check 82": 322,
    "AP Check 83": 323,
    "AP Check 84": 324,
    "AP Check 85": 325,
    "AP Check 86": 326,
    "AP Check 87": 327,
    "AP Check 88": 328,
    "AP Check 89": 329,
    "AP Check 90": 330,
    "AP Check 91": 331,
    "AP Check 92": 332,
    "AP Check 93": 333,
    "AP Check 94": 334,
    "AP Check 95": 335,
    "AP Check 96": 336,
    "AP Check 97": 337,
    "AP Check 98": 338,
    "AP Check 99": 339,
    "AP Check 100": 340,
    "AP Check 101": 341,
    "AP Check 102": 342,
    "AP Check 103": 343,
    "AP Check 104": 344,
    "AP Check 105": 345,
    "AP Check 106": 346,
    "AP Check 107": 347,
    "AP Check 108": 348,
    "AP Check 109": 349,
    "AP Check 110": 350,
    "AP Check 111": 351,
    "AP Check 112": 352,
    "AP Check 113": 353,
    "AP Check 114": 354,
    "AP Check 115": 355,
    "AP Check 116": 356,
    "AP Check 117": 357,
    "AP Check 118": 358,
    "AP Check 119": 359,
    "AP Check 120": 360,
    "AP Check 121": 361,
    "AP Check 122": 362,
    "AP Check 123": 363,
    "AP Check 124": 364,
    "AP Check 125": 365,
    "AP Check 126": 366,
    "AP Check 127": 367,
    "AP Check 128": 368,
    "AP Check 129": 369,
    "AP Check 130": 370,
    "AP Check 131": 371,
    "AP Check 132": 372,
    "AP Check 133": 373,
    "AP Check 134": 374,
    "AP Check 135": 375,
    "AP Check 136": 376,
    "AP Check 137": 377,
    "AP Check 138": 378,
    "AP Check 139": 379,
    "AP Check 140": 1118,
    "AP Check 141": 1119,
    "AP Check 142": 1120,
    "AP Check 143": 1121,
    "AP Check 144": 1122,
    "AP Check 145": 1123,
    "AP Check 146": 1124,
    "AP Check 147": 1125,
    "AP Check 148": 1126,
    "AP Check 149": 1127,
    "AP Check 150": 1128,
    "Send: Amethyst": 381,
    "Send: Anchor": 382,
    "Send: Apple": 383, 
    "Send: Banana": 384,
    "Send: Banana Peel": 385,
    "Send: Bar of Soap": 386,
    "Send: Bartender": 387,
    "Send: Bear": 388, 
    "Send: Beastmaster": 389,
    "Send: Bee": 390,
    "Send: Beehive": 391,
    "Send: Beer": 392,
    "Send: Big Ore": 393,
    "Send: Big Urn": 394, 
    "Send: Billionaire": 395, 
    "Send: Bounty Hunter": 396,
    "Send: Bronze Arrow": 397, 
    "Send: Bubble": 398,
    "Send: Buffing Capsule": 399,
    "Send: Candy": 400, 
    "Send: Card Shark": 401,
    "Send: Cat": 402,
    "Send: Cheese": 403, 
    "Send: Chef": 404,
    "Send: Chemical Seven": 405, 
    "Send: Cherry": 406,
    "Send: Chick": 407, 
    "Send: Chicken": 408,
    "Send: Clubs": 409,
    "Send: Coal": 410,
    "Send: Coconut": 411,
    "Send: Coconut Half": 412,
    "Send: Coin": 413,
    "Send: Comedian": 414,
    "Send: Cow": 415,
    "Send: Crab": 416,
    "Send: Crow": 417,
    "Send: Cultist": 418, 
    "Send: Dame": 419,
    "Send: Diamond": 420,
    "Send: Diamonds": 421,
    "Send: Diver": 422,
    "Send: Dog": 423,
    "Send: Dove": 424,
    "Send: Dwarf": 425,
    "Send: Egg": 426,
    "Send: Eldritch Creature": 427,
    "Send: Emerald": 428,
    "Send: Essence Capsule": 429,
    "Send: Farmer": 430,
    "Send: Five-Sided Die": 431,
    "Send: Flower": 432,
    "Send: Frozen Fossil": 433,
    "Send: Gambler": 434,
    "Send: General Zaroff": 435,
    "Send: Geologist": 436,
    "Send: Golden Arrow": 437,
    "Send: Golden Egg": 438,
    "Send: Goldfish": 439,
    "Send: Golem": 440,
    "Send: Goose": 441,
    "Send: Hearts": 442,
    "Send: Hex of Destruction": 443,
    "Send: Hex of Draining": 444,
    "Send: Hex of Emptiness": 445,
    "Send: Hex of Hoarding": 446,
    "Send: Hex of Midas": 447,
    "Send: Hex of Tedium": 448,
    "Send: Hex of Thievery": 449,
    "Send: Highlander": 450,
    "Send: Honey": 451,
    "Send: Hooligan": 452,
    "Send: Hustling Capsule": 453, 
    "Send: Item Capsule": 454,
    "Send: Jellyfish": 455, 
    "Send: Joker": 456,
    "Send: Key": 457,
    "Send: King Midas": 458,
    "Send: Light Bulb": 459,
    "Send: Lockbox": 460,
    "Send: Lucky Capsule": 461,
    "Send: Magic Key": 462,
    "Send: Magpie": 463,
    "Send: Martini": 464,
    "Send: Matryoshka Doll": 465,
    "Send: Matryoshka Doll 2": 466,
    "Send: Matryoshka Doll 3": 467,
    "Send: Matryoshka Doll 4": 468,
    "Send: Matryoshka Doll 5": 469,
    "Send: Mega Chest": 470,
    "Send: Midas Bomb": 471,
    "Send: Milk": 472,
    "Send: Mine": 473,
    "Send: Miner": 474,
    "Send: Monkey": 475,
    "Send: Moon": 476,
    "Send: Mouse": 477,
    "Send: Mrs. Fruit": 478,
    "Send: Ninja": 479,
    "Send: Omelette": 480,
    "Send: Orange": 481,
    "Send: Ore": 482,
    "Send: Owl": 483,
    "Send: Oyster": 484,
    "Send: Peach": 485,
    "Send: Pear": 486,
    "Send: Pearl": 487,
    "Send: Pirate": 488,
    "Send: Pinata": 489,
    "Send: Present": 490,
    "Send: Pufferfish": 491,
    "Send: Rabbit": 492,
    "Send: Rabbit Fluff": 493, 
    "Send: Rain": 494,
    "Send: Removal Capsule": 495,
    "Send: Reroll Capsule": 496,
    "Send: Robin Hood": 497,
    "Send: Ruby": 498,
    "Send: Safe": 499,
    "Send: Sand Dollar": 500,
    "Send: Sapphire": 501,
    "Send: Seed": 502,
    "Send: Shiny Pebble": 503,
    "Send: Silver Arrow": 504,
    "Send: Sloth": 505,
    "Send: Snail": 506,
    "Send: Spades": 507,
    "Send: Spirit": 508,
    "Send: Strawberry": 509,
    "Send: Sun": 510,
    "Send: Target": 511,
    "Send: Tedium Capsule": 512,
    "Send: Thief": 513,
    "Send: Three-Sided Die": 514,
    "Send: Time Capsule": 515,
    "Send: Toddler": 516,
    "Send: Tomb": 517,
    "Send: Treasure Chest": 518,
    "Send: Turtle": 519,
    "Send: Urn": 520,
    "Send: Void Creature": 521,
    "Send: Void Fruit": 522,
    "Send: Void Stone": 523,
    "Send: Watermelon": 524,
    "Send: Wealthy Capsule": 525,
    "Send: Wildcard": 526,
    "Send: Wine": 527,
    "Send: Witch": 528,
    "Send: Wolf": 529,
    "Effect: Anchor is in the corner": 531,
    "Effect: Banana Peel Destroys Thief": 532,
    "Effect: Bar of Soap adds Bubble": 533,
    "Effect: Bartender adds Chemical Seven": 534,
    "Effect: Bartender adds Beer": 535,
    "Effect: Bartender adds Wine": 536,
    "Effect: Bartender adds Martini": 537,
    "Effect: Bear Destroys Honey": 538,
    "Effect: Beastmaster Boosts Magpie": 539,
    "Effect: Beastmaster Boosts Void Creature": 540,
    "Effect: Beastmaster Boosts Turtle": 541,
    "Effect: Beastmaster Boosts Snail": 542,
    "Effect: Beastmaster Boosts Sloth": 543,
    "Effect: Beastmaster Boosts Oyster": 544,
    "Effect: Beastmaster Boosts Owl": 545,
    "Effect: Beastmaster Boosts Mouse": 546,
    "Effect: Beastmaster Boosts Monkey": 547,
    "Effect: Beastmaster Boosts Rabbit": 548,
    "Effect: Beastmaster Boosts Goose": 549,
    "Effect: Beastmaster Boosts Goldfish": 550,
    "Effect: Beastmaster Boosts Dog": 551,
    "Effect: Beastmaster Boosts Crab": 552,
    "Effect: Beastmaster Boosts Chick": 553,
    "Effect: Beastmaster Boosts Cat": 554,
    "Effect: Beastmaster Boosts Bee": 555,
    "Effect: Beastmaster Boosts Sand Dollar": 556,
    "Effect: Beastmaster Boosts Wolf": 557,
    "Effect: Beastmaster Boosts Pufferfish": 558,
    "Effect: Beastmaster Boosts Dove": 559,
    "Effect: Beastmaster Boosts Crow": 560,
    "Effect: Beastmaster Boosts Chicken": 561,
    "Effect: Beastmaster Boosts Cow": 562,
    "Effect: Beastmaster Boosts Bear": 563,
    "Effect: Beastmaster Boosts Eldritch Creature": 564,
    "Effect: Bee Boosts Flower": 565,
    "Effect: Bee Boosts Beehive": 566,
    "Effect: Bee Boosts Honey": 567,
    "Effect: Beehive adds Honey": 568,
    "Effect: Big Urn adds Spirit": 569,
    "Effect: Billionaire Boosts Cheese": 570,
    "Effect: Billionaire Boosts Wine": 571,
    "Effect: Bounty Hunter Destroys Thief": 572,
    "Effect: Bronze Arrow Boosts a Symbol": 573,
    "Effect: Bronze Arrow Destroys Target": 574,
    "Effect: Buffing Capsule Boosts Symbols": 575,
    "Effect: Card Shark Makes Clubs Wildcard": 576,
    "Effect: Card Shark Makes Diamonds Wildcard": 577,
    "Effect: Card Shark Makes Hearts Wildcard": 578,
    "Effect: Card Shark Makes Spades Wildcard": 579,
    "Effect: Cat Destroys Milk": 580,
    "Effect: Chef Boosts Chemical Seven": 581,
    "Effect: Chef Boosts Void Fruit": 582,
    "Effect: Chef Boosts Banana": 583,
    "Effect: Chef Boosts Beer": 584,
    "Effect: Chef Boosts Candy": 585,
    "Effect: Chef Boosts Cheese": 586,
    "Effect: Chef Boosts Cherry": 587,
    "Effect: Chef Boosts Egg": 588,
    "Effect: Chef Boosts Milk": 589,
    "Effect: Chef Boosts Pear": 590,
    "Effect: Chef Boosts Wine": 591,
    "Effect: Chef Boosts Coconut Half": 592,
    "Effect: Chef Boosts Orange": 593,
    "Effect: Chef Boosts Peach": 594,
    "Effect: Chef Boosts Strawberry": 595,
    "Effect: Chef Boosts Omelette": 596,
    "Effect: Chef Boosts Martini": 597,
    "Effect: Chef Boosts Honey": 598,
    "Effect: Chef Boosts Golden Egg": 599,
    "Effect: Chef Boosts Apple": 600,
    "Effect: Chef Boosts Watermelon": 601,
    "Effect: Chemical Seven Destroys Itself": 602,
    "Effect: Chick grows into Chicken": 603,
    "Effect: Clubs adjacent to Clubs": 604,
    "Effect: Clubs adjacent to Spades": 605,
    "Effect: Coal Transforms into Diamond": 606,
    "Effect: Comedian Boosts Banana": 607,
    "Effect: Comedian Boosts Banana Peel": 608,
    "Effect: Comedian Boosts Dog": 609,
    "Effect: Comedian Boosts Monkey": 610,
    "Effect: Comedian Boosts Toddler": 611,
    "Effect: Comedian Boosts Joker": 612,
    "Effect: Cow adds Milk": 613,
    "Effect: Crab in same row": 614,
    "Effect: Crow Loses Coins": 615,
    "Effect: Cultist Boosts Cultist": 616,
    "Effect: Dame Boosts Void Stone": 617,
    "Effect: Dame Boosts Amethyst": 618,
    "Effect: Dame Boosts Pearl": 619,
    "Effect: Dame Boosts Shiny Pebble": 620,
    "Effect: Dame Boosts Sapphire": 621,
    "Effect: Dame Boosts Emerald": 622,
    "Effect: Dame Boosts Ruby": 623,
    "Effect: Dame Boosts Diamond": 624,
    "Effect: Dame Destroys Martini": 625,
    "Effect: Diamond Boosts Diamond": 626,
    "Effect: Diamonds Boosts Diamonds": 627,
    "Effect: Diamonds Boosts Hearts": 628,
    "Effect: Diver Destroys Snail": 629,
    "Effect: Diver Destroys Turtle": 630,
    "Effect: Diver Destroys Anchor": 631,
    "Effect: Diver Destroys Crab": 632,
    "Effect: Diver Destroys Goldfish": 633,
    "Effect: Diver Destroys Oyster": 634,
    "Effect: Diver Destroys Pearl": 635,
    "Effect: Diver Destroys Jellyfish": 636,
    "Effect: Diver Destroys Pufferfish": 637,
    "Effect: Diver Destroys Sand Dollar": 638,
    "Effect: Dog Boosts Robin Hood": 639,
    "Effect: Dog Boosts Thief": 640,
    "Effect: Dog Boosts Cultist": 641,
    "Effect: Dog Boosts Toddler": 642,
    "Effect: Dog Boosts Bounty Hunter": 643,
    "Effect: Dog Boosts Miner": 644,
    "Effect: Dog Boosts Dwarf": 645,
    "Effect: Dog Boosts King Midas": 646,
    "Effect: Dog Boosts Gambler": 647,
    "Effect: Dog Boosts General Zaroff": 648,
    "Effect: Dog Boosts Witch": 649,
    "Effect: Dog Boosts Pirate": 650,
    "Effect: Dog Boosts Ninja": 651,
    "Effect: Dog Boosts Mrs. Fruit": 652,
    "Effect: Dog Boosts Hooligan": 653,
    "Effect: Dog Boosts Farmer": 654,
    "Effect: Dog Boosts Diver": 655, 
    "Effect: Dog Boosts Dame": 656, 
    "Effect: Dog Boosts Chef": 657,
    "Effect: Dog Boosts Card Shark": 658,
    "Effect: Dog Boosts Beastmaster": 659,
    "Effect: Dog Boosts Geologist": 660,
    "Effect: Dog Boosts Joker": 661,
    "Effect: Dog Boosts Comedian": 662,
    "Effect: Dog Boosts Bartender": 663,
    "Effect: Dove Protects destroyed Symbol": 664,
    "Effect: Dwarf Destroys Beer": 665,
    "Effect: Dwarf Destroys Wine": 666,
    "Effect: Egg transforms into Chick": 667,
    "Effect: Eldritch Creature Destroys Cultist": 668,
    "Effect: Eldritch Creature Destroys Witch": 669,
    "Effect: Eldritch Creature Destroys Hex of Destruction": 670,
    "Effect: Eldritch Creature Destroys Hex of Draining": 671,
    "Effect: Eldritch Creature Destroys Hex of Emptiness": 672,
    "Effect: Eldritch Creature Destroys Hex of Hoarding": 673,
    "Effect: Eldritch Creature Destroys Hex of Midas": 674,
    "Effect: Eldritch Creature Destroys Hex of Tedium": 675,
    "Effect: Eldritch Creature Destroys Hex of Thievery": 676,
    "Effect: Emerald Boosts Emerald": 677,
    "Effect: Essence Capsule Destroys itself": 678,
    "Effect: Farmer Boosts Void Fruit": 679,
    "Effect: Farmer Boosts Banana": 680,
    "Effect: Farmer Boosts Cheese": 681,
    "Effect: Farmer Boosts Cherry": 682,
    "Effect: Farmer Boosts Chick": 683,
    "Effect: Farmer Boosts Coconut": 684,
    "Effect: Farmer Boosts Seed": 685,
    "Effect: Farmer Boosts Egg": 686,
    "Effect: Farmer Boosts Flower": 687,
    "Effect: Farmer Boosts Milk": 688,
    "Effect: Farmer Boosts Pear": 689,
    "Effect: Farmer Boosts Chicken": 690,
    "Effect: Farmer Boosts Orange": 691,
    "Effect: Farmer Boosts Peach": 692,
    "Effect: Farmer Boosts Strawberry": 693,
    "Effect: Farmer Boosts Golden Egg": 694,
    "Effect: Farmer Boosts Cow": 695,
    "Effect: Farmer Boosts Apple": 696,
    "Effect: Farmer Boosts Watermelon": 697,
    "Effect: Farmer Boosts Seed Growing": 698,
    "Effect: Five-Sided Die Rolls": 699,
    "Effect: Frozen Fossil Destroys Cultist": 700,
    "Effect: Frozen Fossil Destroys Witch": 701,
    "Effect: Frozen Fossil Destroys Hex of Destruction": 702,
    "Effect: Frozen Fossil Destroys Hex of Draining": 703,
    "Effect: Frozen Fossil Destroys Hex of Emptiness": 704,
    "Effect: Frozen Fossil Destroys Hex of Hoarding": 705,
    "Effect: Frozen Fossil Destroys Hex of Midas": 706,
    "Effect: Frozen Fossil Destroys Hex of Tedium": 707,
    "Effect: Frozen Fossil Destroys Hex of Thievery": 708,
    "Effect: Frozen Fossil Transforms into Eldritch Creature": 709,
    "Effect: Gambler gets Destroyed by Dice": 710,
    "Effect: General Zaroff Destroys Robin Hood": 711,
    "Effect: General Zaroff Destroys Thief": 712,
    "Effect: General Zaroff Destroys Billionaire": 713,
    "Effect: General Zaroff Destroys Cultist": 714,
    "Effect: General Zaroff Destroys Toddler": 715,
    "Effect: General Zaroff Destroys Bounty Hunter": 716,
    "Effect: General Zaroff Destroys Miner":  717,
    "Effect: General Zaroff Destroys Dwarf": 718,
    "Effect: General Zaroff Destroys King Midas": 719,
    "Effect: General Zaroff Destroys Gambler": 720,
    "Effect: General Zaroff Destroys General Zaroff": 721,
    "Effect: General Zaroff Destroys Witch": 722, 
    "Effect: General Zaroff Destroys Pirate": 723,
    "Effect: General Zaroff Destroys Ninja": 724,
    "Effect: General Zaroff Destroys Mrs. Fruit": 725,
    "Effect: General Zaroff Destroys Hooligan": 726,
    "Effect: General Zaroff Destroys Farmer": 727,
    "Effect: General Zaroff Destroys Diver": 728, 
    "Effect: General Zaroff Destroys Dame": 729,
    "Effect: General Zaroff Destroys Chef": 730,
    "Effect: General Zaroff Destroys Card Shark": 731,
    "Effect: General Zaroff Destroys Beastmaster": 732,
    "Effect: General Zaroff Destroys Geologist": 733,
    "Effect: General Zaroff Destroys Joker": 734, 
    "Effect: General Zaroff Destroys Comedian": 735,
    "Effect: General Zaroff Destroys Bartender": 736,
    "Effect: Geologist Destroys Ore": 737,
    "Effect: Geologist Destroys Pearl": 738,
    "Effect: Geologist Destroys Shiny Pebble": 739,
    "Effect: Geologist Destroys Big Ore": 740,
    "Effect: Geologist Destroys Sapphire": 741,
    "Effect: Golden Arrow Boosts a Symbol": 742,
    "Effect: Golden Arrow Destroys Target": 743,
    "Effect: Goldfish Destroys Bubble": 744,
    "Effect: Golem Becomes ore": 745,
    "Effect: Goose Lays Golden Egg": 746,
    "Effect: Hearts Boost Diamonds": 747,
    "Effect: Hex of Destruction Destroys a Symbol": 748,
    "Effect: Hex of Draining Makes a Symbol give 0": 749,
    "Effect: Hex of Emptiness Skip next Symbol": 750,
    "Effect: Hex of Hoarding Force grab next Symbol": 751,
    "Effect: Hex of Midas adds Coin": 752,
    "Effect: Hex of Thievery lose 6 Coins": 753,
    "Effect: Hooligan Destroys Urn": 754,
    "Effect: Hooligan Destroys Big Urn": 755,
    "Effect: Hooligan Destroys Tomb": 756,
    "Effect: Hustling Capsule adds Pool Ball": 757, 
    "Effect: Item Capsule adds a Common Item": 758,
    "Effect: Jellyfish gives Removal Token": 759,
    "Effect: Joker Boosts Clubs": 760,
    "Effect: Joker Boosts Diamonds": 761,
    "Effect: Joker Boosts Hearts": 762,
    "Effect: Joker Boosts Spades": 763,
    "Effect: Key Destroys Lockbox": 764,
    "Effect: Key Destroys Safe": 765,
    "Effect: Key Destroys Treasure Chest": 766,
    "Effect: Key Destroys Mega Chest": 767,
    "Effect: King Midas adds Coin": 768,
    "Effect: King Midas Boosts Coin": 769,
    "Effect: Light Bulb Boosts Void Stone": 770,
    "Effect: Light Bulb Boosts Amethyst": 771,
    "Effect: Light Bulb Boosts Pearl": 772,
    "Effect: Light Bulb Boosts Shiny Pebble": 773,
    "Effect: Light Bulb Boosts Sapphire": 774,
    "Effect: Light Bulb Boosts Emerald": 775,
    "Effect: Light Bulb Boosts Ruby": 776,
    "Effect: Light Bulb Boosts Diamond": 777,
    "Effect: Light Bulb Destroys Itself": 778,
    "Effect: Lucky Capsule Destroys Itself": 779,
    "Effect: Magic Key Destroys Lockbox": 780,
    "Effect: Magic Key Destroys Safe": 781,
    "Effect: Magic Key Destroys Treasure Chest": 782,
    "Effect: Magic Key Destroys Mega Chest": 783,
    "Effect: Magpie gain 9 coins": 784,
    "Effect: Matryoshka Doll turns into Matryoshka Doll 1": 785,
    "Effect: Matryoshka Doll 1 turns into Matryoshka Doll 2": 786,
    "Effect: Matryoshka Doll 2 turn into Matryoshka Doll 3": 787,
    "Effect: Matryoshka Doll 3 turn into Matryoshka Doll 4": 788,
    "Effect: Matryoshka Doll 4 turn into Matryoshka Doll 5": 789,
    "Effect: Midas Bomb Destroys Symbols around": 790,
    "Effect: Mine adds Ore": 791,
    "Effect: Mine adds Mining Pick": 792,
    "Effect: Miner Destroys Ore": 793,
    "Effect: Miner Destroys Big Ore": 794,
    "Effect: Monkey Destroys Banana": 795,
    "Effect: Monkey Destroys Coconut": 796,
    "Effect: Monkey Destroys Coconut Half": 797,
    "Effect: Moon Boosts Owl": 798,
    "Effect: Moon Boosts Rabbit": 799,
    "Effect: Moon Boosts Wolf": 800,
    "Effect: Mouse Destroys Cheese": 802,
    "Effect: Mrs. Fruit Destroys Banana": 803, 
    "Effect: Mrs. Fruit Destroys Cherry": 804,
    "Effect: Mrs. Fruit Destroys Coconut": 805,
    "Effect: Mrs. Fruit Destroys Coconut Half": 806,
    "Effect: Mrs. Fruit Destroys Orange": 807,
    "Effect: Mrs. Fruit Destroys Peach": 808,
    "Effect: Ninja gives 1 less coin": 809,
    "Effect: Omelette Boosts Cheese": 810,
    "Effect: Omelette Boosts Egg": 811,
    "Effect: Omelette Boosts Milk": 812,
    "Effect: Omelette Boosts Golden Egg": 813,
    "Effect: Omelette Boosts Omelette": 814,
    "Effect: Owl Gives 1 more": 815,
    "Effect: Oyster adds Pearl": 816,
    "Effect: Pear give 1 more Coin": 818,
    "Effect: Pirate Destroys Anchor": 819,
    "Effect: Pirate Destroys Beer": 820,
    "Effect: Pirate Destroys Coin": 821,
    "Effect: Pirate Destroys Lockbox": 822,
    "Effect: Pirate Destroys Safe": 823,
    "Effect: Pirate Destroys Orange": 824,
    "Effect: Pirate Destroys Treasure Chest": 825,
    "Effect: Pirate Destroys Mega Chest": 826,
    "Effect: Present Destroys itself": 827,
    "Effect: Pufferfish give 1 Reroll Token": 828,
    "Effect: Rabbit gives 2 more": 829,
    "Effect: Rain Boosts Flower": 830,
    "Effect: Rain Boosts Seed Growing": 831,
    "Effect: Removal Capsule Gives 1 Destroy Token": 832,
    "Effect: Reroll Capsule Gives 1 Reroll Token": 833,
    "Effect: Robin Hood Makes Bronze Arrow give 3 Coins": 834,
    "Effect: Robin Hood Makes Silver Arrow give 3 coins": 835,
    "Effect: Robin Hood Makes Golden Arrow give 3 coins": 836,
    "Effect: Robin Hood Makes Thief give 3 coins": 837,
    "Effect: Robin Hood Destroys Billionaire": 838,
    "Effect: Robin Hood Destroys Target": 839,
    "Effect: Robin Hood Destroys Apple": 840,
    "Effect: Ruby Boosts Ruby": 841,
    "Effect: Silver Arrow Boosts a Symbol": 842,
    "Effect: Silver Arrow Destroys Target": 843,
    "Effect: Sloth gives 4 coins": 844,
    "Effect: Snail gives 5 coins": 845,
    "Effect: Spades Boosts Spades": 846,
    "Effect: Spades Boosts Clubs": 847,
    "Effect: Strawberry Boosts Strawberry": 848,
    "Effect: Sun Boosts Flower": 849,
    "Effect: Sun Boosts Seed Growth": 850,
    "Effect: Tedium Capsule Destroys itself": 857,
    "Effect: Thief Removes Coin": 851,
    "Effect: Three-Sided Die Roll": 852,
    "Effect: Time Capsule Destroys itself": 853,
    "Effect: Toddler Destroys Candy": 854,
    "Effect: Toddler Destroys Pinata": 855,
    "Effect: Toddler Destroys Present": 856,
    "Effect: Toddler Destroys Bubble": 867,
    "Effect: Tomb adds Spirit": 868,
    "Effect: Turtle Gives 4 Coins": 869,
    "Effect: Void Creature Gives 8 Coins": 871,
    "Effect: Void Fruit Gives 8 Coins": 873,
    "Effect: Void Stone Gives 8 Coins": 875,
    "Effect: Watermelon Boosts Watermelon": 876,
    "Effect: Wealthy Capsule Gives 10 Coins": 877,
    "Effect: Wildcard Copies a Symbol": 878,
    "Effect: Wine Gives 1 more Coin": 879,
    "Effect: Witch Boosts Cat": 880,
    "Effect: Witch Boosts Owl": 881,
    "Effect: Witch Boosts Crow": 882,
    "Effect: Witch Boosts Apple": 883,
    "Effect: Witch Boosts Hex of Destruction": 884,
    "Effect: Witch Boosts Hex of Draining": 885,
    "Effect: Witch Boosts Hex of Emptiness": 886, 
    "Effect: Witch Boosts Hex of Hoarding": 887,
    "Effect: Witch Boosts Hex of Midas": 888,
    "Effect: Witch Boosts Hex of Tedium": 889,
    "Effect: Witch Boosts Hex of Thievery": 890,
    "Effect: Witch Boosts Eldritch Creature": 891,
    "Effect: Witch Boosts Spirit": 892,
    "Send: 5th Ace": 893,
    "Send: Adoption Papers": 894,
    "Send: Ancient Lizard Blade": 895,
    "Send: Anthropology Degree": 896,
    "Send: Barrel of Dwarves": 897,
    "Send: Big Symbol Bomb": 898,
    "Send: Birdhouse": 899,
    "Send: Black Cat": 900,
    "Send: Black Pepper": 901,
    "Send: Black Suits": 902,
    "Send: Blue Pepper": 903,
    "Send: Booster Pack": 904,
    "Send: Bowling Ball": 905,
    "Send: Brown Pepper": 906,
    "Send: Capsule Machine": 907,
    "Send: Cardboard Box": 908,
    "Send: Checkered Flag": 909,
    "Send: Chicken Coop": 910,
    "Send: Chili Powder": 911,
    "Send: Cleaning Rag": 912,
    "Send: Clear Sky": 913,
    "Send: Coffee": 914,
    "Send: Coin on a String": 915,
    "Send: Comfy Pillow": 916,
    "Send: Compost Heap": 917,
    "Send: Conveyor Belt": 918,
    "Send: Copycat": 919,
    "Send: Credit Card": 920,
    "Send: Cursed Katana": 921,
    "Send: Cyan Pepper": 922,
    "Send: Dark Humor": 923,
    "Send: Devil's Deal": 924,
    "Send: Dishwasher": 925,
    "Send: Dwarven Anvil": 926,
    "Send: Egg Carton": 927,
    "Send: Fertilizer": 928,
    "Send: Fish Tank": 929,
    "Send: Flush": 930,
    "Send: Four-leaf clover": 931,
    "Send: Frozen Pizza": 932,
    "Send: Fruit Basket": 933,
    "Send: Frying Pan": 934,
    "Send: Golden Carrot": 935,
    "Send: Goldilocks": 936,
    "Send: Grave Robber": 937,
    "Send: Gray Pepper": 938,
    "Send: Green Pepper": 939,
    "Send: Guillotine": 940,
    "Send: Happy Hour": 941,
    "Send: Holy Water": 942,
    "Send: Horseshoe": 943,
    "Send: Instant Ramen": 944,
    "Send: Jack-o'-lantern": 945,
    "Send: Kyle the Kernite": 946,
    "Send: Lefty the Rabbit": 947,
    "Send: Lemon": 948,
    "Send: Lime Pepper": 949,
    "Send: Lint Roller": 950,
    "Send: Lockpick": 951,
    "Send: Looting Glove": 952,
    "Send: Lucky Carrot": 953,
    "Send: Lucky Cat": 954,
    "Send: Lucky Dice": 955,
    "Send: Lucky Seven": 956,
    "Send: Lunchbox": 957,
    "Send: Maxwell the Bear": 958,
    "Send: Mining Pick": 959,
    "Send: Mobius Strip": 960,
    "Send: Ninja and Mouse": 961,
    "Send: Nori the Rabbit": 962,
    "Send: Oil Can": 963,
    "Send: Oswald the Monkey": 964,
    "Send: Piggy Bank": 965,
    "Send: Pink Pepper": 966,
    "Send: Pizza the Cat": 967,
    "Send: Pool Ball": 968,
    "Send: Popsicle": 969,
    "Send: Protractor": 970,
    "Send: Purple Pepper": 971,
    "Send: Quantum Symbol Bomb": 972,
    "Send: Quiver": 973,
    "Send: Rain Cloud": 974,
    "Send: Recycling": 975,
    "Send: Red Pepper": 976,
    "Send: Red Suits": 977,
    "Send: Reroll": 978,
    "Send: Ricky the Banana": 979,
    "Send: Ritual Candle": 980,
    "Send: Rusty Gear": 981,
    "Send: Shattered Mirror": 982,
    "Send: Shedding Season": 983,
    "Send: Shrine": 984,
    "Send: Small Symbol Bomb": 985,
    "Send: Sunglasses": 986,
    "Send: Swapping Device": 987,
    "Send: Swear Jar": 988,
    "Send: Tax Evasion": 989,
    "Send: Telescope": 990,
    "Send: The Tortoise and the Hare": 991,
    "Send: Time Machine": 992,
    "Send: Treasure Map": 993,
    "Send: Triple Coins": 994,
    "Send: Undertaker": 995,
    "Send: Very Big Symbol Bomb": 996,
    "Send: Void Party": 997,
    "Send: Void Portal": 998,
    "Send: Wanted Poster": 999,
    "Send: Watering Can": 1000,
    "Send: White Pepper": 1001,
    "Send: X-ray Machine": 1002,
    "Send: Yellow Pepper": 1003,
    "Send: Zaroff's Contract": 1004,
    "Send: 5th Ace Essence": 1005,
    "Send: Adoption Papers Essence": 1006,
    "Send: Ancient Lizard Blade Essence": 1007,
    "Send: Anthropology Degree Essence": 1008,
    "Send: Barrel of Dwarves Essence": 1009,
    "Send: Big Symbol Bomb Essence": 1010,
    "Send: Birdhouse Essence": 1011,
    "Send: Black Cat Essence": 1012,
    "Send: Black Pepper Essence": 1013,
    "Send: Black Suits Essence": 1014,
    "Send: Blue Pepper Essence": 1015,
    "Send: Booster Pack Essence": 1016,
    "Send: Bowling Ball Essence": 1017,
    "Send: Brown Pepper Essence": 1018,
    "Send: Capsule Machine Essence": 1019,
    "Send: Cardboard Box Essence": 1020,
    "Send: Checkered Flag Essence": 1021,
    "Send: Chicken Coop Essence": 1022,
    "Send: Chili Powder Essence": 1023,
    "Send: Cleaning Rag Essence": 1024,
    "Send: Clear Sky Essence": 1025,
    "Send: Coffee Essence": 1026,
    "Send: Coin on a String Essence": 1027,
    "Send: Comfy Pillow Essence": 1028,
    "Send: Compost Heap Essence": 1029,
    "Send: Conveyor Belt Essence": 1030,
    "Send: Copycat Essence": 1031,
    "Send: Credit Card Essence": 1032,
    "Send: Cursed Katana Essence": 1033,
    "Send: Cyan Pepper Essence": 1034,
    "Send: Dark Humor Essence": 1035,
    "Send: Devil's Deal Essence": 1036,
    "Send: Dishwasher Essence": 1037,
    "Send: Dwarven Anvil Essence": 1038,
    "Send: Egg Carton Essence": 1039,
    "Send: Fertilizer Essence": 1040,
    "Send: Fish Tank Essence": 1041,
    "Send: Flush Essence": 1042,
    "Send: Four-leaf clover Essence": 1043,
    "Send: Frozen Pizza Essence": 1044,
    "Send: Fruit Basket Essence": 1045,
    "Send: Frying Pan Essence": 1046,
    "Send: Golden Carrot Essence": 1047,
    "Send: Goldilocks Essence": 1048,
    "Send: Grave Robber Essence": 1049,
    "Send: Gray Pepper Essence": 1050,
    "Send: Green Pepper Essence": 1051,
    "Send: Guillotine Essence": 1052,
    "Send: Happy Hour Essence": 1053,
    "Send: Holy Water Essence": 1054,
    "Send: Horseshoe Essence": 1055,
    "Send: Instant Ramen Essence": 1056,
    "Send: Jack-o'-lantern Essence": 1057,
    "Send: Kyle the Kernite Essence": 1058,
    "Send: Lefty the Rabbit Essence": 1059,
    "Send: Lemon Essence": 1060,
    "Send: Lime Pepper Essence": 1061,
    "Send: Lint Roller Essence": 1062,
    "Send: Lockpick Essence": 1063,
    "Send: Looting Glove Essence": 1064,
    "Send: Lucky Carrot Essence": 1065,
    "Send: Lucky Cat Essence": 1066,
    "Send: Lucky Dice Essence": 1067,
    "Send: Lucky Seven Essence": 1068,
    "Send: Lunchbox Essence": 1069,
    "Send: Maxwell the Bear Essence": 1070,
    "Send: Mining Pick Essence": 1071,
    "Send: Mobius Strip Essence": 1072,
    "Send: Ninja and Mouse Essence": 1073,
    "Send: Nori the Rabbit Essence": 1074,
    "Send: Oil Can Essence": 1075,
    "Send: Oswald the Monkey Essence": 1076,
    "Send: Piggy Bank Essence": 1077,
    "Send: Pink Pepper Essence": 1078,
    "Send: Pizza the Cat Essence": 1079,
    "Send: Pool Ball Essence": 1080,
    "Send: Popsicle Essence": 1081,
    "Send: Protractor Essence": 1082,
    "Send: Purple Pepper Essence": 1083,
    "Send: Quantum Symbol Bomb Essence": 1084,
    "Send: Quigley the Wolf Essence": 1085,
    "Send: Quiver Essence": 1086,
    "Send: Rain Cloud Essence": 1087,
    "Send: Recycling Essence": 1088,
    "Send: Red Pepper Essence": 1089,
    "Send: Red Suits Essence": 1090,
    "Send: Reroll Essence": 1091,
    "Send: Ricky the Banana Essence": 1092,
    "Send: Ritual Candle Essence": 1093,
    "Send: Rusty Gear Essence": 1094,
    "Send: Shattered Mirror Essence": 1095,
    "Send: Shedding Season Essence": 1096,
    "Send: Shrine Essence": 1097,
    "Send: Small Symbol Bomb Essence": 1098,
    "Send: Sunglasses Essence": 1099,
    "Send: Swapping Device Essence": 1100,
    "Send: Swear Jar Essence": 1101,
    "Send: Tax Evasion Essence": 1102,
    "Send: Telescope Essence": 1103,
    "Send: The Tortoise and the Hare Essence": 1104,
    "Send: Time Machine Essence": 1105,
    "Send: Treasure Map Essence": 1106,
    "Send: Triple Coins Essence": 1107,
    "Send: Undertaker Essence": 1108,
    "Send: Very Big Symbol Bomb Essence": 1109,
    "Send: Void Party Essence": 1110,
    "Send: Void Portal Essence": 1111,
    "Send: Wanted Poster Essence": 1112,
    "Send: Watering Can Essence": 1113,
    "Send: White Pepper Essence": 1114,
    "Send: X-ray Machine Essence": 1115,
    "Send: Yellow Pepper Essence": 1116,
    "Send: Zaroff's Contract Essence": 1117,
}

    # --------------------------------------------------
    # Automatically generate per-floor Send/Effect checks
    # --------------------------------------------------

BASE_SEND_EFFECT_LOCATION_NAMES = tuple(
    name
    for name in LOCATION_NAME_TO_ID
    if (
        name.startswith("Send: ")
        or name.startswith("Effect: ")
    )
)

_next_location_id = max(LOCATION_NAME_TO_ID.values()) + 1

for floor_number in range(1, 21):
    for base_name in BASE_SEND_EFFECT_LOCATION_NAMES:

        floor_location_name = (
           f"Floor {floor_number} - {base_name}"
        )

        LOCATION_NAME_TO_ID[floor_location_name] = (
            _next_location_id
        )

        _next_location_id += 1


# Each Location instance must correctly report the "game" it belongs to.
# To make this simple, it is common practice to subclass the basic Location class and override the "game" field.
class LBALLocation(Location):
    game = "Luck be a Landlord"


# Let's make one more helper method before we begin actually creating locations.
# Later on in the code, we'll want specific subsections of LOCATION_NAME_TO_ID.
# To reduce the chance of copy-paste errors writing something like {"Chest": LOCATION_NAME_TO_ID["Chest"]},
# let's make a helper method that takes a list of location names and returns them as a dict with their IDs.
# Note: There is a minor typing quirk here. Some functions want location addresses to be an "int | None",
# so while our function here only ever returns dict[str, int], we annotate it as dict[str, int | None].
def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_NAME_TO_ID[location_name] for location_name in location_names}


def create_all_locations(world: LBALWorld) -> None:
    create_regular_locations(world)



rare_names = {
    "Amethyst", "Apple", "Bartender", "Beastmaster", "Beehive",
    "Card Shark", "Chef", "Chicken", "Comedian", "Cow",
    "Dame", "Diver", "Dove", "Emerald", "Farmer",
    "Frozen Fossil", "General Zaroff", "Geologist", "Golden Egg",
    "Honey", "Joker", "King Midas", "Magic Key", "Martini",
    "Mine", "Moon", "Mrs. Fruit", "Omelette", "Pear",
    "Robin Hood", "Ruby", "Silver Arrow", "Spirit", "Strawberry",
    "Sun", "Tomb", "Treasure Chest", "Witch",
    "Anthropology Degree",
    "Anthropology Degree Essence",
    "Booster Pack",
    "Booster Pack Essence",
    "Bowling Ball",
    "Bowling Ball Essence",
    "Capsule Machine",
    "Capsule Machine Essence",
    "Chicken Coop",
    "Chicken Coop Essence",
    "Chili Powder",
    "Chili Powder Essence",
    "Clear Sky",
    "Clear Sky Essence",
    "Coffee",
    "Coffee Essence",
    "Devil's Deal",
    "Devil's Deal Essence",
    "Dishwasher",
    "Dishwasher Essence",
    "Holy Water",
    "Holy Water Essence",
    "Instant Ramen",
    "Instant Ramen Essence",
    "Lucky Carrot",
    "Lucky Carrot Essence",
    "Lucky Dice",
    "Lucky Dice Essence",
    "Oil Can",
    "Oil Can Essence",
    "Protractor",
    "Protractor Essence",
    "Quiver",
    "Quiver Essence",
    "Sunglasses",
    "Sunglasses Essence",
    "Swapping Device",
    "Swapping Device Essence",
    "Undertaker",
    "Undertaker Essence",
    "Very Big Symbol Bomb",
    "Very Big Symbol Bomb Essence",
    "Void Party",
    "Void Party Essence",
    "Void Portal",
    "Void Portal Essence",
}

very_rare_names = {
    "Diamond",
    "Eldritch Creature",
    "Golden Arrow",
    "Highlander",
    "Mega Chest",
    "Midas Bomb",
    "Pirate",
    "Watermelon",
    "Wildcard",
    "Ancient Lizard Blade",
    "Ancient Lizard Blade Essence",
    "Copycat",
    "Copycat Essence",
    "Credit Card",
    "Credit Card Essence",
    "Four-leaf clover",
    "Four-leaf clover Essence",
    "Frozen Pizza",
    "Frozen Pizza Essence",
    "Golden Carrot",
    "Golden Carrot Essence",
    "Mobius Strip",
    "Mobius Strip Essence",
    "Popsicle",
    "Popsicle Essence",
    "Recycling",
    "Recycling Essence",
    "Telescope",
    "Telescope Essence",
}

def is_rare_or_very_rare(check_text: str) -> bool:
    return any(re.search(rf"(?<!\w){re.escape(name)}(?!\w)", check_text, re.IGNORECASE,)
        for name in rare_names | very_rare_names
    )

def get_enabled_send_effect_names(world: LBALWorld) -> list[str]:
    enabled_names = []

    for base_name in BASE_SEND_EFFECT_LOCATION_NAMES:

        if base_name.startswith("Send: "):
            check_text = base_name.removeprefix("Send: ")
        else:
            check_text = base_name.removeprefix("Effect: ")

        if not world.options.Rare:
            if any(
                re.search(
                    rf"(?<!\w){re.escape(name)}(?!\w)",
                    check_text,
                    re.IGNORECASE,
                )
                for name in rare_names
            ):
                continue

        if not world.options.VeryRare:
            if any(
                re.search(
                    rf"(?<!\w){re.escape(name)}(?!\w)",
                    check_text,
                    re.IGNORECASE,
                )
                for name in very_rare_names
            ):
                continue

        enabled_names.append(base_name)

    return enabled_names

def create_regular_locations(world: LBALWorld) -> None:
    # Finally, we need to put the Locations ("checks") into their regions.
    # Once again, before we do anything, we can grab our regions we created by using world.get_region()
    Floor_1 = world.get_region("Floor 1")

    if "2" in world.options.Floors.value:
        Floor_2 = world.get_region("Floor 2")

    if "3" in world.options.Floors.value:
        Floor_3 = world.get_region("Floor 3")

    if "4" in world.options.Floors.value:
        Floor_4 = world.get_region("Floor 4")

    if "5" in world.options.Floors.value:
        Floor_5 = world.get_region("Floor 5")

    if "6" in world.options.Floors.value:
        Floor_6 = world.get_region("Floor 6")

    if "7" in world.options.Floors.value:
        Floor_7 = world.get_region("Floor 7")

    if "8" in world.options.Floors.value:
        Floor_8 = world.get_region("Floor 8")

    if "9" in world.options.Floors.value:
        Floor_9 = world.get_region("Floor 9")

    if "10" in world.options.Floors.value:
        Floor_10 = world.get_region("Floor 10")

    if "11" in world.options.Floors.value:
        Floor_11 = world.get_region("Floor 11")

    if "12" in world.options.Floors.value:
        Floor_12 = world.get_region("Floor 12")

    if "13" in world.options.Floors.value:
        Floor_13 = world.get_region("Floor 13")

    if "14" in world.options.Floors.value:
        Floor_14 = world.get_region("Floor 14")

    if "15" in world.options.Floors.value:
        Floor_15 = world.get_region("Floor 15")

    if "16" in world.options.Floors.value:
        Floor_16 = world.get_region("Floor 16")

    if "17" in world.options.Floors.value:
        Floor_17 = world.get_region("Floor 17")

    if "18" in world.options.Floors.value:
        Floor_18 = world.get_region("Floor 18")

    if "19" in world.options.Floors.value:
        Floor_19 = world.get_region("Floor 19")

    if "20" in world.options.Floors.value:
        Floor_20 = world.get_region("Floor 20")
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

    enabled_floors = [1] + sorted(
        int(floor)
        for floor in world.options.Floors.value
    )

    for base_name in get_enabled_send_effect_names(world):



        if base_name.startswith("Send: "):
            check_text = base_name.removeprefix("Send: ")
        else:
            check_text = base_name.removeprefix("Effect: ")

        # Rare disabled
        if not world.options.Rare:
            if any(re.search(rf"(?<!\w){re.escape(name)}(?!\w)", check_text, re.IGNORECASE,) for name in rare_names):
                continue

        if not world.options.VeryRare:
            if any(re.search(rf"(?<!\w){re.escape(name)}(?!\w)", check_text, re.IGNORECASE,) for name in very_rare_names):
                continue
        # --------------------------------------------------
        # Floor-dependent mode
        # --------------------------------------------------
        if world.options.FloorDependentChecks:

            for floor_number in enabled_floors:

                floor_region = world.get_region(
                    f"Floor {floor_number}"
                )

                floor_location_name = (
                    f"Floor {floor_number} - {base_name}"
                )

                location = LBALLocation(
                    world.player,
                    floor_location_name,
                    world.location_name_to_id[
                        floor_location_name
                    ],
                    floor_region,
                )

                floor_region.locations.append(location)

        # --------------------------------------------------
        # Original mode
        # --------------------------------------------------
        else:

            location = LBALLocation(
                world.player,
                base_name,
                world.location_name_to_id[
                    base_name
                ],
                Symbol_Send,
            )

            Symbol_Send.locations.append(location)
    

    

    # # One way to create locations is by just creating them directly via their constructor.
    # bottom_left_chest = APQuestLocation(
    #     world.player, "Bottom Left Chest", world.location_name_to_id["Bottom Left Chest"], overworld
    # )

    #  # You can then add them to the region.
    #  overworld.locations.append(bottom_left_chest)
    
    
    ap_check_1 = LBALLocation(
        world.player, "AP Check 1", world.location_name_to_id["AP Check 1"], Progressive_AP_1_10
    )
    Progressive_AP_1_10.locations.append(ap_check_1)

    ap_check_2 = LBALLocation(
        world.player, "AP Check 2", world.location_name_to_id["AP Check 2"], Progressive_AP_1_10
    )
    Progressive_AP_1_10.locations.append(ap_check_2)

    ap_check_3 = LBALLocation(
        world.player, "AP Check 3", world.location_name_to_id["AP Check 3"], Progressive_AP_1_10
    )
    Progressive_AP_1_10.locations.append(ap_check_3)

    ap_check_4 = LBALLocation(
        world.player, "AP Check 4", world.location_name_to_id["AP Check 4"], Progressive_AP_1_10
    )
    Progressive_AP_1_10.locations.append(ap_check_4)

    ap_check_5 = LBALLocation(
        world.player, "AP Check 5", world.location_name_to_id["AP Check 5"], Progressive_AP_1_10
    )
    Progressive_AP_1_10.locations.append(ap_check_5)

    ap_check_6 = LBALLocation(
        world.player, "AP Check 6", world.location_name_to_id["AP Check 6"], Progressive_AP_1_10
    )
    Progressive_AP_1_10.locations.append(ap_check_6)

    ap_check_7 = LBALLocation(
        world.player, "AP Check 7", world.location_name_to_id["AP Check 7"], Progressive_AP_1_10
    )
    Progressive_AP_1_10.locations.append(ap_check_7)

    ap_check_8 = LBALLocation(
        world.player, "AP Check 8", world.location_name_to_id["AP Check 8"], Progressive_AP_1_10
    )
    Progressive_AP_1_10.locations.append(ap_check_8)

    ap_check_9 = LBALLocation(
        world.player, "AP Check 9", world.location_name_to_id["AP Check 9"], Progressive_AP_1_10
    )
    Progressive_AP_1_10.locations.append(ap_check_9)

    ap_check_10 = LBALLocation(
        world.player, "AP Check 10", world.location_name_to_id["AP Check 10"], Progressive_AP_1_10
    )
    Progressive_AP_1_10.locations.append(ap_check_10)

    ap_check_11 = LBALLocation(
        world.player, "AP Check 11", world.location_name_to_id["AP Check 11"], Progressive_AP_11_20
    )
    Progressive_AP_11_20.locations.append(ap_check_11)

    ap_check_12 = LBALLocation(
        world.player, "AP Check 12", world.location_name_to_id["AP Check 12"], Progressive_AP_11_20
    )
    Progressive_AP_11_20.locations.append(ap_check_12)

    ap_check_13 = LBALLocation(
        world.player, "AP Check 13", world.location_name_to_id["AP Check 13"], Progressive_AP_11_20
    )
    Progressive_AP_11_20.locations.append(ap_check_13)

    ap_check_14 = LBALLocation(
        world.player, "AP Check 14", world.location_name_to_id["AP Check 14"], Progressive_AP_11_20
    )
    Progressive_AP_11_20.locations.append(ap_check_14)

    ap_check_15 = LBALLocation(
        world.player, "AP Check 15", world.location_name_to_id["AP Check 15"], Progressive_AP_11_20
    )
    Progressive_AP_11_20.locations.append(ap_check_15)

    ap_check_16 = LBALLocation(
        world.player, "AP Check 16", world.location_name_to_id["AP Check 16"], Progressive_AP_11_20
    )
    Progressive_AP_11_20.locations.append(ap_check_16)

    ap_check_17 = LBALLocation(
        world.player, "AP Check 17", world.location_name_to_id["AP Check 17"], Progressive_AP_11_20
    )
    Progressive_AP_11_20.locations.append(ap_check_17)

    ap_check_18 = LBALLocation(
        world.player, "AP Check 18", world.location_name_to_id["AP Check 18"], Progressive_AP_11_20
    )
    Progressive_AP_11_20.locations.append(ap_check_18)

    ap_check_19 = LBALLocation(
        world.player, "AP Check 19", world.location_name_to_id["AP Check 19"], Progressive_AP_11_20
    )
    Progressive_AP_11_20.locations.append(ap_check_19)

    ap_check_20 = LBALLocation(
        world.player, "AP Check 20", world.location_name_to_id["AP Check 20"], Progressive_AP_11_20
    )
    Progressive_AP_11_20.locations.append(ap_check_20)

    ap_check_21 = LBALLocation(
        world.player, "AP Check 21", world.location_name_to_id["AP Check 21"], Progressive_AP_21_30
    )
    Progressive_AP_21_30.locations.append(ap_check_21)

    ap_check_22 = LBALLocation(
        world.player, "AP Check 22", world.location_name_to_id["AP Check 22"], Progressive_AP_21_30
    )
    Progressive_AP_21_30.locations.append(ap_check_22)

    ap_check_23 = LBALLocation(
        world.player, "AP Check 23", world.location_name_to_id["AP Check 23"], Progressive_AP_21_30
    )
    Progressive_AP_21_30.locations.append(ap_check_23)

    ap_check_24 = LBALLocation(
        world.player, "AP Check 24", world.location_name_to_id["AP Check 24"], Progressive_AP_21_30
    )
    Progressive_AP_21_30.locations.append(ap_check_24)

    ap_check_25 = LBALLocation(
        world.player, "AP Check 25", world.location_name_to_id["AP Check 25"], Progressive_AP_21_30
    )
    Progressive_AP_21_30.locations.append(ap_check_25)

    ap_check_26 = LBALLocation(
        world.player, "AP Check 26", world.location_name_to_id["AP Check 26"], Progressive_AP_21_30
    )
    Progressive_AP_21_30.locations.append(ap_check_26)

    ap_check_27 = LBALLocation(
        world.player, "AP Check 27", world.location_name_to_id["AP Check 27"], Progressive_AP_21_30
    )
    Progressive_AP_21_30.locations.append(ap_check_27)

    ap_check_28 = LBALLocation(
        world.player, "AP Check 28", world.location_name_to_id["AP Check 28"], Progressive_AP_21_30
    )
    Progressive_AP_21_30.locations.append(ap_check_28)

    ap_check_29 = LBALLocation(
        world.player, "AP Check 29", world.location_name_to_id["AP Check 29"], Progressive_AP_21_30
    )
    Progressive_AP_21_30.locations.append(ap_check_29)

    ap_check_30 = LBALLocation(
        world.player, "AP Check 30", world.location_name_to_id["AP Check 30"], Progressive_AP_21_30
    )
    Progressive_AP_21_30.locations.append(ap_check_30)

    ap_check_31 = LBALLocation(
        world.player, "AP Check 31", world.location_name_to_id["AP Check 31"], Progressive_AP_31_40
    )
    Progressive_AP_31_40.locations.append(ap_check_31)

    ap_check_32 = LBALLocation(
        world.player, "AP Check 32", world.location_name_to_id["AP Check 32"], Progressive_AP_31_40
    )
    Progressive_AP_31_40.locations.append(ap_check_32)

    ap_check_33 = LBALLocation(
        world.player, "AP Check 33", world.location_name_to_id["AP Check 33"], Progressive_AP_31_40
    )
    Progressive_AP_31_40.locations.append(ap_check_33)

    ap_check_34 = LBALLocation(
        world.player, "AP Check 34", world.location_name_to_id["AP Check 34"], Progressive_AP_31_40
    )
    Progressive_AP_31_40.locations.append(ap_check_34)

    ap_check_35 = LBALLocation(
        world.player, "AP Check 35", world.location_name_to_id["AP Check 35"], Progressive_AP_31_40
    )
    Progressive_AP_31_40.locations.append(ap_check_35)

    ap_check_36 = LBALLocation(
        world.player, "AP Check 36", world.location_name_to_id["AP Check 36"], Progressive_AP_31_40
    )
    Progressive_AP_31_40.locations.append(ap_check_36)

    ap_check_37 = LBALLocation(
        world.player, "AP Check 37", world.location_name_to_id["AP Check 37"], Progressive_AP_31_40
    )
    Progressive_AP_31_40.locations.append(ap_check_37)

    ap_check_38 = LBALLocation(
        world.player, "AP Check 38", world.location_name_to_id["AP Check 38"], Progressive_AP_31_40
    )
    Progressive_AP_31_40.locations.append(ap_check_38)

    ap_check_39 = LBALLocation(
        world.player, "AP Check 39", world.location_name_to_id["AP Check 39"], Progressive_AP_31_40
    )
    Progressive_AP_31_40.locations.append(ap_check_39)

    ap_check_40 = LBALLocation(
        world.player, "AP Check 40", world.location_name_to_id["AP Check 40"], Progressive_AP_31_40
    )
    Progressive_AP_31_40.locations.append(ap_check_40)

    ap_check_41 = LBALLocation(
        world.player, "AP Check 41", world.location_name_to_id["AP Check 41"], Progressive_AP_41_50
    )
    Progressive_AP_41_50.locations.append(ap_check_41)

    ap_check_42 = LBALLocation(
        world.player, "AP Check 42", world.location_name_to_id["AP Check 42"], Progressive_AP_41_50
    )
    Progressive_AP_41_50.locations.append(ap_check_42)

    ap_check_43 = LBALLocation(
        world.player, "AP Check 43", world.location_name_to_id["AP Check 43"], Progressive_AP_41_50
    )
    Progressive_AP_41_50.locations.append(ap_check_43)

    ap_check_44 = LBALLocation(
        world.player, "AP Check 44", world.location_name_to_id["AP Check 44"], Progressive_AP_41_50
    )
    Progressive_AP_41_50.locations.append(ap_check_44)

    ap_check_45 = LBALLocation(
        world.player, "AP Check 45", world.location_name_to_id["AP Check 45"], Progressive_AP_41_50
    )
    Progressive_AP_41_50.locations.append(ap_check_45)

    ap_check_46 = LBALLocation(
        world.player, "AP Check 46", world.location_name_to_id["AP Check 46"], Progressive_AP_41_50
    )
    Progressive_AP_41_50.locations.append(ap_check_46)

    ap_check_47 = LBALLocation(
        world.player, "AP Check 47", world.location_name_to_id["AP Check 47"], Progressive_AP_41_50
    )
    Progressive_AP_41_50.locations.append(ap_check_47)

    ap_check_48 = LBALLocation(
        world.player, "AP Check 48", world.location_name_to_id["AP Check 48"], Progressive_AP_41_50
    )
    Progressive_AP_41_50.locations.append(ap_check_48)

    ap_check_49 = LBALLocation(
        world.player, "AP Check 49", world.location_name_to_id["AP Check 49"], Progressive_AP_41_50
    )
    Progressive_AP_41_50.locations.append(ap_check_49)

    ap_check_50 = LBALLocation(
        world.player, "AP Check 50", world.location_name_to_id["AP Check 50"], Progressive_AP_41_50
    )
    Progressive_AP_41_50.locations.append(ap_check_50)

    ap_check_51 = LBALLocation(
        world.player, "AP Check 51", world.location_name_to_id["AP Check 51"], Progressive_AP_51_60
    )
    Progressive_AP_51_60.locations.append(ap_check_51)

    ap_check_52 = LBALLocation(
        world.player, "AP Check 52", world.location_name_to_id["AP Check 52"], Progressive_AP_51_60
    )
    Progressive_AP_51_60.locations.append(ap_check_52)

    ap_check_53 = LBALLocation(
        world.player, "AP Check 53", world.location_name_to_id["AP Check 53"], Progressive_AP_51_60
    )
    Progressive_AP_51_60.locations.append(ap_check_53)

    ap_check_54 = LBALLocation(
        world.player, "AP Check 54", world.location_name_to_id["AP Check 54"], Progressive_AP_51_60
    )
    Progressive_AP_51_60.locations.append(ap_check_54)

    ap_check_55 = LBALLocation(
        world.player, "AP Check 55", world.location_name_to_id["AP Check 55"], Progressive_AP_51_60
    )
    Progressive_AP_51_60.locations.append(ap_check_55)

    ap_check_56 = LBALLocation(
        world.player, "AP Check 56", world.location_name_to_id["AP Check 56"], Progressive_AP_51_60
    )
    Progressive_AP_51_60.locations.append(ap_check_56)

    ap_check_57 = LBALLocation(
        world.player, "AP Check 57", world.location_name_to_id["AP Check 57"], Progressive_AP_51_60
    )
    Progressive_AP_51_60.locations.append(ap_check_57)

    ap_check_58 = LBALLocation(
        world.player, "AP Check 58", world.location_name_to_id["AP Check 58"], Progressive_AP_51_60
    )
    Progressive_AP_51_60.locations.append(ap_check_58)

    ap_check_59 = LBALLocation(
        world.player, "AP Check 59", world.location_name_to_id["AP Check 59"], Progressive_AP_51_60
    )
    Progressive_AP_51_60.locations.append(ap_check_59)

    ap_check_60 = LBALLocation(
        world.player, "AP Check 60", world.location_name_to_id["AP Check 60"], Progressive_AP_51_60
    )
    Progressive_AP_51_60.locations.append(ap_check_60)

    ap_check_61 = LBALLocation(
        world.player, "AP Check 61", world.location_name_to_id["AP Check 61"], Progressive_AP_61_70
    )
    Progressive_AP_61_70.locations.append(ap_check_61)

    ap_check_62 = LBALLocation(
        world.player, "AP Check 62", world.location_name_to_id["AP Check 62"], Progressive_AP_61_70
    )
    Progressive_AP_61_70.locations.append(ap_check_62)

    ap_check_63 = LBALLocation(
        world.player, "AP Check 63", world.location_name_to_id["AP Check 63"], Progressive_AP_61_70
    )
    Progressive_AP_61_70.locations.append(ap_check_63)

    ap_check_64 = LBALLocation(
        world.player, "AP Check 64", world.location_name_to_id["AP Check 64"], Progressive_AP_61_70
    )
    Progressive_AP_61_70.locations.append(ap_check_64)

    ap_check_65 = LBALLocation(
        world.player, "AP Check 65", world.location_name_to_id["AP Check 65"], Progressive_AP_61_70
    )
    Progressive_AP_61_70.locations.append(ap_check_65)

    ap_check_66 = LBALLocation(
        world.player, "AP Check 66", world.location_name_to_id["AP Check 66"], Progressive_AP_61_70
    )
    Progressive_AP_61_70.locations.append(ap_check_66)

    ap_check_67 = LBALLocation(
        world.player, "AP Check 67", world.location_name_to_id["AP Check 67"], Progressive_AP_61_70
    )
    Progressive_AP_61_70.locations.append(ap_check_67)

    ap_check_68 = LBALLocation(
        world.player, "AP Check 68", world.location_name_to_id["AP Check 68"], Progressive_AP_61_70
    )
    Progressive_AP_61_70.locations.append(ap_check_68)

    ap_check_69 = LBALLocation(
        world.player, "AP Check 69", world.location_name_to_id["AP Check 69"], Progressive_AP_61_70
    )
    Progressive_AP_61_70.locations.append(ap_check_69)

    ap_check_70 = LBALLocation(
        world.player, "AP Check 70", world.location_name_to_id["AP Check 70"], Progressive_AP_61_70
    )
    Progressive_AP_61_70.locations.append(ap_check_70)

    ap_check_71 = LBALLocation(
        world.player, "AP Check 71", world.location_name_to_id["AP Check 71"], Progressive_AP_71_80
    )
    Progressive_AP_71_80.locations.append(ap_check_71)

    ap_check_72 = LBALLocation(
        world.player, "AP Check 72", world.location_name_to_id["AP Check 72"], Progressive_AP_71_80
    )
    Progressive_AP_71_80.locations.append(ap_check_72)

    ap_check_73 = LBALLocation(
        world.player, "AP Check 73", world.location_name_to_id["AP Check 73"], Progressive_AP_71_80
    )
    Progressive_AP_71_80.locations.append(ap_check_73)

    ap_check_74 = LBALLocation(
        world.player, "AP Check 74", world.location_name_to_id["AP Check 74"], Progressive_AP_71_80
    )
    Progressive_AP_71_80.locations.append(ap_check_74)

    ap_check_75 = LBALLocation(
        world.player, "AP Check 75", world.location_name_to_id["AP Check 75"], Progressive_AP_71_80
    )
    Progressive_AP_71_80.locations.append(ap_check_75)

    ap_check_76 = LBALLocation(
        world.player, "AP Check 76", world.location_name_to_id["AP Check 76"], Progressive_AP_71_80
    )
    Progressive_AP_71_80.locations.append(ap_check_76)

    ap_check_77 = LBALLocation(
        world.player, "AP Check 77", world.location_name_to_id["AP Check 77"], Progressive_AP_71_80
    )
    Progressive_AP_71_80.locations.append(ap_check_77)

    ap_check_78 = LBALLocation(
        world.player, "AP Check 78", world.location_name_to_id["AP Check 78"], Progressive_AP_71_80
    )
    Progressive_AP_71_80.locations.append(ap_check_78)

    ap_check_79 = LBALLocation(
        world.player, "AP Check 79", world.location_name_to_id["AP Check 79"], Progressive_AP_71_80
    )
    Progressive_AP_71_80.locations.append(ap_check_79)

    ap_check_80 = LBALLocation(
        world.player, "AP Check 80", world.location_name_to_id["AP Check 80"], Progressive_AP_71_80
    )
    Progressive_AP_71_80.locations.append(ap_check_80)

    ap_check_81 = LBALLocation(
        world.player, "AP Check 81", world.location_name_to_id["AP Check 81"], Progressive_AP_81_90
    )
    Progressive_AP_81_90.locations.append(ap_check_81)

    ap_check_82 = LBALLocation(
        world.player, "AP Check 82", world.location_name_to_id["AP Check 82"], Progressive_AP_81_90
    )
    Progressive_AP_81_90.locations.append(ap_check_82)

    ap_check_83 = LBALLocation(
        world.player, "AP Check 83", world.location_name_to_id["AP Check 83"], Progressive_AP_81_90
    )
    Progressive_AP_81_90.locations.append(ap_check_83)

    ap_check_84 = LBALLocation(
        world.player, "AP Check 84", world.location_name_to_id["AP Check 84"], Progressive_AP_81_90
    )
    Progressive_AP_81_90.locations.append(ap_check_84)

    ap_check_85 = LBALLocation(
        world.player, "AP Check 85", world.location_name_to_id["AP Check 85"], Progressive_AP_81_90
    )
    Progressive_AP_81_90.locations.append(ap_check_85)

    ap_check_86 = LBALLocation(
        world.player, "AP Check 86", world.location_name_to_id["AP Check 86"], Progressive_AP_81_90
    )
    Progressive_AP_81_90.locations.append(ap_check_86)

    ap_check_87 = LBALLocation(
        world.player, "AP Check 87", world.location_name_to_id["AP Check 87"], Progressive_AP_81_90
    )
    Progressive_AP_81_90.locations.append(ap_check_87)

    ap_check_88 = LBALLocation(
        world.player, "AP Check 88", world.location_name_to_id["AP Check 88"], Progressive_AP_81_90
    )
    Progressive_AP_81_90.locations.append(ap_check_88)

    ap_check_89 = LBALLocation(
        world.player, "AP Check 89", world.location_name_to_id["AP Check 89"], Progressive_AP_81_90
    )
    Progressive_AP_81_90.locations.append(ap_check_89)

    ap_check_90 = LBALLocation(
        world.player, "AP Check 90", world.location_name_to_id["AP Check 90"], Progressive_AP_81_90
    )
    Progressive_AP_81_90.locations.append(ap_check_90)

    ap_check_91 = LBALLocation(
        world.player, "AP Check 91", world.location_name_to_id["AP Check 91"], Progressive_AP_91_100
    )
    Progressive_AP_91_100.locations.append(ap_check_91)

    ap_check_92 = LBALLocation(
        world.player, "AP Check 92", world.location_name_to_id["AP Check 92"], Progressive_AP_91_100
    )
    Progressive_AP_91_100.locations.append(ap_check_92)

    ap_check_93 = LBALLocation(
        world.player, "AP Check 93", world.location_name_to_id["AP Check 93"], Progressive_AP_91_100
    )
    Progressive_AP_91_100.locations.append(ap_check_93)

    ap_check_94 = LBALLocation(
        world.player, "AP Check 94", world.location_name_to_id["AP Check 94"], Progressive_AP_91_100
    )
    Progressive_AP_91_100.locations.append(ap_check_94)

    ap_check_95 = LBALLocation(
        world.player, "AP Check 95", world.location_name_to_id["AP Check 95"], Progressive_AP_91_100
    )
    Progressive_AP_91_100.locations.append(ap_check_95)

    ap_check_96 = LBALLocation(
        world.player, "AP Check 96", world.location_name_to_id["AP Check 96"], Progressive_AP_91_100
    )
    Progressive_AP_91_100.locations.append(ap_check_96)

    ap_check_97 = LBALLocation(
        world.player, "AP Check 97", world.location_name_to_id["AP Check 97"], Progressive_AP_91_100
    )
    Progressive_AP_91_100.locations.append(ap_check_97)

    ap_check_98 = LBALLocation(
        world.player, "AP Check 98", world.location_name_to_id["AP Check 98"], Progressive_AP_91_100
    )
    Progressive_AP_91_100.locations.append(ap_check_98)

    ap_check_99 = LBALLocation(
        world.player, "AP Check 99", world.location_name_to_id["AP Check 99"], Progressive_AP_91_100
    )
    Progressive_AP_91_100.locations.append(ap_check_99)

    ap_check_100 = LBALLocation(
        world.player, "AP Check 100", world.location_name_to_id["AP Check 100"], Progressive_AP_91_100
    )
    Progressive_AP_91_100.locations.append(ap_check_100)

    ap_check_101 = LBALLocation(
        world.player, "AP Check 101", world.location_name_to_id["AP Check 101"], Progressive_AP_101_110
    )
    Progressive_AP_101_110.locations.append(ap_check_101)

    ap_check_102 = LBALLocation(
        world.player, "AP Check 102", world.location_name_to_id["AP Check 102"], Progressive_AP_101_110
    )
    Progressive_AP_101_110.locations.append(ap_check_102)

    ap_check_103 = LBALLocation(
        world.player, "AP Check 103", world.location_name_to_id["AP Check 103"], Progressive_AP_101_110
    )
    Progressive_AP_101_110.locations.append(ap_check_103)

    ap_check_104 = LBALLocation(
        world.player, "AP Check 104", world.location_name_to_id["AP Check 104"], Progressive_AP_101_110
    )
    Progressive_AP_101_110.locations.append(ap_check_104)

    ap_check_105 = LBALLocation(
        world.player, "AP Check 105", world.location_name_to_id["AP Check 105"], Progressive_AP_101_110
    )
    Progressive_AP_101_110.locations.append(ap_check_105)

    ap_check_106 = LBALLocation(
        world.player, "AP Check 106", world.location_name_to_id["AP Check 106"], Progressive_AP_101_110
    )
    Progressive_AP_101_110.locations.append(ap_check_106)

    ap_check_107 = LBALLocation(
        world.player, "AP Check 107", world.location_name_to_id["AP Check 107"], Progressive_AP_101_110
    )
    Progressive_AP_101_110.locations.append(ap_check_107)

    ap_check_108 = LBALLocation(
        world.player, "AP Check 108", world.location_name_to_id["AP Check 108"], Progressive_AP_101_110
    )
    Progressive_AP_101_110.locations.append(ap_check_108)

    ap_check_109 = LBALLocation(
        world.player, "AP Check 109", world.location_name_to_id["AP Check 109"], Progressive_AP_101_110
    )
    Progressive_AP_101_110.locations.append(ap_check_109)

    ap_check_110 = LBALLocation(
        world.player, "AP Check 110", world.location_name_to_id["AP Check 110"], Progressive_AP_101_110
    )
    Progressive_AP_101_110.locations.append(ap_check_110)

    ap_check_111 = LBALLocation(
        world.player, "AP Check 111", world.location_name_to_id["AP Check 111"], Progressive_AP_111_120
    )
    Progressive_AP_111_120.locations.append(ap_check_111)

    ap_check_112 = LBALLocation(
        world.player, "AP Check 112", world.location_name_to_id["AP Check 112"], Progressive_AP_111_120
    )
    Progressive_AP_111_120.locations.append(ap_check_112)

    ap_check_113 = LBALLocation(
        world.player, "AP Check 113", world.location_name_to_id["AP Check 113"], Progressive_AP_111_120
    )
    Progressive_AP_111_120.locations.append(ap_check_113)

    ap_check_114 = LBALLocation(
        world.player, "AP Check 114", world.location_name_to_id["AP Check 114"], Progressive_AP_111_120
    )
    Progressive_AP_111_120.locations.append(ap_check_114)

    ap_check_115 = LBALLocation(
        world.player, "AP Check 115", world.location_name_to_id["AP Check 115"], Progressive_AP_111_120
    )
    Progressive_AP_111_120.locations.append(ap_check_115)

    ap_check_116 = LBALLocation(
        world.player, "AP Check 116", world.location_name_to_id["AP Check 116"], Progressive_AP_111_120
    )
    Progressive_AP_111_120.locations.append(ap_check_116)

    ap_check_117 = LBALLocation(
        world.player, "AP Check 117", world.location_name_to_id["AP Check 117"], Progressive_AP_111_120
    )
    Progressive_AP_111_120.locations.append(ap_check_117)

    ap_check_118 = LBALLocation(
        world.player, "AP Check 118", world.location_name_to_id["AP Check 118"], Progressive_AP_111_120
    )
    Progressive_AP_111_120.locations.append(ap_check_118)

    ap_check_119 = LBALLocation(
        world.player, "AP Check 119", world.location_name_to_id["AP Check 119"], Progressive_AP_111_120
    )
    Progressive_AP_111_120.locations.append(ap_check_119)

    ap_check_120 = LBALLocation(
        world.player, "AP Check 120", world.location_name_to_id["AP Check 120"], Progressive_AP_111_120
    )
    Progressive_AP_111_120.locations.append(ap_check_120)

    ap_check_121 = LBALLocation(
        world.player, "AP Check 121", world.location_name_to_id["AP Check 121"], Progressive_AP_121_130
    )
    Progressive_AP_121_130.locations.append(ap_check_121)

    ap_check_122 = LBALLocation(
        world.player, "AP Check 122", world.location_name_to_id["AP Check 122"], Progressive_AP_121_130
    )
    Progressive_AP_121_130.locations.append(ap_check_122)

    ap_check_123 = LBALLocation(
        world.player, "AP Check 123", world.location_name_to_id["AP Check 123"], Progressive_AP_121_130
    )
    Progressive_AP_121_130.locations.append(ap_check_123)

    ap_check_124 = LBALLocation(
        world.player, "AP Check 124", world.location_name_to_id["AP Check 124"], Progressive_AP_121_130
    )
    Progressive_AP_121_130.locations.append(ap_check_124)

    ap_check_125 = LBALLocation(
        world.player, "AP Check 125", world.location_name_to_id["AP Check 125"], Progressive_AP_121_130
    )
    Progressive_AP_121_130.locations.append(ap_check_125)

    ap_check_126 = LBALLocation(
        world.player, "AP Check 126", world.location_name_to_id["AP Check 126"], Progressive_AP_121_130
    )
    Progressive_AP_121_130.locations.append(ap_check_126)

    ap_check_127 = LBALLocation(
        world.player, "AP Check 127", world.location_name_to_id["AP Check 127"], Progressive_AP_121_130
    )
    Progressive_AP_121_130.locations.append(ap_check_127)

    ap_check_128 = LBALLocation(
        world.player, "AP Check 128", world.location_name_to_id["AP Check 128"], Progressive_AP_121_130
    )
    Progressive_AP_121_130.locations.append(ap_check_128)

    ap_check_129 = LBALLocation(
        world.player, "AP Check 129", world.location_name_to_id["AP Check 129"], Progressive_AP_121_130
    )
    Progressive_AP_121_130.locations.append(ap_check_129)

    ap_check_130 = LBALLocation(
        world.player, "AP Check 130", world.location_name_to_id["AP Check 130"], Progressive_AP_121_130
    )
    Progressive_AP_121_130.locations.append(ap_check_130)

    ap_check_131 = LBALLocation(
        world.player, "AP Check 131", world.location_name_to_id["AP Check 131"], Progressive_AP_131_140
    )
    Progressive_AP_131_140.locations.append(ap_check_131)

    ap_check_132 = LBALLocation(
        world.player, "AP Check 132", world.location_name_to_id["AP Check 132"], Progressive_AP_131_140
    )
    Progressive_AP_131_140.locations.append(ap_check_132)

    ap_check_133 = LBALLocation(
        world.player, "AP Check 133", world.location_name_to_id["AP Check 133"], Progressive_AP_131_140
    )
    Progressive_AP_131_140.locations.append(ap_check_133)

    ap_check_134 = LBALLocation(
        world.player, "AP Check 134", world.location_name_to_id["AP Check 134"], Progressive_AP_131_140
    )
    Progressive_AP_131_140.locations.append(ap_check_134)

    ap_check_135 = LBALLocation(
        world.player, "AP Check 135", world.location_name_to_id["AP Check 135"], Progressive_AP_131_140
    )
    Progressive_AP_131_140.locations.append(ap_check_135)

    ap_check_136 = LBALLocation(
        world.player, "AP Check 136", world.location_name_to_id["AP Check 136"], Progressive_AP_131_140
    )
    Progressive_AP_131_140.locations.append(ap_check_136)

    ap_check_137 = LBALLocation(
        world.player, "AP Check 137", world.location_name_to_id["AP Check 137"], Progressive_AP_131_140
    )
    Progressive_AP_131_140.locations.append(ap_check_137)

    ap_check_138 = LBALLocation(
        world.player, "AP Check 138", world.location_name_to_id["AP Check 138"], Progressive_AP_131_140
    )
    Progressive_AP_131_140.locations.append(ap_check_138)

    ap_check_139 = LBALLocation(
        world.player, "AP Check 139", world.location_name_to_id["AP Check 139"], Progressive_AP_131_140
    )
    Progressive_AP_131_140.locations.append(ap_check_139)

    ap_check_140 = LBALLocation(
        world.player, "AP Check 140", world.location_name_to_id["AP Check 140"], Progressive_AP_131_140
    )
    Progressive_AP_131_140.locations.append(ap_check_140)

    ap_check_141 = LBALLocation(
        world.player, "AP Check 141", world.location_name_to_id["AP Check 141"], Progressive_AP_141_150
    )
    Progressive_AP_141_150.locations.append(ap_check_141)

    ap_check_142 = LBALLocation(
        world.player, "AP Check 142", world.location_name_to_id["AP Check 142"], Progressive_AP_141_150
    )
    Progressive_AP_141_150.locations.append(ap_check_142)

    ap_check_143 = LBALLocation(
        world.player, "AP Check 143", world.location_name_to_id["AP Check 143"], Progressive_AP_141_150
    )
    Progressive_AP_141_150.locations.append(ap_check_143)

    ap_check_144 = LBALLocation(
        world.player, "AP Check 144", world.location_name_to_id["AP Check 144"], Progressive_AP_141_150
    )
    Progressive_AP_141_150.locations.append(ap_check_144)

    ap_check_145 = LBALLocation(
        world.player, "AP Check 145", world.location_name_to_id["AP Check 145"], Progressive_AP_141_150
    )
    Progressive_AP_141_150.locations.append(ap_check_145)

    ap_check_146 = LBALLocation(
        world.player, "AP Check 146", world.location_name_to_id["AP Check 146"], Progressive_AP_141_150
    )
    Progressive_AP_141_150.locations.append(ap_check_146)

    ap_check_147 = LBALLocation(
        world.player, "AP Check 147", world.location_name_to_id["AP Check 147"], Progressive_AP_141_150
    )
    Progressive_AP_141_150.locations.append(ap_check_147)

    ap_check_148 = LBALLocation(
        world.player, "AP Check 148", world.location_name_to_id["AP Check 148"], Progressive_AP_141_150
    )
    Progressive_AP_141_150.locations.append(ap_check_148)

    ap_check_149 = LBALLocation(
        world.player, "AP Check 149", world.location_name_to_id["AP Check 149"], Progressive_AP_141_150
    )
    Progressive_AP_141_150.locations.append(ap_check_149)

    ap_check_150 = LBALLocation(
        world.player, "AP Check 150", world.location_name_to_id["AP Check 150"], Progressive_AP_141_150
    )
    Progressive_AP_141_150.locations.append(ap_check_150)

    for ap_check in (
        ap_check_10,
        ap_check_20,
        ap_check_30,
        ap_check_40,
        ap_check_50,
        ap_check_60,
        ap_check_70,
        ap_check_80,
        ap_check_90,
        ap_check_100,
        ap_check_110,
        ap_check_120,
        ap_check_130,
        ap_check_140,
    ):
        ap_check.place_locked_item(world.create_item("Progressive AP"))

    Floor_1_Payment_1 = LBALLocation(
        world.player, "Floor 1 Payment 1", world.location_name_to_id["Floor 1 Payment 1"], Floor_1
    )

    Floor_1.locations.append(Floor_1_Payment_1)

    Floor_1_Payment_2 = LBALLocation(
        world.player, "Floor 1 Payment 2", world.location_name_to_id["Floor 1 Payment 2"], Floor_1
    )

    Floor_1.locations.append(Floor_1_Payment_2)

    Floor_1_Payment_3 = LBALLocation(
        world.player, "Floor 1 Payment 3", world.location_name_to_id["Floor 1 Payment 3"], Floor_1
    )

    Floor_1.locations.append(Floor_1_Payment_3)

    Floor_1_Payment_4 = LBALLocation(
        world.player, "Floor 1 Payment 4", world.location_name_to_id["Floor 1 Payment 4"], Floor_1
    )

    Floor_1.locations.append(Floor_1_Payment_4)

    Floor_1_Payment_5 = LBALLocation(
        world.player, "Floor 1 Payment 5", world.location_name_to_id["Floor 1 Payment 5"], Floor_1
    )

    Floor_1.locations.append(Floor_1_Payment_5)

    Floor_1_Payment_6 = LBALLocation(
        world.player, "Floor 1 Payment 6", world.location_name_to_id["Floor 1 Payment 6"], Floor_1
    )

    Floor_1.locations.append(Floor_1_Payment_6)

    Floor_1_Payment_7 = LBALLocation(
        world.player, "Floor 1 Payment 7", world.location_name_to_id["Floor 1 Payment 7"], Floor_1
    )

    Floor_1.locations.append(Floor_1_Payment_7)

    Floor_1_Payment_8 = LBALLocation(
        world.player, "Floor 1 Payment 8", world.location_name_to_id["Floor 1 Payment 8"], Floor_1
    )

    Floor_1.locations.append(Floor_1_Payment_8)

    Floor_1_Payment_9 = LBALLocation(
        world.player, "Floor 1 Payment 9", world.location_name_to_id["Floor 1 Payment 9"], Floor_1
    )

    Floor_1.locations.append(Floor_1_Payment_9)

    Floor_1_Payment_10 = LBALLocation(
        world.player, "Floor 1 Payment 10", world.location_name_to_id["Floor 1 Payment 10"], Floor_1
    )

    Floor_1.locations.append(Floor_1_Payment_10)

    Floor_1_Payment_11 = LBALLocation(
        world.player, "Floor 1 Payment 11", world.location_name_to_id["Floor 1 Payment 11"], Floor_1
    )

    Floor_1.locations.append(Floor_1_Payment_11)

    Floor_1_Payment_12 = LBALLocation(
        world.player, "Floor 1 Payment 12", world.location_name_to_id["Floor 1 Payment 12"], Floor_1
    )

    Floor_1.locations.append(Floor_1_Payment_12)
    if "2" in world.options.Floors.value:
        Floor_2_Payment_1 = LBALLocation(
            world.player, "Floor 2 Payment 1", world.location_name_to_id["Floor 2 Payment 1"], Floor_2
        )

        Floor_2.locations.append(Floor_2_Payment_1)
    if "2" in world.options.Floors.value:
        Floor_2_Payment_2 = LBALLocation(
            world.player, "Floor 2 Payment 2", world.location_name_to_id["Floor 2 Payment 2"], Floor_2
        )

        Floor_2.locations.append(Floor_2_Payment_2)
    if "2" in world.options.Floors.value:
        Floor_2_Payment_3 = LBALLocation(
            world.player, "Floor 2 Payment 3", world.location_name_to_id["Floor 2 Payment 3"], Floor_2
        )

        Floor_2.locations.append(Floor_2_Payment_3)
    if "2" in world.options.Floors.value:
        Floor_2_Payment_4 = LBALLocation(
            world.player, "Floor 2 Payment 4", world.location_name_to_id["Floor 2 Payment 4"], Floor_2
        )

        Floor_2.locations.append(Floor_2_Payment_4)
    if "2" in world.options.Floors.value:
        Floor_2_Payment_5 = LBALLocation(
            world.player, "Floor 2 Payment 5", world.location_name_to_id["Floor 2 Payment 5"], Floor_2
        )

        Floor_2.locations.append(Floor_2_Payment_5)
    if "2" in world.options.Floors.value:
        Floor_2_Payment_6 = LBALLocation(
            world.player, "Floor 2 Payment 6", world.location_name_to_id["Floor 2 Payment 6"], Floor_2
        )

        Floor_2.locations.append(Floor_2_Payment_6)
    if "2" in world.options.Floors.value:
        Floor_2_Payment_7 = LBALLocation(
            world.player, "Floor 2 Payment 7", world.location_name_to_id["Floor 2 Payment 7"], Floor_2
        )

        Floor_2.locations.append(Floor_2_Payment_7)
    if "2" in world.options.Floors.value:
        Floor_2_Payment_8 = LBALLocation(
            world.player, "Floor 2 Payment 8", world.location_name_to_id["Floor 2 Payment 8"], Floor_2
        )

        Floor_2.locations.append(Floor_2_Payment_8)
    if "2" in world.options.Floors.value:
        Floor_2_Payment_9 = LBALLocation(
            world.player, "Floor 2 Payment 9", world.location_name_to_id["Floor 2 Payment 9"], Floor_2
        )

        Floor_2.locations.append(Floor_2_Payment_9)
    if "2" in world.options.Floors.value:
        Floor_2_Payment_10 = LBALLocation(
            world.player, "Floor 2 Payment 10", world.location_name_to_id["Floor 2 Payment 10"], Floor_2
        )

        Floor_2.locations.append(Floor_2_Payment_10)
    if "2" in world.options.Floors.value:
        Floor_2_Payment_11 = LBALLocation(
            world.player, "Floor 2 Payment 11", world.location_name_to_id["Floor 2 Payment 11"], Floor_2
        )

        Floor_2.locations.append(Floor_2_Payment_11)
    if "2" in world.options.Floors.value:
        Floor_2_Payment_12 = LBALLocation(
            world.player, "Floor 2 Payment 12", world.location_name_to_id["Floor 2 Payment 12"], Floor_2
        )

        Floor_2.locations.append(Floor_2_Payment_12)
        
    if "3" in world.options.Floors.value:
        Floor_3_Payment_1 = LBALLocation(
            world.player, "Floor 3 Payment 1", world.location_name_to_id["Floor 3 Payment 1"], Floor_3
        )

        Floor_3.locations.append(Floor_3_Payment_1)

    if "3" in world.options.Floors.value:
        Floor_3_Payment_2 = LBALLocation(
            world.player, "Floor 3 Payment 2", world.location_name_to_id["Floor 3 Payment 2"], Floor_3
        )

        Floor_3.locations.append(Floor_3_Payment_2)

    if "3" in world.options.Floors.value:
        Floor_3_Payment_3 = LBALLocation(
            world.player, "Floor 3 Payment 3", world.location_name_to_id["Floor 3 Payment 3"], Floor_3
        )

        Floor_3.locations.append(Floor_3_Payment_3)

    if "3" in world.options.Floors.value:
        Floor_3_Payment_4 = LBALLocation(
            world.player, "Floor 3 Payment 4", world.location_name_to_id["Floor 3 Payment 4"], Floor_3
        )

        Floor_3.locations.append(Floor_3_Payment_4)

    if "3" in world.options.Floors.value:
        Floor_3_Payment_5 = LBALLocation(
            world.player, "Floor 3 Payment 5", world.location_name_to_id["Floor 3 Payment 5"], Floor_3
        )

        Floor_3.locations.append(Floor_3_Payment_5)

    if "3" in world.options.Floors.value:
        Floor_3_Payment_6 = LBALLocation(
            world.player, "Floor 3 Payment 6", world.location_name_to_id["Floor 3 Payment 6"], Floor_3
        )

        Floor_3.locations.append(Floor_3_Payment_6)

    if "3" in world.options.Floors.value:
        Floor_3_Payment_7 = LBALLocation(
            world.player, "Floor 3 Payment 7", world.location_name_to_id["Floor 3 Payment 7"], Floor_3
        )

        Floor_3.locations.append(Floor_3_Payment_7)

    if "3" in world.options.Floors.value:
        Floor_3_Payment_8 = LBALLocation(
            world.player, "Floor 3 Payment 8", world.location_name_to_id["Floor 3 Payment 8"], Floor_3
        )

        Floor_3.locations.append(Floor_3_Payment_8)

    if "3" in world.options.Floors.value:
        Floor_3_Payment_9 = LBALLocation(
            world.player, "Floor 3 Payment 9", world.location_name_to_id["Floor 3 Payment 9"], Floor_3
        )

        Floor_3.locations.append(Floor_3_Payment_9)

    if "3" in world.options.Floors.value:
        Floor_3_Payment_10 = LBALLocation(
            world.player, "Floor 3 Payment 10", world.location_name_to_id["Floor 3 Payment 10"], Floor_3
        )

        Floor_3.locations.append(Floor_3_Payment_10)

    if "3" in world.options.Floors.value:
        Floor_3_Payment_11 = LBALLocation(
            world.player, "Floor 3 Payment 11", world.location_name_to_id["Floor 3 Payment 11"], Floor_3
        )

        Floor_3.locations.append(Floor_3_Payment_11)

    if "3" in world.options.Floors.value:
        Floor_3_Payment_12 = LBALLocation(
            world.player, "Floor 3 Payment 12", world.location_name_to_id["Floor 3 Payment 12"], Floor_3
        )

        Floor_3.locations.append(Floor_3_Payment_12)

    if "4" in world.options.Floors.value:
        Floor_4_Payment_1 = LBALLocation(
            world.player, "Floor 4 Payment 1", world.location_name_to_id["Floor 4 Payment 1"], Floor_4
        )

        Floor_4.locations.append(Floor_4_Payment_1)

    if "4" in world.options.Floors.value:
        Floor_4_Payment_2 = LBALLocation(
            world.player, "Floor 4 Payment 2", world.location_name_to_id["Floor 4 Payment 2"], Floor_4
        )

        Floor_4.locations.append(Floor_4_Payment_2)

    if "4" in world.options.Floors.value:
        Floor_4_Payment_3 = LBALLocation(
            world.player, "Floor 4 Payment 3", world.location_name_to_id["Floor 4 Payment 3"], Floor_4
        )

        Floor_4.locations.append(Floor_4_Payment_3)

    if "4" in world.options.Floors.value:
        Floor_4_Payment_4 = LBALLocation(
            world.player, "Floor 4 Payment 4", world.location_name_to_id["Floor 4 Payment 4"], Floor_4
        )

        Floor_4.locations.append(Floor_4_Payment_4)

    if "4" in world.options.Floors.value:
        Floor_4_Payment_5 = LBALLocation(
            world.player, "Floor 4 Payment 5", world.location_name_to_id["Floor 4 Payment 5"], Floor_4
        )

        Floor_4.locations.append(Floor_4_Payment_5)

    if "4" in world.options.Floors.value:
        Floor_4_Payment_6 = LBALLocation(
            world.player, "Floor 4 Payment 6", world.location_name_to_id["Floor 4 Payment 6"], Floor_4
        )

        Floor_4.locations.append(Floor_4_Payment_6)

    if "4" in world.options.Floors.value:
        Floor_4_Payment_7 = LBALLocation(
            world.player, "Floor 4 Payment 7", world.location_name_to_id["Floor 4 Payment 7"], Floor_4
        )

        Floor_4.locations.append(Floor_4_Payment_7)

    if "4" in world.options.Floors.value:
        Floor_4_Payment_8 = LBALLocation(
            world.player, "Floor 4 Payment 8", world.location_name_to_id["Floor 4 Payment 8"], Floor_4
        )

        Floor_4.locations.append(Floor_4_Payment_8)

    if "4" in world.options.Floors.value:
        Floor_4_Payment_9 = LBALLocation(
            world.player, "Floor 4 Payment 9", world.location_name_to_id["Floor 4 Payment 9"], Floor_4
        )

        Floor_4.locations.append(Floor_4_Payment_9)

    if "4" in world.options.Floors.value:
        Floor_4_Payment_10 = LBALLocation(
            world.player, "Floor 4 Payment 10", world.location_name_to_id["Floor 4 Payment 10"], Floor_4
        )

        Floor_4.locations.append(Floor_4_Payment_10)

    if "4" in world.options.Floors.value:
        Floor_4_Payment_11 = LBALLocation(
            world.player, "Floor 4 Payment 11", world.location_name_to_id["Floor 4 Payment 11"], Floor_4
        )

        Floor_4.locations.append(Floor_4_Payment_11)

    if "4" in world.options.Floors.value:
        Floor_4_Payment_12 = LBALLocation(
            world.player, "Floor 4 Payment 12", world.location_name_to_id["Floor 4 Payment 12"], Floor_4
        )

        Floor_4.locations.append(Floor_4_Payment_12)


    if "5" in world.options.Floors.value:
        Floor_5_Payment_1 = LBALLocation(
            world.player, "Floor 5 Payment 1", world.location_name_to_id["Floor 5 Payment 1"], Floor_5
        )

        Floor_5.locations.append(Floor_5_Payment_1)

    if "5" in world.options.Floors.value:
        Floor_5_Payment_2 = LBALLocation(
            world.player, "Floor 5 Payment 2", world.location_name_to_id["Floor 5 Payment 2"], Floor_5
        )

        Floor_5.locations.append(Floor_5_Payment_2)

    if "5" in world.options.Floors.value:
        Floor_5_Payment_3 = LBALLocation(
            world.player, "Floor 5 Payment 3", world.location_name_to_id["Floor 5 Payment 3"], Floor_5
        )

        Floor_5.locations.append(Floor_5_Payment_3)

    if "5" in world.options.Floors.value:
        Floor_5_Payment_4 = LBALLocation(
            world.player, "Floor 5 Payment 4", world.location_name_to_id["Floor 5 Payment 4"], Floor_5
        )

        Floor_5.locations.append(Floor_5_Payment_4)

    if "5" in world.options.Floors.value:
        Floor_5_Payment_5 = LBALLocation(
            world.player, "Floor 5 Payment 5", world.location_name_to_id["Floor 5 Payment 5"], Floor_5
        )

        Floor_5.locations.append(Floor_5_Payment_5)

    if "5" in world.options.Floors.value:
        Floor_5_Payment_6 = LBALLocation(
            world.player, "Floor 5 Payment 6", world.location_name_to_id["Floor 5 Payment 6"], Floor_5
        )

        Floor_5.locations.append(Floor_5_Payment_6)

    if "5" in world.options.Floors.value:
        Floor_5_Payment_7 = LBALLocation(
            world.player, "Floor 5 Payment 7", world.location_name_to_id["Floor 5 Payment 7"], Floor_5
        )

        Floor_5.locations.append(Floor_5_Payment_7)

    if "5" in world.options.Floors.value:
        Floor_5_Payment_8 = LBALLocation(
            world.player, "Floor 5 Payment 8", world.location_name_to_id["Floor 5 Payment 8"], Floor_5
        )

        Floor_5.locations.append(Floor_5_Payment_8)

    if "5" in world.options.Floors.value:
        Floor_5_Payment_9 = LBALLocation(
            world.player, "Floor 5 Payment 9", world.location_name_to_id["Floor 5 Payment 9"], Floor_5
        )

        Floor_5.locations.append(Floor_5_Payment_9)

    if "5" in world.options.Floors.value:
        Floor_5_Payment_10 = LBALLocation(
            world.player, "Floor 5 Payment 10", world.location_name_to_id["Floor 5 Payment 10"], Floor_5
        )

        Floor_5.locations.append(Floor_5_Payment_10)

    if "5" in world.options.Floors.value:
        Floor_5_Payment_11 = LBALLocation(
            world.player, "Floor 5 Payment 11", world.location_name_to_id["Floor 5 Payment 11"], Floor_5
        )

        Floor_5.locations.append(Floor_5_Payment_11)

    if "5" in world.options.Floors.value:
        Floor_5_Payment_12 = LBALLocation(
            world.player, "Floor 5 Payment 12", world.location_name_to_id["Floor 5 Payment 12"], Floor_5
        )

        Floor_5.locations.append(Floor_5_Payment_12)

    if "6" in world.options.Floors.value:
        Floor_6_Payment_1 = LBALLocation(
            world.player, "Floor 6 Payment 1", world.location_name_to_id["Floor 6 Payment 1"], Floor_6
        )

        Floor_6.locations.append(Floor_6_Payment_1)

    if "6" in world.options.Floors.value:
        Floor_6_Payment_2 = LBALLocation(
            world.player, "Floor 6 Payment 2", world.location_name_to_id["Floor 6 Payment 2"], Floor_6
        )

        Floor_6.locations.append(Floor_6_Payment_2)

    if "6" in world.options.Floors.value:
        Floor_6_Payment_3 = LBALLocation(
            world.player, "Floor 6 Payment 3", world.location_name_to_id["Floor 6 Payment 3"], Floor_6
        )

        Floor_6.locations.append(Floor_6_Payment_3)

    if "6" in world.options.Floors.value:
        Floor_6_Payment_4 = LBALLocation(
            world.player, "Floor 6 Payment 4", world.location_name_to_id["Floor 6 Payment 4"], Floor_6
        )

        Floor_6.locations.append(Floor_6_Payment_4)

    if "6" in world.options.Floors.value:
        Floor_6_Payment_5 = LBALLocation(
            world.player, "Floor 6 Payment 5", world.location_name_to_id["Floor 6 Payment 5"], Floor_6
        )

        Floor_6.locations.append(Floor_6_Payment_5)

    if "6" in world.options.Floors.value:
        Floor_6_Payment_6 = LBALLocation(
            world.player, "Floor 6 Payment 6", world.location_name_to_id["Floor 6 Payment 6"], Floor_6
        )

        Floor_6.locations.append(Floor_6_Payment_6)

    if "6" in world.options.Floors.value:
        Floor_6_Payment_7 = LBALLocation(
            world.player, "Floor 6 Payment 7", world.location_name_to_id["Floor 6 Payment 7"], Floor_6
        )

        Floor_6.locations.append(Floor_6_Payment_7)

    if "6" in world.options.Floors.value:
        Floor_6_Payment_8 = LBALLocation(
            world.player, "Floor 6 Payment 8", world.location_name_to_id["Floor 6 Payment 8"], Floor_6
        )

        Floor_6.locations.append(Floor_6_Payment_8)

    if "6" in world.options.Floors.value:
        Floor_6_Payment_9 = LBALLocation(
            world.player, "Floor 6 Payment 9", world.location_name_to_id["Floor 6 Payment 9"], Floor_6
        )

        Floor_6.locations.append(Floor_6_Payment_9)

    if "6" in world.options.Floors.value:
        Floor_6_Payment_10 = LBALLocation(
            world.player, "Floor 6 Payment 10", world.location_name_to_id["Floor 6 Payment 10"], Floor_6
        )

        Floor_6.locations.append(Floor_6_Payment_10)

    if "6" in world.options.Floors.value:
        Floor_6_Payment_11 = LBALLocation(
            world.player, "Floor 6 Payment 11", world.location_name_to_id["Floor 6 Payment 11"], Floor_6
        )

        Floor_6.locations.append(Floor_6_Payment_11)

    if "6" in world.options.Floors.value:
        Floor_6_Payment_12 = LBALLocation(
            world.player, "Floor 6 Payment 12", world.location_name_to_id["Floor 6 Payment 12"], Floor_6
        )

        Floor_6.locations.append(Floor_6_Payment_12)

    if "7" in world.options.Floors.value:
        Floor_7_Payment_1 = LBALLocation(
            world.player, "Floor 7 Payment 1", world.location_name_to_id["Floor 7 Payment 1"], Floor_7
        )

        Floor_7.locations.append(Floor_7_Payment_1)

    if "7" in world.options.Floors.value:
        Floor_7_Payment_2 = LBALLocation(
            world.player, "Floor 7 Payment 2", world.location_name_to_id["Floor 7 Payment 2"], Floor_7
        )

        Floor_7.locations.append(Floor_7_Payment_2)

    if "7" in world.options.Floors.value:
        Floor_7_Payment_3 = LBALLocation(
            world.player, "Floor 7 Payment 3", world.location_name_to_id["Floor 7 Payment 3"], Floor_7
        )

        Floor_7.locations.append(Floor_7_Payment_3)

    if "7" in world.options.Floors.value:
        Floor_7_Payment_4 = LBALLocation(
            world.player, "Floor 7 Payment 4", world.location_name_to_id["Floor 7 Payment 4"], Floor_7
        )

        Floor_7.locations.append(Floor_7_Payment_4)

    if "7" in world.options.Floors.value:
        Floor_7_Payment_5 = LBALLocation(
            world.player, "Floor 7 Payment 5", world.location_name_to_id["Floor 7 Payment 5"], Floor_7
        )

        Floor_7.locations.append(Floor_7_Payment_5)

    if "7" in world.options.Floors.value:
        Floor_7_Payment_6 = LBALLocation(
            world.player, "Floor 7 Payment 6", world.location_name_to_id["Floor 7 Payment 6"], Floor_7
        )

        Floor_7.locations.append(Floor_7_Payment_6)

    if "7" in world.options.Floors.value:
        Floor_7_Payment_7 = LBALLocation(
            world.player, "Floor 7 Payment 7", world.location_name_to_id["Floor 7 Payment 7"], Floor_7
        )

        Floor_7.locations.append(Floor_7_Payment_7)

    if "7" in world.options.Floors.value:
        Floor_7_Payment_8 = LBALLocation(
            world.player, "Floor 7 Payment 8", world.location_name_to_id["Floor 7 Payment 8"], Floor_7
        )

        Floor_7.locations.append(Floor_7_Payment_8)

    if "7" in world.options.Floors.value:
        Floor_7_Payment_9 = LBALLocation(
            world.player, "Floor 7 Payment 9", world.location_name_to_id["Floor 7 Payment 9"], Floor_7
        )

        Floor_7.locations.append(Floor_7_Payment_9)

    if "7" in world.options.Floors.value:
        Floor_7_Payment_10 = LBALLocation(
            world.player, "Floor 7 Payment 10", world.location_name_to_id["Floor 7 Payment 10"], Floor_7
        )

        Floor_7.locations.append(Floor_7_Payment_10)

    if "7" in world.options.Floors.value:
        Floor_7_Payment_11 = LBALLocation(
            world.player, "Floor 7 Payment 11", world.location_name_to_id["Floor 7 Payment 11"], Floor_7
        )

        Floor_7.locations.append(Floor_7_Payment_11)

    if "7" in world.options.Floors.value:
        Floor_7_Payment_12 = LBALLocation(
            world.player, "Floor 7 Payment 12", world.location_name_to_id["Floor 7 Payment 12"], Floor_7
        )

        Floor_7.locations.append(Floor_7_Payment_12)

    if "8" in world.options.Floors.value:
        Floor_8_Payment_1 = LBALLocation(
            world.player, "Floor 8 Payment 1", world.location_name_to_id["Floor 8 Payment 1"], Floor_8
        )

        Floor_8.locations.append(Floor_8_Payment_1)

    if "8" in world.options.Floors.value:
        Floor_8_Payment_2 = LBALLocation(
            world.player, "Floor 8 Payment 2", world.location_name_to_id["Floor 8 Payment 2"], Floor_8
        )

        Floor_8.locations.append(Floor_8_Payment_2)

    if "8" in world.options.Floors.value:
        Floor_8_Payment_3 = LBALLocation(
            world.player, "Floor 8 Payment 3", world.location_name_to_id["Floor 8 Payment 3"], Floor_8
        )

        Floor_8.locations.append(Floor_8_Payment_3)

    if "8" in world.options.Floors.value:
        Floor_8_Payment_4 = LBALLocation(
            world.player, "Floor 8 Payment 4", world.location_name_to_id["Floor 8 Payment 4"], Floor_8
        )

        Floor_8.locations.append(Floor_8_Payment_4)

    if "8" in world.options.Floors.value:
        Floor_8_Payment_5 = LBALLocation(
            world.player, "Floor 8 Payment 5", world.location_name_to_id["Floor 8 Payment 5"], Floor_8
        )

        Floor_8.locations.append(Floor_8_Payment_5)

    if "8" in world.options.Floors.value:
        Floor_8_Payment_6 = LBALLocation(
            world.player, "Floor 8 Payment 6", world.location_name_to_id["Floor 8 Payment 6"], Floor_8
        )

        Floor_8.locations.append(Floor_8_Payment_6)

    if "8" in world.options.Floors.value:
        Floor_8_Payment_7 = LBALLocation(
            world.player, "Floor 8 Payment 7", world.location_name_to_id["Floor 8 Payment 7"], Floor_8
        )

        Floor_8.locations.append(Floor_8_Payment_7)

    if "8" in world.options.Floors.value:
        Floor_8_Payment_8 = LBALLocation(
            world.player, "Floor 8 Payment 8", world.location_name_to_id["Floor 8 Payment 8"], Floor_8
        )

        Floor_8.locations.append(Floor_8_Payment_8)

    if "8" in world.options.Floors.value:
        Floor_8_Payment_9 = LBALLocation(
            world.player, "Floor 8 Payment 9", world.location_name_to_id["Floor 8 Payment 9"], Floor_8
        )

        Floor_8.locations.append(Floor_8_Payment_9)

    if "8" in world.options.Floors.value:
        Floor_8_Payment_10 = LBALLocation(
            world.player, "Floor 8 Payment 10", world.location_name_to_id["Floor 8 Payment 10"], Floor_8
        )

        Floor_8.locations.append(Floor_8_Payment_10)

    if "8" in world.options.Floors.value:
        Floor_8_Payment_11 = LBALLocation(
            world.player, "Floor 8 Payment 11", world.location_name_to_id["Floor 8 Payment 11"], Floor_8
        )

        Floor_8.locations.append(Floor_8_Payment_11)

    if "8" in world.options.Floors.value:
        Floor_8_Payment_12 = LBALLocation(
            world.player, "Floor 8 Payment 12", world.location_name_to_id["Floor 8 Payment 12"], Floor_8
        )

        Floor_8.locations.append(Floor_8_Payment_12)

    if "9" in world.options.Floors.value:
        Floor_9_Payment_1 = LBALLocation(
            world.player, "Floor 9 Payment 1", world.location_name_to_id["Floor 9 Payment 1"], Floor_9
        )

        Floor_9.locations.append(Floor_9_Payment_1)

    if "9" in world.options.Floors.value:
        Floor_9_Payment_2 = LBALLocation(
            world.player, "Floor 9 Payment 2", world.location_name_to_id["Floor 9 Payment 2"], Floor_9
        )

        Floor_9.locations.append(Floor_9_Payment_2)

    if "9" in world.options.Floors.value:
        Floor_9_Payment_3 = LBALLocation(
            world.player, "Floor 9 Payment 3", world.location_name_to_id["Floor 9 Payment 3"], Floor_9
        )

        Floor_9.locations.append(Floor_9_Payment_3)

    if "9" in world.options.Floors.value:
        Floor_9_Payment_4 = LBALLocation(
            world.player, "Floor 9 Payment 4", world.location_name_to_id["Floor 9 Payment 4"], Floor_9
        )

        Floor_9.locations.append(Floor_9_Payment_4)

    if "9" in world.options.Floors.value:
        Floor_9_Payment_5 = LBALLocation(
            world.player, "Floor 9 Payment 5", world.location_name_to_id["Floor 9 Payment 5"], Floor_9
        )

        Floor_9.locations.append(Floor_9_Payment_5)

    if "9" in world.options.Floors.value:
        Floor_9_Payment_6 = LBALLocation(
            world.player, "Floor 9 Payment 6", world.location_name_to_id["Floor 9 Payment 6"], Floor_9
        )

        Floor_9.locations.append(Floor_9_Payment_6)

    if "9" in world.options.Floors.value:
        Floor_9_Payment_7 = LBALLocation(
            world.player, "Floor 9 Payment 7", world.location_name_to_id["Floor 9 Payment 7"], Floor_9
        )

        Floor_9.locations.append(Floor_9_Payment_7)

    if "9" in world.options.Floors.value:
        Floor_9_Payment_8 = LBALLocation(
            world.player, "Floor 9 Payment 8", world.location_name_to_id["Floor 9 Payment 8"], Floor_9
        )

        Floor_9.locations.append(Floor_9_Payment_8)

    if "9" in world.options.Floors.value:
        Floor_9_Payment_9 = LBALLocation(
            world.player, "Floor 9 Payment 9", world.location_name_to_id["Floor 9 Payment 9"], Floor_9
        )

        Floor_9.locations.append(Floor_9_Payment_9)

    if "9" in world.options.Floors.value:
        Floor_9_Payment_10 = LBALLocation(
            world.player, "Floor 9 Payment 10", world.location_name_to_id["Floor 9 Payment 10"], Floor_9
        )

        Floor_9.locations.append(Floor_9_Payment_10)

    if "9" in world.options.Floors.value:
        Floor_9_Payment_11 = LBALLocation(
            world.player, "Floor 9 Payment 11", world.location_name_to_id["Floor 9 Payment 11"], Floor_9
        )

        Floor_9.locations.append(Floor_9_Payment_11)

    if "9" in world.options.Floors.value:
        Floor_9_Payment_12 = LBALLocation(
            world.player, "Floor 9 Payment 12", world.location_name_to_id["Floor 9 Payment 12"], Floor_9
        )

        Floor_9.locations.append(Floor_9_Payment_12)

    if "10" in world.options.Floors.value:
        Floor_10_Payment_1 = LBALLocation(
            world.player, "Floor 10 Payment 1", world.location_name_to_id["Floor 10 Payment 1"], Floor_10
        )

        Floor_10.locations.append(Floor_10_Payment_1)

    if "10" in world.options.Floors.value:
        Floor_10_Payment_2 = LBALLocation(
            world.player, "Floor 10 Payment 2", world.location_name_to_id["Floor 10 Payment 2"], Floor_10
        )

        Floor_10.locations.append(Floor_10_Payment_2)

    if "10" in world.options.Floors.value:
        Floor_10_Payment_3 = LBALLocation(
            world.player, "Floor 10 Payment 3", world.location_name_to_id["Floor 10 Payment 3"], Floor_10
        )

        Floor_10.locations.append(Floor_10_Payment_3)

    if "10" in world.options.Floors.value:
        Floor_10_Payment_4 = LBALLocation(
            world.player, "Floor 10 Payment 4", world.location_name_to_id["Floor 10 Payment 4"], Floor_10
        )

        Floor_10.locations.append(Floor_10_Payment_4)

    if "10" in world.options.Floors.value:
        Floor_10_Payment_5 = LBALLocation(
            world.player, "Floor 10 Payment 5", world.location_name_to_id["Floor 10 Payment 5"], Floor_10
        )

        Floor_10.locations.append(Floor_10_Payment_5)

    if "10" in world.options.Floors.value:
        Floor_10_Payment_6 = LBALLocation(
            world.player, "Floor 10 Payment 6", world.location_name_to_id["Floor 10 Payment 6"], Floor_10
        )

        Floor_10.locations.append(Floor_10_Payment_6)

    if "10" in world.options.Floors.value:
        Floor_10_Payment_7 = LBALLocation(
            world.player, "Floor 10 Payment 7", world.location_name_to_id["Floor 10 Payment 7"], Floor_10
        )

        Floor_10.locations.append(Floor_10_Payment_7)

    if "10" in world.options.Floors.value:
        Floor_10_Payment_8 = LBALLocation(
            world.player, "Floor 10 Payment 8", world.location_name_to_id["Floor 10 Payment 8"], Floor_10
        )

        Floor_10.locations.append(Floor_10_Payment_8)

    if "10" in world.options.Floors.value:
        Floor_10_Payment_9 = LBALLocation(
            world.player, "Floor 10 Payment 9", world.location_name_to_id["Floor 10 Payment 9"], Floor_10
        )

        Floor_10.locations.append(Floor_10_Payment_9)

    if "10" in world.options.Floors.value:
        Floor_10_Payment_10 = LBALLocation(
            world.player, "Floor 10 Payment 10", world.location_name_to_id["Floor 10 Payment 10"], Floor_10
        )

        Floor_10.locations.append(Floor_10_Payment_10)

    if "10" in world.options.Floors.value:
        Floor_10_Payment_11 = LBALLocation(
            world.player, "Floor 10 Payment 11", world.location_name_to_id["Floor 10 Payment 11"], Floor_10
        )

        Floor_10.locations.append(Floor_10_Payment_11)

    if "10" in world.options.Floors.value:
        Floor_10_Payment_12 = LBALLocation(
            world.player, "Floor 10 Payment 12", world.location_name_to_id["Floor 10 Payment 12"], Floor_10
        )

        Floor_10.locations.append(Floor_10_Payment_12)

    if "11" in world.options.Floors.value:
        Floor_11_Payment_1 = LBALLocation(
            world.player, "Floor 11 Payment 1", world.location_name_to_id["Floor 11 Payment 1"], Floor_11
        )

        Floor_11.locations.append(Floor_11_Payment_1)

    if "11" in world.options.Floors.value:
        Floor_11_Payment_2 = LBALLocation(
            world.player, "Floor 11 Payment 2", world.location_name_to_id["Floor 11 Payment 2"], Floor_11
        )

        Floor_11.locations.append(Floor_11_Payment_2)

    if "11" in world.options.Floors.value:
        Floor_11_Payment_3 = LBALLocation(
            world.player, "Floor 11 Payment 3", world.location_name_to_id["Floor 11 Payment 3"], Floor_11
        )

        Floor_11.locations.append(Floor_11_Payment_3)

    if "11" in world.options.Floors.value:
        Floor_11_Payment_4 = LBALLocation(
            world.player, "Floor 11 Payment 4", world.location_name_to_id["Floor 11 Payment 4"], Floor_11
        )

        Floor_11.locations.append(Floor_11_Payment_4)

    if "11" in world.options.Floors.value:
        Floor_11_Payment_5 = LBALLocation(
            world.player, "Floor 11 Payment 5", world.location_name_to_id["Floor 11 Payment 5"], Floor_11
        )

        Floor_11.locations.append(Floor_11_Payment_5)

    if "11" in world.options.Floors.value:
        Floor_11_Payment_6 = LBALLocation(
            world.player, "Floor 11 Payment 6", world.location_name_to_id["Floor 11 Payment 6"], Floor_11
        )

        Floor_11.locations.append(Floor_11_Payment_6)

    if "11" in world.options.Floors.value:
        Floor_11_Payment_7 = LBALLocation(
            world.player, "Floor 11 Payment 7", world.location_name_to_id["Floor 11 Payment 7"], Floor_11
        )

        Floor_11.locations.append(Floor_11_Payment_7)

    if "11" in world.options.Floors.value:
        Floor_11_Payment_8 = LBALLocation(
            world.player, "Floor 11 Payment 8", world.location_name_to_id["Floor 11 Payment 8"], Floor_11
        )

        Floor_11.locations.append(Floor_11_Payment_8)

    if "11" in world.options.Floors.value:
        Floor_11_Payment_9 = LBALLocation(
            world.player, "Floor 11 Payment 9", world.location_name_to_id["Floor 11 Payment 9"], Floor_11
        )

        Floor_11.locations.append(Floor_11_Payment_9)

    if "11" in world.options.Floors.value:
        Floor_11_Payment_10 = LBALLocation(
            world.player, "Floor 11 Payment 10", world.location_name_to_id["Floor 11 Payment 10"], Floor_11
        )

        Floor_11.locations.append(Floor_11_Payment_10)

    if "11" in world.options.Floors.value:
        Floor_11_Payment_11 = LBALLocation(
            world.player, "Floor 11 Payment 11", world.location_name_to_id["Floor 11 Payment 11"], Floor_11
        )

        Floor_11.locations.append(Floor_11_Payment_11)

    if "11" in world.options.Floors.value:
        Floor_11_Payment_12 = LBALLocation(
            world.player, "Floor 11 Payment 12", world.location_name_to_id["Floor 11 Payment 12"], Floor_11
        )

        Floor_11.locations.append(Floor_11_Payment_12)


    if "12" in world.options.Floors.value:
        Floor_12_Payment_1 = LBALLocation(
            world.player, "Floor 12 Payment 1", world.location_name_to_id["Floor 12 Payment 1"], Floor_12
        )

        Floor_12.locations.append(Floor_12_Payment_1)

    if "12" in world.options.Floors.value:
        Floor_12_Payment_2 = LBALLocation(
            world.player, "Floor 12 Payment 2", world.location_name_to_id["Floor 12 Payment 2"], Floor_12
        )

        Floor_12.locations.append(Floor_12_Payment_2)

    if "12" in world.options.Floors.value:
        Floor_12_Payment_3 = LBALLocation(
            world.player, "Floor 12 Payment 3", world.location_name_to_id["Floor 12 Payment 3"], Floor_12
        )

        Floor_12.locations.append(Floor_12_Payment_3)

    if "12" in world.options.Floors.value:
        Floor_12_Payment_4 = LBALLocation(
            world.player, "Floor 12 Payment 4", world.location_name_to_id["Floor 12 Payment 4"], Floor_12
        )

        Floor_12.locations.append(Floor_12_Payment_4)

    if "12" in world.options.Floors.value:
        Floor_12_Payment_5 = LBALLocation(
            world.player, "Floor 12 Payment 5", world.location_name_to_id["Floor 12 Payment 5"], Floor_12
        )

        Floor_12.locations.append(Floor_12_Payment_5)

    if "12" in world.options.Floors.value:
        Floor_12_Payment_6 = LBALLocation(
            world.player, "Floor 12 Payment 6", world.location_name_to_id["Floor 12 Payment 6"], Floor_12
        )

        Floor_12.locations.append(Floor_12_Payment_6)

    if "12" in world.options.Floors.value:
        Floor_12_Payment_7 = LBALLocation(
            world.player, "Floor 12 Payment 7", world.location_name_to_id["Floor 12 Payment 7"], Floor_12
        )

        Floor_12.locations.append(Floor_12_Payment_7)

    if "12" in world.options.Floors.value:
        Floor_12_Payment_8 = LBALLocation(
            world.player, "Floor 12 Payment 8", world.location_name_to_id["Floor 12 Payment 8"], Floor_12
        )

        Floor_12.locations.append(Floor_12_Payment_8)

    if "12" in world.options.Floors.value:
        Floor_12_Payment_9 = LBALLocation(
            world.player, "Floor 12 Payment 9", world.location_name_to_id["Floor 12 Payment 9"], Floor_12
        )

        Floor_12.locations.append(Floor_12_Payment_9)

    if "12" in world.options.Floors.value:
        Floor_12_Payment_10 = LBALLocation(
            world.player, "Floor 12 Payment 10", world.location_name_to_id["Floor 12 Payment 10"], Floor_12
        )

        Floor_12.locations.append(Floor_12_Payment_10)

    if "12" in world.options.Floors.value:
        Floor_12_Payment_11 = LBALLocation(
            world.player, "Floor 12 Payment 11", world.location_name_to_id["Floor 12 Payment 11"], Floor_12
        )

        Floor_12.locations.append(Floor_12_Payment_11)

    if "12" in world.options.Floors.value:
        Floor_12_Payment_12 = LBALLocation(
            world.player, "Floor 12 Payment 12", world.location_name_to_id["Floor 12 Payment 12"], Floor_12
        )

        Floor_12.locations.append(Floor_12_Payment_12)

    if "13" in world.options.Floors.value:
        Floor_13_Payment_1 = LBALLocation(
            world.player, "Floor 13 Payment 1", world.location_name_to_id["Floor 13 Payment 1"], Floor_13
        )

        Floor_13.locations.append(Floor_13_Payment_1)

    if "13" in world.options.Floors.value:
        Floor_13_Payment_2 = LBALLocation(
            world.player, "Floor 13 Payment 2", world.location_name_to_id["Floor 13 Payment 2"], Floor_13
        )

        Floor_13.locations.append(Floor_13_Payment_2)

    if "13" in world.options.Floors.value:
        Floor_13_Payment_3 = LBALLocation(
            world.player, "Floor 13 Payment 3", world.location_name_to_id["Floor 13 Payment 3"], Floor_13
        )

        Floor_13.locations.append(Floor_13_Payment_3)

    if "13" in world.options.Floors.value:
        Floor_13_Payment_4 = LBALLocation(
            world.player, "Floor 13 Payment 4", world.location_name_to_id["Floor 13 Payment 4"], Floor_13
        )

        Floor_13.locations.append(Floor_13_Payment_4)

    if "13" in world.options.Floors.value:
        Floor_13_Payment_5 = LBALLocation(
            world.player, "Floor 13 Payment 5", world.location_name_to_id["Floor 13 Payment 5"], Floor_13
        )

        Floor_13.locations.append(Floor_13_Payment_5)

    if "13" in world.options.Floors.value:
        Floor_13_Payment_6 = LBALLocation(
            world.player, "Floor 13 Payment 6", world.location_name_to_id["Floor 13 Payment 6"], Floor_13
        )

        Floor_13.locations.append(Floor_13_Payment_6)

    if "13" in world.options.Floors.value:
        Floor_13_Payment_7 = LBALLocation(
            world.player, "Floor 13 Payment 7", world.location_name_to_id["Floor 13 Payment 7"], Floor_13
        )

        Floor_13.locations.append(Floor_13_Payment_7)

    if "13" in world.options.Floors.value:
        Floor_13_Payment_8 = LBALLocation(
            world.player, "Floor 13 Payment 8", world.location_name_to_id["Floor 13 Payment 8"], Floor_13
        )

        Floor_13.locations.append(Floor_13_Payment_8)

    if "13" in world.options.Floors.value:
        Floor_13_Payment_9 = LBALLocation(
            world.player, "Floor 13 Payment 9", world.location_name_to_id["Floor 13 Payment 9"], Floor_13
        )

        Floor_13.locations.append(Floor_13_Payment_9)

    if "13" in world.options.Floors.value:
        Floor_13_Payment_10 = LBALLocation(
            world.player, "Floor 13 Payment 10", world.location_name_to_id["Floor 13 Payment 10"], Floor_13
        )

        Floor_13.locations.append(Floor_13_Payment_10)

    if "13" in world.options.Floors.value:
        Floor_13_Payment_11 = LBALLocation(
            world.player, "Floor 13 Payment 11", world.location_name_to_id["Floor 13 Payment 11"], Floor_13
        )

        Floor_13.locations.append(Floor_13_Payment_11)

    if "13" in world.options.Floors.value:
        Floor_13_Payment_12 = LBALLocation(
            world.player, "Floor 13 Payment 12", world.location_name_to_id["Floor 13 Payment 12"], Floor_13
        )

        Floor_13.locations.append(Floor_13_Payment_12)


    if "14" in world.options.Floors.value:
        Floor_14_Payment_1 = LBALLocation(
            world.player, "Floor 14 Payment 1", world.location_name_to_id["Floor 14 Payment 1"], Floor_14
        )

        Floor_14.locations.append(Floor_14_Payment_1)

    if "14" in world.options.Floors.value:
        Floor_14_Payment_2 = LBALLocation(
            world.player, "Floor 14 Payment 2", world.location_name_to_id["Floor 14 Payment 2"], Floor_14
        )

        Floor_14.locations.append(Floor_14_Payment_2)

    if "14" in world.options.Floors.value:
        Floor_14_Payment_3 = LBALLocation(
            world.player, "Floor 14 Payment 3", world.location_name_to_id["Floor 14 Payment 3"], Floor_14
        )

        Floor_14.locations.append(Floor_14_Payment_3)

    if "14" in world.options.Floors.value:
        Floor_14_Payment_4 = LBALLocation(
            world.player, "Floor 14 Payment 4", world.location_name_to_id["Floor 14 Payment 4"], Floor_14
        )

        Floor_14.locations.append(Floor_14_Payment_4)

    if "14" in world.options.Floors.value:
        Floor_14_Payment_5 = LBALLocation(
            world.player, "Floor 14 Payment 5", world.location_name_to_id["Floor 14 Payment 5"], Floor_14
        )

        Floor_14.locations.append(Floor_14_Payment_5)

    if "14" in world.options.Floors.value:
        Floor_14_Payment_6 = LBALLocation(
            world.player, "Floor 14 Payment 6", world.location_name_to_id["Floor 14 Payment 6"], Floor_14
        )

        Floor_14.locations.append(Floor_14_Payment_6)

    if "14" in world.options.Floors.value:
        Floor_14_Payment_7 = LBALLocation(
            world.player, "Floor 14 Payment 7", world.location_name_to_id["Floor 14 Payment 7"], Floor_14
        )

        Floor_14.locations.append(Floor_14_Payment_7)

    if "14" in world.options.Floors.value:
        Floor_14_Payment_8 = LBALLocation(
            world.player, "Floor 14 Payment 8", world.location_name_to_id["Floor 14 Payment 8"], Floor_14
        )

        Floor_14.locations.append(Floor_14_Payment_8)

    if "14" in world.options.Floors.value:
        Floor_14_Payment_9 = LBALLocation(
            world.player, "Floor 14 Payment 9", world.location_name_to_id["Floor 14 Payment 9"], Floor_14
        )

        Floor_14.locations.append(Floor_14_Payment_9)

    if "14" in world.options.Floors.value:
        Floor_14_Payment_10 = LBALLocation(
            world.player, "Floor 14 Payment 10", world.location_name_to_id["Floor 14 Payment 10"], Floor_14
        )

        Floor_14.locations.append(Floor_14_Payment_10)

    if "14" in world.options.Floors.value:
        Floor_14_Payment_11 = LBALLocation(
            world.player, "Floor 14 Payment 11", world.location_name_to_id["Floor 14 Payment 11"], Floor_14
        )

        Floor_14.locations.append(Floor_14_Payment_11)

    if "14" in world.options.Floors.value:
        Floor_14_Payment_12 = LBALLocation(
            world.player, "Floor 14 Payment 12", world.location_name_to_id["Floor 14 Payment 12"], Floor_14
        )

        Floor_14.locations.append(Floor_14_Payment_12)

    if "15" in world.options.Floors.value:
        Floor_15_Payment_1 = LBALLocation(
            world.player, "Floor 15 Payment 1", world.location_name_to_id["Floor 15 Payment 1"], Floor_15
        )

        Floor_15.locations.append(Floor_15_Payment_1)

    if "15" in world.options.Floors.value:
        Floor_15_Payment_2 = LBALLocation(
            world.player, "Floor 15 Payment 2", world.location_name_to_id["Floor 15 Payment 2"], Floor_15
        )

        Floor_15.locations.append(Floor_15_Payment_2)

    if "15" in world.options.Floors.value:
        Floor_15_Payment_3 = LBALLocation(
            world.player, "Floor 15 Payment 3", world.location_name_to_id["Floor 15 Payment 3"], Floor_15
        )

        Floor_15.locations.append(Floor_15_Payment_3)

    if "15" in world.options.Floors.value:
        Floor_15_Payment_4 = LBALLocation(
            world.player, "Floor 15 Payment 4", world.location_name_to_id["Floor 15 Payment 4"], Floor_15
        )

        Floor_15.locations.append(Floor_15_Payment_4)

    if "15" in world.options.Floors.value:
        Floor_15_Payment_5 = LBALLocation(
            world.player, "Floor 15 Payment 5", world.location_name_to_id["Floor 15 Payment 5"], Floor_15
        )

        Floor_15.locations.append(Floor_15_Payment_5)

    if "15" in world.options.Floors.value:
        Floor_15_Payment_6 = LBALLocation(
            world.player, "Floor 15 Payment 6", world.location_name_to_id["Floor 15 Payment 6"], Floor_15
        )

        Floor_15.locations.append(Floor_15_Payment_6)

    if "15" in world.options.Floors.value:
        Floor_15_Payment_7 = LBALLocation(
            world.player, "Floor 15 Payment 7", world.location_name_to_id["Floor 15 Payment 7"], Floor_15
        )

        Floor_15.locations.append(Floor_15_Payment_7)

    if "15" in world.options.Floors.value:
        Floor_15_Payment_8 = LBALLocation(
            world.player, "Floor 15 Payment 8", world.location_name_to_id["Floor 15 Payment 8"], Floor_15
        )

        Floor_15.locations.append(Floor_15_Payment_8)

    if "15" in world.options.Floors.value:
        Floor_15_Payment_9 = LBALLocation(
            world.player, "Floor 15 Payment 9", world.location_name_to_id["Floor 15 Payment 9"], Floor_15
        )

        Floor_15.locations.append(Floor_15_Payment_9)

    if "15" in world.options.Floors.value:
        Floor_15_Payment_10 = LBALLocation(
            world.player, "Floor 15 Payment 10", world.location_name_to_id["Floor 15 Payment 10"], Floor_15
        )

        Floor_15.locations.append(Floor_15_Payment_10)

    if "15" in world.options.Floors.value:
        Floor_15_Payment_11 = LBALLocation(
            world.player, "Floor 15 Payment 11", world.location_name_to_id["Floor 15 Payment 11"], Floor_15
        )

        Floor_15.locations.append(Floor_15_Payment_11)

    if "15" in world.options.Floors.value:
        Floor_15_Payment_12 = LBALLocation(
            world.player, "Floor 15 Payment 12", world.location_name_to_id["Floor 15 Payment 12"], Floor_15
        )

        Floor_15.locations.append(Floor_15_Payment_12)

    if "16" in world.options.Floors.value:
        Floor_16_Payment_1 = LBALLocation(
            world.player, "Floor 16 Payment 1", world.location_name_to_id["Floor 16 Payment 1"], Floor_16
        )

        Floor_16.locations.append(Floor_16_Payment_1)

    if "16" in world.options.Floors.value:
        Floor_16_Payment_2 = LBALLocation(
            world.player, "Floor 16 Payment 2", world.location_name_to_id["Floor 16 Payment 2"], Floor_16
        )

        Floor_16.locations.append(Floor_16_Payment_2)

    if "16" in world.options.Floors.value:
        Floor_16_Payment_3 = LBALLocation(
            world.player, "Floor 16 Payment 3", world.location_name_to_id["Floor 16 Payment 3"], Floor_16
        )

        Floor_16.locations.append(Floor_16_Payment_3)

    if "16" in world.options.Floors.value:
        Floor_16_Payment_4 = LBALLocation(
            world.player, "Floor 16 Payment 4", world.location_name_to_id["Floor 16 Payment 4"], Floor_16
        )

        Floor_16.locations.append(Floor_16_Payment_4)

    if "16" in world.options.Floors.value:
        Floor_16_Payment_5 = LBALLocation(
            world.player, "Floor 16 Payment 5", world.location_name_to_id["Floor 16 Payment 5"], Floor_16
        )

        Floor_16.locations.append(Floor_16_Payment_5)

    if "16" in world.options.Floors.value:
        Floor_16_Payment_6 = LBALLocation(
            world.player, "Floor 16 Payment 6", world.location_name_to_id["Floor 16 Payment 6"], Floor_16
        )

        Floor_16.locations.append(Floor_16_Payment_6)

    if "16" in world.options.Floors.value:
        Floor_16_Payment_7 = LBALLocation(
            world.player, "Floor 16 Payment 7", world.location_name_to_id["Floor 16 Payment 7"], Floor_16
        )

        Floor_16.locations.append(Floor_16_Payment_7)

    if "16" in world.options.Floors.value:
        Floor_16_Payment_8 = LBALLocation(
            world.player, "Floor 16 Payment 8", world.location_name_to_id["Floor 16 Payment 8"], Floor_16
        )

        Floor_16.locations.append(Floor_16_Payment_8)

    if "16" in world.options.Floors.value:
        Floor_16_Payment_9 = LBALLocation(
            world.player, "Floor 16 Payment 9", world.location_name_to_id["Floor 16 Payment 9"], Floor_16
        )

        Floor_16.locations.append(Floor_16_Payment_9)

    if "16" in world.options.Floors.value:
        Floor_16_Payment_10 = LBALLocation(
            world.player, "Floor 16 Payment 10", world.location_name_to_id["Floor 16 Payment 10"], Floor_16
        )

        Floor_16.locations.append(Floor_16_Payment_10)

    if "16" in world.options.Floors.value:
        Floor_16_Payment_11 = LBALLocation(
            world.player, "Floor 16 Payment 11", world.location_name_to_id["Floor 16 Payment 11"], Floor_16
        )

        Floor_16.locations.append(Floor_16_Payment_11)

    if "16" in world.options.Floors.value:
        Floor_16_Payment_12 = LBALLocation(
            world.player, "Floor 16 Payment 12", world.location_name_to_id["Floor 16 Payment 12"], Floor_16
        )

        Floor_16.locations.append(Floor_16_Payment_12)

    if "17" in world.options.Floors.value:
        Floor_17_Payment_1 = LBALLocation(
            world.player, "Floor 17 Payment 1", world.location_name_to_id["Floor 17 Payment 1"], Floor_17
        )

        Floor_17.locations.append(Floor_17_Payment_1)

    if "17" in world.options.Floors.value:
        Floor_17_Payment_2 = LBALLocation(
            world.player, "Floor 17 Payment 2", world.location_name_to_id["Floor 17 Payment 2"], Floor_17
        )

        Floor_17.locations.append(Floor_17_Payment_2)

    if "17" in world.options.Floors.value:
        Floor_17_Payment_3 = LBALLocation(
            world.player, "Floor 17 Payment 3", world.location_name_to_id["Floor 17 Payment 3"], Floor_17
        )

        Floor_17.locations.append(Floor_17_Payment_3)

    if "17" in world.options.Floors.value:
        Floor_17_Payment_4 = LBALLocation(
            world.player, "Floor 17 Payment 4", world.location_name_to_id["Floor 17 Payment 4"], Floor_17
        )

        Floor_17.locations.append(Floor_17_Payment_4)

    if "17" in world.options.Floors.value:
        Floor_17_Payment_5 = LBALLocation(
            world.player, "Floor 17 Payment 5", world.location_name_to_id["Floor 17 Payment 5"], Floor_17
        )

        Floor_17.locations.append(Floor_17_Payment_5)

    if "17" in world.options.Floors.value:
        Floor_17_Payment_6 = LBALLocation(
            world.player, "Floor 17 Payment 6", world.location_name_to_id["Floor 17 Payment 6"], Floor_17
        )

        Floor_17.locations.append(Floor_17_Payment_6)

    if "17" in world.options.Floors.value:
        Floor_17_Payment_7 = LBALLocation(
            world.player, "Floor 17 Payment 7", world.location_name_to_id["Floor 17 Payment 7"], Floor_17
        )

        Floor_17.locations.append(Floor_17_Payment_7)

    if "17" in world.options.Floors.value:
        Floor_17_Payment_8 = LBALLocation(
            world.player, "Floor 17 Payment 8", world.location_name_to_id["Floor 17 Payment 8"], Floor_17
        )

        Floor_17.locations.append(Floor_17_Payment_8)

    if "17" in world.options.Floors.value:
        Floor_17_Payment_9 = LBALLocation(
            world.player, "Floor 17 Payment 9", world.location_name_to_id["Floor 17 Payment 9"], Floor_17
        )

        Floor_17.locations.append(Floor_17_Payment_9)

    if "17" in world.options.Floors.value:
        Floor_17_Payment_10 = LBALLocation(
            world.player, "Floor 17 Payment 10", world.location_name_to_id["Floor 17 Payment 10"], Floor_17
        )

        Floor_17.locations.append(Floor_17_Payment_10)

    if "17" in world.options.Floors.value:
        Floor_17_Payment_11 = LBALLocation(
            world.player, "Floor 17 Payment 11", world.location_name_to_id["Floor 17 Payment 11"], Floor_17
        )

        Floor_17.locations.append(Floor_17_Payment_11)

    if "17" in world.options.Floors.value:
        Floor_17_Payment_12 = LBALLocation(
            world.player, "Floor 17 Payment 12", world.location_name_to_id["Floor 17 Payment 12"], Floor_17
        )

        Floor_17.locations.append(Floor_17_Payment_12)


    if "18" in world.options.Floors.value:
        Floor_18_Payment_1 = LBALLocation(
            world.player, "Floor 18 Payment 1", world.location_name_to_id["Floor 18 Payment 1"], Floor_18
        )

        Floor_18.locations.append(Floor_18_Payment_1)

    if "18" in world.options.Floors.value:
        Floor_18_Payment_2 = LBALLocation(
            world.player, "Floor 18 Payment 2", world.location_name_to_id["Floor 18 Payment 2"], Floor_18
        )

        Floor_18.locations.append(Floor_18_Payment_2)

    if "18" in world.options.Floors.value:
        Floor_18_Payment_3 = LBALLocation(
            world.player, "Floor 18 Payment 3", world.location_name_to_id["Floor 18 Payment 3"], Floor_18
        )

        Floor_18.locations.append(Floor_18_Payment_3)

    if "18" in world.options.Floors.value:
        Floor_18_Payment_4 = LBALLocation(
            world.player, "Floor 18 Payment 4", world.location_name_to_id["Floor 18 Payment 4"], Floor_18
        )

        Floor_18.locations.append(Floor_18_Payment_4)

    if "18" in world.options.Floors.value:
        Floor_18_Payment_5 = LBALLocation(
            world.player, "Floor 18 Payment 5", world.location_name_to_id["Floor 18 Payment 5"], Floor_18
        )

        Floor_18.locations.append(Floor_18_Payment_5)

    if "18" in world.options.Floors.value:
        Floor_18_Payment_6 = LBALLocation(
            world.player, "Floor 18 Payment 6", world.location_name_to_id["Floor 18 Payment 6"], Floor_18
        )

        Floor_18.locations.append(Floor_18_Payment_6)

    if "18" in world.options.Floors.value:
        Floor_18_Payment_7 = LBALLocation(
            world.player, "Floor 18 Payment 7", world.location_name_to_id["Floor 18 Payment 7"], Floor_18
        )

        Floor_18.locations.append(Floor_18_Payment_7)

    if "18" in world.options.Floors.value:
        Floor_18_Payment_8 = LBALLocation(
            world.player, "Floor 18 Payment 8", world.location_name_to_id["Floor 18 Payment 8"], Floor_18
        )

        Floor_18.locations.append(Floor_18_Payment_8)

    if "18" in world.options.Floors.value:
        Floor_18_Payment_9 = LBALLocation(
            world.player, "Floor 18 Payment 9", world.location_name_to_id["Floor 18 Payment 9"], Floor_18
        )

        Floor_18.locations.append(Floor_18_Payment_9)

    if "18" in world.options.Floors.value:
        Floor_18_Payment_10 = LBALLocation(
            world.player, "Floor 18 Payment 10", world.location_name_to_id["Floor 18 Payment 10"], Floor_18
        )

        Floor_18.locations.append(Floor_18_Payment_10)

    if "18" in world.options.Floors.value:
        Floor_18_Payment_11 = LBALLocation(
            world.player, "Floor 18 Payment 11", world.location_name_to_id["Floor 18 Payment 11"], Floor_18
        )

        Floor_18.locations.append(Floor_18_Payment_11)

    if "18" in world.options.Floors.value:
        Floor_18_Payment_12 = LBALLocation(
            world.player, "Floor 18 Payment 12", world.location_name_to_id["Floor 18 Payment 12"], Floor_18
        )

        Floor_18.locations.append(Floor_18_Payment_12)


    if "19" in world.options.Floors.value:
        Floor_19_Payment_1 = LBALLocation(
            world.player, "Floor 19 Payment 1", world.location_name_to_id["Floor 19 Payment 1"], Floor_19
        )

        Floor_19.locations.append(Floor_19_Payment_1)

    if "19" in world.options.Floors.value:
        Floor_19_Payment_2 = LBALLocation(
            world.player, "Floor 19 Payment 2", world.location_name_to_id["Floor 19 Payment 2"], Floor_19
        )

        Floor_19.locations.append(Floor_19_Payment_2)

    if "19" in world.options.Floors.value:
        Floor_19_Payment_3 = LBALLocation(
            world.player, "Floor 19 Payment 3", world.location_name_to_id["Floor 19 Payment 3"], Floor_19
        )

        Floor_19.locations.append(Floor_19_Payment_3)

    if "19" in world.options.Floors.value:
        Floor_19_Payment_4 = LBALLocation(
            world.player, "Floor 19 Payment 4", world.location_name_to_id["Floor 19 Payment 4"], Floor_19
        )

        Floor_19.locations.append(Floor_19_Payment_4)

    if "19" in world.options.Floors.value:
        Floor_19_Payment_5 = LBALLocation(
            world.player, "Floor 19 Payment 5", world.location_name_to_id["Floor 19 Payment 5"], Floor_19
        )

        Floor_19.locations.append(Floor_19_Payment_5)

    if "19" in world.options.Floors.value:
        Floor_19_Payment_6 = LBALLocation(
            world.player, "Floor 19 Payment 6", world.location_name_to_id["Floor 19 Payment 6"], Floor_19
        )

        Floor_19.locations.append(Floor_19_Payment_6)

    if "19" in world.options.Floors.value:
        Floor_19_Payment_7 = LBALLocation(
            world.player, "Floor 19 Payment 7", world.location_name_to_id["Floor 19 Payment 7"], Floor_19
        )

        Floor_19.locations.append(Floor_19_Payment_7)

    if "19" in world.options.Floors.value:
        Floor_19_Payment_8 = LBALLocation(
            world.player, "Floor 19 Payment 8", world.location_name_to_id["Floor 19 Payment 8"], Floor_19
        )

        Floor_19.locations.append(Floor_19_Payment_8)

    if "19" in world.options.Floors.value:
        Floor_19_Payment_9 = LBALLocation(
            world.player, "Floor 19 Payment 9", world.location_name_to_id["Floor 19 Payment 9"], Floor_19
        )

        Floor_19.locations.append(Floor_19_Payment_9)

    if "19" in world.options.Floors.value:
        Floor_19_Payment_10 = LBALLocation(
            world.player, "Floor 19 Payment 10", world.location_name_to_id["Floor 19 Payment 10"], Floor_19
        )

        Floor_19.locations.append(Floor_19_Payment_10)

    if "19" in world.options.Floors.value:
        Floor_19_Payment_11 = LBALLocation(
            world.player, "Floor 19 Payment 11", world.location_name_to_id["Floor 19 Payment 11"], Floor_19
        )

        Floor_19.locations.append(Floor_19_Payment_11)

    if "19" in world.options.Floors.value:
        Floor_19_Payment_12 = LBALLocation(
            world.player, "Floor 19 Payment 12", world.location_name_to_id["Floor 19 Payment 12"], Floor_19
        )

        Floor_19.locations.append(Floor_19_Payment_12)


    if "20" in world.options.Floors.value:
        Floor_20_Payment_1 = LBALLocation(
            world.player, "Floor 20 Payment 1", world.location_name_to_id["Floor 20 Payment 1"], Floor_20
        )

        Floor_20.locations.append(Floor_20_Payment_1)

    if "20" in world.options.Floors.value:
        Floor_20_Payment_2 = LBALLocation(
            world.player, "Floor 20 Payment 2", world.location_name_to_id["Floor 20 Payment 2"], Floor_20
        )

        Floor_20.locations.append(Floor_20_Payment_2)

    if "20" in world.options.Floors.value:
        Floor_20_Payment_3 = LBALLocation(
            world.player, "Floor 20 Payment 3", world.location_name_to_id["Floor 20 Payment 3"], Floor_20
        )

        Floor_20.locations.append(Floor_20_Payment_3)

    if "20" in world.options.Floors.value:
        Floor_20_Payment_4 = LBALLocation(
            world.player, "Floor 20 Payment 4", world.location_name_to_id["Floor 20 Payment 4"], Floor_20
        )

        Floor_20.locations.append(Floor_20_Payment_4)

    if "20" in world.options.Floors.value:
        Floor_20_Payment_5 = LBALLocation(
            world.player, "Floor 20 Payment 5", world.location_name_to_id["Floor 20 Payment 5"], Floor_20
        )

        Floor_20.locations.append(Floor_20_Payment_5)

    if "20" in world.options.Floors.value:
        Floor_20_Payment_6 = LBALLocation(
            world.player, "Floor 20 Payment 6", world.location_name_to_id["Floor 20 Payment 6"], Floor_20
        )

        Floor_20.locations.append(Floor_20_Payment_6)

    if "20" in world.options.Floors.value:
        Floor_20_Payment_7 = LBALLocation(
            world.player, "Floor 20 Payment 7", world.location_name_to_id["Floor 20 Payment 7"], Floor_20
        )

        Floor_20.locations.append(Floor_20_Payment_7)

    if "20" in world.options.Floors.value:
        Floor_20_Payment_8 = LBALLocation(
            world.player, "Floor 20 Payment 8", world.location_name_to_id["Floor 20 Payment 8"], Floor_20
        )

        Floor_20.locations.append(Floor_20_Payment_8)

    if "20" in world.options.Floors.value:
        Floor_20_Payment_9 = LBALLocation(
            world.player, "Floor 20 Payment 9", world.location_name_to_id["Floor 20 Payment 9"], Floor_20
        )

        Floor_20.locations.append(Floor_20_Payment_9)

    if "20" in world.options.Floors.value:
        Floor_20_Payment_10 = LBALLocation(
            world.player, "Floor 20 Payment 10", world.location_name_to_id["Floor 20 Payment 10"], Floor_20
        )

        Floor_20.locations.append(Floor_20_Payment_10)

    if "20" in world.options.Floors.value:
        Floor_20_Payment_11 = LBALLocation(
            world.player, "Floor 20 Payment 11", world.location_name_to_id["Floor 20 Payment 11"], Floor_20
        )

        Floor_20.locations.append(Floor_20_Payment_11)

    if "20" in world.options.Floors.value:
        Floor_20_Payment_12 = LBALLocation(
            world.player, "Floor 20 Payment 12", world.location_name_to_id["Floor 20 Payment 12"], Floor_20
        )

        Floor_20.locations.append(Floor_20_Payment_12)



    # # A simpler way to do this is by using the region.add_locations helper.
    # # For this, you need to have a dict of location names to their IDs (i.e. a subset of location_name_to_id)
    # # Aha! So that's why we made that "get_location_names_with_ids" helper method earlier.
    # # You also need to pass your overridden Location class.
    # bottom_right_room_locations = get_location_names_with_ids(
    #     ["Bottom Right Room Left Chest", "Bottom Right Room Right Chest"]
    # )
    # bottom_right_room.add_locations(bottom_right_room_locations, APQuestLocation)

    # top_left_room_locations = get_location_names_with_ids(["Top Left Room Chest"])
    # top_left_room.add_locations(top_left_room_locations, APQuestLocation)

    # right_room_locations = get_location_names_with_ids(["Right Room Enemy Drop"])
    # right_room.add_locations(right_room_locations, APQuestLocation)


    # Locations may exist only if the player enables certain options.
    # In our case, the extra_starting_chest option adds the Bottom Left Extra Chest location.
    #if world.options.extra_starting_chest:
        # Once again, it is important to stress that even though the Bottom Left Extra Chest location doesn't always
        # exist, it must still always be present in the world's location_name_to_id.
        # Whether the location actually exists in the seed is purely determined by whether we create and add it here.
    #    bottom_left_extra_chest = get_location_names_with_ids(["Bottom Left Extra Chest"])
    #    overworld.add_locations(bottom_left_extra_chest, APQuestLocation)
