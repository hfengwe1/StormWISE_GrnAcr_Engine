# -*- coding: utf-8 -*-
"""
stormwise.py
takes a stormwise input file in YAML format
converts it to an AMPL dat file
and then runs AMPL on the dat file to generate stormwise output
"""
import yaml
from yaml_ampl import yaml_to_ampl
def main():
    with open('wingohocking.yaml', 'r') as fin:
        doc = yaml.load(fin)
        ampl = yaml_to_ampl(doc)
        #docString = yaml.dump(doc, default_flow_style=True)
        #doc2 = yaml.load(docString)
        #yaml_to_ampl(doc2)
    with open('wingohocking.dat', 'w') as fout:     
        fout.write(ampl)
main()

