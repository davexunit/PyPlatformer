import pyglet
import cocos
import weakref

import debug
import game
from actor.component import Component

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
        self.move = {'up': False, 'down': False, 'left': False, 'right': False}

    def on_refresh(self):
        self.require('physics')

    def on_key_press(self, key, modifiers):
        if key == game.game.config.get_keycode('move_up'):
            self.dispatch_event('on_move_start', self.MOVE_UP)

    def on_key_release(self, key, modifiers):
        if key == game.config.get_keycode('move_up'):
            self.dispatch_event('on_move_stop', self.MOVE_UP)

    def update(self, dt):
        #physics = self.owner.get_component('physics')
        #fy = (self.move['up'] - self.move['down']) * 9000
        #physics.body.reset_forces()
        physics.body.apply_force((0, fy))

PlayerInputComponent.register_event_type('on_move_start')
PlayerInputComponent.register_event_type('on_move_stop')

