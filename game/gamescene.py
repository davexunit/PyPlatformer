import pyglet
import cocos

import debug
import util.resource

class GameScene(cocos.scene.Scene):
    def __init__(self):
        debug.msg('Creating game scene')
        super(GameScene, self).__init__()
        self.add(cocos.layer.ColorLayer(128, 128, 128, 255))

