
# -*- coding: utf-8 -*-
"""
stormwise_grnacr.py

stormwise() function:
	takes a stormwise input file in YAML format
	computes benefit slopes and investment upper bounds
	outputs an AMPL dat file
	and then runs AMPL on the dat file to generate stormwise_grnacr output

evaluate_solution() function:
	takes dictionaries containing a solution, benefit slopes, and the YAML document defining the problem
	and produces a large solutionDict dictionary containing multiple dictionaries for displaying totals
	of investment decisions and benefits
"""
import os
os.chdir('C:\StormWISE_GrnAcr_Cml')  # for my computer only

import yaml
import subprocess
from StormWISE_GrnAcr_Engine.stormwise_grnacr_ampl import generate_ampl_dat_file
from StormWISE_GrnAcr_Engine.stormwise_grnacr_ampl import generate_ampl_benefit_file
# from StormWISE_GrnAcr_Engine.stormwise_grnacr_benefits_and_bounds import benefit_slopes

def stormwise(amplPath,inYamlDoc,benefitDict):
    amplDat = generate_ampl_dat_file(inYamlDoc)
    # store the structure of the problem as found in the YAML file
    with open('stormwise_com.dat', 'w') as fout:     
        fout.write(amplDat)
        fout.close()

    amplBenefits = generate_ampl_benefit_file(benefitDict)
    with open('stormwise_com_benefits.dat', 'w') as fout:
        fout.write(amplBenefits)
        fout.close()
    cmd=[amplPath,"stormwise_com.run"]
    subprocess.call(cmd,shell='true')
    subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    with open('stormwise_com.yaml', 'r') as fin:
        solution = yaml.load(fin)
        x = solution['x']
        I = inYamlDoc['I']
        J = inYamlDoc['J']
        K = inYamlDoc['K']
        KONJ = inYamlDoc['KONJ']
        # generate decision variable dictionary filling in zeros where necessary
        decisions = {}
        for i in I:  
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




def evaluate_solution(decisions,s,inYamlDoc):
    solutionDict = {}
    solutionDict['decisions'] = decisions
    I = inYamlDoc['I']
    J = inYamlDoc['J']
    K = inYamlDoc['K']
    T = inYamlDoc['T']

#  EVALUATE INVESTMENT SOLUTIONS:
    investmentTotal = 0.0  #  will contain scalar value containing the total optimal investment ($)
# Investment Totals Dictionaries:
    invTotsByZone = {}   #  [i]
    invTotsByLanduse = {}  # [j]
    invTotsByGi = {}  # [k]
    invTotsByZoneByLanduse = {}  # [i][j]
    invTotsByZoneByGi = {}   # [i][k]
    invTotsByLanduseByGi = {}  #  [j][k]

# Calculate investmentTotal:
    for i in I:
        for j in J:
            for k in K:
                investmentTotal += decisions[i][j][k]
    solutionDict['investmentTotal'] = investmentTotal

# Investment totals by Zone:
    for i in I:
        tot = 0.0
        for j in J:
            for k in K:
                tot += decisions[i][j][k]
        invTotsByZone[i] = tot
    solutionDict['invTotsByZone'] = invTotsByZone 
# Investment totals by Landuse:
    for j in J:
        tot = 0.0
        for i in I:
            for k in K:
                tot += decisions[i][j][k]
        invTotsByLanduse[j] = tot
    solutionDict['invTotsByLanduse'] = invTotsByLanduse
# Investment totals by GI technology
    for k in K:
        tot = 0.0
        for i in I:
            for j in J:
                tot += decisions[i][j][k]
        invTotsByGi[k] = tot
    solutionDict['invTotsByGi'] = invTotsByGi
# Investment totals by Zone by Landuse:
    for i in I:
        jDict = {}
        for j in J:
            tot = 0.0
            for k in K:
                tot += decisions[i][j][k]
            jDict[j] = tot
        invTotsByZoneByLanduse[i] = jDict
    solutionDict['invTotsByZoneByLanduse'] = invTotsByZoneByLanduse
# Investment totals by Zone by Gi:
    for i in I:
        kDict = {}
        for k in K:
            tot = 0.0
            for j in J:
                tot += decisions[i][j][k]
            kDict[k] = tot
        invTotsByZoneByGi[i] = kDict
    solutionDict['invTotsByZoneByGi'] = invTotsByZoneByGi
# Investment totals by Landuse by Gi:
    for j in J:
        kDict = {}
        for k in K:
            tot = 0.0
            for i in I:
                tot += decisions[i][j][k]
            kDict[k] = tot
        invTotsByLanduseByGi[j] = kDict
    solutionDict['invTotsByLanduseByGi'] = invTotsByLanduseByGi

#  EVALUATE BENEFIT SOLUTIONS:

#  BENEFIT FUNDAMENTAL UNITS USED IN STORMWISE ENGINE:
	# Volume: cubic meters
	# Pollutant Mass:  kilograms
	# Land Area:  hectare (10^4 square meter)

	# Obsolete:  it is now the responsibility of the displaying functions to convert units
    '''
    benefitUnits = {'1_volume': 'Million Gallons', '2_sediment': 'Tons',
                    '3_nitrogen': 'Pounds', '4_phosphorous': 'Pounds'}        
    '''

    benefits = {}   # 4-D dictionary of dictionaries [i][j][k][t]
    benefitsByZoneByLanduseByGi = {}   # benefits first 4-D dictionary of dictionaries [t][i][j][k]

    #benefit totals dictionaries:  all have [t] first
    benTotsByBenefit = {}    # [t]
    benTotsByBenefitByZone = {}   # [t][i]
    benTotsByBenefitByLanduse = {}   # [t][j]
    benTotsByBenefitByGi = {}    # [t][k]
    benTotsByBenefitByZoneByLanduse = {}   # [t][i][j]
    benTotsByBenefitByZoneByGi = {}    # [t][i][k]
    benTotsByBenefitByLanduseByGi = {}   # [t][j][k]

# Individual BENEFITS BY ZONE BY LANDUSE BY GI BY BENEFIT CATEGORY:    
    #print "Individual benefits by zone by landuse by GI by benefit category (I,J,K,T):"
    for i in sorted(I):
        jDict = {}
        for j in sorted(J):
            kDict = {}
            for k in sorted(K):
                tDict = {}
                for t in sorted(T):
                    tDict[t] = s[i][j][k][t]*decisions[i][j][k] #individual benefit
                kDict[k] = tDict
            jDict[j] = kDict
        benefits[i] = jDict
    #benefitsYaml = yaml.dump(benefits)
    #print benefitsYaml
    solutionDict['benefits'] = benefits
# INDIVIDUAL BENEFITS BY BENEFIT CATEGORY BY ZONE BY LANDUSE BY GI:   
    #print "Individual benefits by benefit category by zone by landuse by GI (T,I,J,K)" 
    for t in sorted(T):
        iDict = {}
        for i in sorted(I):
            jDict = {}
            for j in sorted(J):
                kDict = {}
                for k in sorted(K):
                    kDict[k] =  benefits[i][j][k][t]
                jDict[j] = kDict
            iDict[i] = jDict
        benefitsByZoneByLanduseByGi[t] = iDict
    #totsYaml = yaml.dump(benefitsByZoneByLanduseByGi)
    #print totsYaml     
    solutionDict['benefitsByZoneByLanduseByGi'] = benefitsByZoneByLanduseByGi
# TOTALS BY BENEFIT CATEGORY:   
    #print "Total benefits by benefit category (T):" 
    for t in sorted(T):
        tot_t = 0.0
        for i in sorted(I):
            for j in sorted(J):
                for k in sorted(K):
                    value = benefits[i][j][k][t]
                    tot_t += value                    
        benTotsByBenefit[t] = tot_t
    solutionDict['benTotsByBenefit'] = benTotsByBenefit
#   TOTALS BY BENEFIT CATEGORY BY ZONE:
    #print "Total benefits by benefit category by zone (T,I):"
    for t in sorted(T):
        iDict = {}
        for i in sorted(I):
            tot_ti = 0.0
            for j in sorted(J):
                for k in sorted(K):
                    tot_ti += benefits[i][j][k][t]
            iDict[i] = tot_ti
        benTotsByBenefitByZone[t] = iDict
    solutionDict['benTotsByBenefitByZone'] = benTotsByBenefitByZone
    #totsYaml = yaml.dump(benTotsByBenefitByZone)
    #print totsYaml
# TOTALS BY BENEFIT CATEGORY BY LANDUSE:
    #print "Total benefits by benefit category by landuse (T,J):"
    for t in sorted(T):
        jDict = {}
        for j in sorted(J):
            tot_tj = 0.0
            for i in sorted(I):
                for k in sorted(K):
                    tot_tj += benefits[i][j][k][t]
            jDict[j] = tot_tj
        benTotsByBenefitByLanduse[t] = jDict
    solutionDict['benTotsByBenefitByLanduse'] = benTotsByBenefitByLanduse
    #totsYaml = yaml.dump(benTotsByBenefitByLanduse)
    #print totsYaml 
# TOTALS BY BENEFIT CATEGORY BY GI:
    #print "Total benefits by benefit category by gi technology (T,K):"    
    for t in sorted(T):
        kDict = {}
        for k in sorted(K):
            tot_tk = 0.0
            for i in sorted(I):
                for j in sorted(J):
                    tot_tk += benefits[i][j][k][t]
            kDict[k] = tot_tk
        benTotsByBenefitByGi[t] = kDict
    solutionDict['benTotsByBenefitByGi'] = benTotsByBenefitByGi
    #totsYaml = yaml.dump(benTotsByBenefitByGi)
    #print totsYaml 

    
# TOTALS BY BENEFIT BY ZONE BY LANDUSE:
    #print "Total benefits by benefit category by zone by landuse (T,I,J):"
    for t in sorted(T):
        iDict = {}
        for i in sorted(I):
            jDict = {}
            for j in sorted(J):
                tot_k = 0.0
                for k in sorted(K):
                    tot_k += benefits[i][j][k][t]
                jDict[j] = tot_k
            iDict[i] = jDict
        benTotsByBenefitByZoneByLanduse[t] = iDict
    solutionDict['benTotsByBenefitByZoneByLanduse'] = benTotsByBenefitByZoneByLanduse
    #totsYaml = yaml.dump(benTotsByBenefitByZoneByLanduse)
    #print totsYaml 
            
# TOTALS BY BENEFIT BY ZONE BY GI:
    #print "Total benefits by benefit category by zone by gi technology (T,I,K)"
    for t in sorted(T):
        iDict = {}
        for i in sorted(I):
            kDict = {}
            for k in sorted(K):
                tot_j = 0.0
                for j in sorted(J):
                    tot_j += benefits[i][j][k][t]
                kDict[k] = tot_j
            iDict[i] = kDict
        benTotsByBenefitByZoneByGi[t] = iDict
    solutionDict['benTotsByBenefitByZoneByGi'] = benTotsByBenefitByZoneByGi
    #totsYaml = yaml.dump(benTotsByBenefitByZoneByGi)
    #print totsYaml 

# TOTALS BY BENEFIT BY LANDUSE BY GI:
    #print "Total benefits by benefit category by landuse by gi technology (T,J,K):"
    for t in sorted(T):
        jDict = {}
        for j in sorted(J):
            kDict = {}
            for k in sorted(K):
                tot_i = 0.0
                for i in sorted(I):
                    tot_i += benefits[i][j][k][t]
                kDict[k] = tot_i
            #print "j = %s" % j
            jDict[j] = kDict
        benTotsByBenefitByLanduseByGi[t] = jDict
    solutionDict['benTotsByBenefitByLanduseByGi'] = benTotsByBenefitByLanduseByGi
    #totsYaml = yaml.dump(benTotsByBenefitByLanduseByGi)
    #print totsYaml 
    return(solutionDict)  
