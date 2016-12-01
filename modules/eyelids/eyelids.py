import maya.cmds as cmds

import singleEyelid
from autorigger.modules import part
reload(singleEyelid)

class Eyelids(part.Part):
    def __init__(self, name, lidCount=3):
        super(Eyelids, self).__init__(name)
        self.name = name
        self.lidCount = lidCount
        self.positions = []

        self.mirror = True
        self.lids = []

    def setup(self):
        self.initializeSetup()

        for i in range(self.lidCount):
            prefix = "{}{:02d}".format(self.name, i+1)
            result = singleEyelid.SingleEyelid(prefix)
            result.setup()

            self.lids.append(result)


    def postSetup(self):
        super(Eyelids, self).postSetup()

    def preBuild(self):
        super(Eyelids, self).preBuild()

    def build(self):
        super(Eyelids, self).build()

    def postBuild(self):
        super(Eyelids, self).postBuild()