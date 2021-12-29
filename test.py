from pynput import keyboard
import cv2
import threading



class InputListener():

    def __init__(self):
        self.video_capture = cv2.VideoCapture(0)
        self.running = True
        self.input_thread_running = True
        self.input_thread = threading.Thread(target=self.get_input)
        self.input_thread.start()

    def get_input(self):
        while self.input_thread_running:
            inp = input()      
            if inp == "q":
                self.input_thread_running = False
                self.running = False

    def run(self):
        while self.running:
            img_retrieved, img = self.video_capture.read()
            if img_retrieved:
                # Display image.
                cv2.imshow("Camera Stream", img)
                k = cv2.waitKey(1)
        print("Ending program. Tello going to rest. See ya! :)")
        self.input_thread.join()




if __name__ == "__main__":
    # For testing purposes.

    # video_capture = cv2.VideoCapture(0)
    # input_listener = InputListener()

    # while input_listener.running:
    #     # Get camera image.
    #     img_retrieved, img = video_capture.read()
        

    #     if img_retrieved:
    #         # Display image.
    #         cv2.imshow("Camera Stream", img)
    #         k = cv2.waitKey(1)

    # print("Ending program.")
    # input_listener.input_thread.join()

    il = InputListener()
    il.run()

