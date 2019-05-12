from threading import Thread
import pandas as pd
from queue import Queue
from io import StringIO
import sys
from smartbeds import alice
from smartbeds.utils import get_model
import warnings
warnings.filterwarnings("ignore")


class BedProcess:

    model = get_model()

    def __init__(self, bed):
        self._bed = bed
        self._cuento = 0
        self._window = 90
        self._index = 0
        self._datetime = ["DateTime"]
        self.stopped = False
        self._queue = Queue()

        columns = ["MAC_NGMATT", "UUID_BSN", "DateTime"]
        self._press = ["P" + str(i) for i in range(1, 13)]
        self._vital = ["HR", "RR", "SV", "HRV", "SS", "B2B", "STATUS"]
        self._columns = columns + self._press + self._vital
        types = ["str", "str", "str"] + ["int"] * 20

        self._dtypes = {}
        for col in range(len(self._columns)):
            self._dtypes[self._columns[col]] = types[col]

        self._start_data()

    def _start_data(self):

        self._last = pd.DataFrame(columns=self._columns)

    def _new_row(self, newRow):
        MAX_INTERVAL = 3600
        newRow = StringIO(newRow)
        added = False
        df = pd.read_csv(newRow, header=None,
                         names=self._columns,
                         dtype=self._dtypes,
                         parse_dates=self._datetime)
        self._index += 1
        df.index = [self._index]

        if len(self._last) > 0:
            rang = df.DateTime[self._index] - self._last.tail(1).DateTime.iloc[0]

            if rang.total_seconds() > MAX_INTERVAL:
                sys.stdout.flush()
                self._start_data()

        if df.SS.iloc[0] > 400:  # Suficientes datos
            self._last = self._last.append(df)
            added = True

        if len(self._last) > self._window:  # Tenemos uno de más
            sys.stdout.flush()
            self._last.drop(self._last.index.tolist()[0], inplace=True)

        return df, added

    def _create_basic_package(self, df, added):
        # 0: Está durmiendo normal
        # 1: Hay crisis
        # 2: No está durmiendo
        # 3: Insuficientes datos para hacer el cálculo
        package = {"result": [0, 0, df.SS.iloc[0], df.STATUS.iloc[0]],
                   "instance": str(df.DateTime.iloc[0]),
                   "vital": [df.HR.iloc[0], df.RR.iloc[0], df.SV.iloc[0], df.HRV.iloc[0], df.B2B.iloc[0]/1000],
                   "pressure": [df.P1.iloc[0], df.P2.iloc[0], df.P3.iloc[0],
                                df.P4.iloc[0], df.P5.iloc[0], df.P6.iloc[0]]}


        if added and len(self._last) == self._window:
            result, proba = self._get_result()
            package["result"][0] = result
            package["result"][1] = proba
        else:
            package["result"][0] = 3
        return package

    def _get_result(self):
        _input = self._preprocess()
        return self._predict(_input)

    def _preprocess(self):
        to_proc = self._last[["DateTime"]+["P" + str(i) for i in range(1, 7)]]
        _input = alice.rolling_extract_features(to_proc, self._window, alice.fc_parameters)
        return _input

    @staticmethod
    def _predict(_input):
        # Debug
        _input.drop("DateTime", axis=1, inplace=True)
        result = BedProcess.model.predict(_input)
        proba = BedProcess.model.predict_proba(_input)
        if result:
            result = 1
        else:
            result = 0
        return result, proba[0][1]

    def next_package(self):
        if self._queue.empty():
            return None
        else:
            return self._queue.get()

    def run(self):
        while not self._bed.stopped:
            newrow = self._bed.next_package()
            if newrow is not None:
                df, added = self._new_row(newrow)
                package = self._create_basic_package(df, added)
                self._queue.put(package)
        else:
            self.stopped = True

    def start(self):
        Thread(target=self.run, daemon=True).start()
