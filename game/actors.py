import weakref
import pyglet
import cocos
import pymunk

import util.anim
import util.resource
from actor.actor import Actor
from components import *

def make_rect(body, width, height, friction, mass=pymunk.inf, moment=pymunk.inf):
    w = width / 2.0
    h = height / 2.0
    vertices = [(w, h), (-w, h), (-w, -h), (w, -h)]
    rect = pymunk.Poly(body, vertices)
    rect.friction = friction
    return rect

class Player(Actor):
    def __init__(self):
        super(Player, self).__init__()
        # Load animations
        anims = util.anim.load_animset(util.resource.path('anims/king.xml'))

        self.add_component(AnimComponent(anims))

        width = 38
        height = 66
        body = pymunk.Body(10, pymunk.inf)
        rect = make_rect(body,width, height, 0.5)
        self.add_component(PhysicsComponent(body, (rect,)))

        self.add_component(PlayerInputComponent())
        self.add_component(MovementComponent())

        self.refresh_components()

class Block(Actor):
    def __init__(self):
        super(Block, self).__init__()

        width = 38
        height = 66
        self.add_component(SpriteComponent(cocos.sprite.Sprite('images/block_grass.png')))
        body = pymunk.Body(10, pymunk.inf)
        rect = make_rect(body, width, height, 0.5)
        self.add_component(PhysicsComponent(body, (rect,)))
        self.refresh_components()

