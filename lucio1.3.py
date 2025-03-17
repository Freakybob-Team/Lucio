import pygame as pg
import numpy as np
def collision(p1, p2):
    if (p1.le <= p2.ri and
        p1.ri >= p2.le and
        p1.to <= p2.bo and
        p1.bo >= p2.to):
        pts1 = p1.pts + p1.pos
        pts2 = p2.pts + p2.pos
        moverlap = float('inf')
        bnormal = None
        for p in [p1, p2]:
            x = p.pts[:,0]
            y = p.pts[:,1]
            for i in range(p.n):
                ex = x[(i + 1) % p.n] - x[i]
                ey = y[(i + 1) % p.n] - y[i]
                normal = np.array([-ey, ex])
                normal /= np.linalg.norm(normal)
                pp1 = np.dot(pts1, normal)
                pp2 = np.dot(pts2, normal)
                min1, max1 = np.min(pp1), np.max(pp1)
                min2, max2 = np.min(pp2), np.max(pp2)
                if max1 < min2 or max2 < min1: return
                overlap = min(max1, max2) - max(min1, min2)
                if overlap < moverlap:
                    moverlap = overlap
                    bnormal = normal
        direction = 1 if np.dot(p2.pos - p1.pos, bnormal) > 0 else -1
        mtv = bnormal * moverlap * direction
        p1.dpos -= mtv / 2
        p2.dpos += mtv / 2
        rv = p2.v - p1.v
        rvn = np.dot(rv, bnormal)
        e = min(p1.e, p2.e)
        j = -(1 + e) * rvn
        j /= 1 / p1.m + 1 / p2.m
        impulse = j * bnormal
        p1.v -= impulse / p1.m
        p2.v += impulse / p2.m
class Polygon:
    def __init__(self, pos, pts, m, d, e, col):
        self.pos = np.array(pos, np.float64)
        self.pts = np.array(pts, np.float64)
        self.m, self.d, self.e = m, d, e
        self.n = len(self.pts)
        self.a = self.get_a()
        self.pts -= self.get_c()
        self.pts *= np.sqrt(self.m / self.d / self.a)
        self.a = self.m / self.d
        self.v = np.zeros(2)
        self.f = np.zeros(2)
        self.dpos = np.zeros(2)
        self.update_box()
        self.col = col
    def get_a(self):
        x = self.pts[:,0]
        y = self.pts[:,1]
        dot1 = np.dot(x, np.roll(y, -1))
        dot2 = np.dot(y, np.roll(x, -1))
        return np.abs(dot1 - dot2) / 2
    def get_c(self):
        x = self.pts[:,0]
        y = self.pts[:,1]
        f = (x * np.roll(y, -1)) - (y * np.roll(x, -1))
        cx = np.sum((x + np.roll(x, -1)) * f) / (6 * self.a)
        cy = np.sum((y + np.roll(y, -1)) * f) / (6 * self.a)
        return np.array([cx, cy])
    def rotate(self, th):
        sth = np.sin(th)
        cth = np.cos(th)
        x = self.pts[:,0]
        y = self.pts[:,1]
        nx = x * cth - y * sth
        ny = x * sth + y * cth
        self.pts = np.vstack([nx, ny]).T
    def update_box(self):
        x = self.pts[:,0] + self.pos[0]
        y = self.pts[:,1] + self.pos[1]
        self.le, self.ri = np.min(x), np.max(x)
        self.to, self.bo = np.min(y), np.max(y)
    def update(self, dt):
        self.v += self.f / self.m * dt
        self.pos += self.v * dt
        self.pos += self.dpos
        self.dpos = np.zeros(2)
        self.update_box()
    def draw(self, surface):
        pg.draw.polygon(surface, self.col, self.pts + self.pos)
        pg.draw.polygon(surface, (150, 150, 150), self.pts + self.pos, 5)
class Player(Polygon):
    def __init__(self, pos, pts, m, d, e, col):
        super().__init__(pos, pts, m, d, e, col)
    def update(self, dt):
        m = np.array(pg.mouse.get_pos(), np.float64)
        self.f = (m - self.pos) * self.m
        super().update(dt)
        #self.pos = m