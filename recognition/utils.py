import cv2
import pickle
from .models import RecognizedFace, UserProfile
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
import os
import logging
import face_recognition
logging.basicConfig(level=logging.DEBUG)
import numpy as np
import io
import dlib
import tempfile

def recognize_and_save_face(known_faces, known_names, image_file):
    # Read the image file into a PIL Image
    pil_image = Image.open(image_file)

    # Convert PIL Image to NumPy array
    image_array = np.array(pil_image)

    # Initialize the dlib face detector
    detector = dlib.get_frontal_face_detector()

    # Detect faces in the image
    detected_faces = detector(image_array, 1)  # 1 is the upsample_num_times parameter

    # Extract face encodings
    encodings = []
    for face in detected_faces:
        # Extract face region
        face_image = image_array[face.top():face.bottom(), face.left():face.right()]
        # Convert face region to PIL Image for face_recognition library
        face_pil_image = Image.fromarray(face_image)
        # Get encoding using face_recognition library
        encoding = face_recognition.face_encodings(np.array(face_pil_image))
        if encoding:
            encodings.append(encoding[0])

    # Recognize faces
    recognized_names = []
    for encoding in encodings:
        # Compare faces
        matches = face_recognition.compare_faces(known_faces, encoding)

        # Check if any face matches
        if np.any(matches):  # Use np.any() to handle the array properly
            first_match_index = np.where(matches)[0][0]  # Get the index of the first match
            recognized_names.append(known_names[first_match_index])

    return recognized_names







def process_and_save_video(known_faces, known_names, video_file):
    # Check if the video_file has a method for temporary file path or save it to a temp file
    if hasattr(video_file, 'temporary_file_path'):
        video_path = video_file.temporary_file_path()
    else:
        # Save the file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            for chunk in video_file.chunks():
                temp_file.write(chunk)
            video_path = temp_file.name

    # Initialize OpenCV VideoCapture
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {'error': 'Could not open video file.'}

    recognized_faces = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to RGB (face_recognition expects RGB format)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Find face locations and encodings in the frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for encoding in face_encodings:
            matches = face_recognition.compare_faces(known_faces, encoding)
            if np.any(matches):  # Use np.any() to handle the array properly
                first_match_index = np.where(matches)[0][0]
                recognized_faces.append(known_names[first_match_index])

    cap.release()
    os.remove(video_path)  # Clean up the temporary file

    return recognized_faces



def save_encodings(encodings, names):
    with open('encodings.pkl', 'wb') as f:
        pickle.dump({'encodings': encodings, 'names': names}, f)



def load_encodings():
    if not os.path.exists('encodings.pkl'):
        raise FileNotFoundError("The 'encodings.pkl' file was not found. Please ensure it exists or generate it.")
    
    with open('encodings.pkl', 'rb') as f:
        known_faces, known_names = pickle.load(f)
    return known_faces, known_names

def extract_face_encodings_user_create(image_file):
    try:
        image = face_recognition.load_image_file(image_file)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        if face_encodings:
            return [encoding.tolist() for encoding in face_encodings]  # Convert to list for JSON serialization
        return None
    except Exception as e:
        print(f"Error extracting face encodings: {e}")
        return None


def extract_face_encodings(image_file):
    try:
        # Open image file with PIL
        pil_image = Image.open(image_file)

        # Convert image to RGB if it's not already
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # Convert PIL image to numpy array
        image_array = np.array(pil_image)

        # Use face_recognition to get face encodings
        face_locations = face_recognition.face_locations(image_array)
        face_encodings = face_recognition.face_encodings(image_array, face_locations)
        
        # Return the first encoding found (if any)
        if face_encodings:
            return face_encodings[0]
        else:
            return None
    except Exception as e:
        raise ValueError(f"Error processing image: {str(e)}")
