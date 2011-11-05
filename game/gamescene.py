import pyglet
import cocos
import pymunk

import debug
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

        # Test garbage
        background = cocos.layer.ScrollableLayer()
        background.add(cocos.sprite.Sprite('backgrounds/background.png',
            anchor=(0,0)))
        background.px_width = 1024
        background.px_height = 768
        self.scroller.add(background)

        debug.msg('Creating actor layer')
        self.actors = actorlayer.ActorLayer()
        self.add(self.actors, z=1)

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

