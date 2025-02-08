import logging
import struct
import typing

from NetUtils import ClientStatus
from worlds._bizhawk.client import BizHawkClient
from worlds._bizhawk import read, write, display_message
from . import constants

logger = logging.getLogger("Client")

MAGIC_BROKEN = 0x0
MAGIC_UNBROKEN = 0x1F
MAGIC_EMPTY_SEED = ' '*20

class SegaSRAM(object):
    _raw: typing.List[bytes]
    clean_data: bytes
    byte_count: int
    ram_type = 0
    format: str = ""
    fields = ()
    staged: typing.List[typing.Tuple]
    extra_addresses: typing.List[typing.Tuple[int,int,str]]
    extra_data: typing.List[bytes]

    def __init__(self, format, ram_type=0):
        '''Ram_type 0 for even addresses, 1 for odd addresses, 2 for both'''
        self._raw = []
        self.set_format(format)
        self.ram_type = ram_type
        self.staged = []
        self.extra_addresses = []
        self.extra_data = []
    
    def set_format(self, format: str):
        self.format = format
        self.byte_count = struct.calcsize(format)*(1 if self.ram_type == 2 else 2)
        if self.byte_count%2 != 0: # Memory is 16 bit aligned.
            self.byte_count += 1

    async def read_bytes(self, ctx, clear_stage=True):
        if clear_stage:
            self.staged = []
        data = await read(ctx.bizhawk_ctx, [(0x0, self.byte_count, "SRAM"),]+self.extra_addresses)
        self._raw = data[0]
        self.extra_data = data[1:]
        # Because of 8bit sram stupidity, we're probably going to need to unpack this by dropping every other byte.
        # So:
        if self.ram_type == 0:
          self.clean_data = bytes([data[0][i] for i in range(0,len(data[0]), 2)])
        elif self.ram_type == 1:
          self.clean_data = bytes([data[0][i] for i in range(1,len(data[0]), 2)])
        else:
          self.clean_data = data[0]
        self.fields = struct.unpack(self.format,self.clean_data)
        #seed_name = ''.join([chr(c) for c in clean_data[-20:]])
        #logger.info(f"Data... {clean_data=} ({len(clean_data)=}) {seed_name=} {len(seed_name)=}")
        # We're only caring about the seed in the start.
    
    async def full_write(self, ctx, data, clear_stage=True):
        if clear_stage:
            self.staged = []
        self.fields = tuple(data)
        self.clean_data = struct.pack(self.format, *data)
        wrdata = []
        if self.ram_type == 0:
            for b in self.clean_data:
                wrdata.extend([b,0x0])
        elif self.ram_type == 1:
            for b in self.clean_data:
                wrdata.extend([0x0,b])
        else:
          wrdata = data
        self._raw = bytes(wrdata)
        await write(ctx.bizhawk_ctx, [(0, wrdata, "SRAM")])
    
    def stage(self, offset, data):
        for i in range(0,len(data)):
            if self.fields[offset+i] != data[i]:
                self.staged.append((offset+i, data[i]))
    
    async def commit(self, ctx):
        if len(self.staged) > 0:
          out = list(self.fields)
          while len(self.staged):
              u = self.staged.pop(0)
              out[u[0]] = u[1]
          self.fields = tuple(out)
          self.clean_data = struct.pack(self.format, *out)
          wrdata = []
          if self.ram_type == 0:
              for b in self.clean_data:
                  wrdata.extend([b,0x0])
          elif self.ram_type == 1:
              for b in self.clean_data:
                  wrdata.extend([0x0,b])
          else:
            wrdata = self.clean_data
          tempraw = bytes(wrdata)
          patches = []
          for i,bs in enumerate(zip(self._raw, tempraw)):
              if bs[0] != bs[1]:
                  logger.info(f"{i=} {bs=}")
                  patches.append([i,[bs[1]], "SRAM"])
          self._raw = tempraw
          await write(ctx.bizhawk_ctx,patches)

class S1Client(BizHawkClient):
    system = ("GEN",)
    patch_suffix = (".aps1",)
    game = "Sonic the Hedgehog 1"

    async def validate_rom(self, ctx):
        # loaded_hash = await get_hash(ctx.bizhawk_ctx)
        print(ctx.rom_hash)
        if ctx.rom_hash == "5935F48C40D03AF1C25F1D7C0303DF0FAC7B9BDD": # Patched against known `Sonic The Hedgehog (W) (REV00)`
            ctx.game = self.game
            ctx.items_handling = 0b111
            ctx.finished_game = False
            ctx.remote_seed_name = MAGIC_EMPTY_SEED
            ctx.rom_seed_name = MAGIC_EMPTY_SEED
            ctx.sram_abstraction = SegaSRAM(">4s196BBBBBBBBB20s")
            ctx.sram_abstraction.extra_addresses.append((0x0F600, 1, "68K RAM")) # Game mode
            ctx.sram_abstraction.extra_addresses.append((0x0FE10, 7, "68K RAM")) # Zone and Act... v_lastspecial is 0xFE16
            ctx.curr_map = None
            return True
        return False

    def on_package(self, ctx, cmd, args):
        if cmd == 'RoomInfo':
            logger.debug(f"{args['seed_name']=} ?= {ctx.rom_seed_name=}")
            ctx.remote_seed_name = f"{args['seed_name'][-20:]:20}"
            ctx.seed_name = args['seed_name']
            if ctx.rom_seed_name != ctx.remote_seed_name:
                if ctx.rom_seed_name != MAGIC_EMPTY_SEED:
                  # CommonClient's on_package displays an error to the user in this case, but connection is not cancelled.
                  self.game_state = False
                  self.disconnect_pending = True
                  print("foo")
                print("bar")
                if len(ctx.locations_checked) != 0:
                    # This is in the hopes of avoiding sending reused data
                    ctx.locations_checked.clear()
                    ctx.locations_scouted.clear()
                    ctx.stored_data_notification_keys.clear()
                    ctx.checked_locations.clear()
        #if cmd != "PrintJSON":
        #    logger.info(f"{cmd=} -> {args=}")
        #if cmd == "PrintJSON" and args["type"] in {}:
        super().on_package(ctx, cmd, args)

    async def game_watcher(self, ctx):
        assert isinstance(ctx.sram_abstraction, SegaSRAM)
        await ctx.sram_abstraction.read_bytes(ctx)
        if ctx.sram_abstraction.fields[0] != b'AS10' or b'\xff' in ctx.sram_abstraction.fields[-1]:
            return # This means we're not initialised
        seed_name = str(ctx.sram_abstraction.fields[-1],'ascii')
        #logger.info(f"Data... {clean_data=} ({len(clean_data)=}) {seed_name=} {len(seed_name)=}")
        # We're only caring about the seed in the start.
        ctx.rom_seed_name = seed_name

        if not ctx.server or not ctx.server.socket.open or ctx.server.socket.closed or ctx.remote_seed_name == MAGIC_EMPTY_SEED:
            return
        
        if ctx.sram_abstraction.extra_data[0] == b"\x0C": # Level mode
            # This fixes the oddity of the game switching to GHZ1 for special stage conclusion:
            if ctx.curr_map not in range(19,25):
                map_code = constants.level_bytes.get(ctx.sram_abstraction.extra_data[1][:2],0)
            else:
                map_code = ctx.curr_map
        elif ctx.sram_abstraction.extra_data[0] == b"\x10": # Special zone
            map_code = int(ctx.sram_abstraction.extra_data[1][6])+19
        else:
            map_code = 0
        
        if ctx.curr_map != map_code:
            ctx.curr_map = map_code
            await ctx.send_msgs([{
                "cmd": "Set",
                "key": f"{ctx.slot}_{ctx.team}_sonic1_area",
                "default": 0,
                "want_reply": True,
                "operations": [{
                    "operation": "replace",
                    "value": map_code,
                }],
            }])

        cleanslate = False

        if ctx.sram_abstraction.fields[0] == b'AS10':
            # So, this should be valid save data...
            if seed_name == MAGIC_EMPTY_SEED:
                # Only, there's a blank save, so we should write the full save.
                output = [b'AS10']
                #logger.info(f"{ctx.locations_checked=} {ctx.checked_locations=}")
                output += bytes([MAGIC_BROKEN if constants.id_base+i in ctx.checked_locations else MAGIC_UNBROKEN 
                                 for i in range(1,len(constants.monitor_by_id)+1)])
                output.extend([0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0])
                output.append(ctx.remote_seed_name.encode())
                await ctx.sram_abstraction.full_write(ctx, output)
                await ctx.sram_abstraction.read_bytes(ctx)
                seed_name = ctx.remote_seed_name
                ctx.rom_seed_name = seed_name
                cleanslate = True

                '''
                move.w #0,(a0)+ ; Special zone bitfield
                move.w #0,(a0)+ ; Emerald bitfield, 0x00 (none), 0x01 (first em), upto 0x3F (all 6)
                ; Boss's alive bitfield: FZ Star3 Lab3 Spring3 Marb3 GH3
                move.w #0,(a0)+ ; Boss bitfield, 0x3F (none), 0x3E (GH3), upto 0x00 (all 6 alive)
                move.w #0,(a0)+ ; Buff: Disable goal blocks. 0x00 (off), 0x01 (on)
                move.w #0,(a0)+ ; Buff: Disable R. 0x00 (off), 0x01 (on)
                move.w #0,(a0)+ ; Number of rings found.
                move.w #0,(a0)+ ; Level gate bitmask.
                move.w #0,(a0)+ ; Specials gate bitmask.
                '''

            if seed_name == ctx.remote_seed_name:
                dirty = False
                for i in range(1,len(constants.monitor_by_id)+1):
                    broken = (ctx.sram_abstraction.fields[i] == MAGIC_BROKEN)
                    checked = constants.id_base+i in ctx.checked_locations
                    if broken != checked:
                        #logger.info(f"{constants.monitor_by_idx[i]} {broken} != {checked}")
                        ctx.locations_checked.add(constants.id_base+i) # Do I need to do this?
                        dirty = True
                
                basis = 1+len(constants.monitor_by_id)

                specials = ctx.sram_abstraction.fields[basis]
                special_build = 0
                for bit, idx in [[1,221], [2,222], [4,223], [8,224], [16,225], [32,226]]:
                    if constants.id_base+idx in ctx.checked_locations:
                        special_build |= bit
                    else:
                        if specials&bit != 0:
                            ctx.locations_checked.add(constants.id_base+idx) # Do I need to do this?
                            dirty = True
                if cleanslate:
                    ctx.sram_abstraction.stage(basis, [special_build])

                emeralds = ctx.sram_abstraction.fields[basis+1]

                # GH3, MZ3, SY3, LZ3, SL3, FZ
                bosses = ctx.sram_abstraction.fields[basis+2]
                boss_build = 0
                for bit, idx in [[1,211], [2,212], [4,213], [8,214], [16,215], [32,216]]:
                    if constants.id_base+idx in ctx.checked_locations:
                        boss_build |= bit
                    else:
                        if bosses&bit != 0:
                            ctx.locations_checked.add(constants.id_base+idx) # Do I need to do this?
                            dirty = True
                if cleanslate:
                    ctx.sram_abstraction.stage(basis+2, [boss_build])

                #logger.info(f"Data... {clean_data[basis:]=}")
                #logger.info(f"Data... {ctx.items_received=}")
                #ctx.items_received=[NetworkItem(item=3141501088, location=3141501221, player=2, flags=2)]
                ringcount = 0
                emeraldsset = 0
                buffs = [0,0]
                levelkeys = 0
                sskeys = 0
                for it in ctx.items_received:
                    idx = it.item - constants.id_base
                    #logger.info(["Emerald 1", "Emerald 2", "Emerald 3", "Emerald 4", "Emerald 5", "Emerald 6", "Disable GOAL blocks", "Disable R blocks"][idx-1])
                    if idx <= 6:
                        emeraldsset |= [1,2,4,8,16,32][idx-1]
                    elif idx == 7:
                        buffs[0] = 1
                    elif idx == 8:
                        buffs[1] = 1
                    elif idx in range(9,17):
                        levelkeys |= [1,2,4,8,16,32,64,128][idx-9]
                    elif idx in range(17,23):
                        sskeys |= [1,2,4,8,16,32,64,128][idx-17]
                    elif idx in [23,24]:
                        ringcount += 1
                    elif idx >= constants.filler_base:
                        # Junk item... do nothing
                        pass
                    else:
                        logger.info(f"Received item {idx} and I don't know what it is.")
                
                if ctx.slot_data.get("hard_mode", 0):
                    ringcount = 0

                ctx.sram_abstraction.stage(basis+1, [emeraldsset])
                ctx.sram_abstraction.stage(basis+3, [buffs[0], buffs[1], ringcount, levelkeys, sskeys])
                await ctx.sram_abstraction.commit(ctx)
                
                if dirty:
                    await ctx.send_msgs([{"cmd": "LocationChecks", "locations": list(ctx.locations_checked)}]) # Or this?
                    #logger.info(f"{ctx.locations_checked=}")
                if not ctx.finished_game and (
                        bosses == 0x3F # All bosses
                    and specials == 0x3F # All specials
                    and emeraldsset == 0x3F # All Emeralds received
                    and ringcount >= ctx.slot_data.get("ring_goal",100) # Ring goal from config.
                ):
                    await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            else:
                logger.info(f"{seed_name=} =?= {ctx.remote_seed_name=}")
            #logger.info(f"{ctx.username=}")
            