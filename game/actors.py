import weakref
import pyglet
import cocos

from component import *
from .. import mapload
class Player(Actor):
    def __init__(self):
        super(Player, self).__init__()
        self.size = (24, 24)

        # Load animations
        anims = mapload.load_animset('anims/king.xml')

        self.add_component(HumanInputComponent())
        self.add_component(SpriteComponent(anims, offset=(-4,0)))
        self.add_component(PhysicsComponent(200))
        self.add_component(PlayerSoundComponent())
        self.refresh_components()

class Derp(Actor):
    def __init__(self, animfile, dialog):
        super(Derp, self).__init__()
        self.size = (24, 24)

        # Load animations
        from .. import mapload
        anims = mapload.load_animset(animfile)

        #self.add_component(DumbAI())
        self.add_component(SpriteComponent(anims, offset=(-4,0)))
        self.add_component(PhysicsComponent(200))
        self.add_component(DialogComponent(dialog))
        self.refresh_components()

@mapload.register_actor_factory('npc')
def load_npc(properties):
    npc = Derp(properties['file'], properties['dialog'])
    return npc

class Sign(Actor):
    def __init__(self, text):
        super(Sign, self).__init__()
        self.add_component(DialogComponent(text))
        self.refresh_components()

@mapload.register_actor_factory('sign')
def load_sign(properties):
    sign = Sign(properties['text'])
    return sign

class Portal(Actor):
    def __init__(self, destination, exit_portal):
        super(Portal, self).__init__()
        self.destination = destination
        self.exit_portal = exit_portal
        self.active = True
        self.refresh_components()

    def on_actor_enter(self, actor):
        if self.active:
            def load_map(dt):
                from .. import map
                from .. import util
                from ..game import game

                # Load new map
                new_scene = mapload.load_map(self.destination)
                new_scene.name = self.destination
                new_scene.focus = actor

                # Get the exit portal
                portal = new_scene.actors.get_actor(self.exit_portal)
                # The active flag is so that when the actor is placed onto the
                # portal it doesn't trigger a map change causing an unbounded
                # loop.
                portal.active = False

                #def old_death(ref):
                #    print "old map died"
                #oldmap = weakref.ref(actor.parent_map, old_death)

                # Remove actor from current map and place on new map
                self.parent_map.actors.remove_actor(actor)
                new_scene.actors.add_actor(actor)
                actor.position = portal.position

                # Add the walkaround state
                walkaround = map.mapscene.WalkaroundState()
                walkaround.input_component = actor.get_component('input')
                new_scene.state_replace(walkaround)

                # Replace map
                cocos.director.director.replace(cocos.scenes.transitions.FadeTransition(new_scene, 1))

                #def do_refcount(dt):
                #    from sys import getrefcount
                #    print oldmap(), getrefcount(oldmap())
                #pyglet.clock.schedule_interval(do_refcount, 1)
                #from sys import getrefcount
                #print "ref count:", getrefcount(oldmap())
                #print "weakref count:", weakref.getweakrefcount(oldmap())
                #def print_ref(dt):
                #    import debug
                #    debug.print_referrers(oldmap())
            # Perform the map loading on the next game loop
            pyglet.clock.schedule_once(load_map, 0)

    def on_actor_exit(self, actor):
        self.active = True

@mapload.register_actor_factory('portal')
def load_portal(properties):
    return Portal(properties['map'], properties['exit'])

from .. import map
class TestScript(Actor):
    def __init__(self):
        super(TestScript, self).__init__()

    def on_actor_enter(self, actor):
        def func():
            self.parent_map.state_push(map.mapscene.DialogState('Testing!'))
        action = cocos.actions.CallFunc(func)#cocos.actions.Blink(5,.1)
        self.parent_map.state_push(map.mapscene.CinematicState(action))
