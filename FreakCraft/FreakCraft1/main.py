import pygame as pg, numpy as np, os
from threading import Thread
from queue import Queue
width, height = 1000, 700
rdist = 12
fps = 60
class Chunks:
    def __init__(self, game):
        self.game = game
        self.loaded = {}
        self.loading = set()
        self.queue = Queue()
        os.makedirs("chunks", exist_ok=True)
        Thread(target=self.loader, daemon=True).start()
    def create(self, x, z):
        data = np.zeros(16384, dtype=np.uint8)
        self.store(data, x, z)
    def store(self, data, x, z):
        filename = f"chunks/{x}_{z}.dat"
        data.tofile(filename)
    def load(self, x, z):
        if (x, z) not in self.loaded:
            if (x, z) not in self.loading:
                self.loading.add((x, z))
                self.queue.put((x, z))
    def unload(self, x, z):
        data = self.loaded[(x, z)]
        #self.store(data, x, z)
        del self.loaded[(x, z)]
    def loader(self):
        while True:
            (x, z) = self.queue.get()
            filename = f"chunks/{x}_{z}.dat"
            if not os.path.exists(filename):
                self.create(x, z)
            data = np.fromfile(filename, dtype=np.uint8)
            self.loaded[(x, z)] = data
            self.loading.discard((x, z))
            self.queue.task_done()
    def update(self):
        if not self.game.frame % fps:
            px = int(self.game.player.x) // 16
            pz = int(self.game.player.z) // 16
            for (x, z) in self.loaded.copy():
                if (x - px)**2 + (z - pz)**2 >= rdist**2:
                    self.unload(x, z)
            for x in range(px - rdist, px + rdist):
                for z in range(pz - rdist, pz + rdist):
                    if (x - px)**2 + (z - pz)**2 < rdist**2:
                        self.load(x, z)
    def draw(self):
        for (x, z) in self.loaded.copy():
            sx = 16 * x - self.game.player.x + width // 2
            sz = 16 * z - self.game.player.z + height // 2
            pg.draw.rect(self.game.screen, "green", (sx, sz, 16, 16))
class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.z = 0, 0
        self.speed = 10
    def update(self):
        keys = pg.key.get_pressed()
        dx, dz = 0, 0
        if keys[pg.K_w]: dz -= 1
        if keys[pg.K_a]: dx -= 1
        if keys[pg.K_s]: dz += 1
        if keys[pg.K_d]: dx += 1
        if dx or dz:
            l = np.sqrt(dx**2 + dz**2)
            dx /= l
            dz /= l
        self.x += dx * self.speed * self.game.dt
        self.z += dz * self.speed * self.game.dt
    def draw(self):
        sx = width // 2
        sz = height // 2
        pg.draw.circle(self.game.screen, "red", (sx, sz), 3)
class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("FreakCraft")
        self.screen = pg.display.set_mode((width, height))
        self.clock = pg.time.Clock()
        self.chunks = Chunks(self)
        self.player = Player(self)
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
        self.frame = 0
        while True:
            self.dt = self.clock.tick(fps) / 1000
            self.check_events()
            self.update()
            self.draw()
            self.frame += 1
            self.frame %= fps
if __name__ == "__main__":
    game = Game()
    game.run()