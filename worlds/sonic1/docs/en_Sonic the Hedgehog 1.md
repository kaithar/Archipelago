# Welcome to Sonic 1, 1991, with bonus features.

## What you need to know about the Archipelago mode

- The location checks for this game are every monitor, all six bosses and all six special zones.
- This world will add to the item pool 6 emeralds, 14 keys, 2 buff items (more on those in a moment), rings, and filler.
- There are 6 keys for the normal zones, 1 for the Final Zone, 1 for Specials access, and 6 for the special stages themselves.
- The player will start with the Specials access key and one random normal zone key unlocked, the remaining 12 are in the pool.
- The pool rings are split into the goal count number of Shiny Rings (progression) and the remaining pool are Gold Rings (useful).  
- To complete the world you need to beat the 6 specials, 6 bosses, get 6 emeralds in the pool, and some amount of the pool rings.
- The number of rings added to the pool is set by an option, the remaining item slots will contain junk items.

## Required Software

- This world uses the BizHawk client, thus the usual instructions apply.
- Archipelago launcher with this world, it can't track your game otherwise.
- A Sonic The Hedgehog 16 bit (1991) ROM file.  We can't help you acquire this, please don't ask. You need one of the following:
    - Sonic The Hedgehog Revision 0 - This is the original world wide release cart.
    - Sonic The Hedgehog Revision 1 - This is the updated cart released in Japan.
    - Sega Classics SONIC_w.68K - This is actually just the rev1 ROM with an odd name.
    - Sonic The Hedgehog GameCube Edition - This is almost the same as rev1 so it's close enough.

## Tracker support

- Universal Tracker is supported, just requires having both worlds on the same launcher.
- Pop Tracker is supported, you can load the tracker directory or download the packaged .poptracker file.

Both have working auto tracking and map following, just connect to your AP game.

## World options

The generation options are suitably documented.  Some specific notes:
- If you want to generate a solo world be sure that "No local key placement" isn't enabled.
- The Ring Goal won't pose much of a challenge in a normal game, you can tweak these settings to make things much harder.
- The default difficulty is tuned to the assumption you will need to check most monitors in a reasonable amount of time.
- The Boring Filler option is there to disable the joke filler items.  All (non-functional) junk items have "(Junk)" in the name.

## What changes to Sonic 1 you need to know about

- Progression:
    - To make this sane to play you start in level select and get kicked back there after a level.
    - Monitor breaking is persistent and all of them are now ring boxes.  This will slightly increase difficulty.
    - Special stages will play in order, you won't move on to the next until you pass one.
    - You start with a random zone unlocked, further zone unlocks are via keys in other players' pools
- Rings and damge:
    - If you take damage and when you enter a level the mod will treat your AP received Ring count as your minimum instead of 0.
    - With the AP ring gift, you can survive any damage that would make you drop rings, like you immediately pick up rings.
    - The AP ring gift can be disabled during world gen.
    - To save rom space, Sonic hurt from an enemy will drop 6 rings and reset to the AP count as long as you have at least 1 ring.
    - You are not immune to instant deaths like squishing, time out and drowning.
    - Spikes floors are potentially more dangerous, they can lock you into a bounce loop instead of killing you.
    - You don't lose lives when dying, since it makes no sense in this context.
- Helping:
    - Pause a level and press C to exit back to level select.
    - A basic spin dash has been added to make life a little less miserable.
    - The 50 ring secret upper path on SBZ2 is disabled as there are no checks up there.
    - Special stage buffs:  The UP block is disabled, no speeding up.  Goal and R blocks can be disabled using buff items in the pool.
    - ReadySonic's "Roll into Catakiller" fix has been included, so you can kill them by rolling into them.
    - ReadySonic's "High speed camera fix" has also been included to hopefully make things a little safer.
- Rewards:
    - Repeating a boss doesn't give you extra rewards.
    - You don't gain extra lives for 100 rings, but you can't lose lives either.
    - Completing a stage with 50 rings won't spawn a giant ring due to progression gating.
    - Completing acts 2 or 3 of Scrap Brain won't advance you to the next zone.
