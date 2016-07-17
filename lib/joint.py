'''

joint class

'''

import maya.cmds as cmds
import mayaBaseObject as mbo
import nameSpace

reload(mbo)

class Joint(mbo.MayaBaseObject):

    def __init__(self, name=None, position=(0,0,0), parent=None):
        super(Joint, self).__init__(name, position)
        self.nameType = nameSpace.JOINT
        self.name = name
        self.position = position
        self.parent = parent


    def create(self):
        # self.format_name()
        cmds.joint(n=self.name, p=self.position )



    # just freezes transform. Looks fancy but under the hood it's not
    def orientToRotate(self):
        cmds.makeIdentity( self.getName(), apply=True, rotate=True)
