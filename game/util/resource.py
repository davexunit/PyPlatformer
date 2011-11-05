import os
import pyglet

def path(filename):
    return os.path.join(pyglet.resource.location(filename).path, filename)

