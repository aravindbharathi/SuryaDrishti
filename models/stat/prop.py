import numpy as np


# W/m^2
def calc_flux(rate):
    start_energy_flux = np.log10(3e-9)
    start_rate = np.log10(1e1)
    end_energy_flux = np.log10(7e-7)
    end_rate = np.log10(1e3)
    flux_slope = ((end_rate - start_rate) / (end_energy_flux - start_energy_flux))
    A = np.power(10, start_rate - flux_slope * start_energy_flux)
    flux = np.power(np.array(rate / A), 1 / flux_slope)
    return flux


# sub-A (Q), A, B, C, M, X
def find_flare_class(flux):
    flare_class_val = np.log10(np.max(flux)) + 8
    flare_class = 'A'
    if(flare_class_val < 0):
        flare_class = 'sub-A'
    elif(flare_class_val < 1):
        flare_class = 'A' + str(np.int32(flux / 1e-8))
    elif(flare_class_val < 2):
        flare_class = 'B' + str(np.int32(flux / 1e-7))
    elif(flare_class_val < 3):
        flare_class = 'C' + str(np.int32(flux / 1e-6))
    elif(flare_class_val < 4):
        flare_class = 'M' + str(np.int32(flux / 1e-5))
    else:
        flare_class = 'X' + str(np.int32(flux / 1e-4))
    return flare_class


# In MK
def calc_temperature(flux):
    if (flux < 7e-8):
        return 9.28 + 0.32 * np.log10(flux)
    elif (flux > 1e-7):
        return 34 + 3.9 * np.log10(flux)
    else:
        return ((np.log10(1e-7) - np.log10(flux)) * (9.28 + 0.32 * np.log10(flux))
                + (np.log10(flux) - np.log10(7e-8)) * (34 + 3.9 * np.log10(flux))) \
            / (np.log10(1e-7) - np.log10(7e-8))


# In cm^3
def calc_EM(flux):
    return 10**53 * flux**0.86


# In ergs
def calc_lrad(flux):
    return 10**34 * flux**0.9
