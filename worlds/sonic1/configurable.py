from dataclasses import dataclass
import os
import typing
import Utils
from worlds.Files import APProcedurePatch

from settings import get_settings
import settings
from Options import DefaultOnToggle, NamedRange, OptionGroup, Toggle, Range, PerGameCommonOptions

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

class Sonic1ProcedurePatch(APProcedurePatch):
    game = "Sonic the Hedgehog 1"
    hash = "1bc674be034e43c96b86487ac69d9293"
    patch_file_ending = ".aps1"
    result_file_ending = ".md"

    procedure = [
        ("apply_bsdiff4", ["sonic1-ap.bsdiff4"]),
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
        """File name of your Sonic 1 (JUE/W) Rev0 ROM (also called "Sonic The Hedgehog (USA, Europe)") """
        required = True
        description = "Sonic 1 English Rev0 ROM File"
        copy_to = "Sonic The Hedgehog (USA, Europe).md"
        md5s = [Sonic1ProcedurePatch.hash]
    
    class Sonic1ForwardMessages(settings.Bool):
        """Forward AP messages to Bizhawk (currently not working)"""

    rom_file: Sonic1RomFile = Sonic1RomFile(Sonic1RomFile.copy_to)
    forward_messages: typing.Union[Sonic1ForwardMessages, bool] = True

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

@dataclass
class Sonic1GameOptions(PerGameCommonOptions):
    no_local_keys: NoLocalKeys
    allow_disable_goal: AllowDisableGoal
    allow_disable_r: AllowDisableR
    hard_mode: HardMode
    ring_goal: RingGoal
    available_rings: AvailableRings
    boring_filler: BoringFiller
