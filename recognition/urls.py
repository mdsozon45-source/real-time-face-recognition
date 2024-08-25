from django.urls import path
from .views import FaceRecognitionView, UserProfileCreateAPIView


urlpatterns = [
    path('recognize/', FaceRecognitionView.as_view(), name='face-recognition'),
    path('create-profile/', UserProfileCreateAPIView.as_view(), name='create-profile'),
]
