extends Reference

# Generated from the AP effect location table.
const EFFECT_RULE_COUNT = 357
const EFFECT_RULES_BY_SOURCE = {
	"amethyst": [
		{"id": 530, "name": "Effect: Amethyst Gets Boosted", "source": "amethyst", "targets": [], "kind": "boost", "mode": "target_boost"},
	],
	"anchor": [
		{"id": 531, "name": "Effect: Anchor is in the corner", "source": "anchor", "targets": [], "kind": "position"},
	],
	"banana_peel": [
		{"id": 532, "name": "Effect: Banana Peel Destroys Thief", "source": "banana_peel", "targets": ["thief"], "kind": "destroy"},
	],
	"bar_of_soap": [
		{"id": 533, "name": "Effect: Bar of Soap adds Bubble", "source": "bar_of_soap", "targets": ["bubble"], "kind": "add"},
	],
	"bartender": [
		{"id": 534, "name": "Effect: Bartender adds Chemical Seven", "source": "bartender", "targets": ["chemical_seven"], "kind": "add"},
		{"id": 535, "name": "Effect: Bartender adds Beer", "source": "bartender", "targets": ["beer"], "kind": "add"},
		{"id": 536, "name": "Effect: Bartender adds Wine", "source": "bartender", "targets": ["wine"], "kind": "add"},
		{"id": 537, "name": "Effect: Bartender adds Martini", "source": "bartender", "targets": ["martini"], "kind": "add"},
	],
	"bear": [
		{"id": 538, "name": "Effect: Bear Destroys Honey", "source": "bear", "targets": ["honey"], "kind": "destroy"},
	],
	"beastmaster": [
		{"id": 539, "name": "Effect: Beastmaster Boosts Magpie", "source": "beastmaster", "targets": ["magpie"], "kind": "boost"},
		{"id": 540, "name": "Effect: Beastmaster Boosts Void Creature", "source": "beastmaster", "targets": ["void_creature"], "kind": "boost"},
		{"id": 541, "name": "Effect: Beastmaster Boosts Turtle", "source": "beastmaster", "targets": ["turtle"], "kind": "boost"},
		{"id": 542, "name": "Effect: Beastmaster Boosts Snail", "source": "beastmaster", "targets": ["snail"], "kind": "boost"},
		{"id": 543, "name": "Effect: Beastmaster Boosts Sloth", "source": "beastmaster", "targets": ["sloth"], "kind": "boost"},
		{"id": 544, "name": "Effect: Beastmaster Boosts Oyster", "source": "beastmaster", "targets": ["oyster"], "kind": "boost"},
		{"id": 545, "name": "Effect: Beastmaster Boosts Owl", "source": "beastmaster", "targets": ["owl"], "kind": "boost"},
		{"id": 546, "name": "Effect: Beastmaster Boosts Mouse", "source": "beastmaster", "targets": ["mouse"], "kind": "boost"},
		{"id": 547, "name": "Effect: Beastmaster Boosts Monkey", "source": "beastmaster", "targets": ["monkey"], "kind": "boost"},
		{"id": 548, "name": "Effect: Beastmaster Boosts Rabbit", "source": "beastmaster", "targets": ["rabbit"], "kind": "boost"},
		{"id": 549, "name": "Effect: Beastmaster Boosts Goose", "source": "beastmaster", "targets": ["goose"], "kind": "boost"},
		{"id": 550, "name": "Effect: Beastmaster Boosts Goldfish", "source": "beastmaster", "targets": ["goldfish"], "kind": "boost"},
		{"id": 551, "name": "Effect: Beastmaster Boosts Dog", "source": "beastmaster", "targets": ["dog"], "kind": "boost"},
		{"id": 552, "name": "Effect: Beastmaster Boosts Crab", "source": "beastmaster", "targets": ["crab"], "kind": "boost"},
		{"id": 553, "name": "Effect: Beastmaster Boosts Chick", "source": "beastmaster", "targets": ["chick"], "kind": "boost"},
		{"id": 554, "name": "Effect: Beastmaster Boosts Cat", "source": "beastmaster", "targets": ["cat"], "kind": "boost"},
		{"id": 555, "name": "Effect: Beastmaster Boosts Bee", "source": "beastmaster", "targets": ["bee"], "kind": "boost"},
		{"id": 556, "name": "Effect: Beastmaster Boosts Sand Dollar", "source": "beastmaster", "targets": ["sand_dollar"], "kind": "boost"},
		{"id": 557, "name": "Effect: Beastmaster Boosts Wolf", "source": "beastmaster", "targets": ["wolf"], "kind": "boost"},
		{"id": 558, "name": "Effect: Beastmaster Boosts Pufferfish", "source": "beastmaster", "targets": ["pufferfish"], "kind": "boost"},
		{"id": 559, "name": "Effect: Beastmaster Boosts Dove", "source": "beastmaster", "targets": ["dove"], "kind": "boost"},
		{"id": 560, "name": "Effect: Beastmaster Boosts Crow", "source": "beastmaster", "targets": ["crow"], "kind": "boost"},
		{"id": 561, "name": "Effect: Beastmaster Boosts Chicken", "source": "beastmaster", "targets": ["chicken"], "kind": "boost"},
		{"id": 562, "name": "Effect: Beastmaster Boosts Cow", "source": "beastmaster", "targets": ["cow"], "kind": "boost"},
		{"id": 563, "name": "Effect: Beastmaster Boosts Bear", "source": "beastmaster", "targets": ["bear"], "kind": "boost"},
		{"id": 564, "name": "Effect: Beastmaster Boosts Eldritch Creature", "source": "beastmaster", "targets": ["eldritch_creature"], "kind": "boost"},
	],
	"bee": [
		{"id": 565, "name": "Effect: Bee Boosts Flower", "source": "bee", "targets": ["flower"], "kind": "boost"},
		{"id": 566, "name": "Effect: Bee Boosts Beehive", "source": "bee", "targets": ["beehive"], "kind": "boost"},
		{"id": 567, "name": "Effect: Bee Boosts Honey", "source": "bee", "targets": ["honey"], "kind": "boost"},
	],
	"beehive": [
		{"id": 568, "name": "Effect: Beehive adds Honey", "source": "beehive", "targets": ["honey"], "kind": "add"},
	],
	"big_urn": [
		{"id": 569, "name": "Effect: Big Urn adds Spirit", "source": "big_urn", "targets": ["spirit"], "kind": "add"},
	],
	"billionaire": [
		{"id": 570, "name": "Effect: Billionaire Boosts Cheese", "source": "billionaire", "targets": ["cheese"], "kind": "boost"},
		{"id": 571, "name": "Effect: Billionaire Boosts Wine", "source": "billionaire", "targets": ["wine"], "kind": "boost"},
	],
	"bounty_hunter": [
		{"id": 572, "name": "Effect: Bounty Hunter Destroys Thief", "source": "bounty_hunter", "targets": ["thief"], "kind": "destroy"},
	],
	"bronze_arrow": [
		{"id": 573, "name": "Effect: Bronze Arrow Boosts a Symbol", "source": "bronze_arrow", "targets": [], "kind": "boost"},
		{"id": 574, "name": "Effect: Bronze Arrow Destroys Target", "source": "bronze_arrow", "targets": ["target"], "kind": "destroy"},
	],
	"buffing_capsule": [
		{"id": 575, "name": "Effect: Buffing Capsule Boosts Symbols", "source": "buffing_capsule", "targets": [], "kind": "boost"},
	],
	"card_shark": [
		{"id": 576, "name": "Effect: Card Shark Makes Clubs Wildcard", "source": "card_shark", "targets": ["clubs"], "kind": "wildcard"},
		{"id": 577, "name": "Effect: Card Shark Makes Diamonds Wildcard", "source": "card_shark", "targets": ["diamonds"], "kind": "wildcard"},
		{"id": 578, "name": "Effect: Card Shark Makes Hearts Wildcard", "source": "card_shark", "targets": ["hearts"], "kind": "wildcard"},
		{"id": 579, "name": "Effect: Card Shark Makes Spades Wildcard", "source": "card_shark", "targets": ["spades"], "kind": "wildcard"},
	],
	"cat": [
		{"id": 580, "name": "Effect: Cat Destroys Milk", "source": "cat", "targets": ["milk"], "kind": "destroy"},
	],
	"chef": [
		{"id": 581, "name": "Effect: Chef Boosts Chemical Seven", "source": "chef", "targets": ["chemical_seven"], "kind": "boost"},
		{"id": 582, "name": "Effect: Chef Boosts Void Fruit", "source": "chef", "targets": ["void_fruit"], "kind": "boost"},
		{"id": 583, "name": "Effect: Chef Boosts Banana", "source": "chef", "targets": ["banana"], "kind": "boost"},
		{"id": 584, "name": "Effect: Chef Boosts Beer", "source": "chef", "targets": ["beer"], "kind": "boost"},
		{"id": 585, "name": "Effect: Chef Boosts Candy", "source": "chef", "targets": ["candy"], "kind": "boost"},
		{"id": 586, "name": "Effect: Chef Boosts Cheese", "source": "chef", "targets": ["cheese"], "kind": "boost"},
		{"id": 587, "name": "Effect: Chef Boosts Cherry", "source": "chef", "targets": ["cherry"], "kind": "boost"},
		{"id": 588, "name": "Effect: Chef Boosts Egg", "source": "chef", "targets": ["egg"], "kind": "boost"},
		{"id": 589, "name": "Effect: Chef Boosts Milk", "source": "chef", "targets": ["milk"], "kind": "boost"},
		{"id": 590, "name": "Effect: Chef Boosts Pear", "source": "chef", "targets": ["pear"], "kind": "boost"},
		{"id": 591, "name": "Effect: Chef Boosts Wine", "source": "chef", "targets": ["wine"], "kind": "boost"},
		{"id": 592, "name": "Effect: Chef Boosts Coconut Half", "source": "chef", "targets": ["coconut_half"], "kind": "boost"},
		{"id": 593, "name": "Effect: Chef Boosts Orange", "source": "chef", "targets": ["orange"], "kind": "boost"},
		{"id": 594, "name": "Effect: Chef Boosts Peach", "source": "chef", "targets": ["peach"], "kind": "boost"},
		{"id": 595, "name": "Effect: Chef Boosts Strawberry", "source": "chef", "targets": ["strawberry"], "kind": "boost"},
		{"id": 596, "name": "Effect: Chef Boosts Omelette", "source": "chef", "targets": ["omelette"], "kind": "boost"},
		{"id": 597, "name": "Effect: Chef Boosts Martini", "source": "chef", "targets": ["martini"], "kind": "boost"},
		{"id": 598, "name": "Effect: Chef Boosts Honey", "source": "chef", "targets": ["honey"], "kind": "boost"},
		{"id": 599, "name": "Effect: Chef Boosts Golden Egg", "source": "chef", "targets": ["golden_egg"], "kind": "boost"},
		{"id": 600, "name": "Effect: Chef Boosts Apple", "source": "chef", "targets": ["apple"], "kind": "boost"},
		{"id": 601, "name": "Effect: Chef Boosts Watermelon", "source": "chef", "targets": ["watermelon"], "kind": "boost"},
	],
	"chemical_seven": [
		{"id": 602, "name": "Effect: Chemical Seven Destroys Itself", "source": "chemical_seven", "targets": [], "kind": "destroy"},
	],
	"chick": [
		{"id": 603, "name": "Effect: Chick grows into Chicken", "source": "chick", "targets": ["chicken"], "kind": "transform"},
	],
	"clubs": [
		{"id": 604, "name": "Effect: Clubs adjacent to Clubs", "source": "clubs", "targets": ["clubs"], "kind": "position"},
		{"id": 605, "name": "Effect: Clubs adjacent to Spades", "source": "clubs", "targets": ["spades"], "kind": "position"},
	],
	"coal": [
		{"id": 606, "name": "Effect: Coal Transforms into Diamond", "source": "coal", "targets": ["diamond"], "kind": "transform"},
	],
	"comedian": [
		{"id": 607, "name": "Effect: Comedian Boosts Banana", "source": "comedian", "targets": ["banana"], "kind": "boost"},
		{"id": 608, "name": "Effect: Comedian Boosts Banana Peel", "source": "comedian", "targets": ["banana_peel"], "kind": "boost"},
		{"id": 609, "name": "Effect: Comedian Boosts Dog", "source": "comedian", "targets": ["dog"], "kind": "boost"},
		{"id": 610, "name": "Effect: Comedian Boosts Monkey", "source": "comedian", "targets": ["monkey"], "kind": "boost"},
		{"id": 611, "name": "Effect: Comedian Boosts Toddler", "source": "comedian", "targets": ["toddler"], "kind": "boost"},
		{"id": 612, "name": "Effect: Comedian Boosts Joker", "source": "comedian", "targets": ["joker"], "kind": "boost"},
	],
	"cow": [
		{"id": 613, "name": "Effect: Cow adds Milk", "source": "cow", "targets": ["milk"], "kind": "add"},
	],
	"crab": [
		{"id": 614, "name": "Effect: Crab in same row", "source": "crab", "targets": [], "kind": "position", "mode": "manual"},
	],
	"crow": [
		{"id": 615, "name": "Effect: Crow Loses Coins", "source": "crow", "targets": [], "kind": "lose"},
	],
	"cultist": [
		{"id": 616, "name": "Effect: Cultist Boosts Cultist", "source": "cultist", "targets": ["cultist"], "kind": "boost"},
	],
	"dame": [
		{"id": 617, "name": "Effect: Dame Boosts Void Stone", "source": "dame", "targets": ["void_stone"], "kind": "boost"},
		{"id": 618, "name": "Effect: Dame Boosts Amethyst", "source": "dame", "targets": ["amethyst"], "kind": "boost"},
		{"id": 619, "name": "Effect: Dame Boosts Pearl", "source": "dame", "targets": ["pearl"], "kind": "boost"},
		{"id": 620, "name": "Effect: Dame Boosts Shiny Pebble", "source": "dame", "targets": ["shiny_pebble"], "kind": "boost"},
		{"id": 621, "name": "Effect: Dame Boosts Sapphire", "source": "dame", "targets": ["sapphire"], "kind": "boost"},
		{"id": 622, "name": "Effect: Dame Boosts Emerald", "source": "dame", "targets": ["emerald"], "kind": "boost"},
		{"id": 623, "name": "Effect: Dame Boosts Ruby", "source": "dame", "targets": ["ruby"], "kind": "boost"},
		{"id": 624, "name": "Effect: Dame Boosts Diamond", "source": "dame", "targets": ["diamond"], "kind": "boost"},
		{"id": 625, "name": "Effect: Dame Destroys Martini", "source": "dame", "targets": ["martini"], "kind": "destroy"},
	],
	"diamond": [
		{"id": 626, "name": "Effect: Diamond Boosts Diamond", "source": "diamond", "targets": ["diamond"], "kind": "boost"},
	],
	"diamonds": [
		{"id": 627, "name": "Effect: Diamonds Boosts Diamonds", "source": "diamonds", "targets": ["diamonds"], "kind": "boost"},
		{"id": 628, "name": "Effect: Diamonds Boosts Hearts", "source": "diamonds", "targets": ["hearts"], "kind": "boost"},
	],
	"diver": [
		{"id": 629, "name": "Effect: Diver Destroys Snail", "source": "diver", "targets": ["snail"], "kind": "destroy"},
		{"id": 630, "name": "Effect: Diver Destroys Turtle", "source": "diver", "targets": ["turtle"], "kind": "destroy"},
		{"id": 631, "name": "Effect: Diver Destroys Anchor", "source": "diver", "targets": ["anchor"], "kind": "destroy"},
		{"id": 632, "name": "Effect: Diver Destroys Crab", "source": "diver", "targets": ["crab"], "kind": "destroy"},
		{"id": 633, "name": "Effect: Diver Destroys Goldfish", "source": "diver", "targets": ["goldfish"], "kind": "destroy"},
		{"id": 634, "name": "Effect: Diver Destroys Oyster", "source": "diver", "targets": ["oyster"], "kind": "destroy"},
		{"id": 635, "name": "Effect: Diver Destroys Pearl", "source": "diver", "targets": ["pearl"], "kind": "destroy"},
		{"id": 636, "name": "Effect: Diver Destroys Jellyfish", "source": "diver", "targets": ["jellyfish"], "kind": "destroy"},
		{"id": 637, "name": "Effect: Diver Destroys Pufferfish", "source": "diver", "targets": ["pufferfish"], "kind": "destroy"},
		{"id": 638, "name": "Effect: Diver Destroys Sand Dollar", "source": "diver", "targets": ["sand_dollar"], "kind": "destroy"},
	],
	"dog": [
		{"id": 639, "name": "Effect: Dog Boosts Robin Hood", "source": "dog", "targets": ["robin_hood"], "kind": "boost"},
		{"id": 640, "name": "Effect: Dog Boosts Thief", "source": "dog", "targets": ["thief"], "kind": "boost"},
		{"id": 641, "name": "Effect: Dog Boosts Cultist", "source": "dog", "targets": ["cultist"], "kind": "boost"},
		{"id": 642, "name": "Effect: Dog Boosts Toddler", "source": "dog", "targets": ["toddler"], "kind": "boost"},
		{"id": 643, "name": "Effect: Dog Boosts Bounty Hunter", "source": "dog", "targets": ["bounty_hunter"], "kind": "boost"},
		{"id": 644, "name": "Effect: Dog Boosts Miner", "source": "dog", "targets": ["miner"], "kind": "boost"},
		{"id": 645, "name": "Effect: Dog Boosts Dwarf", "source": "dog", "targets": ["dwarf"], "kind": "boost"},
		{"id": 646, "name": "Effect: Dog Boosts King Midas", "source": "dog", "targets": ["king_midas"], "kind": "boost"},
		{"id": 647, "name": "Effect: Dog Boosts Gambler", "source": "dog", "targets": ["gambler"], "kind": "boost"},
		{"id": 648, "name": "Effect: Dog Boosts General Zaroff", "source": "dog", "targets": ["general_zaroff"], "kind": "boost"},
		{"id": 649, "name": "Effect: Dog Boosts Witch", "source": "dog", "targets": ["witch"], "kind": "boost"},
		{"id": 650, "name": "Effect: Dog Boosts Pirate", "source": "dog", "targets": ["pirate"], "kind": "boost"},
		{"id": 651, "name": "Effect: Dog Boosts Ninja", "source": "dog", "targets": ["ninja"], "kind": "boost"},
		{"id": 652, "name": "Effect: Dog Boosts Mrs. Fruit", "source": "dog", "targets": ["mrs_fruit"], "kind": "boost"},
		{"id": 653, "name": "Effect: Dog Boosts Hooligan", "source": "dog", "targets": ["hooligan"], "kind": "boost"},
		{"id": 654, "name": "Effect: Dog Boosts Farmer", "source": "dog", "targets": ["farmer"], "kind": "boost"},
		{"id": 655, "name": "Effect: Dog Boosts Diver", "source": "dog", "targets": ["diver"], "kind": "boost"},
		{"id": 656, "name": "Effect: Dog Boosts Dame", "source": "dog", "targets": ["dame"], "kind": "boost"},
		{"id": 657, "name": "Effect: Dog Boosts Chef", "source": "dog", "targets": ["chef"], "kind": "boost"},
		{"id": 658, "name": "Effect: Dog Boosts Card Shark", "source": "dog", "targets": ["card_shark"], "kind": "boost"},
		{"id": 659, "name": "Effect: Dog Boosts Beastmaster", "source": "dog", "targets": ["beastmaster"], "kind": "boost"},
		{"id": 660, "name": "Effect: Dog Boosts Geologist", "source": "dog", "targets": ["geologist"], "kind": "boost"},
		{"id": 661, "name": "Effect: Dog Boosts Joker", "source": "dog", "targets": ["joker"], "kind": "boost"},
		{"id": 662, "name": "Effect: Dog Boosts Comedian", "source": "dog", "targets": ["comedian"], "kind": "boost"},
		{"id": 663, "name": "Effect: Dog Boosts Bartender", "source": "dog", "targets": ["bartender"], "kind": "boost"},
	],
	"dove": [
		{"id": 664, "name": "Effect: Dove Protects destroyed Symbol", "source": "dove", "targets": [], "kind": "protect"},
	],
	"dwarf": [
		{"id": 665, "name": "Effect: Dwarf Destroys Beer", "source": "dwarf", "targets": ["beer"], "kind": "destroy"},
		{"id": 666, "name": "Effect: Dwarf Destroys Wine", "source": "dwarf", "targets": ["wine"], "kind": "destroy"},
	],
	"egg": [
		{"id": 667, "name": "Effect: Egg transforms into Chick", "source": "egg", "targets": ["chick"], "kind": "transform"},
	],
	"eldritch_creature": [
		{"id": 668, "name": "Effect: Eldritch Creature Destroys Cultist", "source": "eldritch_creature", "targets": ["cultist"], "kind": "destroy"},
		{"id": 669, "name": "Effect: Eldritch Creature Destroys Witch", "source": "eldritch_creature", "targets": ["witch"], "kind": "destroy"},
		{"id": 670, "name": "Effect: Eldritch Creature Destroys Hex of Destruction", "source": "eldritch_creature", "targets": ["hex_of_destruction"], "kind": "destroy"},
		{"id": 671, "name": "Effect: Eldritch Creature Destroys Hex of Draining", "source": "eldritch_creature", "targets": ["hex_of_draining"], "kind": "destroy"},
		{"id": 672, "name": "Effect: Eldritch Creature Destroys Hex of Emptiness", "source": "eldritch_creature", "targets": ["hex_of_emptiness"], "kind": "destroy"},
		{"id": 673, "name": "Effect: Eldritch Creature Destroys Hex of Hoarding", "source": "eldritch_creature", "targets": ["hex_of_hoarding"], "kind": "destroy"},
		{"id": 674, "name": "Effect: Eldritch Creature Destroys Hex of Midas", "source": "eldritch_creature", "targets": ["hex_of_midas"], "kind": "destroy"},
		{"id": 675, "name": "Effect: Eldritch Creature Destroys Hex of Tedium", "source": "eldritch_creature", "targets": ["hex_of_tedium"], "kind": "destroy"},
		{"id": 676, "name": "Effect: Eldritch Creature Destroys Hex of Thievery", "source": "eldritch_creature", "targets": ["hex_of_thievery"], "kind": "destroy"},
	],
	"emerald": [
		{"id": 677, "name": "Effect: Emerald Boosts Emerald", "source": "emerald", "targets": ["emerald"], "kind": "boost"},
	],
	"essence_capsule": [
		{"id": 678, "name": "Effect: Essence Capsule Destroys itself", "source": "essence_capsule", "targets": [], "kind": "destroy"},
	],
	"farmer": [
		{"id": 679, "name": "Effect: Farmer Boosts Void Fruit", "source": "farmer", "targets": ["void_fruit"], "kind": "boost"},
		{"id": 680, "name": "Effect: Farmer Boosts Banana", "source": "farmer", "targets": ["banana"], "kind": "boost"},
		{"id": 681, "name": "Effect: Farmer Boosts Cheese", "source": "farmer", "targets": ["cheese"], "kind": "boost"},
		{"id": 682, "name": "Effect: Farmer Boosts Cherry", "source": "farmer", "targets": ["cherry"], "kind": "boost"},
		{"id": 683, "name": "Effect: Farmer Boosts Chick", "source": "farmer", "targets": ["chick"], "kind": "boost"},
		{"id": 684, "name": "Effect: Farmer Boosts Coconut", "source": "farmer", "targets": ["coconut"], "kind": "boost"},
		{"id": 685, "name": "Effect: Farmer Boosts Seed", "source": "farmer", "targets": ["seed"], "kind": "boost", "vtc": "value_multiplier"},
		{"id": 686, "name": "Effect: Farmer Boosts Egg", "source": "farmer", "targets": ["egg"], "kind": "boost"},
		{"id": 687, "name": "Effect: Farmer Boosts Flower", "source": "farmer", "targets": ["flower"], "kind": "boost"},
		{"id": 688, "name": "Effect: Farmer Boosts Milk", "source": "farmer", "targets": ["milk"], "kind": "boost"},
		{"id": 689, "name": "Effect: Farmer Boosts Pear", "source": "farmer", "targets": ["pear"], "kind": "boost"},
		{"id": 690, "name": "Effect: Farmer Boosts Chicken", "source": "farmer", "targets": ["chicken"], "kind": "boost"},
		{"id": 691, "name": "Effect: Farmer Boosts Orange", "source": "farmer", "targets": ["orange"], "kind": "boost"},
		{"id": 692, "name": "Effect: Farmer Boosts Peach", "source": "farmer", "targets": ["peach"], "kind": "boost"},
		{"id": 693, "name": "Effect: Farmer Boosts Strawberry", "source": "farmer", "targets": ["strawberry"], "kind": "boost"},
		{"id": 694, "name": "Effect: Farmer Boosts Golden Egg", "source": "farmer", "targets": ["golden_egg"], "kind": "boost"},
		{"id": 695, "name": "Effect: Farmer Boosts Cow", "source": "farmer", "targets": ["cow"], "kind": "boost"},
		{"id": 696, "name": "Effect: Farmer Boosts Apple", "source": "farmer", "targets": ["apple"], "kind": "boost"},
		{"id": 697, "name": "Effect: Farmer Boosts Watermelon", "source": "farmer", "targets": ["watermelon"], "kind": "boost"},
		{"id": 698, "name": "Effect: Farmer Boosts Seed Growing", "source": "farmer", "targets": ["seed"], "kind": "boost", "vtc": "bonus_values"},
	],
	"five_sided_die": [
		{"id": 699, "name": "Effect: Five-Sided Die Rolls", "source": "five_sided_die", "targets": [], "kind": "roll"},
		{"id": 1119, "name": "Effect: Five-Sided Die Destroys Gambler", "source": "five_sided_die", "targets": ["gambler"], "kind": "destroy"},
	],
	"frozen_fossil": [
		{"id": 700, "name": "Effect: Frozen Fossil Destroys Cultist", "source": "frozen_fossil", "targets": ["cultist"], "kind": "destroy"},
		{"id": 701, "name": "Effect: Frozen Fossil Destroys Witch", "source": "frozen_fossil", "targets": ["witch"], "kind": "destroy"},
		{"id": 702, "name": "Effect: Frozen Fossil Destroys Hex of Destruction", "source": "frozen_fossil", "targets": ["hex_of_destruction"], "kind": "destroy"},
		{"id": 703, "name": "Effect: Frozen Fossil Destroys Hex of Draining", "source": "frozen_fossil", "targets": ["hex_of_draining"], "kind": "destroy"},
		{"id": 704, "name": "Effect: Frozen Fossil Destroys Hex of Emptiness", "source": "frozen_fossil", "targets": ["hex_of_emptiness"], "kind": "destroy"},
		{"id": 705, "name": "Effect: Frozen Fossil Destroys Hex of Hoarding", "source": "frozen_fossil", "targets": ["hex_of_hoarding"], "kind": "destroy"},
		{"id": 706, "name": "Effect: Frozen Fossil Destroys Hex of Midas", "source": "frozen_fossil", "targets": ["hex_of_midas"], "kind": "destroy"},
		{"id": 707, "name": "Effect: Frozen Fossil Destroys Hex of Tedium", "source": "frozen_fossil", "targets": ["hex_of_tedium"], "kind": "destroy"},
		{"id": 708, "name": "Effect: Frozen Fossil Destroys Hex of Thievery", "source": "frozen_fossil", "targets": ["hex_of_thievery"], "kind": "destroy"},
		{"id": 709, "name": "Effect: Frozen Fossil Transforms into Eldritch Creature", "source": "frozen_fossil", "targets": ["eldritch_creature"], "kind": "transform"},
	],
	"gambler": [
		{"id": 710, "name": "Effect: Gambler gets Destroyed by Dice", "source": "gambler", "targets": [], "kind": "destroy"},
	],
	"general_zaroff": [
		{"id": 711, "name": "Effect: General Zaroff Destroys Robin Hood", "source": "general_zaroff", "targets": ["robin_hood"], "kind": "destroy"},
		{"id": 712, "name": "Effect: General Zaroff Destroys Thief", "source": "general_zaroff", "targets": ["thief"], "kind": "destroy"},
		{"id": 713, "name": "Effect: General Zaroff Destroys Billionare", "source": "general_zaroff", "targets": ["billionaire"], "kind": "destroy"},
		{"id": 714, "name": "Effect: General Zaroff Destroys Cultist", "source": "general_zaroff", "targets": ["cultist"], "kind": "destroy"},
		{"id": 715, "name": "Effect: General Zaroff Destroys Toddler", "source": "general_zaroff", "targets": ["toddler"], "kind": "destroy"},
		{"id": 716, "name": "Effect: General Zaroff Destroys Bounty Hunter", "source": "general_zaroff", "targets": ["bounty_hunter"], "kind": "destroy"},
		{"id": 717, "name": "Effect: General Zaroff Destroys Miner", "source": "general_zaroff", "targets": ["miner"], "kind": "destroy"},
		{"id": 718, "name": "Effect: General Zaroff Destroys Dwarf", "source": "general_zaroff", "targets": ["dwarf"], "kind": "destroy"},
		{"id": 719, "name": "Effect: General Zaroff Destroys King Midas", "source": "general_zaroff", "targets": ["king_midas"], "kind": "destroy"},
		{"id": 720, "name": "Effect: General Zaroff Destroys Gambler", "source": "general_zaroff", "targets": ["gambler"], "kind": "destroy"},
		{"id": 721, "name": "Effect: General Zaroff Destroys General Zaroff", "source": "general_zaroff", "targets": ["general_zaroff"], "kind": "destroy"},
		{"id": 722, "name": "Effect: General Zaroff Destroys Witch", "source": "general_zaroff", "targets": ["witch"], "kind": "destroy"},
		{"id": 723, "name": "Effect: General Zaroff Destroys Pirate", "source": "general_zaroff", "targets": ["pirate"], "kind": "destroy"},
		{"id": 724, "name": "Effect: General Zaroff Destroys Ninja", "source": "general_zaroff", "targets": ["ninja"], "kind": "destroy"},
		{"id": 725, "name": "Effect: General Zaroff Destroys Mrs. Fruit", "source": "general_zaroff", "targets": ["mrs_fruit"], "kind": "destroy"},
		{"id": 726, "name": "Effect: General Zaroff Destroys Hooligan", "source": "general_zaroff", "targets": ["hooligan"], "kind": "destroy"},
		{"id": 727, "name": "Effect: General Zaroff Destroys Farmer", "source": "general_zaroff", "targets": ["farmer"], "kind": "destroy"},
		{"id": 728, "name": "Effect: General Zaroff Destroys Diver", "source": "general_zaroff", "targets": ["diver"], "kind": "destroy"},
		{"id": 729, "name": "Effect: General Zaroff Destroys Dame", "source": "general_zaroff", "targets": ["dame"], "kind": "destroy"},
		{"id": 730, "name": "Effect: General Zaroff Destroys Chef", "source": "general_zaroff", "targets": ["chef"], "kind": "destroy"},
		{"id": 731, "name": "Effect: General Zaroff Destroys Card Shark", "source": "general_zaroff", "targets": ["card_shark"], "kind": "destroy"},
		{"id": 732, "name": "Effect: General Zaroff Destroys Beastmaster", "source": "general_zaroff", "targets": ["beastmaster"], "kind": "destroy"},
		{"id": 733, "name": "Effect: General Zaroff Destroys Geologist", "source": "general_zaroff", "targets": ["geologist"], "kind": "destroy"},
		{"id": 734, "name": "Effect: General Zaroff Destroys Joker", "source": "general_zaroff", "targets": ["joker"], "kind": "destroy"},
		{"id": 735, "name": "Effect: General Zaroff Destroys Comedian", "source": "general_zaroff", "targets": ["comedian"], "kind": "destroy"},
		{"id": 736, "name": "Effect: General Zaroff Destroys Bartender", "source": "general_zaroff", "targets": ["bartender"], "kind": "destroy"},
	],
	"geologist": [
		{"id": 737, "name": "Effect: Geologist Destroys Ore", "source": "geologist", "targets": ["ore"], "kind": "destroy"},
		{"id": 738, "name": "Effect: Geologist Destroys Pearl", "source": "geologist", "targets": ["pearl"], "kind": "destroy"},
		{"id": 739, "name": "Effect: Geologist Destroys Shiny Pebble", "source": "geologist", "targets": ["shiny_pebble"], "kind": "destroy"},
		{"id": 740, "name": "Effect: Geologist Destroys Big Ore", "source": "geologist", "targets": ["big_ore"], "kind": "destroy"},
		{"id": 741, "name": "Effect: Geologist Destroys Sapphire", "source": "geologist", "targets": ["sapphire"], "kind": "destroy"},
	],
	"golden_arrow": [
		{"id": 742, "name": "Effect: Golden Arrow Boosts a Symbol", "source": "golden_arrow", "targets": [], "kind": "boost"},
		{"id": 743, "name": "Effect: Golden Arrow Destroys Target", "source": "golden_arrow", "targets": ["target"], "kind": "destroy"},
	],
	"goldfish": [
		{"id": 744, "name": "Effect: Goldfish Destroys Bubble", "source": "goldfish", "targets": ["bubble"], "kind": "destroy"},
	],
	"golem": [
		{"id": 745, "name": "Effect: Golem Becomes ore", "source": "golem", "targets": ["ore"], "kind": "transform"},
	],
	"goose": [
		{"id": 746, "name": "Effect: Goose Lays Golden Egg", "source": "goose", "targets": ["golden_egg"], "kind": "add"},
	],
	"hearts": [
		{"id": 747, "name": "Effect: Hearts Boost Diamonds", "source": "hearts", "targets": ["diamonds"], "kind": "boost"},
	],
	"hex_of_destruction": [
		{"id": 748, "name": "Effect: Hex of Destruction Destroys a Symbol", "source": "hex_of_destruction", "targets": [], "kind": "destroy"},
	],
	"hex_of_draining": [
		{"id": 749, "name": "Effect: Hex of Draining Makes a Symbol give 0", "source": "hex_of_draining", "targets": [], "kind": "give"},
	],
	"hex_of_emptiness": [
		{"id": 750, "name": "Effect: Hex of Emptiness Skip next Symbol", "source": "hex_of_emptiness", "targets": [], "kind": "skip"},
	],
	"hex_of_hoarding": [
		{"id": 751, "name": "Effect: Hex of Hoarding Force grab next Symbol", "source": "hex_of_hoarding", "targets": [], "kind": "force"},
	],
	"hex_of_midas": [
		{"id": 752, "name": "Effect: Hex of Midas adds Coin", "source": "hex_of_midas", "targets": ["coin"], "kind": "add"},
	],
	"hex_of_thievery": [
		{"id": 753, "name": "Effect: Hex of Thievery lose 6 Coins", "source": "hex_of_thievery", "targets": [], "kind": "lose"},
	],
	"hooligan": [
		{"id": 754, "name": "Effect: Hooligan Destroys Urn", "source": "hooligan", "targets": ["urn"], "kind": "destroy"},
		{"id": 755, "name": "Effect: Hooligan Destroys Big Urn", "source": "hooligan", "targets": ["big_urn"], "kind": "destroy"},
		{"id": 756, "name": "Effect: Hooligan Destroys Tomb", "source": "hooligan", "targets": ["tomb"], "kind": "destroy"},
	],
	"hustling_capsule": [
		{"id": 757, "name": "Effect: Hustling Capsule adds Pool Ball", "source": "hustling_capsule", "targets": ["pool_ball"], "kind": "add"},
	],
	"item_capsule": [
		{"id": 758, "name": "Effect: Item Capsule adds a Common Item", "source": "item_capsule", "targets": [], "kind": "add"},
	],
	"jellyfish": [
		{"id": 759, "name": "Effect: Jellyfish gives Removal Token", "source": "jellyfish", "targets": [], "kind": "give", "currency": "removal_token", "mode": "removed_or_destroyed_reward"},
	],
	"joker": [
		{"id": 760, "name": "Effect: Joker Boosts Clubs", "source": "joker", "targets": ["clubs"], "kind": "boost"},
		{"id": 761, "name": "Effect: Joker Boosts Diamonds", "source": "joker", "targets": ["diamonds"], "kind": "boost"},
		{"id": 762, "name": "Effect: Joker Boosts Hearts", "source": "joker", "targets": ["hearts"], "kind": "boost"},
		{"id": 763, "name": "Effect: Joker Boosts Spades", "source": "joker", "targets": ["spades"], "kind": "boost"},
	],
	"key": [
		{"id": 764, "name": "Effect: Key Destroys Lockbox", "source": "key", "targets": ["lockbox"], "kind": "destroy"},
		{"id": 765, "name": "Effect: Key Destroys Safe", "source": "key", "targets": ["safe"], "kind": "destroy"},
		{"id": 766, "name": "Effect: Key Destroys Treasure Chest", "source": "key", "targets": ["treasure_chest"], "kind": "destroy"},
		{"id": 767, "name": "Effect: Key Destroys Mega Chest", "source": "key", "targets": ["mega_chest"], "kind": "destroy"},
	],
	"king_midas": [
		{"id": 768, "name": "Effect: King Midas adds Coin", "source": "king_midas", "targets": ["coin"], "kind": "add"},
		{"id": 769, "name": "Effect: King Midas Boosts Coin", "source": "king_midas", "targets": ["coin"], "kind": "boost"},
	],
	"light_bulb": [
		{"id": 770, "name": "Effect: Light Bulb Boosts Void Stone", "source": "light_bulb", "targets": ["void_stone"], "kind": "boost", "vtc": "value_multiplier"},
		{"id": 771, "name": "Effect: Light Bulb Boosts Amethyst", "source": "light_bulb", "targets": ["amethyst"], "kind": "boost", "vtc": "value_multiplier"},
		{"id": 772, "name": "Effect: Light Bulb Boosts Pearl", "source": "light_bulb", "targets": ["pearl"], "kind": "boost", "vtc": "value_multiplier"},
		{"id": 773, "name": "Effect: Light Bulb Boosts Shiny Pebble", "source": "light_bulb", "targets": ["shiny_pebble"], "kind": "boost", "vtc": "value_multiplier"},
		{"id": 774, "name": "Effect: Light Bulb Boosts Sapphire", "source": "light_bulb", "targets": ["sapphire"], "kind": "boost", "vtc": "value_multiplier"},
		{"id": 775, "name": "Effect: Light Bulb Boosts Emerald", "source": "light_bulb", "targets": ["emerald"], "kind": "boost", "vtc": "value_multiplier"},
		{"id": 776, "name": "Effect: Light Bulb Boosts Ruby", "source": "light_bulb", "targets": ["ruby"], "kind": "boost", "vtc": "value_multiplier"},
		{"id": 777, "name": "Effect: Light Bulb Boosts Diamond", "source": "light_bulb", "targets": ["diamond"], "kind": "boost", "vtc": "value_multiplier"},
		{"id": 778, "name": "Effect: Light Bulb Destroys Itself", "source": "light_bulb", "targets": [], "kind": "destroy"},
	],
	"lucky_capsule": [
		{"id": 779, "name": "Effect: Lucky Capsule Destroys Itself", "source": "lucky_capsule", "targets": [], "kind": "destroy"},
	],
	"magic_key": [
		{"id": 780, "name": "Effect: Magic Key Destroys Lockbox", "source": "magic_key", "targets": ["lockbox"], "kind": "destroy"},
		{"id": 781, "name": "Effect: Magic Key Destroys Safe", "source": "magic_key", "targets": ["safe"], "kind": "destroy"},
		{"id": 782, "name": "Effect: Magic Key Destroys Treasure Chest", "source": "magic_key", "targets": ["treasure_chest"], "kind": "destroy"},
		{"id": 783, "name": "Effect: Magic Key Destroys Mega Chest", "source": "magic_key", "targets": ["mega_chest"], "kind": "destroy"},
	],
	"magpie": [
		{"id": 784, "name": "Effect: Magpie gain 9 coins", "source": "magpie", "targets": [], "kind": "give"},
	],
	"matryoshka_doll": [
		{"id": 785, "name": "Effect: Matryoshka Doll turns into Matryoshka Doll 1", "source": "matryoshka_doll", "targets": ["matryoshka_doll"], "kind": "transform", "mode": "manual"},
		{"id": 786, "name": "Effect: Matryoshka Doll 1 turns into Matryoshka Doll 2", "source": "matryoshka_doll", "targets": ["matryoshka_doll"], "kind": "transform", "mode": "manual"},
		{"id": 787, "name": "Effect: Matryoshka Doll 2 turn into Matryoshka Doll 3", "source": "matryoshka_doll", "targets": ["matryoshka_doll"], "kind": "transform", "mode": "manual"},
		{"id": 788, "name": "Effect: Matryoshka Doll 3 turn into Matryoshka Doll 4", "source": "matryoshka_doll", "targets": ["matryoshka_doll"], "kind": "transform", "mode": "manual"},
		{"id": 789, "name": "Effect: Matryoshka Doll 4 turn into Matryoshka Doll 5", "source": "matryoshka_doll", "targets": ["matryoshka_doll"], "kind": "transform", "mode": "manual"},
	],
	"midas_bomb": [
		{"id": 790, "name": "Effect: Midas Bomb Destroys Symbols around", "source": "midas_bomb", "targets": [], "kind": "destroy"},
	],
	"mine": [
		{"id": 791, "name": "Effect: Mine adds Ore", "source": "mine", "targets": ["ore"], "kind": "add"},
		{"id": 792, "name": "Effect: Mine adds Mining Pick", "source": "mine", "targets": ["mining_pick"], "kind": "add"},
	],
	"miner": [
		{"id": 793, "name": "Effect: Miner Destroys Ore", "source": "miner", "targets": ["ore"], "kind": "destroy"},
		{"id": 794, "name": "Effect: Miner Destroys Big Ore", "source": "miner", "targets": ["big_ore"], "kind": "destroy"},
	],
	"monkey": [
		{"id": 795, "name": "Effect: Monkey Destroys Banana", "source": "monkey", "targets": ["banana"], "kind": "destroy"},
		{"id": 796, "name": "Effect: Monkey Destroys Coconut", "source": "monkey", "targets": ["coconut"], "kind": "destroy"},
		{"id": 797, "name": "Effect: Monkey Destroys Coconut Half", "source": "monkey", "targets": ["coconut_half"], "kind": "destroy"},
	],
	"moon": [
		{"id": 798, "name": "Effect: Moon Boosts Owl", "source": "moon", "targets": ["owl"], "kind": "boost"},
		{"id": 799, "name": "Effect: Moon Boosts Rabbit", "source": "moon", "targets": ["rabbit"], "kind": "boost"},
		{"id": 800, "name": "Effect: Moon Boosts Wolf", "source": "moon", "targets": ["wolf"], "kind": "boost"},
		{"id": 801, "name": "Effect: Moon adds Cheese", "source": "moon", "targets": ["cheese"], "kind": "add"},
	],
	"mouse": [
		{"id": 802, "name": "Effect: Mouse Destroys Cheese", "source": "mouse", "targets": ["cheese"], "kind": "destroy"},
	],
	"mrs_fruit": [
		{"id": 803, "name": "Effect: Mrs. Fruit Destroys Banana", "source": "mrs_fruit", "targets": ["banana"], "kind": "destroy"},
		{"id": 804, "name": "Effect: Mrs. Fruit Destroys Cherry", "source": "mrs_fruit", "targets": ["cherry"], "kind": "destroy"},
		{"id": 805, "name": "Effect: Mrs. Fruit Destroys Coconut", "source": "mrs_fruit", "targets": ["coconut"], "kind": "destroy"},
		{"id": 806, "name": "Effect: Mrs. Fruit Destroys Coconut Half", "source": "mrs_fruit", "targets": ["coconut_half"], "kind": "destroy"},
		{"id": 807, "name": "Effect: Mrs. Fruit Destroys Orange", "source": "mrs_fruit", "targets": ["orange"], "kind": "destroy"},
		{"id": 808, "name": "Effect: Mrs. Fruit Destroys Peach", "source": "mrs_fruit", "targets": ["peach"], "kind": "destroy"},
	],
	"ninja": [
		{"id": 809, "name": "Effect: Ninja gives 1 less coin", "source": "ninja", "targets": [], "kind": "give"},
	],
	"omelette": [
		{"id": 810, "name": "Effect: Omelette Boosts Cheese", "source": "omelette", "targets": ["cheese"], "kind": "boost"},
		{"id": 811, "name": "Effect: Omelette Boosts Egg", "source": "omelette", "targets": ["egg"], "kind": "boost"},
		{"id": 812, "name": "Effect: Omelette Boosts Milk", "source": "omelette", "targets": ["milk"], "kind": "boost"},
		{"id": 813, "name": "Effect: Omelette Boosts Golden Egg", "source": "omelette", "targets": ["golden_egg"], "kind": "boost"},
		{"id": 814, "name": "Effect: Omelette Boosts Omelette", "source": "omelette", "targets": ["omelette"], "kind": "boost"},
	],
	"owl": [
		{"id": 815, "name": "Effect: Owl Gives 1 more", "source": "owl", "targets": [], "kind": "give"},
	],
	"oyster": [
		{"id": 816, "name": "Effect: Oyster adds Pearl", "source": "oyster", "targets": ["pearl"], "kind": "add"},
	],
	"peach": [
	],
	"pear": [
		{"id": 818, "name": "Effect: Pear give 1 more Coin", "source": "pear", "targets": ["coin"], "kind": "give", "mode": "target_boost"},
	],
	"pirate": [
		{"id": 819, "name": "Effect: Pirate Destroys Anchor", "source": "pirate", "targets": ["anchor"], "kind": "destroy"},
		{"id": 820, "name": "Effect: Pirate Destroys Beer", "source": "pirate", "targets": ["beer"], "kind": "destroy"},
		{"id": 821, "name": "Effect: Pirate Destroys Coin", "source": "pirate", "targets": ["coin"], "kind": "destroy"},
		{"id": 822, "name": "Effect: Pirate Destroys Lockbox", "source": "pirate", "targets": ["lockbox"], "kind": "destroy"},
		{"id": 823, "name": "Effect: Pirate Destroys Safe", "source": "pirate", "targets": ["safe"], "kind": "destroy"},
		{"id": 824, "name": "Effect: Pirate Destroys Orange", "source": "pirate", "targets": ["orange"], "kind": "destroy"},
		{"id": 825, "name": "Effect: Pirate Destroys Treasure Chest", "source": "pirate", "targets": ["treasure_chest"], "kind": "destroy"},
		{"id": 826, "name": "Effect: Pirate Destroys Mega Chest", "source": "pirate", "targets": ["mega_chest"], "kind": "destroy"},
	],
	"present": [
		{"id": 827, "name": "Effect: Present Destroys itself", "source": "present", "targets": [], "kind": "destroy", "mode": "manual"},
	],
	"pufferfish": [
		{"id": 828, "name": "Effect: Pufferfish give 1 Reroll Token", "source": "pufferfish", "targets": [], "kind": "give", "currency": "reroll_token", "mode": "removed_or_destroyed_reward"},
	],
	"rabbit": [
		{"id": 829, "name": "Effect: Rabbit gives 2 more", "source": "rabbit", "targets": [], "kind": "give"},
	],
	"rain": [
		{"id": 830, "name": "Effect: Rain Boosts Flower", "source": "rain", "targets": ["flower"], "kind": "boost"},
		{"id": 831, "name": "Effect: Rain Boosts Seed Growing", "source": "rain", "targets": ["seed"], "kind": "boost"},
	],
	"removal_capsule": [
		{"id": 832, "name": "Effect: Removal Capsule Gives 1 Destroy Token", "source": "removal_capsule", "targets": [], "kind": "give"},
	],
	"reroll_capsule": [
		{"id": 833, "name": "Effect: Reroll Capsule Gives 1 Reroll Token", "source": "reroll_capsule", "targets": [], "kind": "give", "currency": "reroll_token"},
	],
	"robin_hood": [
		{"id": 834, "name": "Effect: Robin Hood Makes Bronze Arrow give 3 Coins", "source": "robin_hood", "targets": ["bronze_arrow"], "kind": "give"},
		{"id": 835, "name": "Effect: Robin Hood Makes Silver Arrow give 3 coins", "source": "robin_hood", "targets": ["silver_arrow"], "kind": "give"},
		{"id": 836, "name": "Effect: Robin Hood Makes Golden Arrow give 3 coins", "source": "robin_hood", "targets": ["golden_arrow"], "kind": "give"},
		{"id": 837, "name": "Effect: Robin Hood Makes Thief give 3 coins", "source": "robin_hood", "targets": ["thief"], "kind": "give"},
		{"id": 838, "name": "Effect: Robin Hood Destroys Billionare", "source": "robin_hood", "targets": ["billionaire"], "kind": "destroy"},
		{"id": 839, "name": "Effect: Robin Hood Destroys Target", "source": "robin_hood", "targets": ["target"], "kind": "destroy"},
		{"id": 840, "name": "Effect: Robin Hood Destroys Apple", "source": "robin_hood", "targets": ["apple"], "kind": "destroy"},
	],
	"ruby": [
		{"id": 841, "name": "Effect: Ruby Boosts Ruby", "source": "ruby", "targets": ["ruby"], "kind": "boost"},
	],
	"sand_dollar": [
	],
	"silver_arrow": [
		{"id": 842, "name": "Effect: Silver Arrow Boosts a Symbol", "source": "silver_arrow", "targets": [], "kind": "boost"},
		{"id": 843, "name": "Effect: Silver Arrow Destroys Target", "source": "silver_arrow", "targets": ["target"], "kind": "destroy"},
	],
	"sloth": [
		{"id": 844, "name": "Effect: Sloth gives 4 coins", "source": "sloth", "targets": [], "kind": "give"},
	],
	"snail": [
		{"id": 845, "name": "Effect: Snail gives 5 coins", "source": "snail", "targets": [], "kind": "give"},
	],
	"spades": [
		{"id": 846, "name": "Effect: Spades Boosts Spades", "source": "spades", "targets": ["spades"], "kind": "boost"},
		{"id": 847, "name": "Effect: Spades Boosts Clubs", "source": "spades", "targets": ["clubs"], "kind": "boost"},
	],
	"strawberry": [
		{"id": 848, "name": "Effect: Strawberry Boosts Strawberry", "source": "strawberry", "targets": ["strawberry"], "kind": "boost"},
	],
	"sun": [
		{"id": 849, "name": "Effect: Sun Boosts Flower", "source": "sun", "targets": ["flower"], "kind": "boost"},
		{"id": 850, "name": "Effect: Sun Boosts Seed Growth", "source": "sun", "targets": ["seed"], "kind": "boost"},
	],
	"tedium_capsule": [
		{"id": 857, "name": "Effect: Tedium Capsule Destroys itself", "source": "tedium_capsule", "targets": [], "kind": "destroy"},
	],
	"thief": [
		{"id": 851, "name": "Effect: Thief Removes Coin", "source": "thief", "targets": ["coin"], "kind": "remove_coin", "mode": "thief_spin"},
	],
	"three_sided_die": [
		{"id": 852, "name": "Effect: Three-Sided Die Roll", "source": "three_sided_die", "targets": [], "kind": "roll"},
		{"id": 1118, "name": "Effect: Three-Sided Die Destroys Gambler", "source": "three_sided_die", "targets": ["gambler"], "kind": "destroy"},
	],
	"time_capsule": [
		{"id": 853, "name": "Effect: Time Capsule Destroys itself", "source": "time_capsule", "targets": [], "kind": "destroy"},
	],
	"toddler": [
		{"id": 854, "name": "Effect: Toddler Destroys Candy", "source": "toddler", "targets": ["candy"], "kind": "destroy"},
		{"id": 855, "name": "Effect: Toddler Destroys Pinata", "source": "toddler", "targets": ["pinata"], "kind": "destroy"},
		{"id": 856, "name": "Effect: Toddler Destroys Present", "source": "toddler", "targets": ["present"], "kind": "destroy"},
		{"id": 867, "name": "Effect: Toddler Destroys Bubble", "source": "toddler", "targets": ["bubble"], "kind": "destroy"},
	],
	"tomb": [
		{"id": 868, "name": "Effect: Tomb adds Spirit", "source": "tomb", "targets": ["spirit"], "kind": "add"},
	],
	"turtle": [
		{"id": 869, "name": "Effect: Turtle Gives 4 Coins", "source": "turtle", "targets": [], "kind": "give"},
	],
	"void_creature": [
		{"id": 871, "name": "Effect: Void Creature Gives 8 Coins", "source": "void_creature", "targets": [], "kind": "give", "mode": "void_destroy_bonus"},
	],
	"void_fruit": [
		{"id": 873, "name": "Effect: Void Fruit Gives 8 Coins", "source": "void_fruit", "targets": [], "kind": "give", "mode": "void_destroy_bonus"},
	],
	"void_stone": [
		{"id": 875, "name": "Effect: Void Stone Gives 8 Coins", "source": "void_stone", "targets": [], "kind": "give", "mode": "void_destroy_bonus"},
	],
	"watermelon": [
		{"id": 876, "name": "Effect: Watermelon Boosts Watermelon", "source": "watermelon", "targets": ["watermelon"], "kind": "boost"},
	],
	"wealthy_capsule": [
		{"id": 877, "name": "Effect: Wealthy Capsule Gives 10 Coins", "source": "wealthy_capsule", "targets": [], "kind": "give"},
	],
	"wildcard": [
		{"id": 878, "name": "Effect: Wildcard Copies a Symbol", "source": "wildcard", "targets": [], "kind": "copy"},
	],
	"wine": [
		{"id": 879, "name": "Effect: Wine Gives 1 more Coin", "source": "wine", "targets": [], "kind": "give"},
	],
	"witch": [
		{"id": 880, "name": "Effect: Witch Boosts Cat", "source": "witch", "targets": ["cat"], "kind": "boost"},
		{"id": 881, "name": "Effect: Witch Boosts Owl", "source": "witch", "targets": ["owl"], "kind": "boost"},
		{"id": 882, "name": "Effect: Witch Boosts Crow", "source": "witch", "targets": ["crow"], "kind": "boost"},
		{"id": 883, "name": "Effect: Witch Boosts Apple", "source": "witch", "targets": ["apple"], "kind": "boost"},
		{"id": 884, "name": "Effect: Witch Boosts Hex of Destruction", "source": "witch", "targets": ["hex_of_destruction"], "kind": "boost"},
		{"id": 885, "name": "Effect: Witch Boosts Hex of Draining", "source": "witch", "targets": ["hex_of_draining"], "kind": "boost"},
		{"id": 886, "name": "Effect: Witch Boosts Hex of Emptiness", "source": "witch", "targets": ["hex_of_emptiness"], "kind": "boost"},
		{"id": 887, "name": "Effect: Witch Boosts Hex of Hoarding", "source": "witch", "targets": ["hex_of_hoarding"], "kind": "boost"},
		{"id": 888, "name": "Effect: Witch Boosts Hex of Midas", "source": "witch", "targets": ["hex_of_midas"], "kind": "boost"},
		{"id": 889, "name": "Effect: Witch Boosts Hex of Tedium", "source": "witch", "targets": ["hex_of_tedium"], "kind": "boost"},
		{"id": 890, "name": "Effect: Witch Boosts Hex of Thievery", "source": "witch", "targets": ["hex_of_thievery"], "kind": "boost"},
		{"id": 891, "name": "Effect: Witch Boosts Eldritch Creature", "source": "witch", "targets": ["eldritch_creature"], "kind": "boost"},
		{"id": 892, "name": "Effect: Witch Boosts Spirit", "source": "witch", "targets": ["spirit"], "kind": "boost"},
	],
}

static func rules_for_source(source_key):
	return EFFECT_RULES_BY_SOURCE.get(str(source_key), []).duplicate(true)

static func source_count():
	return EFFECT_RULES_BY_SOURCE.size()
