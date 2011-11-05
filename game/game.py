import pyglet
import cocos
from cocos.director import director
import pymunk

import debug
import config
import util.resource
import gamescene
import editor

class Game(object):
    '''Wraps up all of the game content into one class.
    '''
    def __init__(self):
        debug.msg('Initializing game')

        self.config = None

        # Add paths for pyglet to use for resources
        pyglet.resource.path.append('../data/')
        pyglet.resource.path.append('../data/maps/')
        pyglet.resource.reindex()

    def load_config(self, filename):
        debug.msg('Loading configuration')
        self.config = config.GameConfig(filename)

    def run(self):
        debug.msg('Starting game')

        # Load configuration file
        self.load_config(util.resource.path('game.conf'))

        # Initialize physics library
        pymunk.init_pymunk()

        # Create window
        debug.msg('Creating window')
        director.init(width=self.config.getint('Graphics', 'screen_width'),
                height=self.config.getint('Graphics', 'screen_height'),
                do_not_scale=True, resizable=True, 
                fullscreen=self.config.getboolean('Graphics', 'fullscreen'))
        director.show_FPS = True

        # Run game scene
        scene = gamescene.GameScene()
        display_editor = True
        if display_editor:
            scene.add(editor.EditorLayer(), z=1)

        debug.msg('Starting game director')
        director.run(scene)

        debug.msg('Exiting game')

# OH NOES A GLOBAL VARIABLE
# Deal with it.
game = Game()

if __name__ == '__main__':
    game.run()
