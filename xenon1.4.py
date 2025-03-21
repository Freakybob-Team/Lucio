import pygame as pg
import numpy as np
def pib(pt, body):
    p = pt.p
    x, y = p
    inside = False
    cedge = None
    moverlap = float('inf')
    for i in range(body.n):
        pt1 = body.pts[i]
        pt2 = body.pts[(i + 1) % body.n]
        p1 = pt1.p
        p2 = pt2.p
        x1, y1 = p1
        x2, y2 = p2
        if min(y1, y2) < y <= max(y1, y2):
            xi = (y - y1) * (x2 - x1) / (y2 - y1) + x1
            if x < xi: inside = not inside
        dp = p2 - p1
        lsq = np.dot(dp, dp)
        t = np.dot(p - p1, dp) / lsq
        t = np.clip(t, 0, 1)
        cp = p1 + t * dp
        overlap = np.linalg.norm(p - cp)
        if overlap < moverlap:
            moverlap = overlap
            cedge = [pt1, pt2, cp]
    return inside, cedge
def resolve_overlap(pt, cedge):
    pt1, pt2, cp = cedge
    dp = pt.p - cp
    l = np.linalg.norm(dp)
    el = np.linalg.norm(pt2.p - pt1.p)
    l1 = np.linalg.norm(pt1.p - cp)
    l2 = np.linalg.norm(pt2.p - cp)
    tm = pt.m + pt1.m + pt2.m
    if l > 0:
        pt.p -= dp * (pt1.m + pt2.m) / tm
        pt1.p += dp * (pt.m / tm) * (l2 / el)
        pt2.p += dp * (pt.m / tm) * (l1 / el)
        ndp = dp / l
        rv = pt.v - (pt1.v * l2 + pt2.v * l1) / el
        nrv = np.dot(rv, ndp) * ndp
        e = 0.8
        j = -(1 + e) * nrv / (1 / pt.m + (l2**2 + l1**2) / (pt1.m + pt2.m) / el**2)
        pt.v += j / pt.m
        pt1.v -= j * l2 / (pt1.m + pt2.m) / el
        pt2.v -= j * l1 / (pt1.m + pt2.m) / el
def collision(body1, body2):
    for pt in body1.pts:
        inside, cedge = pib(pt, body2)
        if inside: resolve_overlap(pt, cedge)
    for pt in body2.pts:
        inside, cedge = pib(pt, body1)
        if inside: resolve_overlap(pt, cedge)
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
        self.rl = np.linalg.norm(self.b.p - self.a.p)
    def apply_force(self):
        dp = self.b.p - self.a.p
        l = np.linalg.norm(dp)
        if l > 0:
            ndp = dp / l
            f = self.k * (l - self.rl)
            f += np.dot(self.b.v - self.a.v, ndp) / 3
            f *= ndp
            self.a.f += f
            self.b.f -= f
    def draw(self, surface):
        pg.draw.line(surface, "green", self.a.p, self.b.p, 3)
class Frame:
    def __init__(self, body):
        self.body = body
        self.skl = [pt.p - self.body.p for pt in self.body.pts]
        self.pts = [Point(pt.p + 0, pt.m) for pt in self.body.pts]
        sprs = [[self.pts[i], self.body.pts[i]] for i in range(self.body.n)]
        self.sprs = [Spring(a, b, self.body.k) for a, b in sprs]
        self.update()
    def apply_forces(self):
        for spr in self.sprs: spr.apply_force()
    def rotate(self, th):
        sth = np.sin(th)
        cth = np.cos(th)
        for pt in self.pts:
            pt.p -= self.body.p
            x = pt.p[0]
            y = pt.p[1]
            nx = x * cth - y * sth
            ny = x * sth + y * cth
            pt.p = np.array([nx, ny], float) + self.body.p
    def update(self):
        for pt in self.pts: pt.p = self.body.p + 0
        ths = []
        for i in range(self.body.n):
            self.pts[i].p += self.skl[i]
            a = self.pts[i].p - self.body.p
            b = self.body.pts[i].p - self.body.p
            th = np.arctan2(b[1], b[0]) - np.arctan2(a[1], a[0])
            ths.append(th)
        cmean = np.mean([np.cos(th) for th in ths], 0)
        smean = np.mean([np.sin(th) for th in ths], 0)
        ath = np.arctan2(smean, cmean)
        self.rotate(ath)
    def draw(self, surface):
        for spr in self.sprs: spr.draw(surface)
        for pt in self.pts: pt.draw(surface)
class Body:
    def __init__(self, p, m, k, pts, sprs):
        self.n = len(pts)
        self.p = np.array(p, float)
        self.m, self.k = m, k
        pts = np.array(pts, float)
        pts -= np.mean(pts, 0)
        pts += self.p
        self.pts = [Point(pt, self.m / self.n) for pt in pts]
        sprs = [[self.pts[a], self.pts[b]] for a, b in sprs]
        self.sprs = [Spring(a, b, self.k) for a, b in sprs]
        self.frame = Frame(self)
    def update(self, dt):
        self.p = np.mean([pt.p for pt in self.pts], 0)
        self.frame.update()
        self.frame.apply_forces()
        for spr in self.sprs: spr.apply_force()
        for pt in self.pts: pt.update(dt)
    def draw(self, surface):
        #self.frame.draw(surface)
        #for spr in self.sprs: spr.draw(surface)
        #for pt in self.pts: pt.draw(surface)
        #for i in range(self.n):
        #    pg.draw.line(surface, "yellow", self.pts[i].p, self.pts[(i + 1) % self.n].p, 3)
        pg.draw.polygon(surface, "yellow", [pt.p for pt in self.pts])
        pg.draw.polygon(surface, "red", [pt.p for pt in self.pts], 3)