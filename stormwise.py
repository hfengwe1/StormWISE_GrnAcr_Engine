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
def main():
    with open('wingohocking.yaml', 'r') as fin:
        doc = yaml.load(fin)
        ampl = yaml_to_ampl(doc)
        # store the structure of the problem as found in the YAML file
        I = doc['I']
        J = doc['J']
        KONJ = doc['KONJ']
        KONJ2 = doc['KONJ2']
        T = doc['T']
    with open('wingohocking.dat', 'w') as fout:     
        fout.write(ampl)
        fout.close()
    call(["/Applications/amplide.macosx64/ampl","min_cost.run"])
    with open('min_cost.yaml', 'r') as fin:
        solution = yaml.load(fin)
        x = solution['x']
        u = solution['u']
        s = solution['s']
        print ""
        maxBenefitTotal = {}
        for t in T:
            maxtot = 0.0
            for i in sorted(I):
                for j in sorted(J):
                    if KONJ[j] != None:
                        for k in sorted(KONJ[j]):
                            spend = u[i][j][k]
                            maxtot += s[i][j][k][t]*spend
            maxBenefitTotal[t] = maxtot
        print "Maximum Benefit Totals:"      
        for t in sorted(maxBenefitTotal):
            print "    %s:  %10.4f" % (t,maxBenefitTotal[t])

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
        benefitTotal = {}
        for t in T:
            tot = 0.0
            for i in sorted(I):
                for j in sorted(J):
                    if KONJ[j] != None:
                        for k in sorted(KONJ[j]):
                            spend = x[i][j][k]
                            tot += s[i][j][k][t]*spend
            benefitTotal[t] = tot
        print "Actual Benefit Totals:"      
        for t in sorted(benefitTotal):
            print "    %s:  %10.4f" % (t,benefitTotal[t])
        
        investTotal = 0.0
        for i in sorted(I):
            for j in sorted(J):
                if KONJ[j] != None:
                    for k in sorted(KONJ[j]):
                        spend = x[i][j][k]
                        investTotal += spend
        investMillions = investTotal/1e6
        print "Actual Total Investment Required:   $%10.2f Million" % investMillions
        
main()

