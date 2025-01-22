from typing import ClassVar, List

from worlds.AutoWorld import World

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
    settings = ClassVar[configurable.Sonic1Settings]

    def create_item(self, name: str) -> Item:
        item = constants.item_by_name[name]
        return locations.S1Item(name, item.itemclass, item.id, self.player)

    def create_items(self) -> None:
        for item in constants.item_by_idx.values():
           self.multiworld.itempool.append(locations.S1Item(item.name, item.itemclass, item.id, self.player))

    def create_regions(self):
        menu = Region('Menu', self.player, self.multiworld)
        self.multiworld.regions.append(menu)
        regions: dict[str, locations.S1Region] = {}
        for z in constants.zones_base:
            if len(z.acts) == 3:
                rs = [
                    locations.S1Region(z, 1, self.player, self.multiworld),
                    locations.S1Region(z, 2, self.player, self.multiworld),
                    locations.S1Region(z, 3, self.player, self.multiworld)]
                es: list[Entrance] = [
                    locations.S1A1Entrance(self.player, f"{z.long} 1", menu),
                    locations.S1A2Entrance(self.player, f"{z.long} 2", menu),
                    locations.S1A3Entrance(self.player, f"{z.long} 3", menu)]
                for r,e in zip(rs,es):
                    regions[r.name] = r
                    self.multiworld.regions.append(r)
                    menu.exits.append(e)
                    e.connect(r)

                    for m in constants.monitor_by_zone[r.zone]:
                        mo = locations.S1Monitor(self.player, m, r)
                        r.locations.append(mo)
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
           r.locations.append(locations.S1Boss(self.player, b, r))
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
            r.locations.append(locations.S1Special(self.player, constants.special_by_idx[ssid], r))
            specials.append(r)
      
        # from Utils import visualize_regions
        # visualize_regions(self.multiworld.get_region("Menu", self.player), "my_world.puml")
    def set_rules(self):
       def completion_check(state: CollectionState):
          for c in constants.completion:
              if not state.can_reach_location(c, self.player):
                return False
          for c in ['Emerald 1','Emerald 2','Emerald 3','Emerald 4','Emerald 5','Emerald 6']:
             if not state.has(c,self.player):
                return False
          return True
       self.multiworld.completion_condition[self.player] = lambda state: completion_check(state)
