# -*- coding: utf-8 -*-
########################################
# Hyperscanning Fingertapping Experiment
########################################
import os, sys
import psychopy
from psychopy import event, visual, core, sound, data, logging
import numpy as np
import pandas as pd
import pygame

######################################
# create a data subfolder for log-data
######################################
# define info about the experiment session
print('Enter pair number:')
pairnumber = raw_input()
expInfo = {u'session': u'001', u'group': pairnumber}
expInfo['expName'] = 'Fingertapping_Task'

# if not already existent, create folder in which data is saved
if not os.path.isdir('hyper_log'):
    os.makedirs('hyper_log')  # if this fails (e.g. permissions) we will get error
filename = 'hyper_log' + os.path.sep + '%s' %['group']    #os.path.sep simply creates '\'
logFile = logging.LogFile(filename + '.log', level=logging.EXP)
logging.console.setLevel(logging.CRITICAL) # this outputs to the screen, not a file

############################################
# Create a data subfolder for experiment data
############################################
# get the path of currently executed script
EXPPATH = os.path.dirname(os.path.abspath('Hyper_Main.py'))
DATAPATH = EXPPATH + '/hyper_data'
# add a data subfolder
if not os.path.exists(DATAPATH):
    os.makedirs(DATAPATH)
# Name of csv file
csvfile = '%s.csv' %expInfo['group']
path = DATAPATH +'/' + csvfile

#######################
# Experiment Parameters
#######################
num_trials_training = 6       # 6; default
num_trials = 25               # 25; num of required trials
num_taps = 9                  # 9; num of required taps per trial
num_blocks = 12               # 12; num of blocks
pre_duration = 3              # waiting time til trial starts
iti = 1.0                     # inter trial interval
jitters_onset = [0.05, 0.025, 0.075, 0.1]
iti_jitters = [1.25, 1.5, 1.75]
full_screen = True
width_height = [1920,1080]
fix_cross_arm_len = 50 # in pixels
red = [.7,-1,-1]
####################
# Pygame mixer sound
####################
# Initialize pygame mixer settings
pygame.mixer.pre_init(frequency = 44100, size = -16, channels = 2, buffer = 2048)       # channels = 2 means stereo, =1 means mono
pygame.mixer.init()
trialstart = pygame.mixer.Sound("Sounds/start-short.wav")
trialend = pygame.mixer.Sound("Sounds/stop.wav")
breaktone = pygame.mixer.Sound("Sounds/break.wav")
bp_player1 = pygame.mixer.Sound("Sounds/sound1-75ms.wav")
bp_player2 = pygame.mixer.Sound("Sounds/sound2-75ms.wav")
#help(pygame.mixer.Sound)

#### create psychopy screens
# Create a window and the stimuli to be shown on screen. Also implemented two circles as visual feedback of the tapping
if full_screen == True:
    SCREEN_1 = psychopy.visual.Window(fullscr = True, pos = None, screen = 0)
    m = psychopy.event.Mouse(win=SCREEN_1)
    m.setVisible(0)
    SCREEN_2 = psychopy.visual.Window(fullscr = True, pos = None, screen = 1)
    m = psychopy.event.Mouse(win=SCREEN_2)
    m.setVisible(0)
else:
    SCREEN_1 = psychopy.visual.Window(width_height, pos = None, screen = 0)
    m = psychopy.event.Mouse(win=SCREEN_1)
    m.setVisible(0)
    SCREEN_2 = psychopy.visual.Window(width_height, pos = None, screen = 1 )
    m = psychopy.event.Mouse(win=SCREEN_2)
    m.setVisible(0)


# text to display (always double because separate key-presses for each screen or subject)
# s1 = subject1, s2 = subject2
s1_instructions_message = "Steps:\n\
Your task is to synchronize your tapping with the other participant.\n\
1. At start of each trial, a red cross is shown in the middle of the screen.\n\
2. When the cross changes to green - wait 3 seconds until you start tapping the  \'yellow-button\'. You will not be able to hear any sound if you tap prior to 3 sec!\n\
3. Tap 9 times with your index finger of dominant hand.\n\
4. As a reference for tapping speed, tap two time/sec.\n\
5. Place finger right above the button, use appropriate force to press it - don\'t slam it!\n\
6. Synchronize your taps with the other participant.\n\
7. When both of you tapped 9 times, the cross changes its color to red again.\n\
8. Very short break time, then procedure will be repeated from 1.\n\
9. After 25 trials, the text \'BREAK\' will occur, indicating the end of a block.\n\
10. You can take a small rest and press the \'white-button\' when ready to continue.\n\
11. There will be a total of 12 blocks. \n\n\
Please remember: Try to focus on fixation cross, sit still and avoid exploratory eye movements. Last but not least - enjoy!\n\n\
Press \'white-button\' when ready..."
s2_instructions_message = s1_instructions_message
s1_practice_block_message = "PRACTICE BLOCK.\n\nPress \'white-button\' to start" # also possible to press \"esc\" to quit.
s2_practice_block_message = "PRACTICE BLOCK.\n\nPress \'white-button\' to start"
s1_exp_block_message = "EXPERIMENT.\n\nPress \'white-button\' to start"         # same here
s2_exp_block_message = "EXPERIMENT.\n\nPress \'white-button\' to start"
s1_break_message = "BREAK.\n\nPress \'white-button\' to continue"
s2_break_message = "BREAK.\n\nPress \'white-button\' to continue"
long_break_message1 = "You completed a quarter of the task!\n\nPlease inform the experimenter."
long_break_message2 = "You are half way through - take a breath!\n\nPlease inform the experimenter."
long_break_message3  = "Damn well - you mastered three-quarters of the task!\n\nPlease inform the experimenter."
long_break_message4  = "DONE - you are finished!!!\n\nPlease inform the experimenter."
