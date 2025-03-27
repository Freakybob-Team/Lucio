import pygame, numpy, time, os
from threading import Thread
width, height = 1000, 700
rdist, fps = 16, 60
class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.y, self.z = 0, 0, 0
        self.thx, self.thy, self.thz = 0, 0, 0
        self.speed = 30
    def update(self):
        keys = pygame.key.get_pressed()
        dx, dz = 0, 0
        if keys[pygame.K_w]: dz -= 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_s]: dz += 1
        if keys[pygame.K_d]: dx += 1
        if dx or dz:
            length = numpy.sqrt(dx**2 + dz**2)
            dx /= length
            dz /= length
        self.x += dx * self.speed * self.game.dt
        self.z += dz * self.speed * self.game.dt
    def draw(self):
        sx = width // 2
        sz = height // 2
        pygame.draw.circle(self.game.screen, "red", (sx, sz), 3)
class Chunks:
    def __init__(self, game):
        self.game = game
        self.loaded = {}
        self.loading = set()
        os.makedirs("chunks", exist_ok=True)
        Thread(target=self.loader, daemon=True).start()
    def create(self, x, z):
        blocks = numpy.zeros(16384, dtype=numpy.uint8)
        for i in range(8192): blocks[i] = 1
        visible = self.getvisible(blocks)
        self.store(blocks, visible, x, z)
    def store(self, blocks, visible, x, z):
        filename = f"chunks/{x}_{z}.dat"
        data = numpy.hstack((blocks, visible.flatten()))
        data.tofile(filename)
    def load(self, x, z):
        if (x, z) not in self.loaded:
            if (x, z) not in self.loading:
                self.loading.add((x, z))
    def unload(self, x, z):
        #blocks = self.loaded[(x, z)]["blocks"]
        #visible = self.loaded[(x, z)]["visible"]
        #self.store(blocks, visible, x, z)
        del self.loaded[(x, z)]
    def getvisible(self, blocks):
        neighbors = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]
        visible = []
        for i in range(16384):
            if not blocks[i]:
                bx = i % 16
                by = i // 256
                bz = (i // 16) % 16
                for (dx, dy, dz) in neighbors:
                    nx = bx + dx
                    ny = by + dy
                    nz = bz + dz
                    if 0 <= nx <= 15 and 0 <= nz <= 15 and 0 <= ny <= 63:
                        ni = nx + 16 * nz + 256 * ny
                        if blocks[ni]:
                            visible.append((nx, ny, nz))
        visible = numpy.array(visible, dtype=numpy.uint8)
        return visible
    def loader(self):
        while True:
            px = int(self.game.player.x) // 16
            pz = int(self.game.player.z) // 16
            for (x, z) in self.loaded.copy():
                if (x - px)**2 + (z - pz)**2 >= rdist**2:
                    self.unload(x, z)
            for x in range(px - rdist, px + rdist):
                for z in range(pz - rdist, pz + rdist):
                    if (x - px)**2 + (z - pz)**2 < rdist**2:
                        self.load(x, z)
            for (x, z) in sorted(self.loading, key=lambda p: (p[0] - px)**2 + (p[1] - pz)**2):
                if (x - px)**2 + (z - pz)**2 >= rdist**2:
                    self.loading.discard((x, z))
                    continue
                filename = f"chunks/{x}_{z}.dat"
                if not os.path.exists(filename): self.create(x, z)
                data = numpy.fromfile(filename, dtype=numpy.uint8)
                blocks = data[:16384]
                visible = data[16384:].reshape(-1, 3)
                self.loaded[(x, z)] = {"blocks": blocks, "visible": visible}
                self.loading.discard((x, z))
            time.sleep(1)
    def draw(self):
        for (x, z) in self.loaded.copy():
            sx = 16 * x - self.game.player.x + width // 2
            sz = 16 * z - self.game.player.z + height // 2
            pygame.draw.rect(self.game.screen, "green", (sx, sz, 16, 16), 1)
class Renderer:
    def __init__(self, game):
        self.game = game
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("FreakCraft")
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.player = Player(self)
        self.chunks = Chunks(self)
        self.renderer = Renderer(self)
    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
    def update(self):
        self.player.update()
    def draw(self):
        self.screen.fill("black")
        self.chunks.draw()
        self.player.draw()
        pygame.display.flip()
    def run(self):
        while True:
            self.dt = self.clock.tick(fps) / 1000
            self.check_events()
            self.update()
            self.draw()
if __name__ == "__main__":
    game = Game()
    game.run()