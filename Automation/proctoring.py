"""
Proctoring Module
Handles camera tracking, audio monitoring, and multiple person detection
Uses OpenCV for face detection (no face_recognition library required)
"""
import cv2
import numpy as np
import time
import threading
from collections import deque

try:
    import pyaudio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False


class ProctoringSystem:
    def __init__(self):
        self.camera = None
        self.is_monitoring = False
        self.violations = []
        self.face_detected = False
        self.multiple_faces_detected = False
        self.audio_levels = deque(maxlen=100)
        self.frame_count = 0
        self.last_face_time = time.time()
        self.face_detection_interval = 0.5  # Check every 0.5 seconds
        
    def initialize_camera(self):
        """Initialize camera"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                return False
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def detect_faces(self, frame):
        """Detect faces in frame using OpenCV"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        return len(faces), faces
    
    def process_frame(self, frame):
        """Process a single frame for proctoring"""
        num_faces, faces = self.detect_faces(frame)
        
        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Update face detection status
        if num_faces == 0:
            self.face_detected = False
            if time.time() - self.last_face_time > 3:  # No face for 3 seconds
                self.record_violation("No face detected for extended period")
        elif num_faces == 1:
            self.face_detected = True
            self.multiple_faces_detected = False
            self.last_face_time = time.time()
        else:
            self.multiple_faces_detected = True
            self.record_violation(f"Multiple faces detected: {num_faces}")
        
        return frame, {
            "faces_detected": num_faces,
            "face_detected": self.face_detected,
            "multiple_faces": self.multiple_faces_detected,
            "timestamp": time.time()
        }
    
    def record_violation(self, violation_type):
        """Record a proctoring violation"""
        violation = {
            "type": violation_type,
            "timestamp": time.time(),
            "frame": self.frame_count
        }
        self.violations.append(violation)
    
    def get_violations_summary(self):
        """Get summary of violations"""
        if not self.violations:
            return {
                "total_violations": 0,
                "no_face_violations": 0,
                "multiple_face_violations": 0,
                "audio_violations": 0
            }
        
        summary = {
            "total_violations": len(self.violations),
            "no_face_violations": sum(1 for v in self.violations if "No face" in v["type"]),
            "multiple_face_violations": sum(1 for v in self.violations if "Multiple faces" in v["type"]),
            "audio_violations": sum(1 for v in self.violations if "audio" in v["type"].lower())
        }
        return summary
    
    def start_monitoring(self):
        """Start proctoring monitoring"""
        if not self.initialize_camera():
            return False
        self.is_monitoring = True
        self.violations = []
        self.frame_count = 0
        return True
    
    def stop_monitoring(self):
        """Stop proctoring monitoring"""
        self.is_monitoring = False
        if self.camera:
            self.camera.release()
            self.camera = None
    
    def get_frame(self):
        """Get current frame from camera"""
        if not self.camera or not self.is_monitoring:
            return None, None
        
        ret, frame = self.camera.read()
        if not ret:
            return None, None
        
        self.frame_count += 1
        processed_frame, status = self.process_frame(frame)
        return processed_frame, status
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_monitoring()


# Audio monitoring functions
def monitor_audio_level():
    """Monitor audio input levels"""
    if not AUDIO_AVAILABLE:
        return None
    
    try:
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        data = stream.read(CHUNK)
        audio_level = np.abs(np.frombuffer(data, dtype=np.int16)).mean()
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        return audio_level
    except Exception as e:
        return None


def check_audio_violation(audio_level, threshold=1000):
    """Check if audio level indicates violation (e.g., talking)"""
    if audio_level is None:
        return False
    return audio_level > threshold

