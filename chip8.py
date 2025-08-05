import tkinter as tk
import threading
import time

width = 64
height = 32
size = 10
timer = 60
cpu = 500


KeyMap = {
    '1': 0x1, '2': 0x2, '3': 0x3, '4': 0xC,
    'q': 0x4, 'w': 0x5, 'e': 0x6, 'r': 0xD,
    'a': 0x7, 's': 0x8, 'd': 0x9, 'f': 0xE,
    'z': 0xA, 'x': 0x0, 'c': 0xB, 'v': 0xF
}

class chip8:
    def __init__(self, debug = False):
        self.memory = [0] * 4096
        self.V = [0] * 16           
        self.I = 0              
        self.pc = 0x200
        self.stack = []
        self.DelayTimer = 0
        self.SoundTimer = 0
        self.keys = [0] * 16
        self.display = [[0] * width for _ in range(height)]
        self.draw_flag = False
        self.fontset()

    def fontset(self):
        fontset = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, 
            0x20, 0x60, 0x20, 0x20, 0x70,
            0xF0, 0x10, 0xF0, 0x80, 0xF0, 
            0xF0, 0x10, 0xF0, 0x10, 0xF0, 
            0x90, 0x90, 0xF0, 0x10, 0x10,
            0xF0, 0x80, 0xF0, 0x10, 0xF0,
            0xF0, 0x80, 0xF0, 0x90, 0xF0,
            0xF0, 0x10, 0x20, 0x40, 0x40, 
            0xF0, 0x90, 0xF0, 0x90, 0xF0, 
            0xF0, 0x90, 0xF0, 0x10, 0xF0, 
            0xF0, 0x90, 0xF0, 0x90, 0x90, 
            0xE0, 0x90, 0xE0, 0x90, 0xE0, 
            0xF0, 0x80, 0x80, 0x80, 0xF0, 
            0xE0, 0x90, 0x90, 0x90, 0xE0, 
            0xF0, 0x80, 0xF0, 0x80, 0xF0, 
            0xF0, 0x80, 0xF0, 0x80, 0x80
        ]
        for i, byte in enumerate(fontset):
            self.memory[i] = byte

    def loadROM(self, path):
        with open(path, "rb") as f:
            rom = f.read()
        for offset, byte in enumerate(rom):
            self.memory[0x200 + offset] = byte
                
    def fetch(self):
        opcode = self.memory[self.pc] << 8 | self.memory[self.pc +1]
        self.pc += 2
        return opcode

    def execute(self, opcode):
        x   = (opcode & 0x0F00) >> 8
        y   = (opcode & 0x00F0) >> 4
        n   = (opcode & 0x000F)
        nn  = opcode & 0x00FF
        nnn = opcode & 0x0FFF

        if opcode == 0x00E0:
            self.display = [[0]*width for _ in range(height)]
            self.draw_flag = True
        elif opcode == 0x00EE:
            self.pc = self.stack.pop()
        elif (opcode & 0xF000) == 0x1000:
            self.pc = nnn
        elif (opcode & 0xF000) == 0x2000:
            self.stack.append(self.pc)
            self.pc = nnn
        elif (opcode & 0xF000) == 0x3000:
            if self.V[x] == nn:
                self.pc += 2
        elif (opcode & 0xF000) == 0x4000:
            if self.V[x] != nn:
                self.pc += 2
        elif (opcode & 0xF00F) == 0x5000:
            if self.V[x] == self.V[y]:
                self.pc += 2
        elif (opcode & 0xF000) == 0x6000:
            self.V[x] = nn
        elif (opcode & 0xF00F) == 0x8001:
            self.V[x] |= self.V[y]
        elif (opcode & 0xF00F) == 0x8002:
            self.V[x] &= self.V[y]
        elif (opcode & 0xF00F) == 0x8003:
            self.V[x] ^= self.V[y]
        elif (opcode & 0xF00F) == 0x8004:
            total = self.V[x] + self.V[y]
            self.V[0xF] = 1 if total > 255 else 0
            self.V[x] = total & 0xFF
        elif (opcode & 0xF000) == 0x7000:
            self.V[x] = (self.V[x] + nn) & 0xFF
        elif (opcode & 0xF00F) == 0x8000:
            self.V[x] = self.V[y]
        elif (opcode & 0xF00F) == 0x8005:
            self.V[0xF] = 1 if self.V[x] > self.V[y] else 0
            self.V[x] = (self.V[x] - self.V[y]) & 0xFF
        elif (opcode & 0xF00F) == 0x8006:
            self.V[0xF] = self.V[x] & 0x1
            self.V[x] >>= 1
        elif (opcode & 0xF00F) == 0x8007:
            self.V[0xF] = 1 if self.V[y] > self.V[x] else 0
            self.V[x] = (self.V[y] - self.V[x]) & 0xFF
        elif (opcode & 0xF00F) == 0x800E:
            self.V[0xF] = (self.V[x] >> 7) & 0x1
            self.V[x] = (self.V[x] << 1) & 0xFF
        elif (opcode & 0xF00F) == 0x9000:
            if self.V[x] != self.V[y]:
                self.pc += 2
        elif (opcode & 0xF000) == 0xA000:
            self.I = nnn
        elif (opcode & 0xF000) == 0xB000:
            self.pc = nnn + self.V[0]
        elif (opcode & 0xF000) == 0xC000:
            import random
            self.V[x] = random.randint(0, 255) & nn
        elif (opcode & 0xF000) == 0xD000:
            self.V[0xF] = 0
            for row in range(n):
                sprite = self.memory[self.I + row]
                for col in range(8):
                    if sprite & (0x80 >> col):
                        px = (self.V[x] + col) % width
                        py = (self.V[y] + row) % height
                        if self.display[py][px]:
                            self.V[0xF] = 1
                        self.display[py][px] ^= 1
            self.draw_flag = True
        elif (opcode & 0xF0FF) == 0xE09E:
            if self.keys[self.V[x]]:
                self.pc += 2
        elif (opcode & 0xF0FF) == 0xE0A1:
            if not self.keys[self.V[x]]:
                self.pc += 2
        elif (opcode & 0xF0FF) == 0xF007:
            self.V[x] = self.DelayTimer
        elif (opcode & 0xF0FF) == 0xF00A:
            key_pressed = False
            for i, val in enumerate(self.keys):
                if val:
                    self.V[x] = i
                    key_pressed = True
                    break
            if not key_pressed:
                self.pc -= 2
        elif (opcode & 0xF0FF) == 0xF015:
            self.DelayTimer = self.V[x]
        elif (opcode & 0xF0FF) == 0xF018:
            self.SoundTimer = self.V[x]
        elif (opcode & 0xF0FF) == 0xF01E:
            self.I = (self.I + self.V[x]) & 0xFFF
        elif (opcode & 0xF0FF) == 0xF029:
            self.I = self.V[x] * 5
        elif (opcode & 0xF0FF) == 0xF033:
            self.memory[self.I] = self.V[x] // 100
            self.memory[self.I + 1] = (self.V[x] // 10) % 10
            self.memory[self.I + 2] = self.V[x] % 10
        elif (opcode & 0xF0FF) == 0xF055:
            for i in range(x + 1):
                self.memory[self.I + i] = self.V[i]
        elif (opcode & 0xF0FF) == 0xF065:
            for i in range(x + 1):
                self.V[i] = self.memory[self.I + i]
        else:
            print(f"Unknown opcode: {opcode:04X}")
            
    def emulate_cycle(self):
        opcode = self.fetch()
        self.execute(opcode)

    def update_timers(self):
        if self.DelayTimer > 0:
            self.DelayTimer -= 1
        if self.SoundTimer > 0:
            self.SoundTimer -= 1

class chip8gui:
    def __init__(self, chip: chip8):
        self.chip = chip
        self.root = tk.Tk()
        self.root.title("Chip-8 Emulator")
        self.canvas = tk.Canvas(
            self.root,
            width = width * size,
            height = height * size,
            bg = "black"
        )
        self.canvas.pack()

        self.root.bind("<KeyPress>", self.key_down_events)
        self.root.bind("<KeyRelease>", self.key_up_events)

        self.running = True
        threading.Thread(target = self.run_emulator, daemon = True).start()
        self.root.mainloop()

    def draw_display(self):
        self.canvas.delete("all")
        for y in range(height):
            for x in range(width):
                if self.chip.display[y][x]:
                    self.canvas.create_rectangle(
                        x * size,
                        y * size,
                        (x+1) * size,
                        (y+1) * size,
                        fill = "white",
                        outline = ""
                    )

    def run_emulator(self):
        cpu_delay = 1 / cpu
        timer_delay = 1 / timer
        last_timer_update = time.time()

        while self.running:
            start = time.time()
            self.chip.emulate_cycle()
            if start - last_timer_update >= timer_delay:
                self.chip.update_timers()
                last_time_update = start

            if self.chip.draw_flag:
                self.draw_display()
                self.draw_flag = False

            elapsed = time.time() - start
            time.sleep(max(cpu_delay - elapsed, 0))

    def key_down_events(self, event):
        key = event.keysym.lower()
        if key in KeyMap:
            self.chip.keys[KeyMap[key]] = 1

    def key_up_events(self, event):
        key = event.keysym.lower()
        if key in KeyMap:
            self.chip.keys[KeyMap[key]] = 0

if __name__ == '__main__':
    chip = chip8()
    chip.loadROM('br8kout.ch8')
    chip8gui(chip)


































            
