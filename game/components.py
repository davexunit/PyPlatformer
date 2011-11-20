import pyglet
import cocos
import weakref
import math

import debug
import game
from actor.component import Component

class SpriteComponent(Component):
    component_type = 'sprite'
    def __init__(self, sprite=None):
        super(SpriteComponent, self).__init__()
        self.sprite = sprite

    def on_refresh(self):
        self.physics = self.owner.require('physics')
        self.physics.push_handlers(self)

    def on_move(self, x, y, rel_x, rel_y):
        self.sprite.position = (int(x), int(y))

    def on_rotate(self, angle):
        # Convert that shit to degrees because chipmunk uses radians
        self.sprite.rotation = math.degrees(angle)

class AnimComponent(SpriteComponent):
    '''Graphics component that displays an animated sprite.
    '''
    def __init__(self, anims):
        super(AnimComponent, self).__init__(cocos.sprite.Sprite(anims['stand_south']))
        # Offset the sprite from the actor's hitbox
        self.anims = anims
        self.walking = False
        self.direction = 'south'

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

class PhysicsComponent(Component):
    component_type = 'physics'

    def __init__(self, body, objs):
        super(PhysicsComponent, self).__init__()
        self.body = body
        self.objs = objs
        self.old_x = 0
        self.old_y = 0
        self.old_angle = 0

    def update(self, dt):
        x, y = self.body.position

        if self.old_x != x or self.old_y != y:
            self.dispatch_event('on_move', x, y, 0, 0)

        self.old_x = x
        self.old_y = y

        if self.old_angle != self.body.angle:
            self.dispatch_event('on_rotate', self.body.angle)

        self.old_angle = self.body.angle

PhysicsComponent.register_event_type('on_move')
PhysicsComponent.register_event_type('on_rotate')

class CharacterPhysicsComponent(PhysicsComponent):
    '''A physics component for all controllable (via AI or human input) game
    actors.
    '''
    DIR_LEFT = 0
    DIR_RIGHT = 1

    def __init__(self, body, objs):
        super(CharacterPhysicsComponent, self).__init__(body, objs)
        self.movement_obj = None
        self.move_flags = [False, False]
        self.speed = 250
        self.jump_force = 4000

    def move(self, direction):
        self.move_flags[direction] = True
        self.update_forces()

    def stop_move(self, direction):
        self.move_flags[direction] = False
        self.update_forces()

    def jump(self):
        self.body.apply_impulse((0, self.jump_force))

    def update_forces(self):
        fx = (self.move_flags[self.DIR_RIGHT] - self.move_flags[self.DIR_LEFT]) * self.speed
        #self.body.reset_forces()
        self.movement_obj.surface_velocity = (fx, 0)
        self.dispatch_event('on_direction_changed', fx, 0)
CharacterPhysicsComponent.register_event_type('on_direction_changed')

class InputComponent(Component):
    component_type = 'input'

class PlayerInputComponent(InputComponent):
    '''Allows an actor to be controlled by keyboard/mouse.
    Input events must be injected from other code.
    '''
    DIR_LEFT = 0
    DIR_RIGHT = 1

    def __init__(self):
        super(PlayerInputComponent, self).__init__()

    def on_refresh(self):
        self.physics = self.owner.require('physics', CharacterPhysicsComponent)

    def on_key_press(self, key, modifiers):
        if key == game.game.config.get_keycode('move_up'):
            self.physics.jump()
        if key == game.game.config.get_keycode('move_left'):
            self.physics.move(CharacterPhysicsComponent.DIR_LEFT)
        if key == game.game.config.get_keycode('move_right'):
            self.physics.move(CharacterPhysicsComponent.DIR_RIGHT)

    def on_key_release(self, key, modifiers):
        if key == game.game.config.get_keycode('move_left'):
            self.physics.stop_move(CharacterPhysicsComponent.DIR_LEFT)
        if key == game.game.config.get_keycode('move_right'):
            self.physics.stop_move(CharacterPhysicsComponent.DIR_RIGHT)

