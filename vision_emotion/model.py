"""Export trained model to ONNX for faster inference on Raspberry Pi / Jetson."""
import argparse
import torch
from model import LumisEmotionNet

parser = argparse.ArgumentParser()
parser.add_argument("--checkpoint", required=True)
parser.add_argument("--out", default="lumis_emotion.onnx")
args = parser.parse_args()

model = LumisEmotionNet(num_classes=7, pretrained=False)
model.load_state_dict(torch.load(args.checkpoint, map_location="cpu"))
model.eval()

dummy = torch.randn(1, 3, 224, 224)
torch.onnx.export(
    model, dummy, args.out,
    input_names=["input"], output_names=["output"],
    dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
    opset_version=13,
)
print(f"Exported to {args.out}")