"""
Train LUMIS facial emotion model on RAF-DB.

Usage:
    python train.py --data_root /path/to/RAF-DB --epochs 30 --batch_size 64
"""

import argparse
import os
import copy
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

from dataset import RAFDBDataset, RAF_LABELS
from model import LumisEmotionNet

IMG_SIZE = 224
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]


def get_transforms():
    train_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
        transforms.RandomErasing(p=0.2),
    ])
    eval_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])
    return train_tf, eval_tf


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root", required=True, help="Path to RAF-DB folder")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--out_dir", default="./checkpoints")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    train_tf, eval_tf = get_transforms()
    train_ds = RAFDBDataset(args.data_root, phase="train", transform=train_tf)
    test_ds = RAFDBDataset(args.data_root, phase="test", transform=eval_tf)

    print("Class distribution (train):", dict(zip(RAF_LABELS.values(), train_ds.class_counts())))

    # Handle RAF-DB's known class imbalance (Happiness >> Fear/Disgust)
    labels_arr = np.array([lbl for _, lbl in train_ds.samples])
    class_weights = compute_class_weight(
        class_weight="balanced", classes=np.arange(7), y=labels_arr
    )
    class_weights = torch.tensor(class_weights, dtype=torch.float32).to(device)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                               num_workers=4, pin_memory=True)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False,
                              num_workers=4, pin_memory=True)

    model = LumisEmotionNet(num_classes=7, pretrained=True).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=0.05)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    best_acc = 0.0
    best_state = None
    patience, patience_counter = 7, 0

    for epoch in range(args.epochs):
        model.train()
        running_loss, correct, total = 0.0, 0, 0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * imgs.size(0)
            _, preds = outputs.max(1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

        train_loss = running_loss / total
        train_acc = correct / total

        val_acc, val_loss = evaluate(model, test_loader, criterion, device)
        scheduler.step()

        print(f"Epoch {epoch+1}/{args.epochs} | "
              f"train_loss={train_loss:.4f} train_acc={train_acc:.4f} | "
              f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}")

        if val_acc > best_acc:
            best_acc = val_acc
            best_state = copy.deepcopy(model.state_dict())
            patience_counter = 0
            torch.save(best_state, os.path.join(args.out_dir, "lumis_emotion_best.pt"))
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print("Early stopping triggered.")
                break

    print(f"Best validation accuracy: {best_acc:.4f}")
    print(f"Model saved to {args.out_dir}/lumis_emotion_best.pt")


def evaluate(model, loader, criterion, device):
    model.eval()
    running_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for imgs, labels in loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            running_loss += loss.item() * imgs.size(0)
            _, preds = outputs.max(1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    return correct / total, running_loss / total


if __name__ == "__main__":
    main()