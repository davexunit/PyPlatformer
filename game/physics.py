try:
    from xml.etree import ElementTree
except ImportError:
    import elementtree.ElementTree as ElementTree

import pymunk

import debug
import tiled.tiled

COLLTYPE_STATIC = 0
COLLTYPE_CHARACTER = 1
COLLTYPE_OBJECT = 2

LAYER_PLAYER = 1
LAYER_ENEMY = 2
LAYER_ITEM = 4
LAYER_PLAYEROBJECT = 8
LAYER_ENEMYOBJECT = 16
LAYER_PLAYERBULLET = 32
LAYER_ENEMYBULLET = 64 
LAYER_OBJECTPLAYERBULLET = 128
LAYER_OBJECTENEMYBULLET = 256

class Physics(object):
    def __init__(self):
        debug.msg('Initializing physics')
        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0.0, -900.0)
        self.update_physics = True

        # Register a bunch of collision callbacks
        self.space.add_collision_handler(COLLTYPE_STATIC, COLLTYPE_CHARACTER,
                self.on_character_jump_land, None, None, None)
        self.space.add_collision_handler(COLLTYPE_OBJECT, COLLTYPE_CHARACTER,
                self.on_character_jump_land, None, None, None)

    def update(self, dt):
        if self.update_physics:
            self.space.step(1.0/60.0)
    
    def on_actor_add(self, actor):
        if actor.has_component('physics'):
            physics = actor.get_component('physics')
            self.space.add(physics.body, *physics.objs)
    
    def on_actor_remove(self, actor):
        if actor.has_component('physics'):
            physics = actor.get_component('physics')
            self.space.remove(physics.body, *physics.objs)

    def on_character_jump_land(self, space, arbiter):
        '''Handles characters that jump and land on static geometry.
        '''
        debug.msg("%s, %s" % (arbiter.contacts[0].normal, len(arbiter.contacts)))

        #if arbiter.contacts[0].normal.dot(arbiter.contacts[1].normal) > 0:
        actor = arbiter.shapes[1].actor()
        physics = actor.get_component('physics')
        physics.on_jump_land()
        return True

def make_static_polygon(vertices):
    body = pymunk.Body(pymunk.inf, pymunk.inf)
    polygon = pymunk.Poly(body, vertices)
    polygon.collision_type = COLLTYPE_STATIC
    polygon.friction = .95
    return polygon

def from_xml(filename):
    # Open xml file
    tree = ElementTree.parse(filename)
    root = tree.getroot()

    # Root level tag is expected to be <geometry> so raise an exception if it's not
    if root.tag != 'physics':
        raise Exception('%s root level tag is %s rather than <physics>' % (filename, root.tag))

    physics = Physics()

    for p in root.findall('polygon'):
        vertices = []
        for v in p.findall('vertex'):
            vertices.append((int(v.get('x')), int(v.get('y'))))
        physics.space.add_static(make_static_polygon(vertices))

    return physics

