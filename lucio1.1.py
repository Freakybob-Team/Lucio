import pygame as pg
import numpy as np
def collision(p1, p2):
    if (p1.le <= p2.ri and
        p1.ri >= p2.le and
        p1.to <= p2.bo and
        p1.bo >= p2.to):
        moverlap = float('inf')
        bnormal = None
        pts1 = p1.pts + p1.p
        pts2 = p2.pts + p2.p
        for p in [p1, p2]:
            normals = p.get_rnormals()
            for normal in normals:
            #x = p.pts[:,0]
            #y = p.pts[:,1]
            #for i in range(p.n):
                #ex = x[(i + 1) % p.n] - x[i]
                #ey = y[(i + 1) % p.n] - y[i]
                #normal = np.array([-ey, ex])
                #normal /= np.linalg.norm(normal)
                pp1 = np.dot(pts1, normal)
                pp2 = np.dot(pts2, normal)
                min1, max1 = np.min(pp1), np.max(pp1)
                min2, max2 = np.min(pp2), np.max(pp2)
                if max1 < min2 or max2 < min1: return
                overlap = min(max1, max2) - max(min1, min2)
                if overlap < moverlap:
                    moverlap = overlap
                    bnormal = normal
        direction = 1 if np.dot(p1.p - p2.p, bnormal) >= 0 else -1
        mtv = bnormal * moverlap * direction
        p1.dp += mtv / 2
        p2.dp -= mtv / 2
class Polygon:
    def __init__(self, p, pts, m, d, col):
        self.p = np.array(p, np.float64)
        self.pts = np.array(pts, np.float64)
        self.m, self.d, self.n = m, d, len(self.pts)
        self.a = self.get_a()
        self.pts -= self.get_c()
        self.pts *= np.sqrt(self.m / self.d / self.a)
        self.normals = self.get_normals()
        self.a = self.m / self.d
        self.dp = np.zeros(2)
        self.v = np.zeros(2)
        self.f = np.zeros(2)
        self.th = 0.0
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
        f = (x * np.roll(y, -1) - y * np.roll(x, -1))
        cx = np.sum((x + np.roll(x, -1)) * f) / (6 * self.a)
        cy = np.sum((y + np.roll(y, -1)) * f) / (6 * self.a)
        return np.array([cx, cy])
    def get_normals(self):
        x = self.pts[:,0]
        y = self.pts[:,1]
        ex = np.roll(x, -1) - x
        ey = np.roll(y, -1) - y
        normals = np.vstack([-ey, ex]).T
        normals /= np.linalg.norm(normals, axis=1, keepdims=True)
        return normals
    def get_rnormals(self):
        sa = np.sin(self.th)
        ca = np.cos(self.th)
        x = self.normals[:,0]
        y = self.normals[:,1]
        nx = x * ca - y * sa
        ny = x * sa + y * ca
        return np.vstack([nx, ny]).T
    def rotate(self, a):
        sa = np.sin(a)
        ca = np.cos(a)
        x = self.pts[:,0]
        y = self.pts[:,1]
        nx = x * ca - y * sa
        ny = x * sa + y * ca
        self.pts = np.vstack([nx, ny]).T
        self.th += a
        self.th %= 360
    def update_box(self):
        x = self.pts[:,0] + self.p[0]
        y = self.pts[:,1] + self.p[1]
        self.le, self.ri = np.min(x), np.max(x)
        self.to, self.bo = np.min(y), np.max(y)
    def update(self, dt):
        self.p += self.dp
        self.v += self.f / self.m * dt
        self.p += self.v * dt
        self.dp = np.zeros(2)
        self.update_box()
    def draw(self, surface):
        pg.draw.polygon(surface, self.col, self.pts + self.p)
        pg.draw.polygon(surface, (150, 150, 150), self.pts + self.p, 5)
class Player(Polygon):
    def __init__(self, p, m, d, col):
        pts = [[0, 0], [1, 0], [1, 1], [0, 1]]
        super().__init__(p, pts, m, d, col)
    def update(self, dt):
        m = np.array(pg.mouse.get_pos(), np.float64)
        self.f = (m - self.p) * self.m
        super().update(dt)