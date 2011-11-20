try:
    from xml.etree import ElementTree
except ImportError:
    import elementtree.ElementTree as ElementTree

import pymunk

import debug
import tiled.tiled

class Physics(object):
    def __init__(self):
        debug.msg('Initializing physics')
        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0.0, -900.0)
        self.update_physics = True

    def update(self, dt):
        if self.update_physics:
            self.space.step(1.0/60.0)

def make_static_polygon(vertices):
    body = pymunk.Body(pymunk.inf, pymunk.inf)
    polygon = pymunk.Poly(body, vertices)
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

