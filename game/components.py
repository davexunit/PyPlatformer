import pyglet
import cocos
import weakref

import debug
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

