import pandas as pd  # se importa pandas como pd
import numpy as np  # numpy como np
import seaborn as sns
import tsfresh as tf


def rolling_extract_features(dataFrame, window, fc_parameters):
    """
    Calcula las características especificadas por fc_parameters del dataFrame según una ventana.

    Parámetros:
    dataFrame -- Datos incluyendo las columnas 'DateTime' y presiones
    window -- ventana para el cálculo de las características
    fc_parameters -- diccionario con las características que se quieren calcular

    Retorno:
    features -- DataFrame con las características incluyendo 'DateTime' y características
    """

    if len(dataFrame) < window:
        raise Exception("La ventana debe ser menor o igual a la longitud del DataFrame.")

    # preparar el formato de los datos para pasárselos a la función de extracción de características
    X, datetime = dataFrame, dataFrame['DateTime']
    X['id'] = 1
    X = X.reset_index(drop=True)

    # extracción de características por ventana
    features = pd.DataFrame()
    for i in range(len(X) - window + 1):
        X_rolling = X.iloc[i:i + window]
        features_rolling = tf.extract_features(X_rolling, default_fc_parameters=fc_parameters, column_id='id',
                                               column_sort='DateTime', disable_progressbar=True, n_jobs=0)
        features = pd.concat([features, features_rolling], axis=0)

    # volver a añadir DateTime
    features.reset_index(drop=True, inplace=True)
    datetime = datetime[window - 1:].reset_index(drop=True)
    features = pd.concat([datetime, features], axis=1)

    return features


# características a calcular
# para más info: https://tsfresh.readthedocs.io/en/latest/text/list_of_features.html
# y https://tsfresh.readthedocs.io/en/latest/text/feature_extraction_settings.html
fc_parameters = {
    "agg_linear_trend": [{"attr": "intercept", "chunk_len": 5, "f_agg": "var"},
                         {"attr": "stderr", "chunk_len": 5, "f_agg": "min"}],
    "symmetry_looking": [{"r": 0.6}],
    "change_quantiles": [{"ql": 0.2, "qh": 1.0, "isabs": False, "f_agg": "var"},
                         {"ql": 0.4, "qh": 0.8, "isabs": False, "f_agg": "var"},
                         {"ql": 0.4, "qh": 0.6, "isabs": True, "f_agg": "var"},
                         {"ql": 0.0, "qh": 0.6, "isabs": True, "f_agg": "mean"},
                         {"ql": 0.4, "qh": 1.0, "isabs": True, "f_agg": "mean"}],
    "last_location_of_minimum": None,
    "number_peaks": [{"n": 1}]
}
