"""
everything we program is useless,
unless justified in the making of
art - be practical
"""

import maya.cmds as cmds


class switch(object):
    """
    switch routine to mimic other languages switch
    """

    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        yield self.match
        raise StopIteration

    def match(self, *args):

        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False


class rig:
    """
    rig class should mantain a character's modules
    and be responsible for curating it: rebuilding
    positions and perhaps updating itself
    """

    def __init__(self, name=None, path=None):
        self.name = name
        self.path = path
        self.modules = list()
        self.import_modules()

    def rig_node(self):
        if not cmds.objExists("%s_rig" % self.name):
            cmds.createNode("transform", n="%s_rig" % self.name)


class module:
    """
    module class will need certain common utilities
    like building ik, fk, spines, connections,
    space switching, chain blending

    rig modules will inherit from this class
    """

    def __init__(self, name=None, path=None, type=None):
        self.name = name
        self.path = path
        self.is_done_building = False
