'''Tiled is a 2D tile-based map editor. Tiled uses a highly customizable XML
format for storing created maps.
Tile layers are translated into Cocos2D RectMapLayer objects. Object layers are
loaded into a simple data type, but the objects themselves are loaded by
factory methods are that registered by the user. See register_object_factory
for details.
This module intends to be as general as possible, allowing you, the user, to
adapt these functions to your needs.
'''

try:
    from xml.etree import ElementTree
except ImportError:
    import elementtree.ElementTree as ElementTree

import os
import base64
import zlib
import array
import pyglet
from pyglet.gl import *
import cocos

class TileSet(list):
    pass

class ObjectLayer(object):
    def __init__(self, name, width, height, objects):
        self.name = name
        self.width = width
        self.height = height
        self.objects = objects

class TiledMap(object):
    def __init__(self):
        self.orientation = None
        self.version = None
        self.width = 0
        self.height = 0
        self.tile_width = 0
        self.tile_height = 0
        self.tileset = TileSet()
        self.layers = {}
        self.object_groups = {}
        self.properties = {}

class MapException(Exception):
    pass

def load_image(tag):
    # Get image properties
    source = tag.get('source')
    width = int(tag.get('width'))
    height = int(tag.get('height'))
    return pyglet.resource.image(source), width, height

def load_tileset(tag):
    # Get tileset properties
    firstgid = int(tag.get('firstgid'))
    name = tag.get('name')
    tile_width = int(tag.get('tilewidth'))
    tile_height = int(tag.get('tileheight'))

    child = tag.find('image')
    # Raise an exception if child tag is not <image>
    if child.tag != 'image':
        raise MapException('Unsupported tag in tileset: %s' % child.tag)
    # Load image
    image, image_width, image_height  = load_image(child)

    # Construct tileset
    tileset = TileSet()
    for y in range(0, image_height, tile_height):
        for x in range(0, image_width, tile_width):
            tile = image.get_region(x, image_height - y - tile_height, tile_width, tile_height)
            tileset.append(cocos.tiles.Tile(y * (image_width / tile_width) + x, None, tile))
            # set texture clamping to avoid mis-rendering subpixel edges
            # Borrowed from cocos2d sources - tiles.py
            tile.texture.id
            glBindTexture(tile.texture.target, tile.texture.id)
            glTexParameteri(tile.texture.target, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(tile.texture.target, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    return tileset

# Object factories
factories = dict()
def register_object_factory(name):
    def decorate(func):
        factories[name] = func
        return func
    return decorate

def load_map(filename):
    # Open xml file
    tree = ElementTree.parse(filename)
    root = tree.getroot()

    # Root level tag is expected to be <map> so raise an exception if it's not
    if root.tag != 'map':
        raise MapException('%s root level tag is %s rather than <map>' % (filename, root.tag))
    # We can only load orthogonal maps here because that's all I care about :P
    if root.get('orientation') != 'orthogonal':
        raise MapException('Map orientation %s not supported. Orthogonal maps only' % root.get('orientation'))

    # Initialize map
    tiledmap = TiledMap()
    tiledmap.orientation = root.get('orientation')
    tiledmap.version = root.get('version')
    tiledmap.width = int(root.get('width'))
    tiledmap.height = int(root.get('height'))
    tiledmap.tile_width = int(root.get('tilewidth'))
    tiledmap.tile_height = int(root.get('tileheight'))

    # Load map properties
    properties = root.find('properties')
    for p in properties.findall('property'):
        tiledmap.properties[p.get('name')] = p.get('value')

    # Load tilesets
    for tag in root.findall('tileset'):
        tiledmap.tileset += load_tileset(tag)

    # Load layers
    for tag in root.findall('layer'):
        layer = load_layer(tag, tiledmap)
        tiledmap.layers[layer.id] = layer

    # Load object layers
    for tag in root.findall('objectgroup'):
        layer = load_object_group(tag, tiledmap)
        tiledmap.object_groups[layer.name] = layer

    return tiledmap
    
def load_layer(tag, tiledmap):
    # Get layer properties
    name = tag.get('name')
    width = int(tag.get('width'))
    height = int(tag.get('height'))

    child = tag.find('data')
    # Raise exception if there is no <data> tag because that's fucked up
    if child == None:
        raise MapException('No <data> tag in layer')

    # Load layer data
    data = load_data(child)
    # Construct layer
    columns = []
    for i in range(0, width):
        row = []
        columns.append(row)
        for j in range(0, height):
            index = j * width + i
            tile = tiledmap.tileset[data[index] - 1]
            if data[index] == 0:
                tile = None
            row.insert(0, cocos.tiles.RectCell(i, height - j - 1,
                tiledmap.tile_width, tiledmap.tile_height, None, tile))

    return cocos.tiles.RectMapLayer(name, tiledmap.tile_width, 
                                    tiledmap.tile_height, columns, (0,0,0),
                                    None)

def load_data(tag):
    # Get data properties
    encoding = tag.get('encoding')
    compression = tag.get('compression')
    data = tag.text

    # Only base64 encoding supported as of now
    if encoding != 'base64':
        raise MapException('Encoding type %s not supported' % encoding)
    # Only zlib compression supported as of now
    if compression != 'zlib':
        raise MapException('Compression type %s not supported' % compression)

    # Uncompress data
    decoded_data = zlib.decompress(base64.b64decode(data))

    # decoded_data is a string made of 64 bit integers now
    # Turn that string into an array of 64 bit integers
    # TODO: Use encoding 'L' or 'I' accordingly based upon CPU architecture.
    #       32 bit = 'L' and 64 bit = 'I'

    return array.array('I', decoded_data)

def load_object_group(tag, tiledmap):
    name = tag.get('name')
    width = int(tag.get('width'))
    height = int(tag.get('height'))

    objects = []
    for child in tag.findall('object'):
        objects.append(load_object(child, tiledmap))

    return ObjectLayer(name, width, height, objects)

def load_object(tag, tiledmap):
    '''Loads Tiled object XML.
    Map height and tile height need to be passed because OpenGL uses the
    bottom-left of the screen as the origin where as Tiled uses the upper-left.
    This means that we have to invert the Y coordinate.
    '''
    # Get object properties
    properties = dict()

    # Every tiled object has these properties
    properties['name'] = tag.get('name')
    properties['type'] = tag.get('type')
    properties['x'] = int(tag.get('x'))
    properties['y'] = height * tiledmap.tile_height - int(tag.get('y')) - \
                        tiledmap.tile_height
    properties['width'] = int(tag.get('width'))
    properties['height'] = int(tag.get('height'))

    # Read custom properties
    for p in tag.find('properties'):
        properties[p.get('name')] = p.get('value')

    # Load object
    obj = factories[actor_type](properties)

    return obj

