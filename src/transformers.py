from sklearn.base import TransformerMixin
from scipy import signal as sg
from pandas import DataFrame
import numpy as np

class FilterTransform(TransformerMixin):

    def transform(self,X):
        Y = np.zeros(X.shape)
        if isinstance(X,DataFrame):
            X = X.to_numpy()
        for f in range(X.shape[1]):
            y = self._filData(X[:,f])
            Y[:,f] = y
        return Y

class ButterTransform(FilterTransform):

    def __init__(self, N, Wn,btype='low', analog=False, output='ba', fs=None):
        self.N = N
        self.Wn = Wn
        self.btype = btype
        self.analog = analog
        self.output = output
        self.fs = fs

    def fit(self, X, y=None):
        self.b, self.a = sg.butter(self.N,self.Wn,btype=self.btype,analog=self.analog,output=self.output,fs=self.fs)
        return self

    def _filData(self,X):
        return sg.filtfilt(self.b,self.a,X)


class SavgolTransform(FilterTransform):

    def __init__(self, window_length, polyorder=2, deriv=0, delta=1.0, axis=-1, mode='interp', cval=0.0):
        self.window_length = window_length
        self.polyorder = polyorder
        self.deriv = deriv
        self.delta = delta
        self.axis = axis
        self.mode = mode
        self.cval = cval

    def fit(self, X, y=None):
        return self

    def _filData(self,X):
        return sg.savgol_filter(X,self.window_length,self.polyorder,deriv=self.deriv,delta=self.delta,axis=self.axis,mode=self.mode,cval=self.cval)

if __name__ == '__main__':
    import pandas as pd # se importa pandas como pd
    import numpy as np  #numpy como np
    import pickle as pk
    with open('data/datos_raw.pdd','rb') as f:
        datos_raw = pk.load(f)
    X = datos_raw.iloc[:,1:13]
    Y = SavgolTransform(5).fit_transform(X)
    print(Y)
