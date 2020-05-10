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

##### Later loop through all pairs!!! #####
#for pair in subj_list:
pair = 202
# n = len(df[df['pair'] == pair]['ttap3'])/2

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
len(df2)xc

# Store rejected trials to count them later
rejectedTrials1 = []
rejectedTrials2 = []

# 1. Exclude the asynchronous trials from the data:
# the trials in which the overall order of taps was not consecutive,
# i.e. when tap i+1 of one participant occurred before-/or at the time of tap i of the other participant.
# In other words, when one of them skipped ahead by tapping twice,
# causing the other to lag behind by one tap.

# Calculate the distance between all taps of sub1 and sub2
df2['Delta'] = abs(df2['ttap3'].sub(df2['ttap3_sub2'], axis = 0))

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

# Loop through trials and Calculate Alpha for all taps
