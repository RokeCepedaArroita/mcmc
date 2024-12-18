''' emission.py:
List of emission functions:
The first two arguments must be "nu" and "beam".
Add your custom functions at the end!
Default values in function definitions will be fitted, so hardcode them if you want them fixed - see
the case of freefree, where T_e has been fixed to 7500 K.
'''

import numpy as np



# Synchrotron Emission

def synchrotron(nu, beam, A_sync, alpha):

    # TODO: add beam here so that amplitude is in Janksys

    c = 299792458.
    k = 1.3806488e-23
    h = 6.62606957e-34

    S = A_sync * nu**alpha

    return S


# # Free-Free Emission
#
# def freefree(nu, beam, EM):
#     ''' Full Draine 2011 free-free model put into numpy '''
#
#     Te = 7500 # K, fixed temperature
#
#     c = 299792458.
#     g_ff = np.log(np.exp(5.960 - (np.sqrt(3.0)/np.pi)*np.log(np.multiply(nu, (Te/10000.0)**(-3.0/2.0) ) )) + 2.71828)
#     tau_ff = 5.468e-2 * np.power(Te,-1.5) * np.power(nu,-2.0) * EM * g_ff
#     T_ff = Te * (1.0 - np.exp(-tau_ff))
#     S = 2.0 * 1380.6488 * T_ff * np.power(np.multiply(nu,1e9),2) / c**2  * beam
#
#     return S



# Anomalous Microwave Emission (Lognormal Approximation)

def ame(nu, beam, A_AME, nu_AME, W_AME):
    ''' Here the beam doesn't do anything, but you still need it '''

    # TODO: scale by the beam so that amplitude of AME is in janskys!!!

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
    modify = 10**tau * (nu/353e9)**beta # set to tau_353
    S = 2 * h * nu**3/c**2 /planck * modify * beam * 1e26

    return S


# CMB Anisotropies

def cmb(nu, beam, dT):

    dT = dT/1e6 # dT in microkelvin


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



# Clive's Thermal Dust Curve. As far as I know it is the same as thermaldust above!

def thermal_dust_clive(nu, beam, thermaldust_amp, thermaldust_index, thermaldust_temp):

    c = 299792458.
    k = 1.3806488e-23
    h = 6.62606957e-34
    dust_optical_depth_freq = 1198.8

    nu = np.array(nu)
    nu_9 = np.multiply(nu,1e9)

    xx = np.multiply(h,nu_9)/np.multiply(k,thermaldust_temp)
    dust_norm = (nu/dust_optical_depth_freq)**thermaldust_index
    nu_over_c = (nu_9**3)/(c**2)
    bbody = 1/(np.exp(xx)-1)
    thermaldust=2*h*bbody*nu_over_c*dust_norm
    S = thermaldust_amp*thermaldust*beam*1e26

    return S



# def freefree(nu, beam, EM):
#
#     T_e = 7500. # fixed electron temperature
#
#     c = 299792458.
#     k = 1.3806488e-23
#     h = 6.62606957e-34
#
#     a = 0.366 * np.power(nu,0.1)* np.power(T_e,-0.15) * (np.log(np.divide(4.995e-2, nu)) + 1.5 * np.log(T_e))
#     T_ff = 8.235e-2 * a * np.power(T_e,-0.35) * np.power(nu,-2.1) * (1. + 0.08) * EM
#
#     S = 2. * k * beam * np.power(np.multiply(nu,1e9),2)  / c**2 * T_ff * 1e26
    #
    # return S



# def freefree(nu, beam, EM):
#     ''' Full Draine 2011 free-free model '''
#
#     Te = 7500 # K, fixed temperature
#
#     c = 299792458.
#     g_ff = np.log(np.exp(5.960 - (np.sqrt(3.0)/np.pi)*np.log(nu*(Te/10000.0)**(-3.0/2.0))) + 2.71828)
#     tau_ff = 5.468e-2 * Te**(-1.5) * nu**(-2.0) * EM * g_ff
#     T_ff = Te * (1.0 - np.exp(-tau_ff))
#     S = 2.0 * 1381.0 * T_ff * (nu*1e9)**2 / c**2  * beam
#
#     return S



#Free-Free Emission with Optically Thick Downturn

def freefree(nu, beam, EM):

    T_e = 7500 # fixed electron temperature

    c = 299792458.
    k = 1.3806488e-23
    h = 6.62606957e-34

    import math
    import numpy as np
    nu = np.array(nu)

    part_1 = np.power(T_e/10000,(-3/2))
    part_2 = np.log(1*nu*part_1)
    part_3 = (np.sqrt(3)/math.pi)*part_2
    part_4 = 5.960-part_3
    part_5 = np.exp(part_4)+2.71828
    g_ff = np.log(part_5)


    tau_ff = (5.468*(10**-2))*(T_e**-1.5)*(nu**-2)*EM*g_ff

    T_ff = T_e*(1. - np.exp(-tau_ff))
    #smalltau = np.where(tau_ff <  1.0e-10)[0]
    #'if (smalltau[0] > 0):
    #    T_ff[smalltau] = T_e * (tau_ff[smalltau] - (-tau_ff[smalltau]**2)/2 - (-tau_ff[smalltau]**3)/6)
    S = 2. * k * beam * np.power(np.multiply(nu,1e9),2)*T_ff*1e26 / c**2

    return S


# class pdr:
#
#     def __init__(self,nu, beam, A_AME, nu_AME):
#         # find max
#         # interp func
#
#     def __call__(self, nu, beam, A_AME, nu_AME):
#         # pdr1 = pdr(...)
#         # S = pdr1(nu, beam, A_AME, nu_AME)
#         # pdr1.func1(something)
#         S = np.multiply(query_template(template, modified_nu), A_AME*beam*1e20)
#
#         return S


def pdr(nu, beam, A_AME, nu_AME):
    ''' Loads template and then shifts, scales and evaluates it'''

    template_dir = '/scratch/nas_falcon/scratch/rca/projects/mcmc/amemodels'
    template_name = 'spdust2_rn.dat'

    # Read templates and skip first 21 rows of info
    template = np.loadtxt(template_dir+'/'+template_name, skiprows=21)

    def findmaxima(template):
        '''Find the amplitude and peak frequency values of your template using spline interpolation'''
        from scipy.interpolate import InterpolatedUnivariateSpline
        x_axis = template[:,0]
        y_axis = template[:,1]
        f = InterpolatedUnivariateSpline(x_axis, y_axis, k=4)
        cr_pts = f.derivative().roots()
        cr_pts = np.append(cr_pts, (x_axis[0], x_axis[-1]))  # also check the endpoints of the interval
        cr_vals = f(cr_pts)
        max_index = np.argmax(cr_vals)

        max_amplitude = cr_vals[max_index]
        peak_frequency = cr_pts[max_index]

        return max_amplitude, peak_frequency


    # Evaluate peak frequency and amplitude of your template
    max_amplitude, peak_frequency = findmaxima(template)

    # Modify your query frequencies (thus effectively "shifting" your templates)
    frequency_shift =  nu_AME - peak_frequency
    modified_nu = np.subtract(nu, frequency_shift)

    # Query interpolated template at nu points
    def query_template(template, nu):
        '''Find the amplitude and peak frequency values of a template at given nu values'''
        from scipy.interpolate import InterpolatedUnivariateSpline
        x_axis = template[:,0]
        y_axis = template[:,1]
        f = InterpolatedUnivariateSpline(x_axis, y_axis, k=4)
        S = f(nu)
        return S

    # Get flux and scale so that  AME amplitude is in Janksys
    S = np.multiply(query_template(template, modified_nu), A_AME*beam*1e20)

    return S




# Add Your Custom Model!

def custom_model(nu, beam, variable1, variable2, add_your_own_variables):

    c = 299792458.
    k = 1.3806488e-23
    h = 6.62606957e-34

    S = 0

    return S
