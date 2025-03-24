import pygame as pg
import numpy as np
import os
class Chunks:
    def __init__(self, game):
        self.game = game
        os.makedirs("chunks", exist_ok=True)
        self.loaded_chunks = []
    def create_chunk(self, x, z):
        chunk = np.zeros(16 * 16 * 64, dtype=np.uint8)
        self.save_chunk(chunk, x, z)
    def save_chunk(self, chunk, x, z):
        filename = f"chunks/{x}_{z}.dat"
        chunk.tofile(filename)
    def load_chunk(self, x, z):
        filename = f"chunks/{x}_{z}.dat"
        if not os.path.exists(filename):
            self.create_chunk(x, z)
        self.loaded_chunks.append([[x, z], np.fromfile(filename, dtype=np.uint8)])
    def update(self):
        self.loaded_chunks = []
        px = int(self.game.player.x) // self.game.chunk_size
        pz = int(self.game.player.z) // self.game.chunk_size
        for x in range(px - self.game.render_distance, px + self.game.render_distance):
            for z in range(pz - self.game.render_distance, pz + self.game.render_distance):
                if np.hypot(x - px, z - pz) < self.game.render_distance:
                    self.load_chunk(x, z)
    def draw(self):
        for chunk in self.loaded_chunks:
            x, z = chunk[0]
            data = chunk[1]
            for i in range(16):
                for j in range(16):
                    pg.draw.rect(self.game.screen, "green",
                                 (i * self.game.block_size + x * self.game.chunk_size - self.game.player.x + self.game.width // 2,
                                  j * self.game.block_size + z * self.game.chunk_size - self.game.player.z + self.game.height // 2,
                                  self.game.block_size, self.game.block_size), 1)
            pg.draw.rect(self.game.screen, "blue",
                         (x * self.game.chunk_size - self.game.player.x + self.game.width // 2,
                          z * self.game.chunk_size - self.game.player.z + self.game.height // 2,
                          self.game.chunk_size, self.game.chunk_size), 1)
class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.z = 0, 0
        self.speed = 100
    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.z -= self.speed * self.game.dt
        if keys[pg.K_a]:
            self.x -= self.speed * self.game.dt
        if keys[pg.K_s]:
            self.z += self.speed * self.game.dt
        if keys[pg.K_d]:
            self.x += self.speed * self.game.dt
    def draw(self):
        pg.draw.circle(self.game.screen, "red", (self.game.width // 2, self.game.height // 2), 5)
class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("chunk system for FreakCraft")
        self.width, self.height = 1500, 700
        self.screen = pg.display.set_mode((self.width, self.height))
        self.clock = pg.time.Clock()
        self.block_size = 5
        self.chunk_size = 16 * self.block_size
        self.render_distance = 6
        self.chunks = Chunks(self)
        self.player = Player(self)
        self.events = []
        self.dt = 1
    def check_events(self):
        self.events = pg.event.get()
        for event in self.events:
            if event.type == pg.QUIT:
                pg.quit()
    def update(self):
        self.chunks.update()
        self.player.update()
    def draw(self):
        self.screen.fill("black")
        self.chunks.draw()
        self.player.draw()
        pg.display.flip()
    def run(self):
        while True:
            self.dt = self.clock.tick(60) / 1000
            self.check_events()
            self.update()
            self.draw()
if __name__ == "__main__":
    game = Game()
    game.run()