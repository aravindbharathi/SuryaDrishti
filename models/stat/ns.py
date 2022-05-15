from astropy.stats import sigma_clipped_stats as scs

import numpy as np


def n_sigma(time, rates, n=3):
    t_arr = []
    mean, _, sigma = scs(rates[~np.isnan(rates)])
    t_start_idx = 0
    t_end_idx = t_start_idx
    j = 0
    temp = 0
    for i in range(len(time)):
        if rates[i] < mean + n * sigma:
            if j != 0:
                t_end_idx = temp
                if j > 4:
                    t_arr.append([t_start_idx, t_end_idx])
            j = 0
        elif j == 0:
            if not np.isnan(rates[i]):
                t_start_idx = i
                temp = t_start_idx
                j += 1
        else:
            if not np.isnan(rates[i]):
                temp = i
                j += 1
            if i == len(time) - 1:
                t_end_idx = i
                if j > 4:
                    t_arr.append([t_start_idx, t_end_idx])

    return t_arr
