import cv2
import mediapipe as mp
import pyautogui

# Initialize MediaPipe Hands
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Initialize PyAutoGUI
pyautogui.FAILSAFE = False

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
HANDS_CONFIDENCE_THRESHOLD = 0.5

with mp_hands.Hands(min_detection_confidence=HANDS_CONFIDENCE_THRESHOLD, min_tracking_confidence=HANDS_CONFIDENCE_THRESHOLD) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Process the image to detect hands
        results = hands.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            # Assume the first detected hand is the controlling hand
            hand_landmarks = results.multi_hand_landmarks[0]

            # Get the coordinates of the index finger (landmark 8)
            index_finger = hand_landmarks.landmark[8]
            index_finger_x = int(index_finger.x * SCREEN_WIDTH)
            index_finger_y = int(index_finger.y * SCREEN_HEIGHT)

            # Move the cursor to the position of the index finger
            pyautogui.moveTo(index_finger_x, index_finger_y, duration=0.1)

        # Draw hand landmarks on the image
        mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow('Hand Gesture Control', image)

        if cv2.waitKey(1) & 0xFF == 27:  # Press Esc to exit
            break

cap.release()
cv2.destroyAllWindows()
