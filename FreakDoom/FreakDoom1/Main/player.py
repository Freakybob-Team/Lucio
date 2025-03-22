import math
import pygame as pg
from settings import *
class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.y = player_pos
        self.angle = player_angle
    def movement(self):
        sa = math.sin(self.angle)
        ca = math.cos(self.angle)
        dx, dy = 0, 0
        speed = player_lin_speed * self.game.dt
        sspeed = speed * sa
        cspeed = speed * ca
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            dx += cspeed
            dy += sspeed
        if keys[pg.K_a]:
            dx += sspeed
            dy += -cspeed
        if keys[pg.K_s]:
            dx += -cspeed
            dy += -sspeed
        if keys[pg.K_d]:
            dx += -sspeed
            dy += cspeed
        self.check_wall_collision(dx, dy)
        #if keys[pg.K_LEFT]:
        #    self.angle -= player_rot_speed * self.game.dt
        #if keys[pg.K_RIGHT]:
        #    self.angle += player_rot_speed * self.game.dt
        self.angle %= math.tau
    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map
    def check_wall_collision(self, dx, dy):
        size_scale = player_size / self.game.dt
        if self.check_wall(int(self.x + dx * size_scale), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * size_scale)):
            self.y += dy
    def mouse_control(self):
        mx, my = pg.mouse.get_pos()
        if (mx < mouse_border_left or mx > mouse_border_right or
            my < mouse_border_top or my > mouse_border_bottom):
            pg.mouse.set_pos([width // 2, height // 2])
        self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-mouse_max_speed, min(mouse_max_speed, self.rel))
        self.angle += self.rel * mouse_sensitivity * self.game.dt
    def update(self):
        self.movement()
        self.mouse_control()
    def draw(self):
        #pg.draw.line(self.game.screen, "orange", (self.x * 75, self.y * 75),
        #            (self.x * 75 + width * math.cos(self.angle),
        #             self.y * 75 + width * math.sin(self.angle)), 3)
        pg.draw.circle(self.game.screen, "red", (self.x * 75, self.y * 75), 15)
    def pos(self):
        return (self.x, self.y)
    def map_pos(self):
        return (int(self.x), int(self.y))