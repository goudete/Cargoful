"""
Author: Luis Costa
email: lcosta@cargoful.org

This script converts fuel price data for different Mexican states in the file PreciosPromedioMensuales.csv to a dictionary
mapping the name of a state to gasolina and diesel prices. This dictionary is saved in the working directory as 'dict.pickle'
so that it can be loaded by other scripts.

Data from https://datos.gob.mx/busca/dataset/ubicacion-de-gasolineras-y-precios-comerciales-de-gasolina-y-diesel-por-estacion/resource/8b8b3e9a-3d2c-40b8-bf7c-2abd51b27964
"""
import pandas as pd
import numpy as np 
import pickle

#load data as pandas dataframe
file ="PreciosPromedioMensuales.csv"
df = pd.read_csv(file,header=1,encoding='latin-1')

state_list = list(np.unique(df['Entidad federativa'])) #list of states

#each entry in price_dict is of the form          state : {'Gasolina mínimo 87 octanos':price, 'Diésel': price}
prices_dict = {}
for state in state_list:
    state_entries = df.loc[df['Entidad federativa'] == state]
    most_recent = state_entries.iloc[-1] #get last entry for prices for that state i.e. most recently recorded.
    gasolina_price = most_recent['Gasolina mínimo 87 octanos']
    diesel_price = most_recent['Diésel']
    prices_dict[state] = {'Gasolina mínimo 87 octanos':gasolina_price,'Diésel':diesel_price}

pickle_out = open("dict.pickle","wb")
pickle.dump(prices_dict, pickle_out)
pickle_out.close()