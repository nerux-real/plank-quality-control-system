#kā bāzes modeli, es izmantošu Torchvision ResNet18
import torch
from torchvision import datasets, models
from torchvision.transforms import v2
import os
from torch.utils.data import DataLoader

BILDES_IZM=320
MEAN=[0.485, 0.456, 0.406] #vidējās vērtības RGB
STD=[0.229, 0.224, 0.225] #izkliede RGB

#transformācijas apmācībai ar nejaušām izmaiņām, lai no ierobežotas datu kopas iegūtu labāku rezultātu.
train_transform = v2.Compose([
    v2.ToImage(),
    v2.Resize((BILDES_IZM, BILDES_IZM)), #maina attēla izmēru uz 320x320
    v2.RandomHorizontalFlip(),
    v2.RandomVerticalFlip(),
    v2.RandomRotation(5),
    v2.ColorJitter(brightness=0.3, contrast=0.3),
    v2.ToDtype(torch.float32, scale=True),
    v2.Normalize(MEAN, STD),
])

val_transform = v2.Compose([
    v2.ToImage(),
    v2.Resize((BILDES_IZM, BILDES_IZM)),
    v2.ToDtype(torch.float32, scale=True),
    v2.Normalize(MEAN, STD),
])

train_path = os.path.join(os.path.dirname(__file__),"dataset", "train")
val_path = os.path.join(os.path.dirname(__file__), "dataset", "val")

if not os.path.exists(train_path) or not os.path.exists(val_path):
    raise FileNotFoundError(f"Treniņu datu mape '{train_path}' neeksistē. Sākumā jāizpilda 'prepare_dataset.py' skripts, lai sagatvotu datu kopu.")

train_dataset = datasets.ImageFolder(root=train_path, transform=train_transform)
val_dataset = datasets.ImageFolder(root=val_path, transform=val_transform)

print(train_dataset.classes, "klases treniņu datu kopā")
print(len(train_dataset), "attēli treniņu datu kopā")
print(len(val_dataset), "attēli validācijas datu kopā")

train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True, num_workers=0)
val_loader = DataLoader(val_dataset, batch_size=8, shuffle=False, num_workers=0)

print(len(train_loader), "partijas treniņu datu kopā")
print(len(val_loader), "partijas validācijas datu kopā")
images, labels = next(iter(train_loader))
print(images.shape, "attēlu partijas izmērs")
print(labels)

model = models.resnet18(weights="DEFAULT")
for param in model.parameters():
    param.requires_grad = False

model.fc = torch.nn.Linear(model.fc.in_features, 2) #jauns slānis ar 2 klasēm\

outputs = model(images)
print(outputs.shape, "izvades izmērs")

#apmācības cikls'
weights = torch.tensor([2.0, 1.0]) #svara koef, lai liektos vairāk uz bojāto dēli, ja atbildi nezina.
loss_fn = torch.nn.CrossEntropyLoss(weight=weights) #zaudējumu funkcija, kas ņem vērā svara koeficientus
optimizer = torch.optim.Adam(model.fc.parameters(), lr=0.001)
EPOCHS=20
best_acc=0.0

for epoch in range(EPOCHS):
    #1.apmācība
    model.train()
    total_loss=0.0
    for images, labels in train_loader:
        optimizer.zero_grad() #notīra iepriekšējās procijas gradientus
        outputs = model(images) #prognoze
        loss = loss_fn(outputs, labels) #cik ļoti kļūdījās
        loss.backward() #izrēķina gradientus
        optimizer.step() #pabīda svarus
        total_loss += loss.item()

    #2.pārbaude
    model.eval() #pārbaudes režīms
    correct=0
    missed_bad=0 #bojātie dēļi, kruus mi nosauca par labiem
    with torch.no_grad():
        for images, labels in val_loader:
            outputs = model(images)
            preds=outputs.argmax(dim=1) #lielākā no 2 vērtībām: 0=bad, 1=good
            correct+=(preds==labels).sum().item()
            missed_bad+=((labels==0) & (preds==1)).sum().item() #bojātie dēļi, kas tika klasificēti kā labi

    acc=correct/len(val_dataset)
    print(f"""
    \n============================
    Treniņa rezultāti:\n
    Epohs {epoch+1}/{EPOCHS},\n
    Zaudējums: {total_loss/len(train_loader):.3f},\n
    Precizitāte: {acc:.0%},\n
    Nepareizi klasificēti bojātie dēļi: {missed_bad}
    \n============================\n
    """)

    if acc>=best_acc:
        best_acc=acc
        torch.save(model.state_dict(), "plank_model.pth")
        print(f"Labākais modelis saglabāts ar precizitāti: {best_acc:.4f}\n")