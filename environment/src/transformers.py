from sklearn.base import TransformerMixin
from sklearn.feature_selection import VarianceThreshold
from scipy import signal as sg
from pandas import DataFrame
import numpy as np
import pandas as pd

class FilterTransformer(TransformerMixin):
    """
    Abstract filter transformer
    """
    __author__ = "José Luis Garrido Labrador"

    def transform(self,X):
        """
        Transform X applying a filter
        
        Parameters
        ----------
            X: Pandas Dataframe 
                whose columns are compatible with filter
            
        Returns
        -------
        Pandas Dataframe
            X filtered
        """
        Y = X.copy()
        mode = 'DataFrame'
        if type(Y) == pd.Series:
            mode = 'Series'
            Y = Y.to_frame()
            
        size = len(Y.columns)
        #if isinstance(X,DataFrame):
        #    X = X.to_numpy()
        for f in Y.columns:
            y = self._filData(Y[f])
            Y[f+" "+self._NAME] = y
        
        if mode == 'DataFrame':
            return Y.iloc[:,size:len(Y.columns)]
        elif mode == 'Series':
            return Y[Y.columns[-1]]
    
    def _filData(self,X):
        """
        Abstract function to apply filter to a column
        
        Parameters
        ----------
            X: Pandas serie
                Serie to apply filter
                
        Returns
        -------
        Padas Serie
            X filtered
                
        """
        pass

class ButterTransformer(FilterTransformer):
    __author__ = "José Luis Garrido Labrador"

    def __init__(self, N, Wn,btype='low', analog=False):
        """
        Build a ButterWorth filter transformer
        
        Parameters
        ----------
        N : int
            The order of the filter.
        Wn : array_like
            A scalar or length-2 sequence giving the critical frequencies. For a Butterworth filter, this is the point at which the gain drops to 1/sqrt(2) that of the passband (the “-3 dB point”).
            For digital filters, Wn are in the same units as fs. By default, fs is 2 half-cycles/sample, so these are normalized from 0 to 1, where 1 is the Nyquist frequency. (Wn is thus in half-cycles / sample.)
            For analog filters, Wn is an angular frequency (e.g. rad/s).
        btype : {‘lowpass’, ‘highpass’, ‘bandpass’, ‘bandstop’}, optional
            The type of filter. Default is ‘lowpass’.
        analog : bool, optional
            When True, return an analog filter, otherwise a digital filter is returned.
        """
        self._NAME = 'BUTTER'
        self._N = N
        self._Wn = Wn
        self._btype = btype
        self._analog = analog
        self._output = 'ba'

    def fit(self, X, y=None):
        """
        Create Numerator (b) and denominator (a) polynomials of the IIR filter
        """
        assert type(X) == pd.DataFrame or type(X) == pd.Series, "This transformer only works with pandas DataFrame or Series"
        self._b, self._a = sg.butter(self._N,self._Wn,btype=self._btype,analog=self._analog,output=self._output)
        return self

    def _filData(self,X):
        return sg.filtfilt(self._b,self._a,X)


class SavgolTransformer(FilterTransformer):
    __author__ = "José Luis Garrido Labrador"

    def __init__(self, window_length, polyorder=2, deriv=0, delta=1.0, axis=-1, mode='interp', cval=0.0):
        """
        window_length : int
            The length of the filter window (i.e. the number of coefficients). window_length must be a positive odd integer. If mode is ‘interp’, window_length must be less than or equal to the size of x.
        polyorder : int
            The order of the polynomial used to fit the samples. polyorder must be less than window_length.
        deriv : int, optional
            The order of the derivative to compute. This must be a nonnegative integer. The default is 0, which means to filter the data without differentiating.
        delta : float, optional
            The spacing of the samples to which the filter will be applied. This is only used if deriv > 0. Default is 1.0.
        axis : int, optional
            The axis of the array x along which the filter is to be applied. Default is -1.
        mode : str, optional
            Must be ‘mirror’, ‘constant’, ‘nearest’, ‘wrap’ or ‘interp’. This determines the type of extension to use for the padded signal to which the filter is applied. When mode is ‘constant’, the padding value is given by cval. See the Notes for more details on ‘mirror’, ‘constant’, ‘wrap’, and ‘nearest’. When the ‘interp’ mode is selected (the default), no extension is used. Instead, a degree polyorder polynomial is fit to the last window_length values of the edges, and this polynomial is used to evaluate the last window_length // 2 output values.
        cval : scalar, optional
            Value to fill past the edges of the input if mode is ‘constant’. Default is 0.0.
        """
        self._NAME = 'SAVGOL'
        self._window_length = window_length
        self._polyorder = polyorder
        self._deriv = deriv
        self._delta = delta
        self._axis = axis
        self._mode = mode
        self._cval = cval

    def fit(self, X, y=None):
        assert type(X) == pd.DataFrame or type(X) == pd.Series, "This transformer only works with pandas DataFrame or Series"
        return self

    def _filData(self,X):
        return sg.savgol_filter(X,self._window_length,self._polyorder,deriv=self._deriv,delta=self._delta,axis=self._axis,mode=self._mode,cval=self._cval)
    
class VarianceThresholdPD(TransformerMixin):
    __author__ = "José Luis Garrido Labrador"
    
    def __init__(self,threshold=0.0):
        """
        sklearn.feature_selection.VarianceThreshold like transformer Pandas dataframe's index compatible
        
        Parameters
        ----------
            threshold: float, optional
                Features with a training-set variance lower than this threshold will be removed. The default is to keep all features with non-zero variance, i.e. remove the features that have the same value in all samples.                
        """
        self._threshold = threshold
        
    def fit(self, X, y=None):
        return self
    
    def transform(self,X):
        data = X.copy()
        selector = VarianceThreshold(threshold=self._threshold)
        selector.fit(data)
        return data[data.columns[selector.get_support(indices=True)]]

###Compuestos###

class ConcatenateTransformer(TransformerMixin):
    __author__ = "José Luis Garrido Labrador"

    def __init__(self,*transformers):
        """
        Concatenate differents transformers output
        
        Parameters
        ----------
            *transformers: args
                List of transformers to concatenate
        """
        self._transformers = transformers
        for t in self._transformers:
            dt = t.__dir__()
            assert 'fit' in dt and 'transform' in dt and 'fit_transform' in dt, str(t)+' is invalid transformer'

    def fit(self,X,y=None):
        assert type(X) == pd.DataFrame or type(X) == pd.Series, "This transformer only works with pandas DataFrame or Series"
        return self

    def transform(self,X):
        Y = DataFrame()
        for t in self._transformers:
            r = t.fit_transform(X)
            Y = pd.concat([Y,r],axis=1)
        return Y

class PipelineTransformer(TransformerMixin):
    __author__ = "José Luis Garrido Labrador"

    def __init__(self,*transformers):
        """
        Create a pipeline of transformers
        
        Parameters
        ----------
            *transformers: args
                List of transformers to connect in a pipeline
        """
        self._transformers = transformers
        for t in self._transformers:
            dt = t.__dir__()
            assert 'fit' in dt and 'transform' in dt and 'fit_transform' in dt, str(t)+' is invalid transformer'

    def fit(self,X,y=None):
        assert type(X) == pd.DataFrame or type(X) == pd.Series, "This transformer only works with pandas DataFrame or Series"
        return self

    def transform(self,X):
        Y = X.dropna()
        for t in self._transformers:
            Y = t.fit_transform(Y).dropna()
        return Y
    
class Normalizer(TransformerMixin):
    """
    Normalize all data between 0 and 1. 
    """
    __author__ = "José Luis Garrido Labrador"

    def __init__(self,max_=1):
        """
        Normalizer all features with same scale
        
        Parameters
        ----------
            max_: float,optional
                max value to normalized data
        """
        self._max = max_
    
    def fit(self, X, y=None):
        assert type(X) == pd.DataFrame or type(X) == pd.Series or type(X) == np.ndarray or type(X) == np.matrixlib.defmatrix.matrix, "This transformer only works with pandas DataFrame or Series or numpy matrix and arrays "
        return self

    def transform(self, data):
        maxi = np.max(np.max(data))
        mini = np.min(np.min(data))
        rang = maxi-mini   
        dataNorm = (data - mini) / rang
        return dataNorm*self._max
    
class EachNormalizer(TransformerMixin):
    """
    Normalize each feature with own scale
    """
    __author__ = "José Luis Garrido Labrador"

    def fit(self,X,y=None):
        assert type(X) == pd.DataFrame or type(X) == pd.Series, "This transformer only works with pandas DataFrame or Series"
        return self
    
    def transform(self,data):
        if type(data) == pd.Series:
            data_ = data.to_frame()
        else:
            data_ = data   

        datos = data_.copy()
        for c in data_:
            max_ = data_[c].max()
            min_ = data_[c].min()
            rang = max_ - min_
            datos[c] = (data_[c] - min_) / rang

        if type(data) == pd.Series:
            return datos[datos.columns[0]]
        else:
            return datos

class NoiseFilter(TransformerMixin): 
    __author__ = "Alicia Olivares Gil"

    def __init__(self,minimum=0):
        """
        Makes 0 all values less than 'minimum'.
        
        Parameters
        ----------
            minimum: float, optional
                limit value
        """
        self._minimum = minimum
    
    def fit(self,X,y=None):
        return self
    
    def transform(self, data):
        dataN = data.copy()
        for d in dataN: 
            if dataN[d].dtype == np.float64: 
                dataN.loc[data[d]< self._minimum, d]=0.0      
        return dataN
    
class MoveTargetsTransformer(TransformerMixin):
    __author__ = "José Luis Garrido Labrador"
    
    def __init__(self,window=25,mode='only',target_col = 'target'):
        """
        Transforms targets for rolling statics transformations
        
        Parameters
        ----------
            window: int, optional
                rolling static window
            mode: string, optional
                Mode of targets transformation.
                only = if all statics that compound it are true the final target will be true
                half = if at least statics that compound it are true the final target will be true
                start = if the first element of rolling are true the final target will be true
                end = if the last element of rolling are true the final target will be true
            target_col: string, optional
                Name of target columns
        """
        self._transformers = {'only':self._only_seizure,'half':self._half_seizure,
                          'start':self._start_seizure,'end':self._end_seizure}
        self._window = window
        self._transform = self._transformers[mode]
        self._target_col = target_col
        
    def fit(self, X, y=None):
        assert type(X) == pd.DataFrame, "This transformer only works with pandas DataFrame"
        return self
    
    def transform(self, data):
        assert data[self._target_col].dtype == bool, 'Target column must be boolean'
        data = data.copy()
        
        return self._transform(data)
    
    def _only_seizure(self,data):
        """
        Target set to true if all data that compose it are true
        """
        trues = data.loc[data[self._target_col] == True]
        
        i = trues.first_valid_index()
        
        data.loc[i:i+self._window-1, self._target_col] = False 
        return data
    
    def _half_seizure(self,data):
        """
        Target set to true if at least the half that compose it are true
        """
        trues = data.loc[data[self._target_col] == True]
        
        i = trues.first_valid_index()
        j = trues.last_valid_index()
        
        data.loc[i:i+int(self._window/2)-1, self._target_col] = False    
        data.loc[j:j+int(self._window/2), self._target_col] = True
        
        return data
        
    def _start_seizure(self,data):
        """Target set to true if the first data that compose it are true"""
        data = self._only_seizure(data)
        trues = data.loc[data[self._target_col] == True]
        i = trues.last_valid_index()
        
        data.loc[i:i+self._window,self._target_col]=True
        return data
    
    def _end_seizure(self,data):
        """
        Target set to true if the last data that compose it are true
        """
        return data
    
class StatisticsTransformer(TransformerMixin): 
    __author__ = "Alicia Olivares Gil"
    
    def __init__(self,mode='mean',window=25):
        """
        Calculates rolling statistics of the columns from data. 

        Parameters
        ----------
            mode: string, optional
                'mean': rolling mean
                'std': rolling standard deviation
                'max': rolling maximun value
                'min': rolling minimum value
                'range' : rolling ranges (difference between max and min)
            window: int, optional 
        """
        self._mode = mode
        self._window = window
        #Functions
        mean = lambda x: x.rolling(self._window).mean()
        std = lambda x: x.rolling(self._window).std()
        _max = lambda x: x.rolling(self._window).max()
        _min = lambda x: x.rolling(self._window).min()
        rang = lambda x: _max(x)-_min(x)
        self._functions = {'mean':mean,'std':std,'max':_max,'min':_min,'range':rang}
    
    def fit(self, X, y=None): 
        return self
    
    def transform(self, data): 
        statistics = pd.DataFrame()
        try:
            func = self._functions[self._mode]
        except:
            raise NameError('Unknown mode, use mean, std, max, min or range')
        for c in data.columns: 
            statistics[c+' '+self._mode+" "+str(self._window)] = func(data[c])
        return statistics

if __name__ == '__main__':
    #Prueba rápida
    import pandas as pd # se importa pandas como pd
    import numpy as np  #numpy como np
    import pickle as pk
    with open('data/datos_raw.pdd','rb') as f:
        datos_raw = pk.load(f)
    X = datos_raw.iloc[:,1:13]
    M = StatisticsTransformer('mean',25)
    STD = StatisticsTransformer('std',18)
    R = StatisticsTransformer('range',24)
    CON = ConcatenateTransformer(M,STD,R)
    S = SavgolTransformer(5)
    V = VarianceThresholdPD(threshold=0.5)
    Y = PipelineTransformer(CON,V).fit_transform(X)
    print(Y)
