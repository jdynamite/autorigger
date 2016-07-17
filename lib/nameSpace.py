'''
--------------------------------
 Name Library
---------------------------

Function: to change names in one place

'''
import os

DIR = os.path.dirname(__file__)

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

# colors
COLORS = {"left": "blue", "right": "red", "center": "yellow", "default": "yellow"}
COLOR_TO_INT = {"red" : 13, "blue": 6, "yellow": 17}

# extensions
WEIGHTSEXTENSION = ".skin"

# paths
WEIGHTSFOLDER = "weights"
CONTROL_LIB_PATH = os.path.join(DIR, "controls.ctrl")

# nodes
MULTIPLYDIVIDE = "MDN"
CONDITION = "CND"
PLUSMINUSAVG = "PMA"
REVERSE = "RVR"
DCM = "DCM"
VCP = "VCP"

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

        # if not L_, R_, or C_
        if (splitName[0] == RIGHT):
            return splitName[0]

        elif (splitName[0] == LEFT):
            return splitName[0]

        elif (splitName[0] == CENTER):
            return splitName[0]

        #error
        else:
            raise RuntimeError("NAME input must start with a side prefix of 'L_', 'R_', or 'C_' !" )

    return None
