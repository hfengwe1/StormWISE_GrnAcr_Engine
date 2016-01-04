# -*- coding: utf-8 -*-
import yaml
	
def yaml_to_ampl(doc):
    sets = ['I','J','K','T'] # I = zone, J = landuse, K = GItype, T = benefit
    #ret = ""
    for s in sets:  
        print "set %s := " % s,
        #ret = ret + "set %s := " % s, 
        x = list(doc[s])   
        for h in sorted(x):
            print "%s" % h,
        print ";"
    setsonset = {'KONJ': ('K','J')}
    for s in sorted(setsonset):
        s1 = setsonset[s][1]
        x = list(doc[s1])
        for h in sorted(x):
            print "set %s[%s] := " % (s,h),
            value = doc[s][h]
            if value == None:
                value = "" 
            print "%s;" % value
    params_1d = {'convert': 'T'}
    #x = doc['convert']
    #print sorted(x)
    #print doc['convert']['1_volume']
    for p in sorted(params_1d):
        print "param %s := " % p
        s = params_1d[p]
        x = list(doc[s])
        for h in sorted(x):
            value = doc[p][h]
            if value == None:
                value = '.'  # Ampl data file notation for null value
            print "    %s %s" % (h,value)
        print ";"
    params_2d = {'cost': ('J','K'),   # specify (row,column)
                 'export': ('J','T'),
                 'area': ('I','J'),}
    for p in sorted(params_2d):
        print "param %s :" % p,
        s = params_2d[p]
        s0 = s[0] # rows set
        s1 = s[1] # columns set
        x = list(doc[s1])  # contains column names
        for h in sorted(x):
            print " %s" % h,
        print ":="
        y = list(doc[s0])  # contains row names
        for g in sorted(y):
            print "    %s " % g,
            for h in sorted(x):
                value = doc[p][h][g]
                if value == None:
                    value = '.'  # Ampl data file notation for null value
                print " %s" % value,
            print ""
        print ";"
    params_3d = {'eta': ('I','K','T'),
                 'f': ('I','J','K')}
    for p in sorted(params_3d):
        print "param %s :=" % p
        s = params_3d[p]
        s0 = s[0] # rows set
        s1 = s[1] # columns set
        s2 = s[2] # layers set
        z = list(doc[s2])  # contains layer names
        y = list(doc[s1])  # contains row names
        x = list(doc[s0])  # contains column names
        for e in sorted(z):
            print "    [*,*,%s]:" % e,
            for g in sorted(y):
                print " %s" % g,
            print ":="
            #print doc['eta']['1_volume']['1_bioswale']['1_headwaters']

            for h in sorted(x):
                print "    %s" % h,
                for g in sorted(y):
                    value = doc[p][e][g][h]
                    if value == None:
                        value = '.' # Ampl data file notation for null value
                    print " %s" % value,
            print ""
        print ";"

def main():
    with open('wingohocking.yaml', 'r') as f:
        doc = yaml.load(f)
        yaml_to_ampl(doc)
        docString = yaml.dump(doc, default_flow_style=True)
        doc2 = yaml.load(docString)
        yaml_to_ampl(doc2)
        print docString

main()



