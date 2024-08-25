from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from .serializers import UserProfileSerializer, FaceRecognitionInputSerializer, FaceRecognitionOutputSerializer
from .utils import recognize_and_save_face, process_and_save_video, load_encodings
from django.contrib.auth.models import User
from .models import UserProfile
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from .serializers import UserProfileSerializer
from .utils import extract_face_encodings
import face_recognition
import io



class UserProfileCreateAPIView(APIView):
    permission_classes = [AllowAny]  # Allow any user to access this view

    def post(self, request, *args, **kwargs):
        # Initialize the serializer with the request data
        serializer = UserProfileSerializer(data=request.data)
        
        # Validate and save the user profile
        if serializer.is_valid():
            user_profile = serializer.save()

            # Extract face encodings from uploaded image if available
            image_file = request.FILES.get('image')
            if image_file:
                encoding = extract_face_encodings(image_file)
                if encoding:
                    user_profile.encoding = encoding
                    user_profile.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class FaceRecognitionView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = FaceRecognitionInputSerializer(data=request.data)
        if serializer.is_valid():
            known_faces = load_encodings()

            if 'image' in request.data:
                image = serializer.validated_data['image']
                names = recognize_and_save_face(known_faces, image)
                return Response({'names': names}, status=status.HTTP_200_OK)

            elif 'video' in request.data:
                video = serializer.validated_data['video']
                names = process_and_save_video(known_faces, video.temporary_file_path())
                return Response({'names': names}, status=status.HTTP_200_OK)

            return Response({'error': 'No image or video provided'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
