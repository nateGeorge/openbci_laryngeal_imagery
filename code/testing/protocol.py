import sys
import time

from psychopy import gui, core
import psychopy.visual as visual
from psychopy.event import Mouse, getKeys
import colorama
from colorama import Fore, Style

# from brainflow.board_shim import BoardShim, BrainFlowInputParams



class experiment():
    def __init__(self):
        pass
    def start_exp(self, exit_after=True, pKey='p', escKey='escape'):
        self.win = visual.Window()
        self.pKey = pKey
        self.escKey = escKey
        if exit_after:
            for i in range(6):
                print(i)
                time.sleep(1)
            self.win.close()
        return self.win


    def pause(self, end_sect=False):
        pKey = self.pKey
        escKey = self.escKey
        print('Paused')
        if end_sect:
                text = visual.TextStim(win=self.win, text='Press ' + str(pKey) + ' to go on to the next section')
                text.draw()
                self.win.flip()
                print('Press ' + str(pKey) + ' to go on to the next section')
        else:
            print('Press ' + str(pKey) + ' to unpause')
        print('Press ' + str(escKey) + ' to quit')

        while True:
            self.keys = getKeys()
            if pKey in self.keys:
                break
            if escKey in self.keys:
                print('Goodbye... for now.')
                self.win.close()
                core.quit()


    def listen_for(self, find=[], wait=-1):
        print('Press ' + self.escKey + ' to quit')
        print('Press ' + self.pKey + ' to pause')
        if wait >= 0:
            for i in range(wait):
                self.keys = getKeys()
                print(self.keys)
                print(i)
                time.sleep(1)
                found = []
                for f in find:
                    if f in self.keys:
                        found.append(f)
                for f in found:
                    print(f)
                    if f == self.escKey:
                        print('Goodbye... for now.')
                        self.win.close()
                        core.quit()
                    if f == self.pKey:
                        EXP.pause()
            # Maybe flip window here (this is after you've waited wait seconds)
        elif wait == -1:
            i=0
            while True:
                self.keys = getKeys()
                if i % 200000 == 0:
                    print('...')
                found = []
                for f in find:
                    if f in self.keys:
                        found.append(f)
                for f in found:
                    print(self.keys)
                    if f == self.escKey:
                        print('Goodbye... for now.')
                        self.win.close()
                        core.quit()
                    if f == self.pKey:
                        EXP.pause()
                i+=1

    def run_section(self, section='prexp'):
        self.win.flip() # clear window before each new section

        if section == 'prexp':
            self.curSec = 'prexp'
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=[escKey, pKey], wait=5)
            EXP.pause(end_sect=True)
        if section == 'ssvep':
            self.curSec = 'ssvep'
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=[escKey, pKey], wait=1)
            EXP.pause(end_sect=True)
        if section == 'mi-a':
            self.curSec = 'mi-a'
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=[escKey, pKey], wait=1)
            EXP.pause(end_sect=True)
        if section == 'mi-i':
            self.curSec = 'mi-i'
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=[escKey, pKey], wait=1)
            EXP.pause(end_sect=True)
        if section == 'lmi-abs-a':
            self.curSec = 'lmi-abs-a'
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=[escKey, pKey], wait=1)
            EXP.pause(end_sect=True)
        if section == 'lmi-abs-i':
            self.curSec = 'lmi--abs-i'
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=[escKey, pKey], wait=1)
            EXP.pause(end_sect=True)
        if section == 'lmi-pitch-a':
            self.curSec = 'lmi--pitch-a'
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=[escKey, pKey], wait=1)
            EXP.pause(end_sect=True)
        if section == 'lmi-pitch-i':
            self.curSec = 'lmi--pitch-i'
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=[escKey, pKey], wait=1)
            EXP.pause(end_sect=True)








exit_after=False
pKey = 'p' # pause key
escKey = 'escape'
EXP = experiment()
EXP.start_exp(exit_after=exit_after, pKey=pKey, escKey=escKey)
# EXP.listen_for(find=[escKey, pKey])
EXP.run_section('prexp')
EXP.run_section('ssvep')

if not exit_after:
    EXP.win.close()
