# -*- coding: utf-8 -*-
########################################
# Hyperscanning Fingertapping Experiment
########################################

# About:
# Two subjects will sit in front of their respective buttonbox while facing
# each other. The task is to start tapping after a signal sound is played
# and to synchronize their finger tappings as soon and as accurate as
# possible until a second tone occurs which indicates the end of the trial.
# There is a break implemented between each block whose start and end is
# indicated by a small melody. The end of the whole experiment is also
# indicated by a low, prolonged tone.

# Do not forget to define your experiment and triggers in the
# 'Experiment Parameters' section in Hyper_Parameters.py
import os, sys
import pygame
from Hyper_Parameters_NEW import *
from Hyper_Functions_NEW import *
import psychopy
from psychopy import event, visual, core, data, logging
import csv
import threading
import random

#################################
# Start with experiment procedure
#################################
print('Initializing Experiment...')
# Define clock for timing of whole experiment
total_dur = core.Clock()
# Define clock for timing of break_block
clock3 = core.Clock()

# Check for screen setup
print_s1("SCREEN 1", 40)
print_s2("SCREEN 2", 40)
waitForExperimenter()

#######################
# Instruct participants
#######################
# Show initial instructions on screen
print_on_screen(s1_instructions_message, s2_instructions_message, 25)
waitForConfirm(" ", total_dur)
# Call defineButton() to assign Buttons to Toolboxes
defineButton1()
defineButton2()
# call waitForConfirm() to start testBlock
print_on_screen(s1_practice_block_message, s2_practice_block_message, 30)
waitForConfirm("PRACTICE BLOCK.", total_dur)
# start testBlock()
for x in range(num_trials_training):
    print_red_fix_cross()
    core.wait(iti)
    testBlock()

#########################
# Start actual experiment
#########################
print_on_screen(s1_exp_block_message, s2_exp_block_message, 30)
# call waitForConfirm() to start experiment
waitForConfirm("EXPERIMENT.", total_dur)
# Reset clock to count from the start of the "real experiment"
total_dur.reset()
# enumerate trials consecutively from 1 to last without reset
ful_trial = 1
# repeat trial_block() and break_block() for num_blocks for each condition
for block in range(num_blocks):
    #######################################################
    # Condition 1: Subjects do not see each other --> blind
    #######################################################
    s1_block_message = "BLOCK Nr. %s\n\nPress \'white-button\' to start" %(block+1)
    s2_block_message = "BLOCK Nr. %s\n\nPress \'white-button\' to start" %(block+1)
    print_on_screen(s1_block_message, s2_block_message, 30)
    condition = 'blind'
    waitForConfirm("BLOCK Nr. %s" %(block+1), total_dur)
    # initialize trials of duration num_trials:
    if block == 1:
        p.setData(24)
        core.wait(0.01)
        p.setData(0)
    if block == 2:
        p.setData(25)
        core.wait(0.01)
        p.setData(0)
    if block == 3:
        p.setData(26)
        core.wait(0.01)
        p.setData(0)
    if block == 4:
        p.setData(27)
        core.wait(0.01)
        p.setData(0)
    if block == 5:
        p.setData(28)
        core.wait(0.01)
        p.setData(0)
    if block == 6:
        p.setData(29)
        core.wait(0.01)
        p.setData(0)
    if block == 7:
        p.setData(30)
        core.wait(0.01)
        p.setData(0)
    if block == 8:
        p.setData(31)
        core.wait(0.01)
        p.setData(0)
    if block == 9:
        p.setData(32)
        core.wait(0.01)
        p.setData(0)
    if block == 10:
        p.setData(33)
        core.wait(0.01)
        p.setData(0)
    if block == 11:
        p.setData(34)
        core.wait(0.01)
        p.setData(0)
    if block == 12:
        p.setData(35)
        core.wait(0.01)
        p.setData(0)
    for trial in range(num_trials):
    	if trial == 0:
    	    fixation_s1 = psychopy.visual.ShapeStim(SCREEN_1,vertices = ((0,-fix_cross_arm_len),(0,fix_cross_arm_len),(0,0),(-fix_cross_arm_len,0),(fix_cross_arm_len,0)), units='pix', lineWidth = 10,closeShape = False, lineColor = red)
    	    fixation_s2 = psychopy.visual.ShapeStim(SCREEN_2,vertices = ((0,-fix_cross_arm_len),(0,fix_cross_arm_len),(0,0),(-fix_cross_arm_len,0),(fix_cross_arm_len,0)), units='pix', lineWidth = 10,closeShape = False, lineColor = red)
    	    fixation_s1.draw()
    	    fixation_s2.draw()
    	    SCREEN_1.flip()
    	    SCREEN_2.flip()
            p.setData(3)
            core.wait(0.01)
            p.setData(0)
    	    core.wait(iti)
        dataset = trialBlock(block+1, ful_trial, condition)
        # Write the aquired data of each trial into the csv
        with open(path, 'a') as f:
            wr = csv.writer(f)
            for list in dataset:
                wr.writerow(list)
        ful_trial += 1
        # waiting time till next trial begins
        core.wait(random.choice(iti_jitters))
    if block == 1:
        p.setData(36)
        core.wait(0.01)
        p.setData(0)
    if block == 2:
        p.setData(37)
        core.wait(0.01)
        p.setData(0)
    if block == 3:
        p.setData(38)
        core.wait(0.01)
        p.setData(0)
    if block == 4:
        p.setData(39)
        core.wait(0.01)
        p.setData(0)
    if block == 5:
        p.setData(40)
        core.wait(0.01)
        p.setData(0)
    if block == 6:
        p.setData(41)
        core.wait(0.01)
        p.setData(0)
    if block == 7:
        p.setData(42)
        core.wait(0.01)
        p.setData(0)
    if block == 8:
        p.setData(43)
        core.wait(0.01)
        p.setData(0)
    if block == 9:
        p.setData(44)
        core.wait(0.01)
        p.setData(0)
    if block == 10:
        p.setData(45)
        core.wait(0.01)
        p.setData(0)
    if block == 11:
        p.setData(46)
        core.wait(0.01)
        p.setData(0)
    if block == 12:
        p.setData(47)
        core.wait(0.01)
        p.setData(0)
    # Initialize the Break after Block is finished
    # Display text ("Pause block...")
    # if any([block+1==3, block+1==6, block+1==9]):
    #     print_on_screen(long_break_message, long_break_message, 30)
    #     waitForExperimenter()
    #     print_on_screen(s1_break_message, s2_break_message, 30)
    #     waitForConfirm("BREAK.", total_dur)
    if block+1 == 3:
        print_on_screen(long_break_message1, long_break_message1, 30)
        waitForExperimenter()
    elif block+1 == 6:
        print_on_screen(long_break_message2, long_break_message2, 30)
        waitForExperimenter()
    elif block+1 == 9:
        print_on_screen(long_break_message3, long_break_message3, 30)
        waitForExperimenter()
    elif block+1 == 12:
        print_on_screen(long_break_message4, long_break_message4, 30)
        waitForExperimenter()
    else:
        pass
    print_on_screen(s1_break_message, s2_break_message, 30)
    waitForConfirm("BREAK.", total_dur)



# End of experiment
# Get time of whole experiment duration
print("Total duration: %s" %(round(total_dur.getTime(), 2)))
# Close the window
screen.close()
print('terminate experiment')
core.quit()
