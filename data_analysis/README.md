# Data Analysis
This part of the repository was mainly concerned with data analysis.

The purpose of each file is explained in its header.

Since there were multiple approaches and drawbacks, there are many files
seemingly fullfilling the same purpose. This is due to many switches in 
implementation: For example `main_preprocessing.py` implements manual 
preprocessing as a python function, aimed to work when run from a local 
python install. `main_preprocesssing.ipynb` implements manual remote 
preprocessing, working as a jupyter notebook which can be run through 
the browser, while using the IKW computers for calculations. 
`main_preprocessing_auto.ipynb` (which was used for the final analysis) 
implements remote preprocessing, but only manually marking ICA components,
while data cleaning is performed by autoreject.

The files used for the final analysis are:
- All the `functions_` files, providing functions to work with.
- `main_preprocessing_auto.ipynb` to preprocess the data and annotate 
bad channels, segments, and ICs.
- `main_phases.py`, to apply the preprocessing and calculate the phase vectors.
- `main_ispc.py` to calculate the ISPCs from the phase vectors.
- `main_swi.py` to calculate the Small World Index from the ISPCs.

Statistics and visualisation were performed in `main_statistics.ipynb` and
the `plot_` files.