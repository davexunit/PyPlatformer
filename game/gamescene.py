import pyglet
import cocos
import pymunk

import debug
import tiled.tiled
import util.resource
import actorlayer
import actors
import physics

class GameScene(cocos.scene.Scene, pyglet.event.EventDispatcher):
    def __init__(self):
        debug.msg('Initializing game scene')
        super(GameScene, self).__init__()

        # All map layers are kept in the scrolling manager for obvious reasons
        self.scroller = cocos.layer.ScrollingManager()
        self.add(self.scroller)

    def on_enter(self):
        super(GameScene, self).on_enter()
        self.load_map()

    def load_map(self):
        debug.msg('Loading map')
        self.map_filename = 'maps/test.tmx'
        self.tiledmap = tiled.tiled.load_map(util.resource.path(self.map_filename))
        self.scroller.add(self.tiledmap.layers['middleground'], z=1)
        self.scroller.add(self.tiledmap.layers['background'], z=0)

        debug.msg('Loading level geometry')
        physics_file = util.resource.path(self.tiledmap.properties['physics'])
        self.physics = physics.from_xml(physics_file)

        debug.msg('Creating test actor layer')
        self.actors = actorlayer.ActorLayer()
        self.actors.push_handlers(self)
        self.scroller.add(self.actors, z=1)

        self.test_actor()

        self.dispatch_event('on_map_load')

    def test_actor(self):
        self.player = actors.Player()
        self.player.name = 'Player'
        self.player.get_component('physics').body.position = (100, 100)
        self.actors.add_actor(self.player)

        for x in range(250, 1000, 50):
            block = actors.Block()
            block.name = 'Block %d' % x
            block.get_component('physics').body.position = (x, 600)
            self.actors.add_actor(block)

    def on_actor_add(self, actor):
        if actor.has_component('physics'):
            physics = actor.get_component('physics')
            self.physics.space.add(physics.body, *physics.objs)

    def on_actor_exit(self, actor):
        if actor.has_component('physics'):
            physics = actor.get_component('physics')
            self.physics.space.remove(physics.body, *physics.objs)
    
    def _step(self, dt):
        self.physics.update(dt)


GameScene.register_event_type('on_map_load')

