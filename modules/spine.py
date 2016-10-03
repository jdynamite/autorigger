'''

--------------------------------------------------------
Spine class
--------------------------------------------------------

Creates a basic spine with 3 joints.

1. spine1_JNT (root of spine)
2. spine2_JNT ( ribs )
3. chest_JNT ( chest.. )


To-do: create a more robust rig that will allow different joint counts.

'''

# imported goods
import maya.cmds as cmds
import part
from autorigger.lib import joint
from autorigger.lib import control
from autorigger.lib import nameSpace
from autorigger.lib import attribute
from autorigger.lib import ikfk
from autorigger.lib import ribbon
from autorigger.lib import curve
from autorigger.lib import noRoll
from autorigger.lib import spline
from autorigger.lib import util

# reload. Can delete this after initial development
reload(part)
reload(joint)
reload(control)
reload(nameSpace)
reload(attribute)
reload(ikfk)
reload(ribbon)
reload(curve)
reload(noRoll)
reload(spline)

class Spine(part.Part):
    def __init__(self, name, position=([0, 10, 0], [0, 15, 0], [0, 18, 0] ), mirror=False):
        super(Spine, self).__init__(name)

        self.position = position

        print str(self.position) + ": position __________"

        # joint init
        self.spine1 = joint.Joint(
            "spine1_{0}".format(nameSpace.BINDJOINT),
            position=self.position[0]
        )

        self.spine2 = joint.Joint(
            "spine2_{0}".format(nameSpace.BINDJOINT),
            position = self.position[1]
        )

        self.spine3 = joint.Joint(
            "spine3_{0}".format(nameSpace.BINDJOINT),
            position = self.position[2]
        )

        # this sets up the ribbon master group
        self.ribbonMasterGroup = "{0}_rbn_master_grp".format(name)

        self.mirror = mirror


    def setup(self):
        super(Spine, self).setup()


        # stores joint names in a list
        jointList = [self.spine1, self.spine2, self.spine3]


        self.createSetupJoints(jointList)



    def postSetup(self):
        super(Spine, self).postSetup()

    def preBuild(self):
        super(Spine, self).preBuild()

    def build(self):
        super(Spine, self).build()

    def postBuild(self):
        super(Limb, self).postBuild()

    def createSetupJoints(self, joints):
        # this builds and names the bind joints
        parent = self.skeletonGroup
        self.guides = list()
        for i, jnt in enumerate(joints):
            print jnt.getPosition()
            jnt.create()
            print self.position[i]
            jnt.setPosition(self.position[i])
            jnt.setParent(parent)
            self.guides.append(
                self.createGuide(
                    name=jnt.getName().replace(nameSpace.BINDJOINT, nameSpace.GUIDE),
                    jnt=jnt.getName(),
                    position=jnt.getPosition(),
                    parent=self.guidesGroup
                )
            )
            parent = jnt.getName()
















