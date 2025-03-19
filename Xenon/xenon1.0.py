import pygame as pg
import numpy as np
class Point:
    def __init__(self, p, m):
        self.p = p
        self.m = m
        self.v = np.zeros(2)
        self.f = np.zeros(2)
    def update(self, dt):
        dmpf = -0.5 * self.v
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
        self.rl = np.linalg.norm(b.p - a.p)
    def update(self):
        d = self.b.p - self.a.p
        l = np.linalg.norm(d)
        if l: fm = self.k * (l - self.rl); f = -fm * (d / l)
        else: f = np.zeros(2)
        self.a.f -= f
        self.b.f += f
class Body:
    def __init__(self, pos, pts, sprs):
        self.pos = np.array(pos, float)
        self.n = len(pts)
        self.pts = []
        for pt in pts:
            p = np.array(pt[0], float)
            p -= pts[0][0]
            p += self.pos
            m = pt[1]
            pt = Point(p, m)
            self.pts.append(pt)
        self.sprs = []
        for spr in sprs:
            a = self.pts[spr[0] - 1]
            b = self.pts[spr[1] - 1]
            k = spr[2]
            spr = Spring(a, b, k)
            self.sprs.append(spr)
    def update(self, dt):
        for spr in self.sprs: spr.update()
        for pt in self.pts: pt.update(dt)
    def draw(self, surface):
        for spr in self.sprs: pg.draw.line(surface, "yellow", spr.a.p, spr.b.p, 3)
        for pt in self.pts: pt.draw(surface)
