from maya import mel, cmds
from maya.api import OpenMaya as om
import util

"""
collection of utilities for parsing component selections
"""


def getIndexFromStr(string):
    if not isinstance(string, basestring) and not all(s in string for s in ["[", "]"]):
        return RuntimeError("Couldn't parse {0}".format(string))
    index = string[string.index("[") + 1:string.index("]")]
    return int(index)


def getStrFromIndex(index, obj, component="vtx"):
    base = "{0}.{1}[{2}]"
    return base.format(obj, component, int(index))


def flattenComponents(components):
    ordered = components
    for i, vtx in enumerate(ordered):
        if ":" in vtx:
            ordered.pop(i)
            start = vtx.index('[') + 1
            end = vtx.index(']')
            substr = vtx[start:end]
            new = substr.split(':')
            new = [int(n) for n in new]
            for k, v in enumerate(xrange(new[0], new[1] + 1)):
                ordered.insert(i + k, unicode("body.vtx[{0}]".format(str(v))))
    return ordered


def orderedVertices(vtx1=None, vtx2=None):
    """
    After selecting two vertices, function returns
    an ordered list of vertices between vtx1 and vtx2
    """
    sel = []

    if all(v for v in [vtx1, vtx2]) is None:
        sel = cmds.ls(sl=True)
    else:
        sel = [vtx1, vtx2]
    if None in sel or len(sel) != 2:
        raise RuntimeError("Unable to work with input")

    start = util.getIndexFromStr(sel[0])
    end = util.getIndexFromStr(sel[1])

    allverts = util.flattenComponents(mel.eval("polySelectSp -q -loop"))
    allindices = [util.getIndexFromStr(idx) for idx in allverts]
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

    return [util.getStrFromIndex(i, mesh) for i in ordered]
