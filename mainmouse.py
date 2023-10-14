import cv2
import mediapipe as mp
import pyautogui
import math
from enum import IntEnum
import screen_brightness_control as sbcontrol

pyautogui.FAILSAFE = False
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Gesture Encodings
class Gest(IntEnum):
    PALM = 0
    FIST = 1
    TWO_FINGERS = 2
    THREE_FINGERS = 3
    FOUR_FINGERS = 4
    FIVE_FINGERS = 5
    OK = 6

class HandRecog:
    def __init__(self):
        self.finger = 0
        self.ori_gesture = Gest.PALM
        self.prev_gesture = Gest.PALM
        self.frame_count = 0

    def update_hand_result(self, hand_result):
        self.hand_result = hand_result

    def set_finger_state(self):
        if self.hand_result is None:
            return
        self.finger = 0
        for idx, point in enumerate(self.hand_result.landmark):
            if idx > 0:  # Exclude wrist
                self.finger += 1

    def get_gesture(self):
        if self.hand_result is None:
            return Gest.PALM
        current_gesture = Gest.PALM

        # Determine the gesture based on the number of fingers detected
        if self.finger == 0:
            current_gesture = Gest.PALM
        elif self.finger == 1:
            current_gesture = Gest.FIST
        elif self.finger == 2:
            current_gesture = Gest.TWO_FINGERS
        elif self.finger == 3:
            current_gesture = Gest.THREE_FINGERS
        elif self.finger == 4:
            current_gesture = Gest.FOUR_FINGERS
        elif self.finger >= 5:
            current_gesture = Gest.FIVE_FINGERS

        if current_gesture == self.prev_gesture:
            self.frame_count += 1
        else:
            self.frame_count = 0
            self.prev_gesture = current_gesture

        if self.frame_count > 10:
            self.ori_gesture = current_gesture

        return self.ori_gesture

class Controller:
    def __init__(self):
        self.prev_hand = None
        self.palm_detected = False

    def get_position(self, hand_result):
        point = 8
        position = [hand_result.landmark[point].x, hand_result.landmark[point].y]
        sx, sy = pyautogui.size()
        x_old, y_old = pyautogui.position()
        x = int(position[0] * sx)
        y = int(position[1] * sy)

        if self.prev_hand is None:
            self.prev_hand = x, y

        delta_x = x - self.prev_hand[0]
        delta_y = y - self.prev_hand[1]
        distsq = delta_x ** 2 + delta_y ** 2
        ratio = 1

        self.prev_hand = [x, y]

        if distsq <= 25:
            ratio = 0
        elif distsq <= 900:
            ratio = 0.07 * (distsq ** (1 / 2))
        else:
            ratio = 2.1

        x, y = x_old + delta_x * ratio, y_old + delta_y * ratio

        return x, y

    def handle_controls(self, gesture, hand_result):
        x, y = None, None

        if gesture != Gest.PALM:
            x, y = self.get_position(hand_result)

        if gesture == Gest.PALM:
            self.palm_detected = True
        else:
            self.palm_detected = False

        # Implement various controls based on the gesture
        if gesture == Gest.TWO_FINGERS:
            # Move the cursor when two fingers detected
            pyautogui.moveTo(x, y, duration=0.1)
        elif gesture == Gest.FIST:
            # Perform actions for a fist gesture (e.g., left-click)
            pyautogui.mouseDown(button="left")
            pyautogui.moveTo(x, y, duration=0.1)
        elif gesture == Gest.FIVE_FINGERS:
            # Perform actions for five fingers (e.g., right-click)
            pyautogui.mouseDown(button="right")
            pyautogui.moveTo(x, y, duration=0.1)
        else:
            # Release the mouse button if no specific gesture is detected
            pyautogui.mouseUp()

# Main Class
class GestureController:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def start(self):
        hand_recog = HandRecog()
        controller = Controller()

        with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5,
                            min_tracking_confidence=0.5) as hands:
            while self.cap.isOpened():
                success, image = self.cap.read()

                if not success:
                    print("Ignoring empty camera frame.")
                    continue

                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = hands.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        hand_recog.update_hand_result(hand_landmarks)
                        hand_recog.set_finger_state()
                        gesture = hand_recog.get_gesture()
                        controller.handle_controls(gesture, hand_landmarks)
                        mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                cv2.imshow('GestureController', image)
                if cv2.waitKey(5) & 0xFF == 13:
                    break

        self.cap.release()
        cv2.destroyAllWindows()

# Uncomment to run directly
gc1 = GestureController()
gc1.start()
