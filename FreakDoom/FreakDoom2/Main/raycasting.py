import math
import pygame as pg
from settings import *
class RayCasting:
    def __init__(self, game):
        self.game = game
        self.ray_casting_result = []
        self.objects_to_render = []
        self.textures = self.game.object_renderer.wall_textures
    def get_objects_to_render(self):
        self.objects_to_render = []
        for ray, values in enumerate(self.ray_casting_result):
            depth, proj_height, texture, offset = values
            if proj_height < height:
                wall_column = self.textures[texture].subsurface(
                    offset * (texture_size - scale), 0, scale, texture_size
                )
                wall_column = pg.transform.scale(wall_column, (scale, proj_height))
                wall_pos = (ray * scale, height // 2 - proj_height // 2)
            else:
                texture_height = texture_size * height / proj_height
                wall_column = self.textures[texture].subsurface(
                    offset * (texture_size - scale), texture_size // 2 - texture_height // 2,
                    scale, texture_height
                )
                wall_column = pg.transform.scale(wall_column, (scale, height))
                wall_pos = (ray * scale, 0)
            self.objects_to_render.append((depth, wall_column, wall_pos))
    def ray_cast(self):
        self.ray_casting_result = []
        ox, oy = self.game.player.pos()
        oxm, oym = self.game.player.map_pos()
        texture_hor, texture_vert = 1, 1
        ray_angle = self.game.player.angle - fov / 2 + 0.0001
        for ray in range(nrays):
            sa = math.sin(ray_angle)
            ca = math.cos(ray_angle)
            y_hor, dy = (oym + 1, 1) if sa > 0 else (oym - 1e-6, -1)
            depth_hor = (y_hor - oy) / sa
            x_hor = ox + depth_hor * ca
            ddepth = dy / sa
            dx = ddepth * ca
            for i in range(max_depth):
                tile_hor = (int(x_hor), int(y_hor))
                if tile_hor in self.game.map.world_map:
                    texture_hor = self.game.map.world_map[tile_hor]
                    break
                x_hor += dx
                y_hor += dy
                depth_hor += ddepth
            x_vert, dx = (oxm + 1, 1) if ca > 0 else (oxm - 1e-6, -1)
            depth_vert = (x_vert - ox) / ca
            y_vert = oy + depth_vert * sa
            ddepth = dx / ca
            dy = ddepth * sa
            for i in range(max_depth):
                tile_vert = (int(x_vert), int(y_vert))
                if tile_vert in self.game.map.world_map:
                    texture_vert = self.game.map.world_map[tile_vert]
                    break
                x_vert += dx
                y_vert += dy
                depth_vert += ddepth
            if depth_vert < depth_hor:
                depth, texture = depth_vert, texture_vert
                y_vert %= 1
                offset = y_vert if ca > 0 else (1 - y_vert)
            else:
                depth, texture = depth_hor, texture_hor
                x_hor %= 1
                offset = (1 - x_hor) if sa > 0 else x_hor
            depth *= math.cos(self.game.player.angle - ray_angle)
            proj_height = screen_dist / (depth + 0.0001)
            self.ray_casting_result.append((depth, proj_height, texture, offset))
            #color_fix = (1 + depth ** 2 * 0.02)
            #color = [200 / color_fix, 200 / color_fix, 50 / color_fix]
            #pg.draw.rect(self.game.screen, color,
            #             (ray * scale, height // 2 - proj_height // 2, scale, proj_height))
            #pg.draw.line(self.game.screen, "blue", (ox * 75, oy * 75),
            #             (ox * 75 + depth * 75 * ca, oy * 75 + depth * 75 * sa), 3)
            ray_angle += dangle
    def update(self):
        self.ray_cast()
        self.get_objects_to_render()