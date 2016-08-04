# -*- coding: utf-8 -*-
"""
stormwise_tmdl.py
takes a stormwise input file in YAML format
computes benefit slopes and investment upper bounds
outputs an AMPL dat file
and then runs AMPL on the dat file to generate stormwise_tmdl output
"""
import yaml
from subprocess import call
from stormwise_tmdl_ampl import generate_ampl_dat_file

def stormwise(inYamlDoc):
    ampl = generate_ampl_dat_file(inYamlDoc)
    # store the structure of the problem as found in the YAML file
    with open('stormwise_tmdl.dat', 'w') as fout:     
        fout.write(ampl)
        fout.close()
    call(["/Applications/amplide.macosx64/ampl","stormwise_tmdl.run"])
    with open('stormwise_tmdl.yaml', 'r') as fin:
        solution = yaml.load(fin)
        x = solution['x']
        I = inYamlDoc['I']
        J = inYamlDoc['J']
        K = inYamlDoc['K']
        KONJ = inYamlDoc['KONJ']
        decisions = {}
        for i in I:  # generate decision variable dictionary
            jDict = {}
            for j in J: 
                kDict = {}
                if KONJ[j] != None:
                    for k in K:                   
                        if k in KONJ[j]:
                            kDict[k] = x[i][j][k]
                        else:
                            kDict[k] = 0.0
                else:
                    for k in K:
                        kDict[k] = 0.0
                jDict[j] = kDict
            decisions[i] = jDict
        return decisions




def evaluate_solution(decisions,s):
    #with open('min_cost.yaml', 'r') as fin:
        #solution = yaml.load(fin)
        #x = solution['x']
        #u = solution['u']
        #s = solution['s']        
        # PRINT OUT RESULTS TO CONSOLE:
    solutionDict = {}
    solutionDict['decisions'] = decisions
    with open(inYamlFile, 'r') as fin:
        doc = yaml.load(fin)
        I = doc['I']
        J = doc['J']
        K = doc['K']
        T = doc['T']
        cost = doc['cost']
        export = doc['export']
        area = doc['area']
        eta = doc['eta']
        f = doc['f']

        '''
        benefitUnits = {'1_volume': 'Million Gallons', '2_sediment': 'Tons',
                        '3_nitrogen': 'Pounds', '4_phosphorous': 'Pounds'}        
        '''
        benefits = {}
        totalsByBenefit = {}
        totalsByBenefitByZone = {}
        totalsByBenefitByLanduse = {}
        totalsByBenefitByGi = {}
        benefitsByZoneByLanduseByGi = {}
        
        tot = 0.0
        for i in sorted(I):
            for j in sorted(J):
                b_ijt
                if KONJ[j] != None:
                    for k in sorted(KONJ[j]):
                        b_ijk = {}
                        tot_ijk = 0
                        for t in T:
                            benefit = s[i][j][k][t]*x[i][j][k] #individual benefit
                            b_ijk[t] = benefit
                            tot_ijk += benefit
                        
        totalsByBenefit[t] = tot
        solutionDict['totalsByBenefit'] = totalsByBenefit
        print "Actual Benefit Totals:"      
        for t in sorted(totalsByBenefit):
            print "    %s:  %10.4f %s" % (t,totalsByBenefit[t],'fundamental units')
        
        investTotal = 0.0
        for i in sorted(I):
            for j in sorted(J):
                if KONJ[j] != None:
                    for k in sorted(KONJ[j]):
                        spend = x[i][j][k]
                        investTotal += spend
        investTotalMillions = investTotal/1e6
        print "Actual Total Investment Required:   $%10.2f Million" % investTotalMillions
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
    solutionStr = yaml.dump(solutionDict)
    print "\n\nsolutionStr printout:"
    print solutionStr
    return ()
            
def main(inYamlFile):
    with open(inYamlFile, 'r') as fin:
        inYamlDoc = yaml.load(fin)
    decisions = stormwise(inYamlDoc)
#    s = benefit_slopes(inYamlDoc)
#    evaluate_solution(inYamlDoc,decisions)
#    u = upper_bounds(inYamlDoc)
#    evaluate_solution(inYamlDoc,u)

    print "\nDECISIONS:"
    print yaml.dump(decisions)
#    print "\nUPPER BOUNDS:"
#    print yaml.dump(u)
#    print "\nBENEFIT SLOPES:"
#    print yaml.dump(s)


main('wingohocking.yaml')

