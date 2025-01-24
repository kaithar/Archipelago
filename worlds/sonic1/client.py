import logging

from NetUtils import ClientStatus
from worlds._bizhawk.client import BizHawkClient
from worlds._bizhawk import read, write

from . import constants

logger = logging.getLogger("Client")

MAGIC_BROKEN = 0x0
MAGIC_UNBROKEN = 0x1F
MAGIC_EMPTY_SEED = ' '*20

class S1Client(BizHawkClient):
    system = ("GEN",)
    patch_suffix = (".aps1",)
    game = "Sonic the Hedgehog 1"

    async def validate_rom(self, ctx):
        # loaded_hash = await get_hash(ctx.bizhawk_ctx)
        print(ctx.rom_hash)
        if ctx.rom_hash == "0B02CA9FE8F5EA1067EC491465BD8FA22DB0D74E": # Patched against known `Sonic The Hedgehog (W) (REV00)`
            ctx.game = self.game
            ctx.items_handling = 0b111
            ctx.remote_seed_name = MAGIC_EMPTY_SEED
            ctx.rom_seed_name = MAGIC_EMPTY_SEED
            return True
        return False

    def on_package(self, ctx, cmd, args):
        if cmd == 'RoomInfo':
            logger.debug(f"{args['seed_name']=} ?= {ctx.rom_seed_name=}")
            ctx.remote_seed_name = f"{args['seed_name'][-20:]:20}"
            if ctx.rom_seed_name != ctx.remote_seed_name and ctx.rom_seed_name != MAGIC_EMPTY_SEED:
                # CommonClient's on_package displays an error to the user in this case, but connection is not cancelled.
                self.game_state = False
                self.disconnect_pending = True
        #if cmd != "PrintJSON":
            #logger.info(f"{cmd=} -> {args=}")
        super().on_package(ctx, cmd, args)

    async def game_watcher(self, ctx):
        data = await read(ctx.bizhawk_ctx, [(0x0, 0x1B2+40, "SRAM"),])
        # Because of the stupidity of how sram works, we're going to unpack this by dropping every other byte.
        # So:
        clean_data = [data[0][i] for i in range(0,len(data[0]), 2)]
        seed_name = ''.join([chr(c) for c in clean_data[-20:]])
        #logger.info(f"Data... {clean_data=} ({len(clean_data)=}) {seed_name=} {len(seed_name)=}")
        # We're only caring about the seed in the start.
        ctx.rom_seed_name = seed_name

        if not ctx.server or not ctx.server.socket.open or ctx.server.socket.closed or ctx.remote_seed_name == MAGIC_EMPTY_SEED:
            return

        if clean_data[0:4] == [65, 83, 49, 48]: # AS10
            # So, this should be valid save data...
            if seed_name == MAGIC_EMPTY_SEED:
                # Only, there's a blank save, so we should write the full save.
                output = [65, 83, 49, 48]
                for i in range(1,len(constants.monitor_by_id)+1):
                    output.append(MAGIC_BROKEN if constants.id_base+i in ctx.locations_checked else MAGIC_UNBROKEN)
                output.extend([0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0])
                output.extend([ord(c) for c in ctx.remote_seed_name])
                wrdata = []
                for b in output:
                    wrdata.extend([b,0x0])
                await write(ctx.bizhawk_ctx, [(0, wrdata, "SRAM")])
                seed_name = ctx.remote_seed_name
                ctx.rom_seed_name = seed_name

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
                    broken = (clean_data[3+i] == MAGIC_BROKEN)
                    checked = constants.id_base+i in ctx.locations_checked
                    if broken != checked:
                        #logger.info(f"{constants.monitor_by_idx[i]} {broken} != {checked}")
                        ctx.locations_checked.add(constants.id_base+i) # Do I need to do this?
                        dirty = True
                
                basis = 4+len(constants.monitor_by_id)

                specials = clean_data[basis]
                for bit, idx in [[1,221], [2,222], [4,223], [8,224], [16,225], [32,226]]:
                    if specials&bit != 0 and constants.id_base+idx not in ctx.locations_checked:
                        ctx.locations_checked.add(constants.id_base+idx) # Do I need to do this?
                        dirty = True

                emeralds = clean_data[basis+1]

                # GH3, MZ3, SY3, LZ3, SL3, FZ
                bosses = clean_data[basis+2]
                for bit, idx in [[1,211], [2,212], [4,213], [8,214], [16,215], [32,216]]:
                    if bosses&bit != 0 and constants.id_base+idx not in ctx.locations_checked:
                        ctx.locations_checked.add(constants.id_base+idx) # Do I need to do this?
                        dirty = True

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
                    else:
                        ringcount += 1
                
                if emeralds != emeraldsset:
                    await write(ctx.bizhawk_ctx, [((basis+1)*2, [emeraldsset], "SRAM")])
                if clean_data[basis+3] != buffs[0]:
                    await write(ctx.bizhawk_ctx, [((basis+3)*2, [buffs[0]], "SRAM")])
                if clean_data[basis+4] != buffs[1]:
                    await write(ctx.bizhawk_ctx, [((basis+4)*2, [buffs[1]], "SRAM")])
                if clean_data[basis+5] != ringcount:
                    await write(ctx.bizhawk_ctx, [((basis+5)*2, [ringcount], "SRAM")])
                if clean_data[basis+6] != levelkeys:
                    await write(ctx.bizhawk_ctx, [((basis+6)*2, [levelkeys], "SRAM")])
                if clean_data[basis+7] != levelkeys:
                    await write(ctx.bizhawk_ctx, [((basis+7)*2, [sskeys], "SRAM")])
                
                if dirty:
                    await ctx.send_msgs([{"cmd": "LocationChecks", "locations": list(ctx.locations_checked)}]) # Or this?
                    #logger.info(f"{ctx.locations_checked=}")
                if not ctx.finished_game and (
                        bosses == 0x3F # All bosses
                    and specials == 0x3F # All specials
                    and emeraldsset == 0x3F # All Emeralds received
                    and ringcount >= 100 # 100 rings received.
                ):
                    await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            else:
                logger.info(f"{seed_name=} =?= {ctx.remote_seed_name=}")
            #logger.info(f"{ctx.username=}")
            