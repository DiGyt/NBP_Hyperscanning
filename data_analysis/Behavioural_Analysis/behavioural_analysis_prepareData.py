import os
import sys
import glob
import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os.path import expanduser

######### APPLY DIRKS ALPHA & CLEANING ########

# Set defaults
data_path = "/Users/anne/github/NBP_Hyperscanning/data_analysis/Behavioural_Analysis/BehaviouralData"
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
df = pd.concat(df_from_each_file, ignore_index=True)

# create a list with all pairs
pair_list = list(df['pair'].unique())

# Eliminate Subjects with invalid datasets (from subj_list and from df)
pairs_with_invalid_data = [200, 210, 213, 214, 299]
pair_list = [item for item in pair_list if item not in pairs_with_invalid_data]
df = df[np.logical_not(df["pair"].isin(pairs_with_invalid_data))]

#eliminate not needed columns for a better overview
df.drop(['condition','player_start_first', 'jitter'], axis = 1, inplace = True)# Function to calculate alph from both subject's perspectives
'''
#TEST SORTING ALGORITHM
df_sorted = df[df.pair == 203].sort_values(by = ['trial', 'ttap'])
df_sorted[17:36]
df[df.pair == 203][17:36]
'''

def calculate_alpha(df):
    """
    Calculates the circular tapping synchrony measure as defined in Novembre et al. (2017).
    """

    # calculate the inter-person difference P(x) T(n) - P(y) T(n)
    # from both subjects' perspectives
    df = df.sort_values(['trial', 'tapnr'])
    df['ITI_inter'] = df['ttap'].diff()
    df.iloc[::2, df.columns.get_loc('ITI_inter')] = df['ttap'].diff(-1)

    # calculate the intra-person difference P(x) T(n + 1) - P(x) T(n)
    df['ITI_intra'] = abs(df.groupby(['subject', 'trial'])['ttap'].diff(-1))  # .fillna(0)

    # calculate alpha and linearized alpha for all taps
    df['alpha'] = abs(df['ITI_inter'] / df['ITI_intra']) * 360
    df['alpha_lin'] = abs(180 - abs(df['alpha'] - 180))
    # TODO: discuss the linearization/ asynchronous trials. I found that there are single taps where the circular measure is larger than 360°
    # This means theoretically that the interperson diff is way bigger than the intra person diff, meaning that P1 made
    # the next tap already while P2 "misses" out one tap. By doing % 360, i define that these asynchronous trials are valid
    # and people can be synchronous, even if one tap was missed out by a person.
    # We could also instead remove these trials by removing the `% 360`, and cropping all df["alpha"] > 360 afterwards.

    return df

# Create a new df with all synchronization measures (i.e. alpha & inter-/intra tap distances)
df_alpha = pd.DataFrame(columns=df.columns)

# Calculate alpha and ITI for all subs
for pair in pair_list:
    pairwise_df = df[df.pair == pair]
    df_alpha_pair = calculate_alpha(pairwise_df)
    df_alpha = pd.concat([df_alpha, df_alpha_pair])
    #sort tapping-times according to their temporal order
    pairwise_df = pairwise_df.sort_values(by = ['trial', 'ttap'])
df_alpha.reset_index(inplace = True, drop = True)

# Save time of first and last tap per trial in dataframe
first_tap = df_alpha.index - df_alpha.index[df_alpha.index%18]
df_alpha["first_tap"] = df_alpha["ttap"][first_tap].to_numpy()
last_tap = df_alpha.index - df_alpha.index[(df_alpha.index%18)] +17
df_alpha["last_tap"] = df_alpha["ttap"][last_tap].to_numpy()

# CLEAN DATA:
# Now, we should select the alpha-values according to the rule of Novembre et. al,
# i.e.  odd trials: alpha from sub1 perspective
#       even trials: alpha from sub2 perspective
df_alpha = df_alpha[df_alpha["trial"]%2 != df_alpha["subject"] - 1]

# FOR LATER PLOTS
bin_size = int(np.ceil(np.sqrt(len(df_alpha[df_alpha["alpha"] <= 360]["alpha_lin"]))))
#######

# Remove all trials where one person tapped twice before the other person did
lost_taps = df_alpha[df_alpha["alpha"] > 360][["pair","trial"]]
lost_taps = lost_taps.drop_duplicates(subset=['pair','trial'])

for pair in pair_list:
    lost_taps_tmp = lost_taps[lost_taps["pair"]==pair]["trial"]
    lost_taps_tmp.to_csv('{}_lost_taps.csv'.format(pair))

print("percentage of lost trials after removing double taps:", round(len(lost_taps)/len(df_alpha)*100,2), "%")
df_alpha = df_alpha[df_alpha["alpha"] <= 360]
df_alpha['double_taps'] = df_alpha["alpha"] > 360
df_alpha[:20]


df_alpha.to_csv('cleaned_data.csv')

# Split data into early/late segments
# Select those alpha values that occur within the range of first tap + 1.5s and last tap - 1.5s (of each trial)
df_early = df_alpha[df_alpha["ttap"] <= df_alpha.first_tap+1.5 ][["pair","trial","alpha_lin","double_taps"]]#["alpha_lin"]#.plot.hist(bins=bin_size)
df_early.reset_index(inplace = True, drop = True)
df_late = df_alpha[df_alpha["ttap"] >= df_alpha.last_tap-1.5 ][["pair","trial","alpha_lin","double_taps"]]
df_late.reset_index(inplace = True, drop = True)

#["alpha_lin"]#.plot.hist(bins=bin_size)

# create (early/late) df with alpha-average per trial which can then be correlated with EEG early/late epochs
mean_alpha_early = df_early.groupby(['pair','trial']).alpha_lin.mean().reset_index()
mean_alpha_late = df_late.groupby(['pair','trial']).alpha_lin.mean().reset_index()
# merge both dataframes into one
mean_alpha = mean_alpha_early.merge(mean_alpha_late, on=["pair","trial"],suffixes=("_early","_late"))
mean_alpha[:50]


# save all as csv
df_alpha.to_csv('df_alpha_temporal_order.csv')
df_early.to_csv('alpha_early.csv')
df_late.to_csv('alpha_late.csv')
mean_alpha.to_csv('mean_alpha.csv')

############ PLOTS ####################
from scipy import stats
# get the distribution of valid alphas

df_alpha["alpha_lin"].plot.hist(bins=bin_size)
plt.xlabel('Alpha (linearised) [degrees]')
plt.ylabel('Occurance')
plt.title('All valid alphas (alpha<360°)')
# create fig object
alpha_all = plt.gcf()
# save fig object
#pickle.dump(alpha_all, open(behav_plots + "alpha_all.p", 'wb'))

mean = np.around(np.mean(df_alpha["alpha_lin"]),decimals=2)
median = np.around(np.median(df_alpha["alpha_lin"]),decimals=2)
mode,xyz3 = stats.mode(np.around(df_alpha["alpha_lin"], decimals=3))

names = ["mode", "median", "mean"]
colors = ['red', 'blue', 'green']
measurements = [mode, median, mean]


for measurement, name, color in zip(measurements, names, colors):
    plt.vlines(x=measurement,ymin=0,ymax=1050, linestyle='--', linewidth=2.5,
                label='{0} at {1}'.format(name, measurement), colors=color)
plt.legend();
df_early["alpha_lin"].plot.hist(bins=bin_size)
df_late["alpha_lin"].plot.hist(bins=bin_size)

plt.suptitle('Early vs. late taps')
plt.legend(['First 1.5s','Last 1.5s'])
plt.xlabel('Alpha (linearised) [degrees]')
plt.ylabel('Occurance')

######### REMOVE OUTLIERS (not recommended due to huge lost of data) #######

def remove_outliers(df, exclude_stddev):
    """Remove all trials where the average alpha is `exclude_sttdev` sttdevs larger or
    smaller than the mean."""

    # calculate the mean alpha for each trial
    means = df.groupby(['trial'])["alpha"].mean()

    # define the upper and lower bounds, based on the mean and stddev of these means
    lower_bound = means.mean() - exclude_stddev * means.std()
    upper_bound = means.mean() + exclude_stddev * means.std()

    # filter the means so only the trials within the defined bounds remain
    good_trials = means[(lower_bound < means) & (means < upper_bound)]

    # return the df filtered for only the good trials
    return df[df["trial"].isin(good_trials.index)]


df_clean = remove_outliers(df, 1)
print("Percentage of lost data after removing outliers:",1-len(df_clean)/len(df))














######### MY ALPHA ########
path = os.getcwd() + '/data_analysis/Behavioural_Analysis'
# add functions script file path to sys path
sys.path.append(path)
from behavioural_analysis_functions import (get_alpha, clean_data)#, eliminate_ghost_triggers)
from functions_preprocessing_mne20 import \
    (split_raws, mark_bads, save_bads, run_ica, save_ica)

#%matplotlib qt

### Behavioural PART ####
# Load Behavioural Data (all pairs in one df with alpha values)
df = pd.read_csv("Behvaioural_Analysis_Data/Behavioural_Data_Alpha.csv", index_col=0)
# 2.1 Delete all rows with "None" (all tap #9)
#behvaioural_df_alpha = behvaioural_df_alpha.dropna()
df[df.pair==203]

def remove_outliers(df, exclude_stddev):
    """Remove all trials where the average alpha is `exclude_sttdev` sttdevs larger or
    smaller than the mean."""

    # calculate the mean alpha for each trial
    means = df.groupby(['trial'])["alpha"].mean()

    # define the upper and lower bounds, based on the mean and stddev of these means
    lower_bound = means.mean() - exclude_stddev * means.std()
    upper_bound = means.mean() + exclude_stddev * means.std()

    # filter the means so only the trials within the defined bounds remain
    good_trials = means[(lower_bound < means) & (means < upper_bound)]

    # return the df filtered for only the good trials
    return df[df["trial"].isin(good_trials.index)]


df_tmp = remove_outliers(df, 1)
amount_lost_data= (len(df)-len(df_tmp))/len(df_tmp)

df
