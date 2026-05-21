import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import roc_auc_score, average_precision_score, classification_report
import matplotlib.pyplot as plt

# ConvLSTM Cell
class ConvLSTMCell(nn.Module):
    def __init__(self, input_channels, hidden_channels, kernel_size):
        super().__init__()
        self.hidden_channels = hidden_channels
        padding = kernel_size // 2
        self.gates = nn.Conv2d(
            input_channels + hidden_channels,
            4 * hidden_channels,
            kernel_size,
            padding=padding
        )

    def forward(self, x, h, c):
        combined = torch.cat([x, h], dim=1)
        gates = self.gates(combined)
        i, f, g, o = gates.chunk(4, dim=1)
        i = torch.sigmoid(i)
        f = torch.sigmoid(f)
        g = torch.tanh(g)
        o = torch.sigmoid(o)
        c_next = f * c + i * g
        h_next = o * torch.tanh(c_next)
        return h_next, c_next

# Full ConvLSTM HAB Predictor
class ConvLSTMHAB(nn.Module):
    def __init__(self, input_channels=1, hidden_channels=32, 
                 kernel_size=3, patch_size=8):
        super().__init__()
        self.hidden_channels = hidden_channels
        self.patch_size = patch_size
        
        self.convlstm1 = ConvLSTMCell(input_channels, hidden_channels, kernel_size)
        self.convlstm2 = ConvLSTMCell(hidden_channels, hidden_channels, kernel_size)
        
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(hidden_channels, 32),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        # x shape: (batch, time, channels, height, width)
        batch_size = x.shape[0]
        
        h1 = torch.zeros(batch_size, self.hidden_channels, 
                         self.patch_size, self.patch_size).to(x.device)
        c1 = torch.zeros_like(h1)
        h2 = torch.zeros_like(h1)
        c2 = torch.zeros_like(h1)
        
        for t in range(x.shape[1]):
            h1, c1 = self.convlstm1(x[:, t], h1, c1)
            h2, c2 = self.convlstm2(h1, h2, c2)
        
        return self.classifier(h2).squeeze()

# Dataset
class ConvHABDataset(Dataset):
    def __init__(self, X, y):
        # X shape: (samples, time, height, width)
        # Add channel dimension
        self.X = torch.FloatTensor(X).unsqueeze(2)  # (samples, time, 1, H, W)
        self.y = torch.FloatTensor(y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

if __name__ == "__main__":
    print("Loading sequences...")
    X = np.load("data/X_conv_sequences.npy")
    y = np.load("data/y_conv_labels.npy")
    meta = pd.read_csv("data/conv_meta.csv")
    meta['date'] = pd.to_datetime(meta['date'])

    # Handle NaN in patches
    X = np.nan_to_num(X, nan=0.0)

    # Normalize
    X_mean = np.nanmean(X)
    X_std = np.nanstd(X) + 1e-8
    X = (X - X_mean) / X_std

    # Split by year
    train_idx = meta[meta['date'].dt.year <= 2019].index
    val_idx = meta[(meta['date'].dt.year >= 2020) & 
                   (meta['date'].dt.year <= 2022)].index
    test_idx = meta[meta['date'].dt.year >= 2023].index

    print(f"Train: {len(train_idx)} | Val: {len(val_idx)} | Test: {len(test_idx)}")

    X_train, y_train = X[train_idx], y[train_idx]
    X_val, y_val = X[val_idx], y[val_idx]

    train_loader = DataLoader(ConvHABDataset(X_train, y_train), 
                              batch_size=32, shuffle=True)
    val_loader = DataLoader(ConvHABDataset(X_val, y_val), 
                            batch_size=32, shuffle=False)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    model = ConvLSTMHAB(patch_size=8).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    criterion = nn.BCELoss()

    EPOCHS = 30
    best_auc = 0
    patience_counter = 0
    PATIENCE = 5

    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            preds = model(X_batch)
            loss = criterion(preds, y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        model.eval()
        val_preds = []
        with torch.no_grad():
            for X_batch, _ in val_loader:
                X_batch = X_batch.to(device)
                preds = model(X_batch).cpu().numpy()
                val_preds.extend(preds)

        val_auc = roc_auc_score(y_val, val_preds)
        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {total_loss/len(train_loader):.4f} | Val AUC: {val_auc:.4f}")

        if val_auc > best_auc:
            best_auc = val_auc
            torch.save(model.state_dict(), 'data/convlstm_model.pt')
            patience_counter = 0
        else:
            patience_counter += 1
        
        if patience_counter >= PATIENCE:
            print(f"Early stopping at epoch {epoch+1}")
            break

    print(f"\nBest Val AUC: {best_auc:.4f}")
    print(f"XGBoost baseline: 0.936")