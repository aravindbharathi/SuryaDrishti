import sys

import numpy as np

sys.path.append("..")
from models.stat.lc import LC
from models.ml.snn import SNN

if __name__ == '__main__':
    snn = SNN()

    file_path = '../../ch2_xsm_20211013_v1_level2.lc'
    bin_size = 50
    lc = LC(file_path, bin_size)

    flares = lc.get_flares()
    print(flares)

    ml_data_list = lc.get_ml_data()

    conf_list = snn.get_conf(ml_data_list)
    for conf in conf_list:
        print(round(100.0 * conf))

    labels = np.ones((len(flares),))
    labels[-1] = 0.0
    snn.train(ml_data_list, labels, epochs=10)

    conf_list = snn.get_conf(ml_data_list)
    for conf in conf_list:
        print(round(100.0 * conf))

    labels = np.ones((len(flares),))
    snn.train(ml_data_list, labels, epochs=10)

    conf_list = snn.get_conf(ml_data_list)
    for conf in conf_list:
        print(round(100.0 * conf))
