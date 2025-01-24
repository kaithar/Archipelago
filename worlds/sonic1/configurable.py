import os
from settings import get_settings
import settings
import Utils
from worlds.Files import APProcedurePatch

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
        copy_to = "Sonic 1 (W).md"
        md5s = [Sonic1ProcedurePatch.hash]

    rom_file: Sonic1RomFile = Sonic1RomFile("Sonic The Hedgehog (USA, Europe).md")

