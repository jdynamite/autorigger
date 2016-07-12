'''

joint class

'''

import maya.cmds as cmds
import mayaBaseObject as mbo
import nameSpace

reload(mbo)

class Joint(mbo.MayaBaseObject):

    def __init__(self, name="joint", side="", align_to="world", parent="None", position=[0,0,0]):

        # since we are overloading init, it already goes through the \
        # routines to self assign class variables such as self.name  \
        # and self.side, etc

        super(Joint, self).__init__(name=name, side=side, nameType=nameSpace.JOINT, position=position)

    def create(self):
        cmds.joint(n=self.long_name)

    # just freezes transform. Looks fancy but under the hood it's not
    def orientToRotate(self):
        cmds.makeIdentity( self.getLongName(), apply=True, rotate=True)

    def setPosition(self, position, isWorld=True):
        cmds.xform(self.getLongName(), ws=isWorld)