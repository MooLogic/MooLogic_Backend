import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import pytorch_lightning as pl
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import torch.nn.functional as F
from torch import nn
import torchmetrics
from typing import List, Dict, Union
import pickle
import os



class DiseaseDataset(Dataset):
    def __init__(self, csv_path):
        self.data = pd.read_csv(csv_path)
        self.symptoms = self.data.columns[:-1].tolist()
        self.labels = self.data['prognosis']

        self.label_encoder = LabelEncoder()
        self.encoded_labels = self.label_encoder.fit_transform(self.labels)

        self.X = self.data[self.symptoms].values.astype('float32')
        self.y = self.encoded_labels.astype('int64')

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return {
            'features': torch.tensor(self.X[idx]),
            'label': torch.tensor(self.y[idx])
        }

    def get_labels(self):
        return list(self.label_encoder.classes_)

    def get_symptoms(self):
        return self.symptoms


class DiseaseClassifier(pl.LightningModule):
    def __init__(self, input_dim, num_classes, lr=1e-3):
        super().__init__()
        self.save_hyperparameters()

        self.model = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, num_classes)
        )

        self.train_acc = torchmetrics.Accuracy(task="multiclass", num_classes=num_classes)
        self.train_precision = torchmetrics.Precision(task="multiclass", num_classes=num_classes, average='macro')
        self.train_recall = torchmetrics.Recall(task="multiclass", num_classes=num_classes, average='macro')
        self.train_f1 = torchmetrics.F1Score(task="multiclass", num_classes=num_classes, average='macro')

        self.val_acc = self.train_acc.clone()
        self.val_precision = self.train_precision.clone()
        self.val_recall = self.train_recall.clone()
        self.val_f1 = self.train_f1.clone()

        self.test_acc = self.train_acc.clone()
        self.test_precision = self.train_precision.clone()
        self.test_recall = self.train_recall.clone()
        self.test_f1 = self.train_f1.clone()

    def forward(self, x):
        return self.model(x)

    def step(self, batch, stage):
        x, y = batch['features'], batch['label']
        logits = self.forward(x)
        loss = F.cross_entropy(logits, y)
        preds = torch.argmax(logits, dim=1)

        metrics = {
            'loss': loss,
            'acc': getattr(self, f'{stage}_acc')(preds, y),
            'precision': getattr(self, f'{stage}_precision')(preds, y),
            'recall': getattr(self, f'{stage}_recall')(preds, y),
            'f1': getattr(self, f'{stage}_f1')(preds, y)
        }
        return metrics

    def training_step(self, batch, batch_idx):
        metrics = self.step(batch, 'train')
        self.log_dict({f'train_{k}': v for k, v in metrics.items()}, prog_bar=True)
        return metrics['loss']

    def validation_step(self, batch, batch_idx):
        metrics = self.step(batch, 'val')
        self.log_dict({f'val_{k}': v for k, v in metrics.items()}, prog_bar=True)

    def test_step(self, batch, batch_idx):
        metrics = self.step(batch, 'test')
        self.log_dict({f'test_{k}': v for k, v in metrics.items()}, prog_bar=True)

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.hparams.lr)


def predict(model_path: str, label_encoder_path: str, 
            input_data: Union[List[str], Dict[str, int]], 
            symptom_list: List[str]):
    with open(label_encoder_path, 'rb') as f:
        label_encoder = pickle.load(f)

    num_classes = len(label_encoder.classes_)
    input_dim = len(symptom_list)

    model = DiseaseClassifier(input_dim=input_dim, num_classes=num_classes)
    model.load_state_dict(torch.load(model_path))
    model.eval()

    if isinstance(input_data, list):
        input_vector = [1 if symptom in input_data else 0 for symptom in symptom_list]
    elif isinstance(input_data, dict):
        if len(input_data) != len(symptom_list):
            raise ValueError("Length of input dictionary must match number of symptoms")
        input_vector = [input_data[symptom] for symptom in symptom_list]
    else:
        raise TypeError("Input must be a list or a dictionary.")

    input_tensor = torch.tensor(input_vector, dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        logits = model(input_tensor)
        predicted_index = torch.argmax(logits, dim=1).item()
        predicted_label = label_encoder.inverse_transform([predicted_index])[0]

    return predicted_label


# Train, Save and Example Prediction
if __name__ == "__main__":
    # Load Dataset
    dataset = DiseaseDataset(r'./dataset/Training.csv')
    model_path = './result/disease_model.pt' 
    label_path = './result/label_encoder.pkl' 
    
    # Split indices
    train_indices, test_indices = train_test_split(range(len(dataset)), test_size=0.2, random_state=42, stratify=dataset.y)
    val_indices, test_indices = train_test_split(test_indices, test_size=0.5, random_state=42, stratify=[dataset.y[i] for i in test_indices])

    train_dataset = torch.utils.data.Subset(dataset, train_indices)
    val_dataset = torch.utils.data.Subset(dataset, val_indices)
    test_dataset = torch.utils.data.Subset(dataset, test_indices)

    # Loaders
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32)
    test_loader = DataLoader(test_dataset, batch_size=32)

    # Model
    model = DiseaseClassifier(input_dim=len(dataset.get_symptoms()), num_classes=len(dataset.get_labels()))

    # Trainer
    trainer = pl.Trainer(max_epochs=10, log_every_n_steps=1)
    trainer.fit(model, train_loader, val_loader)

    # Save Model
    torch.save(model.state_dict(), model_path)

    # Save Label Encoder
    
    with open(label_path, 'wb') as f:
        pickle.dump(dataset.label_encoder, f)

    # Test
    trainer.test(model, test_loader)

    # Predict Example
    sample_symptoms = ['fever', 'lethargy', 'high_temp']
    prediction = predict(
        model_path=model_path, 
        label_encoder_path = label_path,
        input_data=sample_symptoms,
        symptom_list=dataset.get_symptoms()
    )
    print(f"Predicted Disease: {prediction}")

