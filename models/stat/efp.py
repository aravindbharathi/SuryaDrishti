import numpy as np

from scipy.optimize import curve_fit
from scipy.special import erf
from scipy.stats import chisquare

from matplotlib import pyplot as plt


def EFP(x, A, B, C, D):
    Z = (2 * B + C**2 * D) / (2 * C)
    return 1 / 2 * np.sqrt(np.pi) * A * C \
        * np.exp(D * (B - x) + C**2 * D**2 / 4) \
        * (erf(Z) - erf(Z - x / C))


def fit_efp(time, rates, sigma, A0=1, B0=1, C0=1, D0=0.1):
    valid = ~np.isnan(rates)
    time_burst = time[valid]
    rates_burst = rates[valid]

    A0 *= (max(rates_burst))**(1 / 2)
    B0 *= time_burst[np.argmax(rates_burst)]
    C0 *= (max(rates_burst))**(1 / 2)
    D0 *= (time_burst[-1] - B0) / (time_burst[-1] - time_burst[0])

    c_num = 10
    d_num = 10
    c_arr = np.linspace(C0 / 100, C0, c_num)
    d_arr = np.linspace(D0 / 100, D0, d_num)

    chisq_arr = np.zeros((c_num, d_num))
    for i in range(c_num):
        for j in range(d_num):
            try:
                popt, _ = curve_fit(EFP, time_burst, rates_burst, p0=[A0, B0, c_arr[i], d_arr[j]])
                chisq_val, _ = chisquare(EFP(time_burst, *popt), rates_burst)
                chisq_arr[i, j] = chisq_val
            except Exception:
                chisq_arr[i, j] = np.inf

    if np.argmin(chisq_arr) == np.inf:
        return {
            'is_fit': False,
            'ChiSq': np.inf
        }

    (i_opt, j_opt) = np.unravel_index(np.argmin(chisq_arr), (c_num, d_num))

    popt, _ = curve_fit(EFP, time_burst, rates_burst, p0=[A0, B0, c_arr[i_opt], d_arr[j_opt]])

    base_dur = time_burst[-1] - time_burst[0]
    t_long = np.linspace(time_burst[0] - 5 * base_dur,
                         time_burst[-1] + 5 * base_dur,
                         len(time_burst) * 100)

    fit_long = EFP(t_long, *popt)
    t_arr = t_long[np.argwhere(np.diff(np.sign(fit_long - sigma))).flatten()]
    t_max = t_long[np.argmax(fit_long)]

    if len(t_arr) < 2:
        duration = round(3 * base_dur)
        rise = None
        decay = None
    else:
        duration = round(t_arr[-1] - t_arr[0])
        rise = round(t_max - t_arr[0])
        decay = round(t_arr[-1] - t_max)

    # fit_time = np.linspace(t_arr[0], t_arr[-1], len(time_burst) * 100)
    # plt.figure(figsize=(12, 8))
    # plt.plot(time_burst, rates_burst, 'o', label='Processed data', c='b')
    # plt.plot(fit_time, EFP(fit_time, *popt), '-', label='EFP Fit', c='orange')
    # plt.plot(fit_time, np.ones_like(fit_time) * sigma, '--', label='Sigma={}'.format(round(sigma, 2)), c='g')
    # plt.scatter(t_arr, np.ones_like(t_arr) * sigma, c='r')
    # plt.scatter(t_max, EFP(t_max, *popt), c='r')
    # plt.text(t_arr[0] - 100, sigma + 350, 'Start', c='k', size=14)
    # plt.text(t_arr[-1] - 100, sigma + 350, 'End', c='k', size=14)
    # plt.text(t_max - 100, EFP(t_max, *popt) - 1000, 'Peak', c='k', size=14)
    # plt.xlabel('Time (s)', size=14)
    # plt.ylabel('Photon Count rate', size=14)
    # plt.title('EFP Fit', size=16)
    # plt.legend()
    # plt.grid()
    # plt.show()
    # sys.exit(0)

    return {
        'is_fit': True,
        'A': popt[0],
        'B': popt[1],
        'C': popt[2],
        'D': popt[3],
        'ChiSq': chisq_arr[i_opt, j_opt] / len(time_burst),
        'Duration': duration,
        'Rise': rise,
        'Decay': decay
    }
