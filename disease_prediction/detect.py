from typing import List
from disease_detection import predict, DiseaseDataset

def detect_disease(symptoms: List[str]) -> str:
    """
    Detect disease based on symptoms.
    
    Args:
        symptoms (List[str]): List of symptoms.
        
    Returns:
        str: Predicted disease.
    """
    # Paths
    model_path = './result/disease_model.pt'
    label_path = './result/label_encoder.pkl'
    dataset_path = './dataset/Training.csv'
    
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
    
    return prediction
if __name__ == "__main__":
    symptoms = ['fever', 'lethargy', 'coughing']
    result = detect_disease(symptoms)
    print(f"Predicted Disease: {result}")