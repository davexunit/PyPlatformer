import ConfigParser
import pyglet

class GameConfig(ConfigParser.RawConfigParser):
    def __init__(self, filename):
        ConfigParser.RawConfigParser.__init__(self)
        self.read(filename)

    def get_keycode(self, name):
        return eval("pyglet.window.key." + self.get('Controls', name))
