''' emission.py:
List of emission functions:
The first two arguments must be "nu" and "beam".
Add your custom functions at the end!
Default values in function definitions will be fitted, so hardcode them if you want them fixed - see
the case of freefree, where T_e has been fixed to 7000 K.
'''

import numpy as np



# Synchrotron Emission

def synchrotron(nu, beam, A_sync, alpha):

    c = 299792458.
    k = 1.3806488e-23
    h = 6.62606957e-34

    S = A_sync * nu**alpha

    return S



#Free-Free Emission

def freefree(nu, beam, EM):

    T_e = 7000. # fixed electron temperature

    c = 299792458.
    k = 1.3806488e-23
    h = 6.62606957e-34

    a = 0.366 * np.power(nu,0.1)* np.power(T_e,-0.15) * (np.log(np.divide(4.995e-2, nu)) + 1.5 * np.log(T_e))
    T_ff = 8.235e-2 * a * np.power(T_e,-0.35) * np.power(nu,-2.1) * (1. + 0.08) * EM

    S = 2. * k * beam * np.power(np.multiply(nu,1e9),2)  / c**2 * T_ff * 1e26

    return S



# Anomalous Microwave Emission (Lognormal Approximation)

def ame(nu, beam, A_AME, nu_AME, W_AME):
    ''' Here the beam doesn't do anything, but you still need it '''

    nlog = np.log(nu)
    nmaxlog = np.log(nu_AME)

    S = A_AME*np.exp(-0.5 * ((nlog-nmaxlog)/W_AME)**2)

    return S



# Thermal Dust Emission

def thermaldust(nu, beam, T_d, tau, beta):

    c = 299792458.
    k = 1.3806488e-23
    h = 6.62606957e-34
    nu = np.multiply(nu,1e9)

    planck = np.exp(h*nu/k/T_d) - 1.
    modify = 10**tau * (nu/1.2e12)**beta
    S = 2 * h * nu**3/c**2 /planck * modify * beam * 1e26

    return S



# CMB Anisotropies

def cmb(nu, beam, dT):


    def planckcorr(nu_in):
        c = 299792458.
        k = 1.3806488e-23
        h = 6.62606957e-34
        T_cmb = 2.725
        nu = np.multiply(nu_in,1e9)
        x = h*nu/k/T_cmb
        return x**2*np.exp(x)/(np.exp(x) - 1.)**2

    c = 299792458.
    k = 1.3806488e-23
    h = 6.62606957e-34

    nu = np.multiply(nu,1e9)

    T_cmb = 2.725
    xx = h * nu / (k*T_cmb)
    xx2 = h* nu / (k * (T_cmb + dT))

    nu_Hz = np.divide(nu,1e9)

    S = (2. * k * nu**2 * beam / c**2) * dT * planckcorr(nu_Hz) * 1e26

    return S



# Add Your Custom Model!

def custom_model(nu, beam, variable1, variable2, add_your_own_variables):

    c = 299792458.
    k = 1.3806488e-23
    h = 6.62606957e-34

    S = 0

    return S
