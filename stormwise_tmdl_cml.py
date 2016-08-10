# -*- coding: utf-8 -*-
"""
Created on Sun Aug  7 16:33:12 2016

@author: arthur

provide command line input and output for stormwise_tmdl
"""
import yaml
import sys
from copy import deepcopy
from stormwise_tmdl import stormwise
from stormwise_tmdl import evaluate_solution
from stormwise_tmdl_upper_bounds import upper_bounds
from stormwise_tmdl_benefit_slopes import benefit_slopes

benefitUnits = {'1_volume': 'Million Gallons', '2_sediment': 'Tons',
            '3_nitrogen': 'Pounds', '4_phosphorous': 'Pounds'}   
benefitConvertUnits =  {'1_volume': 264.172e-6,   # million gallons per cubic meter    
                        '2_sediment':  0.0011,    # english ton per kg
                        '3_nitrogen':  2.2,          # pound per kg
                        '4_phosphorous': 2.2    # pound per kg
                        }

def multiply_dict_by_constant(dct,constant):
    for key in sorted(dct):
        if type(dct[key]) is dict:
            multiply_dict_by_constant(dct[key],constant)
        else:
            dct[key] *= constant
def convert_benefit_units(benDict,benefitConvertUnits):
    dct = deepcopy(benDict)
    for t in sorted(dct):   # the first level is the benefit type
        dct[t] *= benefitConvertUnits[t]
    return dct


def print_output(solutionDict):  
    print "Benefit Units:"
    print yaml.dump(benefitUnits)   
    benTotsByBenefit = solutionDict['benTotsByBenefit']
    benTotsByBenefitConverted = convert_benefit_units(benTotsByBenefit,benefitConvertUnits)
    print "Benefits:"
    print yaml.dump(benTotsByBenefitConverted)

    investmentTotal = solutionDict['investmentTotal']
    investmentTotalMillions = investmentTotal/1e6
    print "Total GSI Investment Required to Obtain These Benefits:   $%10.2f Million\n" % investmentTotalMillions
    '''
    invTotsByZone = {}   #  [i]
    invTotsByLanduse = {}  # [j]
    invTotsByGi = {}  # [k]
    invTotsByZoneByLanduse = {}  # [i][j]
    invTotsByZoneByGi = {}   # [i][k]
    invTotsByLanduseByGi = {}  #  [j][k]
    '''
    while True:
        print "\n Choose one of the following options for Investment details:"
        print "0 - No more details"
        print "1 - By geographic zone"
        print "2 - By land use"
        print "3 - By green infrastructure technology"
        displayOption = int(raw_input("Enter your choice:"))
        if displayOption == 0:
            break
        if displayOption == 1:
            print yaml.dump(solutionDict['invTotsByZone'])
        if displayOption == 2:
            print yaml.dump(solutionDict['invTotsByLanduse'])
        if displayOption == 3:
            print yaml.dump(solutionDict['invTotsByGi'])



    '''
    # Decision Space Output:
    print "\nDecision Space Output:"
    zoneTot = {}
    luTot = {}
    giTot = {}
    for i in sorted(I):  # Compute and output total investments by zone
        zoneTot[i] = 0.0
        for j in sorted(J):
            if KONJ[j] != None:
                for k in sorted(KONJ[j]):
                    zoneTot[i] += x[i][j][k]
        zoneTotMillions = zoneTot[i]/1e6
        print '\nZone:  %s with Total investment in zone =  %10.2f Million (details below)' % (i,zoneTotMillions)
        print '\n%18s' % '',
        for k in sorted(K):
            print "%16s" % k,
        print "%18s" % 'Land Use Total'
        luZoneTot = {}
        for j in sorted(J):  # compute and output total investments by landuse
            print "%-18s" % j,
            luZoneTot[j] = 0.0
            for k in sorted(K):
                if KONJ[j] != None:
                    if k in KONJ[j]:
                        luZoneTot[j] += x[i][j][k]
                        investMillion = x[i][j][k]/1e6
                        print "%18.2f" % investMillion,
                    else:
                        print "%18.2f" % 0.0,
                else:
                    print "%18.2f" % 0.0,
            luZoneTotMillion = luZoneTot[j]/1e6
            print "%18.2f" % luZoneTotMillion
            print ''
            luTot[i] = luZoneTot
        giZoneTot = {}
        for k in sorted(K):
            giZoneTot[k] = 0.0
            for j in sorted(J):
                if KONJ[j] != None:
                    if k in KONJ[j]:
                        giZoneTot[k] += x[i][j][k]
        print "%18s" % "GI Practice Total",
        giTot[i] = giZoneTot
        for k in sorted(K):
            giTotMillion = giZoneTot[k]/1e6
            print "%18.2f" % giTotMillion,
    #print ''
    #print zoneTot
    #print luTot
    #print giTot
    '''
def main(inYamlFile):
    print "\n\nStormWISE_TMDL COMMAND LINE VERSION\n"
    print "Instructions:"
    print "1. Before running StormWISE, you must prepare an input text file in YAML format"
    print "   and you will specify the name of that file below"
    print "2. StormWISE will calculate and display the MAXIMUM POSSIBLE BENEFITS"
    print "   that can be achieved by installing Green Stormwater Infrastructure (GSI)"
    print "   AT ALL POSSIBLE SITES in the watershed"
    print "3. StormWISE will also display an estimate of the"
    print "   TOTAL WATERSHED-WIDE INVESTMENT DOLLARS required"
    print "   to achieve maximum possible benefits"
    print "4. Then you will be asked to specify numeric values for"
    print "   the BENEFIT LEVELS THAT YOU ACTUALLY WANT TO ACHIEVE,"
    print "   using the units specified"
    print "5. StormWISE will then run its OPTIMIZATION MODEL to"
    print "   find the best way to allocate investment dollars among"
    print "   different geographic zones, land uses, and GSI technologies"
    print "   so as to MINIMIZE TOTAL WATERSHED-WIDE INVESTMENT DOLLARS"
    print "6. The StormWISE solution will be displayed to the screen"
    print "   and you will then be given several options for breaking out benefits"
    print "   and investment dollars according to geographic zone, land use, and GSI technologies"
    print "7. You will then be invited to perform \"Sensitivity Analyses\""
    print "   by entering ALTERNATIVE BENEFIT LEVELS that will produce"
    print "   corresponding OPTIMAL SOLUTIONS"

    prompt = "\nEnter the file name containing your\n  StormWISE input data in YAML format\n  (or type Q to quit) :  "
    inYamlFile = raw_input(prompt)
    if inYamlFile == "Q" or inYamlFile == "q":
        sys.exit("StormWISE Run Completed")
    with open(inYamlFile, 'r') as fin:
        inYamlDoc = yaml.load(fin)
    u = upper_bounds(inYamlDoc)
    s = benefit_slopes(inYamlDoc)
    T = inYamlDoc['T']
    upperBounds = upper_bounds(inYamlDoc)
    upperBoundSolutionDict = evaluate_solution(upperBounds,s,inYamlDoc)
    print "\n\n\nUPPER LIMITS ON BENEFITS:\n"
    print_output(upperBoundSolutionDict)

# Load the benefitDict using console input:
    while True:
        benefitDict = {}
        print "Enter Your Chosen Minimum Benefit Levels in Specified Units: (Type Q to QUIT)"
        tDict = {}
        for t in sorted(T):
            prompt = "%s (%s):  " % (t,benefitUnits[t])
            inString = raw_input(prompt)
            if inString == 'Q'or inString == 'q':
                sys.exit("StormWISE Run Completed")
            else:
                tDict[t] = float(inString)/benefitConvertUnits[t]  # convert to fundamental units
        benefitDict['benefitLowerBounds'] = tDict
        print "\n\nRUNNING STORMWISE USING AMPL WITH MINOS SOLVER:\n"
        decisions = stormwise(inYamlDoc,benefitDict)
        print "\nDisplaying the StormWISE OPTIMAL SOLUTION:\n"
        solutionDict = evaluate_solution(decisions,s,inYamlDoc)
        print_output(solutionDict)
#    solutionStr = yaml.dump(solutionDict)
#    print "\n\nsolutionStr printout:"
#    print solutionStr

main('wingohocking.yaml')