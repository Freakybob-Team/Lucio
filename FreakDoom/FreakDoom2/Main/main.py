import pygame as pg
from object_renderer import *
from object_handler import *
from sprite_object import *
from raycasting import *
from settings import *
from player import *
from map import *
import sys
class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)
        self.screen = pg.display.set_mode((width, height))
        self.clock = pg.time.Clock()
        self.dt = 1
        self.new_game()
    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
    def update(self):
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        pg.display.flip()
        self.dt = self.clock.tick(fps)
        pg.display.set_caption(str(round(self.clock.get_fps())))
    def draw(self):
        #self.screen.fill((50, 0, 50))
        self.object_renderer.draw()
        #self.map.draw()
        #self.player.draw()
    def check_events(self):
        for event in pg.event.get():
            if (event.type == pg.QUIT or
                (event.type == pg.KEYDOWN and
                 event.key == pg.K_ESCAPE)):
                pg.quit()
                sys.exit()
    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()
if __name__ == "__main__":
    game = Game()
    game.run()