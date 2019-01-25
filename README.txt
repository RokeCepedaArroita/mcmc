STRUCTURE ***

The main script is mcmc.py, which is a function that uses all the tools in tools.py and the emission models in emission.py


3-STEP MCMC GUIDE ***

1. Copy the mcmc_config.py file from example_config to your separate working directory.
Then configure this dummy configuration file with your own preferences.

2. In your separate working folder, import the mcmc module into your script by using:

"import sys
sys.path.insert(0, mcmc_folder)
import mcmc, emission, tools"

where mcmc_folder is your path to the photometry code.

3. Query the program by using (example):

"mcmc_data, mcmc_model, mcmc_settings = mcmc.mcmc(nu, flux, flux_err, beam=0.00034421768435898063, excluded=[19, 100, 217, 4997])"
