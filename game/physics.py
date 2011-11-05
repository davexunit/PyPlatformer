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
    polygon.friction = .75
    return polygon

@tiled.tiled.register_element_factory('physics')
def load_physics(element):
    physics = Physics()

    for p in element.findall('polygon'):
        vertices = []
        for v in p.findall('vertex'):
            vertices.append((int(v.get('x')), int(v.get('y'))))
        physics.space.add_static(make_static_polygon(vertices))

    return physics

