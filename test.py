from config_mcmc import *


mcmc_folder = '/scratch/nas_falcon/scratch/rca/projects/mcmc'

import sys
sys.path.insert(0, mcmc_folder)
import mcmc, emission, tools


nu = [4.080e-01, 1.420e+00, 1.100e+01, 1.300e+01, 1.700e+01, 1.900e+01, 2.280e+01,
     3.300e+01, 4.070e+01, 6.070e+01, 9.360e+01, 2.840e+01, 4.400e+01, 7.000e+01,
     1.000e+02, 1.430e+02, 2.170e+02, 3.530e+02, 5.450e+02, 8.570e+02, 1.249e+03,
     2.141e+03, 2.998e+03, 4.997e+03,]

flux = [9.38501026e+01, 4.49797574e+01, 4.03517106e+01, 4.24453019e+01,
     4.33246172e+01, 3.22389220e+01, 5.51491588e+01, 4.91534462e+01,
     4.48830771e+01, 4.73572237e+01, 9.34086787e+01, 5.00488221e+01,
     4.37560812e+01, 5.45675939e+01, 1.53656570e+02, 2.95910047e+02,
     1.36044568e+03, 5.69547226e+03, 1.77809914e+04, 5.06190193e+04,
     9.44706870e+04, 1.28425274e+05, 6.21732061e+04, 2.30559468e+04]

flux_err = [3.86953886e+01, 1.81319199e+01, 1.21055141e+00, 1.27335983e+00,
     7.79843120e+00, 9.02689817e+00, 5.51494157e-01, 4.91536321e-01,
     4.48830909e-01, 4.73575937e-01, 9.34091129e-01, 5.00488857e-01,
     4.37560958e-01, 5.45675943e-01, 1.53657895e+00, 2.95911039e+00,
     1.36044569e+01, 7.40411419e+01, 2.31152985e+02, 7.08666664e+02,
     1.27535820e+04, 1.36130925e+04, 7.21212506e+03, 2.30560055e+03]

mcmc_data, mcmc_model, mcmc_settings = mcmc.mcmc(nu, flux, flux_err, beam=0.00034421768435898063, excluded=[19, 100, 217, 4997])
