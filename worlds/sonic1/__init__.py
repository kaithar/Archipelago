import os
from typing import ClassVar, List
import typing

import BaseClasses
from worlds.AutoWorld import World, WebWorld
from worlds.generic.Rules import set_rule, add_item_rule

from BaseClasses import CollectionState, Entrance, Item, Region, Tutorial

from . import constants, configurable, client, locations  # noqa: F401

class Sonic1WebWorld(WebWorld):
    option_groups = [configurable.ring_options,configurable.special_generics]
    tutorials = [Tutorial(
        "Sonic 1 Setup Guide", "A short guide to setting up Sonic 1 for Archipelago",
        "English", "setup_en.md", "setup/en", ["Kaithar"])]

def map_key_index(idx):
    return int(idx or 0)

class Sonic1World(World):
    """
    Beginning to go fast, Sonic 1991
    """

    game = "Sonic the Hedgehog 1"
    data_version = 1
    item_name_to_id= constants.item_name_to_id
    location_name_to_id = constants.location_name_to_id
    item_name_groups = constants.item_name_groups

    settings_key = "sonic1_settings"
    settings: ClassVar[configurable.Sonic1Settings]

    options_dataclass = configurable.Sonic1GameOptions
    options: configurable.Sonic1GameOptions

    tracker_world = {
        "map_page_folder": "tracker",
        "map_page_maps": "maps/maps.json",
        "map_page_locations": "locations/locations.json",
        "map_page_setting_key": "sonic1_area",
        "map_page_index": map_key_index,
    }

    web = Sonic1WebWorld()

    def generate_early(self):
        super().generate_early()
        # So, we care about making this sane...
        if self.options.ring_goal.value > self.options.available_rings.value:
            # This is going to be really bad, so we correct that here
            # Per the option description, ring_goal wins.
            self.options.ring_goal.value = self.options.available_rings.value

    def create_item(self, name: str) -> Item:
        item = constants.item_by_name[name]
        return locations.S1Item(name, getattr(BaseClasses.ItemClassification,item.itemclass), item.id, self.player)

    def create_items(self) -> None:
        local_items = ["Special Stages Key", self.random.choice(constants.possible_starters)]
        item_prep = constants.core_items.copy()
        to_push: typing.List[typing.List] = []
        to_keep: typing.List[typing.List] = []

        if self.options.allow_disable_goal:
            item_prep.append(constants.goal_item)
        if self.options.allow_disable_r:
            item_prep.append(constants.r_item)

        for item in item_prep:
            if item[0] in local_items:
                to_keep.append(item)
            else:
                to_push.append(item)

        requested_rings = self.options.available_rings.value - self.options.ring_goal.value
        to_push.extend([constants.prog_ring]*self.options.ring_goal.value)
        to_push.extend([constants.fill_ring]*requested_rings)

        filler_needed = constants.location_total - len(to_push)
        if not self.options.boring_filler:
            for item in self.random.sample(constants.silly_filler,min(filler_needed//2,len(constants.silly_filler))):
                to_push.append(item)
        
        filler_needed = constants.location_total - len(to_push)
        to_push.extend([constants.boring_filler]*filler_needed)
        for src,dst in ((to_keep,self.multiworld.push_precollected), (to_push, self.multiworld.itempool.append)):
            for i in src:
                item = constants.item_by_idx[i[1]]
                oi = locations.S1Item(item.name, getattr(BaseClasses.ItemClassification,item.itemclass), item.id, self.player)
                dst(oi)

    def create_regions(self):
        menu = Region('Menu', self.player, self.multiworld)
        self.multiworld.regions.append(menu)
        regions: dict[str, locations.S1Region] = {}
        exclusion_locations = []
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
                        exclusion_locations.append(mo)
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
           exclusion_locations.append(mo)
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
            exclusion_locations.append(mo)
            r.locations.append(mo)
            specials.append(r)
        
        if self.options.no_local_keys:
            for mo in exclusion_locations:
                add_item_rule(mo, lambda item: item.name not in constants.item_name_groups["keys"])
      
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
            for c in constants.emeralds:
                if not state.has(c,self.player):
                    return False
            return state.has_group("rings",self.player,self.options.ring_goal.value)
        self.multiworld.completion_condition[self.player] = lambda state: completion_check(state)

    def generate_output(self, output_directory: str) -> None:
        patch = configurable.Sonic1ProcedurePatch(player=self.player, player_name=self.player_name)
        out_file_name = self.multiworld.get_out_file_name_base(self.player)
        patch.write(os.path.join(output_directory, f"{out_file_name}{patch.patch_file_ending}"))

    def fill_slot_data(self):
        return self.options.as_dict("hard_mode","ring_goal")

