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
NULL = "NULL"
ZERO = "ZERO"
GUIDE = "GUIDE"
SETUP = "SET"
IK = "IK"
FK = "FK"

# joints
BINDJOINT = "bindJNT"
DRVJOINT =  "drvJNT"
SPLINE = "splineJNT"

# sides
RIGHT = "R"
LEFT = "L"
CENTER = "C"
SIDES = {"right":RIGHT, "left":LEFT, "center":CENTER}

# extensions
WEIGHTSEXTENSION = ".skin"

# paths
WEIGHTSFOLDER = "weights"

# nodes
MULTIPLYDIVIDE = "MDN"
CONDITION = "CND"
PLUSMINUSAVG = "PMA"
REVERSE = "RVR"

#template of how names get input
NAMETEMPLATE = "side.location.description.number.type"
DELIMITER = "_"

def getSide(name):
    '''
    Returns side of the name passed in.
    '''
    if not DELIMITER in name:
        raise RuntimeError("{0} must be part of name. {1}".format(DELIMITER,NAMETEMPLATE))

    splitName = name.split(DELIMITER)

    if splitName:
        return splitName[0]

    return None
