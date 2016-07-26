'''
--------------------------------
 Name Library
---------------------------

Function: to change names in one place

'''

GROUP = "GRP"
JOINT = "JNT"
LOCATOR = "LOC"
CONTROL = "CON"
SUBCONTROL = "SUB"
NULL = "NULL"
ZERO = "ZERO"
GUIDE = "GUIDE"
SETUP = "SET"
IK = "IK"
FK = "FK"

# joints
BINDJOINT = "bindJNT"
DRVJOINT = "drvJNT"
SPLINE = "splineJNT"
HANDLE = "ikHdl"
POLEVECTOR = "pv"

# sides
RIGHT = "R"
LEFT = "L"
CENTER = "C"
SIDES = [LEFT, RIGHT, CENTER]

# extensions
WEIGHTSEXTENSION = ".skin"

# paths
WEIGHTSFOLDER = "weights"

# nodes
MULTIPLYDIVIDE = "MDN"
CONDITION = "CND"
PLUSMINUSAVG = "PMA"
REVERSE = "RVR"
DCM = "DCM"
VCP = "VCP"

# template of how names get input
NAMETEMPLATE = "side.location.description.number.type"
DELIMITER = "_"


def getSide(name):
    '''
    Returns side of the name passed in.
    '''
    if DELIMITER not in name:
        err = "{0} must be part of name. {1}"
        raise RuntimeError(err.format(DELIMITER, NAMETEMPLATE))

    # if not L_, R_, or C_
    # expanded to accept suffixes _L
    for side in SIDES:
        if name.startswith(side + DELIMITER):
            return side
        elif name.endswith(DELIMITER + side):
            return side

    err = "NAME input must start or end with {0}!"
    raise RuntimeError(err.format(' or '.join(SIDES)))
    return None
