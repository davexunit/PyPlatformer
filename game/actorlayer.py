import cocos

import actor.actorlayer

class ActorLayer(actor.actorlayer.ActorLayer):
    def __init__(self):
        super(ActorLayer, self).__init__()
        self.batch = cocos.batch.BatchNode()
        self.add(self.batch)

    def add_actor(self, actor):
        super(ActorLayer, self).add_actor(actor)

        if actor.has_component('graphics'):
            self.batch.add(actor.get_component('graphics').sprite)

    def remove_actor(self, actor):
        super(ActorLayer, self).remove_actor(actor)

        if actor.has_component('graphics'):
            self.batch.remove(actor.get_component('graphics').sprite)

