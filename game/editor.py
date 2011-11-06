'''This module provides a cocos layer that can be added to a GameScene for
interactive editing of collision data.
'''

try:
    from xml.etree import ElementTree
except ImportError:
    import elementtree.ElementTree as ElementTree

import pyglet
from pyglet.gl import *
import cocos
import pymunk

import debug
import util.resource
import physics

class Polygon(cocos.cocosnode.CocosNode):
    def __init__(self, vertices=[]):
        super(Polygon, self).__init__()
        self.vertices = list(vertices)
        self.make_convex()
        self.color = (1.0, 1.0, 1.0, 1.0)

    def add_vertex(self, point):
        self.vertices.append(point)
        self.make_convex()
    
    def make_convex(self):
        if len(self.vertices) > 2:
            self.vertices = pymunk.util.convex_hull(self.vertices)

    def draw(self):
        glPushMatrix()
        self.transform()
        glLineWidth(3.0)
        glBegin(GL_LINE_LOOP)
        glColor4f(*self.color)
        for x, y in self.vertices:
            glVertex2f(x, y)
        glEnd()
        glPopMatrix()

class EditorLayer(cocos.layer.ScrollableLayer):
    is_event_handler = True

    def __init__(self):
        debug.msg('Initializing editor')

        super(EditorLayer, self).__init__()

        self.polygon = None
        self.polygons = []
        self.active_color = (1.0, 0.0, 0.0, 1.0)
        self.inactive_color = (1.0, 1.0, 1.0, 1.0)
    
    def on_enter(self):
        super(EditorLayer, self).on_enter()

        self.parent.push_handlers(self)

        self.polygon_layer = cocos.layer.ScrollableLayer()
        self.parent.scroller.add(self.polygon_layer, z=5)

        # Capture key state for easy movement handling
        self.keys = pyglet.window.key.KeyStateHandler()
        cocos.director.director.window.push_handlers(self.keys)

    def on_exit(self):
        super(EditorLayer, self).on_exit()

        self.parent.remove_handlers(self)
        cocos.director.director.window.remove_handlers(self.keys)

    def on_map_load(self):
        self.physics = self.parent.physics
        self.populate()

    def on_key_press(self, key, modifiers):
        if key == pyglet.window.key.S and modifiers & pyglet.window.key.MOD_CTRL:
            self.save()
            return True

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            # Make a new polygon if need be
            if self.polygon == None:
                self.polygon = Polygon()
                self.polygon.color = self.active_color
                self.polygon_layer.add(self.polygon)

            # Add vertex to polygon
            self.polygon.add_vertex(self.parent.scroller.pixel_from_screen(x, y))
        elif button == pyglet.window.mouse.RIGHT:
            # Done editing shape.
            self.polygon.color = self.inactive_color
            self.commit_polygon()

    def _step(self, dt):
        # Scroll map with WASD
        move_inc = 20
        dx = (self.keys[pyglet.window.key.D] - self.keys[pyglet.window.key.A]) * move_inc
        dy = (self.keys[pyglet.window.key.W] - self.keys[pyglet.window.key.S]) * move_inc
        scroller = self.parent.scroller
        scroller.set_focus(scroller.fx + dx, scroller.fy + dy)

    def commit_polygon(self):
        debug.msg('Adding polygon')
        # Add to physics space
        polygon = physics.make_static_polygon(self.polygon.vertices)
        self.polygons.append((polygon, self.polygon))
        self.physics.space.add_static(polygon)
        # Polygon committed. Let user make a new one.
        self.polygon = None

    def populate(self):
        debug.msg('Populating physics editor')
        for shape in self.physics.space.static_shapes:
            if isinstance(shape, pymunk.Poly):
                polygon = Polygon()
                for p in shape.get_points():
                    polygon.add_vertex((p.x, p.y))
                self.polygon_layer.add(polygon)

    def save(self):
        debug.msg('Saving level geometry')

        builder = ElementTree.TreeBuilder()

        builder.start('physics', {'name': 'physics'})

        for shape in self.physics.space.static_shapes:
            if isinstance(shape, pymunk.Poly):
                builder.start('polygon', {})

                for v in shape.get_points():
                    x = str(int(v.x))
                    y = str(int(v.y))
                    builder.start('vertex', {'x': x, 'y': y})
                    builder.end('vertex')

                builder.end('polygon')

        builder.end('physics')

        tree = ElementTree.ElementTree(builder.close())
        filename = util.resource.path(self.parent.tiledmap.properties['physics'])
        tree.write(filename)

