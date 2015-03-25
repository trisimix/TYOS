#Main.py
#Copyright (c) 2015 Tyler Spadgenske
#GPL License
VERSION = '0.1.0'

import pygame, sys, os
from pygame.locals import *
import framebuffer, toolbar

class tyfone():
    def __init__(self):
        self.VERSION = VERSION

        self.scope = framebuffer.pyscope()
        self.toolbar = toolbar.Toolbar()
        pygame.init()

        self.WINDOWWIDTH = 320
        self.WINDOWHIEGHT = 480

        self.surface = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHIEGHT), pygame.FULLSCREEN)

        self.clock = pygame.time.Clock()

        #Colors        R   G   B
        self.BLUE =  (  0,  0,255)
        self.WHITE = (255,255,255)
        self.BLACK = (  0,  0,  0)

        self.surface.fill(self.WHITE)

        self.update = True

        #Setup logo
        self.logo = pygame.image.load('/home/pi/tyos/graphics/logo.png')
        self.logo_rect = self.logo.get_rect()
        self.logo_rect.y = self.surface.get_rect().centery - 50
        self.logo_rect.centerx = self.surface.get_rect().centerx

        #Setup Battery Icon
        self.bat = pygame.image.load('/home/pi/tyos/graphics/bat.png')
        self.bat_rect = self.bat.get_rect()
        self.bat_rect.centery = 15
        self.bat_rect.right = self.WINDOWWIDTH - 10

        #Setup App Toolbar
        self.app_toolbar = pygame.Rect(0, 0, 320, 30)

        #Image Dictionary
        self.images = {'surfaces':[self.logo, self.bat], 'rects':[self.logo_rect, self.bat_rect]}
        #Rectangle Dictionary
        self.rectangles = {'rects':[self.app_toolbar], 'colors':[self.BLACK]}
        #Reception Rectangle dictionary
        self.reception_bars = {'rects':[], 'colors':[]}
        #Battery Left Text
        self.bat_left = {'surface':self.toolbar.bat_left, 'rect':self.toolbar.bat_left_rect}
        
    def home(self):
        #TODO: Remove when toolbar.clock() is done
        self.reception_bars = self.toolbar.check_reception(self.reception_bars)
        self.bat_left = self.toolbar.check_battery(self.bat_left)
        
        while True:
            #handle events and clock
            self.handle_events()
            pygame.display.update()
            self.clock.tick()

            #Update if neccesary
            if self.update:
                self.blit(self.images, self.rectangles, self.reception_bars, self.bat_left)
                self.update = False

    def blit(self, surfaces, rects, reception, bat):
        #Blit all rectangles
        for rect, color in zip(rects['rects'], rects['colors']):
            pygame.draw.rect(self.surface, color, rect)

        #Blit all reception bars
        for rect, color in zip(reception['rects'], reception['colors']):
            pygame.draw.rect(self.surface, color, rect)

        #Blit all images
        for surface, rect in zip(surfaces['surfaces'], surfaces['rects']):
            self.surface.blit(surface, rect)

        #Blit battery Percentage
        self.surface.blit(bat['surface'], bat['rect'])

    def handle_events(self):
        for event in pygame.event.get():
            self.update = True
            if event.type == MOUSEBUTTONDOWN:
                pass
                
                
tyos = tyfone()
try:
    tyos.home()
    
except KeyboardInterrupt:
    print
    print 'Closing TYOS ' + tyos.VERSION
    pygame.quit()
    sys.exit()