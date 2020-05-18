import os
import sys
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# add functions script file path to sys path
#conf_path = os.getcwd()
#sys.path.append(conf_path)
#sys.path.append(conf_path + '/data_analysis')

#from Behavioural_Analysis.behavioural_analysis_functions import (get_alpha, clean_data)

# !!!! eliminate subs 200, 210, 213, 214, 299
#%matplotlib qt

#for p in sys.path:
    #print(p)


# Load and Prepare the data
# create a list of all file names
# Create path to the folder "behavioral"
filepath = "/Users/anne/BehaviouralData"

# Create a list of path names that end with .csv
all_files = glob.glob(os.path.join(filepath, "*.csv"))

# Concatenate all files to obtain a single dataframe
df_from_each_file = (pd.read_csv(f) for f in all_files)
df = pd.concat(df_from_each_file, ignore_index=True)
# Compute real tapping-times (substract first 3s from all time points)
df['ttap3'] = df['ttap'] - 3.0
subj_list = list(df['pair'].unique())
# Compute alpha synchronization measure, individual intertap-Interval (ITI) and tapping distanca (Delta)
alpha_df = get_alpha(df, subj_list)


alpha_df[alpha_df.pair == 206][:50]
# Delete all rows with "None" (all tap #9)
alpha_df = alpha_df.dropna()
# Plot mean alpha synchrinization per tap (of all trials) for all pairs
# Shows weard outliers!! --> discard in cleaning step

alpha_mean_before = alpha_df.groupby(['pair', 'tapnr'], as_index=False)['alpha_lin'].mean()
#alpha_mean.plot(kind='line',x='tapnr',y='alpha_lin', title='Alpha-average before Cleaning')
fig, ax = plt.subplots(figsize=(8,4))
for idx, gp in alpha_mean_before.groupby('pair'):
    gp.plot(x='tapnr', y='alpha_lin', ax=ax, label=idx,title='Alpha-average before Cleaning')
plt.show()

#new_df.set_index('index', inplace=True)

# Clean the data:
# Discard trials associated with extreme syn- chronization values
# i.e. when the average of the eight synchrony values was higher or lower than
# 2 s.d. from the participant’s mean synchrony (see Novembre 2012)

df_cleaned = clean_data(alpha_df)

# Plot mean alpha synchrinization per tap (of all trials) for all pairs after cleaning (outliers removed)
alpha_mean_after = df_cleaned.groupby(['pair', 'tapnr'], as_index=False)['alpha_lin'].mean()

fig, ax = plt.subplots(figsize=(8,4))
for idx, gp in alpha_mean_after.groupby('pair'):
    gp.plot(x='tapnr', y='alpha_lin', ax=ax, label=idx,title='Alpha-average after Cleaning')
    ax.set_ylim(0,60)
plt.show()
