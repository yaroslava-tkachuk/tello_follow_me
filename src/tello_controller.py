"""Copyright 2022 Yaroslava Tkachuk. All rights reserved."""

import threading

from follow_me import Tello


class TelloFollowMeController():

    """Class for running main Tello follow-me mode program.
    
    Responsible for:
        - initizlizing Tello command and video stream threads;
        - initializing keyboard input thread;
        - displaying Tello video stream."""

    #--------------------------------------------------------------------------
    # Init
    #--------------------------------------------------------------------------

    def __init__(self):
        self._tello = Tello()

        # Logging
        self._info_tag = "TELLO_COMMANDER_INFO: "
        self._err_tag = "TELLO_COMMANDER_ERR: "

        # Threads
        self._running = True
        self._input_thread_running = True
        # Start reading input from terminal.
        self._input_thread = threading.Thread(target=self.get_input)
        self.input_thread.start()

    #--------------------------------------------------------------------------
    # End Init
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Getters
    #--------------------------------------------------------------------------

    @property
    def tello(self):
        return self._tello
    
    @property
    def info_tag(self):
        return self._info_tag

    @property
    def err_tag(self):
        return self._err_tag

    @property
    def running(self):
        return self._running

    @property
    def input_thread_running(self):
        return self._input_thread_running

    @property
    def input_thread(self):
        return self._input_thread

    #--------------------------------------------------------------------------
    # End Getters
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Setters
    #--------------------------------------------------------------------------

    @running.setter
    def running(self, new_running):
        self._running = new_running

    @input_thread_running.setter
    def input_thread_running(self, new_input_thread_running):
        self._input_thread_running = new_input_thread_running

    #--------------------------------------------------------------------------
    # End Setters
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Class Methods
    #--------------------------------------------------------------------------

    def get_input(self):

        """Method for reading input from keyboard.
        
        Terminates program when 'q' character is entered."""

        while self.input_thread_running:
            inp = input()      
            if inp == "q":
                self.input_thread_running = False
                self.running = False

    def run(self):

        """Method for running main Tello follow-me mode program.
        
        Initializes all Tello threads, keyboard input thread, and displays
        Tello video stream."""

        while self.running:
            try:
                self.tello.show_video_frame()
            except Exception as e:
                # Log message.
                self.log_message(self.err_tag, str(e))
        
        # Log message.
        msg = "Ending program. Tello going to rest. See ya! :)"
        self.log_message(self.info_tag, msg)

        # Terminate all threads.
        self.terminate()

    #--------------------------------------------------------------------------
    # Terminators
    #--------------------------------------------------------------------------
        
    def terminate(self):
        
        """Method for terminating Tello and keyboard input threads."""

        self.input_thread.join()
        self.tello.terminate()

    #--------------------------------------------------------------------------
    # End Terminators
    #--------------------------------------------------------------------------

    def log_message(self, tag, msg):
        
        """Method for logging messages.
        
        IN:
            tag - str - message tag (TELLO_COMMANDER_INFO or
                TELLO_COMMANDER_ERR)
            msg - str - message to be logged."""

        print(tag + msg)

    #--------------------------------------------------------------------------
    # End Class Methods
    #--------------------------------------------------------------------------
