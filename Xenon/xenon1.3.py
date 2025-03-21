import pygame as pg
import numpy as np
def zs(n): return np.zeros(n)
def vl(v): return np.linalg.norm(v)
def arr(a): return np.array(a, float)
def dot(a, b): return np.dot(a, b)
def cross(a, b): return np.cross(a, b)
def clip(x, a, b): return np.clip(x, a, b)
def mean(a, ax): return np.mean(a, ax)
def sin(th): return np.sin(th)
def cos(th): return np.cos(th)
def arccos(cth): return np.arccos(cth)
def arctan2(a, b): return np.arctan2(a, b)
def dcircle(s, c, a, r): pg.draw.circle(s, c, a, r)
def dline(s, c, a, b, w): pg.draw.line(s, c, a, b, w)
class Point:
    def __init__(self, p, m):
        self.p = p
        self.m = m
        self.v = zs(2)
        self.f = zs(2)
    def update(self, dt):
        self.v += (self.f / self.m) * dt
        self.p += self.v * dt
        self.f = zs(2)
    def draw(self, surface):
        dcircle(surface, "red", self.p, 3)
class Spring:
    def __init__(self, a, b, k):
        self.a = a
        self.b = b
        self.k = k
        self.rl = vl(self.b.p - self.a.p)
    def apply_force(self):
        dp = self.b.p - self.a.p
        l = vl(dp)
        if l:
            ndp = dp / l
            x = l - self.rl
            dv = self.b.v - self.a.v
            f = (self.k * x + dot(dv, ndp) / 3) * ndp
            self.a.f += f
            self.b.f -= f
    def draw(self, surface):
        dline(surface, "green", self.a.p, self.b.p, 3)
class Frame:
    def __init__(self, body):
        self.body = body
        self.skl = [pt.p - body.p for pt in self.body.pts]
        self.pts = [Point(pt.p + 0, pt.m) for pt in self.body.pts]
        self.sprs = [Spring(self.pts[i], self.body.pts[i], self.body.k) for i in range(self.body.n)]
        self.update()
    def apply_forces(self):
        for spr in self.sprs: spr.apply_force()
    def rotate(self, th):
        sth = sin(th)
        cth = cos(th)
        for pt in self.pts:
            x = pt.p[0] - self.body.p[0]
            y = pt.p[1] - self.body.p[1]
            pt.p = arr([x * cth - y * sth, x * sth + y * cth]) + self.body.p
    def update(self):
        angles = []
        for pt in self.pts: pt.p = self.body.p + 0
        for i in range(self.body.n):
            self.pts[i].p += self.skl[i]
            a = self.body.pts[i].p - self.body.p
            b = self.pts[i].p - self.body.p
            angle = arctan2(b[1], b[0]) - arctan2(a[1], a[0])
            angles.append(angle)
        mean_cos = np.mean([cos(a) for a in angles])
        mean_sin = np.mean([sin(a) for a in angles])
        ath = -arctan2(mean_sin, mean_cos)
        self.rotate(ath)
    def draw(self, surface):
        for spr in self.sprs: spr.draw(surface)
        for pt in self.pts: pt.draw(surface)
class Body:
    def __init__(self, p, m, k, pts, sprs):
        self.n = len(pts)
        self.p = arr(p)
        self.m = m
        self.k = k
        pts = arr(pts) + self.p - mean(pts, 0)
        self.pts = [Point(pt, self.m / self.n) for pt in pts]
        sprs = [[self.pts[a], self.pts[b]] for a, b in sprs]
        self.sprs = [Spring(a, b, self.k) for a, b in sprs]
        self.frame = Frame(self)
    def rotate(self, th):
        sth = sin(th)
        cth = cos(th)
        for pt in self.pts:
            x = pt.p[0] - self.p[0]
            y = pt.p[1] - self.p[1]
            pt.p = arr([x * cth - y * sth, x * sth + y * cth]) + self.p
    def update(self, dt):
        self.p = mean([pt.p for pt in self.pts], 0)
        self.frame.update()
        self.frame.apply_forces()
        for spr in self.sprs: spr.apply_force()
        for pt in self.pts: pt.update(dt)
    def draw(self, surface):
        #self.frame.draw(surface)
        #for spr in self.sprs: spr.draw(surface)
        #for pt in self.pts: pt.draw(surface)
        for i in range(self.n):
            dline(surface, "yellow", self.pts[i].p, self.pts[(i + 1) % self.n].p, 3)
