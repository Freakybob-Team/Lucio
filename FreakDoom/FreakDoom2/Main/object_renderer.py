import pygame as pg
from settings import *
class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_textures()
        self.sky_image = self.get_texture("resources/textures/sky.jpg", (width, height // 2))
        self.sky_offset = 0
    def draw(self):
        self.draw_background()
        self.render_game_objects()
    def draw_background(self):
        self.sky_offset = (self.sky_offset + 4.0 * self.game.player.rel) % width
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + width, 0))
        pg.draw.rect(self.screen, "darkgray", (0, height // 2, width, height))
    def render_game_objects(self):
        objects = sorted(self.game.raycasting.objects_to_render, key=lambda x: x[0], reverse=True)
        for depth, image, pos in objects:
            self.screen.blit(image, pos)
    def get_texture(self, path, res=(texture_size, texture_size)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)
    def load_wall_textures(self):
        return {
            1: self.get_texture("resources/textures/1.jpg")
        }