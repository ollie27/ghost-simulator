from __future__ import absolute_import, division, print_function
from gslib.engine import primitives

__author__ = 'Martin'


# IMPORTANT: Name these functions with 'trigger' in the name, for reasons of saving.

def flip_state_trigger(targets):
    def func(interactee, interacter, options=None):
        for target in targets:
            target.state_index = str((int(target.state_index) + 1) % len(target.states))
    func.__name__ = 'flip_state_trigger'
    return func

def red_square_trigger(targets):
    def func(interactee, interacter, options=None):
        for target in targets:
            target.fear = 0
            target.fainted = True

            sprite = primitives.RectPrimitive(width=10, height=10, color=(120, 0, 0, 255))
            target.flair['fear_harvested'] = (sprite, (-5, target.dimensions[1] + 5))
    func.__name__ = 'red_square_trigger'
    return func

def activate_trigger(targets):
    def func(interactee, interacter, options=None):
        for target in targets:
            target.activate()
    func.__name__ = 'activate_trigger'
    return func

def begin_cutscene_trigger(targets):
    def func(interactee, interacter, option=None):
        if not option is None:
            interacter.game_class.run_cutscene(option)
    func.__name__ = 'begin_cutscene_trigger'
    return func

def change_map_trigger(targets):
    def func(interactee, interacter, option=None):
        if not option is None:
            interacter.game_class.go_to_map(option)
    func.__name__ = 'change_map_trigger'
    return func

def pick_up_torch_trigger(targets): # make this more generic with an options list to pick up flair/props
    def func(interactee, interacter, option=None):
        sprite = primitives.RectPrimitive(width=2, height=24, color=(139, 69, 19, 255))

        interacter.flair['torch'] = (sprite, (10, 0))
    func.__name__ = 'pick_up_torch_trigger'
    return func