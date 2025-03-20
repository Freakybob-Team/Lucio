import pygame as pg
import numpy as np
class Point:
    def __init__(self, p, m):
        self.p = p
        self.m = m
        self.v = np.zeros(2)
        self.f = np.zeros(2)
    def update(self, dt):
        self.v += (self.f / self.m) * dt
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
    def apply_force(self):
        dp = self.b.p - self.a.p
        l = np.linalg.norm(dp)
        if l > 0:
            ndp = dp / l
            x = l - self.rl
            dv = self.b.v - self.a.v
            f = (self.k * x + np.dot(dv, ndp) / 2) * ndp
        else: f = np.zeros(2)
        self.a.f += f
        self.b.f -= f
    def draw(self, surface):
        pg.draw.line(surface, "green", self.a.p, self.b.p, 3)
class Frame:
    def __init__(self, p, k, pts):
        self.k = k
        self.pts = pts
        self.fptsp = [pt.p - p for pt in pts]
        self.fpts = [Point(pt.p+0, pt.m) for pt in pts]
        self.fsprs = [Spring(self.fpts[i], pts[i], self.k) for i in range(len(pts))]
        self.update()
    def apply_forces(self):
        for fspr in self.fsprs: fspr.apply_force()
    def update(self):
        mean = np.mean([pt.p for pt in self.pts], axis=0)
        for i, fpt in enumerate(self.fpts):
            fpt.p = self.fptsp[i]
        ath = []
        for i in range(len(self.pts)):
            dp1 = self.pts[i].p - mean
            dp2 = self.fptsp[i]
            dot = np.dot(dp1, dp2)
            l1 = np.linalg.norm(dp1)
            l2 = np.linalg.norm(dp2)
            cth = dot / (l1 * l2)
            th = np.arccos(cth)
            cross = np.cross(dp1, dp2)
            if cross > 0: th *= -1
            elif cross == 0: th = 0
            ath.append(th)
        ath = np.mean(ath)
        #print(np.degrees(ath))
        sth = np.sin(ath)
        cth = np.cos(ath)
        for fpt in self.fpts:
            x = fpt.p[0]
            y = fpt.p[1]
            fpt.p = np.array([x * cth - y * sth, x * sth + y * cth])
        for fpt in self.fpts:
            fpt.p += mean
    def draw(self, surface):
        for fspr in self.fsprs: fspr.draw(surface)
        for fpt in self.fpts: fpt.draw(surface)
class Body:
    def __init__(self, p, m, k, pts, sprs, outl):
        self.p = np.array(p, float)
        self.m, self.k = m, k
        self.n = len(pts)
        mean = np.mean(pts, axis=0)
        pts = np.array(pts, float) + self.p - mean
        self.pts = [Point(pt, m / self.n) for pt in pts]
        sprs = [[self.pts[spr[0]], self.pts[spr[1]]] for spr in sprs]
        self.sprs = [Spring(spr[0], spr[1], k) for spr in sprs]
        self.frame = Frame(self.p, self.k, self.pts)
        self.outl = outl
    def update(self, dt):
        self.frame.update()
        self.frame.apply_forces()
        for spr in self.sprs: spr.apply_force()
        for pt in self.pts: pt.update(dt)
    def draw(self, surface):
        self.frame.draw(surface)
        for spr in self.sprs: spr.draw(surface)
        for pt in self.pts: pt.draw(surface)
        for i in range(len(self.outl)):
            pg.draw.line(surface, "yellow", self.pts[self.outl[i]].p, self.pts[self.outl[(i + 1) % len(self.outl)]].p, 3)