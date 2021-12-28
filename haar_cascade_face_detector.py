import cv2


class HaarCascadeFaceDetector():

    """Class for detecting faces in images.
    
    Uses Haar Cascade classifier from OpenCV library."""

    #--------------------------------------------------------------------------
    # Init
    #--------------------------------------------------------------------------

    def __init__(self):
        # Load configuration files.
        self._frontal_config = "haarcascade_frontalface_alt2.xml"
        self._profile_config = "haarcascade_profileface.xml"
        self._frontal_face_detector = cv2.CascadeClassifier(self.frontal_config)
        self._profile_face_detector = cv2.CascadeClassifier(self.profile_config)

    #--------------------------------------------------------------------------
    # End Init
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Getters
    #--------------------------------------------------------------------------

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
        else:
            x, y, width, height = faces[0]
            # Draw rectangle on the image
            img = cv2.rectangle(img, (x, y),(x+width, y+height), (255, 0, 0), 2)

            # Return image and first detected face's bounding box.
            return img, faces[0]

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