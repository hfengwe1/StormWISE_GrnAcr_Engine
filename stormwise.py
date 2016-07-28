# -*- coding: utf-8 -*-
"""
stormwise.py
takes a stormwise input file in YAML format
converts it to an AMPL dat file
and then runs AMPL on the dat file to generate stormwise output
"""
import yaml
from subprocess import call
from yaml_ampl import yaml_to_ampl
def stormwise(inYamlFile):
    with open(inYamlFile, 'r') as fin:
        doc = yaml.load(fin)
        ampl = yaml_to_ampl(doc)
        # store the structure of the problem as found in the YAML file
        #I = doc['I']
        #J = doc['J']
        #K = doc['K']
        #KONJ = doc['KONJ']
        #T = doc['T']
        #convert = doc['convert']
    with open('min_cost.dat', 'w') as fout:     
        fout.write(ampl)
        fout.close()
    call(["/Applications/amplide.macosx64/ampl","min_cost.run"])
    with open('min_cost.yaml', 'r') as fin:
        solution = yaml.load(fin)
        x = solution['x']
        return x
        #u = solution['u']
        #s = solution['s']
def upper_bounds(inYamlFile):
    with open(inYamlFile, 'r') as fin:
        doc = yaml.load(fin)
        I = doc['I']
        J = doc['J']
        K = doc['K']
        KONJ = doc['KONJ']
        cost = doc['cost']
        f = doc['f']
        area = doc['area']
        u = {}  # will be a dictionary of dictionaries
        for i in sorted(I):
            uj = {}
            for j in sorted(J):
                uk = {}
                if KONJ[j] != None:
                    for k in sorted(KONJ[j]):
                        uk[k] = cost[k][j]*f[k][j][i]*area[j][i]
                    uj[j] = uk
            u[i] = uj
        return u
    
def evaluate_solution(inYamlFile,x):
    #with open('min_cost.yaml', 'r') as fin:
        #solution = yaml.load(fin)
        #x = solution['x']
        #u = solution['u']
        #s = solution['s']        
        # PRINT OUT RESULTS TO CONSOLE:
    with open(inYamlFile, 'r') as fin:
        doc = yaml.load(fin)
        I = doc['I']
        J = doc['J']
        K = doc['K']
        KONJ = doc['KONJ']
        T = doc['T']
        convert = doc['convert']
        cost = doc['cost']
        export = doc['export']
        #print export
        area = doc['area']
        eta = doc['eta']
        f = doc['f']
        # Compute benefit slopes
        s = {}   # will be a dictionary of dictionaries
        for i in sorted(I):
            sj = {}
            for j in sorted(J):
                sk = {}
                if KONJ[j] != None:
                    for k in sorted(KONJ[j]):
                        st = {}
                        for t in T:
                            st[t] = eta[t][k][i]*export[t][j]/cost[k][j]
                        sk[k] = st
                    sj[j] = sk
            s[i] = sj
        #print s
        # Compute investment upper bounds:
        '''
        u = {}  # will be a dictionary of dictionaries
        for i in sorted(I):
            uj = {}
            for j in sorted(J):
                uk = {}
                if KONJ[j] != None:
                    for k in sorted(KONJ[j]):
                        uk[k] = cost[k][j]*f[k][j][i]*area[j][i]
                    uj[j] = uk
            u[i] = uj
        '''


        benefitUnits = {'1_volume': 'Million Gallons', '2_sediment': 'Tons',
                        '3_nitrogen': 'Pounds', '4_phosphorous': 'Pounds'}        
        '''
        print ""
        maxBenefitTotal = {}
        for t in T:
            maxtot = 0.0
            for i in sorted(I):
                for j in sorted(J):
                    if KONJ[j] != None:
                        for k in sorted(KONJ[j]):
                            spend = u[i][j][k]
                            maxtot += convert[t]*s[i][j][k][t]*spend
            maxBenefitTotal[t] = maxtot
        print "Maximum Benefit Totals:"      
        for t in sorted(maxBenefitTotal):
            print "    %s:  %10.4f %s" % (t,maxBenefitTotal[t],benefitUnits[t])

        maxInvestTotal = 0.0
        for i in sorted(I):
            for j in sorted(J):
                if KONJ[j] != None:
                    for k in sorted(KONJ[j]):
                        spend = u[i][j][k]
                        maxInvestTotal += spend
        maxInvestMillions = maxInvestTotal/1e6
        print "Maximum Total Investment Required:   $%10.2f Million" % maxInvestMillions
        print ""
        '''
        benefitTotal = {}
        for t in T:
            tot = 0.0
            for i in sorted(I):
                for j in sorted(J):
                    if KONJ[j] != None:
                        for k in sorted(KONJ[j]):
                            spend = x[i][j][k]
                            tot += convert[t]*s[i][j][k][t]*spend
            benefitTotal[t] = tot
        print "Actual Benefit Totals:"      
        for t in sorted(benefitTotal):
            print "    %s:  %10.4f %s" % (t,benefitTotal[t],benefitUnits[t])
        
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
    return ()

def storm_max(inYamlFile):
    with open(inYamlFile, 'r') as fin:
        doc = yaml.load(fin)
        #ampl = yaml_to_ampl(doc)
        # store the structure of the problem as found in the YAML file
        I = doc['I']
        J = doc['J']
        K = doc['K']
        KONJ = doc['KONJ']
        T = doc['T']
        convert = doc['convert']
        cost = doc['cost']
        export = doc['export']
        #print export
        area = doc['area']
        eta = doc['eta']
        f = doc['f']
        # Compute benefit slopes
        s = {}   # will be a dictionary of dictionaries
        for i in sorted(I):
            sj = {}
            for j in sorted(J):
                sk = {}
                if KONJ[j] != None:
                    for k in sorted(KONJ[j]):
                        st = {}
                        for t in T:
                            st[t] = eta[t][k][i]*export[t][j]/cost[k][j]
                        sk[k] = st
                    sj[j] = sk
            s[i] = sj
        #print s
        # Compute investment upper bounds:
        u = {}  # will be a dictionary of dictionaries
        for i in sorted(I):
            uj = {}
            for j in sorted(J):
                uk = {}
                if KONJ[j] != None:
                    for k in sorted(KONJ[j]):
                        uk[k] = cost[k][j]*f[k][j][i]*area[j][i]
                    uj[j] = uk
            u[i] = uj
        #print u        
#param s{i in I,j in J,k in KONJ[j],t in T} = eta[i,k,t]*export[j,t]/cost[j,k];	# calculated benefit slopes
#param u{i in I,j in J,k in KONJ[j]} = cost[j,k]*f[i,j,k]*area[i,j];				# calculated upper spending limits

        
    #with open('wingohocking.dat', 'w') as fout:     
    #    fout.write(ampl)
    #    fout.close()
    #call(["/Applications/amplide.macosx64/ampl","min_cost.run"])
    #with open('min_cost.yaml', 'r') as fin:
    #    solution = yaml.load(fin)
    #    x = solution['x']
    #    u = solution['u']
     #   s = solution['s']
        
        # PRINT OUT RESULTS TO CONSOLE:


        benefitUnits = {'1_volume': 'Million Gallons', '2_sediment': 'Tons',
                        '3_nitrogen': 'Pounds', '4_phosphorous': 'Pounds'}        
        print ""
        maxBenefitTotal = {}
        for t in T:
            maxtot = 0.0
            for i in sorted(I):
                for j in sorted(J):
                    if KONJ[j] != None:
                        for k in sorted(KONJ[j]):
                            spend = u[i][j][k]
                            maxtot += convert[t]*s[i][j][k][t]*spend
            maxBenefitTotal[t] = maxtot
        print "Maximum Benefit Totals:"      
        for t in sorted(maxBenefitTotal):
            print "    %s:  %10.4f %s" % (t,maxBenefitTotal[t],benefitUnits[t])

        maxInvestTotal = 0.0
        for i in sorted(I):
            for j in sorted(J):
                if KONJ[j] != None:
                    for k in sorted(KONJ[j]):
                        spend = u[i][j][k]
                        maxInvestTotal += spend
        maxInvestMillions = maxInvestTotal/1e6
        print "Maximum Total Investment Required:   $%10.2f Million" % maxInvestMillions

            
#stormwise()
def main(inYamlFile):
    x = stormwise(inYamlFile)
    evaluate_solution(inYamlFile,x)
    u = upper_bounds(inYamlFile)
    evaluate_solution(inYamlFile,u)


main('wingohocking.yaml')

