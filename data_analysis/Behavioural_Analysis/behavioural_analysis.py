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

#compute real tapping-times (substract first 3s from all time points)
df['ttap3'] = df['ttap'] - 3.0


#compute real tapping-times (substract first 3s from all time points)
subj_list = list(df['pair'].unique())
df['ttap']

##### Later loop through all pairs!!! #####
#for pair in subj_list:
pair = 202
# n = len(df[df['pair'] == pair]['ttap3'])/2

# 1. Create one df with only this pair
df_pair = df[df['pair'] == pair]
#sub1 = list(df_pair[df_pair['subject']== 1]['ttap3'])
#sub2 = list(df_pair[df_pair['subject']== 2]['ttap3'])
#list(df_pair[df_pair['subject']== 1].index)

# 2. Separate df: one with sub1 and one with sub2 data
# (delete the partner's taps, while containing all trial/ block/ etc. information)
sub_df = df_pair.drop(list(df_pair[df_pair['subject']== 2].index), axis=0)
sub2_df = df_pair.drop(list(df_pair[df_pair['subject']== 1].index), axis=0)

# 3. Combine both to one
# (sub1 and sub2 in separat columns not separate rows, easier to process)
sub_df['ttap3_sub2'] = list(sub2_df['ttap3'])
sub_df['subject2'] = list(sub2_df['subject'])
len(sub_df)

# Store rejected trials to count them later
rejectedTrials1 = []
rejectedTrials2 = []

#loop through whole data set to check for synchrony (direction 1)
for i in range(len(df[df['pair'] == pair]['ttap3'])):
    i = 1
    min = abs(sub1[i] - sub2[i])
    rightTap = abs(sub1[i] - sub2[i+1])
    leftTap = abs(sub1[i] - sub2[i-1])
    next1 = rightTap < min
    next2 = leftTap < min

    if next1 or next2:
        rejectedTrials[count1] =


'''
for i in range(len(sub1)):
    i = 1
    min = abs(sub1[i] - sub2[i])
    rightTap = abs(sub1[i] - sub2[i+1])
    leftTap = abs(sub1[i] - sub2[i-1])
    next1 = rightTap < min
    next2 = leftTap < min

    if next1 or next2:
        rejectedTrials[count1] =

'''

def synchronize_data():
