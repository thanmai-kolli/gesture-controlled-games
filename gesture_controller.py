"""Webcam hand-gesture recognizer shared by every game in the suite.

Wraps OpenCV capture + MediaPipe Hands behind a small class so games no
longer poke at module-level globals or open their own cv2 preview window.
Recognized gestures: NONE, LEFT, RIGHT, OPEN, FIST.
"""
from collections import Counter, deque

import cv2
import mediapipe as mp
import pygame

import config

# Keyboard stands in for gestures when no webcam is available (or as an
# always-on accessibility fallback while a camera is present).
_KEY_GESTURES = {
    pygame.K_LEFT: "LEFT",
    pygame.K_RIGHT: "RIGHT",
    pygame.K_UP: "OPEN",
    pygame.K_SPACE: "OPEN",
    pygame.K_DOWN: "FIST",
}


class GestureController:
    """Reads one gesture per frame from the webcam, with keyboard fallback."""

    def __init__(self, camera_index=config.CAMERA_INDEX, smoothing=config.GESTURE_SMOOTHING):
        self._mp_hands = mp.solutions.hands  # type: ignore[attr-defined]
        self._mp_draw = mp.solutions.drawing_utils  # type: ignore[attr-defined]
        self._hands = self._mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
        )
        self._history = deque(maxlen=max(smoothing, 1))
        self._last_frame_rgb = None  # last annotated frame, already RGB

        cap = cv2.VideoCapture(camera_index)
        self.camera_available = bool(cap is not None and cap.isOpened())
        self._cap = cap if self.camera_available else None

    def read(self):
        """Returns the smoothed gesture string ("NONE"/"LEFT"/"RIGHT"/"OPEN"/"FIST")."""
        raw = self._read_camera_gesture() if self.camera_available else "NONE"
        raw = self._apply_keyboard_fallback(raw)

        self._history.append(raw)
        return Counter(self._history).most_common(1)[0][0]

    def _read_camera_gesture(self):
        if self._cap is None:
            return "NONE"
        ok, frame = self._cap.read()
        if not ok:
            return "NONE"

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb)

        gesture = "NONE"
        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            lm = hand.landmark

            # Horizontal intent from wrist position.
            hand_x = lm[0].x
            if hand_x < config.LEFT_THRESHOLD:
                gesture = "LEFT"
            elif hand_x > config.RIGHT_THRESHOLD:
                gesture = "RIGHT"

            # Vertical intent from finger curl (open palm vs. fist).
            tips = [8, 12, 16, 20]
            folded = sum(lm[tip].y > lm[tip - 2].y for tip in tips)
            if folded == 0:
                gesture = "OPEN"
            elif folded >= 3:
                gesture = "FIST"

            self._mp_draw.draw_landmarks(rgb, hand, self._mp_hands.HAND_CONNECTIONS)
            cv2.line(rgb, (int(w * config.LEFT_THRESHOLD), 0), (int(w * config.LEFT_THRESHOLD), h), (255, 80, 80), 2)
            cv2.line(rgb, (int(w * config.RIGHT_THRESHOLD), 0), (int(w * config.RIGHT_THRESHOLD), h), (80, 120, 255), 2)

        self._last_frame_rgb = rgb
        return gesture

    @staticmethod
    def _apply_keyboard_fallback(gesture):
        keys = pygame.key.get_pressed()
        for key, mapped in _KEY_GESTURES.items():
            if keys[key]:
                return mapped
        return gesture

    def get_preview_surface(self, size=config.PREVIEW_SIZE):
        """Latest camera frame (with landmark overlay) as a pygame Surface, or None."""
        if self._last_frame_rgb is None:
            return None
        frame = cv2.resize(self._last_frame_rgb, size)
        return pygame.image.frombuffer(frame.tobytes(), size, "RGB")

    def release(self):
        """Releases the webcam and MediaPipe resources. Safe to call multiple times."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
            self.camera_available = False
        self._hands.close()
