import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

# Screen center dead zone
LEFT_THRESHOLD = 0.40
RIGHT_THRESHOLD = 0.60

def detect_gesture():
    ret, frame = cap.read()
    if not ret:
        return "NONE"

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    gesture = "NONE"

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        lm = hand.landmark

        # -----------------------------
        # 1️⃣ HORIZONTAL INTENT (POSITION)
        # -----------------------------
        hand_x = lm[0].x   # wrist X (stable)

        if hand_x < LEFT_THRESHOLD:
            gesture = "LEFT"
        elif hand_x > RIGHT_THRESHOLD:
            gesture = "RIGHT"

        # -----------------------------
        # 2️⃣ VERTICAL INTENT (OPEN / FIST)
        # -----------------------------
        tips = [8, 12, 16, 20]
        folded = sum(lm[tip].y > lm[tip - 2].y for tip in tips)

        if folded == 0:
            gesture = "OPEN"
        elif folded >= 3:
            gesture = "FIST"

        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        # Debug visuals
        cv2.line(frame, (int(w*LEFT_THRESHOLD), 0), (int(w*LEFT_THRESHOLD), h), (255,0,0), 2)
        cv2.line(frame, (int(w*RIGHT_THRESHOLD), 0), (int(w*RIGHT_THRESHOLD), h), (0,0,255), 2)

    cv2.putText(
        frame,
        f"Gesture: {gesture}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )

    cv2.imshow("Gesture Controller", frame)
    cv2.waitKey(1)

    return gesture
