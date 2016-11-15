'''
Blendshapes tools

'''
import maya.cmds as cmds


# extracts all blendshapes from selected blendshape NODE
# target is the mesh that will be duplicated. Can be the mesh with the blendshape, or a mesh you have wrapped
def extractShapes(blendshape, designationMesh):

    shapes = getTargets(blendshape)
    dupes = []

    for shape in shapes:

        # fire on the bshp
        shapeAttr = "{0}.{1}".format(blendshape, shape)
        cmds.setAttr(shapeAttr, 1)

        # duplicate the target from designationMesh
        cmds.select(designationMesh)
        dupe = cmds.duplicate(n=shape)[0]
        cmds.parent(w=True)
        dupes.append(dupe)

        # turn off the bshp
        cmds.setAttr(shapeAttr, 0)

    cmds.select(dupes)

# returns all target names in a blendshape node
def getTargets(bshp):

    result = cmds.listAttr(bshp, m=True, st="weight" )
    return result