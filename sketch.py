#IMPORTS
import RPi.GPIO as gpio
import picamera
import time
import os
import PIL.Image
import pygame
import cups


from threading import Thread
from pygame.locals import *
from time import sleep
from PIL import Image

#initialise global variables
gpio.setmode(gpio.BCM) #Set GPIO to BCM Layout
LEDon = False #LED Flashing Control
timepulse = 999 #Pulse Rate of LED
closeme = True #Loop Control Variable
Numeral = "" #Numeral is the number display
Message = "" #Message is a fullscreen message
SmallMessage = "" #SmallMessage is a lower banner message
TotalImageCount = 1 #Counter for Display and to monitor paper usage
PhotosPerCart = 16 #Selphy takes 16 sheets per tray
dispx = 1440
dispy = dispx/4*3


#pygame.mixer.pre_init(44100, -16, 1, 1024*3) #PreInit Music, plays faster
#pygame.init() #Initialise pygame
screen = pygame.display.set_mode((dispx,dispy), pygame.FULLSCREEN) #Full screen, px size set by displayx/y
background = pygame.Surface(screen.get_size()) #Create the background object
background = background.convert() #Convert it to a background

#UpdateDisplay - Thread to update the display, neat generic procedure
def UpdateDisplay():
   #init global variables from main thread
   global Numeral
   global Message
   global SmallMessage
   global TotalImageCount
   global screen
   global background
   global pygame

   SmallText = "Matt Cam" #Default Small Message Text   
   if(TotalImageCount >= (PhotosPerCart - 2)): #Low Paper Warning at 2 images less
      SmallText = "Paper Running Low!..."
   if(TotalImageCount >= PhotosPerCart): #Paper out warning when over Photos per cart
      SmallMessage = "Paper Out!..."
      TotalImageCount = 0
   background.fill(pygame.Color("black")) #black background
   smallfont = pygame.font.Font(None, 50) #Small font for banner message
   SmallText = smallfont.render(SmallText,1, (255,0,0))
   background.blit(SmallText,(10,445)) #Write the small text
   SmallText = smallfont.render('TotalImageCount'+"/"+'PhotosPerCart',1, (255,0,0))
   background.blit(SmallText,(710,445)) #Write the image counter

   if(Message != ""): #If the big message exists write it
      font = pygame.font.Font(None, 180)
      text = font.render(Message, 1, (255,0,0))
      textpos = text.get_rect()
      textpos.centerx = background.get_rect().centerx
      textpos.centery = background.get_rect().centery
      background.blit(text, textpos)
   elif(Numeral != ""): # Else if the number exists display it
      font = pygame.font.Font(None, 800)
      text = font.render(Numeral, 1, (255,0,0))
      textpos = text.get_rect()
      textpos.centerx = background.get_rect().centerx
      textpos.centery = background.get_rect().centery
      background.blit(text, textpos)

   screen.blit(background, (0,0))
   pygame.draw.rect(screen,pygame.Color("red"),(10,10,dispx-20,dispy-30),2) #Draw the red outer box
   pygame.display.flip()
   
   return

#Initialise the camera object
camera = picamera.PiCamera()
#Transparency allows pigame to shine through
camera.preview_alpha = 120
camera.vflip = True
camera.hflip = True
#camera.rotation = 180
#camera.brightness = 45
#camera.exposure_compensation = 6
camera.contrast = 3
camera.resolution = (dispx,dispy)
#Start the preview
camera.preview_window = (0,0,0,0)
camera.start_preview()
UpdateDisplay()
time.sleep(5)
camera.capture('/home/pi/image.jpg')
#Open a connection to cups
conn = cups.Connection()
#get a list of printers
printers = conn.getPrinters()
#select printer 0, print
printer_name = printers.keys()[0]
conn.enablePrinter(printer_name)
#conn.printFile(printer_name,'/home/pi/image.jpg',"PhotoBooth",{})
camera.stop_preview()
camera.close()
pygame.quit()
