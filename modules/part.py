'''

Modules will inherit mainly from this base Part Class

-Setup: position joints
-Build: build off positioned joints

'''

import maya.cmds as cmds
from autorigger.lib import util
from autorigger.lib import nameSpace
from autorigger.lib import mayaBaseObject
from autorigger.lib import control
from autorigger.lib import util

reload(control)


class Part(mayaBaseObject.MayaBaseObject):

    def __init__(self, name, position=[0, 0, 0]):

        self.name = name
        # base position of the partRig
        self.position = position
        self.color = 0

        self.group = "{0}_master_{1}".format(name, nameSpace.GROUP)
        self.jointsGroup = "{0}_joints_{1}".format(name, nameSpace.GROUP)
        self.controlsGroup = "{0}_controls_{1}".format(name, nameSpace.GROUP)
        self.noXformGroup = "{0}_noXform_{1}".format(name, nameSpace.GROUP)
        self.hookGroup = "{0}_hook_{1}".format(name, nameSpace.GROUP)

        self.nameType = nameSpace.GROUP

        self.downAxis = 'x'
        self.upAxis = 'y'

        self.allJoints = []

    def hookTo(self, hooker):
        pass

    def initializeSetup(self):
        self.setupGroup = "{0}_{1}_{2}".format(
            self.getName(), nameSpace.SETUP, nameSpace.GROUP)
        self.skeletonGroup = "{0}_skeleton_{1}".format(
            self.getName(), nameSpace.GROUP)
        self.guidesGroup = "{0}_{1}_{2}".format(
            self.getName(), nameSpace.GUIDE, nameSpace.GROUP)
        self.masterGuide = control.Control(
            "{0}_master_{1}".format(self.getName(), nameSpace.GUIDE))

    # just using this for now as a quick workaround. Can change it later.
    def getSide(self):
        return nameSpace.getSide(self.getName())

    def setup(self):

        # create self.variable for groups
        self.initializeSetup()

        cmds.createNode("transform", n=self.setupGroup)
        cmds.createNode("transform", n=self.skeletonGroup)
        cmds.createNode("transform", n=self.guidesGroup)

        cmds.parent(self.skeletonGroup, self.setupGroup)
        cmds.parent(self.guidesGroup, self.setupGroup)

        for grp in [self.group, self.jointsGroup, self.controlsGroup, self.noXformGroup, self.hookGroup]:
            util.getGroup(grp)

        self.masterGuide.create()
        self.masterGuide.setParent(self.guidesGroup)

    def postSetup(self):
        #turn on LRA
        #make sure to store joints created for setupRigs in self.allJoints
        for joint in self.allJoints:
            cmds.setAttr( "{0}.displayLocalAxis".format(joint), 1 )

    def runSetup(self):
        self.setup()
        self.postSetup()

    def preBuild(self):
        # delete setup data(which is the guides)
        cmds.createNode("transform", n=self.group)
        cmds.addAttr(self.group, ln="bindJnts", at="message")
        cmds.createNode("transform", n=self.jointsGroup)
        cmds.createNode("transform", n=self.controlsGroup)
        cmds.createNode("transform", n=self.noXformGroup)
        cmds.createNode("transform", n=self.hookGroup)

        cmds.parent(self.jointsGroup, self.group)
        cmds.parent(self.controlsGroup, self.group)
        cmds.parent(self.noXformGroup, self.group)
        cmds.parent(self.hookGroup, self.group)

        cmds.delete(self.guidesGroup)

        cmds.parent(cmds.listRelatives(
            self.skeletonGroup, c=True), self.jointsGroup)

        cmds.delete(self.setupGroup)

    def build(self):
        # build will be coded in respective modules. This is just going to be
        # inhereited empty
        pass

    def postBuild(self):
        pass

    def runBuild(self):
        self.preBuild()
        self.build()
        self.postBuild()

    def createGuide(self, name, jnt, position=(0, 0, 0), parent=None):
        guide = control.Guide(name=name, position=position, parent=parent)
        guide.create()
        guide.setColor(self.getColor())

        print guide.getName()

        constraint = cmds.pointConstraint(guide.getName(), jnt)[0]
        cmds.parent(constraint)
        return guide


    def getDownAxis(self):
        return self.downAxis

    def getUpAxis(self):
        return self.upAxis