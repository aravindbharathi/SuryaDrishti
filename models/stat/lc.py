import os
import sys

from astropy.io import fits
from astropy.convolution import convolve, Box1DKernel
from astropy.stats import sigma_clipped_stats as scs
from astropy.table import Table

import numpy as np

from scipy.stats import linregress

import matplotlib.pyplot as plt

sys.path.append("../../")
from models.stat.efp import EFP, fit_efp
from models.stat.prop import calc_flux, find_flare_class, calc_temperature, calc_EM, calc_lrad
from models.stat.lm import local_maxima
from models.stat.ns import n_sigma

stat_dir = os.path.dirname((os.path.realpath(__file__)))


class LC:
    def __init__(self, lc_path, bin_size):
        self.lc_path = lc_path
        self.bin_size = bin_size
        self.sm_batch_size = 70
        self.sm_kernel_size = 8

        self.raw_time, self.raw_rates = self.load_lc(self.lc_path)
        self.raw_len = len(self.raw_time)

        self.sm_time, self.sm_rates = self.smoothen(
            self.raw_time, self.raw_rates, self.sm_batch_size, self.sm_kernel_size)

        self.bin_time, self.bin_rates = self.rebin_lc(
            self.sm_time, self.sm_rates, 1.0, self.bin_size)

        self.day_start = self.bin_time[0]
        self.processed_lc = np.array([self.bin_time - self.day_start, self.bin_rates])

        self.ns_flares = self.ns(self.processed_lc[0], self.processed_lc[1])
        self.lm_flares = self.lm(self.processed_lc[0], self.processed_lc[1], self.raw_len)

        self.flares = self.merge_flares(self.ns_flares, self.lm_flares)

        self.bg_params, self.sigma = self.bg_fit(self.processed_lc, self.flares)

        self.flares = self.add_efp(self.flares, self.processed_lc, self.bg_params, self.sigma)

        self.flares = self.add_char(self.flares)

        self.ml_data_list = self.add_ml_data(self.flares, self.processed_lc, self.sigma)

    def get_lc(self):
        time, rates = self.processed_lc

        res = {
            'start': float(self.day_start),
            'flare_count': len(self.flares),
            'lc_data': [
                {'x': int(x), 'y': round(y)}
                if not np.isnan(y)
                else {'x': int(x), 'y': None}
                for x, y in zip(time, rates)
            ]
        }
        return res

    def get_flares(self):
        time = self.processed_lc[0]
        rates = self.processed_lc[1]
        res = []

        for flare in self.flares:
            if flare['ns']['is_detected']:
                ns = {
                    'is_detected': True,
                }

                if flare['ns']['fit_params']['is_fit']:
                    A = flare['ns']['fit_params']['A']
                    B = flare['ns']['fit_params']['B']
                    C = flare['ns']['fit_params']['C']
                    D = flare['ns']['fit_params']['D']
                    ChiSq = flare['ns']['fit_params']['ChiSq']
                    dur = flare['ns']['fit_params']['Duration']
                    if ChiSq == np.inf:
                        ns['fit_params'] = {
                            'is_fit': False
                        }
                    else:
                        ns['fit_params'] = {
                            'is_fit': True,
                            'A': float(A),
                            'B': float(B),
                            'C': float(C),
                            'D': float(D),
                            'ChiSq': float(ChiSq),
                            'Duration': dur,
                            'Rise': flare['ns']['fit_params']['Rise'],
                            'Decay': flare['ns']['fit_params']['Decay'],
                        }
                else:
                    ns['fit_params'] = {
                        'is_fit': False
                    }

                true_time = time[flare['ns']['start_idx']:flare['ns']['end_idx'] + 1]
                true = rates[flare['ns']['start_idx']:flare['ns']['end_idx'] + 1]

                fit_time = np.linspace(time[flare['ns']['start_idx']],
                                       time[flare['ns']['end_idx']],
                                       len(true_time) * 100)
                fit = EFP(fit_time, A, B, C, D)

                plt.clf()
                if flare['ns']['fit_params']['is_fit']:
                    plt.plot(fit_time, fit, label='EFP Fit', c='r')
                plt.scatter(true_time, true, label='Processed data', c='b')
                plt.xlabel('Time (s)')
                plt.ylabel('Photon Count rate')
                plt.title('Flare detected at {}s by N Sigma algorithm'.format(
                    int(flare['peak_time'])))
                plt.legend()
                plt.grid()
                plt.savefig('{}/../../frontend/src/assets/ns_{}.jpg'.format(
                    stat_dir, int(flare['peak_time'])))
                ns['plot_loc'] = 'ns_{}.jpg'.format(int(flare['peak_time']))
            else:
                ns = {
                    'is_detected': False
                }

            if flare['lm']['is_detected']:
                lm = {
                    'is_detected': True,
                }

                if flare['lm']['fit_params']['is_fit']:
                    A = flare['lm']['fit_params']['A']
                    B = flare['lm']['fit_params']['B']
                    C = flare['lm']['fit_params']['C']
                    D = flare['lm']['fit_params']['D']
                    ChiSq = flare['lm']['fit_params']['ChiSq']
                    dur = flare['lm']['fit_params']['Duration']
                    if ChiSq == np.inf:
                        lm['fit_params'] = {
                            'is_fit': False
                        }
                    else:
                        lm['fit_params'] = {
                            'is_fit': True,
                            'A': float(A),
                            'B': float(B),
                            'C': float(C),
                            'D': float(D),
                            'ChiSq': float(ChiSq),
                            'Duration': dur,
                            'Rise': flare['lm']['fit_params']['Rise'],
                            'Decay': flare['lm']['fit_params']['Decay'],
                        }
                else:
                    lm['fit_params'] = {
                        'is_fit': False
                    }

                true_time = time[flare['lm']['start_idx']:flare['lm']['end_idx'] + 1]
                true = rates[flare['lm']['start_idx']:flare['lm']['end_idx'] + 1]

                fit_time = np.linspace(time[flare['lm']['start_idx']],
                                       time[flare['lm']['end_idx']], len(true_time) * 100)
                fit = EFP(fit_time, A, B, C, D)

                plt.clf()
                if flare['lm']['fit_params']['is_fit']:
                    plt.plot(fit_time, fit, label='EFP Fit', c='r')
                plt.scatter(true_time, true, label='Processed data', c='b')
                plt.xlabel('Time (s)')
                plt.ylabel('Photon Count rate')
                plt.title('Flare detected at {}s by Local Maxima algorithm'.format(
                    int(flare['peak_time'])))
                plt.legend()
                plt.grid()
                plt.savefig('{}/../../frontend/src/assets/lm_{}.jpg'.format(
                    stat_dir, int(flare['peak_time'])))
                lm['plot_loc'] = 'lm_{}.jpg'.format(int(flare['peak_time']))
            else:
                lm = {
                    'is_detected': False
                }

            res.append({
                'peak_time': int(flare['peak_time']),
                'peak_rate': round(flare['peak_rate']),
                'bg_rate': round(flare['bg_rate']),
                'class': flare['class'],
                'peak_flux': float(flare['peak_flux']),
                'peak_temp': float(flare['peak_temp']),
                'peak_em': float(flare['peak_em']),
                'total_lrad': float(flare['total_lrad']),
                'ns': ns,
                'lm': lm,
            })
        return res

    def get_ml_data(self):
        return self.ml_data_list

    def load_lc(self, lc_path):
        filename, file_ext = os.path.splitext(lc_path)
        if file_ext == '.lc':
            lc = fits.open(lc_path)
            rates = lc[1].data['RATE']
            time = lc[1].data['TIME']
            return time, rates

        elif file_ext == '.ascii':
            t = Table.read(lc_path, format='ascii')
            rates = t['RATE']
            time = t['TIME']
            return time, rates

        elif file_ext == '.csv':
            t = Table.read(lc_path, format='ascii.csv')
            rates = t['RATE']
            time = t['TIME']
            return time, rates

        elif file_ext == '.hdf5':
            t = Table.read(lc_path)
            rates = t['RATE']
            time = t['TIME']
            return time, rates

    def smoothen(self, time, rates, box_bin, kernel_size):
        box_time, box_count = np.array([]), np.array([])
        for i in range(len(time[:]) // box_bin):
            if box_bin * i + i <= len(rates):
                counts = rates[box_bin * i + i:box_bin * (i + 1) + kernel_size + 1 + i]
                boxavg_counts = convolve(counts, Box1DKernel(kernel_size))[
                    kernel_size // 2:box_bin + kernel_size // 2 + 1]
                box_count = np.concatenate((box_count, boxavg_counts))
                box_time = np.concatenate((box_time,
                                           time[box_bin * i + i + kernel_size // 2:
                                                box_bin * (i + 1) + kernel_size // 2 + 1 + i])
                                          )
            else:
                continue
        return box_time, box_count

    def rebin_lc(self, time, rates, t_bin, t_bin_new):
        def bin_edges_from_time(time, t_bin):
            time = np.array(time)
            bin_edges = (time[1:] + time[:-1]) / 2.0
            bin_edges = np.insert(bin_edges, 0, bin_edges[0] - t_bin)
            bin_edges = np.append(bin_edges, bin_edges[-1] + t_bin)
            return bin_edges

        new_time = np.arange(time[0] - t_bin / 2 + t_bin_new / 2,
                             time[-1] + t_bin / 2 + t_bin_new / 2, t_bin_new)
        bin_edges = bin_edges_from_time(new_time, t_bin_new)

        bin_counts = np.histogram(time, bins=bin_edges, weights=rates)[0]
        bin_widths = np.histogram(time, bins=bin_edges, weights=np.ones_like(rates))[0]

        bin_rates = np.nan * bin_widths
        bin_rates[bin_widths != 0] = bin_counts[bin_widths != 0] / bin_widths[bin_widths != 0]

        return new_time, bin_rates

    def ns(self, time, rates):
        flares = []
        interval_ids = n_sigma(time, rates)
        for interval in interval_ids:
            peak_idx = interval[0] + np.nanargmax(rates[interval[0]:interval[1]])
            flares.append([interval[0], interval[1], peak_idx])
        return flares

    def lm(self, time, rates, raw_len):
        flares = []
        interval_ids = local_maxima(time, rates, raw_len)
        for interval in interval_ids:
            peak_idx = interval[0] + np.nanargmax(rates[interval[0]:interval[1]])
            flares.append([interval[0], interval[1], peak_idx])
        return flares

    def merge_flares(self, ns_flares, lm_flares):
        flares = []
        for flare in ns_flares:
            flare_base = {
                'peak_idx': flare[2],
                'start_idx': flare[0],
                'end_idx': flare[1],
                'ns': {},
                'lm': {}
            }

            flare_base['ns']['is_detected'] = True
            flare_base['ns']['start_idx'] = flare[0]
            flare_base['ns']['end_idx'] = flare[1]

            flare_base['lm']['is_detected'] = False

            flares.append(flare_base)

        for flare in lm_flares:
            found = False
            for flare_old in flares:
                if flare[2] == flare_old['peak_idx']:
                    flare_old['lm']['is_detected'] = True
                    flare_old['lm']['start_idx'] = flare[0]
                    flare_old['lm']['end_idx'] = flare[1]

                    flare_old['start_idx'] = min(flare_old['start_idx'], flare[0])
                    flare_old['end_idx'] = max(flare_old['end_idx'], flare[1])

                    found = True
                    break

            if not found:
                flare_base = {
                    'peak_idx': flare[2],
                    'start_idx': flare[0],
                    'end_idx': flare[1],
                    'ns': {},
                    'lm': {}
                }

                flare_base['ns']['is_detected'] = False

                flare_base['lm']['is_detected'] = True
                flare_base['lm']['start_idx'] = flare[0]
                flare_base['lm']['end_idx'] = flare[1]

                flares.append(flare_base)

        return flares

    def bg_fit(self, data, flares):
        time = data[0]
        rates = data[1].copy()

        for flare in flares:
            rates[flare['start_idx']:flare['end_idx']] = np.nan

        not_nan_ids = ~np.isnan(rates)

        if np.sum(not_nan_ids):
            slope, intercept, _, _, _ = linregress(time[not_nan_ids], rates[not_nan_ids])
            _, _, sigma = scs(rates[not_nan_ids])
        else:
            slope, intercept, _, _, _ = linregress(time, rates)
            _, _, sigma = scs(rates)

        return (slope, intercept), sigma

    def add_efp(self, flares, data, bg_params, sigma):
        time = data[0]
        rates = data[1]
        slope, intercept = bg_params
        flares_new = []

        for flare in flares:
            flare_prop = {
                'peak_time': time[flare['peak_idx']],
                'peak_rate': rates[flare['peak_idx']],
                'bg_rate': intercept + slope * time[flare['peak_idx']],
                'start_idx': flare['start_idx'],
                'end_idx': flare['end_idx'],
                'peak_idx': flare['peak_idx'],
                'ns': {},
                'lm': {}
            }
            flare_prop['ratio'] = flare_prop['peak_rate'] / flare_prop['bg_rate']

            if flare['ns']['is_detected']:
                fl_time = time[flare['ns']['start_idx']: flare['ns']['end_idx']]
                fl_rates = rates[flare['ns']['start_idx']: flare['ns']['end_idx']]
                fit_params = fit_efp(fl_time, fl_rates, sigma)
                flare_prop['ns'] = {
                    'is_detected': True,
                    'start_idx': flare['ns']['start_idx'],
                    'end_idx': flare['ns']['end_idx'],
                    'fit_params': fit_params
                }
            else:
                flare_prop['ns'] = {
                    'is_detected': False,
                }

            if flare['lm']['is_detected']:
                fl_time = time[flare['lm']['start_idx']:flare['lm']['end_idx']]
                fl_rates = rates[flare['lm']['start_idx']:flare['lm']['end_idx']]
                fit_params = fit_efp(fl_time, fl_rates, sigma)
                flare_prop['lm'] = {
                    'is_detected': True,
                    'start_idx': flare['lm']['start_idx'],
                    'end_idx': flare['lm']['end_idx'],
                    'fit_params': fit_params
                }
            else:
                flare_prop['lm'] = {
                    'is_detected': False,
                }

            flares_new.append(flare_prop)

        return flares_new

    def add_char(self, flares):
        for flare in flares:
            flux = calc_flux(flare['peak_rate'])
            flare['peak_flux'] = flux
            flare['class'] = find_flare_class(flux)
            flare['peak_temp'] = calc_temperature(flux)
            flare['peak_em'] = calc_EM(flux)
            flare['total_lrad'] = calc_lrad(flux)

        return flares

    def add_ml_data(self, flares, data, sigma):
        ml_data_list = []
        for flare in flares:
            processed_lc = data[:, flare['start_idx']:flare['end_idx']]
            processed_lc = processed_lc[:, ~np.isnan(processed_lc[1])]

            if flare['ns']['is_detected']:
                params_ns = {
                    'is_detected': True,
                    'start_time': data[0][flare['ns']['start_idx']],
                    'end_time': data[0][flare['ns']['end_idx']],
                    'fit_params': flare['ns']['fit_params'],
                    'bg_rate': flare['bg_rate'],
                }
            else:
                params_ns = {
                    'is_detected': False,
                    'bg_rate': flare['bg_rate'],
                    'fit_params': {
                        'ChiSq': np.inf
                    }
                }

            if flare['lm']['is_detected']:
                params_lm = {
                    'is_detected': True,
                    'start_time': data[0][flare['lm']['start_idx']],
                    'end_time': data[0][flare['lm']['end_idx']],
                    'fit_params': flare['lm']['fit_params'],
                    'bg_rate': flare['bg_rate'],
                }
            else:
                params_lm = {
                    'is_detected': False,
                    'bg_rate': flare['bg_rate'],
                    'fit_params': {
                        'ChiSq': np.inf
                    }
                }

            psnr = flare['peak_rate'] / sigma

            ml_data_list.append({
                'processed_lc': processed_lc,
                'params_ns': params_ns,
                'params_lm': params_lm,
                'psnr': psnr,
            })

        return ml_data_list


if __name__ == '__main__':
    lc = LC('../../data/ch2_xsm_20211111_v1_level2.lc', 50)

    plt.figure(figsize=(10, 10))
    plt.scatter(lc.raw_time - lc.raw_time[0], lc.raw_rates, s=0.05)
    plt.xlim((10000, 20000))
    plt.ylim((200, 900))
    plt.xlabel('Time (s)', fontsize=14)
    plt.ylabel('Photon Count rate', fontsize=14)
    plt.title('Raw Light Curve for 11-11-2021', fontsize=16)
    plt.legend()
    plt.grid()
    plt.savefig('20211111_raw_lc.png')
    plt.show()

    # flares = lc.get_flares()
    # peak_time = flares[0]['peak_time']
    # peak_rate = flares[0]['peak_rate']
    # plt.figure(figsize=(10, 10))
    # plt.plot(lc.processed_lc[0], lc.processed_lc[1])
    # plt.scatter(peak_time, peak_rate, c='r', s=50)
    # plt.xlim((10000, 20000))
    # plt.ylim((200, 900))
    # plt.xlabel('Time (s)', fontsize=14)
    # plt.ylabel('Photon Count rate', fontsize=14)
    # plt.title('Processed Light Curve for 11-11-2021', fontsize=16)
    # # plt.legend()
    # plt.grid()
    # plt.savefig('20211111_pro_lc.png')
    # plt.show()

    # print(lc.raw_time.shape, lc.processed_lc.shape)
    # plt.plot(lc.sm_time, lc.sm_rates)
    # plt.scatter(lc.sm_time, lc.sm_rates, s=0.01)
    # plt.plot(lc.bin_time, lc.bin_rates)
    # plt.scatter(lc.processed_lc[0], lc.processed_lc[1], s=0.2)

    # slope, intercept = lc.bg_params
    # plt.plot(lc.processed_lc[0], slope * lc.processed_lc[0] + intercept)

    # plt.show()

    # print(lc.flares[-1])
    # print(lc.get_flares()[-1].keys())
    # print(lc.get_lc().keys())
    # print(len(lc.flares))
    # for flare in lc.flares:
    #     print(flare['ns'])

    # flare = lc.flares[0]
    # print(flare['ns'])
