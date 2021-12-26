import cv2


class HaarCascadeFaceDetector():

    def __init__(self):
        self.frontal_face_detector = cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")
        self.profile_face_detector = cv2.CascadeClassifier("haarcascade_profileface.xml")
        self.face = None

    def detect_face(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
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
            return img, faces[0]

if __name__ == "__main__":
    video_capture = cv2.VideoCapture(0)
    haar_cascade_face_detector = HaarCascadeFaceDetector()

    while 1:
        # Get camera image
        img_retrieved, img = video_capture.read()

        if img_retrieved:
            # Detect face
            detected_face = haar_cascade_face_detector.detect_face(img)
            if detected_face is not None:
                img, face_rect = detected_face

            cv2.imshow("Camera Stream", img)
            cv2.waitKey(1)