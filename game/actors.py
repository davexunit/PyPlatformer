import weakref
import pyglet
import cocos
import pymunk

import util.anim
import util.resource
from actor.actor import Actor
from components import *

def make_rect(width, height, friction, mass=pymunk.inf, moment=pymunk.inf):
    w = width / 2.0
    h = height / 2.0
    vertices = [(w, h), (-w, h), (-w, -h), (w, -h)]
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

        width = 64 
        height = 96 
        body, rect = make_rect(width, height, 0.75, mass=10)
        physics = CharacterPhysicsComponent(body, (rect,))
        physics.movement_obj = rect
        self.add_component(physics)

        self.add_component(PlayerInputComponent())

        self.refresh_components()

class Block(Actor):
    def __init__(self):
        super(Block, self).__init__()

        self.add_component(SpriteComponent(cocos.sprite.Sprite('images/block_grass.png')))
        width = 38
        height = 66
        body, rect = make_rect(width, height, 0.5, mass=10.0, moment=-1)
        self.add_component(PhysicsComponent(body, (rect,)))
        self.refresh_components()

