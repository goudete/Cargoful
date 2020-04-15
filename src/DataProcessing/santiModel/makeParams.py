"""
Author: Luis Costa
email: lcosta@cargoful.org

This script takes an excel spreadsheet 'AlgorithmVariables.xlsx' containing variables associated with different truck types that
are to be used in the pricing model. This script converts the data into a dictionary where the keys are the truck types and the
values are dictionaries mapping the variable names to the value for that truck type. This dictionary is then saved as truckParams.pickle.
"""

import pandas as pd
import pickle

df = pd.read_excel('AlgorithmVariables.xlsx',header=1)
varNames = list(df['Variable Name'])

paramDicts ={}
for i,row in enumerate(df):
    variables = list(df[row])
    if i>=2:
        paramDicts[row] = {}
        for i,var in enumerate(variables):
            paramDicts[row][varNames[i]] = var
pickle_out = open("truckParams.pickle","wb")

pickle.dump(paramDicts, pickle_out)
pickle_out.close()