import sys
import time

from psychopy import gui, core
import psychopy.visual as visual
from psychopy.event import Mouse, getKeys
import colorama
from colorama import Fore, Style

# from brainflow.board_shim import BoardShim, BrainFlowInputParams

class slide():
# An object for handling all psychopy objects for one slide
    def __init__(self, texts=[], imgs=[], elph_box=-1):
        # texts and imgs elements should be tuples of (text/img_url, position, and size) i.e. ("text/img_url", (0,0), 0.5)
        # elph_box
        #  -1: don't show elephant elephant box
        #   0: show elephant NOT in box
        #   1: show elephant in box
        self.texts = texts
        self.imgs = imgs
        self.elph_box = elph_box

    def make_stims(self):
        # TextStim
        self.stims = {"texts":[], "imgs":[]}
        for i in range(len(self.texts)):
            print("First in tuple: " + str(self.texts[i][0]))
            print("Second in tuple: " + str(self.texts[i][1]))
            self.stims["texts"].append(visual.TextStim(win=EXP.win, text=self.texts[i][0], pos=self.texts[i][1]))
        for i in range(len(self.imgs)):
            self.stims["imgs"].append(visual.ImageStim(win=EXP.win, image=self.imgs[i][0], pos=self.imgs[i][1]))
        if self.elph_box in [0, 1]:
            self.stims["imgs"].append(visual.ImageStim(win=EXP.win, image="lemmling-2D-cartoon-elephant.jpg", mask="lemmling-2D-cartoon-elephant-transparency-mask.jpg", pos=(0, .5), size=0.4)) # make elephant stimulus

        # ImageStim

    def show_slide(self, EXP):
        # EXP should be an experiment object
        for i in range(len(self.stims['texts'])):
            # text = visual.TextStim(win=EXP.win, text=self.texts[i][0], pos=self.texts[i][1])
            # text.draw()
            self.stims["texts"][i].draw()
        for i in range(len(self.stims['imgs'])):
            self.stims["imgs"][i].draw() # show elephant stimulus
        if self.elph_box in [0, 1]:
            # make and show box stimulus
            if self.elph_box == 0:
                pos = (0.8, 0.5)
            else:
                pos = (0, 0.5)
            boxStim = visual.Rect(win=EXP.win, pos=pos, lineColor="red")
            boxStim.draw()


        EXP.win.flip()
        time.sleep(2)



class experiment():
    def __init__(self):
        self.slides = []
    def start_exp(self, exit_after=True, pKey='p', escKey='escape', fwdKey='right'):
        self.win = visual.Window()
        self.pKey = pKey
        self.escKey = escKey
        self.fwdKey = fwdKey
        if exit_after:
            for i in range(6):
                print(i)
                time.sleep(1)
            self.win.close()
        return self.win

    def close_exp(self, check=False):
        if check:
            text = visual.TextStim(win=self.win, text="Are you sure you want to close the program? \n(y/n)")
            text.draw()
            self.win.flip()
            while True:
                self.keys = getKeys()
                if len(self.keys) > 0:
                    print(self.keys)
                if "y" in self.keys or "n" in self.keys:
                    if "y" in self.keys:
                        print('Goodbye... for now.')
                        self.win.close()
                        core.quit()
                        sys.exit()
                    if "n" in self.keys:
                        self.win.flip()
                        return

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
                self.close_exp(check=True)


    def listen_for(self, find=[], wait=-1):
        print('Press ' + self.escKey + ' to quit')
        print('Press ' + self.pKey + ' to pause')
        print('Press ' + self.fwdKey + ' to move forward ')
        if wait >= 0:
            for i in range(wait):
                self.keys = getKeys()
                print(str(i) + ": " + str(self.keys))
                time.sleep(1)
                found = []
                for f in find:
                    if f in self.keys:
                        found.append(f)
                for f in found:
                    print(f)
                    if f == self.escKey:
                        self.close_exp(check=True)
                    if f == self.pKey:
                        EXP.pause()
            # Maybe flip window here (this is after you've waited wait seconds)
        elif wait == -1:
            i=0
            while True:
                self.keys = getKeys()
                if len(self.keys) > 0:
                    print(self.keys)
                if i % 200000 == 0:
                    print('...')
                found = []
                for f in find:
                    if f in self.keys:
                        found.append(f)
                for f in found:
                    if f == self.escKey:
                        self.close_exp(check=True)
                    if f == self.pKey:
                        EXP.pause()
                    if f == self.fwdKey:
                        return
                i+=1

    def run_section(self, section='prexp', wait=-1):
        self.win.flip() # clear window before each new section
        self.curSec = section
        keys = [escKey, pKey]

        if section == 'prexp':
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=keys + [fwdKey], wait=wait)
            EXP.pause(end_sect=True)
        if section == 'ssvep':
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=keys + [fwdKey], wait=wait)
            EXP.pause(end_sect=True)
        if section == 'mi-a':
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=keys, wait=wait)
            EXP.pause(end_sect=True)
        if section == 'mi-i':
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=keys, wait=wait)
            EXP.pause(end_sect=True)
        if section == 'lmi-abs-a':
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=keys, wait=wait)
            EXP.pause(end_sect=True)
        if section == 'lmi-abs-i':
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=keys, wait=wait)
            EXP.pause(end_sect=True)
        if section == 'lmi-pitch-a':
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=keys, wait=wait)
            EXP.pause(end_sect=True)
        if section == 'lmi-pitch-i':
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=keys, wait=wait)
            EXP.pause(end_sect=True)








exit_after=False
pKey = 'p' # pause key
escKey = 'escape'
fwdKey = 'right'
EXP = experiment()
EXP.start_exp(exit_after=exit_after, pKey=pKey, escKey=escKey, fwdKey=fwdKey)
EXP.run_section('prexp')
EXP.run_section('ssvep')


# slides = []
# slides.append(slide(texts= [("Hey, did I do the thing?",(-.5,0)),
#                             ("Hey did I do a second thing?",(.5, 0))
#                                 ], elph_box=-1))
# slides[0].make_stims()
# slides[0].show_slide(EXP)

if not exit_after:
    EXP.win.close()
