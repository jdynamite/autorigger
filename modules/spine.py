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
    def __init__(self, name, positions=([0, 10, 0], [0, 15, 0], [0, 18, 0] ), mirror=False):
        super(Spine, self).__init__(name)

        self.positions = positions

        # this sets up the ribbon master group
        self.ribbonMasterGroup = "{0}_rbn_master_grp".format(name)

        self.mirror = mirror

        self.downAxis = "y"
        self.upAxis = "x"

        self.controls = []

    def setup(self):
        super(Spine, self).setup()

        self.placeGuides(self.positions)

        self.setPositionUPVS( [5,0,0] )

        self.setDownAxis('y')
        self.setUpAxis('x')

    def postSetup(self):
        super(Spine, self).postSetup()

    def preBuild(self):
        super(Spine, self).preBuild()

    def build(self):
        super(Spine, self).build()

        # create control rig joints
        self.controlRigJoints = []

        for i, jnt in enumerate(self.joints):
            result = cmds.duplicate(
                jnt,
                n=jnt.replace(nameSpace.BINDJOINT, "IK_JNT"),
                po=True
            )
            self.controlRigJoints.append(result)

            if i == 0:
                cmds.select(result)
                cmds.parent(w=True)
            else:
                cmds.parent( result, self.controlRigJoints[i-1] )

        self.buildChest()
        self.buildFk()

    def postBuild(self):
        super(Limb, self).postBuild()

    def buildChest(self):
        # create chest control
        self.chest = control.Control(
            "chest",
            shape="cube"
        )
        self.chest.create()
        self.chest.setPosition(self.positions[1])

        cmds.select(self.controlRigJoints[0])
        cmds.select(self.controlRigJoints[1], tgl=True)
        self.chestIKH = cmds.ikHandle(
            name="chest_IKH",
            sol = "ikSCsolver",
        )[0]
        cmds.parent( self.chestIKH, self.chest.getName() )
        cmds.orientConstraint(
            self.chest.getName(),
            self.controlRigJoints[1]
        )

    def buildFk(self):

        # create the fk controls
        for i, jnt in enumerate(self.joints):

            con = control.Control(
                jnt.replace( nameSpace.JOINT, nameSpace.FK ),
            )

            con.create()
            con.setPosition( self.positions[i] )

            self.controls.append(con)


















