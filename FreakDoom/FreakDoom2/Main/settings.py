import math
width, height = 1200, 675
fps = 60
player_pos = (2, 5)
player_angle = 0
player_lin_speed = 0.004
player_rot_speed = 0.002
player_size = 80
mouse_sensitivity = 0.0003
mouse_max_speed = 40
mouse_border_left = width // 2 - 100
mouse_border_right = width // 2 + 100
mouse_border_top = height // 2 - 100
mouse_border_bottom = height // 2 + 100
fov = math.pi / 3
nrays = width // 2
dangle = fov / nrays
max_depth = 20
screen_dist = (width // 2) / math.tan(fov / 2)
scale = width // nrays
texture_size = 256