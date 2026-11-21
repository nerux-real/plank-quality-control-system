import os
import torch
from PIL import Image
from torchvision import models
from torchvision.transforms import v2
import cv2

BILDES_IZM=320
MEAN=[0.485, 0.456, 0.406] #vidējās vērtības RGB
STD=[0.229, 0.224, 0.225] #izkliede RGB

val_transform = v2.Compose([
    v2.ToImage(),
    v2.Resize((BILDES_IZM, BILDES_IZM)),
    v2.ToDtype(torch.float32, scale=True),
    v2.Normalize(MEAN, STD),
])

MODEL_PATH = os.path.join(os.path.dirname(__file__), "plank_model.pth")

model = models.resnet18(weights=None)
model.fc = torch.nn.Linear(model.fc.in_features, 2)  # jauns slānis ar 2 klasēm
model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
model.eval()

def predict(image_path):
    image=Image.open(image_path).convert("RGB")
    tensor=val_transform(image).unsqueeze(0)  # pievieno partijas dimensiju
    with torch.no_grad():
        output = model(tensor)
    cls=output.argmax(dim=1).item()
    return 2 if cls==0 else 1

def predict_image(image):
    rgb=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image=Image.fromarray(rgb)
    tensor=val_transform(image).unsqueeze(0)
    with torch.no_grad():
        output = model(tensor)
    cls=output.argmax(dim=1).item()
    return 2 if cls==0 else 1

if __name__=="__main__":
    import glob
    for path in glob.glob(os.path.join(os.path.dirname(__file__), "dataset", "val", "*", "*.jpg")):
        print(os.path.basename(path), "->", "PASS" if predict(path)==1 else "REJECT")