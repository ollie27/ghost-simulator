from __future__ import absolute_import, division, print_function
from AI_functions import BaseFunction

__author__ = 'Martin'

################################################################################
### unpossession functions
### These happen when a character is unpossessed
################################################################################

class BecomeUnpossessedFunction(BaseFunction):
    def __init__(self, name, obj):
        super(BecomeUnpossessedFunction, self).__init__(name, obj, 'unpossessed_functions', 'become_unpossessed_functions')


class AdvanceState(BecomeUnpossessedFunction): # advances through states that are purely numerical, starting from 0 (need to be strings)
    def __init__(self, obj):
        super(AdvanceState, self).__init__('Advance State', obj)

    def function(self, unpossessor):
        obj = self.object
        obj.state_index = str((int(obj.state_index) + 1) % len(obj.states))


# def undo_im_possessed(obj):
#     def func(unpossessor):
#         return
#         if not obj.possessed_by:
#             del obj.flair['possessed']
#     func.__name__ = 'undo_im_possessed'
#     return func
#
#
# def flip_state(obj):
#     def func(unpossessor):
#         obj.state_index = str((int(obj.state_index) + 1) % len(obj.states))
#     func.__name__ = 'flip_state'
#     return func
