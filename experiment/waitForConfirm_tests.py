#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os, sys
import psychopy
from psychopy import event, visual, core, sound
import csv
import pygame

list = [1,23,3]
len(list)

########## Original
# def waitForConfirm(statement, total_dur):
#     print('...\n...\nPress \"space\" to start %s or \"esc\" to quit:' %(statement))
#     pressed = False
#     while not pressed:
#         #print pressed
#         event = psychopy.event.getKeys()
#         if event == ['space']:
#             pressed = True
#             print('Starting...')
#         if event == ['escape']:
#             print("Total duration: %s" %(round(total_dur.getTime(), 2)))
#             core.quit()


############ Option 1 - 2x space
# def waitForConfirm(statement, total_dur):
#     print('...\n...\nPress \"space\" to start %s or \"esc\" to quit:' %(statement))
#     space = 0
#     pressed = False
#     while not pressed:
#         #print pressed
#         event = psychopy.event.getKeys()
#         if event == ['escape']:
#             print("Total duration: %s" %(round(total_dur.getTime(), 2)))
#             core.quit()
#         if event == ['space']:
#             space += 1
#         if space == 2:
#             pressed = True
#             print('Starting...')
