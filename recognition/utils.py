import face_recognition
import cv2
import pickle
from .models import RecognizedFace, UserProfile
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image

def recognize_and_save_face(known_faces, face_image, user=None):
    image = face_recognition.load_image_file(face_image)
    unknown_encodings = face_recognition.face_encodings(image)

    if len(unknown_encodings) == 0:
        return None

    results = []
    for known_face in known_faces:
        match = face_recognition.compare_faces([known_face['encoding']], unknown_encodings[0])
        if match[0]:
            results.append(known_face['name'])
            recognized_user = UserProfile.objects.get(user__username=known_face['name']).user
            
            # Save the recognized face
            recognized_face = RecognizedFace(user=recognized_user)
            recognized_face.image.save(face_image.name, face_image)
            recognized_face.save()
            break
    return results

def process_and_save_video(known_faces, video_file_path, user=None):
    video_capture = cv2.VideoCapture(video_file_path)
    recognized_faces = []

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces([face['encoding'] for face in known_faces], face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_faces[first_match_index]['name']
                recognized_user = UserProfile.objects.get(user__username=name).user
                
                # Save recognized face
                recognized_face = RecognizedFace(user=recognized_user)
                recognized_face.video.save(video_file_path, ContentFile(open(video_file_path, 'rb').read()))
                recognized_face.save()

            recognized_faces.append(name)

    video_capture.release()
    return recognized_faces



def save_encodings(encodings, names):
    with open('encodings.pkl', 'wb') as f:
        pickle.dump({'encodings': encodings, 'names': names}, f)

def load_encodings():
    with open('encodings.pkl', 'rb') as f:
        return pickle.load(f)


def extract_face_encodings(image_file):
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