'''
Writing rig modules with this autorigger

Class: SingleEyelids


Notable procs:

Notable variables:
self.joints: list of joints
self.guides: list of guides
self.placeGuides: places guides in .setup() according to positions input. part.setup() will create your joints and guides,
                  but it's up to you to position them.

'''


import maya.cmds as cmds

# It is really important that you import part,
# because we'll be inheriting most of our toys from there.
from autorigger.modules import part
from autorigger.lib import control
from autorigger.lib import attribute
reload(control)
reload(attribute)

# Define your class
class SingleEyelid(part.Part):
    def __init__(self, name, positions=([5, 5, 0], [5, 7.5, 5]), jointAmmount=2, mirror=False):
        super(SingleEyelid, self).__init__(name)

        self.positions = positions
        # do you want it to mirror?
        self.mirror = mirror
        self.jointAmmount = jointAmmount

        self.downAxis='z'
        self.upAxis='y'


    def setup(self):
        super(SingleEyelid, self).setup()

        self.placeGuides(self.positions)
        self.setPositionUPVS([0,0,5])


    def postSetup(self):
        super(SingleEyelid, self).postSetup()
        # before you delete the master guide, query the down axis
        # get what you want from him, then kill him! Bwuahahaha
        self.strAimAttr = (
            cmds.getAttr("{0}.aim".format(self.masterGuide.getName()), asString=True)
        )
        # remove the - if there is one
        if (len(self.strAimAttr)):
            self.downAxis = self.strAimAttr[-1]
        else:
            self.downAxis = self.strAimAttr

    def preBuild(self):
        super(SingleEyelid, self).preBuild()

        pass


    def build(self):
        super(SingleEyelid, self).build()

        self.createHandle()
        self.createControl()

        attribute.connect(self.control.getName(), self.handleNull)

        cmds.select(self.joints[0])
        cmds.parent(w=True)
        cmds.delete(self.group)

    def postBuild(self):
        super(SingleEyelid, self).postBuild()

        pass

    def createHandle(self):
        self.handle = "{0}_IKH".format(self.name)
        cmds.ikHandle(
            sj=self.joints[0],
            ee=self.joints[1],
            sol="ikSCsolver",
            n=self.handle
        )

        self.handleNull = cmds.createNode("transform", n="{0}_NULL".format(self.handle))
        cmds.delete(cmds.pointConstraint(self.handle, self.handleNull))
        handleGrp = cmds.duplicate(self.handleNull, po=True, n="{0}_GRP".format(self.handle))
        cmds.parent(self.handleNull, handleGrp)

        self.controlPosition = cmds.xform(self.handleNull, ws=True, q=True, t=True)

        cmds.parent(self.handle, self.handleNull)

    def createControl(self):

        self.control = control.Control(name=self.name, shape="square")
        self.control.create()
        self.control.setPosition(self.controlPosition)
        self.control.set_color("green")

