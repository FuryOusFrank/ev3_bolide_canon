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

moteur_a = Motor(Port.A) # propulsion (manette et bolide)
moteur_d = Motor(Port.D) # direction (manette et bolide)

# Variables

server = "prof1" # Changer avec le bon nom pour la brique qui est dans le bolide

# Write your program here.
ev3.speaker.beep()

ev3.screen.draw_text(0, 10,"--- Bolide EV3 ---")
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

    ev3.screen.draw_text(0,0, "--- Bolide EV3 ---", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0,30, "Robot", text_color=Color.BLACK, background_color=None)

    # Initialisation de la direction

    ev3.screen.draw_text(0,90, "Initialisation...", text_color=Color.BLACK, background_color=None)

    moteur_d.run_until_stalled(100, then=Stop.COAST, duty_limit=40) # Envoyer les roues à gauche complètement
    moteur_d.reset_angle(0)
    moteur_d.run_until_stalled(-100, then=Stop.COAST, duty_limit=40) # Envoyer les roues à droite complètement
    max_angle_d = moteur_d.angle() # Mesurer l'angle maximum à partir de la gauche
    #print("Angle D maximal = " + str(max_angle_d))
    mid_angle_d = max_angle_d/2 # Milieu
    moteur_d.run_angle(100, -mid_angle_d, then=Stop.HOLD, wait=True) # Ramener les roues au milieu

    moteur_d.reset_angle(0)

    minus_mid_angle_d = abs(mid_angle_d)

    print(minus_mid_angle_d)

    ev3.screen.clear()

    # Connexion à la manette
    ev3.screen.draw_text(0,0, "--- Bolide EV3 ---", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0,30, "Robot", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0,90, "En attente de connexion...", text_color=Color.BLACK, background_color=None)

    server.wait_for_connection()
    ev3.screen.clear()

    ev3.screen.draw_text(0,0, "--- Bolide EV3 ---", text_color=Color.BLACK, background_color=None)
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

            print("Vecteur = " + msg)

            vecteur = msg.split(",")

            direction = int(vecteur[0])
            vitesse = int(vecteur[1])

            moteur_a.run(vitesse*-10)
        
            ev3.screen.print(str(int(minus_mid_angle_d)) + " / " + str(direction) + " / " + str(int(mid_angle_d)))

            if(minus_mid_angle_d > direction > mid_angle_d) :
                moteur_d.run_target(100, direction, then=Stop.HOLD, wait=False)

        
        

def modeManette():
    ev3.screen.clear()
    
    client = BluetoothMailboxClient()
    mbox = TextMailbox("ok", client)

    moteur_a.reset_angle(0)

    # Connexion au robot
    ev3.screen.draw_text(0,0, "--- Véhicule ev3 téléguidé ---", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0,30, "Télécommande", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0,90, "En attente de connexion...", text_color=Color.BLACK, background_color=None)

    client.connect(server)

    ev3.screen.clear()

    ev3.screen.draw_text(0,0, "--- Véhicule ev3 téléguidé ---", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0,30, "Télécommande", text_color=Color.BLACK, background_color=None)
    ev3.screen.draw_text(0,90, "Connecté!", text_color=Color.BLACK, background_color=None)

    vitesse = 0
    angle = 0

    vecteur = str(vitesse) + "," + str(angle)

    mbox.send(vecteur)

    while (True):

        speed_a = (int(moteur_a.angle()/4)) # Au lieu de 10, donc plus de sensibilité
        angle_d = int(moteur_d.angle()/2)

        newVecteur = str(angle_d) + "," + str(speed_a)

        if newVecteur != vecteur :
            vecteur = newVecteur
            mbox.send(vecteur)
            sleep(0.02) # On dirait que trop de changements en même temps boguent la mbox. Le délai permet d'éviter la "congestion"?

# Sélectionner le mode

while (True) :
    if Button.LEFT in ev3.buttons.pressed():
        modeRobot()
        break
    elif Button.RIGHT in ev3.buttons.pressed():
        modeManette()
        break
