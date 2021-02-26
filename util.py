        
def get_pandas_timeframe_frequency(pandas_tf):
    pandas_tf = pandas_tf.upper()
    mapping = {
        "1T": 60,        
        "5T": 300,
        "15T": 900,
        "30T": 1800,
        "1H": 3600,        
        "4H": 14400,
        "1D": 86400,        
        "1W": 604800
    }

    return mapping.get(str(pandas_tf))

