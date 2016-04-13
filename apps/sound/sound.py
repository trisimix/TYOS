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

        self.menu = pygame.image.load('/home/pi/tyos/apps/sound/menu.png')
        self.menu_rect = self.menu.get_rect()
        self.font = pygame.font.Font('/home/pi/tyos/fonts/arial.ttf', 28)

        self.off = self.font.render('OFF', True, self.RED, self.WHITE)
        self.on = self.font.render('ON', True, self.GREEN, self.WHITE)

        # read values from fona for init
        # same as above just read from fona not form conf
        self.chfa = self.fona.transmit('AT+CHFA?')
        self.chfa = self.chfa[1].split(':')
        self.chfa = int(self.chfa[1])

        # Ringtone
        self.rtone = self.fona.transmit('AT+CALS?')
        self.rtone = self.rtone[1].split(':')
        self.rtone = self.rtone[1].split(',')
        self.rtone = int(self.rtone[0])
        self.rtone_set = self.font.render( str(self.rtone), True, self.GREEN, self.WHITE)
        self.rtone_set_rect = self.rtone_set.get_rect()
        self.rtone_set_rect.x = 199
        self.rtone_set_rect.centery = 121

        # Rintone Volume
        self.rlevel = self.fona.transmit('AT+CRSL?')
        self.rlevel = self.rlevel[1].split(':')
        self.rlevel = int(self.rlevel[1])
#        print 'rlevel'
#        print(self.rlevel)
        self.rlevel_set = self.font.render( str(self.rlevel) + '%', True, self.GREEN, self.WHITE)
        self.rlevel_set_rect = self.rlevel_set.get_rect()
        self.rlevel_set_rect.x = 212
        self.rlevel_set_rect.centery = 177

        # Ring Mute on or off
        self.rmute = self.fona.transmit('AT+CALM?')
        self.rmute = self.rmute[1].split(':')
        self.rmute = int(self.rmute[1])
        if self.rmute == 1:
            self.rmute_set = self.on
            self.ringmute = True
        if self.rmute == 0:
            self.rmute_set = self.off
            self.ringmute = False
        self.rmute_set_rect = self.rmute_set.get_rect()
        self.rmute_set_rect.x = 246
        self.rmute_set_rect.centery = 224

        # Mic Gain all channels
        self.micgain = self.fona.transmit('AT+CMIC?')
        self.micgain = self.micgain[1].split(':')
        self.micgain = self.micgain[1].split('),(')
        self.micgain = self.micgain[int(self.chfa)].split(',')
        self.micgain = int(self.micgain[1])
        self.micgain_set = self.font.render( str(float(self.micgain) * 1.5) + 'dB', True, self.GREEN, self.WHITE)
        self.micgain_set_rect = self.micgain_set.get_rect()
        self.micgain_set_rect.x = 190
        self.micgain_set_rect.centery = 272

        # Speaker Volume
        self.volume = self.fona.transmit('AT+CLVL?')
        self.volume = self.volume[1].split(':')
        self.volume = int(self.volume[1])
        self.volume_set = self.font.render( str(self.volume) + '%', True, self.GREEN, self.WHITE)
        self.volume_set_rect = self.volume_set.get_rect()
        self.volume_set_rect.x = 180
        self.volume_set_rect.centery = 320


        #Stuff to follow app protocol
        self.exit = False
        self.blit_one_surface = {'surface':[], 'rects':[]}
        self.blit = {'surfaces':[self.menu, self.rtone_set, self.rlevel_set, self.rmute_set, self.micgain_set, self.volume_set], 'rects':[self.menu_rect, self.rtone_set_rect, self.rlevel_set_rect, self.rmute_set_rect, self.micgain_set_rect, self.volume_set_rect]}


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
        if event.pos[0] > 0 and event.pos[0] < 40:
            if event.pos[1] > 95 and event.pos[1] < 152:
#                print 'ringtone -'
                self.ringtone_down()
        if event.pos[0] > 279 and event.pos[0] < 320:
            if event.pos[1] > 95 and event.pos[1] < 152:
#                print 'ringtone +'
                self.ringtone_up()
        if event.pos[0] > 0 and event.pos[0] < 40:
            if event.pos[1] > 153 and event.pos[1] < 201:
#                print 'ring level -'
                self.ringlevel_down()
        if event.pos[0] > 279 and event.pos[0] < 320:
            if event.pos[1] > 153 and event.pos[1] < 201:
#                print 'ring level +'
                self.ringlevel_up()
        if event.pos[1] > 205 and event.pos[1] < 243:
#            print 'RingMute On Off'
            self.set_ringmute()
        if event.pos[0] > 0 and event.pos[0] < 40:
            if event.pos[1] > 254 and event.pos[1] < 293:
#                print 'MicGain -'
                self.micgain_down()
        if event.pos[0] > 279 and event.pos[0] < 320:
            if event.pos[1] > 254 and event.pos[1] < 293:
#                print 'Mic Gain +'
                self.micgain_up()
        if event.pos[0] > 0 and event.pos[0] < 40:
            if event.pos[1] > 303 and event.pos[1] < 342:
#                print 'Volume -'
                self.volume_down()
        if event.pos[0] > 279 and event.pos[0] < 320:
            if event.pos[1] > 303 and event.pos[1] < 342:
#                print 'Volume +'
                self.volume_up()
#        if event.pos[1] > 347 and event.pos[1] < 384:
#            print 'Vibration On Off'
#        if event.pos[0] > 0 and event.pos[0] < 40:
#            if event.pos[1] > 395 and event.pos[1] < 431:
#                print 'Buzzer Freq -'
#        if event.pos[0] > 279 and event.pos[0] < 320:
#            if event.pos[1] > 395 and event.pos[1] < 431:
#                print 'Buzzer Freq +'
        if event.pos[1] > 444 and event.pos[1] < 476:
            self.exit = True

    def on_first_run(self):
        self.exit = False

    def ringtone_down(self):
        self.rtone = self.rtone -1
        if self.rtone < 0:
            self.rtone = 19
#        print(self.rtone)
        self.fona.transmit('AT+CALS=' + str(self.rtone) + ',1')
        self.rtone_set = self.font.render( str(self.rtone), True, self.GREEN, self.WHITE)
        self.blit['surfaces'][1] = self.rtone_set
        time.sleep(1.5)
        self.fona.transmit('AT+CALS=' + str(self.rtone) + ',0')

    def ringtone_up(self):
        self.rtone = self.rtone +1
        if self.rtone > 19:
            self.rtone = 0
#        print(self.rtone)
        self.fona.transmit('AT+CALS=' + str(self.rtone) + ',1')
        self.rtone_set = self.font.render( str(self.rtone), True, self.GREEN, self.WHITE)
        self.blit['surfaces'][1] = self.rtone_set
        time.sleep(1.5)
        self.fona.transmit('AT+CALS=' + str(self.rtone) + ',0')

    def ringlevel_down(self):
        self.rlevel = self.rlevel -10
        if self.rlevel < 0:
            self.rlevel = 0
#        print(self.rlevel)
        self.fona.transmit('AT+CRSL=' + str(self.rlevel))
        self.rlevel_set = self.font.render( str(self.rlevel) + '%', True, self.GREEN, self.WHITE)
        self.blit['surfaces'][2] = self.rlevel_set
        time.sleep(0.25)
        self.fona.transmit('AT+CALS=' + str(self.rtone) + ',1')
        time.sleep(1)
        self.fona.transmit('AT+CALS=' + str(self.rtone) + ',0')

    def ringlevel_up(self):
        self.rlevel = self.rlevel +10
        if self.rlevel > 100:
            self.rlevel = 100
#        print(self.rlevel)
        self.fona.transmit('AT+CRSL=' + str(self.rlevel))
        self.rlevel_set = self.font.render( str(self.rlevel) + '%', True, self.GREEN, self.WHITE)
        self.blit['surfaces'][2] = self.rlevel_set
        time.sleep(0.25)
        self.fona.transmit('AT+CALS=' + str(self.rtone) + ',1')
        time.sleep(1)
        self.fona.transmit('AT+CALS=' + str(self.rtone) + ',0')

    def set_ringmute(self):
        if self.ringmute:
            self.blit['surfaces'][3] = self.off
            self.ringmute = False
            self.fona.transmit('AT+CALM=0')
        else:
            self.blit['surfaces'][3] = self.on
            self.ringmute = True
            self.fona.transmit('AT+CALM=1')

    def micgain_down(self):
        self.micgain = self.micgain -1
        if self.micgain < 0:
            self.micgain = 0
#        print(self.micgain)
        self.micgain_set = self.font.render( str(float(self.micgain) * 1.5) + 'dB', True, self.GREEN, self.WHITE)
        self.blit['surfaces'][4] = self.micgain_set
        self.fona.transmit('AT+CMIC=' + str(self.chfa) + str(self.micgain))

    def micgain_up(self):
        self.micgain = self.micgain +1
        if self.micgain > 15:
            self.micgain = 15
#        print(self.micgain)
        self.micgain_set = self.font.render( str(float(self.micgain) * 1.5) + 'dB', True, self.GREEN, self.WHITE)
        self.blit['surfaces'][4] = self.micgain_set
        self.fona.transmit('AT+CMIC=' + str(self.chfa) + str(self.micgain))

    def volume_down(self):
        self.volume = self.volume -10
        if self.volume < 0:
            self.volume = 0
#        print(self.volume)
        self.volume_set = self.font.render( str(self.volume) + '%', True, self.GREEN, self.WHITE)
        self.blit['surfaces'][5] = self.volume_set
        self.fona.transmit('AT+CLVL=' + str(self.volume))

    def volume_up(self):
        self.volume = self.volume +10
        if self.volume > 100:
            self.volume = 100
#        print(self.volume)
        self.volume_set = self.font.render( str(self.volume) + '%', True, self.GREEN, self.WHITE)
        self.blit['surfaces'][5] = self.volume_set
        self.fona.transmit('AT+CLVL=' + str(self.volume))
