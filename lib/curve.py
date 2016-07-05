import maya.cmds as cmds
# module to create/export/import curve data with json

def getCVs(curve):
    return cmds.ls("{0}.cv[*]".format(curve),flatten=True)

def getCVpositions(pointList):
    positions = list()

    for point in pointList:

        ws = cmds.xform(point,q=True,ws=True,t=True)
        positions.append(ws)

    return positions

def createFromPoints(points,degree=1,name = "curve#"):
    knotList = [0]

    if degree == 1:
        knotList.extend(range(1,len(points)))
    if degree ==3:
        knotList.extend([0])
        knotList.extend(range(len(points) - 2 ))
        knotList.extend([knotList[-1], knotList[-1]])

    curve = cmds.curve (degree=degree,point=points,knot=knotList)
    curve = cmds.rename (curve,name)

    return curve

def reorient(curve,downAxis):
    x = 0
    y = 0
    z = 0
    if downAxis == "x" or "-x":
        z = z + 90
    elif downAxis == "y" or "-y":
        y = 90
    else:
        x = x + 90
    cmds.rotate (  x,y,z , getCVs(curve))

