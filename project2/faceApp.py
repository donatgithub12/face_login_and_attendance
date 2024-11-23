from flask import Flask, render_template, redirect, url_for, Response
import cv2
import face_recognition
import sqlite3
import numpy as np
import os
import base64
from datetime import datetime, timedelta

app = Flask(__name__)

DB_NAME = os.path.abspath("employee_data.db")
KNOWN_FACES_TABLE = "employees"

# Load known faces from the database
def load_known_faces():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT name, image, job_title, employee_id FROM {KNOWN_FACES_TABLE}")
    data = cursor.fetchall()
    conn.close()

    known_face_encodings = []
    known_face_data = []

    for name, image_blob, job_title, employee_id in data:
        if image_blob:
            image_array = np.frombuffer(image_blob, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            face_encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(face_encoding)
            known_face_data.append({"name": name, "job_title": job_title, "employee_id": employee_id, "image_blob": image_blob})

    return known_face_encodings, known_face_data

known_face_encodings, known_face_data = load_known_faces()

import csv
from datetime import datetime, timedelta

# Dictionary to track attendance records by employee ID
attendance_records = {}

def markAttendance(emp_id, name):
    """Mark attendance for a recognized person with employee ID."""
    now = datetime.now()
    if emp_id in attendance_records:
        last_marked = attendance_records[emp_id]
        # Check if 20 hours have passed since the last marking
        if now - last_marked < timedelta(min):
            print(f"Attendance for {name} (ID: {emp_id}) is already marked within the last 20 hours.")
            return
    
    # Update the attendance record and log attendance
    attendance_records[emp_id] = now
    with open('Attendance.csv', 'a', newline='') as f:  # Use newline='' to prevent extra lines
        writer = csv.writer(f)
        time = now.strftime('%I:%M:%S %p')
        date = now.strftime('%d-%B-%Y')
        writer.writerow([emp_id, name, time, date])  # Proper CSV format
        print(f"Attendance marked for {name} (ID: {emp_id}) at {time} on {date}")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_face')
def process_face():
    """Process a single frame and decide where to redirect."""
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if not ret:
        cap.release()
        return redirect(url_for('not_authorized'))

    # Resize and process the frame
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    # Match faces
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

        if any(matches):  # Check if there's any match
            match_index = np.argmin(face_distances)  # Get the best match based on distance
            matched_user = known_face_data[match_index]

            # Call markAttendance with the correct arguments
            markAttendance(matched_user["employee_id"], matched_user["name"])

            # Convert image blob to Base64 for display
            image_blob = matched_user["image_blob"]
            image_base64 = base64.b64encode(image_blob).decode('utf-8')

            cap.release()
            return render_template('welcome.html',
                                   name=matched_user["name"],
                                   job_title=matched_user["job_title"],
                                   employee_id=matched_user["employee_id"],
                                   image=image_base64)

    cap.release()
    return redirect(url_for('not_authorized'))


@app.route('/not_authorized')
def not_authorized():
    return render_template('not_authorized.html')

if __name__ == '__main__':
    app.run(debug=True)