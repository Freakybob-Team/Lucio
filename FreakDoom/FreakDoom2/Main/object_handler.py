from sprite_object import *
class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprites = []
        self.sprites_path = "resources/sprites/"
        self.add_sprite(SpriteObject(game, path="resources/sprites/freakbob.png",
                                     spr_pos=(8, 3.5), spr_scale=0.6, spr_shift=0.4))
    def update(self):
        [sprite.update() for sprite in self.sprites]
    def add_sprite(self, sprite):
        self.sprites.append(sprite)