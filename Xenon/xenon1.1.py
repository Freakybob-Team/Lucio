import pygame as pg
import numpy as np
class Point:
    def __init__(self, p, m):
        self.p = p
        self.m = m
        self.v = np.zeros(2)
        self.f = np.zeros(2)
    def update(self, dt):
        dmpf = -self.v
        self.f += dmpf
        self.v += self.f / self.m * dt
        self.p += self.v * dt
        self.f = np.zeros(2)
    def draw(self, surface):
        pg.draw.circle(surface, "red", self.p, 3)
class Spring:
    def __init__(self, a, b, k):
        self.a = a
        self.b = b
        self.k = k
        self.rl = np.linalg.norm(self.b.p - self.a.p)
    def apply_force(self):
        d = self.b.p - self.a.p
        l = np.linalg.norm(d)
        f = -((l - self.rl) * self.k) * (d / l)
        self.a.f -= f
        self.b.f += f
    def draw(self, surface):
        pg.draw.line(surface, "green", self.a.p, self.b.p, 3)
class Body:
    def __init__(self, pos, pts, m, sprs, k):
        self.pos = np.array(pos, float)
        self.n = len(pts)
        self.pts = []
        for pt in pts:
            p = np.array(pt, float) - pts[0] + self.pos
            pt = Point(p, m / self.n)
            self.pts.append(pt)
        self.sprs = []
        for spr in sprs:
            a, b = self.pts[spr[0]], self.pts[spr[1]]
            spr = Spring(a, b, k)
            self.sprs.append(spr)
    def update(self, dt):
        for spr in self.sprs: spr.apply_force()
        for pt in self.pts: pt.update(dt)
    def draw(self, surface):
        for spr in self.sprs: spr.draw(surface)
        for pt in self.pts: pt.draw(surface)
