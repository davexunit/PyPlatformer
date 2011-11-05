try:
    from xml.etree import ElementTree
except ImportError:
    import elementtree.ElementTree as ElementTree

import pyglet

# Just a typedef, move along folks
class AnimSet(dict):
    pass

def load_animset(filename):
    # Open xml file
    root = ElementTree.parse(filename).getroot()
    if root.tag != 'animset':
        raise MapException('Expected <animset> tag, found <%s> tag' % root.tag)

    # Get animset properties
    image = pyglet.resource.image('anims/' + root.get('image'))
    tile_width = int(root.get('tilewidth'))
    tile_height = int(root.get('tileheight'))

    # Create image sequence of tiles
    grid = pyglet.image.ImageGrid(image, image.width / tile_width, image.height / tile_height)
    sequence = grid.get_texture_sequence()
    anims = AnimSet()

    # Loop through all animations
    for child in root.findall('anim'):
        anim_name = child.get('name')
        anim_duration = float(child.get('duration'))
        frame_indices = [int(x) for x in child.text.split(',')]
        frames = list()
        for f in frame_indices:
            frames.append(sequence[f])
        anims[anim_name] = pyglet.image.Animation.from_image_sequence(frames, anim_duration, loop=True)
    return anims

