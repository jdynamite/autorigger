'''

joint class

'''

import maya.cmds as cmds
from mayaBaseObject import MayaBaseObject
import nameSpace

class Joint(MayaBaseObject):

    def __init__(self, name=None, side=None, align_to=None, parent=None):
        super(Joint, self).__init__(name)
        self.name = name
        self.side = side
        self.align_to = align_to
        self.parent = parent

        self.nameType = nameSpace.JOINT

    def create(self):

        self.format_name()
        cmds.joint(n=self.long_name)

    # just freezes transform. Looks fancy but under the hood it's not
    def orientToRotate(self):
        cmds.makeIdentity( self.getLongName(), apply=True, rotate=True)

