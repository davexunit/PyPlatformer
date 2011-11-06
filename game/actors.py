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
        self.size = (24, 24)

        # Load animations
        anims = util.anim.load_animset(util.resource.path('anims/king.xml'))

        self.add_component(SpriteComponent(anims, offset=(-4,0)))

        body = pymunk.Body(10, pymunk.inf)
        body.apply_impulse((1000, 9000))
        rect = make_rect(body, self.width, self.height, 0.2)
        self.add_component(PhysicsComponent(body, (rect,)))

        self.add_component(PlayerInputComponent())

        self.refresh_components()

