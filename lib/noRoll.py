#NoRoll Class

#NoRoll will just duplicate given joints and create an ikh with 0,0,0 pole vector direction
#It is meant to be built off an existing set up


import maya.cmds as cmds
from autorigger.lib import nameSpace
from autorigger.lib import control
from autorigger.lib import joint
from autorigger.lib import locator

reload(nameSpace)
reload(control)
reload(joint)
reload(locator)

class Noroll(object) :

    def __init__( self, name, joint1, joint2):

        self.name = name
        self.oldJoint1 = joint1
        self.oldJoint2 = joint2

        self.dupJoint1 = "{0}_noroll1".format( self.oldJoint1 )
        self.dupJoint2 = "{0}_noroll2".format( self.oldJoint2 )

        self.ik = "{0}_norollIk".format( self.name )
        self.jointList = [ self.dupJoint1, self.dupJoint2 ]

    def getIk(self):
        return self.ik

    def getJoint(self, index):
        return self.jointList[index]

    def getNorollJnt1(self):
        return self.dupJoint1

    def getNorollJnt2(self):
        return self.dupJoint2

    def setup(self):

        #duplicate given joints
        cmds.duplicate( self.oldJoint1, n=self.dupJoint1, po=True )
        cmds.duplicate( self.oldJoint2, n=self.dupJoint2, po=True)
        cmds.parent( self.dupJoint2, self.dupJoint1 )
        cmds.parent(self.dupJoint1, w=True)

        #create rp ik
        ik = cmds.ikHandle(sol='ikRPsolver', sj=self.dupJoint1, ee=self.dupJoint2, n=self.ik)[0]
        #zero pole vectors
        cmds.setAttr("{0}.poleVectorX".format(self.ik), 0)
        cmds.setAttr("{0}.poleVectorY".format(self.ik), 0)
        cmds.setAttr("{0}.poleVectorZ".format(self.ik), 0)

        #parent to bindJoint
        cmds.select( self.oldJoint1)
        clav = cmds.pickWalk(d='Up')
        cmds.parent( self.ik, self.oldJoint1)
        cmds.parent( self.dupJoint1, clav )

        #hide ik
        cmds.setAttr( '{0}.v'.format(ik), 0 )

    def twistReader(self, name, joint, noroll, aim, wuo ):
        #create a twist evaluator that happens at the elbow
        twistReader = cmds.duplicate( joint,
                                      po=True,
                                      n='{0}_twistReader_jnt'.format(name) )[0]

        cmds.parent( twistReader, noroll)
        cmds.setAttr( '{0}.radius'.format(twistReader), 4)
        #aim that mother fucker
        cmds.select(cl=True)
        cmds.aimConstraint( aim, twistReader,
                            wut='objectrotation', wuo=wuo,
                            aim=(1,0,0), u=(0,1,0))

        return twistReader
