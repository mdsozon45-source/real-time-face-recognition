from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from .serializers import UserProfileSerializer, FaceRecognitionInputSerializer, FaceRecognitionOutputSerializer
from .utils import load_encodings, recognize_and_save_face, process_and_save_video,extract_face_encodings,extract_face_encodings_user_create
from django.contrib.auth.models import User
from .models import UserProfile
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
import face_recognition
import io
import pickle
import os


class UserProfileCreateAPIView(APIView):
    permission_classes = [AllowAny]  # Allow any user to access this view

    def post(self, request, *args, **kwargs):
        # Initialize the serializer with the request data
        serializer = UserProfileSerializer(data=request.data)

        if serializer.is_valid():
            user_profile = serializer.save()

            # Extract face encodings from uploaded image if available
            image_file = request.FILES.get('image')
            if image_file:
                encoding = extract_face_encodings(image_file)

                if encoding is not None:
                    # Convert numpy array to list before saving
                    user_profile.encoding = encoding.tolist()
                    user_profile.save()

                    # Save encoding to a separate pickle file with the username as the filename
                    self.save_encoding_to_pickle(user_profile.username, encoding)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def save_encoding_to_pickle(self, username, encoding):
        # Directory to store individual pickle files
        encodings_dir = 'encodings/'

        # Ensure the directory exists
        os.makedirs(encodings_dir, exist_ok=True)

        # Create a unique filename based on the username
        filename = f"{username}.pkl"
        filepath = os.path.join(encodings_dir, filename)

        # Save the encoding in a separate pickle file
        with open(filepath, 'wb') as f:
            pickle.dump(encoding.tolist(), f)  # Convert numpy array to list before pickling

        print(f"Saved encoding for {username} at {filepath}")




class FaceRecognitionView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = FaceRecognitionInputSerializer(data=request.data)

        if serializer.is_valid():
            user_id = request.data.get('user_id')
            
            if not user_id:
                return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                known_faces, known_names = self.load_encodings(user_id)
            except Exception as e:
                return Response({'error': f"Failed to load encodings: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if 'image' in request.FILES:
                image_file = request.FILES['image']

                if isinstance(image_file, list):
                    return Response({'error': 'Expected a single image file, but received a list.'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    names = recognize_and_save_face(known_faces, known_names, image_file)
                    return Response({'recognized_faces': names}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({'error': f"Error processing image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            elif 'video' in request.FILES:
                video_file = request.FILES['video']

                try:
                    video_path = video_file.temporary_file_path() if hasattr(video_file, 'temporary_file_path') else video_file
                    names = process_and_save_video(known_faces, known_names, video_path)
                    return Response({'recognized_faces': names}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({'error': f"Error processing video: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'error': 'No image or video provided'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def load_encodings(self, user_id):
        userinfo= UserProfile.objects.get(id=user_id)
        print(userinfo.username)
        encodings_dir = 'encodings/'
        pickle_file_path = os.path.join(encodings_dir, f'{userinfo.username}.pkl')

        if not os.path.exists(pickle_file_path):
            raise FileNotFoundError(f"Encoding file for user {userinfo.username} does not exist")

        with open(pickle_file_path, 'rb') as f:
            encoding = pickle.load(f)
        
        # Return the encoding and username
        return [encoding], [str(userinfo.username)]
