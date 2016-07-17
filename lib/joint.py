'''

joint class

'''

import maya.cmds as cmds
import mayaBaseObject as mbo
import nameSpace

reload(mbo)

class Joint(mbo.MayaBaseObject):

<<<<<<< HEAD
    def __init__(self, name=None, position=(0,0,0), parent=None):
        super(Joint, self).__init__(name, position)
        self.nameType = nameSpace.JOINT
        self.name = name
        self.position = position
        self.parent = parent


    def create(self):
        # self.format_name()
        cmds.joint(n=self.name, p=self.position )


=======
    def __init__(self, name="joint", side="", align_to="world", parent="None", position=[0,0,0]):

        # since we are overloading init, it already goes through the \
        # routines to self assign class variables such as self.name  \
        # and self.side, etc

        super(Joint, self).__init__(name=name, side=side, nameType=nameSpace.JOINT, position=position)

    def create(self):
        cmds.joint(n=self.long_name)
>>>>>>> 756fdac1dcc3b0b59bab8ff200c0b3718af80efd

    # just freezes transform. Looks fancy but under the hood it's not
    def orientToRotate(self):
        cmds.makeIdentity( self.getName(), apply=True, rotate=True)

    def setPosition(self, position, isWorld=True):
        cmds.xform(self.getLongName(), ws=isWorld)