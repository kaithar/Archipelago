from dataclasses import dataclass
import hashlib
import os
import pkgutil
import typing

import bsdiff4
import Utils
from worlds.Files import APPatchExtension, APProcedurePatch

from settings import get_settings
import settings
import Options
from Options import CommonOptions, DefaultOnToggle, NamedRange, OptionGroup, Toggle, Range, PerGameCommonOptions

from . import constants

#### Settings stuff!

# For some stupid reason, the world release ROM sometimes gets called "Sonic The Hedgehog (USA, Europe).md"
# This file actually has Japan in its region list, specifically it has JUE in the header.  Properly it's the Rev 0 release.
# This is the no-intro entry: https://datomatic.no-intro.org/index.php?page=show_record&s=32&n=1231
# Note: md5 is 1bc674be034e43c96b86487ac69d9293, serial is GM 00001009=00
#
# There exists a Japanese/Korea release (serial 00004049-01) that's actually Rev 1... only that's also in English.
# There is also a Sonic Collection version that is different from both of those.
# I'm using Rev 0 because it's the most commonly owned in USA and Europe.

class Sonic1MultiPatch(APPatchExtension):
    game = "Sonic the Hedgehog 1"
    @staticmethod
    def apply_s1_multi_patch(caller: APProcedurePatch, rom: bytes) -> bytes:
        input_md5 = hashlib.md5(rom).hexdigest()
        if input_md5 == "c6c15aea60bda10ae11c6bc375296153":
            # Sonic The Hedgehog (World) (GameCube Edition).md ... unlikely but cheap enough to do anyway
            return Sonic1MultiPatch.gce_to_rev1(caller, rom)
        elif input_md5 == "09dadb5071eb35050067a32462e39c5f":
            # This is rev1, common filenames are:
            # - Sonic The Hedgehog (Japan, Korea).md
            # - SONIC_W.68K (This is from Steam's Genesis classics collection)
            return Sonic1MultiPatch.rev1_to_rev0(caller, rom)
        elif input_md5 ==  "1bc674be034e43c96b86487ac69d9293":
            # This is rev0, the original.
            return Sonic1MultiPatch.rev0_to_ap(caller, rom)
        else:
            # I have no idea how you got here
            raise Exception("Supplied ROM doesn't match any hash I know how to handle.")
        
    @staticmethod
    def gce_to_rev1(caller: APProcedurePatch, rom: bytes) -> bytes:
        older_rom = bsdiff4.patch(rom, pkgutil.get_data(__name__, "gce_rev1.bsdiff4"))
        return Sonic1MultiPatch.rev1_to_rev0(caller, older_rom)

    @staticmethod
    def rev1_to_rev0(caller: APProcedurePatch, rom: bytes) -> bytes:
        older_rom = bsdiff4.patch(rom, pkgutil.get_data(__name__, "rev1_rev0.bsdiff4"))
        return Sonic1MultiPatch.rev0_to_ap(caller, older_rom)

    @staticmethod
    def rev0_to_ap(caller: APProcedurePatch, rom: bytes) -> bytes:
        return bsdiff4.patch(rom, pkgutil.get_data(__name__, "sonic1-ap.bsdiff4"))


class Sonic1ProcedurePatch(APProcedurePatch):
    game = "Sonic the Hedgehog 1"
    patch_file_ending = ".aps1"
    result_file_ending = ".md"
    hash = "Multiple"

    procedure = [
        ("apply_s1_multi_patch", []),
    ]

    @classmethod
    def get_source_data(cls) -> bytes:
        file_name = get_settings().sonic1_settings["rom_file"]
        if not os.path.exists(file_name):
          file_name = Utils.user_path(file_name)
        with open(file_name, "rb") as infile:
            base_rom_bytes = bytes(infile.read())

        return base_rom_bytes

class Sonic1Settings(settings.Group):
    class Sonic1RomFile(settings.UserFilePath):
        """File name of your Sonic 1 ROM. Accepts Rev0, Rev1, and GCE """
        required = True
        description = "Sonic 1 ROM File"
        copy_to = "Sonic The Hedgehog.md"
        md5s = [
            "c6c15aea60bda10ae11c6bc375296153", # GCE
            "09dadb5071eb35050067a32462e39c5f", # Rev1
            "1bc674be034e43c96b86487ac69d9293"  # Rev0
        ]
    
    rom_file: Sonic1RomFile = Sonic1RomFile(Sonic1RomFile.copy_to)

#### Options!


class NoLocalKeys(Toggle):
    """Restrict local placement rules to force this world's keys to be placed in other worlds."""
    display_name = "No local key placement"
    default = False
  

class AllowDisableGoal(DefaultOnToggle):
    """Enable the buff item that disables Special stage GOAL blocks."""
    display_name = "Add a buff to disable GOAL blocks"
    default = True
  
class AllowDisableR(DefaultOnToggle):
    """Enable the buff item that disables Special stage R blocks."""
    display_name = "Add a buff to disable R blocks"
    default = True

class HardMode(Toggle):
    """Hard Mode: The ROM's ring count will remain zero and Sonic still only drops 6 rings.  Doesn't interact with Ring Goal or Available Rings."""
    display_name = "Hard Mode: No persistent rings"
    default = False

class RingGoal(NamedRange):
    """Changes the number of rings that need to be found for you to clear.  Isn't affected by Hard Mode, is overriden by Available Rings."""
    display_name = "Ring Goal for your Victory Condition"
    range_start = 0
    range_end = 150
    default = 100
    special_range_names = {
        "easy": 50,
        "normal": 100,
        "hard": 150
    }

class AvailableRings(Range):
    """Dr Eggman attacked, how many rings fell into the pool for you to recover?  Will cap Ring Goal."""
    display_name = "Number of rings sent to the pool"
    range_start = 0
    range_end = 185
    default = 185

class BoringFiller(Toggle):
    """Enable to take the fun out of the junk filler items"""
    display_name = "Boring filler items"
    default = False

ring_options = OptionGroup("Ring Options",[AvailableRings,RingGoal,HardMode,BoringFiller])

valid_item_keys = [item[0] for item in constants.items if item[2] != "filler"]

class WorthWhileLocal(Options.LocalItems):
    __doc__ = Options.LocalItems.__doc__
    valid_keys = valid_item_keys

class WorthWhileNonLocal(Options.NonLocalItems):
    __doc__ = Options.NonLocalItems.__doc__
    valid_keys = valid_item_keys

class WorthWhileStart(Options.StartInventory):
    __doc__ = Options.StartInventory.__doc__
    valid_keys = valid_item_keys

class WorthWhileStartHint(Options.StartHints):
    __doc__ = Options.StartHints.__doc__
    valid_keys = valid_item_keys

special_generics = OptionGroup("Item & Location Options", [WorthWhileLocal, WorthWhileNonLocal, WorthWhileStart, WorthWhileStartHint], True)

@dataclass
class Sonic1GameOptions(PerGameCommonOptions):
    no_local_keys: NoLocalKeys
    allow_disable_goal: AllowDisableGoal
    allow_disable_r: AllowDisableR
    hard_mode: HardMode
    ring_goal: RingGoal
    available_rings: AvailableRings
    boring_filler: BoringFiller
    local_items: WorthWhileLocal
    non_local_items: WorthWhileNonLocal
    start_inventory: WorthWhileStart
    start_hints: WorthWhileStartHint

