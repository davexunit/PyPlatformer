import pyglet
import cocos
import pymunk

import debug
import tiled.tiled
import util.resource
import actorlayer
import actors

class GameScene(cocos.scene.Scene):
    def __init__(self):
        debug.msg('Initializing game scene')
        super(GameScene, self).__init__()

        # All map layers are kept in the scrolling manager for obvious reasons
        self.scroller = cocos.layer.ScrollingManager()
        self.add(self.scroller)

        self.init_physics()

    def on_enter(self):
        super(GameScene, self).on_enter()
        self.load_map()

    def load_map(self):
        debug.msg('Loading map')
        tile_layers, object_layers =\
            tiled.tiled.load_map(util.resource.path('maps/test.tmx'))
        self.scroller.add(tile_layers['top'], z=1)

        debug.msg('Creating actor layer')
        self.actors = actorlayer.ActorLayer()
        self.scroller.add(self.actors, z=1)

        self.test_actor()

    def test_actor(self):
        player = actors.Player()
        player.position = (100, 100)
        self.actors.add_actor(player)

    def init_physics(self):
        '''Initialize Chipmunk physics space and default settings.
        '''
        debug.msg('Initializing physics')

        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0.0, -900.0)
        self.update_physics = True

