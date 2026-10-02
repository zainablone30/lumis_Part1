"""
RAF-DB loader.
Expected folder layout (standard RAF-DB Basic release):

RAF-DB/
├── EmoLabel/
│   └── list_patition_label.txt      # "train_0001.jpg 5" per line
└── Image/
    ├── aligned/                     # *_aligned.jpg (face-cropped, use this)
    └── original/
"""

import os
from PIL import Image
from torch.utils.data import Dataset

RAF_LABELS = {
    0: "Surprise",
    1: "Fear",
    2: "Disgust",
    3: "Happiness",
    4: "Sadness",
    5: "Anger",
    6: "Neutral",
}


class RAFDBDataset(Dataset):
    def __init__(self, root_dir, phase="train", transform=None, use_aligned=True):
        """
        phase: 'train' or 'test'
        """
        self.root_dir = root_dir
        self.transform = transform
        self.use_aligned = use_aligned
        self.image_dir = os.path.join(
            root_dir, "Image", "aligned" if use_aligned else "original"
        )
        label_path = os.path.join(root_dir, "EmoLabel", "list_patition_label.txt")

        self.samples = []
        with open(label_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                img_name, label_str = line.split()
                label = int(label_str) - 1  # RAF-DB labels are 1-indexed

                if phase == "train" and not img_name.startswith("train"):
                    continue
                if phase == "test" and not img_name.startswith("test"):
                    continue

                if use_aligned:
                    base, ext = os.path.splitext(img_name)
                    img_name = f"{base}_aligned{ext}"

                img_path = os.path.join(self.image_dir, img_name)
                if os.path.exists(img_path):
                    self.samples.append((img_path, label))

        if len(self.samples) == 0:
            raise RuntimeError(
                f"No samples found for phase='{phase}'. Check RAF-DB path: {root_dir}"
            )

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label

    def class_counts(self):
        counts = [0] * 7
        for _, label in self.samples:
            counts[label] += 1
        return counts