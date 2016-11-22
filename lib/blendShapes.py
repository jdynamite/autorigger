# 
'''
Blendshapes tools

'''
import maya.cmds as cmds
import maya.mel as mel


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

# base is like the target destination
def splitShapeSetup():

    # create 3 splitOutput meshes that will be painted
    # start with creating the splitters
    selection = cmds.ls(sl=True)
    meshList = selection[:-1]
    base = selection[-1]
    
    splitters = []
    blends = []
    meshes = ["A", "B", "C"]
    inputMeshList = meshList

    # first target plays an important role, this is the one we're going to default turn on and align to in tx
    first = meshList[0]
    for i, letter in enumerate(meshes):
        # create splitters
        split = "{0}_split{1}".format(base, letter)
        cmds.duplicate(base, n=split)
        cmds.delete(cmds.parentConstraint(first, split))
        # how far to move the dup
        dist = (int(i) + 1) * 10
        cmds.move(dist, 0, 0, split, r=True)

        blend = "{0}_BSHP".format(split)
        cmds.select(split)
        cmds.blendShape(n=blend)
        splitters.append(split)
        blends.append(blend)


    # add blends and set them too yada yada
    blendDrivers = []
    blendDrivers = blendDrivers + meshList
    for i, split in enumerate(splitters):

        # connections?
        cmds.select(blendDrivers)
        cmds.select(split, tgl=True)
        mel.eval("performBlendShapeAdd 0;")
        blendDrivers.append(split)

        # if a splitter, set to -1
        for s in splitters:
            splitBshp = "{0}.{1}".format(blends[i], s)
            if cmds.objExists(splitBshp):
                cmds.setAttr(splitBshp, -1)

    # Turn on the first. Just as a default
    for blend in blends:
        cmds.setAttr("{0}.{1}".format(blend, first), 1)

        # connect all meshList input shapes to each other
        for i, target in enumerate(inputMeshList):
            print inputMeshList
            if blend != blends[0]:
                cmds.connectAttr(
                    "{0}.{1}".format(blends[0], target),
                    "{0}.{1}".format(blend, target)
                )

    #set colors
    setColors(splitters[0], "red")
    setColors(splitters[1], "orange")
    setColors(splitters[2], "yellow")

def setColors(mesh, color):
    c = []
    if color == "yellow":
        c = [0.575, 0.56, 0]
    elif color == "orange":
        c = [0.575, 0.32, 0]
    else:
        #red is default
        c = [0.6, 0.15, 0.1]

    lam = cmds.shadingNode("lambert", asShader=True)

    cmds.select(mesh)
    cmds.hyperShade(a=lam)

    cmds.setAttr("{0}.colorR".format(lam), c[0])
    cmds.setAttr("{0}.colorG".format(lam), c[1])
    cmds.setAttr("{0}.colorB".format(lam), c[2])


# extractimg 
# directions: select all split meshes and run
# NOTE: shapes must be named correctly. "L_", "R_", and "C_" must be used as prefixes
def extractSplits():
    
    splits = cmds.ls(sl=True)
    bshp = "{0}_BSHP".format(splits[0])
    
    # first target should be set to 1, but just in case reset them all
    targets = getTargets(bshp)
    for target in targets:
        blendName = "{0}.{1}".format(bshp, target)
        cmds.setAttr( blendName, 0 )
    
    for target in targets:
        blendName = "{0}.{1}".format(bshp, target)
        cmds.setAttr( blendName, 1 )
        
        # duplicate each split
        for i, split in enumerate(splits):
            cmds.select(split)
            
            # name extraction
            extract = target.split("_")
            name = ("{0}_{1}{2}_{3}".format(extract[0], extract[1], str(i+1), extract[2]))
            
            cmds.duplicate(n=name)
        
        cmds.setAttr( blendName, 0)





