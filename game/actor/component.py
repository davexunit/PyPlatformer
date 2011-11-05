import pyglet
import weakref

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

import cocos
class SpriteComponent(Component):
    '''Graphics component that displays an animated sprite.
    '''
    component_type = 'graphics'

    def __init__(self, anims, offset=(0,0)):
        super(SpriteComponent, self).__init__()
        self.sprite = cocos.sprite.Sprite(anims['stand_south'], anchor=(0,0))
        # Offset the sprite from the actor's hitbox
        self._dx, self._dy = offset
        self.anims = anims
        self.walking = False
        self.direction = 'south'

    def on_refresh(self):
        self.owner.push_handlers(self)
        self.owner.get_component('physics').push_handlers(self)

    def on_move(self, x, y, rel_x, rel_y):
        self.sprite.position = (int(x + self._dx), int(y + self._dy))

    def update_animation(self):
        prefix = 'walk_' if self.walking else 'stand_'
        self.sprite.image = self.anims[prefix + self.direction]

    def on_direction_changed(self, dx, dy):
        if dx == 0 and dy == 0:
            self.walking = False
        else:
            self.walking = True

        if dy > 0:
            self.direction = 'north'
        elif dy < 0:
            self.direction = 'south'
        elif dx > 0:
            self.direction = 'east'
        elif dx < 0:
            self.direction = 'west'
        self.update_animation()

import math
from ..game import game
MOVE_NONE = 0
MOVE_NORTH = 1
MOVE_SOUTH = 2
MOVE_EAST = 4
MOVE_WEST = 8
class HumanInputComponent(Component):
    '''Input component that takes input from the keyboard.
    '''
    component_type = 'input'

    def __init__(self):
        super(HumanInputComponent, self).__init__()
        self.move = MOVE_NONE

    def on_refresh(self):
        self.physics = self.owner.get_component('physics')

    def on_key_press(self, key, modifiers):
        if key == game.config.get_keycode('move_up'):
            self.move |= MOVE_NORTH
        elif key == game.config.get_keycode('move_down'):
            self.move |= MOVE_SOUTH
        elif key == game.config.get_keycode('move_right'):
            self.move |= MOVE_EAST
        elif key == game.config.get_keycode('move_left'):
            self.move |= MOVE_WEST
        self._update_physics()

    def on_key_release(self, key, modifiers):
        if key == game.config.get_keycode('move_up'):
            self.move &= ~MOVE_NORTH
        elif key == game.config.get_keycode('move_down'):
            self.move &= ~MOVE_SOUTH
        elif key == game.config.get_keycode('move_right'):
            self.move &= ~MOVE_EAST
        elif key == game.config.get_keycode('move_left'):
            self.move &= ~MOVE_WEST
        self._update_physics()

    def stop_moving(self):
        self.move = MOVE_NONE
        self.physics.direction = (0.0, 0.0)

    def is_moving(self, dir):
        if dir == MOVE_NONE:
            return self.move == 0

        return (self.move & dir) / dir

    def _update_physics(self):
        self.physics.dy = float(self.is_moving(MOVE_NORTH) - self.is_moving(MOVE_SOUTH))
        self.physics.dx = float(self.is_moving(MOVE_EAST) - self.is_moving(MOVE_WEST))

class DumbAI(Component):
    component_type = 'input'

    def on_refresh(self):
        self.physics = self.owner.get_component('physics')
        self.physics.push_handlers(self)
        self.physics.direction = (1, 1)

    def on_collision(self, collide_x, collide_y):
        if collide_x:
            self.physics.dx *= -1
        if collide_y:
            self.physics.dy *= -1

import pyglet
class PhysicsComponent(Component):
    component_type = 'physics'

    def __init__(self, speed):
        super(PhysicsComponent, self).__init__()
        self._dx, self._dy = 0, 0
        self.speed = speed
        self.collidable = True

    @property
    def dx(self):
        return self._dx

    @dx.setter
    def dx(self, newdx):
        self._dx = newdx
        self.dispatch_event('on_direction_changed', self._dx, self._dy)

    @property
    def dy(self):
        return self._dy

    @dy.setter
    def dy(self, newdy):
        self._dy = newdy
        self.dispatch_event('on_direction_changed', self._dx, self._dy)

    @property
    def direction(self):
        return (self._dx, self._dy)

    @direction.setter
    def direction(self, dir):
        self._dx, self._dy = dir
        self.dispatch_event('on_direction_changed', self._dx, self._dy)

    def start(self):
        self.stopped = False

    def update(self, dt):
        # Normalize direction vector
        mag = math.sqrt((self._dx * self._dx) + (self._dy * self._dy))
        if mag != 0:
            ndx, ndy = self._dx / mag, self._dy / mag
        else:
            ndx, ndy = 0, 0

        # Calculate movement
        move_x = self._dx * self.speed * dt
        move_y = self._dy * self.speed * dt

        # Check collision on X axis
        rect = self.owner.get_rect()
        rect.x += move_x
        collide_x = self.check_collision(rect)

        # Check collision on Y axis
        rect = self.owner.get_rect()
        rect.y += move_y
        collide_y = self.check_collision(rect)

        # Move actor
        if not collide_x:
            self.owner.x += move_x

        if not collide_y:
            self.owner.y += move_y

        # Dispatch collision event if collision occurred
        if collide_x or collide_y:
            self.dispatch_event('on_collision', collide_x, collide_y)

    def check_collision(self, rect):
        # Ignore collision test if collidable flag is not set
        if not self.collidable:
            return False

        if self.owner.parent_map == None:
            return false

        # Check map collision
        for cell in self.owner.parent_map.collision.get_in_region(*(rect.bottomleft + rect.topright)):
            if cell.tile != None:
                return True

        return False

# Events for PhysicsComponent
PhysicsComponent.register_event_type('on_collision')
PhysicsComponent.register_event_type('on_direction_changed')

class PlayerSoundComponent(Component):
    component_type = 'sound'

    def __init__(self):
        super(PlayerSoundComponent, self).__init__()
        self.collision = pyglet.resource.media('sounds/snare.wav', streaming=False)
        self.play_collision = True

    def on_refresh(self):
        self.owner.get_component('physics').push_handlers(self)

    def on_collision(self, collide_x, collide_y):
        if self.play_collision:
            self.collision.play()
            self.play_collision = False
            def activate_sound(dt):
                self.play_collision = True
            pyglet.clock.schedule_once(activate_sound, .5)

class DialogComponent(Component):
    '''TODO: Make this a real dialog system. For now it only stores on text
    field to be displayed when the actor is activated.'''
    component_type = 'dialog'

    def __init__(self, text):
        super(DialogComponent, self).__init__()
        self.text = text

