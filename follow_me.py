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
        self.x_threshold = 30 # 30 px = 5 deg
        self.z_threshold = 76 # 76 px > 20 cm
        self.y_threshold = 28 # 28 > 20 cm
        self.target_face_area = 2500 # approx distance = 80 cm
        self.command_queue = []

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

        self.send_command("up 60")
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
                    resp_msg = self.comm_sock.recvfrom(1024)[0]  # read 1024 bytes from UDP socket
                    self.response_received = True
                    print("Tello command response: {}".format(resp_msg.decode(encoding="utf-8")))
                else:
                    # Send empty "command" every 5 seconds to keep Tello in SDK mode
                    if (datetime.datetime.now() - start_time).total_seconds() >= 5:
                        self.send_command("command")
                        start_time = datetime.datetime.now()
                    else:
                        if self.face_rect is not None:
                            # Calculate and send control commands
                            self.handle_commands()
                        else:
                            time.sleep(1)
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

    def calculate_x_command(self):
        frame_width = self.frame.shape[1]
        frame_center_x = frame_width // 2

        face_x = self.face_rect[0]
        face_width = self.face_rect[2]
        face_center_x = face_x + face_width // 2

        x_center_diff = frame_center_x - face_center_x

        print("frame_center_x: {}, face_center_x: {}, x_center_diff: {}".format(frame_center_x, face_center_x, x_center_diff))

        if abs(x_center_diff) > self.x_threshold:
            turn_degrees = self.fl_controller.calculate_x(abs(x_center_diff))
            if x_center_diff > 0:
                direction = "ccw"
            else:
                direction = "cw"
            self.command_queue.append("{} {}".format(direction, turn_degrees))

    def calculate_z_command(self):
        frame_height = self.frame.shape[0]
        frame_center_z = frame_height // 2

        face_z = self.face_rect[1]
        face_height = self.face_rect[3]
        face_center_z = face_z + face_height // 2

        z_center_diff = frame_center_z - face_center_z

        print("frame_center_z: {}, face_center_z: {}, z_center_diff: {}".format(frame_center_z, face_center_z, z_center_diff))

        if abs(z_center_diff) > self.z_threshold:
            horizontal_distance = self.fl_controller.calculate_z(abs(z_center_diff))
            if z_center_diff > 0:
                direction = "up"
            else:
                direction = "down"
            self.command_queue.append("{} {}".format(direction, horizontal_distance))

    def calculate_y_command(self):
        face_height = self.face_rect[3]

        current_distance = 65 * 80 // face_height

        if current_distance >= 80:
            vertical_distance = current_distance - 80
            direction = "forward"
        else:
            vertical_distance = 80 - current_distance
            direction = "back"
        if vertical_distance > 20:
            self.command_queue.append("{} {}".format(direction, vertical_distance))

        print("target_height: {}, face_height: {}, current_distance: {}".format(50, face_height, current_distance))


        # if self.target_face_area >= face_area:
        #     y_area_diff = self.target_face_area // face_area
        #     direction = "forward"
        # else:
        #     y_area_diff = face_area // self.target_face_area
        #     direction = "back"

        # if y_area_diff > self.y_threshold:
        #     vertical_distance = self.fl_controller.calculate_y(y_area_diff)
        #     self.command_queue.append("{} {}".format(direction, vertical_distance))

        # print("self.target_face_area: {}, face_area: {}, y_area_diff: {}".format(self.target_face_area, face_area, y_area_diff))

    def handle_commands(self):
        if self.command_queue_is_empty():
            self.calculate_x_command()
            self.calculate_z_command()
            self.calculate_y_command()
        else:
            self.execute_command()

    def command_queue_is_empty(self):
        return len(self.command_queue) == 0

    def execute_command(self):
        comm = self.command_queue.pop(0)
        self.send_command(comm)



if __name__ == "__main__":

    tello = Tello()

    while 1:
        try:
            tello.show_video_frame()
        except Exception:
            tello.terminate()
            print("End of program")




    

