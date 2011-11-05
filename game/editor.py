import pyglet
import cocos

import debug
import util

class EditorLayer(cocos.layer.ScrollableLayer):
    is_event_handler = True

    def __init__(self):
        super(EditorLayer, self).__init__()
        self.scroll_x = 0
        self.scroll_y = 0
        self.keys = pyglet.window.key.KeyStateHandler()
        cocos.director.director.window.push_handlers(self.keys)

    def on_key_press(self, key, modifiers):
        pass

    def _step(self, dt):
        # Scroll map with WASD
        move_inc = 20
        dx = (self.keys[pyglet.window.key.D] - self.keys[pyglet.window.key.A]) * move_inc
        dy = (self.keys[pyglet.window.key.W] - self.keys[pyglet.window.key.S]) * move_inc
        self.scroll_x += dx
        self.scroll_y += dy
        self.parent.scroller.set_focus(self.scroll_x, self.scroll_y)

