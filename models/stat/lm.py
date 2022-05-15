from astropy.stats import sigma_clipped_stats as scs

import numpy as np
from scipy.stats import linregress


def local_maxima(time, rates, raw_len):
    def find_start(time, rates, frac=0.3):
        length = int(frac * raw_len * 0.01)
        st_nr = rates[4:] - rates[:-4]
        st_dr = time[4:] - time[:-4]
        st_slope = np.divide(st_nr, st_dr)
        st_slope_nonan = st_slope[~np.isnan(st_slope)]
        st_cutoff = np.average(np.sort(st_slope_nonan)[-1 * length:])

        st_flags = np.array(np.where(st_slope > st_cutoff))

        new_st_flags = [st_flags[0][0]]
        for i in range(len(st_flags[0]) - 1):
            if st_flags[0][i + 1] - st_flags[0][i] > 20:
                new_st_flags.append(st_flags[0][i + 1])
        return new_st_flags

    new_st_flags = find_start(time, rates)
    new_st_flags_alt = find_start(time, rates, 0.1)

    if len(new_st_flags) / len(new_st_flags_alt) > 1.3:
        new_st_flags = new_st_flags_alt

    peak_flags = []

    def find_peaks(st_flag, pk_nr, pk_dr):
        if len(np.where(np.divide(pk_nr, pk_dr) < 1)[0]) >= 6:
            return st_flag + np.where(np.divide(pk_nr, pk_dr) < 1)[0][5]
        elif len(np.where(np.divide(pk_nr, pk_dr) < 1)[0]) > 0:
            return st_flag + np.where(np.divide(pk_nr, pk_dr) < 1)[0][
                len(np.where(np.divide(pk_nr, pk_dr) < 1)[0]) - 1]
        else:
            return st_flag

    for i in range(len(new_st_flags)):
        peak = rates[new_st_flags[i]:]
        pk_nr = peak[4:]
        pk_dr = peak[:-4]
        peak_flags.append(find_peaks(new_st_flags[i], pk_nr, pk_dr))

    def bk_sub(time, rates):
        # Background subtraction
        slope, intercept, r, p, se = linregress(time[~np.isnan(rates)], rates[~np.isnan(rates)])
        bksub_counts = rates - np.array(slope * time + intercept)

        return bksub_counts

    def bk_avg(time, rates):
        iter_counts = rates[~np.isnan(rates)]
        iter = 5
        n = 0.8
        for i in range(iter):
            mean, med, sig = scs(iter_counts)
            iter_counts[iter_counts > mean + n * sig] = mean + n * sig
        mean = np.mean(iter_counts)

        slope, intercept, r, p, se = linregress(time[~np.isnan(rates)], iter_counts)

        return mean, slope * time + intercept, sig

    cts = bk_sub(time, rates)
    cut, fit, sig = bk_avg(time, cts)

    def find_end(rates, mean):
        if (~np.isnan(rates)).sum() == 0:
            return 0
        if len(np.where(rates < mean + 0.25 * sig)[0]) != 0:
            end_time = np.where(rates < mean + 0.25 * sig)[0][0]
        else:
            end_time = np.nanargmin(rates)
        return end_time

    end_flags = []

    remove_flags = []
    for i in range(len(peak_flags)):
        if i != len(peak_flags) - 1:
            temp = find_end(rates[peak_flags[i]:new_st_flags[i + 1]],
                            fit[peak_flags[i]:new_st_flags[i + 1]])
            if temp == 0:
                remove_flags.append(i)
                continue
            end_flags.append(peak_flags[i] + temp)
        else:
            end_flags.append(peak_flags[i] + find_end(rates[peak_flags[i]:],
                                                      fit[peak_flags[i]:]))

    peak_flags = np.delete(peak_flags, remove_flags)

    t_arr = []
    for i in range(len(end_flags)):
        if end_flags[i] - new_st_flags[i] > 4:
            t_arr.append([new_st_flags[i], end_flags[i]])

    return t_arr
