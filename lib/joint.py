'''

joint class

'''

import maya.cmds as cmds
import maya.api.OpenMaya as om
import mayaBaseObject as mbo
import nameSpace
import util
import control

reload(mbo)


class Joint(mbo.MayaBaseObject):

    def __init__(self, name=None, position=(0, 0, 0), parent=None):
        super(Joint, self).__init__(name, position)
        self.nameType = nameSpace.JOINT
        self.name = name
        self.position = position
        self.parent = parent

    def create(self):
        # self.format_name()
        cmds.joint(n=self.name, p=self.position)

    def orientToRotate(self):
        ori = cmds.xform(self.getName(), q=True, ws=True, ro=True)
        cmds.setAttr("{0}.jo".format(self.getName()), 0, 0, 0)
        cmds.xform(self.getName(), ws=True, ro=ori)

    def rotateToOrient(self):
        self.orientToRotate()
        rot = cmds.getAttr( "{0}.r".format( self.getName() ) )
        cmds.setAttr("{0}.jo".format(self.getName()), rot[0][0], rot[0][1], rot[0][2])
        cmds.setAttr("{0}.r".format(self.getName()), 0, 0, 0)

    def orientJoint(self, downAxis, upDown):
        for arg in [downAxis, upDown]:
            if not isinstance(arg, basestring):
                error = "{0} is not of type string."
                return RuntimeError(error.format(arg))
        try:
            cmds.joint(self.name, e=True, oj=downAxis, sao=upDown)
        except:
            a = "First arg should be xyz|yzx|zxy|zyx|yxz|xzy|none."
            b = " Second arg should be xup|xdown|yup|ydown|zup|zdown|none."
            return RuntimeWarning(a + b)

    @classmethod
    def fkChain(cls, joints):

        # given some joints, creates a very primitive FK chain
        # returns list of controls for chain as Control instances

        if not isinstance(joints, list):
            err = "Couldn't create a chain with {0} because it's not a list."
            raise RuntimeError(err.format(joints))
            return

        joints = [j for j in joints if cmds.nodeType(j) == 'joint']
        cons = []
        par = None

        for j in joints:
            con = control.Control(name=j, align_to=j)
            con.create()

            if par is not None:
                con.setParent(par.getName())

            con.drive_parented(j)
            cons.append(con)
            par = con

        return cons
