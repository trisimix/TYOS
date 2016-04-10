#FMRadio App
#copyright (c) 2016 Helmar Waiczies
#MIT License
###############################
#To be packaged with stock TYOS
###############################

from subprocess import Popen
import sys, time
import pygame

class Run():
    def __init__(self, fona):
        self.fona = fona
        self.headset = False
        self.get_audio_mode()
        #Setup colors
        self.RED = (255,0,0)
        self.GREEN = (0,255,0)
        self.WHITE = (255,255,255)
        self.menu = pygame.image.load('/home/pi/tyos/apps/FMRadio/menu.png')
        self.menu_rect = self.menu.get_rect()
        self.font = pygame.font.Font('/home/pi/tyos/fonts/arial.ttf', 32)
        self.off = self.font.render('OFF', True, self.RED, self.WHITE)
        self.on = self.font.render('ON', True, self.GREEN, self.WHITE)
        self.rect = self.off.get_rect()
        self.rect.centerx = 280
        self.rect.y = 158
        # radio stuff
        self.radio_on = False
        self.set_freq = '888'
        self.ch_max = 1
        self.volume= 0
        # set freqency
        freq = float(self.set_freq)
        freq = freq/10
        self.ch_number = 1
        self.radio_rect = self.off.get_rect()
        self.radio_rect.centerx = 280
        self.radio_rect.y = 102
        self.freq = self.font.render(str(self.ch_number) + ': ' + str(freq) + 'MHz' , True, self.GREEN, self.WHITE)
        self.freq_off = self.font.render( '--- MHz' , True, self.RED, self.WHITE)
        self.freq_rect = self.freq.get_rect()
        self.freq_rect.centerx = 200
        self.freq_rect.y = 350
        # set number of channels (after channel scan)
        self.no_of_ch = self.font.render(str(self.ch_max) , True, self.GREEN, self.WHITE)
        self.no_of_ch_rect = self.no_of_ch.get_rect()
        self.no_of_ch_rect.centerx = 280
        self.no_of_ch_rect.y = 255
        # set voulme
        self.vol = self.font.render(str(self.volume) , True, self.GREEN, self.WHITE)
        self.vol_rect = self.vol.get_rect()
        self.vol_rect.centerx = 236
        self.vol_rect.y = 208
        # set signal strength
        self.signal_str = self.font.render('--- / 112' , True, self.GREEN, self.WHITE)
        self.signal_str_rect = self.signal_str.get_rect()
        self.signal_str_rect.centerx = 200
        self.signal_str_rect.y = 398

        #Stuff to follow app protocol
        self.exit = False
        self.blit_one_surface = {'surface':[], 'rects':[]}
        self.blit = {'surfaces':[self.menu, self.off, self.off, self.freq_off, self.no_of_ch, self.vol, self.signal_str], 'rects':[self.menu_rect, self.rect, self.radio_rect, self.freq_rect, self.no_of_ch_rect, self.vol_rect, self.signal_str_rect]}

        #Set audio mode text
        if self.headset:
            self.blit['surfaces'][1] = self.on
        else:
            self.blit['surfaces'][1] = self.off

        self.next_app = None

    def get_audio_mode(self):
        audio_config = open('/home/pi/tyos/configure/audio.conf', 'r')
        file = audio_config.readlines()

        for i in range(0, len(file)):#Parse file
            if file[i][0] == '#':
                pass
                #Do Nothing. Line is comment
            else:
                file[i] = file[i].rstrip()
                if 'mode' in file[i]: #Extract audio mode: 1=Built in, 0=External
                    mode = file[i]

        mode = mode.split('=')
        self.mode = int(mode[1])

        if self.mode == 1:
            self.headset = False
        else:
            self.headset = True


    def run_app(self):
        pass

    def get_events(self, event):
        if event.pos[1] > 95 and event.pos[1] < 152:
            self.set_radio()
        if event.pos[1] > 153 and event.pos[1] < 201:
            self.set_headset()
        if event.pos[1] > 254 and event.pos[1] < 293:
            self.channel_scan()
        if event.pos[1] > 444 and event.pos[1] < 476:
            self.exit = True
        if event.pos[0] > 0 and event.pos[0] < 40:
            if event.pos[1] > 206 and event.pos[1] < 244:
                print 'Volume -'
                self.volume_down()
        if event.pos[0] > 279 and event.pos[0] < 320:
            if event.pos[1] > 206 and event.pos[1] < 244:
                print 'Volume +'
                self.volume_up()
        if event.pos[0] > 0 and event.pos[0] < 40:
            if event.pos[1] > 303 and event.pos[1] < 342:
                print 'Channel -'
                self.channel_down()
        if event.pos[0] > 279 and event.pos[0] < 320:
            if event.pos[1] > 303 and event.pos[1] < 342:
                print 'Channel +'
                self.channel_up()


    def on_first_run(self):
        self.exit = False

    def set_radio(self):
     if self.radio_on:
        self.blit['surfaces'][2] = self.off
        self.blit['surfaces'][3] = self.freq_off
        self.fona.transmit('AT+FMCLOSE')
        time.sleep(0.5)
        self.radio_on = False
     else:
        self.blit['surfaces'][2] = self.on
        self.blit['surfaces'][3] = self.freq
        self.radio_on = True
        self.fona.transmit('AT+FMOPEN=1')
        time.sleep(0.5)
        self.fona.transmit('AT+FMFREQ=' + self.set_freq)
        self.signal = self.fona.transmit('AT+FMSIGNAL=' + self.set_freq)
        self.signal = self.signal[1].split(':')
        print(self.signal)
        self.signal_str = self.font.render(str(self.signal[2]) + ' / 112' , True, self.GREEN, self.WHITE)
        self.blit['surfaces'][6] = self.signal_str

    def set_headset(self):
        if self.headset:
            self.blit['surfaces'][1] = self.off
            self.headset = False
            self.fona.transmit('AT+CHFA=1')
        else:
            self.blit['surfaces'][1] = self.on
            self.headset = True
            self.fona.transmit('AT+CHFA=0')

    def volume_down(self):
        self.volume = self.volume - 1
        if self.volume < 0:
            self.volume = 0
        print(self.volume)
        self.fona.transmit('AT+FMVOLUME=' + str(self.volume))
        time.sleep(0.5)
        self.vol = self.font.render(str(self.volume) , True, self.GREEN, self.WHITE)
        self.blit['surfaces'][5] = self.vol

    def volume_up(self):
        self.volume = self.volume + 1
        if self.volume > 6:
            self.volume = 6
        print(self.volume)
        self.fona.transmit('AT+FMVOLUME=' + str(self.volume))
        time.sleep(0.5)
        self.vol = self.font.render(str(self.volume) , True, self.GREEN, self.WHITE)
        self.blit['surfaces'][5] = self.vol

    def channel_down(self):
        if self.radio_on == False: # checking if radio is on, otherwise it will crash if radio is off
           self.set_radio()
        if self.ch_max == 1:
            self.channel_scan()
        self.ch_number = self.ch_number - 1
        if self.ch_number < 1:
            self.ch_number = self.ch_max
        freq = float(self.channels[self.ch_number - 1])
        freq = freq/10
        self.freq = self.font.render(str(self.ch_number) + ': ' + str(freq) + 'MHz' , True, self.GREEN, self.WHITE)
        self.blit['surfaces'][3] = self.freq
        self.fona.transmit('AT+FMFREQ=' + self.channels[self.ch_number - 1])
        self.signal = self.fona.transmit('AT+FMSIGNAL=' + self.channels[self.ch_number - 1])
        self.signal = self.signal[1].split(':')
        print(self.signal)
        self.signal_str = self.font.render(str(self.signal[2]) + ' / 112' , True, self.GREEN, self.WHITE)
        self.blit['surfaces'][6] = self.signal_str

    def channel_up(self):
        if self.radio_on == False: # checking if radio is on, otherwise it will crash if radio is off
           self.set_radio()
        if self.ch_max == 1:
            self.channel_scan()
        self.ch_number = self.ch_number + 1
        if self.ch_number > self.ch_max:
            self.ch_number = 1
        freq = float(self.channels[self.ch_number - 1])
        freq = freq/10
        self.freq = self.font.render(str(self.ch_number) + ': ' + str(freq) + 'MHz' , True, self.GREEN, self.WHITE)
        self.blit['surfaces'][3] = self.freq
        self.fona.transmit('AT+FMFREQ=' + self.channels[self.ch_number - 1])
        self.signal = self.fona.transmit('AT+FMSIGNAL=' + self.channels[self.ch_number - 1])
        self.signal = self.signal[1].split(':')
        print(self.signal)
        self.signal_str = self.font.render(str(self.signal[2]) + ' / 112' , True, self.GREEN, self.WHITE)
        self.blit['surfaces'][6] = self.signal_str

    def channel_scan(self):
        if self.radio_on == False: # checking if radio is on, otherwise it will crash if radio is off
           self.set_radio()
        self.chlist = str(self.fona.transmit('AT+FMSCAN'))
        time.sleep(15)
        print self.chlist
        ch_max = len(self.chlist)
        print(ch_max)
        if ch_max == 13:  # need it since it usually does not work the fist time when starting FMSCAN, alsways have to do it twice, dont ask me why
            self.chlist = str(self.fona.transmit('AT+FMSCAN'))
            time.sleep(15)
            print self.chlist
            ch_max = len(self.chlist)

        self.chlist = self.chlist.replace('[','')
        self.chlist = self.chlist.replace(']','')
        self.chlist = self.chlist.replace('\'\'','')
        self.chlist = self.chlist.replace(' ,','')
        self.chlist = self.chlist.replace('\'','')
        self.chlist = self.chlist.replace(' ','')
        #print self.chlist
        self.channels=self.chlist.split(',')
        #print(channels)
        self.ch_max = len(self.channels)-3
        #print('ch_max:')
        #print(ch_max)
        del(self.channels[0])
        del(self.channels[self.ch_max])
        del(self.channels[self.ch_max])
        print('channels list:')
        print(self.channels)
        self.ch_max = len(self.channels)
        print('number of channels:')
        print(self.ch_max)
        self.no_of_ch = self.font.render(str(self.ch_max) , True, self.GREEN, self.WHITE)
        self.blit['surfaces'][4] = self.no_of_ch

        #channel_log = open('/home/pi/tyos/logs/channel.log', 'w')
        #channel_log.write(str(channels))
        #channel_log.close()
