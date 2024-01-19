# Python 3.9
# Made by: Fortbonnitar
# This works as a bridge between Unreal Engine and Python by allowing the exchanging of data through a local TCP socket connection.


# # # # # # # # # # # # # # # # # ## # # # # # # # # # # # # # # # # ################                                 ##############        ########################
# XXX XXX XXX XXX XXX XXX XXX XXX ## XXX XXX XXX XXX XXX XXX XXX XXX ################         ############            ################      ########################
# XXX XXX# # # # # # # # #XXX XXX ## XXX XXX# # # # # # # # #XXX XXX ###                    ####        ####          ###           ###                ###
# XXX #         ###         # XXX ## XXX #         ###         # XXX ###                  ###              ###        ###            ###               ###
# XXX #       ### ###       # XXX ## XXX #       ### ###       # XXX ###                ###                  ###      ###            ###               ###
# XXX #      ###   ###      # XXX ## XXX #      ###   ###      # XXX ############      ###                    ###     ###           ###                ###
# XXX #     ###  X  ###     # XXX ## XXX #     ###  X  ###     # XXX ############      ###                    ###     ###         ###                  ###
# XXX #      ###   ###      # XXX ## XXX #      ###   ###      # XXX ###               ###                    ###     #############                    ###
# XXX #       ### ###       # XXX ## XXX #       ### ###       # XXX ###                ###                  ###      ###         ###                  ###
# XXX #         ###         # XXX ## XXX #         ###         # XXX ###                 ###                ###       ###           ###                ###
# XXX XXX# # # # # # # # #XXX XXX ## XXX XXX# # # # # # # # #XXX XXX ###                  ###              ###        ###             ###              ###
# XXX XXX XXX XXX XXX XXX XXX XXX ## XXX XXX XXX XXX XXX XXX XXX XXX ###                   ###            ###         ###              ###             ###
# # # # # # # # # # # # # # # # # ## # # # # # # # # # # # # # # # # ###                     ##############           ###               ###            ###
#################################
#  |_|_|_|_|_|_|_|_|_|_|_|_|_|  #                  #####################################################################################################
#  | | | | | | | | | | | | | |  #
#################################


print("""

Developed by Fortbonnitar

####   #    # #   # # # # # 
#     # #   #  #      #
##   #   #  ###       #
#     # #   #  #      #
#      #    #   #     #
# # # # # # # # # # # # # # 
""")

import socket
import random
import cv2
import numpy as np
import json



##########################################################################################
# Set this script as a TCP-Server and create the socket and listen for Unreal connection
###########################################################################################

def map_value(value, in_min, in_max, out_min, out_max):
    return np.interp(value, [in_min, in_max], [out_min, out_max])

class TCP:
    def __init__(self, ip_adress: str = '127.0.0.1', port: int = 8000):
        self.running = True
        self.ip_adress = ip_adress
        self.port = port
        self.debug = True
        self.directions = ['up', 'right', 'down', 'left']
        self.out_data = ''
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Create a TCP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the server socket to a specific IP address and port
        self.server_address = (self.ip_adress, self.port)
        self.server_socket.bind(self.server_address)

        self.cap = cv2.VideoCapture(0)
        print(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        print(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def listen(self):
        # Listen for incoming connections
        self.server_socket.listen(1)
        print("Server started. Waiting for connections...")

        # Accept a client connection
        self.client_socket, self.client_address = self.server_socket.accept()
        print(f"Client connected: {self.client_address}")

        ##############################################################################
        # After Connection established successfully, if data recieved set as variable
        ###############################################################################

    def get_incoming(self):
        prev_data = '001:center:0:0:0'
        # Inicjalizuj zmienne do przechowywania pozycji twarzy
        face_x = 0
        face_y = 0
        face_radius = 0
        # Main Loop
        while self.running:
            try:
                # Odczyt obrazu z kamery
                ret, frame = self.cap.read()
                if not ret:
                    continue

                # Przykład: Wykrywanie twarzy
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

                for (x, y, w, h) in faces:
                    # Oblicz środek wykrytej twarzy
                    face_x = x + w // 2
                    face_y = y + h // 2

                    # Rysuj punkt na środku twarzy
                    face_radius = max(w, h) // 2
                    cv2.circle(frame, (face_x, face_y), face_radius, (0, 255, 0), -1)

                if face_x == 0 or face_y == 0:
                    self.send_data(prev_data)
                else:
                    # Ustal kierunek kamery na podstawie pozycji twarzy
                    if face_x < frame.shape[1] / 3:
                        self.out_data = "right"
                    elif face_x > 2 * frame.shape[1] / 3:
                        self.out_data = "left"
                    elif face_y < frame.shape[0] / 3:
                        self.out_data = "up"
                    elif face_y > 2 * frame.shape[0] / 3:
                        self.out_data = "down"
                    else:
                        self.out_data = "center"  # Twarz jest w centrum kadru

                #self.send_data(f'001:{self.out_data}')
                #print(f'001:{self.out_data}')
                yaw = map_value(face_x, 20, 620, -20, 20)
                pitch = map_value(face_y, 20, 460, -20, 20)
                fov = map_value(face_radius, 30, 100, 55, 80)
                x = map_value(yaw, -20, 20, 50, -50)
                y = map_value(pitch, -20, 20, 100, 0)
                prev_data = {
                    "pitch": pitch,
                    "yaw": yaw,
                    "fov": fov,
                    "x": x,
                    "y": y
                }
                json_data = json.dumps(prev_data)

                self.send_data(json_data)
                #print(json_data)


                # Display the frame with the central point
                cv2.imshow('Face Detection', frame)

            except Exception as e:
                print(e)

                # Break the loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.cap.release()
        cv2.destroyAllWindows()

    def send_data(self, data_string, encoding='utf-8'):
        # Converting the sending data from string to bytes
        reply_data = bytes(data_string, encoding)

        # Sending back to Unreal Engine
        send = self.client_socket.send(reply_data)


server = TCP()
server.listen()
server.get_incoming()
