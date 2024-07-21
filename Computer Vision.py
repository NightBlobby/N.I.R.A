#===========================================================================================================================================
##MIT License

#Copyright (c) 2024 NightBlobby

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


#============================================================================================================================================


import tkinter as tk
from tkinter import ttk, font, messagebox
import speech_recognition as sr
import pyttsx3
import threading
import datetime
import webbrowser
import requests
import time
import random
import asyncio
import requests
from bleak import BleakScanner, BleakClient
from plyer import notification
import nfc
import os
import smtplib
from email.message import EmailMessage
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter
import pyowm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import joblib
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from PyDictionary import PyDictionary
import hashlib
import cv2
import tensorflow as tf
import numpy as np
import asyncio
# Ensure you have StableLM installed
from newsapi import NewsApiClient  
# Install newsapi-python library
import cv2
import numpy as np
import mediapipe as mp
from tensorflow.keras.models import load_model


# Emotion Recognition Class
class EmotionRecognizer:
    def __init__(self, model_path='model.best.hdf5'):
        self.model = self.load_model(model_path)
        self.emotion_classes = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    
    def load_model(self, model_path):
        try:
            model = load_model(model_path)
            print("Emotion model loaded successfully.")
            return model
        except Exception as e:
            print(f"Failed to load emotion model: {e}")
            return None
    
    def preprocess_image(self, image, size=(48, 48)):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.resize(image, size)
        image = img_to_array(image)
        image = image / 255.0
        image = np.expand_dims(image, axis=0)
        return image
    
    def recognize_emotion(self, face):
        if self.model is None:
            return "Blobby", 0
        face = self.preprocess_image(face)
        try:
            emotion_predictions = self.model.predict(face)
            emotion_idx = np.argmax(emotion_predictions[0])
            emotion = self.emotion_classes[emotion_idx]
            confidence = np.max(emotion_predictions[0])
            return emotion, confidence
        except Exception as e:
            print(f"Error recognizing emotion: {e}")
            return "unknown", 0

# Hand Gesture Recognition Class
class HandGestureRecognizer:
    def __init__(self, model_path='path_to_your_hand_model.h5'):
        self.model = self.load_model(model_path)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.75)
    
    def load_model(self, model_path):
        try:
            model = load_model(model_path)
            print("Hand model loaded successfully.")
            return model
        except Exception as e:
            print(f"Failed to load hand model: {e}")
            return None
    
    def count_fingers(self, hand_landmarks, width, height):
        if not hand_landmarks:
            return 0

        tip_ids = [4, 8, 12, 16, 20]
        base_ids = [2, 5, 9, 13, 17]
        
        finger_tips = []
        finger_bases = []
        
        for tip_id, base_id in zip(tip_ids, base_ids):
            tip = hand_landmarks.landmark[tip_id]
            base = hand_landmarks.landmark[base_id]
            
            tip_x, tip_y = tip.x * width, tip.y * height
            base_x, base_y = base.x * width, base.y * height
            
            if (base_y - tip_y) > (0.15 * (base_y - tip_y)):
                finger_tips.append(tip)
                finger_bases.append(base)
        
        if all(abs(base.y - tip.y) < 0.05 for tip, base in zip(finger_tips, finger_bases)):
            return 0
        
        return len(finger_tips)
    
    def recognize_hand_gesture(self, hand_landmarks_list, width, height):
        if not hand_landmarks_list:
            return ["Unknown"]
        
        results = []
        
        for landmarks in hand_landmarks_list:
            fingers = self.count_fingers(landmarks, width, height)
            
            if fingers == 0:
                gesture = "Fist"
            elif fingers == 1:
                gesture = "1 Finger"
            elif fingers == 2:
                gesture = "2 Fingers"
            elif fingers == 3:
                gesture = "3 Fingers"
            elif fingers == 4:
                gesture = "4 Fingers"
            elif fingers == 5:
                gesture = "5 Fingers"
            else:
                gesture = "Unknown Gesture"
            
            results.append({
                "gesture": gesture,
                "fingers": fingers
            })
        
        formatted_results = [f"Hand {i + 1}: {result['gesture']} (Fingers: {result['fingers']})"
                             for i, result in enumerate(results)]
        return formatted_results

# Face Mask Overlay Class
class FaceMaskOverlay:
    @staticmethod
    def apply_mask(frame, bbox, mask_color=(0, 0, 0), alpha=0.5):
        x, y, w, h = bbox
        mask = np.zeros_like(frame)
        mask[y:y+h, x:x+w] = mask_color
        frame = cv2.addWeighted(frame, 1 - alpha, mask, alpha, 0)
        return frame

# Video Processor Class
class VideoProcessor:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.75)
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(min_detection_confidence=0.75)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(min_detection_confidence=0.75, min_tracking_confidence=0.75)
        self.emotion_recognizer = EmotionRecognizer()
        self.hand_gesture_recognizer = HandGestureRecognizer()
    
    def detect_faces(self, frame):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(image_rgb)
        return results
    
    def detect_hands(self, frame):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)
        return results
    
    def detect_face_mesh(self, frame):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image_rgb)
        return results
    
    def recognize_object(self, frame):
        # Placeholder for object detection logic
        return frame
    
    def process_frame(self, frame):
        height, width, _ = frame.shape
        
        # Face detection
        face_results = self.detect_faces(frame)
        if face_results.detections:
            for detection in face_results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                face = frame[y:y+h, x:x+w]
                emotion, confidence = self.emotion_recognizer.recognize_emotion(face)
                mood_message = self.display_mood(emotion)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(frame, f"{emotion} ({confidence:.2f})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
                cv2.putText(frame, mood_message, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                frame = FaceMaskOverlay.apply_mask(frame, (x, y, w, h))

        # Hand detection
        hand_results = self.detect_hands(frame)
        hand_landmarks_list = hand_results.multi_hand_landmarks if hand_results.multi_hand_landmarks else []

        if hand_landmarks_list:
            for hand_landmarks in hand_landmarks_list:
                mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            gestures = self.hand_gesture_recognizer.recognize_hand_gesture(hand_landmarks_list, width, height)
            for i, gesture in enumerate(gestures):
                cv2.putText(frame, gesture, (10, 70 + i * 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        # Object detection
        frame = self.recognize_object(frame)
        return frame
    
    def display_mood(self, emotion):
        # Placeholder for mood message logic
        mood_messages = {
            "happy": "You seem happy!",
            "sad": "Cheer up!",
            "angry": "Take a deep breath.",
            "surprise": "Surprising, isn't it?",
            "fear": "Everything is fine.",
            "disgust": "That's unpleasant.",
            "neutral": "You're doing fine."
        }
        return mood_messages.get(emotion, "Have a great day!")

# Main Function
def main():
    video_processor = VideoProcessor()
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = video_processor.process_frame(frame)
        cv2.imshow('Video Processor', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()