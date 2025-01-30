import json
import constants


maps = []
locations = []

maps.append({"name": "menu", "location_size": 22, "location_border_thickness": 1, "img": "images/menu.png"})

line = 12
for z in [iz for iz in sorted(constants.zones_base[:6], key=lambda iz: iz.playedin)]:
    for stage in range(1,4): # 3 stages for each
        col = 348
        zone = f"{z.zone}{stage}"
        maps.append({
            "name": zone, "location_size": 12, "location_border_thickness": 1, "img": f"images/{zone.upper()}.png"
        })
        loco = {"name": zone, "access_rules": [f"{z.long} Key"], 
                "chest_unopened_img": "images/monitor_o.png","chest_opened_img": "images/monitor_x.png",
                "children": []
        }
        for m in constants.monitor_by_zone[zone]:
            loco["children"].append({
                "name": m.name, 
                "map_locations": [
                    {"map": zone, "x": m.x/constants.map_data[zone]["scale"], "y": m.y/constants.map_data[zone]["scale"]},
                    {"map": "menu", "x": col, "y": line},
                ],
                "sections": [{"name": m.name}]
            })
            col += 24
        locations.append(loco)
        line += 24

locations.append({"name": "Bosses", "children": [
  {"name": "Green Hill 3 Boss",  "map_locations": [{"map": "menu", "x": 324, "y": 540}],
     "sections": [{"name": "Green Hill 3 Boss", "access_rules":["Green Hill Key"]}]},
  {"name": "Marble Zone 3 Boss", "map_locations": [{"map": "menu", "x": 348, "y": 540}],
     "sections": [{"name": "Marble Zone 3 Boss", "access_rules":["Marble Zone Key"]}]},
  {"name": "Spring Yard 3 Boss", "map_locations": [{"map": "menu", "x": 372, "y": 540}],
     "sections": [{"name": "Spring Yard 3 Boss", "access_rules":["Spring Yard Key"]}]},
  {"name": "Labyrinth 3 Boss",   "map_locations": [{"map": "menu", "x": 396, "y": 540}],
     "sections": [{"name": "Labyrinth 3 Boss", "access_rules":["Labyrinth Key"]}]},
  {"name": "Starlight 3 Boss",   "map_locations": [{"map": "menu", "x": 420, "y": 540}],
     "sections": [{"name": "Starlight 3 Boss", "access_rules":["Starlight Key"]}]},
  {"name": "Final Zone Boss",    "map_locations": [{"map": "menu", "x": 444, "y": 540}],
     "sections": [{"name": "Final Zone Boss", "access_rules":["Final Zone Key"]}]},
]})

locations.extend([
  {"name": "Special Stage 1", "access_rules":["Special Stage 1 Key"], "children": [
    {"name": "Special Stage 1",  "map_locations": [{"map": "menu", "x": 372, "y": 468}], 
     "sections": [{"name": "Special Stage 1"}]}]},
  {"name": "Special Stage 2", "parent": "Special Stage 1", "access_rules":["Special Stage 2 Key"], "children": [
    {"name": "Special Stage 2",  "map_locations": [{"map": "menu", "x": 420, "y": 468}],
     "sections": [{"name": "Special Stage 2"}]}]},
  {"name": "Special Stage 3", "parent": "Special Stage 2", "access_rules":["Special Stage 3 Key"], "children": [
    {"name": "Special Stage 3",  "map_locations": [{"map": "menu", "x": 468, "y": 468}],
     "sections": [{"name": "Special Stage 3"}]}]},
  {"name": "Special Stage 4", "parent": "Special Stage 3", "access_rules":["Special Stage 4 Key"], "children": [
    {"name": "Special Stage 4",  "map_locations": [{"map": "menu", "x": 516, "y": 468}],
     "sections": [{"name": "Special Stage 4"}]}]},
  {"name": "Special Stage 5", "parent": "Special Stage 4", "access_rules":["Special Stage 5 Key"], "children": [
    {"name": "Special Stage 5",  "map_locations": [{"map": "menu", "x": 564, "y": 468}],
     "sections": [{"name": "Special Stage 5"}]}]},
  {"name": "Special Stage 6", "parent": "Special Stage 5", "access_rules":["Special Stage 6 Key"], "children": [
    {"name": "Special Stage 6",  "map_locations": [{"map": "menu", "x": 612, "y": 468}],
     "sections": [{"name": "Special Stage 6"}]}]}
])

for i in range(1,7):
    maps.append({
        "name": f"special_stage_{i}", "location_size": 18, "location_border_thickness": 2, "img": f"images/SpecialStage_{i}.png"
    })
    
maps.append({"name": "fz", "location_size": 18, "location_border_thickness": 2, "img": "images/FZ.png"})

json.dump(maps, open("tracker/maps/maps.json","w"), indent=4)
json.dump(locations, open("tracker/locations/locations.json","w"), indent=4)

