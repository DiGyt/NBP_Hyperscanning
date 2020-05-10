import os
import glob
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import matplotlib.pyplot as plt

# Step1: Load and Prepare the data
# create a list of all file names

# read in all files and bind them row-wise into one df
# copy from francas sheet!

# Create path to the folder "behavioral"
filepath = "/Users/anne/BehaviouralData"

# Create a list of path names that end with .csv
all_files = glob.glob(os.path.join(filepath, "*.csv"))

# Concatenate all files to obtain a single dataframe
df_from_each_file = (pd.read_csv(f) for f in all_files)
df = pd.concat(df_from_each_file, ignore_index=True)

# Compute real tapping-times (substract first 3s from all time points)
df['ttap3'] = df['ttap'] - 3.0


#compute real tapping-times (substract first 3s from all time points)
subj_list = list(df['pair'].unique())
new_df = pd.DataFrame()

for pair in subj_list:
# n = len(df[df['pair'] == pair]['ttap3'])/2
    #pair = 203
    # 1. Create one df with only this pair
    df_pair = df[df['pair'] == pair]
    df_pair = df_pair.reset_index()
    #sub1 = list(df_pair[df_pair['subject']== 1]['ttap3'])
    #sub2 = list(df_pair[df_pair['subject']== 2]['ttap3'])
    #list(df_pair[df_pair['subject']== 1].index)

    # 2. Separate df: one with sub1 and one with sub2 data
    # (delete the partner's taps, while containing all trial/ block/ etc. information)
    df2 = df_pair.drop(list(df_pair[df_pair['subject']== 2].index), axis=0)
    sub2_df = df_pair.drop(list(df_pair[df_pair['subject']== 1].index), axis=0)

    # 3. Combine both to one
    # (sub1 and sub2 in separat columns not separate rows, easier to process)
    df2['ttap3_sub2'] = list(sub2_df['ttap3'])
    df2['subject2'] = list(sub2_df['subject'])
    len(df2)

    # Calculate the distance between the own taps of sub1 and sub2 (individual tapping frequency)
    df2['Delta'] = abs(df2['ttap3'].sub(df2['ttap3_sub2'], axis = 0))
    #df2[:20]
    #df_pair[:20]
    '''
    I decided not to exclude asynchronous trials from the data, since I was not convinced
    why we did it the last time: Our reason to drop asynchronous trials was forumalated as follows:
    "the trials in which the overall order of taps was not consecutive have to be exlcuded, i.e.
    all trials where a tap i+1 of one participant occurred before-/or at the time of tap i of the other participant.
    In other words, when one of them skipped ahead by tapping twice, causing the other to lag behind by one tap.
    > We justified this by saying that when computing the alpha-synchronization,
    the nominator (delta) should be always smaller than the denominator (ITI of reference subject)

    > However, why should this be necessary? asynchronous trials like this onyl reflect
    maximal asynchrony, so they should also be included in our data. Otherwise,
    we are "artificially" improving pairs how try to synchronize but have a really bad performance
    (one of them constantly skipping ahead by tapping twice, causing the other to lag behind by one tap)
    '''

    # Loop through trials and Calculate ITI for all taps
    trials = df2['trial'].unique()
    len(trials)
    #df2[df2['trial'] == 1]
    all_ITIsub1 = []
    all_ITIsub2 = []
    all_alpha = []
    all_alpha_lin = []

    # Compute ITI of all sub1
    for trial in range(1, len(trials)+1):
        print(trial)
        tmp_df = df2[df2['trial'] == trial]
        tmp_df = tmp_df.reset_index()

        ITIsub1 = []
        ITIsub2 = []
        alpha = []
        alpha_lin = []


        for tap in range(8):
            ITIsub1.append(tmp_df['ttap3'][tap+1] - tmp_df['ttap3'][tap])
            ITIsub2.append(tmp_df['ttap3_sub2'][tap+1] - tmp_df['ttap3_sub2'][tap])

        #for tap in range(8):
        # alternate which subject is reference subject and which is follower subject in the circular measure
            if trial%2 > 0:
                ref_sub = ITIsub1
            else:
                ref_sub = ITIsub2
            numerator = tmp_df['Delta'][tap]
            denominator = ref_sub[tap] # sub1 as reference subject
            idx = abs(numerator/ denominator * 360)
            idx_lin = abs((180 - abs(idx - 180)))
            alpha.append(idx)
            alpha_lin.append(idx_lin)


        ITIsub1.append(None)
        ITIsub2.append(None)
        alpha.append(None)
        alpha_lin.append(None)

        all_alpha.append(alpha)
        all_alpha_lin.append(alpha_lin)

        all_ITIsub1.append(ITIsub1)
        all_ITIsub2.append(ITIsub2)


    # Add ITI_sub1 to data frame
    all_ITIsub1 = [item for elem in all_ITIsub1 for item in elem]
    all_ITIsub2 = [item for elem in all_ITIsub2 for item in elem]

    all_alpha = [item for elem in all_alpha for item in elem]
    all_alpha_lin = [item for elem in all_alpha_lin for item in elem]


    df2['ITI_sub1'] = all_ITIsub1
    df2['ITI_sub2'] = all_ITIsub2
    df2['alpha'] = all_alpha
    df2['alpha_lin'] = all_alpha_lin


    df2[:30]
    new_df = new_df.append(df2)
    new_df[:50]
