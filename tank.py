#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.messaging import BluetoothMailboxServer, TextMailbox, BluetoothMailboxClient
from time import sleep

import threading


# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.


# Create your objects here.
ev3 = EV3Brick()

moteur_a = Motor(Port.A) # propulsion gauche (manette et bolide)
moteur_d = Motor(Port.D) # propulsion droite (manette et bolide)

# Variables

server = "prof1" # Changer avec le bon nom pour la brique qui est dans le bolide

# Write your program here.
ev3.speaker.beep()

ev3.screen.draw_text(0, 10,"--- Tank EV3 ---")
ev3.screen.draw_text(0, 30,"Mode :")
ev3.screen.draw_text(0, 50,"<- robot")
ev3.screen.draw_text(0, 70,"-> manette")


def modeRobot():

    moteur_c = Motor(Port.C) # canon

    senseurUltraSons = UltrasonicSensor(Port.S1) # senseur pour contrôler le canon

    ev3.screen.clear()

    server = BluetoothMailboxServer()
    mbox = TextMailbox("ok", server)

    ev3.speaker.beep()

    ev3.screen.draw_text(0,0, "--- Tank EV3 ---", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0,30, "Robot", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0,90, "En attente de connexion...", text_color=Color.BLACK, background_color=None)

    server.wait_for_connection()
    ev3.screen.clear()

    ev3.screen.draw_text(0,0, "--- Tank EV3 ---", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0,30, "Robot", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0,90, "Connecté!", text_color=Color.BLACK, background_color=None)

    msg = "0,0"
    newMsg = "0,0"

    # boucle principale

    while (True):
        
        if (senseurUltraSons.distance() < 500) :

            print("feu!")
            moteur_c.run(1000)

        else :
            moteur_c.stop()

        newMsg = mbox.read()

        if (newMsg) and (newMsg != msg) :

            msg = newMsg

            print("Vitesses = " + msg)

            vitesses = msg.split(",")

            vitesse_gauche = int(vitesses[0])
            vitesse_droite = int(vitesses[1])

            moteur_a.run(vitesse_gauche*10)
            moteur_b.run(vitesse_droite*10)
        
        

def modeManette():
    ev3.screen.clear()
    
    client = BluetoothMailboxClient()
    mbox = TextMailbox("ok", client)

    moteur_a.reset_angle(0)

    # Connexion au robot
    ev3.screen.draw_text(0,0, "--- Tank EV3 ---", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0,30, "Télécommande", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0,90, "En attente de connexion...", text_color=Color.BLACK, background_color=None)

    client.connect(server)

    ev3.screen.clear()

    ev3.screen.draw_text(0,0, "--- Tank EV3 ---", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0,30, "Télécommande", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0,90, "Connecté!", text_color=Color.BLACK, background_color=None)

    vitesse_gauche = 0
    vitesse_droite = 0

    vitesses = str(vitesse_gauche) + "," + str(vitesse_droite)

    mbox.send(vitesses)

    while (True):

        vitesse_gauche = (int(moteur_a.angle()/4)) # 
        vitesse_droite = (int(moteur_d.angle()/4)) # 

        newVitesses = str(vitesse_gauche) + "," + str(droite)

        if newVitesses != vitesses :
            vitesses = newVitesses
            mbox.send(vitesses)
            sleep(0.02) # On dirait que trop de changements en même temps boguent la mbox. Le délai permet d'éviter la "congestion"?

# Sélectionner le mode

while (True) :
    if Button.LEFT in ev3.buttons.pressed():
        modeRobot()
        break
    elif Button.RIGHT in ev3.buttons.pressed():
        modeManette()
        break
