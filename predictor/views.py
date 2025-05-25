from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from PIL import Image
import torch
from torchvision import transforms
import pickle
import os
from rest_framework.permissions import AllowAny 


from image_training.img_det import MultiLabelCNN 

# Define the image transformation
# This should be the same transform used during training
TRANSFORM = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
])

# Define paths to your model and labels file
MODEL_PATH = os.path.join('image_training', 'results', 'multilabel_cnn_final.pt')
LABEL_PATH = os.path.join('labels.pkl')

# Load labels and initialize the model once when the server starts
with open(LABEL_PATH, 'rb') as f:
    LABEL_NAMES = pickle.load(f)

MODEL = MultiLabelCNN(num_classes=len(LABEL_NAMES))
MODEL.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu'))) # Use map_location for CPU
MODEL.eval()

class ImagePredictionView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image')

        if not image_file:
            return Response({"error": "An image file is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Open the image and convert to RGB
            image = Image.open(image_file).convert("RGB")

            # Apply transformations
            image_tensor = TRANSFORM(image).unsqueeze(0)

            # Make prediction
            with torch.no_grad():
                logits = MODEL(image_tensor)
                probabilities = torch.sigmoid(logits).cpu().numpy()[0]

            # Get predicted labels based on a threshold
            threshold = 0.5
            predictions = [LABEL_NAMES[i] for i, p in enumerate(probabilities) if p >= threshold]

            return Response({"diseases": predictions}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 