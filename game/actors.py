import weakref
import pyglet
import cocos

import util.anim
import util.resource
from actor.actor import Actor
from components import *

class Player(Actor):
    def __init__(self):
        super(Player, self).__init__()
        self.size = (24, 24)

        # Load animations
        anims = util.anim.load_animset(util.resource.path('anims/king.xml'))

        #self.add_component(HumanInputComponent())
        self.add_component(SpriteComponent(anims, offset=(-4,0)))
        #self.add_component(PhysicsComponent(200))
        #self.add_component(PlayerSoundComponent())
        self.refresh_components()

