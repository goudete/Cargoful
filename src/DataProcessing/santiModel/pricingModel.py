import pickle
import numpy as np
import os
from haversine import haversine
import json
from pykml import parser
import heapq

parent_dir = os.path.dirname(os.path.realpath(__file__))

#get dictionary containing parameters for different truck types
pickle_in = open(parent_dir + "/truckParams.pickle","rb")
truckParams = pickle.load(pickle_in)

#get dictionary mapping states to fuel prices
pickle_in = open(parent_dir + "/../DataProcurement/dict.pickle","rb")
fuel_prices_dict = pickle.load(pickle_in)

#get stored tolls/peaje costs.
pickle_in = open(parent_dir + "/../DataProcurement/9_11_15_22.pickle","rb")
tollDict = pickle.load(pickle_in)

#get dictionary of state:[cities].
with open(parent_dir + "/../DataProcurement/headless-chrome/state_city_vals.json", 'r') as f:
    state_city_dict = json.load(f)

#filenames for kml data (has coordinates of cities)
df9 = parent_dir + "/../DataProcurement/DF_9.kml"
guan11 =parent_dir + "/../DataProcurement/Guanajato_11.kml"
mex15 = parent_dir + "/../DataProcurement/Mexico_15.kml"
quer22 = parent_dir + "/../DataProcurement/Queretaro_22.kml"

#given a filename of a kml file and state number (as char) adds coordinates for cities in that state
def addCoords(filename,statenumber):
    with open(filename) as f:
        doc = parser.parse(f).getroot().Document.Folder
    for i,pm in enumerate(doc.Placemark):
        coords = pm.Point.coordinates
        coord_list = coords.text.split(',')[:2]
        coord1 = ''.join([dig for dig in coord_list[0] if (dig.isdigit() or dig in ['.','-'])])
        coord2 = ''.join([dig for dig in coord_list[1] if (dig.isdigit() or dig in ['.','-'])])
        global state_city_dict
        state_city_dict[statenumber][i+1]['coordinates'] = (float(coord2),float(coord1))

#add coordinates for Distrito Federal, state number 9
addCoords(df9,'9')
#add coordinates for Guanajato, state number 11
addCoords(guan11,'11')
#add coordinates for Mexico, state number 15
addCoords(mex15,'15')
#add coordinates for Querataro, state number 22
addCoords(quer22,'22')

currently_stored_states = ['9','11','15','22'] #list of state ids we have toll data for
all_state_list = [] #make list of all cities we have the data for
for i,state in enumerate(currently_stored_states):
    all_state_list += state_city_dict[state][1:]


def getTravelDays(km,truck_type,rtrn=False):
    """
    returns estimated duration of the delivery journey (in days).

    @param km: number of kilometers between origin and destination
    @param rtrn: boolean variable, if true then return hours are factored in. default False.
    """
    velocidad = 75 #km/hr
    #calculate rest hours
    if km < 901:
        descanso = 0
    elif km >= 901 and km < 1801:
        descanso = 8
    elif km >= 1801 and km < 2701:
        descanso = 16
    else:
        descanso = 24
    #calculate travel hours
    viaje = km/velocidad
    #If we have to factor in the return journey, multiply travel hours by 2
    if rtrn:
        viaje = viaje*2

    horas_fijas = truckParams[truck_type]['Horas Fijas']

    return (viaje+horas_fijas)/24

def getToll(km,truck_type,start_lat,start_long,dest_lat,dest_long,radius=100):
    closest2start = heapq.nsmallest(1,all_state_list,
                                    key = lambda dic: (haversine((start_lat,start_long),(dic['coordinates']))))

    dist2start = haversine((start_lat,start_long),(closest2start[0]['coordinates']))

    closest2dest = heapq.nsmallest(1,all_state_list,
                                   key = lambda dic: haversine((dest_lat,dest_long),(dic['coordinates'])))

    dist2dest = haversine((dest_lat,dest_long),(closest2dest[0]['coordinates']))
    if (dist2start <= radius and dist2dest <= radius): #if we have data for both origin and destination area
        toll = tollDict[frozenset({closest2start[0]['value'],closest2dest[0]['value']})][2]
        return float(toll)
    else: #if not
        toll = km*truckParams[truck_type]['Toll Roads Price per Km']
        return toll

def pricing_model(precio_combustible,km,truck_type,rtrn=False,iva=False,utilidad=0.35,viaticos_por_dia = 75,
                  dias_efectivos_trabajo = 22,
                  aceite_anticongelante_precio=3500,aceite_anticongelante_km=25000,
                  llantas_precio=5000*10,llantas_km=150000,
                  reparaciones_precio=5000,reparaciones_km=5000,
                  rendimiento_por_km_con_carga = 3, rendimiento_por_km_sin_carga = 3.5,
                  sueldo_bruto = 600, seguro=0, telecomunicaciones=0, monitoreo=0, gastos_administracion=1000,
                  inversion=0,additional_diesel_lts_per_hr=0):
    """
    returns approximate delivery cost for a given journey, for a Torton type truck.
    @param precio_combustible: per liter price of petrol (E21)
    @param km: number of kilometers between origin and destination

    @param rtrn: boolean variable, if true then return costs are added to one-way cost. default False.
    @param iva: boolean variable, if true then VAT is added to fuel cost. default False.
    @param viaticos_por_dia. per day pocket money for driver. default is 75 (pesos) (E43)
    @param aceite_anticongelante_precio: price of the required maintenance ($) (E29)
    @param aceite_anticongelante_km: how many km between maintenance procedures (E28)
    @param  llantas_precio: price of the required maintenance ($) (E32)
    @param llantas_km: how many km between maintenance procedures (E31)
    @param reparaciones_precio: price of required maintenance (E35)
    @param reparaciones_km: how many km between maintenance procedures (E34)
    @param rendimiento_por_km_con_carga: number of liters of petrol consumed per km with cargo (E23)
    @param rendimiento_por_km_sin_carga: number of liters of petrol consumed per km without cargo (E24)
    """

    #-------------------------- Calculate Variable Costs --------------------------
    aceite_per_km = aceite_anticongelante_precio/aceite_anticongelante_km
    rep_per_km = reparaciones_precio/reparaciones_km
    llantas_per_km = llantas_precio/llantas_km
    maintenance_per_km = aceite_per_km + rep_per_km + llantas_per_km
    maintenance_total = maintenance_per_km*km
    if rtrn:
        maintenance_total = maintenance_total*2
    print("maintenance total is : " + str(maintenance_total))

    rendimiento_por_km_con_carga = rendimiento_por_km_con_carga
    if not(iva):
        precio_combustible = precio_combustible/1.16
    price_per_km = precio_combustible/rendimiento_por_km_con_carga
    petrol_total = price_per_km*km
    if rtrn:
        return_price_per_km = precio_combustible/rendimiento_por_km_sin_carga
        petrol_return = return_price_per_km*km
        petrol_total = petrol_total + petrol_return

    print("petrol total is : " + str(petrol_total))

    dias_viaje = getTravelDays(km,truck_type,rtrn)
    viaticos_total = dias_viaje*viaticos_por_dia

    print("viaticos total is : " + str(viaticos_total))

    variable_cost = maintenance_total + petrol_total + viaticos_total

    #-------------------------- Calculate Fixed Costs --------------------------
    carga_social = sueldo_bruto*0.3
    gasto_salarios = carga_social + sueldo_bruto
    gasto_salarios_viaje = (gasto_salarios/dias_efectivos_trabajo)*dias_viaje

    otros = seguro + telecomunicaciones + monitoreo + gastos_administracion
    if not(iva):
        otros = otros/1.16

    otros_viaje = (otros/dias_efectivos_trabajo)*dias_viaje

    vida_util = 20
    depreciacion_mensual = inversion/(12*vida_util)
    depreciacion_viaje = (depreciacion_mensual/dias_efectivos_trabajo)*dias_viaje

    fixed_cost = depreciacion_viaje + gasto_salarios_viaje + otros_viaje

    utilidad_cost = (variable_cost+fixed_cost)/(1-utilidad)-(variable_cost+fixed_cost)
    return (variable_cost + fixed_cost + utilidad_cost)

def calculatePrice(km,start_state,dest_state,truck_type,
                   start_lat,start_long,dest_lat,dest_long,
                   rtrn=False,iva=False):
    variables = truckParams[truck_type]
    #we need a dictionary to map some google maps state names to the ones in the fuel price document.
    gmaps2fuel_dict = {'Mexico City':'Ciudad de México','Coahuila':'Coahuila de Zaragoza','Michoacán':'Michoacán de Ocampo',
                       'State of Mexico':'México','Nuevo Leon':'Nuevo León','Veracruz':'Veracruz de Ignacio de la Llave',
                       'Yucatan':'Yucatán'}
    #similarly need a conversion for names for the fuel type
    fuel_type_dict = {'Diesel':'Diésel','Gasolina':'Gasolina mínimo 87 octanos'}
    fuel_type = fuel_type_dict[variables['Tipo Combustible']]
    #If we have any of the states listed above, apply the hardcoded conversion
    if start_state in gmaps2fuel_dict:
        start_state = gmaps2fuel_dict[start_state]
    if dest_state in gmaps2fuel_dict:
        dest_state = gmaps2fuel_dict[end_state]
    #if for some reason either of the states are not in the fuel_prices_dict, just take average of all prices
    #otherwise we take average of startstate prices and end state prices
    if (start_state not in fuel_prices_dict) or (dest_state not in fuel_prices_dict):
        precio_combustible = np.mean([fuel_type_dict[state][fuel_type] for state in fuel_type_dict])
    else:
        precio_combustible = (0.5*fuel_prices_dict[start_state][fuel_type]+ 0.5*fuel_prices_dict[dest_state][fuel_type])

    params = {}
    #turn variables into parameters we can feed the pricing model.
    params['viaticos_por_dia'] = variables['Viaticos X Día ($)']
    params['aceite_anticongelante_precio'] = variables['Cambio Aceite y Anticongelante ($)']
    params['aceite_anticongelante_km'] = variables['Cambio Aceite y Anticongelante (Kms)']
    params['llantas_precio'] = variables['Cambio Llantas ($)']
    params['llantas_km'] = variables['Cambio Llantas (Kms)']
    params['reparaciones_precio'] = variables['Reparaciones ($)']
    params['reparaciones_km'] = variables['Reparaciones (Kms)']
    params['rendimiento_por_km_con_carga'] = variables['Rendimiento por Kilómetro con Carga']
    params['rendimiento_por_km_sin_carga'] = variables['Rendimiento por Kilómetro sin Carga']
    params['sueldo_bruto'] = variables['Sueldo Bruto']
    params['seguro'] = variables['Seguro']
    params['telecomunicaciones'] = variables['Telecomunicaciones']
    params['monitoreo'] = variables['Monitoreo']
    params['gastos_administracion'] = variables['Gastos Administración']
    params['inversion'] = variables['Inversion']
    params['additional_diesel_lts_per_hr']  = variables['[Refrigerated Only] Additional Diesel Lts. Per Hour Full']
    params['additional_diesel_lts_per_hr']  = 0 #until we get the actual numbers
    truckCategory = variables['SCTCategory']

    peaje = getToll(km,truck_type,start_lat,start_long,dest_lat,dest_long)
    if rtrn:
        peaje = peaje*2

    model_cost = pricing_model(precio_combustible,km,truck_type,rtrn,iva,**params)
    return round(peaje + model_cost)



#def main():
#    print("testing")
#
#if __name__ == '__main__':
#    main()
#args = {'km':201,'start_state':'Aguascalientes','start_city':'Aguascalientes',
#    'dest_state':'Baja California','dest_city':'Cantamar','truck_type':'Low Boy'}
#price = calculatePrice(**args)
#print(price)
