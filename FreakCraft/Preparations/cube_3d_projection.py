import pygame as pg
import numpy as np
pg.init()
screen = pg.display.set_mode((1000, 700))
clock = pg.time.Clock()
class Cube:
    def __init__(self, scale, pos):
        self.pos = np.array(pos, float)
        self.pts = [
            [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1],
            [1, 1, 0], [1, 0, 1], [0, 1, 1], [1, 1, 1]
        ]
        self.edges = [
            [0, 1], [1, 4], [4, 2], [2, 0],
            [3, 5], [5, 7], [7, 6], [6, 3],
            [0, 3], [1, 5], [2, 6], [4, 7]
        ]
        self.pts = np.array(self.pts, float)
        self.pts -= np.mean(self.pts, 0)
        self.pts *= scale / 2
    def projected(self):
        return self.pts[:,:2] + self.pos[:2]
    def rotate(self, thx, thy, thz):
        sthx = np.sin(thx)
        cthx = np.cos(thx)
        rx = np.array([
            [1, 0, 0],
            [0, cthx, -sthx],
            [0, sthx, cthx]
        ])
        sthy = np.sin(thy)
        cthy = np.cos(thy)
        ry = np.array([
            [cthy, 0, sthy],
            [0, 1, 0],
            [-sthy, 0, cthy]
        ])
        sthz = np.sin(thz)
        cthz = np.cos(thz)
        rz = np.array([
            [cthz, -sthz, 0],
            [sthz, cthz, 0],
            [0, 0, 1]
        ])
        r = rx @ ry @ rz
        self.pts @= r.T
    def update(self, dt):
        self.rotate(0.5 * dt, 0.3 * dt, 0.4 * dt)
    def draw(self):
        ppts = self.projected()
        [
            pg.draw.line(screen, "yellow", ppts[self.edges[i][0]], ppts[self.edges[i][1]], 3)
            for i in range(12)
        ]
cube = Cube(300, [500, 350, 0])
xt = False
while True:
    dt = clock.tick(60) / 1000
    for event in pg.event.get():
        if event.type == pg.QUIT:
            xt = True
    if xt: break
    cube.update(dt)
    screen.fill("black")
    cube.draw()
    pg.display.flip()
pg.quit()