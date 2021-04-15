#!/usr/local/bin/python
# -*- coding: utf-8 -*-
########################################
# Hyperscanning Fingertapping Experiment
########################################

import os, sys
import psychopy
from psychopy import prefs
prefs.hardware['audioLib'] = ['PTB']
prefs.hardware['audioDevice'] = 'USB Audio Device: - (hw:3,0)'
from psychopy import visual, event, core
from psychopy import sound
import psychtoolbox as ptb
from Hyper_Parameters_NEW import *
import csv
import threading
import random
#import parallel

#p = parallel.Parallel()
bp_player1 = sound.Sound(sound_bp_player1, bp_soundlength)
bp_player2 = sound.Sound(sound_bp_player2, bp_soundlength)

def print_on_screen(s1_text, s2_text, size):
    print_screen_one = visual.TextStim(SCREEN_1, text=s1_text, pos=(-width_height[0]/4,0.0), wrapWidth=1100, height=size, units='pix', autoLog=False)
    print_screen_two = visual.TextStim(SCREEN_1, text=s2_text, pos=(width_height[0]/4,0.0), wrapWidth=1100, height=size, units='pix', autoLog=False)
    print_screen_one.draw()
    print_screen_two.draw()
    SCREEN_1.flip()

# Create csv file and header
trial_header = ['pair', 'condition', 'block', 'trial', 'subject', 'tapnr', 'ttap', 'jitter', 'player_start_first']
with open(path, 'w') as f:
    wr = csv.writer(f)
    wr.writerow(trial_header)


# Check whether participants press correct button on their toolboxes
# defineButton() assigns correct button to Toolbox
def defineButton1():
    bp_player1 = sound.Sound(sound_bp_player1, bp_soundlength)
    print('Fetch buttons for experiment... \n-->Press \'yellow-button\' :')
    print_on_screen("You\'re assigned to the \'yellow-button\'.\nPlease press it once to hear your sound...", "Wait for other participant...", 30)
    box1 = False
    while box1 != True:
        button1 = psychopy.event.waitKeys()
        if button1 == ['1']:
            bp_player1.play()
            box1 = True
            print('button assigned to \'yellow1\'')
        else:
            box1 = False
            print('pressed wrong button, try again...')


# Same procedure for Toolbox2
def defineButton2():
    bp_player2 = sound.Sound(sound_bp_player2, bp_soundlength)
    print('...\n...\n-->Press \'yellow\' key:')
    print_on_screen("Wait for other participant...", "You\'re assigned to the \'yellow-button\'.\nPlease press it once to hear your sound...", 30)
    box2 = False
    while box2 != True:
        button2 = psychopy.event.waitKeys()
        if button2 == ['8']:
            bp_player2.play()
            box2 = True
            print('button assigned to \'yellow2\'')
        else:
            box2 = False
            print('pressed wrong button, try again...')


# used in the cases where experimenter needs to confirm (with "space")
# e.g. during monitor-setup and for the long breaks
def waitForExperimenter():
    pressed = False
    while not pressed:
        event = psychopy.event.getKeys()
        if event == ['space']:
            pressed = True

# Function that catches key-presses to confirm the proceeding of experiment
# Waits for keypress "l" and "r" to proceed and "escape" to quit
def waitForConfirm(statement, total_dur, size = 30):
    print_on_screen(statement, statement, size)
    print('...\n...\nPress \"space\" to start %s or \"esc\" to quit:' %(statement))
    press_2 = 0
    press_7 = 0
    pressed = False
    while not pressed:
        #print pressed
        event = psychopy.event.getKeys(['2','7'])
        if event == ['escape']:
            print("Total duration: %s" %(round(total_dur.getTime(), 2)))
            core.quit()
        if event == ['2']:
            # When "l" was pressed and it was the 2nd input (because r has already been pressed)
            # --> start immediately with procedure
            if press_7 > 0:
                print_on_screen("Start..", "Start..", 30)
                core.wait(1.0)
            # --> otherwise print "waiting for other participant" statement
            else:
                print_on_screen("Ready... wait for other participant", statement, size)
            press_2 += 1
        elif event == ['7']:
            # In case "r" was pressed + it was 2nd input
            # --> proceed immediately
            if press_2 > 0:
                print_on_screen("Start..", "Start..", 30)
                core.wait(1.0)
            # --> otherwise wait for other participants key-press (same as above)
            else:
                print('P2 is ready')
                print_on_screen(statement, "Ready... wait for other participant", size)
            press_7 += 1
        if press_2 >= 1 and press_7 >= 1:
            pressed = True
            print('Starting...')

def print_red_fix_cross():
    fixation_screen_1 = psychopy.visual.ShapeStim(SCREEN_1, pos=(-width_height[0]/4, 0.0), vertices=((0,-fix_cross_arm_len),(0,fix_cross_arm_len),(0,0),(-fix_cross_arm_len,0),(fix_cross_arm_len,0)), units = 'pix', lineWidth = 10,closeShape = False, lineColor = red)
    fixation_screen_2 = psychopy.visual.ShapeStim(SCREEN_1, pos=(width_height[0]/4, 0.0), vertices=((0,-fix_cross_arm_len),(0,fix_cross_arm_len),(0,0),(-fix_cross_arm_len,0),(fix_cross_arm_len,0)), units = 'pix', lineWidth = 10,closeShape = False, lineColor = red)
    fixation_screen_1.draw()
    fixation_screen_2.draw()
    SCREEN_1.flip()




# Practice block for participants to get used to their sound and the procedure
def testBlock():
    fixation_s1 = psychopy.visual.ShapeStim(SCREEN_1, pos=(-width_height[0]/4, 0.0), vertices=((0,-fix_cross_arm_len),(0,fix_cross_arm_len),(0,0),(-fix_cross_arm_len,0),(fix_cross_arm_len,0)), units='pix', lineWidth = 10,closeShape = False, lineColor ='green')
    fixation_s2 = psychopy.visual.ShapeStim(SCREEN_1, pos=(width_height[0]/4, 0.0), vertices=((0,-fix_cross_arm_len),(0,fix_cross_arm_len),(0,0),(-fix_cross_arm_len,0),(fix_cross_arm_len,0)), units='pix', lineWidth = 10,closeShape = False, lineColor ='green')
    if random.random() > .5:
        fixation_s1.draw()
        SCREEN_1.flip()
        #p.setData(1)
        core.wait(0.01)
        #p.setData(0)
        core.wait(random.choice(jitters_onset))
        fixation_s1.draw()
        fixation_s2.draw()
        SCREEN_1.flip()
        #p.setData(2)
        core.wait(0.01)
        #p.setData(0)
    else:
        fixation_s2.draw()
        SCREEN_1.flip()
        #p.setData(2)
        core.wait(0.01)
        #p.setData(0)
        core.wait(random.choice(jitters_onset))
        fixation_s2.draw()
        fixation_s1.draw()
        SCREEN_1.flip()
        #p.setData(1)
        core.wait(0.01)
        #p.setData(0)
    # wait until the 'pre' time has passed
    core.wait(pre_duration)
    # Counter for nr. of taps
    press_s1 = 0
    press_s2 = 0
    pressed = False
    # make sure to not carry over button presses into next trial
    event.clearEvents(eventType = 'keyboard')
    while pressed != True:
        keys = event.getKeys(keyList = ['1','8'])
        # If statement for subject1 - collecting all information in list sub1*
        if keys == ['1'] and press_s1 < num_taps:
            bp_player1.play()
            press_s1 += 1
        # If statement for subject2 - collecting all information in list sub2**
        if keys == ['8'] and press_s2 < num_taps:
            bp_player2.play()
            press_s2 += 1
        # exit while loop when both players pressed 8 times
        if press_s1 == num_taps and press_s2 == num_taps:
            pressed = True
            core.wait(0.2)


# trialBlock() tracks the time and creates the sounds for each tap
def trialBlock(block, trial, condition):
    # Initialize the clock to track time, starts counting from beginning of statement
    clock = core.Clock()
    # initialize trial_dur to track duration of one trial
    trial_dur = core.Clock()
    #p.setData(48)
    core.wait(0.01)
    #p.setData(0)
    fixation_s1 = psychopy.visual.ShapeStim(SCREEN_1, pos=(-width_height[0]/4, 0.0), vertices=((0,-fix_cross_arm_len),(0,fix_cross_arm_len),(0,0),(-fix_cross_arm_len,0),(fix_cross_arm_len,0)), units='pix', lineWidth = 10,closeShape = False, lineColor ='green')
    fixation_s2 = psychopy.visual.ShapeStim(SCREEN_1, pos=(width_height[0]/4, 0.0), vertices=((0,-fix_cross_arm_len),(0,fix_cross_arm_len),(0,0),(-fix_cross_arm_len,0),(fix_cross_arm_len,0)), units='pix', lineWidth = 10,closeShape = False, lineColor ='green')
    jitter_trial = random.choice(jitters_onset)
    # if a random chosen nr. from interval [0,1) is bigger than .5, show fixation cross first on screen 1
    if random.random() > .5:
        fixation_s1.draw()
        SCREEN_1.flip()
        #p.setData(4)
        core.wait(0.01)
        #p.setData(0)
        core.wait(jitter_trial)
        fixation_s1.draw()
        fixation_s2.draw()
        SCREEN_1.flip()
        #p.setData(5)
        core.wait(0.01)
        #p.setData(0)
        player_start_first = 1
    else:
        fixation_s2.draw()
        SCREEN_1.flip()
        #p.setData(5)
        core.wait(0.01)
        #p.setData(0)
        core.wait(jitter_trial)
        fixation_s2.draw()
        fixation_s1.draw()
        SCREEN_1.flip()
        #p.setData(4)
        core.wait(0.01)
        #p.setData(0)
        player_start_first = 2
    # wait until the 'pre' time has passed
    core.wait(pre_duration)
    # The lists sub1 and sub2 will be fed with the trialdata of subject 1 and 2, respectively
    # At the end of Trialblock, sub1 gets all the trialdata of both subjects and will be returned
    # That enables the right structure of the data when it gets written to the csv
    sub1 = []
    sub2 = []
    # Counter for nr. of taps
    press_s1 = 0
    press_s2 = 0
    pressed = False
    # make sure to not carry over button presses into next trial
    event.clearEvents(eventType = 'keyboard')
    while pressed != True:
        keys = event.getKeys(keyList = ['1','8'])
        # If statement for subject1 - collecting all information in list sub1*
        if keys == ['1'] and press_s1 < num_taps:
            rt1 = clock.getTime()
            bp_player1.play()
            press_s1 += 1
            if press_s1 == 1:
                #p.setData(6)
                core.wait(0.01)
                #p.setData(0)
            if press_s1 == 2:
                #p.setData(7)
                core.wait(0.01)
                #p.setData(0)
            if press_s1 == 3:
                #p.setData(8)
                core.wait(0.01)
                #p.setData(0)
            if press_s1 == 4:
                #p.setData(9)
                core.wait(0.01)
                #p.setData(0)
            if press_s1 == 5:
                #p.setData(10)
                core.wait(0.01)
                #p.setData(0)
            if press_s1 == 6:
                #p.setData(11)
                core.wait(0.01)
                #p.setData(0)
            if press_s1 == 7:
                #p.setData(12)
                core.wait(0.01)
                #p.setData(0)
            if press_s1 == 8:
                #p.setData(13)
                core.wait(0.01)
                #p.setData(0)
            if press_s1 == 9:
                #p.setData(14)
                core.wait(0.01)
                #p.setData(0)
            # define the list of output parameters that will be passed to the csv file FOR SUBJECT1
            trialdata1 = []
            trialdata1.append(pairnumber)
            trialdata1.append(condition)
            trialdata1.append(block)
            trialdata1.append(trial)
            trialdata1.append(1)                #subject nr.
            trialdata1.append(press_s1)
            trialdata1.append(rt1)
            trialdata1.append(jitter_trial)
            trialdata1.append(player_start_first)
            sub1.append(trialdata1)
            trialdata1 = []
        # If statement for subject2 - collecting all information in list sub2**
        if keys == ['8'] and press_s2 < num_taps:
            rt2 = clock.getTime()
            bp_player2.play()
            press_s2 += 1
            if press_s2 == 1:
                #p.setData(15)
                core.wait(0.01)
                #p.setData(0)
            if press_s2 == 2:
                #p.setData(16)
                core.wait(0.01)
                #p.setData(0)
            if press_s2 == 3:
                #p.setData(17)
                core.wait(0.01)
                #p.setData(0)
            if press_s2 == 4:
                #p.setData(18)
                core.wait(0.01)
                #p.setData(0)
            if press_s2 == 5:
                #p.setData(19)
                core.wait(0.01)
                #p.setData(0)
            if press_s2 == 6:
                #p.setData(20)
                core.wait(0.01)
                #p.setData(0)
            if press_s2 == 7:
                #p.setData(21)
                core.wait(0.01)
                #p.setData(0)
            if press_s2 == 8:
                #p.setData(22)
                core.wait(0.01)
                #p.setData(0)
            if press_s2 == 9:
                #p.setData(23)
                core.wait(0.01)
                #p.setData(0)
            # define the list of output parameters that will be passed to the csv file FOR SUBJECT2
            trialdata2 = []
            trialdata2.append(pairnumber)
            trialdata2.append(condition)
            trialdata2.append(block)
            trialdata2.append(trial)
            trialdata2.append(2)
            trialdata2.append(press_s2)
            trialdata2.append(rt2)
            trialdata2.append(jitter_trial)
            trialdata2.append(player_start_first)
            sub2.append(trialdata2)  #**
            trialdata2 = []
        # exit while loop when both players pressed 8 times
        if press_s1 == num_taps and press_s2 == num_taps:
            pressed = True
            # all output info of subject2 (saved in sub2) is appended at the end of sub1
            # this is then returned in order to be written to the csv file
            sub1.extend(sub2)
    #p.setData(49)
    core.wait(0.01)
    #p.setData(0)
    print("Trial duration: {}".format(round(trial_dur.getTime(),2)))
    print_red_fix_cross()
    core.wait(iti)
    return sub1
