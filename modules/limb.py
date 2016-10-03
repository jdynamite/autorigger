'''
Limb Class
'''

'''
Limb Class
'''
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


# limb inherits a bit from IkfkLimb
class Limb(part.Part):
    def __init__(self, name, positions=([2, 5, 0], [7, 5, -2], [12, 5, 0]), jointAmmount=3, mirror=True):
        super(Limb, self).__init__(name)

        '''
        # this is just strings of joint names
        self.startJoint = joint.Joint("{0}_upLimb_{1}".format(
            self.getSide(), nameSpace.BINDJOINT))
        self.middleJoint = joint.Joint(
            "{0}_loLimb_{1}".format(self.getSide(), nameSpace.BINDJOINT))
        self.endJoint = joint.Joint("{0}_endLimb_{1}".format(
            self.getSide(), nameSpace.BINDJOINT))
        '''

        self.positions = positions

        # this sets up the ribbon master group
        self.ribbonMasterGroup = "{0}_rbn_master_grp".format(name)

        # group that allows scale for stretch rig
        self.scaleStretchGroup = "{0}_distance_grp".format(self.getName())

        self.mirror = mirror

        # load necessary plugins
        util.isPluginLoaded('matrixNodes')

    def setup(self):
        super(Limb, self).setup()

        # place guides
        self.placeGuides( self.positions )


        cmds.select(cl=True)

    def postSetup(self):
        super(Limb, self).postSetup()
        pass

    def preBuild(self):
        super(Limb, self).preBuild()
        pass

    def build(self):
        super(Limb, self).build()

        self.ikfkSystem = ikfk.LimbIkFk([
            self.joints[0],
            self.joints[1],
            self.joints[2]
        ])
        self.ikfkSystem.create()

        #get jointNames
        self.ikJoints = self.ikfkSystem.getIkJoints()
        fkJoints = self.ikfkSystem.getFkJoints()
        ikHandle = self.ikfkSystem.getHandle()
        self.ikfkGroup = self.ikfkSystem.getGroup()

        cmds.parent(self.ikfkGroup, self.jointsGroup)
        ###########################################################
        ###
        ###########################################################

        # create pole vector control
        self.createPv()
        # ik ctrl creation
        self.createIk(ikHandle)
        # fk ctrl Creation
        self.createFk(fkJoints)

        # setup stretch on ik
        self.currentDist = self.currentLimbDistSetup()

        # currentDist is the return of currentDist attr
        self.createStretchyIk( self.currentDist )

        # noroll
        self.noRollSetup()

        # close selection before exiting, just to be safe
        cmds.select(cl=True)

    def postBuild(self):
        super(Limb, self).postBuild()

        if cmds.objExists(self.ikfkSystem.getHandle()):
            cmds.setAttr("{0}.v".format(self.ikfkSystem.getHandle()), 0)

        # hide fk, ik, and blend joints.
        for jnt in self.ikfkSystem.getBlendJoints():
            cmds.setAttr("{0}.visibility".format(jnt), 1)
        for jnt in self.ikfkSystem.getIkJoints():
            cmds.setAttr("{0}.visibility".format(jnt), 0)
        for jnt in self.ikfkSystem.getFkJoints():
            cmds.setAttr("{0}.visibility".format(jnt), 0)

        # delete bind joints
        # cmds.delete(self.joints[0])

#####################################################
# Additional Modules for cleaner code
#####################################################

    def createPv(self):

        # pv control init
        pvCtrl = control.Control(
            "{0}_{1}_{2}".format(self.getName(), nameSpace.POLEVECTOR, nameSpace.CONTROL),
            self.ikfkSystem.getPoleVectorPosition(),
            self.controlsGroup,
            "cross"
        )

        #pv control creation
        pvCtrl.create()
        pvCtrl.setColor(self.getColor())

        #set position
        pvCtrl.setPosition(self.ikfkSystem.getPoleVectorPosition())
        cmds.poleVectorConstraint(
            pvCtrl.getName(),
            self.ikfkSystem.getHandle()
        )

        cmds.parent(pvCtrl.getNull(), self.controlsGroup)

        #return pv
        return pvCtrl.getName()

    def createIk(self, ikHandle):
        '''
        ~ikHandle is the ikHandle we call with self.ikfkSystem.getHandle()
        ~self.ikJoints[-1] is the last joint of the ikJointChain. This is solo'ed out because it will be oriented
         to the ik control
        '''

        ikName = "{0}_{1}_{2}".format(self.getName(), nameSpace.IK, nameSpace.CONTROL)
        ikPosition = cmds.xform(self.ikJoints[-1], q=True, ws=True, t=True)



        self.ikCtrl = control.Control(
            ikName,
            ikPosition,
            self.controlsGroup,
            shape="sphere"
        )

        #position input aren't kicking in, so doing this should work


        self.ikCtrl.create()
        self.ikCtrl.setColor(self.getColor())
        self.ikCtrl.setPosition( self.ikCtrl.getPosition() )

        cmds.parent(ikHandle, self.ikCtrl.getName())
        cmds.orientConstraint(self.ikCtrl.getName(), self.ikJoints[-1], mo=True)


        # add ikfk switch attr to ikhandle
        cmds.select(self.ikCtrl.getName())
        cmds.addAttr(ln="ikfk", at="float", min=0, max=1, k=True)
        cmds.connectAttr(
            "{0}.ikfk".format(self.ikCtrl.getName()),
            "{0}.ikfk".format(self.ikfkSystem.getGroup()),
             f=True
        )

        # rename the self.ikfkGroup so it's just no self.ikfkGroup and actually has a
        # part inclued in the name
        cmds.rename(
            self.ikfkGroup,
            "{0}_{1}".format(self.getName(), self.ikfkGroup)
        )

        cmds.parent(self.ikCtrl.getNull(), self.controlsGroup)

    def createFk(self, fkJoints):
        '''
        fkJoints: input list of fkJoints
        '''
        fkCtrls = list()

        parent = self.controlsGroup

        for jnt in fkJoints:

            fkCtrl = control.Control(
                "{0}_{1}".format(jnt, nameSpace.CONTROL),
                cmds.xform(jnt, q=True, ws=True, t=True),
                parent,
                "circle"
            )

            # control creation
            fkCtrl.create()
            # set color control
            fkCtrl.setColor(self.getColor())
            # set position
            fkCtrl.setPosition( fkCtrl.getPosition() )


            ctrlName = fkCtrl.getName()
            # get worldSpace orientation of joint
            rot = cmds.xform(jnt, q=True, ws=True, ro=True)
            # orient the null of the fkCtrl to match the joint
            cmds.xform(fkCtrl.null, ws=True, ro=rot)
            # snap fkCtrl
            cmds.parentConstraint(ctrlName, jnt)
            # cmds.scaleConstraint(ctrlName, jnt)

            # Don't scale constraint because it changes the values of scale when nodes above the hierarchy
            # scale. And that is causing problems.
            # instead we do a direct connection! *Bowser laugh*
            cmds.connectAttr(
                "{0}.scale".format(ctrlName),
                "{0}.scale".format(jnt))


            cmds.parent(fkCtrl.getNull(), parent)
            parent = ctrlName

            # stash this iteration of fkCtrl into list fkCtrls
            fkCtrls.append(fkCtrl)
            # reorient CVs if needed
            curve.reorient(fkCtrl.getName(), self.strAimAttr)

        # mid ctrl (elbow or knee)
        elbowCtrlName = "{0}_mid_{1}".format(self.getName(),nameSpace.CONTROL)
        self.elbowCtrl = control.Control(
            elbowCtrlName,
            [0, 0, 0],
            shape="star"
        )

        self.elbowCtrl.create()
        self.elbowCtrl.setColor(17)
        self.elbowCtrl.setPosition( self.elbowCtrl.getPosition() )

        # snap self.elbowCtrl to elbowJoint
        cmds.pointConstraint(
            self.ikfkSystem.getBlendJoints()[1],
            self.elbowCtrl.null
        )

        # the high rotation values are causing flipping issues
        # so turn on the no flip as a quick fix
        cmds.orientConstraint(
            self.ikfkSystem.getBlendJoints()[0],
            self.ikfkSystem.getBlendJoints()[1],
            self.elbowCtrl.null
        )

        # parent to ctrl group
        cmds.parent(
            self.elbowCtrl.null,
            self.controlsGroup
        )

        # reorient CVs if need be
        curve.reorient(self.elbowCtrl.getName(), self.strAimAttr)

    def currentLimbDistSetup(self):
        # limbDist is created for scale reasons.
        # this creates a node network to keep
        # track of the distance of limbs even if they are bent.

        # create Stretch attribute from 0-1
        cmds.select(self.ikCtrl.getName())
        cmds.addAttr(ln="stretch", at="float", min=0, max=1, k=True)

        #########################################################################
        # create a 2nd dist chain (total distance) to make our stretch rig scalable
        # total distance meaning, get the distance even if limb is bent
        ###################################################################

        # create 2 distance nodes
        hiLimbDistNode = cmds.createNode(
            'distanceBetween',
            name=("{0}_hiLimb_CRNT_distBtwn").format(self.getName())
        )

        loLimbDistNode = cmds.createNode(
            'distanceBetween',
            name=("{0}_loLimb_CRNT_distBtwn").format(self.getName())
        )

        self.limbDistNodes = {
            "hiLimb": hiLimbDistNode,
            "loLimb": loLimbDistNode
        }

        # loc creation for distNodes
        self.hiLimbDistLoc1 = "{0}_hiLimbDist1_CRNT_{1}".format(self.getName(), nameSpace.LOCATOR)
        self.hiLimbDistLoc2 = "{0}_hiLimbDist2_CRNT_{1}".format(self.getName(), nameSpace.LOCATOR)
        self.loLimbDistLoc1 = "{0}_loLimbDist1_CRNT_{1}".format(self.getName(), nameSpace.LOCATOR)
        self.loLimbDistLoc2 = "{0}_loLimbDist2_CRNT_{1}".format(self.getName(), nameSpace.LOCATOR)
        cmds.spaceLocator(n=self.hiLimbDistLoc1)
        cmds.spaceLocator(n=self.hiLimbDistLoc2)
        cmds.spaceLocator(n=self.loLimbDistLoc1)
        cmds.spaceLocator(n=self.loLimbDistLoc2)

        # snap the limbDistLocs
        cmds.delete(cmds.pointConstraint(self.ikJoints[0], self.hiLimbDistLoc1))
        cmds.delete(cmds.pointConstraint(self.ikJoints[1], self.hiLimbDistLoc2))
        cmds.delete(cmds.pointConstraint(self.ikJoints[1], self.loLimbDistLoc1))
        cmds.delete(cmds.pointConstraint(self.ikJoints[2], self.loLimbDistLoc2))

        # create a group for these limbDistLoc
        cmds.createNode("transform", n=self.scaleStretchGroup)
        cmds.parent(
            self.hiLimbDistLoc1,
            self.hiLimbDistLoc2,
            self.loLimbDistLoc1,
            self.loLimbDistLoc2,
            self.scaleStretchGroup
        )

        # hide them
        cmds.setAttr("{0}.visibility".format(self.scaleStretchGroup), 0)

        # create matrix nodes for ws purposes
        hiLimbDcmpMtx1 = cmds.createNode(
            'decomposeMatrix',
            name=("{0}_hilimbDecomposeMatrix1").format(self.getName())
        )

        hiLimbDcmpMtx2 = cmds.createNode(
            'decomposeMatrix',
            name=("{0}_hilimbDecomposeMatrix2").format(self.getName())
        )

        loLimbDcmpMtx1 = cmds.createNode(
            'decomposeMatrix',
            name=("{0}_lolimbDecomposeMatrix1").format(self.getName())
        )
        loLimbDcmpMtx2 = cmds.createNode(
            'decomposeMatrix',
            name=("{0}_lolimbDecomposeMatrix2").format(self.getName())
        )

        # connect locs to martix
        cmds.connectAttr(
            "{0}.worldMatrix[0]".format(self.hiLimbDistLoc1),
            "{0}.inputMatrix".format(hiLimbDcmpMtx1)
        )
        cmds.connectAttr(
            "{0}.worldMatrix[0]".format(self.hiLimbDistLoc2),
            "{0}.inputMatrix".format(hiLimbDcmpMtx2)
        )
        cmds.connectAttr(
            "{0}.worldMatrix[0]".format(self.loLimbDistLoc1),
            "{0}.inputMatrix".format(loLimbDcmpMtx1)
        )
        cmds.connectAttr(
            "{0}.worldMatrix[0]".format(self.loLimbDistLoc2),
            "{0}.inputMatrix".format(loLimbDcmpMtx2)
        )

        # connect the dcmp to distanceBetweens
        # hiLimb
        cmds.connectAttr(
            "{0}.outputTranslate".format(hiLimbDcmpMtx1),
            "{0}.point1".format(hiLimbDistNode)
        )
        cmds.connectAttr(
            "{0}.outputTranslate".format(hiLimbDcmpMtx2),
            "{0}.point2".format(hiLimbDistNode)
        )

        # loLimb
        cmds.connectAttr(
            "{0}.outputTranslate".format(loLimbDcmpMtx1),
            "{0}.point1".format(loLimbDistNode)
        )

        cmds.connectAttr(
            "{0}.outputTranslate".format(loLimbDcmpMtx2),
            "{0}.point2".format(loLimbDistNode)
        )

        # totalDistance
        self.limbTotalDist = cmds.createNode(
            'plusMinusAverage',
            n="{0}_totalDist_PMA".format(self.getName())
        )

        # connect hilimb and lolimb distance to total
        cmds.connectAttr(
            "{0}.distance".format(hiLimbDistNode),
            "{0}.input1D[0]".format(self.limbTotalDist)
        )
        cmds.connectAttr(
            "{0}.distance".format(loLimbDistNode),
            "{0}.input1D[1]".format(self.limbTotalDist)
        )

        # finally, parent group to master
        cmds.parent(self.scaleStretchGroup, self.group)

        return self.limbTotalDist

    def createStretchyIk(self, currentDist):
        # the Actual stretching rig set up
        # build distanceBetween Node
        distanceNode = ("{0}_distBtwn").format(self.getName())
        cmds.createNode(
            'distanceBetween',
            name= distanceNode
        )

        # create 2 locators for distBtwn
        self.distLoc1 = "{0}_distLoc1".format(self.getName())
        self.distLoc2 = "{0}_distLoc2".format(self.getName())
        cmds.spaceLocator(n=self.distLoc1)
        cmds.spaceLocator(n=self.distLoc2)

        # snap them in place
        cmds.delete( cmds.pointConstraint(self.ikJoints[0], self.distLoc1) )
        cmds.delete( cmds.pointConstraint(self.ikJoints[2], self.distLoc2) )

        # create decompose Matrix Nodes
        dcmpMtx1 = cmds.createNode(
            'decomposeMatrix',
            name=("{0}_decomposeMatrix1").format(self.getName())
        )

        dcmpMtx2 = cmds.createNode(
            'decomposeMatrix',
            name=("{0}_decomposeMatrix2").format(self.getName())
        )

        # connect ikJoints to decomposeMatrix
        cmds.connectAttr(
            "{0}.worldMatrix[0]".format(self.distLoc1),
            "{0}.inputMatrix".format(dcmpMtx1)
        )

        cmds.connectAttr(
            "{0}.worldMatrix[0]".format(self.distLoc2),
            "{0}.inputMatrix".format(dcmpMtx2)
        )

        # connect decomposeMatrixes to distanceBetween
        cmds.connectAttr(
            "{0}.outputTranslate".format(dcmpMtx1),
            "{0}.point1".format(distanceNode)
        )

        cmds.connectAttr(
            "{0}.outputTranslate".format(dcmpMtx2),
            "{0}.point2".format(distanceNode)
        )

        # create MDN node
        mdn = cmds.createNode(
            'multiplyDivide',
            n=("{0}_stretchMdn").format(self.getName())
        )

        # set mdn to divide
        cmds.setAttr("{0}.operation".format(mdn), 2)

        # connect Distance to mdn input 1
        cmds.connectAttr(
            "{0}.distance".format(distanceNode),
            "{0}.input1X".format(mdn)
        )

        # connect currentLimbDistSetup to input 2
        cmds.connectAttr(
            "{0}.output1D".format(currentDist),
            "{0}.input2X".format(mdn)
        )

        # create condition node
        cnd = cmds.createNode(
            'condition',
            n="{0}_cnd".format(self.getName())
        )

        # set CND attrs
        cmds.connectAttr(
            "{0}.distance".format(distanceNode),
            "{0}.firstTerm".format(cnd)
        )

        cmds.connectAttr(
            "{0}.output1D".format(self.limbTotalDist),
            "{0}.secondTerm".format(cnd)
        )

        cmds.setAttr("{0}.operation".format(cnd), 3)
        cmds.connectAttr(
            "{0}.outputX".format(mdn),
            "{0}.colorIfTrueR".format(cnd)
        )

        # create blendNode
        blnd = cmds.createNode('blendColors', n="{0}_blnd")

        cmds.connectAttr(
            "{0}.stretch".format(self.ikCtrl.getName()),
            "{0}.blender".format(blnd)
        )

        cmds.connectAttr(
            "{0}.outColorR".format(cnd),
            "{0}.color1R".format(blnd)
        )

        cmds.setAttr("{0}.color2R".format(blnd), 1)

        # connect to down Axis
        cmds.connectAttr(
            "{0}.outputR".format(blnd),
            "{0}.s{1}".format(self.ikJoints[0], self.downAxis)
        )
        cmds.connectAttr(
            "{0}.outputR".format(blnd),
            "{0}.s{1}".format(self.ikJoints[1], self.downAxis)
        )

        # hide distLocs
        cmds.setAttr("{0}.visibility".format(self.distLoc1), 0)
        cmds.setAttr("{0}.visibility".format(self.distLoc2), 0)

        # slip into hierarchy
        cmds.parent( self.distLoc1, self.joints[0])
        cmds.parent( self.distLoc2, self.ikCtrl.getName())

    def noRollSetup(self):
        # spline twist bind joints setup

        # create no roll for hiLimb
        hiNoroll = noRoll.Noroll(
            '{0}up_noroll'.format(self.getName()),
            self.ikfkSystem.getBlendJoints()[0],
            self.ikfkSystem.getBlendJoints()[1]
        )

        hiNoroll.setup()
        cmds.select(cl=True)

        # create uplimb spline
        startPos = cmds.xform(self.joints[0], q=1, ws=1, t=1)
        endPos = cmds.xform(self.joints[1], q=1, ws=1, t=1)

        upSpline = spline.Spline(
            '{0}up'.format(self.getName()),
            startJointDupe=self.ikfkSystem.getBlendJoints()[0],
            endJointDupe=self.ikfkSystem.getBlendJoints()[1]
        )

        print self.ikfkGroup

        upSpline.setup()
        upSpline.buildControls()

        # create no roll for loLimb
        loNoroll = noRoll.Noroll(
            '{0}lo_noroll'.format(self.getName()),
             self.ikfkSystem.getBlendJoints()[1],
             self.ikfkSystem.getBlendJoints()[2]
        )
        loNoroll.setup()

        # Create twist readers/evaluators before creating lolimb setup
        # create a twist evaluator that happens at the elbow

        twistReader = hiNoroll.twistReader(
            self.getName(),
            loNoroll.getJoint(0),
            hiNoroll.getNorollJnt2(),
            self.ikfkSystem.getBlendJoints()[2],
            self.ikfkSystem.getBlendJoints()[1]
        )

        # spline twists for upSpline
        upSpline.setWorldUpObjectStart(hiNoroll.getJoint(0))
        upSpline.setWorldUpObjectEnd(twistReader)

        # create an extra joint for the wrist twist reader
        wristTwistReader2 = cmds.duplicate(
            self.ikfkSystem.getBlendJoints()[2],
            po=True,
            n='{0}_wTwist2'.format(self.getName())
        )[0]
        cmds.parent(wristTwistReader2, self.ikfkSystem.getBlendJoints()[2])
        cmds.setAttr('{0}.tx'.format(wristTwistReader2), 1)

        # create a wrist noroll
        wristNoroll = noRoll.Noroll(
            '{0}wrist_noroll'.format(self.getName()),
            self.ikfkSystem.getBlendJoints()[2],
            wristTwistReader2
        )
        wristNoroll.setup()

        # create a twist reader for the wrist // name, joint, noroll, aim, wuo
        wristTwistReader = loNoroll.twistReader(
            'wrist_{0}'.format(self.getName()),
            self.ikfkSystem.getBlendJoints()[2],
            loNoroll.getNorollJnt2(),
            wristNoroll.getNorollJnt2(),
            self.ikfkSystem.getBlendJoints()[2]
        )
        cmds.delete(wristTwistReader2)

        cmds.parent(wristTwistReader, wristNoroll.getNorollJnt1())
        cmds.select(cl=True)

        ################################
        # lolimb
        ################################
        loSpline = spline.Spline(
            '{0}lo'.format(self.getName()),
            startJointDupe=self.ikfkSystem.getBlendJoints()[1],
            endJointDupe=self.ikfkSystem.getBlendJoints()[2]
        )
        loSpline.setup()
        loSpline.setWorldUpObjectStart(twistReader)
        loSpline.setWorldUpObjectEnd(wristTwistReader)
        loSpline.buildControls()

        # for some reason, the wristReader only works after being updated.
        # so update it
        cmds.select(cl=True)
        cmds.select(loSpline.getSplineIk())
        cmds.select(cl=True)

        # do not parent curve to first blend joint
        cmds.select(upSpline.getSplineCurve())
        cmds.parent(w=True)
        cmds.select(loSpline.getSplineCurve())
        cmds.parent(w=True)

        # parentConstraint spline controls to limb ctrls
        cmds.parentConstraint(self.elbowCtrl.getName(), upSpline.getEndCtrl())
        cmds.parentConstraint(self.elbowCtrl.getName(), loSpline.getStartCtrl())
        cmds.parentConstraint(hiNoroll.getJoint(0), upSpline.getStartCtrl())

        # and wrist spline ctrl to wristBlend joint
        cmds.parentConstraint(
            self.ikfkSystem.getBlendJoints()[2],
            loSpline.getEndCtrl()
        )

        # rename all spline joints as bind joints
        for joint in upSpline.getJoint():
            newName = joint.replace(nameSpace.SPLINE, nameSpace.BINDJOINT)
            cmds.rename(joint, newName)

        for joint in loSpline.getJoint():
            newName = joint.replace(nameSpace.SPLINE, nameSpace.BINDJOINT)
            cmds.rename(joint, newName)

        # clean up
        # move respective nodes to noXform group
        cmds.parent(upSpline.getSplineCurve(), self.noXformGroup)
        cmds.parent(loSpline.getSplineCurve(), self.noXformGroup)
        cmds.parent(upSpline.getSplineIk(), self.noXformGroup)
        cmds.parent(loSpline.getSplineIk(), self.noXformGroup)

        cmds.parent(upSpline.getStartCtrlZero(), self.noXformGroup)
        cmds.parent(upSpline.getMidCtrlZero(), self.noXformGroup)
        cmds.parent(upSpline.getEndCtrlZero(), self.noXformGroup)
        cmds.parent(loSpline.getStartCtrlZero(), self.noXformGroup)
        cmds.parent(loSpline.getMidCtrlZero(), self.noXformGroup)
        cmds.parent(loSpline.getEndCtrlZero(), self.noXformGroup)



        # hide things animators don't need to be looking at because they're ugly
        # ik handles
        cmds.setAttr('{0}.v'.format(upSpline.getSplineIk()), 0)
        cmds.setAttr('{0}.v'.format(loSpline.getSplineIk()), 0)
        # spline Ctrls
        cmds.setAttr('{0}.v'.format(upSpline.getStartCtrlZero()), 0)
        cmds.setAttr('{0}.v'.format(upSpline.getEndCtrlZero()), 0)
        cmds.setAttr('{0}.v'.format(loSpline.getStartCtrlZero()), 0)
        cmds.setAttr('{0}.v'.format(loSpline.getEndCtrlZero()), 0)

        # connect global scales
        cmds.connectAttr(
            "{0}.distance".format(self.limbDistNodes["hiLimb"]),
            "{0}.input2X".format( upSpline.getMdn() )
        )

        cmds.connectAttr(
            "{0}.distance".format(self.limbDistNodes["loLimb"]),
            "{0}.input2X".format(loSpline.getMdn())
        )