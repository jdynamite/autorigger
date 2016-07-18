'''

ik fk library for all ik fk setups

wishlist: separate ik and fk procedures

'''

import maya.cmds as cmds
import maya.OpenMaya as om
from autorigger.lib import wrappers
from autorigger.lib import joint
from autorigger.lib import nameSpace

reload(wrappers)
reload(joint)
reload(nameSpace)


class Ikfk(object):
    def __init__(self, originalJoints):
        '''Initialize method
        :param originalJoints: Joints to build ik/fk system on
        :type originalJoints: list or tuple
        '''

        if not isinstance(originalJoints, list) and not isinstance(originalJoints, tuple):
            raise TypeError(
                "{0} is not of type list or tuple.".format(orignalJoints))

        # Declare class members

        self._originalJoints = originalJoints
        self._ikHandle = str()
        self._group = str()
        self._fkJoints = list()
        self._ikJoints = list()
        self._blendJoints = list()

    def getOriginalJoints(self):
        return self._originalJoints

    def getFkJoints(self):
        return self._fkJoints

    def getIkJoints(self):
        return self._ikJoints

    def getBlendJoints(self):
        return self._blendJoints

    def getHandle(self):
        return self._ikHandle

    def getGroup(self):
        return self._group

    def getIkHandle(self):
        return self._ikHandle

    def setOriginalJoints(self, value):
        if not isinstance(originalJoints, list) and not isinstance(originalJoints, tuple):
            raise TypeError(
                "{0} is not of type list or tuple".format(originalJoints))

        for jnt in value:
            if not cmds.objExists(jnt):
                raise RuntineError(
                    "{0} does not exist in your currect scene".format(jnt))

        self._originalJoints = value

    def setFkJoints(self, value):
        if not isinstance(value, list) and not isinstance(value, tuple):
            raise TypeError("{0} is not of type list or tuple".format(value))

        for jnt in value:
            if not cmds.objExists(jnt):
                raise RuntineError(
                    "{0} does not exist in your currect scene".format(jnt))

        self._fkJoints = value

    def setIkJoints(self, value):
        if not isinstance(value, list) and not isinstance(value, tuple):
            raise TypeError("{0} is not of type list or tuple".format(v))

        for jnt in value:
            if not cmds.objExists(jnt):
                raise RuntineError(
                    "{0} does not exist in your currect scene".format(jnt))

        self._ikJoints = value

    def setBlendJoints(self, value):
        if not isinstance(value, list) and not isinstance(value, tuple):
            raise TypeError("{0} is not of type list or tuple".format(value))

        for jnt in value:
            if not cmds.objExists(jnt):
                raise RuntineError(
                    "{0} does not exist in your currect scene".format(jnt))

        self._blendJoints = value

    def setGroup(self, value):
        if not isinstance(value, basestring):
            raise TypeError("{0} is not of type str or unicode.".format(value))

        if not cmds.objExists(value):
            raise RuntimeError(
                "{0} does not exist in your currecnt scene".formant(value))

        self._group = value

    def setHandle(self, value):
        self._ikHandle = value

    def create(self):
        '''
        This creates our ikfk blend joints and group!
        '''
        # fix this later
        groupNull = self.setGroup(cmds.group(em=True, n="ikfk_grp"))
        cmds.addAttr(ln="ikfk", at="float", min=0, max=1, k=True)
        ikfkAttr = "{0}.ikfk".format(self.getGroup())

        # FK joints
        parent = self.getGroup()
        fkJnts = list()
        for jnt in self.getOriginalJoints():
            cmds.select(cl=True)
            fkJnt = wrappers.duplicateJoint(jnt, "{0}_fk".format(
                jnt.replace(nameSpace.BINDJOINT, nameSpace.JOINT)))
            cmds.parent(fkJnt.getName(), parent)
            fkJnts.append(fkJnt.getName())
            parent = fkJnt.getName()

        self.setFkJoints(fkJnts)

        # IK joints
        parent = self.getGroup()
        ikJnts = list()
        for jnt in self.getOriginalJoints():
            cmds.select(cl=True)
            ikJnt = wrappers.duplicateJoint(jnt, "{0}_ik".format(
                jnt.replace(nameSpace.BINDJOINT, nameSpace.JOINT)))
            cmds.parent(ikJnt.getName(), parent)
            ikJnts.append(ikJnt.getName())
            parent = ikJnt.getName()

        self.setIkJoints(ikJnts)

        # blend joints
        parent = self.getGroup()
        blendJnts = list()
        for i, jnt in enumerate(self.getOriginalJoints()):
            cmds.select(cl=True)
            blendJnt = wrappers.duplicateJoint(jnt, "{0}_blend".format(
                jnt.replace(nameSpace.BINDJOINT, nameSpace.JOINT)))
            # create blend nodes
            bcTrnNode = cmds.createNode(
                "blendColors", n="{0}_trnbcn".format(blendJnt.getName()))
            bcRotNode = cmds.createNode(
                "blendColors", n="{0}_rotbcn".format(blendJnt.getName()))
            bcSclNode = cmds.createNode(
                "blendColors", n="{0}_sclbcn".format(blendJnt.getName()))

            # translation
            cmds.connectAttr('{0}.t'.format(self.getIkJoints()[
                             i]), ('{0}.color1'.format(bcTrnNode)), f=True)
            cmds.connectAttr('{0}.t'.format(self.getFkJoints()[
                             i]), ('{0}.color2'.format(bcTrnNode)), f=True)

            # rotation
            cmds.connectAttr('{0}.r'.format(self.getIkJoints()[
                             i]), ('{0}.color1'.format(bcRotNode)), f=True)
            cmds.connectAttr('{0}.r'.format(self.getFkJoints()[
                             i]), ('{0}.color2'.format(bcRotNode)), f=True)

            # scale
            cmds.connectAttr('{0}.s'.format(self.getIkJoints()[
                             i]), ('{0}.color1'.format(bcSclNode)), f=True)
            cmds.connectAttr('{0}.s'.format(self.getFkJoints()[
                             i]), ('{0}.color2'.format(bcSclNode)), f=True)

            cmds.parent(blendJnt.getName(), parent)

            cmds.connectAttr('{0}.output'.format(bcTrnNode),
                             '{0}.t'.format(blendJnt.getName(), f=True))
            cmds.connectAttr('{0}.output'.format(bcRotNode),
                             '{0}.r'.format(blendJnt.getName(), f=True))
            cmds.connectAttr('{0}.output'.format(bcSclNode),
                             '{0}.s'.format(blendJnt.getName(), f=True))

            # connect IKFK attribute to blend colors
            cmds.connectAttr(ikfkAttr, "{0}.blender".format(bcTrnNode), f=True)
            cmds.connectAttr(ikfkAttr, "{0}.blender".format(bcRotNode), f=True)
            cmds.connectAttr(ikfkAttr, "{0}.blender".format(bcSclNode), f=True)

            blendJnts.append(blendJnt.getName())
            parent = blendJnt.getName()

        self.setBlendJoints(blendJnts)
        # show blend joints
        cmds.setAttr("{0}.visibility".format(blendJnt.getName()), 1)
        '''
    #blendJoints connected to bindJoints
        #translates
        cmds.connectAttr("{0}.t".format(self.getBlendJoints()[0]),"{0}.t".format(self.getOriginalJoints()[0]))
        cmds.connectAttr("{0}.t".format(self.getBlendJoints()[1]),"{0}.t".format(self.getOriginalJoints()[1]))
        cmds.connectAttr("{0}.t".format(self.getBlendJoints()[2]),"{0}.t".format(self.getOriginalJoints()[2]))
        #rotates
        cmds.connectAttr("{0}.r".format(self.getBlendJoints()[0]),"{0}.r".format(self.getOriginalJoints()[0]))
        cmds.connectAttr("{0}.r".format(self.getBlendJoints()[1]),"{0}.r".format(self.getOriginalJoints()[1]))
        cmds.connectAttr("{0}.r".format(self.getBlendJoints()[2]),"{0}.r".format(self.getOriginalJoints()[2]))
        #scalez
        cmds.connectAttr("{0}.scale".format(self.getBlendJoints()[0]),"{0}.scale".format(self.getOriginalJoints()[0]))
        cmds.connectAttr("{0}.scale".format(self.getBlendJoints()[1]),"{0}.scale".format(self.getOriginalJoints()[1]))
        cmds.connectAttr("{0}.scale".format(self.getBlendJoints()[2]),"{0}.scale".format(self.getOriginalJoints()[2]))
        '''

    # This is a decorator. it pulls this out of the method even though it's in
    # it
    @staticmethod
    def createIkHandle(name, startJoint, endJoint, _type='ikRPsolver'):
        ikHandle = cmds.ikHandle(
            n=name, sj=startJoint, ee=endJoint, sol=_type)[0]
        return ikHandle


class LimbIkFk(Ikfk):
    # *args takes in a list, and **kwargs a dictionary
    def __init__(self, originalJoints):
        if not len(originalJoints) == 3:
            raise RuntimeError(
                "{0} must contain only 3 joints".format(originalJoints))
        super(LimbIkFk, self).__init__(originalJoints)

        self._ikHandle = str()

    def getPoleVectorPosition(self, distance=3):
        # position
        origJoints = self.getOriginalJoints()
        startJntPos = cmds.xform(self.getOriginalJoints()[
                                 0], q=True, ws=True, t=True)
        middleJntPos = cmds.xform(self.getOriginalJoints()[
                                  1], q=True, ws=True, t=True)
        endJntPos = cmds.xform(self.getOriginalJoints()[
                               2], q=True, ws=True, t=True)

        print self.getOriginalJoints()[0]

        # vectors
        startJntVector = om.MVector(*startJntPos)
        middleJntVector = om.MVector(*middleJntPos)
        endJntVector = om.MVector(*endJntPos)

        originVector = (endJntVector - startJntVector) / 2
        halfVector = originVector + startJntVector
        pvDirection = (middleJntVector - halfVector) * distance
        pvVector = (pvDirection + halfVector)
        return (pvVector.x, pvVector.y, pvVector.z)

    def create(self):
        super(LimbIkFk, self).create()
        ikJoints = self.getIkJoints()
        self.setHandle(self.createIkHandle("{0}_{1}".format(
            ikJoints[-1], nameSpace.HANDLE), ikJoints[0], ikJoints[-1]))
