import pyglet
import cocos
import pymunk

import debug
import util.resource

class GameScene(cocos.scene.Scene):
    def __init__(self):
        debug.msg('Initializing game scene')
        super(GameScene, self).__init__()

        self.scroller = cocos.layer.ScrollingManager()

        self.init_physics()

    def on_enter(self):
        super(GameScene, self).on_enter()
        self.load_map()

    def load_map(self):
        debug.msg('Loading map')

        # Test garbage
        background = cocos.layer.ScrollableLayer()
        background.add(cocos.sprite.Sprite('backgrounds/background.png',
            anchor=(0,0)))
        background.px_width = 1024
        background.px_height = 768
        self.scroller.add(background)
        self.add(self.scroller)

    def init_physics(self):
        '''Initialize Chipmunk physics space and default settings.
        '''
        debug.msg('Initializing physics')

        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0.0, -900.0)
        self.update_physics = True

