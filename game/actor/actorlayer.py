'''Provides a basic cocos2d scrollable layer for storing actors. This module
does not know about the existence of any component types. Therefore, users
should create a subclass and override the add_actor and remove_actor methods to
do component checking.
For example, a user may want to check for a 'graphics' component and add/remove
a sprite to/from a batch node.
'''

import pyglet
import cocos

class ActorLayer(cocos.layer.ScrollableLayer, pyglet.event.EventDispatcher):
    def __init__(self):
        super(ActorLayer, self).__init__()
        self.actors = {}

    def add_actor(self, actor):
        if actor.name in self.actors:
            raise Exception('Duplicate actor name: %s' % actor.name)

        self.actors[actor.name] = actor
        actor.on_enter()
        self.dispatch_event('on_actor_add', actor)
    
    def remove_actor(self, actor):
        del self.actors[actor.name]
        actor.on_exit()
        self.dispatch_event('on_actor_remove', actor)

    def get_actor(self, name):
        return self.actors[name]

    def get_actors(self):
        return self.actors.values()

    def get_in_region(self, rect):
        '''Returns a list of all actors whose bounding boxes intersect with the
        given rectangle.
        '''
        actors = weakref.WeakSet()
        for a in self.actors.values():
            actor_rect = cocos.rect.Rect(a.x, a.y, a.width, a.height)
            if actor_rect.intersects(rect):
                actors.add(a)
        return actors

    def _step(self, dt):
        for actor in self.actors.values():
            actor.update(dt)

ActorLayer.register_event_type('on_actor_add')
ActorLayer.register_event_type('on_actor_remove')

