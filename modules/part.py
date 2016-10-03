'''

Modules will inherit mainly from this base Part Class

-Setup: Creates joints, guides and groups for hierarchy purposes. The guides will be positioned in modules that are inheriting from Part
        ie: Limb, Foot, Spine, etc

        Each group has it's own variable that can be called

            self.group: master group. The top node
            self.jointsGroup: the joints group.
            self.controlsGroup: controls group
            self.noXformGroup: parts of rig that should not xform with parent
            self.hookGroup: the parts of the rig that need a 'hook' will go here

-Build: build off positioned joints

Notable procs:

Notable variables:
self.joints: list of joints
self.guides: list of guides

'''

import maya.cmds as cmds
from autorigger.lib import util
from autorigger.lib import nameSpace
from autorigger.lib import mayaBaseObject
from autorigger.lib import control
from autorigger.lib import joint
from autorigger.lib import attribute


reload(control)


class Part(mayaBaseObject.MayaBaseObject):

    def __init__(self, name, positions=([0, 0, 0]), jointAmmount=3):

        self.name = name
        # base position of the partRig
        self.positions = positions
        self.jointAmmount = jointAmmount
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

        self.part = {}

    def hookTo(self, hooker):
        pass

    def initializeSetup(self):
        self.setupGroup = "{0}_{1}_{2}".format(self.getName(), nameSpace.SETUP, nameSpace.GROUP)
        self.skeletonGroup = "{0}_skeleton_{1}".format(self.getName(), nameSpace.GROUP)
        self.guidesGroup = "{0}_{1}_{2}".format(self.getName(), nameSpace.GUIDE, nameSpace.GROUP)
        self.masterGuide = control.Control("{0}_master_{1}".format(self.getName(), nameSpace.GUIDE))

        cmds.createNode("transform", n=self.setupGroup)
        cmds.createNode("transform", n=self.skeletonGroup)
        cmds.createNode("transform", n=self.guidesGroup)

        cmds.parent(self.skeletonGroup, self.setupGroup)
        cmds.parent(self.guidesGroup, self.setupGroup)

        self.masterGuide.create()
        self.masterGuide.setParent(self.guidesGroup)

        #position masterGuide up a bit
        cmds.select( "{0}Shape1.cv[0:7]".format(self.masterGuide.getName()) )
        cmds.move( 0,5,0, r=True)


    # just using this for now as a quick workaround. Can change it later.
    def getSide(self):
        return nameSpace.getSide(self.getName())

    def setup(self):
        # create self.variable for groups
        self.initializeSetup()

        # switch class comes in handy here to create aimAttr and upAttr for the masterGuide
        self.aimAttr = attribute.switch(
            self.masterGuide.getName(),
            "aim",
            0,
            ["x", "y", "z", "-x", "-y", "-z"],
            [[1, 0, 0], [0, 1, 0], [0, 0, 1], [-1, 0, 0], [0, -1, 0], [0, 0, -1]]
        )

        self.upAttr = attribute.switch(
            self.masterGuide.getName(),
            "up",
            0,
            ["x", "y", "z", "-x", "-y", "-z"],
            [[1, 0, 0], [0, 1, 0], [0, 0, 1], [-1, 0, 0], [0, -1, 0], [0, 0, -1]]
        )

        # build setup joints and guides
        self.buildSetupJoints()

        # create lra display attribute
        self.lraDisplayOutput = self.lraAttr()

        # aimConstraint joints for orientations
        self.setupJointOrientations(self.joints)

        # store the aim attr
        self.strAimAttr = (
            cmds.getAttr("{0}.aim".format(self.masterGuide.getName()),
                         asString=True)
        )


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

        for grp in [self.jointsGroup, self.controlsGroup, self.noXformGroup, self.hookGroup]:
            util.getGroup(grp)


        cmds.parent(self.jointsGroup, self.group)
        cmds.parent(self.controlsGroup, self.group)
        cmds.parent(self.noXformGroup, self.group)
        cmds.parent(self.hookGroup, self.group)

        cmds.delete(self.guidesGroup)
        cmds.setAttr("{0}.inheritsTransform".format(self.noXformGroup), 0)

        skeletonJnts = self.getSkeletonJoints()

        if skeletonJnts:
            for jnt in skeletonJnts:
                jnt = joint.Joint(jnt)
                jnt.rotateToOrient()
                cmds.addAttr(jnt.getName(), ln="part", at="message")

                cmds.connectAttr(
                    "{0}.bindJnts".format(self.group),
                    "{0}.part".format(jnt.getName()),
                    f=True
                )

        # parent joints to self.jointsGroup
        cmds.parent(
            cmds.listRelatives(self.skeletonGroup, c=True),
            self.jointsGroup
        )

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

        constraint = cmds.pointConstraint(guide.getName(), jnt)[0]
        cmds.parent(constraint)
        return guide

    def getSkeletonJoints(self):
        skeletonJnts = cmds.listRelatives(
            self.skeletonGroup,
            ad=True
        )

        if skeletonJnts:
            return skeletonJnts
        return None


    def getDownAxis(self):
        return self.downAxis

    def getUpAxis(self):
        return self.upAxis

    def buildSetupJoints(self):
        # create the joints and guides
        self.joints = []
        self.guides = []
        cmds.select(cl=True)
        parent = self.skeletonGroup

        for i in range(self.jointAmmount):
            plus = i + 1
            position = [(i * 3), 0, 0]

            jnt = joint.Joint(
                name="{0}{1}_{2}".format(
                    self.getName(),
                    '%02d' % plus,
                    nameSpace.BINDJOINT
                ),
                position=position,
            )
            # jnt.setPosition(jnt.getPosition)
            jnt.create()

            cmds.parent(jnt.getName(), parent)
            parent = jnt.getName()

            self.joints.append(jnt.getName())

            self.guides.append(
                self.createGuide(
                    name=jnt.getName().replace(nameSpace.BINDJOINT, nameSpace.GUIDE),
                    jnt=jnt.getName(),
                    position=jnt.getPosition(),
                    parent=self.masterGuide.getName()
                )
            )

    def lraAttr(self):
        cmds.select(self.masterGuide.getName())
        cmds.addAttr(
            ln="lra",
            at="float",
            k=True,
            dv=1
        )
        attr = "{0}.lra".format(self.masterGuide.getName())
        return attr


    def setupJointOrientations(self, joints):
        #joints is list of joints
        # note that joints must be a single hierarchy AND in correct order
        # single hierarchy meaning joint chains with forks won't work.

        constraints = list()

        for i,jnt in enumerate(joints):

            # if last joint, orient it
            if jnt == joints[-1]:

                jntA = joints[i-1]
                jntB = jnt

                constraints.append(
                    cmds.orientConstraint(jntA, jntB)
                )

            # if not last joint, aim constraint
            else:

                #create upv loc
                upv = cmds.spaceLocator(name = jnt.replace( nameSpace.JOINT, nameSpace.UPV))[0]
                cmds.delete( cmds.parentConstraint( jnt, upv ) )
                cmds.setAttr( "{0}.ty".format(upv), 3 )
                cmds.parent(upv, self.guides[i].getName())

                aimer = self.guides[i+1].getName()
                constraints.append(
                    cmds.aimConstraint(
                        aimer,
                        jnt,
                        wut="object",
                        wuo=upv)[0]
                )

                print self.masterGuide.getName()

                # so that the aim and up are not both x
                cmds.setAttr("{0}.up".format(self.masterGuide.getName()), 1)
                self.strUpAttr = (
                    cmds.getAttr(
                        "{0}.up".format(self.masterGuide.getName()),
                        asString=True)
                )

                # connects axis attributes to aimConstraints
                cmds.connectAttr(self.upAttr, "{0}.upVector".format(constraints[i]), f=True)
                cmds.connectAttr(self.aimAttr, "{0}.aimVector".format(constraints[i]), f=True)

            # connect lra display attribute
            cmds.connectAttr(
                self.lraDisplayOutput,
                "{0}.displayLocalAxis".format(jnt)
            )
            # slip into hierarchy
            cmds.parent(constraints[i], self.guidesGroup)


        return constraints

    def placeGuides(self, jointPositions):
        # note that masterGuide will be moved instead of the first guide in hierarchy


        # place guides
        for i, guide in enumerate(self.guides):

            if i == 0:
                self.masterGuide.setPosition( jointPositions[i] )
            else:
                guide.setPosition(jointPositions[i])




