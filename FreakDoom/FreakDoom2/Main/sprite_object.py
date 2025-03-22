import pygame as pg
from settings import *
class SpriteObject:
    def __init__(self, game, path, spr_pos, spr_scale, spr_shift):
        self.game = game
        self.player = game.player
        self.x, self.y = spr_pos
        self.sprite_scale = spr_scale
        self.sprite_shift = spr_shift
        self.image = pg.image.load(path).convert_alpha()
        self.image_width = self.image.get_width()
        self.image_ratio = self.image_width / self.image.get_height()
        self.dx, self.dy = 0, 0
        self.th, self.screen_x = 0, 0
        self.dist, self.norm_dist = 1, 1
    def get_sprite_projection(self):
        proj = screen_dist / self.norm_dist * self.sprite_scale
        proj_width, proj_height = proj * self.image_ratio, proj
        image = pg.transform.scale(self.image, (proj_width, proj_height))
        height_shift = proj_height * self.sprite_shift
        pos = (self.screen_x - proj_width // 2, height // 2 - proj_height // 2 + height_shift)
        self.game.raycasting.objects_to_render.append((self.norm_dist, image, pos))
    def get_sprite(self):
        dx = self.x - self.player.x
        dy = self.y - self.player.y
        self.dx, self.dy = dx, dy
        self.th = math.atan2(dy, dx)
        dth = self.th - self.player.angle
        if (dx > 0 and self.player.angle > math.pi) or (dx < 0 and dy < 0):
            dth += math.tau
        drays = dth / dangle
        self.screen_x = (nrays // 2 + drays) * scale
        self.dist = math.hypot(dx, dy)
        self.norm_dist = self.dist * math.cos(dth)
        if -self.image_width // 2 < self.screen_x < (width + self.image_width // 2) and self.norm_dist > 0.5:
            self.get_sprite_projection()
    def update(self):
        self.get_sprite()