
"""
SHIP GYM CONFIGURATION PARAMETERS PRELOADED WITH DEFAULT VALUES.

Import these and change the values in code
"""

class LidarConfig(object):
    N_BEAMS = 10
    DISTANCE = 100
    ANGULAR_SPREAD = 180 # In degrees, front facing


class EnvConfig(object):
    HISTORY_SIZE = 2
    MAX_STEPS = 1000
    LIDAR_CONFIG = LidarConfig


class GameConfig(object):
    FPS = 1000
    SPEED = 10 # Speed multiplier
    BOUNDS = (600, 600)
