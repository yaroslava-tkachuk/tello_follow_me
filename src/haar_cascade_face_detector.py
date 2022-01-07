import cv2


class HaarCascadeFaceDetector():

    """Class for detecting faces in images.
    
    Uses Haar Cascade classifier from OpenCV library."""

    #--------------------------------------------------------------------------
    # Init
    #--------------------------------------------------------------------------

    def __init__(self):
        # Colors.
        self._blue = (255, 0, 0)
        self._red = (0, 0, 255)
        # Load configuration files.
        self._frontal_config = "../data/haarcascade_frontalface_alt2.xml"
        self._profile_config = "../data/haarcascade_profileface.xml"
        self._frontal_face_detector = cv2.CascadeClassifier(self.frontal_config)
        self._profile_face_detector = cv2.CascadeClassifier(self.profile_config)

    #--------------------------------------------------------------------------
    # End Init
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Getters
    #--------------------------------------------------------------------------

    @property
    def blue(self):
        return self._blue
    
    @property
    def red(self):
        return self._red

    @property
    def frontal_config(self):
        return self._frontal_config

    @property
    def profile_config(self):
        return self._profile_config

    @property
    def frontal_face_detector(self):
        return self._frontal_face_detector

    @property
    def profile_face_detector(self):
        return self._profile_face_detector

    #--------------------------------------------------------------------------
    # End Getters
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Setters
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # End Setters
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Class Methods
    #--------------------------------------------------------------------------

    def detect_face(self, img):

        """Detects face in a given image using OpenCV Haarcascade Classifier.
        
        IN:
            img - numpy.ndarray - image to be analyzed.
        OUT:
            (img, faces[0]) - tuple - if face was detected.
                img - numpy.ndarray - image with detected face.
                faces[0] - numpy.ndarray - [top_left_x, top_left_y, width,
                    height] of the detected image bounding box.
            None - if no face was detected.
        """

        # Convert image into grayscale.
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Detect frontal face.
        faces = self.frontal_face_detector.detectMultiScale(img_gray, 1.3, 5)
        # If no frontal face was detected, try detecting profile face.
        if len(faces) == 0:
            faces = self.profile_face_detector.detectMultiScale(img_gray, 1.3, 5)
        
        # If no faces were detected, return None.
        if len(faces) == 0:
            return
        
        # Draw face detection results on the image.
        img = self.draw_face_roi(img, faces[0])

        # Return image and first detected face's bounding box.
        return img, faces[0]

    def draw_face_roi(self, img, face):

        """Draws detected face's ROI.

        Draws rectangular face frame and its central point - blue. Draws
        centrral point of the image frame - red. 
        
        IN:
            img - numpy.ndarray - image to be analyzed.
            face - numpy.ndarray - [top_left_x, top_left_y, width,
                height] of the detected image bounding box.
        OUT:
            img - numpy.ndarray - image with ROI.
        """

        x, y, width, height = face
        # Draw rectangle on the image.
        img = cv2.rectangle(img, (x, y), (x+width, y+height), self.blue, 2)
        # Draw central point of the recognised face.
        img = cv2.circle(img, (x+width//2, y+height//2), radius=2,
            color=self.blue, thickness=-1)
        
        # Draw central point of the image frame.
        img_height, img_width = img.shape[0], img.shape[1]
        img = cv2.circle(img, (img_width//2, img_height//2), radius=2,
            color=self.red, thickness=-1)

        return img

    #--------------------------------------------------------------------------
    # End Class Methods
    #--------------------------------------------------------------------------


if __name__ == "__main__":
    # For testing purposes.

    video_capture = cv2.VideoCapture(0)
    haar_cascade_face_detector = HaarCascadeFaceDetector()

    while 1:
        # Get camera image.
        img_retrieved, img = video_capture.read()

        if img_retrieved:
            # Detect face.
            detected_face = haar_cascade_face_detector.detect_face(img)
            if detected_face is not None:
                img, face_rect = detected_face

            # Display image.
            cv2.imshow("Camera Stream", img)
            cv2.waitKey(1)