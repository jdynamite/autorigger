from maya import mel, cmds
from maya.api import OpenMaya as om
import util

"""
collection of utilities for parsing component selections
"""


def getIndexFromStr(string):
    index = util.strBetween(string, '[', ']')
    return int(index)


def getStrFromIndex(index, obj, component="vtx"):
    base = "{0}.{1}[{2}]"
    return base.format(obj, component, int(index))


def flattenComponents(components):
    ordered = list(components)
    base = ordered[0]
    comp = ordered[0]

    if len(ordered):
        base = base.split('.')[0]
        comp = util.strBetween(comp, '.', '[')
    for i, vtx in enumerate(ordered):
        if ":" in vtx:
            ordered.pop(i)
            substr = util.strBetween(vtx, '[', ']')
            new = substr.split(':')
            new = [int(n) for n in new]
            for k, v in enumerate(xrange(new[0], new[1] + 1)):
                component = "{0}.{1}[{2}]".format(base, comp, str(v))
                ordered.insert(i + k, unicode(component))
    return ordered


def loopSort(start=None, end=None, loop=None):

    if all(a is None for a in [start, end, loop]):
        if len(loop):
            start = loop[0]
            end = loop[:-1]

    cmds.select([start, end])
    loop = list(loop)

    firstSweep = vertsBetween(start, end)
    allFlat = flattenComponents(loop)

    secondSweep = list(set(firstSweep) ^ set(allFlat))
    mesh = start.split('.')[0]

    start = getIndexFromStr(start)
    end = getIndexFromStr(end)
    mit = om.MItMeshVertex(util.getDag(mesh))
    secondIndices = [getIndexFromStr(v) for v in secondSweep]

    ordered = []
    ordered.append(start)

    r = mit.setIndex(start)
    if not r:
        r = mit.setIndex(start)

    mask = set(secondIndices + ordered)
    nextVtx = set([v for v in mit.getConnectedVertices()])
    nextVtx = list(nextVtx.intersection(mask))
    nextVtx = nextVtx[0]
    ordered.append(nextVtx)

    for i in xrange(len(secondSweep)):
        r = mit.setIndex(nextVtx)

        if not r:
            r = mit.setIndex(nextVtx)

        newVtx = set([v for v in mit.getConnectedVertices()])

        if end in newVtx:
            ordered.append(end)
            break

        newVtx = newVtx.intersection(secondIndices).difference(ordered)
        newVtx = list(newVtx)

        if not len(newVtx):
            err = "Could not find a connected vtx to {0}"
            cmds.select(getStrFromIndex(nextVtx, mesh))
            raise RuntimeError(err.format(nextVtx))

        nextVtx = newVtx[0]
        ordered.append(nextVtx)

    secondSweep = [getStrFromIndex(i, mesh) for i in ordered]

    return firstSweep, secondSweep


def vertsBetween(vtx1=None, vtx2=None):
    """
    After selecting two vertices, function returns
    an ordered list of vertices between vtx1 and vtx2
    It always bias one orientation based on polySelectSp
    """
    sel = []

    if all(v is None for v in [vtx1, vtx2]):
        sel = cmds.ls(sl=True)
    else:
        if not all(".vtx[" in v for v in [vtx1, vtx2]):
            err = "Args must be in the form of mesh.vtx[n]."
            raise RuntimeError(err)
        sel = [vtx1, vtx2]

    if None in sel or len(sel) != 2:
        err = "Must select two verts or pass two arguments as verts."
        raise RuntimeError(err)

    start, end = [getIndexFromStr(s) for s in sel]
    allverts = flattenComponents(mel.eval("polySelectSp -q -loop"))
    allindices = [getIndexFromStr(idx) for idx in allverts]
    sel = allverts[0]
    mesh = sel.split('.')[0]
    mit = om.MItMeshVertex(util.getDag(mesh))

    ordered = []
    ordered.append(start)

    r = mit.setIndex(start)
    if not r:
        r = mit.setIndex(start)

    nextVtx = [v for v in mit.getConnectedVertices() if v in allindices]
    nextVtx = nextVtx[0]
    ordered.append(nextVtx)

    for i in xrange(len(allindices)):
        r = mit.setIndex(nextVtx)
        if not r:
            r = mit.setIndex(nextVtx)
        nextVtx = [v for v in mit.getConnectedVertices(
        ) if v in allindices and v not in ordered]
        nextVtx = nextVtx[0]
        ordered.append(nextVtx)
        if nextVtx == end:
            break

    return [getStrFromIndex(i, mesh) for i in ordered]
