from threading import Thread
import pandas as pd
import numpy as np
from io import StringIO
import sys


class BedProcess:

    def __init__(self, bed):
        self._bed = bed
        self._cuento = 0
        self._window = 10
        self._index = 0
        self._datetime = ["DateTime"]

        columns = ["MAC_NGMATT", "UUID_BSN", "DateTime"]
        press = ["P" + str(i) for i in range(1, 13)]
        vital = ["HR", "RR", "SV", "HRV", "SS", "B2B", "STATUS"]
        self._columns = columns + press + vital
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
            rang = df.DateTime[self._index]-self._last.tail(1).DateTime[self._index-1]

            if rang.total_seconds() > MAX_INTERVAL:
                sys.stdout.flush()
                self._start_data()

        if df.SS > 400: #Suficientes datos
            self._last = self._last.append(df)
            added=True


        if len(self._last) > self._window: #Tenemos uno de más
            sys.stdout.flush()
            self._last.drop(self._last.index.tolist()[0], inplace=True)

        return df, added

    def _create_basic_package(self, df, added):
        package = {"result": [0, df.SS.iloc[0], df.STATUS.iloc[0]],
                   "instance": str(df.DateTime.iloc[0]),
                   "vital": [df.HR.iloc[0], df.RR.iloc[0], df.SV.iloc[0], df.HRV.iloc[0], df.B2B.iloc[0]],
                   "pressure": [df.P1.iloc[0], df.P2.iloc[0], df.P3.iloc[0],
                                df.P4.iloc[0], df.P5.iloc[0], df.P6.iloc[0]]}
        if added and len(self._last) == self._window:
            result = self._get_result()
            package["result"][0] = result
        return package

    def _get_result(self):
        _input = self._preprocess()
        return self._predict(self, _input)

    def _preprocess(self):
        return None

    def _predict(self, _input):
        return 1

    def run(self):
        while not self._bed.stopped:
            newRow = self._bed.next_package()
            if newRow is not None:
                df, added = self._new_row(newRow)
                self._create_basic_package(df, added)

    def start(self):
        Thread(target=self.run, daemon=True).start()
