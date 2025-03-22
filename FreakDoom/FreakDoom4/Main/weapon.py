from sprite_object import *
class Weapon(AnimatedSpriteObject):
    def __init__(self, game, path="resources/sprites/animated/weapon/gun1.jpg", spr_scale=1.2, anim_time=100):
        super().__init__(game, path, (0, 0), spr_scale, 0, anim_time)
        self.images = [
            pg.transform.smoothscale(image, (self.image.get_width() * spr_scale, self.image.get_height() * spr_scale))
            for image in self.images
        ]
        self.pos = (width // 2 - self.images[0].get_width() // 2, height - self.images[0].get_height())
        self.reloading = False
        self.reloading_i = 0
        self.nimages = len(self.images)
        self.damage = 50
    def animate_shot(self):
        if self.reloading:
            self.game.player.shot = False
            if self.anim_new:
                self.reloading_i += 1
                if self.reloading_i == self.nimages:
                    self.reloading = False
                    self.reloading_i = 0
    def draw(self):
        self.game.screen.blit(self.images[self.reloading_i], self.pos)
    def update(self):
        self.check_anim_time()
        self.animate_shot()