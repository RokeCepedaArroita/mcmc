''' config.py:
MCMC configuration file
'''


# FIT SETTINGS

settings = {'name': 'MCMC',  # name with which your results and figures will start


            # MCMC Settings

            'MCMC': {'nwalkers': 200,               # number of walkers - the more, the wider the parameter space explored
                     'nsteps': 800,                 # number of steps
                     'nburnin': 400,                # number of burn-in steps
                     'randomisation': 30,           # percentage spread of initial guesses
                     'stuck_threshold': 0.001},     # if a walker's standard deviation is less than x%, then throw it because it's stuck


            # Pooling Threads

            'nthreads': 8, # 8 is the optimal number in vulture (any more or less and it will be slower)


            # Pre-Fit Using Least Squares (requires scipy)
            # THIS IS NOT FULLY WORKING YET (AS OF JAN 25 2019), SO KEEP IT SET TO FALSE

            'least_sq_prefit': False,


            # SED Model Settings - choose the number of models of each type!

            'components': {'synchrotron': 0,    # synchrotron emission
                           'freefree': 1,       # free-free emission
                           'ame': 1,            # anomalous microwave emission
                           'cmb': 0,            # cmb anisotropies
                           'thermaldust': 1,    # thermal dust emission
                           'custom_model': 0},  # add your own here!


            # Hard Priors - variable names must match the names in your emission functions
            # Note: case sensitive; if you have more than one model of each, refer to your parameters
            # as "param", "param1", "param2"... for your first, second, third... models
            # Defaults are [-np.inf, np.inf] '''

            'priors': {'T_d': [10, 100],
                       'tau': [-5, -2],
                       'beta': [1.2, 2.2],
                       'nu_AME': [5, 60],
                       'W_AME': [0.2, 1],
                       'nu_AME1': [5, 60],
                       'W_AME': [0.2, 1],
                       'T_d1': [10, 100],
                       'tau1': [-5, -2],
                       'beta1': [1.2, 2.2]},


            # Initial Guesses - variable names must match the names in your emission functions
            # Note: case sensitive; if you have more than one model of each, refer to your parameters
            # as "param", "param1", "param2"... for your first, second, third... models
            # Defaults are 1, or results of the least squares pre-fit if activated '''

            'guesses': {'A_sync': 10,
                        'alpha': -3,
                        'EM': 200,
                        'A_AME': 10,
                        'nu_AME': 30,
                        'W_AME': 0.5,
                        'T_d': 21,
                        'tau': -2.8,
                        'beta': 1.6,
                        'dT': 3e-4,
                        'nu_AME1':30,
                        'T_d1': 21,
                        'tau1': -2.8,
                        'beta1': 1.6},


            # Plotting Settings
            # TODO: add finer plotting control

            'plotting': {'resultdir': 'results',      # results save directory, relative to current path
                         'plotdir': 'results',        # figure save directory, relative to current path
                         'plotSED': False,             # save SED plot
                         'plotCorner': False,          # save corner plot
                         'plotWalkers': False,         # save walkers plot
                         'dpi': 300},                 # set dots per inch value


            # Verbosity Setting

            'verbose': True,     # print pre-fit information and results



            # LaTeX Formatting:
            # Optional. Names must match function argument names.

            'formatting': {'A_sync': '$A_{sync}$',
                        'alpha': r'$\alpha$',
                        'EM': '$EM$',
                        'A_AME': '$A_{AME}$',
                        'nu_AME': r'$\nu_{AME}$',
                        'W_AME': '$W_{AME}$',
                        'T_d': '$T_d$',
                        'tau': r'$\tau$',
                        'beta': r'$\beta$',
                        'dT': r'$\delta_{T}$'}

            }
