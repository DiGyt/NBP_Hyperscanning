# functions_behavioral.py
#
# A collection of functions used to compute our behavioral measures
#

import numpy as np
import pandas as pd
import mne

EVENT_DICT = {'s1/t1':6, 's1/t2':7, 's1/t3':8, 's1/t4':9, 's1/t5':10, 's1/t6':11, 's1/t7':12, 's1/t8':13, 's1/t9':14,
              's2/t1':15, 's2/t2':16, 's2/t3':17, 's2/t4':18, 's2/t5':19, 's2/t6':20, 's2/t7':21, 's2/t8':22, 's2/t9':23}

INV_EVENT_DICT = {str(val): key for key, val in EVENT_DICT.items()}

### Calculate behavioral measures

def calculate_alpha(df):
    """
    Calculates the circular tapping synchrony measure as defined in Novembre et al. (2017).
    Input should be a behavioral dataframe containing trial information.
    """

    # calculate the inter-person difference P(x) T(n) - P(y) T(n)
    # from both subjects' perspectives
    df = df.sort_values(['trial', 'tapnr'])
    df['diff_inter'] = df['ttap'].diff()
    df.iloc[::2, df.columns.get_loc('diff_inter')] = df['ttap'].diff(-1)

    # calculate the intra-person difference P(x) T(n + 1) - P(x) T(n)
    df['diff_intra'] = abs(df.groupby(['subject', 'trial'])['ttap'].diff(-1))  # .fillna(0)

    # calculate alpha and linearized alpha for all taps
    df['alpha'] = abs(df['diff_inter'] / df['diff_intra']) * 360
    df['alpha_lin'] = abs(180 - abs(df['alpha'] - 180)) # abs(180 - abs(df['alpha'] % 360 - 180))
    # TODO: discuss the linearization/ asynchronous trials. I found that there are single taps where the circular measure
    # is larger than 360°
    # This means theoretically that the interperson diff is way bigger than the intra person diff, meaning that P1 made
    # the next tap already while P2 "misses" out one tap. By doing % 360, i define that these asynchronous trials are valid
    # and people can be synchronous, even if one tap was missed out by a person.
    # We could also instead remove these trials by removing the `% 360`, and cropping all df["alpha"] > 360 afterwards.
    
    return df


def remove_outliers(df, exclude_stddev=2):
    """
    Remove all trials where the average alpha is `exclude_sttdev` sttdevs larger or
    smaller than the mean.
    """
    
    # calculate the mean alpha for each trial
    means = df.groupby(['trial'])["alpha"].mean()
    
    # define the upper and lower bounds, based on the mean and stddev of these means
    lower_bound = means.mean() - exclude_stddev * means.std()
    upper_bound = means.mean() + exclude_stddev * means.std()
    
    # filter the means so only the trials within the defined bounds remain
    good_trials = means[(lower_bound < means) & (means < upper_bound)]
    
    # return the df filtered for only the good trials
    return df[df["trial"].isin(good_trials.index)]


### Preprocess events

def create_event_df(raw):
    """Reads events, assigns them event names and creates an event dataframe."""
    
    events = mne.find_events(raw, shortest_event=1)

    # create a pandas DataFrame to make working with events easier
    df_events = pd.DataFrame(events[:, (0, 2)])
    df_events.columns = ('sample','event_code')
    df_events['event_index'] = range(len(df_events))
    
    # add the trial number to later match the df with the behavioral data
    df_events['event_trial'] = 0
    
    # each time we see the "trial start" trigger, we increase the trial number
    for idx, row in df_events.iterrows():
        if row['event_code'] == 48:
            df_events['event_trial'][idx:] += 1

    # filter out the tapping events only
    df_events = df_events[df_events['event_code'].isin(EVENT_DICT.values())]

    # create a column including the event names
    df_events['event_name'] = [INV_EVENT_DICT[str(code)] for code in df_events['event_code']]
    
    return df_events


def remove_ghost_triggers(df):
    """Removes Ghost Triggers from an event dataframe, based on the logic that
    all taps from each person should have a larger code than the previous tap
    from the same person."""
    
    # split the tap dataframe up for each subject
    for subj in [1,2]:
        subj_df = df[df['event_name'].str.startswith("s" + str(subj))]
        subj_df = subj_df.sort_values(['sample'])
    
    
        # look only at the indices and event codes from one person
        indices = subj_df["event_index"].to_numpy()
        event_codes = subj_df["event_code"].to_numpy()
    
        for i in range(len(indices)):
        
            # look at the previous code, current code and the current index
            previous_code = event_codes[i-1]
            current_code = event_codes[i]
            current_index = indices[i]
        
            # the initial tap codes are allowed to be smaller than the previous taps
            #if current_code not in (6, 15):
            # FIXME: The above logic leaves out ghost triggers with code 6 or 15. we must make sure these are also included.
            # i fix this in the below statement. However, this was not run in python, so if there are any errors, this might be the line to correct
            is_start_tap = ((current_code == 6) and (previous_code == 14)) or ((current_code == 15) and (previous_code == 23))
            if not is_start_tap:
            
                # for all other taps, if the code is not one step higher than the
                # previous trigger, it's a ghost trigger.
                if current_code != previous_code + 1:
                
                    # then we remove the ghost trigger from the orginial dataframe
                    df = df[df["event_index"] != current_index]
                    
                    # replace the ghost trigger value in event codes, so the next
                    # iteration will reference the last valid trigger.
                    event_codes[i] = event_codes[i-1]
                
    return df


### Combine dataframes and return MNE events

def join_event_dfs(event_df, behavioral_df):
    """Join a behavioral and an event dataframe."""
    
    # sort both dataframes after trial, subject, tap
    event_df = event_df.sort_values(['event_trial', 'event_name'])
    behavioral_df = behavioral_df.sort_values(['trial', 'subject', 'tapnr'])
    
    # reset the event df index to the behavioral df
    event_df.index = behavioral_df.index
    
    return event_df.join(behavioral_df).drop(columns=['event_trial'])


def events_from_event_df(df):
    """Sort a combined event dataframe and return it to a mne-style numpy array."""
    df = df.sort_values(['event_index'])
    events = np.vstack([df['sample'],
                        np.zeros(len(df)),
                        df['event_code']]).astype(int).T
    
    return events
