# USAGE
# python object_movement.py --video object_tracking_example.mp4
# python object_movement.py

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
# from serial import *
import threading
import serial
import struct
import shelvE
import win32api as win32

achou_o_final = False
#data = serial.Serial('com6', 5000, timeout=1) #TODO
saved = 0
contador = 0

try:
    db = shelvE.open('dados.db')
    tuplaMax = (int(db.get('h_max')), int(db.get('s_max')), int(db.get('v_max')))
    tuplaMin = (int(db.get('h_min')), int(db.get('s_min')), int(db.get('v_min')))
    db.close()
    print(tuplaMin, tuplaMax)
except:
    text = 'É necessaria calibrar as cores antes, inicie o simulador e faça a configuração (Cor Bola).'
    win32.MessageBeep(1)
    win32.MessageBox(0, text, 'Erro')
    tuplaMin = (47, 63, 96) #TODO COMENTAR ESSAS LINHAS PARA COR <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    tuplaMax = (98, 255, 255)


def sendArduino(raio, angulo):
    global data
    global saved
    global contador
    #print("Raio: {:.0f}".format(raio))
    #contador +=1

    #if contador % 10 == 0:
    #    teste = 1
    #else:
    #    teste = 0

    if raio > 0:
        #print("Defender, ângulo: " + str(anguloRobo))
        #sleep(1)

        global achou_o_final
        achou_o_final = True

        # **MUDAR COM4 PARA A ENTRADA DO COMPUTADOR (GERALMENTE COM3), CHECAR PELO WINDOWS *

        # loop infinito

        #pos = int(input("Enter a number: "))  # Pede info para user, digitar 1 ou 0
        pos = int(anguloRobo)
        #print("Movimentando o motor com o angulo de {:.0f}".format(angulo))

        if pos > 90:
            add_value = pos - 90
            pos = 90 + add_value
            #pos = 180 - pos


        elif pos < 90:
            subt_value = 90 - pos
            pos = 90 - subt_value
            #pos = 180 - pos

        #print('Pos: {}   <<<<'.format(pos))

        try:
            banco = shelvE.open('dados.db')
            banco['angulo'] = anguloRobo
            banco['xreal'] = '{:.0f}'.format(xReal)
            banco['yreal'] = '{:.0f}'.format(yReal)
            banco['x'] = '{:.0f}'.format(x)
            banco['y'] = '{:.0f}'.format(y)
            banco['raio'] = '{:.0f}'.format(raio)
            sleep(0.05)
            banco.close()
        except:
            #print('Evitei erro do banco de dados')
            pass
            #print('Enviado {}º'.format(anguloRobo))
            #data.write(struct.pack('>B', pos))  # passa a info para o arduino pelo serial #TODO

    else:

        pos = 90

        #data.write(struct.pack('>B', pos)) #TODO
        #from time import sleep
        #sleep(2)



def receiving(ser):
   while True:
       leitura = ser.read(ser.inWaiting())

       leituraClean = leitura.decode("utf-8")

       #if leituraClean != "":
       #    print("Recebimento na Porta Serial: {}".format(leituraClean))


anguloRoboZerado = 90
anguloRobo = anguloRoboZerado
raioAtual = 0
raioMinimo = 20

def gravar():
   if raioAtual > 0 and raioAtual < 6:
       #ser.write(anguloRobo)
       sleep(1)
   else:
       ser.write(str(anguloRoboZerado).encode())


def set_interval(func, sec):
   def func_wrapper():
       set_interval(func, sec)
       func()

   t = threading.Timer(sec, func_wrapper)
   t.start()

   return t


"""
if __name__ == '__main__':
  ser = Serial(
     port="COM19",
     baudrate=9600,
     bytesize=EIGHTBITS,
     parity=PARITY_NONE,
     stopbits=STOPBITS_ONE,
     timeout=0.1,
     xonxoff=0,
     rtscts=0,
     interCharTimeout=None
  )

  threading.Thread(target=receiving, args=(ser,)).start()

  set_interval(gravar, 0.5)

"""

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the (optional) video file")
#ap.add_argument("-v", "--video", help='C:\\Users\\Daniel Shibata Ema\\Desktop\\Goleiro testes\\teste.mp4')
ap.add_argument("-b", "--buffer", type=int, default=32, help="max buffer size")
args = vars(ap.parse_args())

xMax = 600
yMax = 450

# define the lower and upper boundaries of the "green"
# ball in the HSV color space
greenLower = (tuplaMin)
greenUpper = (tuplaMax)



# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
pts = deque(maxlen=args["buffer"])
counter = 0
(dX, dY) = (0, 0)
direction = ""

testarVideo = True

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
#if not testarVideo:
   camera = cv2.VideoCapture(0)

# otherwise, grab a reference to the video file
else:
   camera = cv2.VideoCapture(args["video"])

# keep looping
while True:
   if achou_o_final == False:


       # grab the current frame
       (grabbed, frame) = camera.read()

       # if we are viewing a video and we did not grab a frame,
       # then we have reached the end of the video
       if args.get("video") and not grabbed:
           break

       # resize the frame, blur it, and convert it to the HSV
       # color space
       frame = imutils.resize(frame, width=600)
       # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
       hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

       # construct a mask for the color "green", then perform
       # a series of dilations and erosions to remove any small
       # blobs left in the mask
       mask = cv2.inRange(hsv, greenLower, greenUpper)
       mask = cv2.erode(mask, None, iterations=2)
       mask = cv2.dilate(mask, None, iterations=2)

       # find contours in the mask and initialize the current
       # (x, y) center of the ball
       cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_SIMPLE)[-2]
       center = None

       x = 0
       y = 0

       # only proceed if at least one contour was found
       if len(cnts) > 0:
           # find the largest contour in the mask, then use
           # it to compute the minimum enclosing circle and
           # centroid
           c = max(cnts, key=cv2.contourArea)
           ((x, y), radius) = cv2.minEnclosingCircle(c)
           M = cv2.moments(c)
           center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

           # only proceed if the radius meets a minimum size
           if radius > 5:
               # draw the circle and centroid on the frame,
               # then update the list of tracked points
               cv2.circle(
                   frame,
                   (int(x), int(y)),
                   int(radius),
                   (0, 255, 255),
                   2
               )

               raioAtual = radius

               cv2.circle(frame, center, 5, (0, 0, 255), -1)
               pts.appendleft(center)

       # loop over the set of tracked points
       for i in np.arange(1, len(pts)):
           # if either of the tracked points are None, ignore
           # them
           if pts[i - 1] is None or pts[i] is None:
               continue

           # check to see if enough points have been accumulated in
           # the buffer
           if len(pts) >= 10:
               if counter >= 10 and i == 1 and pts[-10] is not None:
                   # compute the difference between the x and y
                   # coordinates and re-initialize the direction
                   # text variables
                   dX = pts[-10][0] - pts[i][0]
                   dY = pts[-10][1] - pts[i][1]
                   (dirX, dirY) = ("", "")

                   # ensure there is significant movement in the
                   # x-direction
                   if np.abs(dX) > 20:
                       dirX = "East" if np.sign(dX) == 1 else "West"

                   # ensure there is significant movement in the
                   # y-direction
                   if np.abs(dY) > 20:
                       dirY = "North" if np.sign(dY) == 1 else "South"

                   # handle when both directions are non-empty
                   if dirX != "" and dirY != "":
                       direction = "{}-{}".format(dirY, dirX)

                   # otherwise, only one direction is non-empty
                   else:
                       direction = dirX if dirX != "" else dirY

           # otherwise, compute the thickness of the line and
           # draw the connecting lines
           thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
           cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

       # show the movement deltas and the direction of movement on
       # the frame
       cv2.putText(
           frame,
           direction,
           (10, 30),
           cv2.FONT_HERSHEY_SIMPLEX,
           0.65,
           (0, 0, 255),
           3
       )
       xCoef = xMax / 2
       yCoef = yMax

       xCoef = 321
       yCoef = 276

       #LINHA PARA DIVIDIR A TELA NO MEIO X Y
       cv2.line(frame, (0, yCoef), (600, yCoef), (255, 0, 0))
       cv2.line(frame, (xCoef, 0), (xCoef, yMax), (255, 0, 0))

       xReal = int(x - (xCoef))
       yReal = int(yCoef - y)

       xR = int(x)
       yR = int(y)

       cv2.putText(
           frame,
           "x: {}, y: {}".format(x, y),
           (10, frame.shape[0] - 50),
           cv2.FONT_HERSHEY_SIMPLEX,
           0.35,
           (0, 0, 255),
           1
       )


       cv2.putText(
           frame,
           "xReal: {}, yReal: {}".format(xReal, yReal),
           (10, frame.shape[0] - 10),
           cv2.FONT_HERSHEY_SIMPLEX,
           0.35,
           (0, 0, 255),
           1
       )


       def angle_between(p1, p2):
           ang1 = np.arctan2(*p1[::-1])
           ang2 = np.arctan2(*p2[::-1])
           return np.rad2deg((ang1 - ang2) % (2 * np.pi))


       ponto1 = (0, 0)
       ponto2 = (xReal, yReal)
       #ponto2 = (46, 160)

       angulo = angle_between(ponto1, ponto2) - 180
       #print(angle_between(ponto1, ponto2))
       #print(angulo)

       anguloRobo = str(int(angulo)).encode()


       cv2.putText(
           frame,
           "Angulo: {}".format(anguloRobo),
           (200, frame.shape[0] - 10),
           cv2.FONT_HERSHEY_SIMPLEX,
           0.35,
           (0, 0, 255),
           1
       )

       cv2.putText(
           frame,
           "Raio: {}".format(raioAtual),
           (300, frame.shape[0] - 10),
           cv2.FONT_HERSHEY_SIMPLEX,
           0.35,
           (0, 0, 255),
           1
       )

       from time import sleep
       #sleep(0.5)
       sendArduino(raioAtual, angulo)

       # show the frame to our screen and increment the frame counter
       cv2.imshow("Frame", frame)
       key = cv2.waitKey(1) & 0xFF
       counter += 1

       # if the 'q' key is pressed, stop the loop
       if key == ord("q"):

           break

   else:

       achou_o_final = False

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()


