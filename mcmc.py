''' mcmc.py:
Performs SED fit using MCMC methods
and saves all results/plots into files.
Settings are set in your mcmc_config.py file
(see example_config folder for a dummy config file).

Example usage:
mcmc_data, mcmc_model, mcmc_settings = mcmc.mcmc(nu, flux, flux_err, beam=0.00034421768435898063, excluded=[100, 217, 4997])

Version 1.01 [Jan 2019]
Roke Cepeda-Arroita
roke.cepeda-arroita@manchester.ac.uk
'''


# TODO (minor): it would be handy to save all the fit parameters to a csv file (fit + errors) with pandas so that these can be copied into a report
# TODO (major): fix the least-squares pre-initialisation so that MCMC convergence does not depend on initial guesses as much

def mcmc(nu, flux, flux_err, beam, excluded):


    from config_mcmc import settings
    from tools import SED
    import numpy as np


    # Data Dictionary Initialisation

    data = {'nu': [],               # frequencies in GHz
    		'flux': [],             # fluxes in Jy
    		'flux_err': [],         # flux uncertainties in Jy
    		'beam': [],             # beam size in sr
            'excluded': [],         # list of frequencies in GHz plotted but not fitted
            'nu_fitted': [],        # non excluded frequencies in GHz
            'flux_fitted': [],      # non-excluded fluxes in Jy
            'flux_err_fitted': []   # non-excluded flux errors in Jy
            }


    # Replace Values with Input

    data['nu'] = np.array(nu)
    data['flux'] = np.array(flux)
    data['flux_err'] = np.array(flux_err)
    data['beam'] = np.array(beam)
    data['excluded'] = np.array(excluded)



    # Run MCMC

    '''
    The actual program starts below
    '''


    # Initialise Object

    my_sed = SED(data, settings)


    # Initialise SED Parameters in self.model

    my_sed.fetch_sed_parameters()


    # Print Pre-Fit Information

    my_sed.prefit_info()


    # Build SED Model

    my_sed.build_model()


    # Perform MCMC Fit

    my_sed.mcmc_fit()


    # Print Results

    my_sed.postfit_info()


    # Plot Results

    my_sed.plot_walkers()
    my_sed.plot_sed()
    my_sed.plot_corner()


    # Plot Info

    my_sed.plot_info()


    # Save Results

    my_sed.save_results()


    # Return parameters

    mcmc_data, mcmc_model, mcmc_settings = my_sed.return_params()


    return mcmc_data, mcmc_model, mcmc_settings
