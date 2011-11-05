'''Actors in this context are defined as game objects that possess variable
functionality. Actors have few properties on their own and functionality is
acquired by adding 'components'.

Components encapsulate a specific property of a game object. For example,
Sprite, Physics, and AI could be components.

The component-based game object model avoids the issues involved with deep
inheritance hierarchies, such as code duplication. Components allow
functionality to be defined cleanly, as each class will accomplish one task
only, following the UNIX philosophy of having several small programs work
together to complete a task.
'''

import weakref
import pyglet
import cocos

class Actor(pyglet.event.EventDispatcher):
    '''Actors represent objects in a game that have variable functionality. This class
    is simply a container of components. Mix and match components to create the
    Actors that you need.
    '''
    def __init__(self):
        super(Actor, self).__init__()
        self.name = "Anonymous"
        self.group = None
        self._parent = None
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
    def parent(self):
        if self._parent == None:
            return None

        return self._parent_map()

    @parent.setter
    def parent(self, new_parent):
        if new_parent == None:
            self._parent = None
            return

        if self._parent != None:
            raise Exception('Actor \'%s\' already has a parent' %
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
        if self.parent == None:
            return

        # Get all actors intersecting with bounding box
        actors = self.parent.get_in_region(self.get_rect())
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
        pass

# Event handlers for Actor
Actor.register_event_type('on_move')
Actor.register_event_type('on_actor_enter')
Actor.register_event_type('on_actor_exit')

