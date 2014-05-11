class Error(Exception):
    """Cutscene exception"""
    pass


class CutsceneAction(object):

    def __init__(self, game_, map_, load_dict=None):
        self.game = game_
        self.map = map_
        self.edit_control_map = {}
        self.to_save = []
        self.load_dict = load_dict or {}
        self.wait_til_done = self.property('wait_til_done', 'bool', default=True)

    def property(self, name, editor_type, default=None):
        self.edit_control_map[name] = editor_type
        self.to_save.append(name)

        if name in self.load_dict:
            return self.load_dict[name]
        else:
            return default

    def get_editor(self):
        return self.edit_control_map

    def save(self):
        d = {'class_name': self.__class__.__name__}
        for k in self.to_save:
            d[k] = getattr(self, k)
        return d

    # Used in editor.
    def describe(self):
        return ("WAIT AFTER " if self.wait_til_done else "") + self.__class__.__name__[:-6] + ": "

    # Called when CutsceneAction should forget its state and start anew.
    def restart(self):
        pass

    # Should update() be called again next tick?
    def update_again(self):
        return False

    # Gets called once per tick at least once and then as long as update_again() returns True.
    def update(self):
        raise Exception("CutsceneAction '" + self.__class__.__name__ + "' update() not implemented!")


class Cutscene(object):

    def __init__(self, name, actions):
        self.name = name
        self.actions = actions
        self.current_actions = []
        self.remaining_actions = actions[:]
        self.tick = 0            # just for tracking ticks done
        self.done = False        # just for tracking if finished
        self.waiting_for = []    # just for tracking current wait group

    def restart(self):
        self.current_actions = []
        self.remaining_actions = self.actions[:]
        self.tick = 0           # just for tracking ticks done
        self.done = False       # just for tracking if finished
        self.waiting_for = []   # just for tracking current wait group

    def update(self):
        # anything currently running & blocking new events?
        wait_for = []
        for ca in self.current_actions:
            if ca.wait_til_done:
                wait_for.append(ca)

        # any actions eligible to become current?
        if len(wait_for) == 0:
            while len(self.remaining_actions) > 0:
                ra = self.remaining_actions[0]
                self.current_actions.append(ra)
                self.remaining_actions.remove(ra)
                ra.restart()
                if ra.wait_til_done and ra.update_again():
                    wait_for.append(ra)
                    break

        # do current actions
        keep_actions = []
        for ca in self.current_actions:
            ca.update()
            if ca.update_again():
                keep_actions.append(ca)
        self.current_actions = keep_actions

        # update stats
        self.done = len(self.current_actions) == 0 and len(self.remaining_actions) == 0
        self.waiting_for = wait_for
        self.tick += 1


class TestAction(CutsceneAction):

    def __init__(self, g, m, l):
        CutsceneAction.__init__(self, g, m, l)
        self.ticks_remaining = 30
        self.obj_ref = self.property('obj_ref', 'obj_ref', default='<None>')
        self.pos = self.property('pos', 'coords', default=(0, 0))

    def update_again(self):
        return self.ticks_remaining >= 0

    def update(self):
        self.ticks_remaining -= 1

    def restart(self):
        self.ticks_remaining = 30


class ControllingCutsceneAction(CutsceneAction):

    def __init__(self, g, m, l):
        CutsceneAction.__init__(self, g, m, l)
        self.what = self.property('what', 'obj_ref', default='<None>')

    def valid_ref(self):
        return self.what in self.map.objects

    def get_ref(self):
        return self.map.objects[self.what]

    def hook(self):
        if not self.valid_ref():
            if self.what == '<None>':
                raise Error("Action not configured. You need to set .what on:\n" + self.describe())
            else:
                raise Error("Couldn't find thing named '" + self.what + "' in the current map\n" + self.describe())
        self.get_ref().cutscene_controlling = self

    def unhook(self):
        if self.valid_ref() and self.map.objects[self.what].cutscene_controlling == self:
            self.get_ref().cutscene_controlling = None


class WalkToAction(ControllingCutsceneAction):

    def __init__(self, g, m, l):
        ControllingCutsceneAction.__init__(self, g, m, l)
        self.where = self.property('where', 'coords', default=(0, 0))
        self.speed = self.property('speed', 'int', default=2)

    def describe(self):
        return ControllingCutsceneAction.describe(self) + " " + self.what + " -> " + str(self.where) + \
                                                          " x" + str(self.speed)

    def update_again(self):
        return self.valid_ref() and (self.get_ref().coord[0] != self.where[0] or
                                     self.get_ref().coord[1] != self.where[1])

    def update(self):
        self.hook()

    def restart(self):
        self.unhook()

    def game_object_hook(self, ch):
        p_start = ch.coord
        p_end = self.where

        if not self.update_again():
            self.unhook()
        else:
            ch.velocity = (min(self.speed, max(-self.speed, p_end[0] - p_start[0])),
                           min(self.speed, max(-self.speed, p_end[1] - p_start[1])))


possible_actions = {'Test Action': TestAction, 'Walk To': WalkToAction}
