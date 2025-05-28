from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from typing import List
from rest_framework.permissions import AllowAny
from disease_prompt.disease_detection import predict, DiseaseDataset

class DiseaseDetectionView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        """
        API endpoint to detect disease based on symptoms.
        
        Expects a JSON payload with a 'symptoms' key containing a list of strings.
        Example: {"symptoms": ["fever", "lethargy", "coughing"]}
        
        Returns the predicted disease.
        """
        symptoms = request.data.get('symptoms', None)
        
        if not symptoms or not isinstance(symptoms, list):
            return Response(
                {"error": "Invalid input. 'symptoms' must be a list of strings."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Paths
            model_path = './disease_prompt/result/disease_model.pt'
            label_path = './disease_prompt/result/label_encoder.pkl'
            dataset_path = './disease_prompt/dataset/Training.csv'
            
            # Load dataset to get symptom list
            dataset = DiseaseDataset(dataset_path)
            symptom_list = dataset.get_symptoms()
            
            # Predict
            prediction = predict(
                model_path=model_path,
                label_encoder_path=label_path,
                input_data=symptoms,
                symptom_list=symptom_list
            )
            
            return Response(
                {"predicted_disease": prediction},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )