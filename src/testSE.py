import numpy as np
import pandas as pd
import pickle as pk
from sklearn.manifold import SpectralEmbedding as SE
import warnings
warnings.filterwarnings("error")


with open('data/datos.pdd','rb') as f:
    datos = pk.load(f)

datos_seizure = datos.loc[datos['target']==True]
datos_notSeizure = datos.loc[datos['target']==False]


### Días donde hubo crisis
dayOfSeizures = set()

for i in datos_seizure['DateTime']:
    dayOfSeizures.add(i.date())


#Todos los datos de esos días
crit = datos['DateTime'].map(lambda x: x.date() in dayOfSeizures)

datosPart = datos[crit]
maxNei = int(len(datosPart)/10)

data = datosPart.iloc[:,1:len(datosPart.columns)-1]
data = data.astype(np.float32)

seB = SE(n_components=2).fit_transform(data)

"""with open('result.txt','w') as r:
    for i in range(1200,maxNei,100):
        try:
            seB = SE(n_components=2,n_neighbors=i).fit_transform(data)
            r.write('With '+str(i)+' neighbors the execution finished\n')
            print('Pass')
        except UserWarning:
            r.write('With '+str(i)+' neighbors graph is not fully connected\n')
            print('Neighbors warning')
        except Exception as ex:
            r.write('With'+str(i)+' neighbors get exeption '+str(e)+'\n')
            print('Exception')

"""
