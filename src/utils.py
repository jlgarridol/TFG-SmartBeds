import matplotlib.pyplot as plt
import pandas as pd

def start_end(datosPartHour):
    MIN5 = 300 #Segundos de 5 minutos
    # Horas de inicio y final de cada crisis
    inicio = None
    final  = None

    #Cálculo del comienzo y del final
    b = False
    for index,row in datosPartHour.iterrows():
        if not b and row['target']:
            inicio = row['DateTime']
        elif b and not row['target']:
            final = row['DateTime']-pd.to_timedelta(1,unit='s') #Segundo anterior
        b = row['target']

    assert not(inicio is None) and not(final is None), 'No hay inicio o final'

    inicio_5 = inicio+pd.to_timedelta(MIN5,unit='s')
    final_5 = final-pd.to_timedelta(MIN5,unit='s')
    return inicio, inicio_5, final_5, final

def dibujado(data_raw,data,col='P1',title=''):
    
    inicio, inicio_5, final_5, final = start_end(data)
    
    plt.figure(figsize=(128,16))
    
    aCrt = data['DateTime'].map(lambda x: x < inicio)
    dCrt = data['DateTime'].map(lambda x: x > final)
    fCrt = (data['DateTime'].map(lambda x: x >= inicio)) & (data['DateTime'].map(lambda x: x <= inicio_5))
    lCrt = (data['DateTime'].map(lambda x: x >= final_5)) & (data['DateTime'].map(lambda x: x <= final))
    mCrt = (data['DateTime'].map(lambda x: x > inicio_5)) & (data['DateTime'].map(lambda x: x < final_5))
    
    antes = data[aCrt]
    despues = data[dCrt]
    first5 = data[fCrt]
    last5 = data[lCrt]
    med = data[mCrt]
    
    antes_r = data_raw[aCrt]
    despues_r = data_raw[dCrt]
    first5_r = data_raw[fCrt]
    last5_r = data_raw[lCrt]
    med_r = data_raw[mCrt]
    
    colors = ['navy','gold','k','tomato','darkgreen','deeppink','maroon','yellow','chocolate','aqua']
    states = [antes_r,antes,despues_r,despues,first5_r,first5,med_r,med,last5_r,last5]
    pos = ['Before Raw','Before','After Raw', 'After','First 5 min Raw','First 5 min',
           'Middle minunites Raw','Middle minunites','Last 5 min Raw','Last 5 min']
    
    for i in range(len(states)):
        X = states[i]['DateTime']
        Y = states[i][col]
        plt.plot(X,Y,c=colors[i],linewidth=1.0)
    plt.title(title)
    plt.grid()
    
    plt.legend(tuple(pos), loc='best')