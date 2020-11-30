import os
import sys
import glob
import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os.path import expanduser

######### DIRKS ALPHA & CLEANING ########

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

pair_list = list(df['pair'].unique())
# Eliminate Subjects with invalid datasets (from subj_list and from df)
pairs_with_invalid_data = [200, 210, 213, 214, 299]
pair_list = [item for item in pair_list if item not in pairs_with_invalid_data]
df = df[np.logical_not(df["pair"].isin(pairs_with_invalid_data))]

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
df_alpha = pd.DataFrame(columns=df.columns)

# calculate alpha and ITI for all subs
for pair in pair_list:
    print(pair)
    pairwise_df = df[df.pair == pair]
    df_alpha_pair = calculate_alpha(pairwise_df)
    df_alpha = pd.concat([df_alpha, df_alpha_pair])
    #sort tapping-times according to their temporal order
    pairwise_df = pairwise_df.sort_values(by = ['trial', 'ttap'])


df_alpha.reset_index(inplace = True, drop = True)
df_alpha[df_alpha.pair ==203]
df_alpha.to_csv('df_alpha_temporal_ordewr.csv')
# save time of first and last tap per trial in dataframe
first_tap = df_alpha.index - df_alpha.index[df_alpha.index%18]
df_alpha["first_tap"] = df_alpha["ttap"][first_tap].to_numpy()
last_tap = df_alpha.index - df_alpha.index[(df_alpha.index%18)] +17
df_alpha["last_tap"] = df_alpha["ttap"][last_tap].to_numpy()

# select those alpha values that occur within the range of first tap + 1.5s and last tap - 1.5s (of each trial)
df_early = df_alpha[df_alpha["ttap"] <= df_alpha.first_tap+1.5 ]#["alpha_lin"]#.plot.hist(bins=bin_size)
df_late = df_alpha[df_alpha["ttap"] >= df_alpha.last_tap-1.5 ]#["alpha_lin"]#.plot.hist(bins=bin_size)
###TODO: Solve how to deal with NaNs for all tapnr.9 
df = df_alpha


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
