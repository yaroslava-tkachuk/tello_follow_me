import cv2
import socket
import threading
import datetime
import time

from haar_cascade_face_detector import HaarCascadeFaceDetector
from fuzzy_logic_controller import FuzzyLogicController


class Tello():

    def __init__(self):
        # Communication
        # IPs
        self.tello_ip = "192.168.10.1"
        self.mac_ip = "0.0.0.0"
        # Ports
        self.comm_send_port = 8889
        self.tello_state_port = 8890
        self.video_receive_port = 11111
        self.comm_receive_port = 9003

        # Sockets
        self.comm_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.comm_sock.bind((self.mac_ip, self.comm_receive_port))
        self.comm_sock.settimeout(1)

        # Face detection
        self.haar_face_detector = HaarCascadeFaceDetector()
        self.frame = None
        self.face_rect = None

        # Movement control
        self.fl_controller = FuzzyLogicController()
        self.x_treshold = 30

        # Threads
        self._comm_handle_running = True
        self._video_receive_running = True
        self.response_received = False

        self.comm_handle_thread = threading.Thread(target=self.comm_handle)
        self.comm_handle_thread.start()

        self.send_command("command")
        self.wait_for_response()
        
        self.send_command("streamon")
        self.wait_for_response()

        self.video_cap = cv2.VideoCapture("udp://@{}:{}".format(self.mac_ip, self.video_receive_port))

        self.video_receive_thread = threading.Thread(target=self.video_receive)
        self.video_receive_thread.start()

        self.send_command("takeoff")
        self.wait_for_response()

    def terminate(self):
        self.terminate_comm_handle()
        self.terminate_video_response()

    def terminate_comm_handle(self):
        self._comm_handle_running = False
        self.comm_sock.close()
        self.comm_handle_thread.join()

    def terminate_video_response(self):
        self._video_receive_running = False
        self.video_cap.release()
        cv2.destroyAllWindows()
        self.video_receive_thread.join()
        
    def comm_handle(self):
        start_time = datetime.datetime.now()
        while self._comm_handle_running:
            try:
                if not self.response_received:
                    resp_msg, client_addr = self.comm_sock.recvfrom(1024)  # read 1024 bytes from UDP socket
                    self.response_received = True
                    print("Tello command response: {}".format(resp_msg.decode(encoding="utf-8")))
                else:
                    time.sleep(1)
                    # Send empty "command" every 5 seconds to keep Tello in SDK mode
                    if (datetime.datetime.now() - start_time).total_seconds() >= 5:
                        self.send_command("command")
                        start_time = datetime.datetime.now()
                    else:
                        if self.face_rect is not None:
                            # Calculate and send control command
                            self.move_horizontally()
            except Exception as e:
                print(e)

    def video_receive(self):
        while self._video_receive_running:
            try:
                frame_res, frame = self.video_cap.read()
                if frame_res:
                    # Resize frame to improve performance
                    height, width, _ = frame.shape
                    frame = cv2.resize(frame, (width//2, height//2))
                    
                    # Detect face
                    detected_face = self.haar_face_detector.detect_face(frame)
                    if detected_face is not None:
                        self.frame, self.face_rect = detected_face
                    else:
                        self.frame = frame
            except Exception as e:
                print(e)

    def send_command(self, comm):
        print("Sending command to Tello: {}".format(comm))

        comm = comm.encode(encoding="utf-8")
        self.comm_sock.sendto(comm, (self.tello_ip, self.comm_send_port))
        self.response_received = False

    def show_video_frame(self):
        if self.frame is not None:
            cv2.imshow("Tello Video Stream", self.frame)
            cv2.waitKey(1)

    def wait_for_response(self):
        while not self.response_received:
            continue

    def move_horizontally(self):
        """
        image width = 480 px
        """
        threshold = 30

        frame_height, frame_width, _ = self.frame.shape
        frame_center_x = frame_width // 2

        face_x, face_y, face_width, face_height = self.face_rect
        face_center_x = face_x + face_width // 2

        center_diff = frame_center_x - face_center_x

        print("frame_center_x: {}, face_center_x: {}, center_diff: {}".format(frame_center_x, face_center_x, center_diff))

        if abs(center_diff) >= threshold:
            turn_degrees = self.fl_controller.calculate_x(abs(center_diff))
            if center_diff > 0:
                direction = "ccw"
            else:
                direction = "cw"
            self.send_command("{} {}".format(direction, turn_degrees))
        self.face_rect = None


if __name__ == "__main__":

    tello = Tello()

    while 1:
        try:
            tello.show_video_frame()
        except Exception:
            tello.terminate()
            print("End of program")




    

