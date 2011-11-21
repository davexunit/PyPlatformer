import weakref
import pyglet
import cocos
import pymunk

import util.anim
import util.resource
from actor.actor import Actor
from components import *
from physics import *

def make_rect(width, height, x=0, y=0, friction=0.5, mass=pymunk.inf, moment=pymunk.inf):
    w = width / 2.0
    h = height / 2.0
    vertices = [(x + w, y + h), (x - w, y + h), (x - w, y - h), (x + w, y - h)]
    if moment == -1:
        moment = pymunk.moment_for_poly(mass, vertices, (0,0))
    body = pymunk.Body(mass, moment)
    rect = pymunk.Poly(body, vertices)
    rect.friction = friction
    return body, rect

class Player(Actor):
    def __init__(self):
        super(Player, self).__init__()
        # Load animations
        anims = util.anim.load_animset(util.resource.path('anims/test.xml'))

        self.add_component(AnimComponent(anims))

        width = 48 
        height = 64
        body, rect = make_rect(width, height, y=-16, friction=0.75, mass=10)
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
        width = 30
        height = 50
        body, rect = make_rect(width, height, friction=0.5, mass=10.0, moment=-1)
        rect.layers = LAYER_PLAYEROBJECT | LAYER_ENEMYOBJECT | LAYER_OBJECTPLAYERBULLET | LAYER_OBJECTENEMYBULLET
        rect.collision_type = COLLTYPE_OBJECT
        self.add_component(PhysicsComponent(body, (rect,)))
        self.refresh_components()

