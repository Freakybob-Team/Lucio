import pygame as pg
import numpy as np
def line_intersection(pt1, pt2, pt3, pt4):
    denom = (pt1[0] - pt2[0]) * (pt3[1] - pt4[1]) - (pt1[1] - pt2[1]) * (pt3[0] - pt4[0])
    if denom == 0: return None
    t = ((pt1[0] - pt3[0]) * (pt3[1] - pt4[1]) - (pt1[1] - pt3[1]) * (pt3[0] - pt4[0])) / denom
    u = -((pt1[0] - pt2[0]) * (pt1[1] - pt3[1]) - (pt1[1] - pt2[1]) * (pt1[0] - pt3[0])) / denom
    if 0 <= t <= 1 and 0 <= u <= 1:
        x = pt1[0] + t * (pt2[0] - pt1[0])
        y = pt1[1] + t * (pt2[1] - pt1[1])
        return np.array([x, y])
    return None
def collision(p1, p2, e=0.6, fr=0.4):
    if p1.imm == 2 and p2.imm == 2: return
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
        if p1.imm and not p2.imm: p2.pos += mtv
        elif p2.imm and not p1.imm: p1.pos -= mtv
        else:
            p1.pos -= mtv / 2
            p2.pos += mtv / 2
        cpoints = []
        for i in range(p1.n):
            for j in range(p2.n):
                pt1, pt2 = pts1[i], pts1[(i + 1) % p1.n]
                pt3, pt4 = pts2[j], pts2[(j + 1) % p2.n]
                intersection = line_intersection(pt1, pt2, pt3, pt4)
                if intersection is not None: cpoints.append(intersection)
        if not cpoints: return
        cpoint = np.mean(cpoints, axis=0)
        r1 = cpoint - p1.pos
        r2 = cpoint - p2.pos
        v1 = p1.v + np.array([-p1.w * r1[1], p1.w * r1[0]])
        v2 = p2.v + np.array([-p2.w * r2[1], p2.w * r2[0]])
        rv = v2 - v1
        rvn = np.dot(rv, bnormal)
        j = -(1 + e) * rvn
        j /= (1 / p1.m + 1 / p2.m +
              np.dot(np.cross(r1, bnormal), np.cross(r1, bnormal)) / p1.I +
              np.dot(np.cross(r2, bnormal), np.cross(r2, bnormal)) / p2.I)
        impulse = j * bnormal
        p1.v -= impulse / p1.m
        p2.v += impulse / p2.m
        p1.w -= np.cross(r1, impulse) / p1.I
        p2.w += np.cross(r2, impulse) / p2.I
        tangent = np.array([-bnormal[1], bnormal[0]])
        rvt = np.dot(rv, tangent)
        mfr = fr * abs(j)
        jt = -rvt / (1 / p1.m + 1 / p2.m +
                     np.dot(np.cross(r1, tangent), np.cross(r1, tangent)) / p1.I +
                     np.dot(np.cross(r2, tangent), np.cross(r2, tangent)) / p2.I)
        jt = np.clip(jt, -mfr, mfr)
        frimpulse = jt * tangent
        p1.v -= frimpulse / p1.m
        p2.v += frimpulse / p2.m
        p1.w -= np.cross(r1, frimpulse) / p1.I
        p2.w += np.cross(r2, frimpulse) / p2.I
class Polygon:
    def __init__(self, pos, pts, m, d, col, imm=0):
        self.pos = np.array(pos, np.float64)
        self.pts = np.array(pts, np.float64)
        self.m, self.d = m, d
        self.n = len(self.pts)
        self.a = self.get_a()
        self.pts -= self.get_c()
        self.pts *= np.sqrt(self.m / self.d / self.a)
        self.a = self.m / self.d
        self.v = np.zeros(2)
        self.f = np.zeros(2)
        self.I, self.w = self.get_I(), 0.0
        self.update_box()
        self.col = col
        self.imm = imm
        if imm: self.m = float('inf'); self.I *= 2
        if imm == 2: self.I = float('inf')
    def get_a(self):
        x = self.pts[:,0]
        y = self.pts[:,1]
        dot1 = np.dot(x, np.roll(y, -1))
        dot2 = np.dot(y, np.roll(x, -1))
        return np.abs(dot1 - dot2) / 2
    def get_c(self):
        x = self.pts[:,0]
        y = self.pts[:,1]
        f = np.abs((x * np.roll(y, -1)) - (y * np.roll(x, -1)))
        cx = np.sum((x + np.roll(x, -1)) * f) / (6 * self.a)
        cy = np.sum((y + np.roll(y, -1)) * f) / (6 * self.a)
        return np.array([cx, cy])
    def get_I(self):
        x = self.pts[:,0]
        y = self.pts[:,1]
        numerator = 0.0
        for i in range(self.n):
            xi, yi = x[i], y[i]
            xi1, yi1 = x[(i + 1) % self.n], y[(i + 1) % self.n]
            cross = xi * yi1 - xi1 * yi
            term = (xi**2 + xi * xi1 + xi1**2 + yi**2 + yi * yi1 + yi1**2)
            numerator += cross * term
        return self.m * numerator / (6 * self.a)
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
    def update(self, dt, dmp=0.999999):
        if not self.imm:
            self.v += self.f / self.m * dt
            self.v *= 1 - dmp * dt
            self.pos += self.v * dt
        self.w *= 1 - dmp * dt
        self.rotate(self.w * dt)
        self.update_box()
    def draw(self, surface):
        pg.draw.polygon(surface, self.col, self.pts + self.pos)
        pg.draw.polygon(surface, "gray", self.pts + self.pos, 5)
class Player(Polygon):
    def __init__(self, pos, pts, m, d, col):
        super().__init__(pos, pts, m, d, col)
    def update(self, dt):
        m = np.array(pg.mouse.get_pos(), np.float64)
        self.f = (m - self.pos) * self.m * 20
        super().update(dt)
    def draw(self, surface):
        m = np.array(pg.mouse.get_pos(), np.float64)
        pg.draw.line(surface, "brown", self.pos, m, 10)
        pg.draw.circle(surface, "red", m, 5)
        super().draw(surface)
class Engine:
    def __init__(self, surface):
        self.surface = surface
        self.polygons = []
    def create_polygon(self, pos, pts, m, d, col):
        self.polygons.append(Polygon(pos, pts, m, d, col))
    def update(self, dt):
        for p in self.polygons: p.update(dt)
        for i in range(len(self.polygons)):
            for j in range(i + 1, len(self.polygons)):
                collision(self.polygons[i], self.polygons[j])
        self.surface.fill((50, 0, 50))
        for p in self.polygons: p.draw(self.surface)
        pg.display.flip()
# Lucio
