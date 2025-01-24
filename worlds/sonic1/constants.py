from collections import namedtuple
from typing import Dict, List

from BaseClasses import ItemClassification
id_base = 3141501000

_zoneraw = namedtuple("BaseZone", [
    "zone", "id", "playedin", "long", "acts"
])
zones_base = [
  _zoneraw(*z) for z in [
    ("GH",  0, 0, "Green Hill",   (1,2,3)),
    ("LZ",  1, 3, "Labyrinth",    (1,2,3)),
    ("MZ",  2, 1, "Marble Zone",  (1,2,3)),
    ("SLZ", 3, 4, "Starlight",    (1,2,3)),
    ("SYZ", 4, 2, "Spring Yard",  (1,2,3)),
    ("SB",  5, 5, "Scrap Brain",  (1,2,3)),
    ("END", 6, 6, "Final Zone",   (1,)   ), # exceptional...
    ("SS",  7, 7, "Special Stage",(1,2,3,4,5,6))  # this one too
]]


# Decompress that...
zones = [z.zone for z in zones_base] # This is "wrong" because the ids are out of order.
zones_long = [z.long for z in zones_base]
play_order = [z.zone for z in sorted(zones_base, key=lambda z: z.playedin)]
zone_names = {
    f"{z.zone}{a if len(z.acts)>1 else''}":
    f"{z.long}{(' ' + str(a)) if len(z.acts)>1 else''}"
    for z in zones_base for a in z.acts 
}

_monitor = namedtuple("Monitor", ["zone", "id", "idx", "name"])

monitor_by_zone: Dict[str,List[_monitor]] = {}
monitor_by_id: Dict[int,_monitor] = {}
monitor_by_idx: Dict[int,_monitor] = {}
monitor_by_name: Dict[str,_monitor] = {}
regions = []
regions_by_id = {}

location_name_to_id = {}

monitorcount = [10,10,20,10,11,6,6,3,11,5,9,17,15,8,17,15,25,7]

idcount = 1
for z in play_order[:6]: # My monitor counts are in play order but I only want the 6 real zones
      for stage in range(1,4): # 3 stages for each
          for i in range(monitorcount.pop(0)): # loop to make the right number of monitors
              zone = f"{z}{stage}"
              m = _monitor(zone=zone, id=id_base+idcount, idx=idcount, name=f"{zone_names[zone]} Monitor ({idcount})")
              idcount += 1
              monitor_by_zone.setdefault(m.zone, []).append(m)
              monitor_by_name[m.name] = m
              monitor_by_id[m.id] = m
              monitor_by_idx[m.idx] = m
              location_name_to_id[m.name] = m.id

bosses = [
    ["Green Hill 3",  1, 211],
    ["Marble Zone 3", 2, 212],
    ["Spring Yard 3", 3, 213],
    ["Labyrinth 3",   4, 214],
    ["Starlight 3",   5, 215],
    ["Final Zone",    6, 216]
]
_boss = namedtuple('Boss', ['region', 'name', 'idx', 'id'])

boss_by_id: Dict[int,_boss] = {}
boss_by_idx: Dict[int,_boss] = {}
boss_by_name: Dict[str,_boss] = {}

for b in bosses:
    _b = _boss(b[0], f"{b[0]} Boss", b[1], b[2]+id_base)
    boss_by_id[_b.id] = _b
    boss_by_idx[_b.idx] = _b
    boss_by_name[_b.name] = _b
    location_name_to_id[_b.name] = _b.id

specials = [
    ["Special Stage 1", 1, 221],
    ["Special Stage 2", 2, 222],
    ["Special Stage 3", 3, 223],
    ["Special Stage 4", 4, 224],
    ["Special Stage 5", 5, 225],
    ["Special Stage 6", 6, 226],
]

_special = namedtuple('Special', ['name', 'idx', 'id'])

special_by_id: Dict[int,_special] = {}
special_by_idx: Dict[int,_special] = {}
special_by_name: Dict[str,_special] = {}

for b in specials:
    _b = _special(b[0], b[1], b[2]+id_base)
    special_by_id[_b.id] = _b
    special_by_idx[_b.idx] = _b
    special_by_name[_b.name] = _b
    location_name_to_id[_b.name] = _b.id

items = [
    ["Emerald 1",           1, ItemClassification.progression],
    ["Emerald 2",           2, ItemClassification.progression],
    ["Emerald 3",           3, ItemClassification.progression],
    ["Emerald 4",           4, ItemClassification.progression],
    ["Emerald 5",           5, ItemClassification.progression],
    ["Emerald 6",           6, ItemClassification.progression],
    ["Disable GOAL blocks", 7, ItemClassification.useful],
    ["Disable R blocks",    8, ItemClassification.useful],
    ["Green Hill Key",      9, ItemClassification.progression],
    ["Marble Zone Key",    10, ItemClassification.progression],
    ["Spring Yard Key",    11, ItemClassification.progression],
    ["Labyrinth Key",      12, ItemClassification.progression],
    ["Starlight Key",      13, ItemClassification.progression],
    ["Scrap Brain Key",    14, ItemClassification.progression],
    ["Final Zone Key",     15, ItemClassification.progression],
    ["Special Stages Key", 16, ItemClassification.progression], # Dummy key
    ["Special Stage 1 Key",17, ItemClassification.progression],
    ["Special Stage 2 Key",18, ItemClassification.progression],
    ["Special Stage 3 Key",19, ItemClassification.progression],
    ["Special Stage 4 Key",20, ItemClassification.progression],
    ["Special Stage 5 Key",21, ItemClassification.progression],
    ["Special Stage 6 Key",22, ItemClassification.progression]
]

possible_starters = [ "Green Hill Key", "Marble Zone Key", "Spring Yard Key", "Labyrinth Key", "Starlight Key", "Scrap Brain Key"]

# Specials and Emeralds cancel out. 205 monitors+6 bosses vs 2 buffs+8 zones+6 specials, 195 rings needed
# Except... the dummy key and one of the 6 proper zone keys are prefilled, so we need an extra 2 rings
# For reasons of sanity, 10 are considered "useful" and the rest are "filler"
# In theory that means some will definitely show up but won't flood the useful spots.
items.extend([[f"Ring {i}", 22+i, ItemClassification.useful] for i in range(1,11)])
items.extend([[f"Ring {i}", 22+i, ItemClassification.filler] for i in range(11,198)])

_item = namedtuple('Item', ['name', 'idx','id','itemclass'])
item_name_to_id: Dict[str, int] = {}
item_by_id: Dict[int,_item] = {}
item_by_idx: Dict[int,_item] = {}
item_by_name: Dict[str,_item] = {}

item_name_groups: Dict[str,set[str]] = {
    "keys": {item[0] for item in items if "Key" in item[0]}
}

for item in items:
    _i = _item(item[0],item[1],item[1]+id_base,item[2])
    item_by_id[_i.id] = item_by_idx[_i.idx] = item_by_name[_i.name] = _i
    item_name_to_id[_i.name] = _i.id

victory_id = id_base+500

# Completion locations needed:
completion = [
    'Green Hill 3 Boss',
    'Marble Zone 3 Boss',
    'Spring Yard 3 Boss',
    'Labyrinth 3 Boss',
    'Starlight 3 Boss',
    'Final Zone Boss',
    'Special Stage 1',
    'Special Stage 2',
    'Special Stage 3',
    'Special Stage 4',
    'Special Stage 5',
    'Special Stage 6',
]
