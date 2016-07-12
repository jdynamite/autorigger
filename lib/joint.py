'''

joint class

'''

import maya.cmds as cmds
import mayaBaseObject as mbo
import nameSpace

reload(mbo)

class Joint(mbo.MayaBaseObject):

    def __init__(self, name=None, side=None, align_to=None, parent=None):
        super(Joint, self).__init__(name)
        # note to selves: calling self.side in this module causes an error. Keep it in MBO
        self.name = name
        self.nameType = nameSpace.JOINT
        self.align_to = align_to
        self.parent = parent

        self.format_name()

    def create(self):
        # self.format_name()
        cmds.joint(n=self.long_name)

    # just freezes transform. Looks fancy but under the hood it's not
    def orientToRotate(self):
        cmds.makeIdentity( self.getLongName(), apply=True, rotate=True)

