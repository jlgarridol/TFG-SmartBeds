from sklearn.base import TransformerMixin
from sklearn.feature_selection import VarianceThreshold
from scipy import signal as sg
from pandas import DataFrame
import numpy as np

class FilterTransformer(TransformerMixin):

    def transform(self,X):
        Y = DataFrame()
        #if isinstance(X,DataFrame):
        #    X = X.to_numpy()
        for f in X.columns:
            y = self._filData(X[f])
            Y[f+" "+self._NAME] = y
        return Y

class ButterTransformer(FilterTransformer):

    def __init__(self, N, Wn,btype='low', analog=False, output='ba', fs=None):
        self._NAME = 'BUTTER'
        self._N = N
        self._Wn = Wn
        self._btype = btype
        self._analog = analog
        self._output = output
        self._fs = fs

    def fit(self, X, y=None):
        self._b, self._a = sg.butter(self._N,self._Wn,btype=self._btype,analog=self._analog,output=self._output,fs=self._fs)
        return self

    def _filData(self,X):
        return sg.filtfilt(self._b,self._a,X)


class SavgolTransformer(FilterTransformer):

    def __init__(self, window_length, polyorder=2, deriv=0, delta=1.0, axis=-1, mode='interp', cval=0.0):
        self._NAME = 'SAVGOL'
        self._window_length = window_length
        self._polyorder = polyorder
        self._deriv = deriv
        self._delta = delta
        self._axis = axis
        self._mode = mode
        self._cval = cval

    def fit(self, X, y=None):
        return self

    def _filData(self,X):
        return sg.savgol_filter(X,self._window_length,self._polyorder,deriv=self._deriv,delta=self._delta,axis=self._axis,mode=self._mode,cval=self._cval)
    
class VarianceThresholdPD(TransformerMixin):
    
    def __init__(self,threshold=0.0):
        self._threshold = threshold
        
    def fit(self, X, y=None):
        return self
    
    def transform(self,X):
        R = VarianceThreshold(threshold=0.5).fit_transform(X)
        P = DataFrame()
        v = 0
        for c in X.columns:
            if v >= R.shape[1]:
                break
            P[c] = R[:,v]
            v += 1
        return P

###Compuestos###

class ConcatenateTransformer(TransformerMixin):

    def __init__(self,*transformers):
        self._transformers = transformers

    def fit(self,X,y=None):
        return self

    def transform(self,X):
        Y = DataFrame()
        for t in self._transformers:
            r = t.fit_transform(X)
            Y = pd.concat([Y,r],axis=1)
        return Y

class PipelineTransformer(TransformerMixin):

    def __init__(self,*transformers):
        self.transformers = transformers

    def fit(self,X,y=None):
        return self

    def transform(self,X):
        Y = X
        for t in self.transformers:
            Y = t.fit_transform(Y)
        return Y

if __name__ == '__main__':
    import pandas as pd # se importa pandas como pd
    import numpy as np  #numpy como np
    import pickle as pk
    with open('data/datos_raw.pdd','rb') as f:
        datos_raw = pk.load(f)
    X = datos_raw.iloc[:,1:13]
    S = SavgolTransformer(5)
    V = VarianceThresholdPD(threshold=0.5)
    Y = PipelineTransformer(S,V).fit_transform(X)
    print(Y)