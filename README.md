# CHIP-8-Emulator
-A python based CHIP-8 Emulator that emulates games compatible with CHIP-8 Virtual Machine used in the late 1970s for playing games.
- The above code uses pure python to simulate similar behavior as of the original CHIP-8 Virtual Machine.
# Usage
- To use the emulator, download a CHIP-8 ROM (pong.ch8 for example).
- The code file and the ROM must be in the same folder.
- In the code, loadROM() function is executed in the second last line, and in the function we have the name of the ROM.
- Change the ROM file's name to play any other CHIP-8 game.
- For eg.
    If you want to play br8kout
  all you need to do is change:
            chip.loadROM('rom_name.ch8')
  to:
            chip.loadROM('br8kout.ch8')
  or:
            chip.loadROM('pong.ch8') #if you want to play pong i.e. ping-pong
