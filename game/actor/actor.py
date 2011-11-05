import weakref
import pyglet
import cocos

class Actor(pyglet.event.EventDispatcher):
    '''Actors represent any object on the map that isn't a tile. This class
    is simply a container of components. Mix and match components to create the
    Actors that you need.
    '''
    def __init__(self):
        super(Actor, self).__init__()
        self.name = "Anonymous"
        self.group = None
        self._parent_map = None
        self._x = 0
        self._y = 0
        self.width = 0
        self.height = 0
        self.components = {}
        self.intersect_actors = weakref.WeakSet()

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, newx):
        dx = newx - self._x
        self._x = newx
        self.dispatch_event('on_move', self._x, self._y, dx, 0)
        self.check_triggers()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, newy):
        dy = newy - self._y
        self._y = newy
        self.dispatch_event('on_move', self._x, self._y, 0, dy)
        self.check_triggers()

    @property
    def position(self):
        return (self._x, self._y)

    @position.setter
    def position(self, position):
        newx, newy = position
        dx, dy = newx - self._x, newy - self._y
        self._x, self._y = newx, newy
        self.dispatch_event('on_move', self._x, self._y, dx, dy)
        self.check_triggers()
        
    @property
    def size(self):
        return (self.width, self.height)

    @size.setter
    def size(self, size):
        self.width, self.height = size
    
    def get_rect(self):
        return cocos.rect.Rect(self._x, self._y, self.width, self.height)

    @property
    def parent_map(self):
        if self._parent_map == None:
            return None

        return self._parent_map()

    @parent_map.setter
    def parent_map(self, new_parent_map):
        if new_parent_map == None:
            self._parent_map = None
            return

        if self._parent_map != None:
            raise Exception("Actor '%s' already has a parent map" %
                    (self.name,))
        # Weakrefs keep away evil circular references
        self._parent_map = weakref.ref(new_parent_map)

    def update(self, dt):
        for component in self.components.values():
            component.update(dt)
    
    def check_triggers(self):
        '''Called when the actor moves. If the calling actor is intersecting
        any other actors then trigger events will be dispatched.
        '''
        if self.parent_map == None:
            return

        # Get all actors intersecting with bounding box
        actors = self.parent_map.actors.get_in_region(self.get_rect())
        # Remove this actor from that list
        actors.remove(self)

        # Dispatch on_actor_enter on newly intersecting actors
        enter_actors = actors.difference(self.intersect_actors)
        for actor in enter_actors:
            self.dispatch_event('on_actor_enter', actor)
            actor.intersect_actors.add(self)
            actor.dispatch_event('on_actor_enter', self)

        # Dispatch on_actor_exit on actors that are no longer intersecting.
        exit_actors = self.intersect_actors.difference(actors)
        for actor in exit_actors:
            self.dispatch_event('on_actor_exit', actor)
            try:
                actor.intersect_actors.remove(self)
            except Exception:
                pass
            actor.dispatch_event('on_actor_exit', self)

        for actor in enter_actors.union(exit_actors):
            actor.check_triggers()
        
        # Set new set 
        self.intersect_actors = actors

    def add_component(self, component):
        '''Adds a component to the component dictionary. If a component of the same type is
        already attached, it will be detached and replaced by the new one.
        '''
        t = component.component_type

        # Run clean-up on previous component of the same type
        if t in self.components:
            self.remove_component(t)

        # Add new component
        self.components[t] = component
        component.attach(self)

    def remove_component(self, component_type):
        '''Detaches component of the given type and calls the necessary
        clean-up routines. A KeyError will be raised if a component of given
        type is not attached.
        '''
        self.components[component_type].detach()

    def clear_components(self):
        for component in self.components.values():
            component.detach()

    def has_component(self, component_type):
        '''Tests if a component of given type is attached.
        '''
        return component_type in self.components

    def get_component(self, component_type):
        '''Retrieves reference to the component of the given type. A KeyError
        will be raised if there is no component of that type.
        '''
        return self.components[component_type]

    def refresh_components(self):
        '''Refreshing the components gives each component the chance to hook
        into the events of other components that belong to the Actor.
        You should call this once during the initial creation of the Actor,
        after all of the components have been added.
        If you add/remove components later, make sure to refresh.
        '''
        for component in self.components.values():
            component.on_refresh()

    def on_enter(self):
        '''Callback function when actor is added to a map.
        '''
        pass
    
    def on_exit(self):
        '''Callback function when actor is removed from a map.
        '''
        #for actor in self.intersect_actors:
            #print "purge " + actor.name
            #actor.intersect_actors.remove(self)
            #actor.dispatch_event('on_actor_exit', self)
        # Purge intersecting actors list
        #self.intersect_actors.clear()

# Event handlers for Actor
Actor.register_event_type('on_move')
Actor.register_event_type('on_actor_enter')
Actor.register_event_type('on_actor_exit')

from component import *
from .. import mapload
class Player(Actor):
    def __init__(self):
        super(Player, self).__init__()
        self.size = (24, 24)

        # Load animations
        anims = mapload.load_animset('anims/king.xml')

        self.add_component(HumanInputComponent())
        self.add_component(SpriteComponent(anims, offset=(-4,0)))
        self.add_component(PhysicsComponent(200))
        self.add_component(PlayerSoundComponent())
        self.refresh_components()

class Derp(Actor):
    def __init__(self, animfile, dialog):
        super(Derp, self).__init__()
        self.size = (24, 24)

        # Load animations
        from .. import mapload
        anims = mapload.load_animset(animfile)

        #self.add_component(DumbAI())
        self.add_component(SpriteComponent(anims, offset=(-4,0)))
        self.add_component(PhysicsComponent(200))
        self.add_component(DialogComponent(dialog))
        self.refresh_components()

@mapload.register_actor_factory('npc')
def load_npc(properties):
    npc = Derp(properties['file'], properties['dialog'])
    return npc

class Sign(Actor):
    def __init__(self, text):
        super(Sign, self).__init__()
        self.add_component(DialogComponent(text))
        self.refresh_components()

@mapload.register_actor_factory('sign')
def load_sign(properties):
    sign = Sign(properties['text'])
    return sign

class Portal(Actor):
    def __init__(self, destination, exit_portal):
        super(Portal, self).__init__()
        self.destination = destination
        self.exit_portal = exit_portal
        self.active = True
        self.refresh_components()

    def on_actor_enter(self, actor):
        if self.active:
            def load_map(dt):
                from .. import map
                from .. import util
                from ..game import game

                # Load new map
                new_scene = mapload.load_map(self.destination)
                new_scene.name = self.destination
                new_scene.focus = actor

                # Get the exit portal
                portal = new_scene.actors.get_actor(self.exit_portal)
                # The active flag is so that when the actor is placed onto the
                # portal it doesn't trigger a map change causing an unbounded
                # loop.
                portal.active = False

                #def old_death(ref):
                #    print "old map died"
                #oldmap = weakref.ref(actor.parent_map, old_death)

                # Remove actor from current map and place on new map
                self.parent_map.actors.remove_actor(actor)
                new_scene.actors.add_actor(actor)
                actor.position = portal.position

                # Add the walkaround state
                walkaround = map.mapscene.WalkaroundState()
                walkaround.input_component = actor.get_component('input')
                new_scene.state_replace(walkaround)

                # Replace map
                cocos.director.director.replace(cocos.scenes.transitions.FadeTransition(new_scene, 1))

                #def do_refcount(dt):
                #    from sys import getrefcount
                #    print oldmap(), getrefcount(oldmap())
                #pyglet.clock.schedule_interval(do_refcount, 1)
                #from sys import getrefcount
                #print "ref count:", getrefcount(oldmap())
                #print "weakref count:", weakref.getweakrefcount(oldmap())
                #def print_ref(dt):
                #    import debug
                #    debug.print_referrers(oldmap())
            # Perform the map loading on the next game loop
            pyglet.clock.schedule_once(load_map, 0)

    def on_actor_exit(self, actor):
        self.active = True

@mapload.register_actor_factory('portal')
def load_portal(properties):
    return Portal(properties['map'], properties['exit'])

from .. import map
class TestScript(Actor):
    def __init__(self):
        super(TestScript, self).__init__()

    def on_actor_enter(self, actor):
        def func():
            self.parent_map.state_push(map.mapscene.DialogState('Testing!'))
        action = cocos.actions.CallFunc(func)#cocos.actions.Blink(5,.1)
        self.parent_map.state_push(map.mapscene.CinematicState(action))
