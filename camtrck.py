import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            # Draw landmarks on the image
            for point in landmarks.landmark:
                x, y = int(image.shape[1] * point.x), int(image.shape[0] * point.y)
                cv2.circle(image, (x, y), 5, (0, 255, 0), -1)

    cv2.imshow('Hand Tracking', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()
