# train.py  (works with RAVDESS / CREMA-D / TESS — not provided, plug in later)
"""
Usage: python train.py --csv_manifest manifest.csv
manifest.csv columns: path,label   (label indices aligned to RAF_LABELS for fusion consistency)
"""
import argparse, numpy as np, pandas as pd, torch
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from features import extract_features
from model import VoiceEmotionMLP

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv_manifest", required=True)
    ap.add_argument("--epochs", type=int, default=40)
    args = ap.parse_args()

    df = pd.read_csv(args.csv_manifest)
    X = np.array([extract_features(p) for p in df["path"]])
    y = df["label"].values

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y)

    train_ds = TensorDataset(torch.tensor(X_train, dtype=torch.float32),
                              torch.tensor(y_train, dtype=torch.long))
    val_ds = TensorDataset(torch.tensor(X_val, dtype=torch.float32),
                            torch.tensor(y_val, dtype=torch.long))

    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=32)

    model = VoiceEmotionMLP(input_dim=X.shape[1], num_classes=int(y.max()) + 1)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    crit = torch.nn.CrossEntropyLoss()

    best_acc = 0
    for epoch in range(args.epochs):
        model.train()
        for xb, yb in train_loader:
            opt.zero_grad()
            loss = crit(model(xb), yb)
            loss.backward()
            opt.step()

        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for xb, yb in val_loader:
                preds = model(xb).argmax(1)
                correct += (preds == yb).sum().item()
                total += yb.size(0)
        acc = correct / total
        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), "voice_emotion_best.pt")
        print(f"Epoch {epoch+1}: val_acc={acc:.3f}")

    print(f"Best voice-emotion val accuracy: {best_acc:.3f}")

if __name__ == "__main__":
    main()