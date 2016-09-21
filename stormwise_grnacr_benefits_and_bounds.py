# code for computing StormWISE benefit slopes and upper bounds
# plus code for converting benefit units based on file "convert_benefits.yaml"
# Copyright Arthur E. McGarity, 2016

from Arts_Python_Tools.tools import format_dict_as_strings
from Arts_Python_Tools.tools import multiply_dict_by_constant

def convert_benefit_units(benDict,benefitConvertUnits):
    dct = deepcopy(benDict)
    for t in sorted(dct):   # the first level is the benefit type
        dct[t] *= benefitConvertUnits[t]
    return dct

def format_and_convert_benefit_dict(dct,formatStr,benefitConvertUnits,benefitUnits):
    oneDimDict = False
    for t in sorted(dct):
        if type(dct[t]) is dict:
            multiply_dict_by_constant(dct[t],benefitConvertUnits[t])
            #formatWithUnits = formatStr + benefitUnits[t]
            format_dict_as_strings(dct[t],formatStr)
        else:
            oneDimDict = True
            dct[t] *= benefitConvertUnits[t]
    if oneDimDict:
        format_dict_as_strings(dct,formatStr)
    displayDict = {}
    for t in sorted(dct):
        key = t+' ('+benefitUnits[t]+')'
        displayDict[key] = dct[t]
    return(displayDict)

def benefit_slopes(inYamlDoc):
        I = inYamlDoc['I']
        J = inYamlDoc['J']
        K = inYamlDoc['K']
        KONJ = inYamlDoc['KONJ']
        T = inYamlDoc['T']
        cost = inYamlDoc['cost']
        export = inYamlDoc['export']
        eta = inYamlDoc['eta']
        s = {}  # will be a dictionary of dictionaries
        for i in I:  # generate decision variable dictionary
            jDict = {}
            for j in J: 
                kDict = {}
                if KONJ[j] != None:
                    for k in K:                   
                        tDict = {}
                        if k in KONJ[j]:
                            for t in T:
                                tDict[t] = eta[t][k][i]*export[t][j]/cost[k][j]
                        else:
                            for t in T:
                                tDict[t] = 0.0
                        kDict[k] = tDict
                else:
                    for k in K:
                        tDict = {}
                        for t in T:
                            tDict[t] = 0.0
                        kDict[k] = tDict                 
                jDict[j] = kDict
            s[i] = jDict
        return s

def upper_bounds(inYamlDoc):
        I = inYamlDoc['I']
        J = inYamlDoc['J']
        K = inYamlDoc['K']
        KONJ = inYamlDoc['KONJ']
        cost = inYamlDoc['cost']
        f = inYamlDoc['f']
        area = inYamlDoc['area']
        u = {}  # will be a dictionary of dictionaries
        for i in I:  # generate decision variable dictionary
            jDict = {}
            for j in J: 
                kDict = {}
                if KONJ[j] != None:
                    for k in K:                   
                        if k in KONJ[j]:
                            kDict[k] = cost[k][j]*f[k][j][i]*area[j][i]
                        else:
                            kDict[k] = 0.0
                else:
                    for k in K:
                        kDict[k] = 0.0
                jDict[j] = kDict
            u[i] = jDict
        return u