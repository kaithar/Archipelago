import os
import pkgutil
from typing import ClassVar, List

from worlds.AutoWorld import World
from worlds.generic.Rules import add_rule, set_rule, forbid_item, add_item_rule

from BaseClasses import CollectionState, Entrance, Item, Region

from . import constants, configurable, client, locations  # noqa: F401

class Sonic1World(World):
    """
    Beginning to go fast, Sonic 1991
    """

    game = "Sonic the Hedgehog 1"
    data_version = 1
    item_name_to_id= constants.item_name_to_id
    location_name_to_id = constants.location_name_to_id

    settings_key = "sonic1_settings"
    settings: ClassVar[configurable.Sonic1Settings]

    def create_item(self, name: str) -> Item:
        item = constants.item_by_name[name]
        return locations.S1Item(name, item.itemclass, item.id, self.player)

    def create_items(self) -> None:
        exclude = ["Special Stages Key", self.random.choice(constants.possible_starters)]
        for item in constants.item_by_idx.values():
            oi = locations.S1Item(item.name, item.itemclass, item.id, self.player)
            if item.name in exclude:
                self.multiworld.push_precollected(oi)
                exclude.remove(item.name)
            else:
                self.multiworld.itempool.append(oi)

    def create_regions(self):
        menu = Region('Menu', self.player, self.multiworld)
        self.multiworld.regions.append(menu)
        regions: dict[str, locations.S1Region] = {}
        for z in constants.zones_base:
            if len(z.acts) == 3:
                hub = locations.S1HubRegion(z.long, self.player, self.multiworld)
                rs = [
                    locations.S1Region(z, 1, self.player, self.multiworld),
                    locations.S1Region(z, 2, self.player, self.multiworld),
                    locations.S1Region(z, 3, self.player, self.multiworld)]
                es: list[Entrance] = [
                    locations.S1A1Entrance(self.player, f"{z.long} 1", hub),
                    locations.S1A2Entrance(self.player, f"{z.long} 2", hub),
                    locations.S1A3Entrance(self.player, f"{z.long} 3", hub)]
                for r,e in zip(rs,es):
                    regions[r.name] = r
                    self.multiworld.regions.append(r)
                    hub.exits.append(e)
                    e.connect(r)
                    for m in constants.monitor_by_zone[r.zone]:
                        mo = locations.S1Monitor(self.player, m, r)
                        add_item_rule(mo, lambda item: item.name not in constants.item_name_groups["keys"])
                        r.locations.append(mo)
                regions[hub.name] = hub
                self.multiworld.regions.append(hub)
                he = locations.S1HubEntrance(self.player, z.long, menu)
                menu.exits.append(he)
                he.connect(hub)
        # Now the Final Zone...
        r = locations.S1Region(constants.zones_base[6], 1, self.player, self.multiworld)
        regions[r.name] = r
        self.multiworld.regions.append(r)
        e = locations.S1FinalEntrance(self.player, r.name, menu)
        menu.exits.append(e)
        e.connect(r)
        # Setup the bosses...
        for b in constants.boss_by_idx.values():
           r = regions[b.region]
           mo = locations.S1Boss(self.player, b, r)
           add_item_rule(mo, lambda item: item.name not in constants.item_name_groups["keys"])
           r.locations.append(mo)
        # And Specials...
        specials: List[locations.S1Region] = []
        for ssid in range(1,7):
            r = locations.S1Region(constants.zones_base[7], ssid, self.player, self.multiworld)
            regions[r.name] = r
            self.multiworld.regions.append(r)
            if not specials:    
                e = locations.S1SSEntrance(self.player, r.name, menu)
                menu.exits.append(e)
            else:
                e = locations.S1SSEntrance(self.player, r.name, specials[-1])
                specials[-1].exits.append(e)
            e.connect(r)
            mo = locations.S1Special(self.player, constants.special_by_idx[ssid], r)
            add_item_rule(mo, lambda item: item.name not in constants.item_name_groups["keys"])
            r.locations.append(mo)
            specials.append(r)
      
        # from Utils import visualize_regions
        # visualize_regions(self.multiworld.get_region("Menu", self.player), "my_world.puml")
    def set_rules(self):
        mwge = self.multiworld.get_entrance
        set_rule(mwge("Green Hill", self.player),  lambda state: state.has("Green Hill Key", self.player))
        set_rule(mwge("Marble Zone", self.player), lambda state: state.has("Marble Zone Key", self.player))
        set_rule(mwge("Spring Yard", self.player), lambda state: state.has("Spring Yard Key", self.player))
        set_rule(mwge("Labyrinth", self.player),   lambda state: state.has("Labyrinth Key", self.player))
        set_rule(mwge("Starlight", self.player),   lambda state: state.has("Starlight Key", self.player))
        set_rule(mwge("Scrap Brain", self.player), lambda state: state.has("Scrap Brain Key", self.player))
        set_rule(mwge("Final Zone", self.player),  lambda state: state.has("Final Zone Key", self.player))
        set_rule(mwge("Special Stage 1", self.player), lambda state: state.has("Special Stages Key", self.player))
        for ssid in range(1,7):
            set_rule(mwge(f"Special Stage {ssid}", self.player), lambda state: state.has(f"Special Stage {ssid} Key", self.player))
        def completion_check(state: CollectionState):
            for c in constants.completion:
                if not state.can_reach_location(c, self.player):
                    return False
            for c in ['Emerald 1','Emerald 2','Emerald 3','Emerald 4','Emerald 5','Emerald 6']:
                if not state.has(c,self.player):
                    return False
            return True
        self.multiworld.completion_condition[self.player] = lambda state: completion_check(state)

    def generate_output(self, output_directory: str) -> None:
        patch = configurable.Sonic1ProcedurePatch(player=self.player, player_name=self.player_name)
        patch.write_file("sonic1-ap.bsdiff4", pkgutil.get_data(__name__, "sonic1-ap.bsdiff4"))
        out_file_name = self.multiworld.get_out_file_name_base(self.player)
        patch.write(os.path.join(output_directory, f"{out_file_name}{patch.patch_file_ending}"))

