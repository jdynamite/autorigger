'''

joint class

'''

import maya.cmds as cmds
import maya.api.OpenMaya as om
import mayaBaseObject as mbo
import nameSpace
import util

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

    # just freezes transform. Looks fancy but under the hood it's not
    def orientToRotate(self):
        cmds.makeIdentity(self.getName(), apply=True, rotate=True)

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
