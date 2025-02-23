''' tools.py:
Class and function definitions
'''

import numpy as np


class SED():



    def __init__(self, data, settings):
        '''
        Initialise object
        '''


        self.data = data # this is your SED to fit: nu, flux, flux_error, beam, excluded freq
        self.settings = settings # configuration file: mcmc, components, plotting and verbose


        # Total SED model parameters: components and free parameters

        self.model = {'sed_model': [],         # total SED model, which is a superposition of all components
                 'sed_params': [],             # values of free-parameters in an array
                 'sed_names': [],              # names of free parameters in an array
                 'sed_names_latex': [],        # names of free parameters in LaTeX format
                 'sed_units_latex': [],        # units of free parameters in LaTeX format
                 'sed_nameunit_latex': [],     # strings with both the names and units
                 'sed_errors': [],             # 1-sigma averages
                 'sed_upper_sigma': [],        # upper 1-sigma range
                 'sed_lower_sigma': [],        # lower 1-sigma range
                 'sed_acceptance': [],         # acceptance of mcmc
                 'sed_priors': [],             # here can add priors
                 'sed_guess': [],              # initial guess
                 'sed_chi_squared': [],        # reduced chi-squared of fit


                 # Individual Components

                 'components': {'function': [],           # actual pointer to function of each component
                                'n_components': [],       # number of components of each type added
        		                'name_params': [],        # names of free parameters in each component
        		                'n_params': []            # number of free parameters in each component
                                },


                'walkers': {'kept': [],             # indices of walkers kept
                            'percent_kept': []      # percentage of walkers kept
                            },


                'timing' : {'mcmctime': [],           # time taken to perform MCMC
                            'sed_time': [],           # time taken to plot SED
                            'walker_time': [],        # time taken to plot walkers
                            'corner_time': [],        # time taken to plot corner figure
                            'ls_sq_time': [],         # time taken to prefit using lmfit
                            'start': [],              # start time
                            'finish': [],             # finish time
                            'runtime': [],            # total runtime
                            'timestamp': []           # string with starting datetime
                            }

        }


        # MCMC chain: samples

        self.mcmc_chain = {'samples': [],   # filtered MCMC samples (no nburnin or convergence fails)
                      'full_samples': []    # raw MCMC samples, containing all nburnin and stuck walkers
                      }


        # Record timing information

        import datetime
        import time

        self.model['timing']['timestamp'] = datetime.datetime.today().strftime('%Y%b%d_%H%M%S')
        self.model['timing']['start'] = time.time()


    def check_input(self):
        '''
        Perform a sanity check on your input variables before attempting to run the rest
        '''

        if self.settings['MCMC']['nburnin'] > self.settings['MCMC']['nsteps']:
            print('\nMCMC INPUT ERROR: burn-in steps ({}) greater than number of steps ({})!\n'.format(self.settings['MCMC']['nburnin'], self.settings['MCMC']['nsteps']))
            print('EXECUTION STOPPED.\n')
            exit()



    def fetch_sed_parameters(self):
        '''
        Create list of unique parameters and in the order in which they have to be put into build_model
        Remember that "nu" and "beam" must always be first two arguments of an emission function
        '''

        COMPONENT_NAMES = [key for key,value in self.settings['components'].items() if value > 0]
        COMPONENT_QUANTITIES = [value for key,value in self.settings['components'].items() if value > 0]


        def get_function_paramaters(func):
            '''
            Function to fetch parameters and number of parameters
            '''

            from inspect import getfullargspec

            params = getfullargspec(func).args  # Get the positional argument names
            nparams = len(params)  # Count the number of parameters

            return params, nparams

        # Get model information from emission.py

        import emission

        ncomponent = 0

        for funcname, quantity in zip(COMPONENT_NAMES, COMPONENT_QUANTITIES):
            for i in np.arange(quantity): # add right number of models of each
                component = getattr(emission, funcname) # get pointer to function
                params, nparams = get_function_paramaters(component)
                freeparams = params[2:] # exclude first two parameters 'nu' and 'beam'
                comp_nparams = nparams - 2 # since the first two will be 'nu' and 'beam'

                # If there is more than one component of each type, give each free parameter name an index

                if i > 0:
                    freeparams = [s + str(i) for s in freeparams]

                # Assign model properties

                self.model['components']['function'].append(component)
                self.model['components']['n_components'].append(ncomponent)
                self.model['components']['name_params'].append(freeparams)
                self.model['components']['n_params'].append(comp_nparams)

                ncomponent += 1


        # Flatten all variable names into one list

        self.model['sed_names'] = [j for sub in self.model['components']['name_params'] for j in sub]


        # Assign LaTeX-formatted names

        self.model['sed_names_latex'] = [self.settings['formatting'][name] if name in self.settings['formatting'] else name for name in self.model['sed_names']]


        # Assign LaTeX-formatted units

        self.model['sed_units_latex'] = [self.settings['units'][name] if name in self.settings['formatting'] else '' for name in self.model['sed_names']]


        # Merge names and units here

        for varname, varunit in zip(self.model['sed_names_latex'], self.model['sed_units_latex']):
            if varunit != '':
                self.model['sed_nameunit_latex'].append(varname+' ('+varunit+')')
            else:
                self.model['sed_nameunit_latex'].append(varname)


        # Initialise all variable values as zeros

        self.model['sed_params'] = np.zeros(np.size(self.model['sed_names']))

        # Initialise all variable errors as zeros

        self.model['sed_errors'] = np.zeros(np.size(self.model['sed_names']))

        # Initialise all sigma_bounds as zeros

        self.model['sed_upper_sigma'] = np.zeros(np.size(self.model['sed_names']))
        self.model['sed_lower_sigma'] = np.zeros(np.size(self.model['sed_names']))

        # Initialise priors as [-inf, +inf]

        self.model['sed_priors'] = [[-np.inf, np.inf] for element in self.model['sed_params']]

        # Initialise guesses as ones

        self.model['sed_guess'] = np.full(shape=np.size(self.model['sed_names']), fill_value=1.)

        # Copy priors from self.settings to self.model

        j = 0
        for name in self.model['sed_names']:
            if name in self.settings['priors']: # if priors have been assigned to this variable
                self.model['sed_priors'][j] = self.settings['priors'][name]  # replace prior values
            j += 1

        # Copy initial guesses from self.settings to self.model

        j = 0
        for name in self.model['sed_names']:
            if name in self.settings['guesses']: # if guesses have been assigned to this variable
                self.model['sed_guess'][j] = self.settings['guesses'][name]  # replace prior values
            j += 1

        # Initialise variables by copying guesses

        self.model['sed_params'][:] = self.model['sed_guess'][:]

        # Define non-excluded frequencies, fluxes and flux_errors

        self.data['nu_fitted'] = [freq for freq in self.data['nu'] if freq not in self.data['excluded']]
        self.data['flux_fitted'] = [flux for flux,freq in zip(self.data['flux'],self.data['nu']) if freq not in self.data['excluded']]
        self.data['flux_err_fitted'] = [flux_err for flux_err,freq in zip(self.data['flux_err'],self.data['nu']) if freq not in self.data['excluded']]


        return




    def build_model(self):
        '''
        Creates model from combination of foregrounds
        '''

        # Import Emission Models

        import emission


        # Create Total Model

        def sed_model(nu, beam, freeargs):
            '''
            Sum of all component models
            '''

            total_flux = 0  # initialise flux

            argn = 0 # first argument number

            for i in self.model['components']['n_components']:

                # Read model structure

                component = self.model['components']['function'][i]
                comp_nameparams = self.model['components']['name_params'][i]
                comp_nparams = self.model['components']['n_params'][i]

                # Pass the right number of arguments to each function

                args_to_pass = freeargs[argn:argn+comp_nparams]

                # Calculate the flux of each component and add all together

                total_flux += component(nu,beam,*args_to_pass) # call each function and add up the flux

                # Get index for the next set of parameters

                argn += comp_nparams

            return total_flux


        # Copy the total SED function to self.model['sed_model']

        self.model['sed_model'] = sed_model

        return




    def prefit_info(self):
        '''
        Print pre-fit information:
        NFREQ, NMODELPARAMS, MODEL, SETTINGS
        '''

        if self.settings['verbose']:

            # Calculate Values

            NFREQ = np.size(self.data['nu'])

            N_NOT_EXCLUDED = len([freq for freq in self.data['nu'] if freq not in self.data['excluded']])
            NEXCLUDED = NFREQ-N_NOT_EXCLUDED
            NFREEPARAMS = sum(self.model['components']['n_params'])
            COMPONENT_NAMES = [key for key,value in self.settings['components'].items() if value > 0]
            COMPONENT_QUANTITIES = [value for key,value in self.settings['components'].items() if value > 0]

            COMPONENT_STRING = str() # initialise empty string
            for name, quantity in zip(COMPONENT_NAMES, COMPONENT_QUANTITIES):
                COMPONENT_STRING = COMPONENT_STRING + '{}(x{}) '.format(name.upper(), quantity)

            print('\n************** PRE-FIT INFORMATION **************\n')
            print('NFREQ = {}, NEXCLUDED = {}, NFREEPARAMS = {}'.format(NFREQ, NEXCLUDED, NFREEPARAMS))
            print('NWALKERS = {}, NSTEPS = {}, NBURNIN = {}'.format(self.settings['MCMC']['nwalkers'],
                self.settings['MCMC']['nsteps'],self.settings['MCMC']['nburnin']))
            print('NTHREADS = {}, PREFIT_USING_LEAST_SQ = {}'.format(self.settings['nthreads'],str(self.settings['least_sq_prefit']).upper()))
            print('COMPONENTS = {}'.format(COMPONENT_STRING))
            print('\n')

            return




    def check_priors(self,theta=None):
        '''
        Returns true if all parameters are within priors, false otherwise
        '''

        if theta is None: # if theta not defined
            params_to_check = self.model['sed_params']
        else: # if theta actually defined
            params_to_check = theta

        # Check whether numbers are within priors

        for current_value, priors in zip(params_to_check,self.model['sed_priors']):
                if not priors[0] < current_value < priors[1]: # if value NOT in range of priors
                    return False

        return True # if all numbers are in range




    def mcmc_fit(self):
        '''
        Perform Monte Carlo Fit
        '''

        # Import Modules

        import os
        import time
        import emcee
        import corner

        if self.settings['nthreads'] > 1: # Do not use this together with MPI or memory usage will build up!
            from multiprocessing import Pool


        # Define Prior, Likelihood and Sampling Functions

        def lnprior(theta):
            '''
            Prior function with Gaussian prior for dT parameter if it exists
            '''
            # First check if parameters are within basic bounds
            all_within_priors = self.check_priors(theta)
            if not all_within_priors:
                return -np.inf

            # Initialize prior to 0.0 (for uniform prior case)
            lnp = 0.0

            # Only apply Gaussian prior if dT exists in parameters
            try:
                dT_idx = self.model['sed_names'].index('dT')
                # Gaussian prior parameters for dT
                dT_mean = 0.0
                dT_std = 32.3
                # Add Gaussian prior contribution for dT
                lnp += -0.5 * ((theta[dT_idx] - dT_mean) / dT_std)**2
            except ValueError:
                # dT not in parameters, just use uniform prior
                pass

            return lnp



        def lnlike(theta, x, y, yerr):
            '''
            Likelihood function
            '''

            sed_params = theta

            # Evaluate model and return likelihood

            model = self.model['sed_model'](x,self.data['beam'],sed_params)

            return -0.5*(np.sum( ((y-model)/yerr)**2. ))


        global lnprob

        def lnprob(theta, x, y, yerr):
            '''
            Sampling function
            '''

            lp = lnprior(theta) # check priors

            if not np.isfinite(lp): # if priors not fulfilled
                return -np.inf

            return lp + lnlike(theta, x, y, yerr) # if priors satisfied return likelihood



        def ls_initialisation(self): # TODO: massively improve this initialisation step
            '''
            Fit using lmfit least-squares fitting to initialise positions
            If outside priors then go back to defaults in config
            If you don't have lmfit use 'pip install lmfit' or
            'conda install -c conda-forge lmfit' if you are on Anaconda
            '''

            import time

            time0 = time.time() # start time


            from lmfit import minimize, Parameters, Parameter,fit_report, Minimizer


            # Attempt to pre-fit using lmfit


            try:

                # Add parameters one my one

                lm_param = Parameters()

                for param_name, prior, guess in zip(self.model['sed_names'],self.model['sed_priors'], self.model['sed_guess']):
                    lm_param.add(param_name, guess, vary=True, min=prior[0],max=prior[1])


                # Define error and residual functions

                def Error(lm_param, nu, flux, flux_err):

                    # Convert to numpy arrays
                    nu = np.array(nu)
                    flux = np.array(flux)
                    flux_err = np.array(flux_err)

                    # Extract current parameters from lmfit object lm_param
                    current_params = [x for x in lm_param.valuesdict().values()]

                    # Evaluate model
                    model = self.model['sed_model'](nu, self.data['beam'], current_params)

                    return ((model-flux)*(1./flux_err))**2

                def Residual(r):
                    return np.sum(r.dot(r.T))


                # Fit the function

                fitter = Minimizer(Error,lm_param, reduce_fcn=Residual,fcn_args=(self.data['nu_fitted'],
                    self.data['flux_fitted'], self.data['flux_err_fitted']))

                lmfit_results = fitter.minimize(method='leastsq')


                # Extract resulting parameters

                lmfit_params = [x for x in lmfit_results.params.valuesdict().values()]


                # Copy Results to Current Parameter Values

                self.model['sed_params'] = lmfit_params


                # Timing information

                time1 = time.time() # stop time
                self.model['timing']['ls_sq_time'] = time1-time0


                # If results are within priors, copy them to guesses!
                # It is the parameters that going to be used to initialise the MCMC walkers after all

                all_within_priors = self.check_priors()
                if not all_within_priors: # if priors not satisfied by lmfit results
                    self.model['sed_params'] = self.model['sed_guess'] # revert back to initial guesses
                    if self.settings['verbose']:
                        print('*************** LEAST-SQUARES INFO **************')
                        print('Could not initialise using least squares since')
                        print('your least-squares results are outside your priors.')
                        print('The original guesses will be passed to MCMC instead.\n')

                elif all_within_priors:
                    if self.settings['verbose']:
                        print('*************** LEAST-SQUARES INFO **************')
                        print('Succesfully initialised guesses in {0:.1f} seconds!\n'.format(self.model['timing']['ls_sq_time']))


            except:  # If lmfit fails
                if self.settings['verbose']:
                    print('*************** LEAST-SQUARES INFO **************')
                    print('Could not initialise using least squares since a')
                    print('general lmfit error occurred (e.g. poor data/models).')
                    print('The original guesses will be passed to MCMC instead.\n')


            return





        # If Toggled in config.py, Run a Least Squares Initialisation

        if self.settings['least_sq_prefit']:
            ls_initialisation(self)


        # Fetch the Number of Dimensions / Free Parameters

        ndim = len(self.model['sed_params'])


        # Initialise and Randomise Walker Positions Using an X% Gaussian Ball

        pos = [self.model['sed_params'] + self.settings['MCMC']['randomisation']*1e-2*np.random.randn(ndim) for i in range(self.settings['MCMC']['nwalkers'])]


        # Perform Multithread MCMC

        if self.settings['nthreads'] > 1:

            pool_object = Pool(self.settings['nthreads'])

            sampler = emcee.EnsembleSampler(self.settings['MCMC']['nwalkers'], ndim, lnprob, args=(self.data['nu_fitted'], self.data['flux_fitted'],
                self.data['flux_err_fitted']), pool=pool_object)

        else:
            sampler = emcee.EnsembleSampler(self.settings['MCMC']['nwalkers'], ndim, lnprob, args=(self.data['nu_fitted'], self.data['flux_fitted'],
                self.data['flux_err_fitted']))

        time0 = time.time() # start time

        import warnings
        with warnings.catch_warnings(): # turn off annoying emcee mcmctime warnings
            warnings.simplefilter("ignore")
            pos, prob, state  = sampler.run_mcmc(pos, self.settings['MCMC']['nsteps'], progress=True)


        # Very important to close the pool if you don't want threads to hang on forever!

        if self.settings['nthreads'] > 1:
            pool_object.close()

        time1 = time.time() # stop time

        self.model['timing']['mcmctime'] = time1-time0


        # Flatten Chain and Discard 'nburnin' measurements (don't use sampler.flatchain)
        samples = sampler.chain[:, self.settings['MCMC']['nburnin']:, :].reshape((-1, ndim)) # mix all walkers together and steps after burn in

        # TODO: IMPROVE CONVERGENCE FILTERS
        # At the moment filtering walkers with standard deviations of less than 0.001%. Using exactly 0% will catch almost all cases, so maybe that is a better idea in the future.
        # This would avoid having to define this arbitrary threshold of 0.001%.

        walker_nanstd = np.nanstd(np.diff(sampler.chain[:, -(self.settings['MCMC']['nsteps']-self.settings['MCMC']['nburnin']):, 0], axis=1),axis=1)
        walker_nanmean = np.nanmean(sampler.chain[:, -(self.settings['MCMC']['nsteps']-self.settings['MCMC']['nburnin']):, 0],axis=1)
        mean_walker_value = np.nanmedian(walker_nanmean)


        # Often, walkers that have started outside priors will be stuck, so the nanstd value to be filtered will be exactly or very close to 0.
        # Instead we throw walkers with a tunable percentage standard deviation of less than self.settings['MCMC']['stuck_threshold']%. For example, 0.001%.
        # This stuck walker will also be reflected in every other parameter, so there is no point in checking every single parameter, but the first one.

        '''
        This is the bit that needs changing. We should start by adding an option walker_filter = 'simple_sigma_clip' that contains a 5 sigma filter based on just mean and errors up and down on each side, which we can pull from below. Late add more advanced 'MAD' methods.
        '''


        def sigma_clipping(burned_samples, sigma_level):

            return #walkers_kept


        # Fixed bug where if the mean is negative it would get rid of every walker, by adding np.abs (Dec 2024)
        self.model['walkers']['kept'] = np.where(np.abs(np.divide(walker_nanstd,mean_walker_value)) > self.settings['MCMC']['stuck_threshold'])
        self.model['walkers']['percent_kept'] = np.divide(float(len(self.model['walkers']['kept'][0])),self.settings['MCMC']['nwalkers'])*1e2


        # Copy Full Samples

        self.mcmc_chain['full_samples'] = sampler.chain # TODO: find less memory intensive way of doing this


        # Remove Samples that Did Not Pass Convergence Test

        samples = sampler.chain[self.model['walkers']['kept'], self.settings['MCMC']['nburnin']:, :].reshape((-1, ndim))



        # Record Parameter Values and Errors

        for i in range(ndim): # for all parameters

            # Get Lower 1-sigma, 50% and Upper 1-sigma Quantiles
            mcmc = corner.quantile(samples[:,i], [0.1586552539314571, 0.5, 0.8413447460685429]) # get 1 sigma range

            # Assign 50% Quantile as Final Parameter
            self.model['sed_params'][i] = mcmc[1]

            # Assign Upper and Lower 1-sigma Bounds
            sigma_bounds = np.diff(mcmc)
            self.model['sed_lower_sigma'][i] = sigma_bounds[0]
            self.model['sed_upper_sigma'][i] = sigma_bounds[1]

            # Assign "Mean" 1-sigma Bound
            self.model['sed_errors'][i] = np.mean(sigma_bounds)



    	# Reduced Chi-Squared Calculator

        def chi_squared(ydata,fit,p,errors=None):

            if errors is not None:
                chi_sq = np.sum(np.divide(np.power(ydata-fit,2),np.power(errors,2)))/(len(ydata)-len(p))

            else:
                chi_sq = np.sum(np.power(ydata-fit,2))/(len(ydata)-len(p))

            return chi_sq



        # Calculate Reduced Chi-Squared

        self.model['sed_chi_squared'] = chi_squared( self.data['flux_fitted'], self.model['sed_model'](self.data['nu_fitted'],self.data['beam'],
            self.model['sed_params']), self.model['sed_params'], errors=self.data['flux_err_fitted'])


        # Record Acceptance Fraction

        self.model['sed_acceptance'] = np.mean(sampler.acceptance_fraction)


        # Record samples

        self.mcmc_chain['samples'] = samples


        return




    def save_results(self, source_information=None):
        '''
        Saves results to ASCII text file
        '''

        # Build name of Save File

        if not isinstance(self.settings['source_name'], type(None)): # if source name is defined save to own directory
            import os   # Make source-specific directory
            if not os.path.exists('{}/{}'.format(self.settings['plotting']['resultdir'],self.settings['source_name'])):
                os.makedirs('{}/{}'.format(self.settings['plotting']['resultdir'],self.settings['source_name']))
            save_name = str(self.settings['source_name'])+'/'+self.settings['name']+'_'+str(self.settings['source_name'])+'_'+self.model['timing']['timestamp']+'.txt'
        else: # if it is not defined, save it to the main directory
            save_name = self.settings['name']+'_'+self.model['timing']['timestamp']+'.txt'


        # Record Timing Info

        import time
        self.model['timing']['finish'] = time.time()


        # Overall Runtime

        self.model['timing']['runtime'] = self.model['timing']['finish']-self.model['timing']['start']


        # Save Data to ASCII

        fo = open(self.settings['plotting']['resultdir']+'/'+save_name, 'w')

        yourDictionary = self.settings

        fo.write('*********** INPUT SETTINGS ***********\n\n')

        for key, value in self.settings.items():
            fo.write(str(key) + ': '+ str(value) + '\n\n')

        fo.write('\n\n************ INPUT DATA **************\n\n')

        for key, value in self.data.items():
            fo.write(str(key) + ': '+ str(value) + '\n\n')

        fo.write('\n\n*********** RESULTS & MODELS ***********\n\n')

        for key, value in self.model.items():
            fo.write(str(key) + ': '+ str(value) + '\n\n')

        fo.close()


        # Save Data to Joblib json file
        from joblib import dump
        joblib_save_name = save_name.replace('.txt', '.joblib')

        # Temporarily remove the 'sed_model' before saving
        temp_sed_model = self.model.pop('sed_model', None)

        # Save the object without 'sed_model'
        if source_information is not None:
            dump({'settings': self.settings, 'data': self.data, 'model': self.model, 'source': source_information},
                 self.settings['plotting']['resultdir'] + '/' + joblib_save_name, compress=0)
        else:
            dump({'settings': self.settings, 'data': self.data, 'model': self.model},
                 self.settings['plotting']['resultdir'] + '/' + joblib_save_name, compress=0)

        # Restore the 'sed_model' after saving
        self.model['sed_model'] = temp_sed_model

        if self.settings['verbose']:
            print('\n************** RESULTS SAVED! *************\n')
            save_name_without_txt = save_name.replace('.txt', '')
            print('Saved files as {} in {}'.format(save_name_without_txt, self.settings['plotting']['resultdir']))
            print('Program finished with a runtime of {:.0f}s!\n'.format(self.model['timing']['runtime']))




    def plot_sed(self):
        '''
        Saves SED Plot
        '''

        import time
        import matplotlib.pyplot as plt

        # Serif font for papers
        plt.rc('font', family='serif')
        plt.rc('font', family='serif')
        plt.rc('mathtext',fontset='cm',rm='serif')

        time0 = time.time() # start time


        if self.settings['plotting']['plotSED']:

            # Start gridspec

            factor_smaller = 1.15
            ratio_figures = [1, 0.2]

            fig = plt.figure(1,figsize=(5.2*factor_smaller,4.52*factor_smaller)) # plot fit & components

            # Define subplots

            from matplotlib import gridspec
            gs = gridspec.GridSpec(2, 1, height_ratios=ratio_figures) # set height ratios for sublots
            ax0 = plt.subplot(gs[0])
            ax1 = plt.subplot(gs[1], sharex=ax0)
            plt.setp(ax0.get_xticklabels(), visible=False)
            ax0.tick_params(axis='x', which='both', direction='in')

            nu_space = np.logspace(-2,5,400) # create well-sampled x-space


            # Plot Spread of SEDs in the MCMC Chain  # TODO: MAKE NUMBER OF CHAIN SEDS = 100 TUNABLE ?

            for mcmc_params in self.mcmc_chain['samples'][np.random.randint(len(self.mcmc_chain['samples']), size=100)]:
                ax0.plot(nu_space, self.model['sed_model'](nu_space,self.data['beam'],mcmc_params), color='#0072bd', alpha=0.05)


            # Plot Each Component

            argn = 0 # first argument number

            # Define Style repetition

            style_rep = ['--', '-.', ':']

            for i in self.model['components']['n_components']:

                # Read model structure

                component = self.model['components']['function'][i]
                comp_nameparams = self.model['components']['name_params'][i]
                comp_nparams = self.model['components']['n_params'][i]


                # Pass the right number of arguments to each function

                args_to_pass = self.model['sed_params'][argn:argn+comp_nparams]

                # Calculate the flux of each component

                component_flux = component(nu_space,self.data['beam'],*args_to_pass) # call each function and add up the flux

                # Plot it

                linestyle_to_use = np.mod(i,len(style_rep))
                ax0.plot(nu_space,component_flux,color="#c2c2d6", linestyle=style_rep[linestyle_to_use])

                # Get index for the next set of parameters

                argn += comp_nparams



            # Plot Final Model and Residuals

            ymodel = self.model['sed_model'](nu_space,self.data['beam'],self.model['sed_params'])
            ax0.plot(nu_space,ymodel, color='k', lw=1, alpha=0.8) # Plot Optimal solution

            for i in range(0,len(self.data['nu'])): # Data Points
                if self.data['nu'][i] in self.data['nu_fitted']: # Fitted -> Filled points
                    ax0.errorbar(self.data['nu'][i], self.data['flux'][i], yerr=self.data['flux_err'][i],color='#ff7f0e', fmt='o')
                else: # Not Fitted -> Hollow Points
                    ax0.errorbar(self.data['nu'][i], self.data['flux'][i], yerr=self.data['flux_err'][i], fmt='o', color='#ff7f0e',markerfacecolor='None')


            # Upper x-limit so that models are not shown over 7 THz since they become unphysical at such frequencies

            if np.max(self.data['flux'])*2. > 7e3: # if over 7 THz
                sed_upper_x_limit = 7e3
            else:
                sed_upper_x_limit = np.max(self.data['flux'])*2.
                sed_upper_x_limit = 7e3 # Forcing this for now since a bug occurs sometimes where the highest frequencies are chopped

            ax0.set_xscale('log')
            ax0.set_yscale('log')
            ax0.set_ylabel('Flux Density (Jy)')
            ax0.set_xlim([np.min(self.data['nu'])/2.,sed_upper_x_limit])
            ax0.set_ylim([0.02, np.max(self.data['flux'])*2.])


            # Plot residuals here as a thin x-axis subplot

            residuals = []
            residuals_fitted = []

            for i in range(0,len(self.data['nu'])): # Data Points
                if self.data['nu'][i] in self.data['nu_fitted']: # Fitted -> Filled points
                    ymodel_point = self.model['sed_model'](self.data['nu'][i],self.data['beam'],self.model['sed_params'])
                    #ax1.errorbar(self.data['nu'][i], self.data['flux'][i] - ymodel_point, yerr=self.data['flux_err'][i],color='#ff7f0e', fmt='o')
                    #residuals.append(self.data['flux'][i] - ymodel_point)
                    ax1.errorbar(self.data['nu'][i], (self.data['flux'][i] - ymodel_point)/self.data['flux_err'][i], color='#ff7f0e', fmt='o')
                    residuals.append((self.data['flux'][i] - ymodel_point)/self.data['flux_err'][i])
                    residuals_fitted.append((self.data['flux'][i] - ymodel_point)/self.data['flux_err'][i])
                else: # Not Fitted -> Hollow Points
                    ymodel_point = self.model['sed_model'](self.data['nu'][i],self.data['beam'],self.model['sed_params'])
                    #ax1.errorbar(self.data['nu'][i], self.data['flux'][i]-ymodel_point, yerr=self.data['flux_err'][i], fmt='o', color='#ff7f0e',markerfacecolor='None')
                    #residuals.append(self.data['flux'][i] - ymodel_point)
                    ax1.errorbar(self.data['nu'][i], (self.data['flux'][i] - ymodel_point)/self.data['flux_err'][i], fmt='o', color='#ff7f0e',markerfacecolor='None')
                    residuals.append((self.data['flux'][i] - ymodel_point)/self.data['flux_err'][i])

            ax1.set_xscale('log')
            ax1.plot([np.min(self.data['nu'])/2.,sed_upper_x_limit], [0,0], color='k', lw=1, alpha=0.8)
            # Add a grey band to highlight the ±1 sigma range
            ax1.fill_between(
                [np.min(self.data['nu']) / 2., sed_upper_x_limit],  # x-range
                -1,  # Lower y-limit
                1,   # Upper y-limit
                color='#0072bd',
                alpha=0.05*2,  # Transparency
                edgecolor='none',  # Disable edge lines
                zorder=0    # Ensure it's behind other plot elements
            )
            ax1.set_xlabel('Frequency (GHz)')
            ax1.set_ylabel(r'$\Delta\sigma$')
            ax1.set_xlim([np.min(self.data['nu'])/2.,sed_upper_x_limit])
            ax1.set_ylim([-np.max(np.abs(residuals_fitted))*1.5,np.max(np.abs(residuals_fitted))*1.5])




            # Remove vertical gap between subplots

            plt.tight_layout()
            plt.subplots_adjust(hspace=.03)


            # Build Name of Save File

            if not isinstance(self.settings['source_name'], type(None)): # if source name is defined save to own directory
                import os   # Make source-specific directory
                if not os.path.exists('{}/{}'.format(self.settings['plotting']['plotdir'],self.settings['source_name'])):
                    os.makedirs('{}/{}'.format(self.settings['plotting']['plotdir'],self.settings['source_name']))
                save_name = str(self.settings['source_name'])+'/'+self.settings['name']+'_'+str(self.settings['source_name'])+'_'+self.model['timing']['timestamp']+'_SED'
            else: # if it is not defined, save it to the main directory
                save_name = self.settings['name']+'_'+self.model['timing']['timestamp']+'_SED'


            # Save Figure

            if self.settings['plotting']['pdfSED']:
                plt.savefig(self.settings['plotting']['plotdir']+'/'+save_name+'.pdf', dpi=self.settings['plotting']['dpi'], bbox_inches='tight', pad_inches=0)
            else:
                plt.savefig(self.settings['plotting']['plotdir']+'/'+save_name+'.png', dpi=self.settings['plotting']['dpi'], bbox_inches='tight', pad_inches=0)

            # Suppress the specific warning
            import warnings
            warnings.filterwarnings("ignore", message=".*Attempt to set non-positive xlim.*")

            plt.clf()
            plt.close(1)

        time1 = time.time() # stop time
        self.model['timing']['sed_time'] = time1-time0


        return




    def plot_walkers(self):

        import time
        import matplotlib.pyplot as plt

        # Serif font for papers
        plt.rc('font', family='serif')
        plt.rc('font', family='serif')
        plt.rc('mathtext',fontset='cm',rm='serif')

        time0 = time.time() # start time


        if self.settings['plotting']['plotWalkers']:

            fig = plt.figure(2) # Plot walker position for all dimensions

            fig.set_size_inches(11.69,13.53)

            ndim = len(self.model['sed_params'])

            for i in range(0,ndim):

                ax = plt.subplot(ndim, 1, i+1)

                if np.size(self.model['walkers']['kept']) < 40:
                    ax.plot(np.arange(0,self.settings['MCMC']['nsteps']),np.transpose(self.mcmc_chain['full_samples'][self.model['walkers']['kept'],:,i])[:,:,0],'k-',alpha=0.1)
                else:
                    ax.plot(np.arange(0,self.settings['MCMC']['nsteps']),np.transpose(self.mcmc_chain['full_samples'][self.model['walkers']['kept'][0:40],:,i])[:,:,0],'k-',alpha=0.1)

                ax.set_ylabel(self.model['sed_nameunit_latex'][i])
                ax.set_xlim([0,self.settings['MCMC']['nsteps']])

                if i < ndim-1:
                    ax.set_xticks([])

            ax.set_xlabel("Step Number")



            # Build Name of Save File

            if not isinstance(self.settings['source_name'], type(None)): # if source name is defined save to own directory
                import os   # Make source-specific directory
                if not os.path.exists('{}/{}'.format(self.settings['plotting']['plotdir'],self.settings['source_name'])):
                    os.makedirs('{}/{}'.format(self.settings['plotting']['plotdir'],self.settings['source_name']))
                save_name = str(self.settings['source_name'])+'/'+self.settings['name']+'_'+str(self.settings['source_name'])+'_'+self.model['timing']['timestamp']+'_walkers'
            else: # if it is not defined, save it to the main directory
                save_name = self.settings['name']+'_'+self.model['timing']['timestamp']+'_walkers'


            # Save Figure

            if self.settings['plotting']['pdfWalkers']:
                plt.savefig(self.settings['plotting']['plotdir']+'/'+save_name+'.pdf', dpi=self.settings['plotting']['dpi'], bbox_inches='tight', pad_inches=0)
            else:
                plt.savefig(self.settings['plotting']['plotdir']+'/'+save_name+'.png', dpi=self.settings['plotting']['dpi'], bbox_inches='tight', pad_inches=0)

            plt.clf()
            plt.close(2)


        time1 = time.time() # stop time
        self.model['timing']['walker_time'] = time1-time0


        return



    def plot_corner(self):

        import time
        import corner
        import matplotlib.pyplot as plt

        # Serif font for papers
        plt.rc('font', family='serif')
        plt.rc('font', family='serif')
        plt.rc('mathtext',fontset='cm',rm='serif')
        plt.rcParams.update({'font.size': 8.7})

        time0 = time.time() # start time


        if self.settings['plotting']['plotCorner']:

            plt.figure(3)

            fig = corner.corner(self.mcmc_chain['samples'], labels=self.model['sed_names_latex'],
                #range=[[10, 30], [-5, -2],[1.2,2.1],[0,1000], [0,30],[20,35],[0.3,0.9]],\
                #truths=[T_d_true, tau_true, beta_true, EM_true,A_true, nu_mod_true, nu_width_true],\
                quantiles=[0.170675, 0.5, 0.829325], show_titles=True, quiet=True, labels_args={"fontsize": 40}) # Get 1 Sigma Percentiles

            fig.set_size_inches(11.69,13.53)
            plt.subplots_adjust(hspace=0.03, wspace=0.03)

            # Build Name of Save File

            if not isinstance(self.settings['source_name'], type(None)): # if source name is defined save to own directory
                import os   # Make source-specific directory
                if not os.path.exists('{}/{}'.format(self.settings['plotting']['plotdir'],self.settings['source_name'])):
                    os.makedirs('{}/{}'.format(self.settings['plotting']['plotdir'],self.settings['source_name']))
                save_name = str(self.settings['source_name'])+'/'+self.settings['name']+'_'+str(self.settings['source_name'])+'_'+self.model['timing']['timestamp']+'_corner'
            else: # if it is not defined, save it to the main directory
                save_name = self.settings['name']+'_'+self.model['timing']['timestamp']+'_corner'


            # Save Figure

            if self.settings['plotting']['pdfCorner']:
                plt.savefig(self.settings['plotting']['plotdir']+'/'+save_name+'.pdf', dpi=self.settings['plotting']['dpi'], bbox_inches='tight', pad_inches=0)
            else:
                plt.savefig(self.settings['plotting']['plotdir']+'/'+save_name+'.png', dpi=self.settings['plotting']['dpi'], bbox_inches='tight', pad_inches=0)

            plt.clf()
            plt.close(3)


        time1 = time.time() # stop time
        self.model['timing']['corner_time'] = time1-time0

        # Reset matplotlib params just in case

        plt.rcParams.update(plt.rcParamsDefault)
        plt.rc('font', family='serif')
        plt.rc('font', family='serif')
        plt.rc('mathtext',fontset='cm',rm='serif')

        return




    def postfit_info(self):
        '''
        Print post-fit information:
        '''

        if self.settings['verbose']:

            # Calculate Values

            STEP_TIME = self.model['timing']['mcmctime']/(self.settings['MCMC']['nwalkers']*self.settings['MCMC']['nsteps'])*1e6    # step time in microseconds
            COMPONENT_STRING = str() # initialise empty string
            for name, value, error in zip(self.model['sed_names'], self.model['sed_params'], self.model['sed_errors']):
                COMPONENT_STRING = COMPONENT_STRING + '|    {} = {:0.2f} {} {:0.2f} ({:0.1f}%)\n'.format(name, value, chr(177), error, 1e2*np.abs(error/value))


            print('************** POST-FIT INFORMATION *************\n')
            print('ACCEPTANCE = {0:.1f}%, MCMC_TIME = {1:.1f}s [{2:.0f} us/step]'.format(self.model['sed_acceptance']*1e2, self.model['timing']['mcmctime'], STEP_TIME))
            print('WALKERS_KEPT = {}/{} [{:.1f}%], RED_CHI_SQ = {:0.1f}'.format(len(self.model['walkers']['kept'][0]), self.settings['MCMC']['nwalkers'],
                self.model['walkers']['percent_kept'], self.model['sed_chi_squared']))
            print('FITTED PARAMETERS = \n{}'.format(COMPONENT_STRING))


        return



    def plot_info(self):
        '''
        Print plotting information
        '''

        if self.settings['verbose']:

            # Print Plotting Info

            import os

            print('\n************** PLOTTING INFORMATION *************\n')
            print('SED_PLOT_SAVED = {}, TIME_TAKEN = {:.0f}s'.format(str(self.settings['plotting']['plotSED']).upper(), self.model['timing']['sed_time']))
            print('WALKERS_PLOT_SAVED = {}, TIME_TAKEN = {:.0f}s'.format(str(self.settings['plotting']['plotWalkers']).upper(), self.model['timing']['walker_time']))
            print('CORNER_PLOT_SAVED = {}, TIME_TAKEN = {:.0f}s'.format(str(self.settings['plotting']['plotCorner']).upper(), self.model['timing']['corner_time']))
            print('Saved in {}\n'.format(self.settings['plotting']['plotdir']))

        return



    def return_params(self):
        '''
        Return key parameters
        '''

        return self.data, self.model, self.settings
