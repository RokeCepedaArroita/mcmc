# MCMC Fitter for Spectral Energy Distribution (SED) Models

A Python-based tool for fitting Spectral Energy Distribution (SED) models using Monte Carlo Markov Chains (MCMC). This package uses `emcee` for sampling, includes built-in emission models, and provides utilities for data visualization.

---

## **Overview**

### Main Components:
1. **`mcmc.py`**: The main script to run the MCMC fitting.
2. **`tools.py`**: Contains all utility functions for analysis, plotting, and parameter handling.
3. **`emission.py`**: Houses models for different emission mechanisms such as synchrotron, anomalous microwave emission (AME), thermal dust, and more.

---

## **Dependencies**
This package requires the following Python libraries:
- `emcee`
- `healpy`
- `numpy`
- `datetime`
- `time`
- `sys`
- `inspect`
- `multiprocessing`
- `warnings`
- `lmfit`
- `matplotlib`
- `corner`
- `os`

Install these dependencies using `pip` or `conda`.

---

## **Getting Started**

### 3-Step MCMC Guide

1. **Set Up the Configuration File**:
   - Copy `mcmc_config.py` from the `example_config` directory to your working directory.
   - Modify this dummy configuration file according to your needs.

2. **Import the MCMC Module**:
   Add the path to the MCMC fitter and import it into your script:
   ```python
   import sys
   sys.path.insert(0, "path_to_mcmc_folder")
   import mcmc, emission, tools


3. **Run the MCMC Fitting**

   Use the following syntax to query the program:

   ```python
   mcmc_data, mcmc_model, mcmc_settings = mcmc.mcmc(
       nu,                     # List of frequencies (GHz)
       flux,                   # List of fluxes (Jy)
       flux_err,               # List of flux uncertainties (Jy)
       beam=0.00034421768435898063,  # Beam solid angle (sr)
       excluded=[19, 100, 217, 4997], # Frequencies to exclude (GHz)
       custom_settings=None,   # Optional: custom configuration dictionary
       source_information=None # Optional: additional source-specific metadata
   )
   ```

   - **`nu`**: List of frequencies (in GHz) for your observations.
   - **`flux`**: List of observed fluxes (in Jy) corresponding to the frequencies.
   - **`flux_err`**: List of flux uncertainties (in Jy).
   - **`beam`**: Beam solid angle in steradians, representing the primary aperture.
   - **`excluded`**: List of frequency indices to exclude from the fitting process.
   - **`custom_settings`**: Pass a custom configuration dictionary (overrides the default `mcmc_config.py` settings).
   - **`source_information`**: Pass source-specific metadata (optional).

   **Example Usage**:
   ```python
   mcmc_data, mcmc_model, mcmc_settings = mcmc.mcmc(
       nu=[1.4, 2.7, 4.85],
       flux=[100, 80, 60],
       flux_err=[10, 8, 6],
       beam=0.0001,
       excluded=[2],
       custom_settings=my_settings,
       source_information={'source_name': 'ExampleSource'}
   )
   ```

   The program will automatically:
   1. Validate your input.
   2. Initialize parameter guesses using least-squares fitting (if enabled).
   3. Run the MCMC process with progress updates.
   4. Save the results and plots to the specified directories.
   5. Return fitted data, the model, and settings for further analysis.

   Results will include:
   - Fitted parameter values with uncertainties.
   - Goodness-of-fit statistics (e.g., reduced χ²).
   - Generated figures (SED plot, corner plot, walker plot).


 ---

 ## **Configuration File (`mcmc_config.py`)**

 The configuration file is a Python dictionary with customizable parameters for MCMC settings, plotting, and source-specific options. Below are key sections:

 ### **Fit Settings**
 ```python
 settings = {
     'name': 'MCMC',
     'source_name': None,
     'MCMC': {
         'nwalkers': 230,
         'nsteps': 16000,
         'nburnin': 14000,
         'randomisation': 50,
         'stuck_threshold': 0.001,
     },
     'nthreads': 5,
     'least_sq_prefit': True,
     'components': {},  # Define your SED components here
     'priors': {},      # Define parameter priors
     'guesses': {},     # Initial parameter guesses
     'plotting': {
         'resultdir': '/path/to/results',
         'plotSED': True,
         'plotCorner': True,
         'plotWalkers': True,
         'dpi': 300,
     },
     'verbose': True,
     'formatting': {},  # Optional LaTeX formatting for parameters
     'units': {},       # Units of parameters
 }
 ```

 ---

 ## **Output Example**

 When running the program, the terminal output provides detailed information:

 ```
 ************** PRE-FIT INFORMATION **************
 NFREQ = 27, NEXCLUDED = 4, NFREEPARAMS = 7
 NWALKERS = 230, NSTEPS = 6000, NBURNIN = 4000
 NTHREADS = 5, PREFIT_USING_LEAST_SQ = TRUE
 COMPONENTS = FREEFREE(x1) AME(x1) THERMALDUST(x1)

 *************** LEAST-SQUARES INFO **************
 Successfully initialized guesses in 0.0 seconds!

 ************** POST-FIT INFORMATION *************
 ACCEPTANCE = 47.0%, MCMC_TIME = 46.6s [34 us/step]
 WALKERS_KEPT = 228/230 [99.1%], RED_CHI_SQ = 3.8
 FITTED PARAMETERS =
 |    EM = 48.20 ± 1.55 (3.2%)
 |    A_AME = 19.78 ± 0.32 (1.6%)
 |    nu_AME = 26.16 ± 0.29 (1.1%)
 |    W_AME = 0.52 ± 0.01 (2.5%)
 |    T_d = 20.36 ± 0.45 (2.2%)
 |    tau = -4.46 ± 0.02 (0.5%)
 |    beta = 1.47 ± 0.03 (2.0%)

 ************** PLOTTING INFORMATION *************
 SED_PLOT_SAVED = TRUE, TIME_TAKEN = 1s
 WALKERS_PLOT_SAVED = TRUE, TIME_TAKEN = 8s
 CORNER_PLOT_SAVED = TRUE, TIME_TAKEN = 8s
 Saved in /path/to/results

 ************** RESULTS SAVED! *************
 Saved files as MCMC_<source_name>_<timestamp> in /path/to/results
 Program finished with a runtime of 64s!
 ```

 ---

 ## **Generated Figures**

 Below are example figures generated by the program:

 1. **SED Fit**:
    ![SED Plot](example_results/MCMC_G160.26-18.62_2024Oct22_161840_SED.png)

 2. **Corner Plot**:
    ![Corner Plot](example_results/MCMC_G160.26-18.62_2024Oct22_161840_corner.png)

 3. **Walker Plot**:
    ![Walker Plot](example_results/MCMC_G160.26-18.62_2024Oct22_161840_walkers.png)

 ---

 ## **Emission Models**

 `emission.py` includes the following built-in models:
 - **Synchrotron emission**
 - **Anomalous Microwave Emission (AME)** (log-normal and SPDust templates)
 - **Thermal dust emission**
 - **CMB emission**
 - **Free-free emission**

 Custom emission models can be added as required.

 ---

 ## **Utility Functions**

 Located in `tools.py`, these functions handle:
 - Input validation (`check_input`)
 - Parameter extraction (`fetch_sed_parameters`)
 - Model construction (`build_model`)
 - Least-squares initialization (`ls_initialisation`)
 - MCMC fitting (`mcmc_fit`)
 - Results saving and plotting (`save_results`, `plot_sed`, `plot_corner`, `plot_walkers`)

 ---
