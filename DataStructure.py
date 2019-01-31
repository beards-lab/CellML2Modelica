# define the data structure
from enum import Enum
import re

class MappingType(Enum):
    BINDING = 1
    EQUATION = 2

class InstantiateType(Enum):
    SIBLINGS = 1
    ENCAPSULATION = 2

class Variable:

    def __init__(self, name, unit, str):
        self.name = name
        self.unit = unit
        self.pubIn = True if re.search(r'pub: in', str) is not None else False
        self.pubOut = True if re.search(r'pub: out', str) is not None else False
        self.privIn = True if re.search(r'priv: in', str) is not None else False
        self.privOut = True if re.search(r'priv: out', str) is not None else False
        self.valueType = False

        self.value = next((v for v in re.findall(r'init: ([-0-9.]+)', str)), None)
    
    def returnBinding(self, prefix = None):
        if self.valueType and self.value is not None:
            return self.value
        elif prefix is None:
            return self.name
        else:
            return ".".join([prefix, self.name])



class Mapping:
    """ Maps variables.

    mappingType.Binding: are in the object instantiation. For direction TO target. 
        for encapsulation mappings:
            ObjectName TargetInstance1 (targetVariable = self.sourceVariable);
        for wincest between children:
            ObjectName TargetInstance1 (targetVariable = self.sourceInstance1.sourceVariable);
        

    mappingType.Equation: are in equation section. For direction FROM target
        For encapsulation mappings:
            self.sourceVariable = TargetInstance1.targetVariable
        for wincest between children: the direction is not imprortant here:
            self.sourceInstance1.sourceVariable = TargetInstasnce1.targetVariable
            # and actually never happens! (?)


    TODO EvaluateParameters: if the pub:out variable is a param, then directly insert its value, e.g.
        parentInstance1 = [targetInstance].targetValue

    Mappings are only allowed from top to bottom, e.g. from parent to its children or from environment (top level)

    """

    # EvaluateParameters = True

    def __init__(
        self, XX , x, YY, y):

        if   x.privIn and y.pubOut:
            # A
            self.mappingType = MappingType.EQUATION
            self.instantiateType = InstantiateType.ENCAPSULATION
            self.ownerInstance = XX
            self.ownerVariable = x
            self.targetInstance = YY
            self.targetVariable = y
            self.writeOutput = self.ownerVariable.name + " = " + self.targetVariable.returnBinding(self.targetInstance.uniqueInstanceName)
        elif x.privOut and y.pubIn:
            # B
            self.mappingType = MappingType.BINDING
            self.instantiateType = InstantiateType.ENCAPSULATION
            self.ownerInstance = YY
            self.ownerVariable = y
            self.targetInstance = XX
            self.targetVariable = x
            self.writeOutput = self.ownerVariable.name + " = " + self.targetVariable.returnBinding()
        elif x.pubOut and y.privIn:
            # C
            self.mappingType = MappingType.EQUATION
            self.instantiateType = InstantiateType.ENCAPSULATION
            self.ownerInstance = YY
            self.ownerVariable = y
            self.targetInstance = XX
            self.targetVariable = x
            self.writeOutput = self.ownerVariable.name + " = " + self.targetVariable.returnBinding(self.targetInstance.uniqueInstanceName)
        elif x.pubIn and y.privOut:
            # D
            self.mappingType = MappingType.BINDING
            self.instantiateType = InstantiateType.ENCAPSULATION
            self.ownerInstance = XX
            self.ownerVariable = x
            self.targetInstance = YY
            self.targetVariable = y
            self.writeOutput = self.ownerVariable.name + " = " + self.targetVariable.returnBinding()
        elif x.pubIn and y.pubOut:
            # E
            self.mappingType = MappingType.BINDING
            self.instantiateType = InstantiateType.SIBLINGS
            self.ownerInstance = XX
            self.ownerVariable = x
            self.targetInstance = YY
            self.targetVariable = y
            self.writeOutput = self.ownerVariable.name + " = " + self.targetVariable.returnBinding(self.targetInstance.uniqueInstanceName)
        elif x.pubOut and y.pubIn:
            # F
            self.mappingType = MappingType.BINDING
            self.instantiateType = InstantiateType.SIBLINGS
            self.ownerInstance = YY
            self.ownerVariable = y
            self.targetInstance = XX
            self.targetVariable = x
            self.writeOutput = self.ownerVariable.name + " = " + self.targetVariable.returnBinding(self.targetInstance.uniqueInstanceName)
        else:
            raise ValueError('Sumfin wen wong in mappings! Cannot recognize the type')

    def writeMappingType(self):
        if self.mappingType == MappingType.BINDING:
            return "BINDING"
        else:
            return "EQUATION"
    # def writeOutput(self):
    #     if self.mappingType = MappingType.BINDING and self.instantiateType = InstantiateType.ENCAPSULATION:
            
    #     elif self.mappingType = MappingType.BINDING and self.instantiateType = InstantiateType.ENCAPSULATION:
        

    def _source(self):
        # if Mapping.EvaluateParameters:# and self.__targetValue is not None:
            # return self.__targetValue
        if self.ownerInstance is None:
            return self.ownerVariable
        else:
            return ".".join((self.ownerInstance, self.ownerVariable))

    def _target(self):
        if self.targetInstance is None:
            return self.targetVariable
        else:
            return ".".join((self.targetInstance, self.targetVariable))

    # def getMapping(self):
    #     if self.__mappingType == MappingType.BINDING:
    #         return self.__targetVariable + ' = ' + self._source()
    #     elif self.__mappingType == MappingType.EQUATION:
    #         return self._source() + ' = ' + self._target() + ';\n'
            
class Object:
    def __init__(self, name, text = None, package_name = None, instanceName = None):
        self.name = name
        self.package_name = package_name
        if instanceName is None:
            # defining convention for instance mapping names, unless specified otherwise
            self.instance_name = name
            self.uniqueInstanceName = name + "1"
        else:
            self.instance_name = instanceName

        self.children = list()
        self.instances = list()
        # self.imported_instances = list()
        self.mappings = list()
        self.text = text

    # @property
    # def children(self):
    #     return self.__children

    # @property
    # def mappings(self):
    #     return self.__mappings

    @staticmethod
    def GetPackageName(cellml_filename):
        return re.sub(r'[\.\-]', r'_', cellml_filename)
    
    def __str__(self):
        return ".".join((self.package_name, self.name))
    
    def __repr__(self):
        return "-".join((self.package_name, self.name))