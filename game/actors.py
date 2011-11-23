import weakref
import pyglet
import cocos
import pymunk

import util.anim
import util.resource
from actor.actor import Actor
from components import *
from physics import *

def make_rect(body, width, height, x=0, y=0, friction=0.5):
    w = width / 2.0
    h = height / 2.0
    vertices = [(x + w, y + h), (x - w, y + h), (x - w, y - h), (x + w, y - h)]
    rect = pymunk.Poly(body, vertices)
    rect.friction = friction
    return rect

class Player(Actor):
    def __init__(self):
        super(Player, self).__init__()
        # Load animations
        anims = util.anim.load_animset(util.resource.path('anims/test.xml'))

        self.add_component(AnimComponent(anims))

        width = 48 
        height = 64
        body = pymunk.Body(10, pymunk.inf)
        rect = make_rect(body, width, height, y=-13, friction=0.9)
        rect.layers = LAYER_ENEMY | LAYER_ITEM | LAYER_PLAYEROBJECT | LAYER_ENEMYBULLET
        rect.collision_type = COLLTYPE_CHARACTER
        physics = CharacterPhysicsComponent(body, (rect,))
        physics.movement_obj = rect
        self.add_component(physics)

        self.add_component(PlayerInputComponent())

        self.refresh_components()

class Block(Actor):
    def __init__(self):
        super(Block, self).__init__()

        self.add_component(SpriteComponent(cocos.sprite.Sprite('images/block_grass.png')))
        width = 44
        height = 44
        body = pymunk.Body(10, pymunk.moment_for_box(10, width, height))
        rect = make_rect(body, width, height, friction=0.5)
        rect.layers = LAYER_PLAYEROBJECT | LAYER_ENEMYOBJECT | LAYER_OBJECTPLAYERBULLET | LAYER_OBJECTENEMYBULLET
        rect.collision_type = COLLTYPE_OBJECT
        self.add_component(PhysicsComponent(body, (rect,)))
        self.refresh_components()

class MovingPlatform(Actor):
    def __init__(self):
        super(MovingPlatform, self).__init__()

        self.add_component(SpriteComponent(cocos.sprite.Sprite('images/platform.png')))

        width = 128
        height = 32 
        body = pymunk.Body()
        rect = make_rect(body, width, height, friction=1.0)
        rect.collision_type = COLLTYPE_STATIC
        
        physics = PhysicsComponent(body, (rect,))
        self.add_component(physics)
        self.refresh_components()

