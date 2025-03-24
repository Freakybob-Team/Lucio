import pygame as pg
import numpy as np
import threading
import queue
import os
class Chunks:
    def __init__(self, game):
        self.game = game
        os.makedirs("chunks", exist_ok=True)
        self.loaded_chunks = {}
        self.loading_chunks = set()
        self.chunk_queue = queue.Queue()
        self.loader_thread = threading.Thread(target=self.chunk_loader, daemon=True)
        self.loader_thread.start()
    def create_chunk(self, x, z):
        chunk = np.zeros(16 * 16 * 64, dtype=np.uint8)
        self.save_chunk(chunk, x, z)
    def save_chunk(self, chunk, x, z):
        filename = f"chunks/{x}_{z}.dat"
        chunk.tofile(filename)
    def load_chunk(self, x, z):
        if (x, z) not in self.loaded_chunks and (x, z) not in self.loading_chunks:
            self.loading_chunks.add((x, z))
            self.chunk_queue.put((x, z))
    def chunk_loader(self):
        while True:
            x, z = self.chunk_queue.get()
            filename = f"chunks/{x}_{z}.dat"
            if not os.path.exists(filename):
                self.create_chunk(x, z)
            chunk_data = np.fromfile(filename, dtype=np.uint8)
            self.loaded_chunks[(x, z)] = chunk_data
            self.loading_chunks.discard((x, z))
            self.chunk_queue.task_done()
    def update(self):
        px = int(self.game.player.x) // self.game.chunk_size
        pz = int(self.game.player.z) // self.game.chunk_size
        render_distance_sq = self.game.render_distance ** 2
        to_remove = [key for key in self.loaded_chunks if (key[0] - px) ** 2 + (key[1] - pz) ** 2 >= render_distance_sq]
        for key in to_remove: del self.loaded_chunks[key]
        for x in range(px - self.game.render_distance, px + self.game.render_distance):
            for z in range(pz - self.game.render_distance, pz + self.game.render_distance):
                if (x - px) ** 2 + (z - pz) ** 2 < render_distance_sq:
                    self.load_chunk(x, z)
    def draw(self):
        for (x, z) in self.loaded_chunks:
            pg.draw.rect(self.game.screen, "blue",
                         (x * self.game.chunk_size - self.game.player.x + self.game.width // 2,
                          z * self.game.chunk_size - self.game.player.z + self.game.height // 2,
                          self.game.chunk_size, self.game.chunk_size), 1)
class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.z = 0, 0
        self.speed = 50
    def update(self):
        keys = pg.key.get_pressed()
        dx, dz = 0, 0
        if keys[pg.K_w]: dz -= 1
        if keys[pg.K_a]: dx -= 1
        if keys[pg.K_s]: dz += 1
        if keys[pg.K_d]: dx += 1
        if dx or dz:
            length = np.sqrt(dx ** 2 + dz ** 2)
            dx /= length
            dz /= length
        self.x += dx * self.speed * self.game.dt
        self.z += dz * self.speed * self.game.dt
    def draw(self):
        pg.draw.circle(self.game.screen, "red", (self.game.width // 2, self.game.height // 2), 5)
class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Chunk System")
        self.width, self.height = 1500, 700
        self.screen = pg.display.set_mode((self.width, self.height))
        self.clock = pg.time.Clock()
        self.block_size = 1
        self.chunk_size = 16 * self.block_size
        self.render_distance = 20
        self.chunks = Chunks(self)
        self.player = Player(self)
        self.dt = 1
    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
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