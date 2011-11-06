import pyglet
import cocos
import weakref

import debug
import game
from actor.component import Component

class SpriteComponent(Component):
    component_type = 'graphics'

    def __init__(self, sprite=None):
        super(SpriteComponent, self).__init__()
        self.sprite = sprite

    def on_refresh(self):
        self.owner.push_handlers(self)

    def on_move(self, x, y, rel_x, rel_y):
        self.sprite.position = (int(x), int(y))

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

    def on_refresh(self):
        self.owner.push_handlers(self)

    def on_move(self, x, y, rel_x, rel_y):
        self.body.position = (x, y)

    def update(self, dt):
        self.owner.position = self.body.position

class PlayerInputComponent(Component):
    '''Allows an actor to be controlled by keyboard/mouse.
    Input events must be injected from other code.
    '''
    component_type = 'input'

    def __init__(self):
        super(PlayerInputComponent, self).__init__()

    def on_refresh(self):
        self.require('movement')

    def on_key_press(self, key, modifiers):
        movement = self.owner.get_component('movement')

        if key == game.game.config.get_keycode('move_up'):
            movement.jump()
        if key == game.game.config.get_keycode('move_left'):
            movement.move(MovementComponent.DIR_LEFT)
        if key == game.game.config.get_keycode('move_right'):
            movement.move(MovementComponent.DIR_RIGHT)

    def on_key_release(self, key, modifiers):
        movement = self.owner.get_component('movement')

        if key == game.game.config.get_keycode('move_left'):
            movement.stop_move(MovementComponent.DIR_LEFT)
        if key == game.game.config.get_keycode('move_right'):
            movement.stop_move(MovementComponent.DIR_RIGHT)

class MovementComponent(Component):
    component_type = 'movement'

    DIR_LEFT = 0
    DIR_RIGHT = 1

    def __init__(self):
        super(MovementComponent, self).__init__()
        self.move_flags = [False, False]
        self.speed = 5000
        self.jump_force = 4000

    def on_refresh(self):
        self.require('physics')

    def move(self, direction):
        self.move_flags[direction] = True
        self.update_forces()

    def stop_move(self, direction):
        self.move_flags[direction] = False
        self.update_forces()

    def jump(self):
        physics = self.owner.get_component('physics')
        physics.body.apply_impulse((0, self.jump_force))

    def update_forces(self):
        physics = self.owner.get_component('physics')
        fx = (self.move_flags[self.DIR_RIGHT] - self.move_flags[self.DIR_LEFT]) * self.speed
        physics.body.reset_forces()
        physics.body.apply_force((fx, 0))

