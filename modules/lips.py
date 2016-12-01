# lips setup using super ribbons

import maya.cmds as cmds
from autorigger.lib import ribbon

class Lip(object):

    def __init__(self, name, cvs):
        self.name = name
        self.cvs = cvs

    def createLipRibbon(self):
        '''
            DIRECTIONS:
                planes should already be created. Both HR and LR
                CV selection MUST be from left to right ALWAYS

        '''

        # create lips master
        master = cmds.createNode("transform", n="name_GRP")

        rbn = ribbon.superRibbon(self.name, self.cvs)

        # parent to hierarchy
        for r in rbn:
            cmds.parent(r["fol"], master)

        #rename buildSingles(minors)
        renameRig(self.name, rbn)


    def renameRig(self, dict):
        '''
        :param dict: dictList to be renamed
        :return: None
        '''
        dictList = [
            "master",
            "cNull",
            "jNull",
            "con",
            "jnt",
            "fol"
        ]

        # get center of selection count
        dictSize = len(dict)
        center = dictSize/2

        # Set the prefix
        L = 1
        R = center
        #dictSize is list
        for i in range(dictSize):

            prefix = "L_{0}{1}".format(self.name, str(L))
            L += 1
            if i == center:
                prefix = "C_{0}1".format(self.name)
            if i > center:
                prefix = "R_{0}{1}".format(self.name, str(R))
                R = R-1

            # d is each dict within list
            for d in dictList:
                thisDict = dict[i][d]

                buffer = thisDict.split("_")
                oldName = buffer[0]

                newName = thisDict.replace(oldName, prefix)
                cmds.rename(thisDict, newName)


