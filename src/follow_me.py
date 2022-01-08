import cv2
import socket
import threading
import datetime
import time

from haar_cascade_face_detector import HaarCascadeFaceDetector


class Tello():

    """Class that implements follow-me flight mode of the Tello drone.
    
    Responsible for:
        - sending commands/receiving responces from Tello;
        - receiving video stream from Tello;
        - performing face detection in the video stream frames;
        - calculating flight commands based on the face's bounding box
          coordinates and size;
        - displaying video stream with detected face.
    """

    #--------------------------------------------------------------------------
    # Init
    #--------------------------------------------------------------------------

    def __init__(self):
        # Communication
        # IPs
        self._tello_ip = "192.168.10.1"
        self._mac_ip = "0.0.0.0"
        # Ports
        self._comm_send_port = 8889
        self._tello_state_port = 8890
        self._video_receive_port = 11111
        self._comm_receive_port = 9003
        # Sockets
        self._comm_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.comm_sock.bind((self.mac_ip, self.comm_receive_port))
        self.comm_sock.settimeout(1)

        # Face detection
        self._haar_face_detector = HaarCascadeFaceDetector()
        self._frame = None
        self._face_rect = None

        # Logging
        self._info_tag = "TELLO_INFO: "
        self._err_tag = "TELLO_ERR: "

        # Movement control
        # X axis
        self._x_threshold = 5 # deg
        self._max_turn_degrees = 41 # deg
        # Z axis
        self._z_threshold = 20 # cm
        self._max_z_distance = 50 # cm
        # Y axis
        self._y_threshold = 20 # cm
        self._target_face_height = 65 # px
        self._target_y_distance = 80 # cm
        
        self._command_queue = []

        # Threads
        self._comm_handle_running = True
        self._video_receive_running = True
        self._comm_handle_dead = False
        self._video_receive_dead = False
        self._response_received = False
        
        # Start command handligh thread.
        self._comm_handle_thread = threading.Thread(target=self.comm_handle)
        self.comm_handle_thread.start()

        # Tello sends response when command is received, not when it is
        # completed. For this reason time.sleep() is needed to wait for actual
        # command execution before sending next command.

        self.send_command("command")
        time.sleep(1)

        self.send_command("takeoff")
        time.sleep(7)

        self.send_command("up 60")
        time.sleep(2)
        
        self.send_command("streamon")
        time.sleep(1)

        self._video_cap = cv2.VideoCapture("udp://@{}:{}".format(self.mac_ip, self.video_receive_port))
        self.video_cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

        # Start video stream receiving thread.
        self._video_receive_thread = threading.Thread(target=self.video_receive)
        self.video_receive_thread.start()

    #--------------------------------------------------------------------------
    # End Init
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Getters
    #--------------------------------------------------------------------------

    @property
    def tello_ip(self):
        return self._tello_ip

    @property
    def mac_ip(self):
        return self._mac_ip

    @property
    def comm_send_port(self):
        return self._comm_send_port

    @property
    def tello_state_port(self):
        return self._tello_state_port

    @property
    def video_receive_port(self):
        return self._video_receive_port

    @property
    def comm_receive_port(self):
        return self._comm_receive_port

    @property
    def comm_sock(self):
        return self._comm_sock

    @property
    def haar_face_detector(self):
        return self._haar_face_detector

    @property
    def frame(self):
        return self._frame

    @property
    def face_rect(self):
        return self._face_rect

    @property
    def info_tag(self):
        return self._info_tag

    @property
    def err_tag(self):
        return self._err_tag

    @property
    def x_threshold(self):
        return self._x_threshold

    @property
    def max_turn_degrees(self):
        return self._max_turn_degrees

    @property
    def z_threshold(self):
        return self._z_threshold

    @property
    def max_z_distance(self):
        return self._max_z_distance

    @property
    def y_threshold(self):
        return self._y_threshold

    @property
    def target_face_height(self):
        return self._target_face_height

    @property
    def target_y_distance(self):
        return self._target_y_distance

    @property
    def command_queue(self):
        return self._command_queue

    @property
    def comm_handle_running(self):
        return self._comm_handle_running

    @property
    def video_receive_running(self):
        return self._video_receive_running

    @property
    def comm_handle_dead(self):
        return self._comm_handle_dead

    @property
    def video_receive_dead(self):
        return self._video_receive_dead

    @property
    def response_received(self):
        return self._response_received

    @property
    def comm_handle_thread(self):
        return self._comm_handle_thread

    @property
    def video_cap(self):
        return self._video_cap

    @property
    def video_receive_thread(self):
        return self._video_receive_thread

    #--------------------------------------------------------------------------
    # End Getters
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Setters
    #--------------------------------------------------------------------------

    @frame.setter
    def frame(self, new_frame):
        self._frame = new_frame

    @face_rect.setter
    def face_rect(self, new_face_rect):
        self._face_rect = new_face_rect

    @comm_handle_running.setter
    def comm_handle_running(self, new_comm_handle_running):
        self._comm_handle_running = new_comm_handle_running

    @video_receive_running.setter
    def video_receive_running(self, new_video_receive_running):
        self._video_receive_running = new_video_receive_running

    @comm_handle_dead.setter
    def comm_handle_dead(self, new_comm_handle_dead):
        self._comm_handle_dead = new_comm_handle_dead

    @video_receive_dead.setter
    def video_receive_dead(self, new_video_receive_dead):
        self._video_receive_dead = new_video_receive_dead

    @response_received.setter
    def response_received(self, new_response_received):
        self._response_received = new_response_received

    #--------------------------------------------------------------------------
    # End Setters
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Class Methods
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Command Handling Methonds
    #--------------------------------------------------------------------------
        
    def comm_handle(self):

        """Method for commands sending/responce receiving thread.
        
        While there is no response after sending command - wait for response.
        While not waiting for response - calculate and send control command."""

        start_time = datetime.datetime.now()
        while self.comm_handle_running:
            try:
                if not self.response_received:
                    self.receive_response()
                else:
                    # Send empty "command" every 5 seconds to keep Tello in SDK mode.
                    if (datetime.datetime.now() - start_time).total_seconds() >= 5:
                        self.send_command("command")
                        start_time = datetime.datetime.now()
                    else:
                        if self.face_rect is not None:
                            # Calculate and send control commands.
                            self.handle_commands()
                        else:
                            time.sleep(1)
            except Exception as e:
                # Send log.
                self.log_message(self.err_tag, str(e))
        self.comm_handle_dead = True

    def receive_response(self):

        """Method for receiving response from UDP socket after sending command."""

        # Read 1024 bytes from UDP socket.
        resp_msg = self.comm_sock.recvfrom(1024)[0]
        self.response_received = True

        # Send log.
        msg = "Command response: {}".format(resp_msg.decode(encoding="utf-8"))
        self.log_message(self.info_tag, msg)

    def send_command(self, comm):

        """Method for sending command to Tello through UDP socket.
        
        IN: comm - str - command to be sent to Tello."""

        comm = comm.encode(encoding="utf-8")
        self.comm_sock.sendto(comm, (self.tello_ip, self.comm_send_port))
        self.response_received = False

        # Send log.
        msg = "Sending command: {}".format(comm)
        self.log_message(self.info_tag, msg)

    def handle_commands(self):

        """Method for handling commands.
        
        Adds commands to command queue and initiates their execution."""

        if self.command_queue_is_empty():
            self.calculate_x_command()
            self.calculate_z_command()
            self.calculate_y_command()
        else:
            self.execute_command()

    def calculate_x_command(self):

        """Method for handling control command for X axis.
        
        Determines turn degree and direction based on face recognition
        results."""

        # Find whole frame's central X coordinate.
        frame_width = self.frame.shape[1]
        frame_center_x = frame_width // 2

        # Find faces's bounding box central X coordinate.
        face_x = self.face_rect[0]
        face_width = self.face_rect[2]
        face_center_x = face_x + face_width // 2

        # Find distance from frame's center to face's bounding box center.
        x_center_diff = frame_center_x - face_center_x
        # Calculate turn degrees from proportion:
        # max_turn_degrees - frame_center_x 
        # turn_degrees     - x_center_diff
        turn_degrees = abs(x_center_diff*self.max_turn_degrees//frame_center_x)

        # Send log.
        msg = "Frame center X: {}, Face center X: {}, X diff: {}"
        msg = msg.format(frame_center_x, face_center_x, x_center_diff)
        self.log_message(self.info_tag, msg)

        # If turn_degrees axceed threshold, add a new command to the command
        # queue.
        if turn_degrees > self.x_threshold:
            if x_center_diff > 0:
                direction = "ccw"
            else:
                direction = "cw"
            self.command_queue.append("{} {}".format(direction, turn_degrees))

    def calculate_z_command(self):

        """Method for handling control command for Z axis.
        
        Determines up/down movement distance and direction based on face
        recognition results."""

        # Find whole frame's central Y coordinate (Z in 3D space).
        frame_height = self.frame.shape[0]
        frame_center_z = frame_height // 2

        # Find faces's bounding box central Y coordinate (Z in 3D space).
        face_z = self.face_rect[1]
        face_height = self.face_rect[3]
        face_center_z = face_z + face_height // 2

        # Find distance from frame's center to face's bounding box center.
        z_center_diff =  face_center_z - frame_center_z
        # Calculate up/down movement distance from proportion:
        # max_z_distance      - frame_center_z 
        # horizontal_distance - z_center_diff
        horizontal_distance = abs(z_center_diff*self.max_z_distance//frame_center_z)

        # Send log.
        msg = "Frame center Z: {}, Face center Z: {}, Z diff: {}"
        msg = msg.format(frame_center_z, face_center_z, z_center_diff)
        self.log_message(self.info_tag, msg)

        # If horizontal_distance axceed threshold, add a new command to the
        # command queue.
        if horizontal_distance > self.z_threshold:
            if z_center_diff > 0:
                direction = "down"
            else:
                direction = "up"
            self.command_queue.append("{} {}".format(direction, horizontal_distance))

    def calculate_y_command(self):

        """Method for handling control command for Y axis.
        
        Determines forward/back movement distance and direction based on face
        recognition results."""

        # Get face's bounding box height.
        face_height = self.face_rect[3]

        # We want to keep Tello at the distance of 80 cm from the face.
        # Face's bounding box at such distance has height of approx. 65 px.

        # Calculate current distance from the recognized face from proportion:
        # target_face_height - target_y_distance
        # current_distance   - face_height
        current_distance = self.target_face_height * self.target_y_distance // face_height
        # Calculate forward/back movement distance.
        vertical_distance = abs(current_distance - self.target_y_distance)

        # If vertical_distance axceed threshold, add a new command to the
        # command queue.
        if vertical_distance > self.y_threshold:
            if current_distance >= self.target_y_distance:
                direction = "forward"
            else:
                direction = "back"
            self.command_queue.append("{} {}".format(direction, vertical_distance))

        # Send log.
        msg = "Target height: {}, Face height: {}, current distance: {}"
        msg = msg.format(self.target_face_height, face_height, current_distance)
        self.log_message(self.info_tag, msg)

    def execute_command(self):

        """Method for executing command.
        
        Gets the first command from the command queue and sends it to Tello."""

        comm = self.command_queue.pop(0)
        self.send_command(comm)

    def command_queue_is_empty(self):

        """Method for checking if command queue is empty."""

        return len(self.command_queue) == 0

    #--------------------------------------------------------------------------
    # End Command Handling Methonds
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Video Handling Methonds
    #--------------------------------------------------------------------------

    def video_receive(self):

        """Method for receiving video frames throught UDP socket from Tello."""

        while self.video_receive_running:
            try:
                frame_res, frame = self.video_cap.read()
                if frame_res:
                    # Resize frame to improve performance.
                    height, width, _ = frame.shape
                    frame = cv2.resize(frame, (width//2, height//2))
                    
                    # Detect face.
                    detected_face = self.haar_face_detector.detect_face(frame)
                    if detected_face is not None:
                        self.frame, self.face_rect = detected_face
                    else:
                        self.frame = frame
            except Exception as e:
                # Send log.
                self.log_message(self.err_tag, str(e))
        self.video_receive_dead = True

    def show_video_frame(self):

        """Method for displaying Tello video stream using OpenCV library."""

        if self.frame is not None:
            cv2.imshow("Tello Client", self.frame)
            cv2.setWindowProperty("Tello Client", cv2.WND_PROP_TOPMOST, 1)
            cv2.waitKey(1)
        else:
            time.sleep(1)

    #--------------------------------------------------------------------------
    # End Video Handling Methonds
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Thread Terminators
    #--------------------------------------------------------------------------

    def terminate(self):

        """Method for terminating Tello video stream and command handlig."""

        # Send log.
        msg = "Terminating Tello."
        self.log_message(self.info_tag, msg)

        self.send_command("land")
        self.terminate_comm_handle()
        self.terminate_video_response()

    def terminate_comm_handle(self):

        """Method for terminating Tello command thread."""

        # Send log.
        msg = "Terminating Tello command thread."
        self.log_message(self.info_tag, msg)

        self.comm_handle_running = False
        self.comm_sock.close()
        # Wait for thread to stop working.
        while not self.comm_handle_dead:
            time.sleep(1)
        self.comm_handle_thread.join()

    def terminate_video_response(self):

        """Method for terminating Tello video thread."""

        # Send log.
        msg = "Terminating Tello video stream thread."
        self.log_message(self.info_tag, msg)

        self.video_receive_running = False
        self.video_cap.release()
        cv2.destroyAllWindows()
        # Wait for thread to stop working.
        while not self.video_receive_dead:
            time.sleep(1)
        self.video_receive_thread.join()

    #--------------------------------------------------------------------------
    # End Thread Terminators
    #--------------------------------------------------------------------------

    def log_message(self, tag, msg):
        
        """Method for logging messages.
        
        IN:
            tag - str - message tag (TELLO_INFO or TELLO_ERR)
            msg - str - message to be logged."""

        print(tag + msg)

    #--------------------------------------------------------------------------
    # End Class Methods
    #--------------------------------------------------------------------------
