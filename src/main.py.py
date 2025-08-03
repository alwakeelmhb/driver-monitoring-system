import cv2
import mediapipe as mp
import numpy as np
import pygame
import time
from tkinter import *
from PIL import Image, ImageTk
import threading

# Alarm Setup
pygame.mixer.init()
alarm_sound = pygame.mixer.Sound("audio2.mp3")
cooldown = 10
last_alert_time = 0
alert_display_time = 4
alert_start_time = None
current_alert = None

# Mediapipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# Eye Vals
EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 5
eye_closed_counter = 0

# Clac Eye_ratio
def eye_aspect_ratio(landmarks, eye_indices, w, h):
    p = lambda i: np.array([landmarks[i].x * w, landmarks[i].y * h])
    A = np.linalg.norm(p(eye_indices[1]) - p(eye_indices[5]))
    B = np.linalg.norm(p(eye_indices[2]) - p(eye_indices[4]))
    C = np.linalg.norm(p(eye_indices[0]) - p(eye_indices[3]))
    ear = (A + B) / (2.0 * C)
    return ear

# head angel
def rotation_angles(landmarks, w, h):
    image_points = np.array([
        [landmarks[1].x * w, landmarks[1].y * h],     # Nose tip
        [landmarks[33].x * w, landmarks[33].y * h],   # Left eye inner
        [landmarks[263].x * w, landmarks[263].y * h], # Right eye inner
        [landmarks[61].x * w, landmarks[61].y * h],   # Mouth left
        [landmarks[291].x * w, landmarks[291].y * h], # Mouth right
        [landmarks[199].x * w, landmarks[199].y * h], # Chin
    ], dtype="double")

    model_points = np.array([
        [0.0, 0.0, 0.0],
        [-30.0, -30.0, -30.0],
        [30.0, -30.0, -30.0],
        [-40.0, 30.0, -30.0],
        [40.0, 30.0, -30.0],
        [0.0, 50.0, -50.0],
    ])

    focal_length = w
    center = (w / 2, h / 2)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype="double")

    dist_coeffs = np.zeros((4, 1))
    success, rotation_vec, translation_vec = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs)

    rotation_mat, _ = cv2.Rodrigues(rotation_vec)
    pose_mat = cv2.hconcat((rotation_mat, translation_vec))
    _, _, _, _, _, _, angles = cv2.decomposeProjectionMatrix(pose_mat)

    yaw = angles[1][0] / 180.0
    pitch = angles[0][0] / 180.0
    roll = angles[2][0] / 180.0
    return yaw, pitch, roll

# Tkinter
root = Tk()
root.title("Driver Monitor")
root.geometry("800x600")

frame_label = Label(root)
frame_label.pack()

status_label = Label(root, text="Status: Waiting", font=("Arial", 14))
status_label.pack(pady=10)

running = False
cap = None

def update_frame():
    global last_alert_time, alert_start_time, current_alert, eye_closed_counter

    LEFT_EYE_IDX = [362, 385, 387, 263, 373, 380]
    RIGHT_EYE_IDX = [33, 160, 158, 133, 153, 144]

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                yaw, pitch, roll = rotation_angles(face_landmarks.landmark, w, h)
                nose = face_landmarks.landmark[1]
                cx, cy = int(nose.x * w), int(nose.y * h)

                # direction
                cv2.line(frame, (cx, cy), (cx + int(yaw * -200), cy), (0, 0, 255), 2)
                cv2.line(frame, (cx, cy), (cx, cy + int(pitch * -200)), (0, 255, 0), 2)

                text = f"Yaw: {yaw:.2f}, Pitch: {pitch:.2f}"
                cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # EAR
                left_EAR = eye_aspect_ratio(face_landmarks.landmark, LEFT_EYE_IDX, w, h)
                right_EAR = eye_aspect_ratio(face_landmarks.landmark, RIGHT_EYE_IDX, w, h)
                avg_EAR = (left_EAR + right_EAR) / 2.0
                cv2.putText(frame, f"EAR: {avg_EAR:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                now = time.time()

                if avg_EAR < EYE_AR_THRESH:
                    eye_closed_counter += 1
                else:
                    eye_closed_counter = 0

                # Alert Conditions             
                if ((abs(yaw) > 0.3 or abs(pitch) > 0.25 or abs(roll) > 0.2) or (eye_closed_counter >= EYE_AR_CONSEC_FRAMES)) and (now - last_alert_time > cooldown):
                    if current_alert != "Driver not alert":
                        current_alert = "Driver not alert"
                        alert_start_time = now
                        status_label.after(0, status_label.config, {"text": "🚨 Driver not alert!", "fg": "red"})
                        pygame.mixer.Sound.play(alarm_sound)
                        last_alert_time = now
                elif current_alert == "Driver not alert" and (now - alert_start_time >= alert_display_time):
                    current_alert = None
                    status_label.after(0, status_label.config, {"text": "Driver is alert", "fg": "green"})

        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        frame_label.imgtk = imgtk
        frame_label.configure(image=imgtk)

    cap.release()

def start_monitoring():
    global running, cap
    running = True
    cap = cv2.VideoCapture(0)
    threading.Thread(target=update_frame, daemon=True).start()

def stop_monitoring():
    global running
    running = False
    status_label.config(text="Status: Stopped", fg="black")

def close_app():
    stop_monitoring()
    root.quit()
    root.destroy()

# Buttons
button_frame = Frame(root)
button_frame.pack(pady=10)

Button(button_frame, text="Start Monitoring", font=("Arial", 12), command=start_monitoring).pack(side="left", padx=5)
Button(button_frame, text="Stop", font=("Arial", 12), command=stop_monitoring).pack(side="left", padx=5)
Button(button_frame, text="Exit", font=("Arial", 12), command=close_app).pack(side="left", padx=5)

root.mainloop()