**Tello Client** application for DJI Ryze Tello 1.0 UAV.

Functionalities:
- Drone camera video streaming.
- Real-time face detection in video stream images using Haar Cascade classifier from OpenCV library.
- Autonomous "follow-me" flight mode of the UAV.

Tello "follow-me" flight can be view on [YouTube](https://www.youtube.com/watch?v=JM1rvrMFqlA).

**System Diagram**
![System Diagram](/documentation/tello_system_diagram.png)

**Tello Client Flow**
![System Diagram](/documentation/tello_client_flow.png)

**How to Use Tello Client**
1. Turn on your DJI Ryze Tello 1.0 UAV.
2. Connect to Tello network on your PC.
3. Run `main.py` from `tello_follow_me/src` directory.
4. Enjoy Tello "follow-me" flight.
5. Provide `"q"` in terminal to quit.
