'''
fkChain Class

Future development: Make spine class the go to class for fk ctrls.
                    To do this you'll need to set a param input that allows users
                    to input how many joints they want, and if they want subCtrls!
'''
import maya.cmds as cmds

import part
from autorigger.lib import joint
from autorigger.lib import control
from autorigger.lib import attribute
from autorigger.lib import curve
from autorigger.lib import nameSpace

reload(part)
reload(nameSpace)
'''
import part as part
import RigTools.libs.joint as joint
import RigTools.libs.control as control
import RigTools.libs.name as name
import RigTools.libs.attribute as attribute
import RigTools.libs.curve as curve
reload(part)
reload(joint)
reload(control)
reload(name)
reload(attribute)
reload(curve)
'''

#limb inherits a bit from IkfkLimb
class FkChain(part.Part):

    def __init__(self, name, jointCount=4, subCtrl=True):
        super(FkChain,self).__init__(name)

        self.jointCount = jointCount
        self.fkChainJoints = list()
        self.jointPositions = list()
        for count in range(0,self.jointCount):

            #store class in self.fkChainJoints list
            index = count+1
            self.fkChainJoints.append(
                joint.Joint("{0}{1}_{2}".format(
                    self.getName(),
                    str(index),
                    nameSpace.BINDJOINT)
                )
            )

            #store positions as well: add 3 to Y for each new joint.
            dist = count*3+2
            self.jointPositions.append( [0,dist,0] )


        self.subCtrl = subCtrl

    def setJointPositions(self,value):
        self._jntPositions = value

    def getfkChainControlName(self, index):
        return self.mainCtrls[index].getName()

    def setup(self):
        super(FkChain,self).setup()

        parent = self.skeletonGroup

        #this builds and names the bind joints
        self.guides = list()
        for i,jnt in enumerate(self.fkChainJoints):

            jnt.create()
            self.allJoints.append(jnt.getName())
            #add to allJoints ^

            jnt.setPosition(self.jointPositions[i])

            # workaround because setParent is parenting the parent for now
            cmds.parent(jnt.getName(), parent)

            self.guides.append(
                self.createGuide(
                    jnt.getName().replace(nameSpace.BINDJOINT, nameSpace.GUIDE),
                    jnt.getName(),
                    jnt.getPosition(),
                    self.masterGuide.getName()
                )
            )

            #parent = jnt.getName()

        #create an upvector for fkChain
        self.fkChainUpv = control.Control('{0}_upvGuide'.format(self.getName()), shape='cross')
        self.fkChainUpv.create()


        aimConstraintList = list()
        for index,jnt in enumerate(self.fkChainJoints):

            #the last joint get's orientConstrained
            if index == (self.jointCount-1):
                 constraint = cmds.orientConstraint( self.fkChainJoints[index-1].getName(),
                                                     self.fkChainJoints[index].getName() )
                 cmds.parent(constraint, self.guidesGroup)
            else:
                #all others are aimConstrained
                #aim constraint joint[jnt+1] to joint[jnt]
                aimCon = cmds.aimConstraint( self.guides[index+1].getName(),
                                        self.fkChainJoints[index].getName(),
                                        worldUpType='object',
                                        worldUpObject= self.fkChainUpv.getName() )

                aimConstraintList.append( aimCon[0] )
                cmds.parent(aimConstraintList[index], self.guidesGroup)


        self.aimAttr = attribute.switch(self.masterGuide.getName(),
                        "aim",0,
                        ["x","y","z","-x","-y","-z"],
                        [[1,0,0],[0,1,0],[0,0,1],[-1,0,0],[0,-1,0],[0,0,-1]])

        self.upAttr = attribute.switch(self.masterGuide.getName(),
                        "up",0,
                        ["x","y","z","-x","-y","-z"],
                        [[1,0,0],[0,1,0],[0,0,1],[-1,0,0],[0,-1,0],[0,0,-1]])



        for cst in aimConstraintList:
            cmds.connectAttr(self.upAttr, "{0}.upVector".format(cst),f=True)
            cmds.connectAttr(self.aimAttr, "{0}.aimVector".format(cst),f=True)
            #cmds.setAttr("{0}.worldUpVector".format( cst ), self.upAttr )

        #so that the aim and up are not both x
        cmds.setAttr("{0}.up".format(self.masterGuide.getName()) ,1)
        self.strUpAttr = (cmds.getAttr ("{0}.up".format(self.masterGuide.getName()), asString = True))
        cmds.select(cl=True)

        #move the fkChainUPV somewhere reasonable
        self.fkChainUpv.setPosition( [-5, 10, 0] )
        #and parent it to the masterGuide
        cmds.parent(self.fkChainUpv.getNull(), self.masterGuide.getName())

    def postSetup(self):
        super(FkChain,self).postSetup()

    def preBuild(self):
        super(FkChain,self).preBuild()

    def build(self):
        super(FkChain,self).build()

        #create ctrls and non hierarchy ctrls
        self.mainCtrls = list()
        subCtrls = list()

        for i, joint in enumerate(self.fkChainJoints):

            ii = i+1
            self.mainCtrls.append(
                control.Control("{0}{1}_1".format(
                    self.getName(),
                    str(ii) ),
                position = joint.getPosition(),
                shape='square')
            )

            self.mainCtrls[i].create()
            self.mainCtrls[i].setColor(30)
            #scale self.mainCtrls to be a little bigger
            cmds.select("{0}.cv[0:4]".format(self.mainCtrls[i].getName(), r=True ))
            cmds.scale(1.2,1.2,1.2)

            #point curve in right direction
            self.mainCtrls[i].setOrientation( self.downAxis )

            #build subCtrl?
            if self.subCtrl :

                subCtrls.append(
                    control.Control(
                        "{0}{1}_{2}".format(
                            self.getName(),
                            str(ii),
                            nameSpace.SUBCONTROL
                            ),
                        position = joint.getPosition(),
                        shape='circle' ) )

                subCtrls[i].create()
                subCtrls[i].setColor(26)

                #point curve in right direction
                subCtrls[i].setOrientation( self.downAxis )
                #parent subCtrl to mainCtrl
                cmds.parent( subCtrls[i].getNull(), self.mainCtrls[i].getName() )

            #snap ctrls
            par = cmds.parentConstraint( joint.getName(), self.mainCtrls[i].getNull())
            cmds.delete(par)

            #parent accordingly
            #if i is not 0, parent accordingly
            if (i != 0):
                cmds.parent(self.mainCtrls[i].getNull(), self.mainCtrls[i-1].getName())
                #and zero out zeroGroup1 rotate
                #cmds.setAttr("{0}.rotate".format(self.mainCtrls[i].getNull()), 0, 0,0)

            #parent to subCtrl or mainCtrl?
            if self.subCtrl:
                #parentConstraint subCtrl to joints
                cmds.parentConstraint(subCtrls[i].getName(), joint.getName(), mo=True)
            else:
                #parentConstraint mainCtrl to joints
                cmds.parentConstraint(self.mainCtrls[i].getName(), joint.getName(), mo=True)


        #parent controls to ctrl gorup
        cmds.parent( self.mainCtrls[0].getNull(), self.controlsGroup)
        cmds.select(cl=True)

    def postBuild(self):
        super(FkChain,self).postBuild()







