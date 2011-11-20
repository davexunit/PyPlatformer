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

class ActorException(Exception):
    pass

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
        self.components = {}

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
            raise ActorException('Actor \'%s\' already has a parent' %
                    (self.name,))
        # Weakrefs keep away evil circular references
        self._parent_map = weakref.ref(new_parent_map)

    def update(self, dt):
        for component in self.components.values():
            component.update(dt)
    
    def add_component(self, component):
        '''Adds a component to the component dictionary. A
        ActorDuplicateComponent exception will be raised if a component of the
        same type already exitsts.
        '''
        t = component.component_type

        if t in self.components:
            raise ActorException('Cannot add duplicate component of \
                    type %s to actor %s' % (t, self.name))

        # Add new component
        self.components[t] = component
        component.attach(self)

    def remove_component(self, component_type):
        '''Detaches component of the given type and calls the necessary
        clean-up routines. A KeyError will be raised if a component of given
        type is not attached.
        '''
        del self.components[component_type]
        component.detach()

    def clear_components(self):
        for component in self.components.values():
            component.detach()

    def has_component(self, component_type, component_class=None):
        '''Checks for the existence of given component of given component_type
        and optionally by class instance.
        '''
        exists = component_type in self.components

        if exists and component_class != None:
            return isinstance(self.components[component_type], component_class)
        
        return exists

    def get_component(self, component_type):
        '''Retrieves reference to the component of the given type. A KeyError
        will be raised if there is no component of that type.
        '''
        return self.components[component_type]
    
    def require(self, component_type, component_class=None):
        '''Enforces inter-component dependencies. Returns instance to component
        if it exists. An ActorException is raised if a component is not found.
        '''
        if not self.has_component(component_type, component_class):
            error_message = 'Actor %s is missing dependency: %s' % (self.name, component_type)
            if component_class != None:
                error_message += ' of type %s' % component_clas.__name__

            raise ActorException(error_message)

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
Actor.register_event_type('on_actor_enter')
Actor.register_event_type('on_actor_exit')

