import os
import sys
import glob
import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# add functions script file path to sys path
sys.path.append(os.getcwd() + '/data_analysis')
from Behavioural_Analysis.behavioural_analysis_functions import (get_alpha, clean_data)

# Set defaults
data_path = "/Users/anne/BehaviouralData"
plots_path = './plots/'

# make folder for plots
os.makedirs(os.path.dirname(plots_path), exist_ok=True)

#interactive plots
#%matplotlib qt

# 1. Load and Prepare the data
# Create a list of path names that end with .csv
all_files = glob.glob(os.path.join(data_path, "*.csv"))

# 1.1 Concatenate all files to obtain a single dataframe
df_from_each_file = (pd.read_csv(f) for f in all_files)
behvaioural_df = pd.concat(df_from_each_file, ignore_index=True)

# 1.2 Prepare data-frame for furtcher processing
# Compute real tapping-times (substract first 3s from all time points)
behvaioural_df['ttap3'] = behvaioural_df['ttap'] - 3.0
subj_list = list(behvaioural_df['pair'].unique())
# Eliminate Subjects with invalid datasets
pairs_with_invalid_data = [200, 210, 213, 214, 299]
subj_list = [item for item in subj_list if item not in pairs_with_invalid_data]

# 2. Compute alpha synchronization measure, individual intertap-Interval (ITI) and tapping distance (Delta)
behvaioural_df_alpha = get_alpha(behvaioural_df, subj_list)
behvaioural_df_alpha.groupby(['pair']).Delta.describe()

# 2.1 Delete all rows with "None" (all tap #9)
behvaioural_df_alpha = behvaioural_df_alpha.dropna()
behvaioural_df_alpha.describe()
behvaioural_df_alpha[(behvaioural_df_alpha['Delta']>5)&(behvaioural_df_alpha['alpha_lin']<180)]

# 3. Clean the data:
# Discard trials associated with extreme syn- chronization values
# i.e. when the average of the eight synchrony values was higher or lower than
# 2 s.d. from the participant’s mean synchrony (see Novembre 2012)
behvaioural_df_alpha_cleaned = clean_data(behvaioural_df_alpha)

## OR: Eliminate all taps where alpha_lin is bigger than 180
# TODO: remove whole trial where one alpha_lin > 180
behvaioural_df_alpha_cleaned = behvaioural_df_alpha[behvaioural_df_alpha.alpha_lin<=180]
eliminated_data = 1- len(behvaioural_df_alpha_cleaned)/len(behvaioural_df_alpha)


### 4. PLOTTING ###

### 4.1. Mean alpha synchrinization per tap (of all trials) for all pairs
# tapwise Alpha-Average Before Cleaning ###
alpha_mean_before = behvaioural_df_alpha.groupby(['pair', 'tapnr'], as_index=False)['alpha_lin'].mean()
# tapwise Alpha-Average After cleaning
alpha_mean_after = behvaioural_df_alpha_cleaned.groupby(['pair', 'tapnr'], as_index=False)['alpha_lin'].mean()


plot_df = alpha_mean_before
plot_df = alpha_df
# Plot alpha-synchronization of the whole experiment, all pairs_with_invalid_data
fig, ax = plt.subplots(figsize=(8,4))
for idx, gp in plot_df.groupby('pair'):
    gp.plot.line(x='tapnr', y='alpha_lin', ax=ax, label=idx,title='Alpha-average before Cleaning', lw=0.5)
plt.show()


# 4.2 Plot parts of the data
plot_df = behvaioural_df_alpha_cleaned.reset_index()
# differet cleaning style: eliminate all trials with alpha > 180
# select some pairs
plot_pairs = [208, 203]#,203,206,208]
plot_df = plot_df[plot_df['pair'].isin(plot_pairs)]
# limit number of trials
num_trials= 100
plot_trials = list(np.arange(200,300))
#yticks = [20,40,60,80,100,120,140,160,180]
plot_df = plot_df[plot_df['trial'].isin(plot_trials)]
sns.set(context = 'paper', style = 'whitegrid')
_, ax = plt.subplots(figsize=(8,4))
for idx, gp in plot_df.groupby('pair'):
    gp.reset_index(inplace=True)
    gp.plot.line(y='alpha_lin', ax=ax, ylim = [0,120],label=idx,title='Alpha-values of first {} trials'.format(num_trials))
    ax.set_xlabel("tap number")
    ax.set_ylabel("Aplha (linearized)")
#plt.show()
plt.savefig(plots_path+'Alpha_lin_Last{}'.format(plot_pairs), dpi = 600)

num_trials= 100
plot_trials = list(np.arange(num_trials))
#yticks = [20,40,60,80,100,120,140,160,180]
plot_df = plot_df[plot_df['trial'].isin(plot_trials)]
_, ax = plt.subplots(figsize=(8,4))
for idx, gp in plot_df.groupby('pair'):
    gp.reset_index(inplace=True)
    gp.plot.line(y='alpha_lin', ax=ax, ylim = [0,120],label=idx,title='Alpha-values of first {} trials'.format(num_trials), lw=0.8)
    ax.set_xlabel("tap number")
    ax.set_ylabel("Aplha (linearized)")
plt.show()


fig, axs = plt.subplots(4, 1, sharex=True, sharey=True, figsize=(15,10))
'''
# add big shared axes, hide frame
fig.add_subplot(111, frameon=False)
plt.tick_params(labelcolor='none', top=False, bottom=False, left=False, right=False)
plt.xlabel('tap number')
plt.ylabel('Aplha (linearized)')
plt.title('Alpha-values of first {} trials'.format(num_trials), fontsize = 15)

for gp in plot_df.groupby('pair'):
    axs[idx].plot.line(y='alpha_lin', ax=ax, ylim = [0,120], lw=0.8)
plt.show()


# Plot each graph
axs[0].plot(t, s1)
axs[1].plot(t, s2)
axs[2].plot(t, s3)
axs[3].plot(t, s4)

fig, ax = plt.subplots(figsize=(8,4))
for idx, gp in alpha_mean_after.groupby('pair'):
    gp.plot(x='tapnr', y='alpha_lin', ax=ax, label=idx,title='Alpha-average after Cleaning')
    ax.set_ylim(0,60)
plt.show()

'''
