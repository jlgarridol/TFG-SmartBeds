from src import transformers as tf
import unittest as ut
import pandas as pd

DATA_PATH = 'tests/samples/'
INPUT = 'input/'
OUTPUT = 'output/'
CSV_PRECISION = 10

def launcher():
    suites = []
    suites.append(ut.defaultTestLoader.loadTestsFromTestCase(ButterTransformerTest))
    suites.append(ut.defaultTestLoader.loadTestsFromTestCase(SavGolTransformerTest))
    suites.append(ut.defaultTestLoader.loadTestsFromTestCase(ConcatenateTransformerTest))
    #suite.addTest(ButterTransformerTest())
    #TODO: Add more
    return suites

class TransformerTest(ut.TestCase):

    def __init__(self,output,*args,**kwargs,):
        super(TransformerTest, self).__init__(*args,**kwargs)
        if 'input_' in kwargs:
            input_ = kwargs['input_']
        else:
            input_ = 'generic_input.csv'
        self.input = pd.read_csv(DATA_PATH+INPUT+input_,index_col=0)
        self.output = pd.read_csv(DATA_PATH+OUTPUT+output,index_col=0)
        self.transformer = None

    def test_calculate_dataframe(self):
        output = self.transformer.fit_transform(self.input)

        compare = output.round(CSV_PRECISION)==self.output.round(CSV_PRECISION)

        self.assertFalse(False in compare.values)

    def test_calculate_series(self):    
        serie = self.input[self.input.columns[0]]    
        output = self.transformer.fit_transform(serie)

        compare = output.round(CSV_PRECISION)==self.output[[self.output.columns[0]]].round(CSV_PRECISION)
        self.assertFalse(False in compare.values)

    def test_bad_data(self):
        try:   
            output = self.transformer.fit_transform('String')
            self.fail()
        except AssertionError:
            pass


class ButterTransformerTest(TransformerTest):
     
    def __init__(self,*args,**kwargs):
        super(ButterTransformerTest, self).__init__('butter_output.csv',*args,**kwargs)
        N = 3
        Wn = 0.05
        self.transformer = tf.ButterTransformer(N,Wn)       

class SavGolTransformerTest(TransformerTest):
     
    def __init__(self,*args,**kwargs):
        super(SavGolTransformerTest, self).__init__('savgol_output.csv',*args,**kwargs)
        self.transformer = tf.SavgolTransformer(15)       

class ConcatenateTransformerTest(TransformerTest):
     
    def __init__(self,*args,**kwargs):
        super(ConcatenateTransformerTest, self).__init__('concatenate_output.csv',*args,**kwargs)
        
        N = 3
        Wn = 0.05
        butter = tf.ButterTransformer(N,Wn)
        savgol = tf.SavgolTransformer(15)       
        self.transformer = tf.ConcatenateTransformer(butter,savgol)

    def test_calculate_series(self):    
        serie = self.input[self.input.columns[0]]    
        output = self.transformer.fit_transform(serie)

        compare = output.round(CSV_PRECISION)==self.output[[self.output.columns[0],self.output.columns[len(self.input.columns)]]].round(CSV_PRECISION)
        self.assertFalse(False in compare.values)
