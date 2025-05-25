import os
import json 
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.loggers import CSVLogger
import torchvision.models as models

import pickle 
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl
from torchmetrics.classification import MultilabelPrecision, MultilabelRecall, MultilabelAccuracy


class MultiLabelDataset(Dataset):
    def __init__(self, images_dir, 
                 labels_csv, 
                 transform=None, 
                 save_labels='labels.json', 
                 mode=''): 
        self.images_dir = images_dir
        self.labels_df = pd.read_csv(labels_csv)
        self.transform = transform
        self.labels = self.labels_df.columns[1:].tolist()

        # lab = {}
        # for i in range(len(self.labels)):
        #     lab[i] = self.labels[i]  
        
        # if mode == 'train':
        #     with open(save_labels, 'w') as f:
        #         json.dump(lab, f) 
        
        if mode == 'train':
            with open(save_labels, 'wb') as f:
                pickle.dump(self.labels, f) 

    def __len__(self):
        return len(self.labels_df)

    def __getitem__(self, idx):
        img_name = self.labels_df.iloc[idx, 0]
        img_path = os.path.join(self.images_dir, img_name)
        image = Image.open(img_path).convert("RGB")
        
        if self.transform:
            image = self.transform(image)
        
        labels = self.labels_df.iloc[idx, 1:].values.astype('float32')
        return image, labels

    def get_label_names(self):
        return self.labels
    


class MultiLabelCNN(pl.LightningModule):
    def __init__(self, num_classes, lr=1e-3):
        super().__init__()
        self.save_hyperparameters()

        # self.model = nn.Sequential(
        #     nn.Conv2d(3, 16, 3, padding=1),
        #     nn.ReLU(),
        #     nn.MaxPool2d(2),
        #     nn.Conv2d(16, 128, 3, padding=1),
        #     nn.ReLU(),
        #     nn.AdaptiveAvgPool2d((1, 1)),
        #     nn.Flatten(),
        #     nn.Linear(128, num_classes),
        # )
        
        self.model = models.resnet18(weights=None)
        
        # Replace the final classification layer
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)

        self.criterion = nn.BCEWithLogitsLoss()

        self.train_precision = MultilabelPrecision(num_labels=num_classes, average='macro')
        self.val_precision = MultilabelPrecision(num_labels=num_classes, average='macro')
        self.val_recall = MultilabelRecall(num_labels=num_classes, average='macro')
        self.val_accuracy = MultilabelAccuracy(num_labels=num_classes, threshold=0.5, average='macro')

    def forward(self, x):
        return self.model(x)

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.hparams.lr)
        return optimizer

    def training_step(self, batch, batch_idx):
        images, labels = batch
        logits = self(images)
        loss = self.criterion(logits, labels)
        preds = torch.sigmoid(logits)
        self.train_precision(preds, labels.int())
        self.log("train_loss", loss)
        return loss

    def validation_step(self, batch, batch_idx):
        images, labels = batch
        logits = self(images)
        loss = self.criterion(logits, labels)
        preds = torch.sigmoid(logits)
        self.val_precision(preds, labels.int())
        self.val_recall(preds, labels.int())
        self.val_accuracy(preds, labels.int())
        self.log("val_loss", loss)
        return loss

    def on_validation_epoch_end(self):
        self.log("val_precision", self.val_precision.compute())
        self.log("val_recall", self.val_recall.compute())
        self.log("val_accuracy", self.val_accuracy.compute())
        self.val_precision.reset()
        self.val_recall.reset()
        self.val_accuracy.reset()

def predict_image(image_path, 
                  model_path, 
                  label_path, 
                  transform, 
                  threshold=0.5):
    image = Image.open(image_path).convert("RGB")

    with open(label_path, 'rb') as f:
        label_names = pickle.load(f) 
    
    model = MultiLabelCNN(num_classes=len(label_names)) 
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    image = transform(image).unsqueeze(0).to(model.device)
    with torch.no_grad():
        logits = model(image)
        probs = torch.sigmoid(logits).cpu().numpy()[0]

    predictions = [label_names[i] for i, p in enumerate(probs) if p >= threshold]
    return predictions

from torchvision import transforms

# transform = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.ToTensor(),
# ])

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],   # ImageNet mean
        std=[0.229, 0.224, 0.225]     # ImageNet std
    ),
])

if __name__ == "__main__":

    # Paths
    root_path = r'./image_training/cattle diseases.v2i.multiclass'
    train_dir = os.path.join(root_path, "train") 
    valid_dir = os.path.join(root_path, "valid") 
    train_csv = os.path.join(train_dir, '_classes.csv')
    valid_csv = os.path.join(valid_dir, '_classes.csv')

    # Transforms
    transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
    ])

    # Datasets

    label_path = r'./labels.pkl'
    train_dataset = MultiLabelDataset(train_dir, train_csv, transform, mode='train', 
                                      save_labels=label_path) 
    valid_dataset = MultiLabelDataset(valid_dir, valid_csv, transform)

    # DataLoaders
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=4)
    valid_loader = DataLoader(valid_dataset, batch_size=32, shuffle=False, num_workers=4)

    # Model
    num_classes = len(train_dataset.get_label_names())
    model = MultiLabelCNN(num_classes=num_classes, lr=1e-3)

    # Callbacks & Logger
    checkpoint_callback = ModelCheckpoint(monitor="val_loss", save_top_k=1, mode="min")
    logger = CSVLogger("logs", name="multilabel-cnn")

    # Trainer
    trainer = Trainer(
        max_epochs=10,
        accelerator="auto",
        callbacks=[checkpoint_callback],
        logger=logger,
    )

    # 📝 NOTE: Train gochuu yoo barbaaddan kan uncomment godhaa 
    # trainer.fit(model, train_loader, valid_loader)
    # trainer.validate(model, valid_loader) 
    # torch.save(model.state_dict(), "./image_training/results/multilabel_cnn_final.pt")
    
    diseases = predict_image(
        image_path=r'D:\cattle disease\img1007.jpg', 
        model_path=r'./image_training/results/multilabel_cnn_final.pt', 
        label_path=label_path, 
        transform=transform
    )
    
    print('Diseases: ', diseases)
    