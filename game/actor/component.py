import pyglet
import weakref

class ComponentException(Exception):
    pass

class Component(pyglet.event.EventDispatcher):
    '''Components provide functionality to Actors. Components avoid the deep
    hierarchy inheritance problem with game objects that share functionality.
    Components should do one thing only and do it well. Components talk to each
    other by using the pyglet event framework. Alternatively, components can
    obtain direct references to other components if needed.
    '''
    # Class level variable containing a string with the Component's type
    # string. Child classes must set this variable.
    component_type = None

    def __init__(self):
        self._owner = None

    @property
    def owner(self):
        if self._owner == None:
            return None

        return self._owner()
    
    @owner.setter
    def owner(self, new_owner):
        if new_owner == None:
            self._owner = None
            return

        if self._owner != None:
            raise Exception("Component of type %s already has an owner" %
                    (self.component_type,))

        self._owner = weakref.ref(new_owner)

    def attach(self, actor):
        '''Sets the owner of this component to the given actor. An exception
        will be raised if this component is already owned by someone else.
        '''
        if self.owner != None:
            raise Exception('Component of type %s already has an owner' %
                    self.type)
        self.owner = actor

    def detach(self):
        '''This method is to be called only by the Actor class. If you are
        to call this method manually, you must also manually remove the
        component from the Actor's dictionary. In other words, don't do
        this. Use Actor.remove_component instead.
        '''
        self.owner = None
        self.on_detach()

    def require(self, component_type):
        '''Raises an exception if a component of the given type is not
        attached to the parent. Used to verify component dependencies.
        '''
        if not self.owner.has_component(component_type):
            raise ComponentException('Missing dependency for %s: %s' %
                    (self.component_type, component_type))

    def update(self, dt):
        '''Override this method to do time-based updates.
        '''
        pass

    def on_refresh(self):
        '''This method is called by the Actor class when the component
        'wiring' needs to be refreshed. Use this method to perform all event
        registering and direct reference storing to other components.
        '''
        pass

    def on_detach(self):
        '''When detached (removed by the owner), a well-behaved component will
        unregister all events that it was previously registered to and do
        whatever else it needs to do.
        '''
        pass

