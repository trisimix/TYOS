#settings App
#copyright (c) 2015 Tyler Spadgenske
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
        self.BLACK = (  0,  0,  0)

        self.menu = pygame.image.load('/home/pi/tyos/apps/settings/menu.png')
        self.menu_rect = self.menu.get_rect()

        self.font = pygame.font.Font('/home/pi/tyos/fonts/arial.ttf', 28)

        self.off = self.font.render('OFF', True, self.RED, self.WHITE)
        # fona info Text
        self.model = self.fona.transmit('ATI')

        self.fona_power = self.font.render( str(self.model[1]), True, self.GREEN, self.WHITE)
        self.fona_power_rect = self.off.get_rect()
        self.fona_power_rect.x = 102
        self.fona_power_rect.centery = 223
        self.on = self.font.render('ON', True, self.GREEN, self.WHITE)
        self.rect = self.off.get_rect()
        self.rect.centerx = 280
        self.rect.y = 158

        # Timeformat
        self.time_24hrs = self.font.render('24hrs', True, self.GREEN, self.WHITE)
        self.time_12hrs = self.font.render('12hrs', True, self.GREEN, self.WHITE)
        self.time_rect = self.off.get_rect()
        self.time_rect.centery = 318
        self.time_rect.x = 210

        #restart notice
        self.boot_set = self.font.render( '', True, self.RED, self.WHITE)
        self.boot_set_rect = self.boot_set.get_rect()
        self.boot_set_rect.centery = 366
        self.boot_set_rect.x = 55

        #Stuff to follow app protocol
        self.exit = False
        self.blit_one_surface = {'surface':[], 'rects':[]}
        self.blit = {'surfaces':[self.menu, self.fona_power, self.off, self.time_24hrs, self.boot_set], 'rects':[self.menu_rect, self.fona_power_rect, self.rect, self.time_rect, self.boot_set_rect]}

        #get timeformat
        self.get_time_mode()

        #Set audio mode text
        if self.headset:
            self.blit['surfaces'][2] = self.on
        else:
            self.blit['surfaces'][2] = self.off

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

    def get_time_mode(self):
        time_config = open('/home/pi/tyos/configure/settings.conf', 'r')
        file = time_config.readlines()

        for i in range(0, len(file)):#Parse file
            if file[i][0] == '#':
                pass
                #Do Nothing. Line is comment
            else:
                file[i] = file[i].rstrip()
                if 'time24hrs' in file[i]: #Extract timeformat 24hrs: 1=True in, 0=False (12hrs)
                    mode = file[i]

        mode = mode.split('=')
        self.mode = int(mode[1])

        if self.mode == 0:
            self.timeformat = False
            self.blit['surfaces'][3] = self.time_12hrs
        else:
            self.timeformat = True
            self.blit['surfaces'][3] = self.time_24hrs

    def run_app(self):
        pass

    def get_events(self, event):
        if event.pos[1] > 95 and event.pos[1] < 152:
            self.delete_sms()
        if event.pos[1] > 153 and event.pos[1] < 201:
            self.set_headset()
        if event.pos[1] > 254 and event.pos[1] < 293:
            print 'Vibration On Off'
        if event.pos[1] > 303 and event.pos[1] < 342:
            self.set_timeformat()
        if event.pos[1] > 444 and event.pos[1] < 476:
            self.exit = True

    def on_first_run(self):
        self.exit = False

    def delete_sms(self):
        self.fona.transmit('AT+CMGD=1,4')
        self.exit = True

    def set_headset(self):
        if self.headset:
            self.blit['surfaces'][2] = self.off
            self.headset = False
            self.fona.transmit('AT+CHFA=1')
        else:
            self.blit['surfaces'][2] = self.on
            self.headset = True
            self.fona.transmit('AT+CHFA=0')

    def set_timeformat(self):
        if self.timeformat:
            self.blit['surfaces'][3] = self.time_12hrs
            self.timeformat = False
            USE_RAW_TIME = 'time24hrs=0\n'
        else:
            self.blit['surfaces'][3] = self.time_24hrs
            self.timeformat= True
            USE_RAW_TIME = 'time24hrs=1\n'

        self.conf_file = open('/home/pi/tyos/configure/settings.conf', 'w+')#Create config file and add some lines
        self.conf_file.write('#Timeformat config\n')
        self.conf_file.write(USE_RAW_TIME)
        self.conf_file.close()
        self.boot_set = self.font.render( 'restart to apply', True, self.RED, self.WHITE)
        self.blit['surfaces'][4] = self.boot_set
