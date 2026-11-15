import os
import random
import shutil
import glob

deli_mape_dir = os.path.join(os.path.dirname(__file__), "DELI_Train", "DELI")
l_segments_dir = os.path.join(deli_mape_dir, "..", "L_segments")
dataset_dir = os.path.join(os.path.dirname(__file__), "dataset")

if os.path.exists(dataset_dir):
    shutil.rmtree(dataset_dir)

for split in ["train", "val"]:
    for cls in ["good", "bad"]:
        os.makedirs(os.path.join(dataset_dir, split, cls), exist_ok=True)

def get_name(path):
    return os.path.splitext(os.path.basename(path))[0]

bad_files = sorted(glob.glob(os.path.join(deli_mape_dir, "B_*.jpg")), key=lambda x: int(get_name(x).split("_")[1]))
good_files = sorted(glob.glob(os.path.join(deli_mape_dir, "L_*.jpg")), key=lambda x: int(get_name(x).split("_")[1]))
l_segments = sorted(glob.glob(os.path.join(l_segments_dir, "*.jpg")), key=lambda x: int(get_name(x).split("_")[1]))

print(len(bad_files), "bad files found")
print(len(good_files), "good files found")
print(len(l_segments), "L segments found")

random.seed(42)
val_names = set()
random.shuffle(bad_files)
random.shuffle(good_files)
val_names.update([get_name(f) for f in bad_files[:4]])
val_names.update([get_name(f) for f in good_files[:3]])

print("Validation set names:", val_names)

for path in bad_files+good_files:
    name = get_name(path)
    class_name = "bad" if name.startswith("B_") else "good"
    split = "val" if name in val_names else "train"
    dest_dir = os.path.join(dataset_dir, split, class_name)
    shutil.copy(path, dest_dir)

for path in l_segments:
    name = get_name(path)
    original_name = name.split("_")[0] + "_" + name.split("_")[1]
    split = "val" if original_name in val_names else "train"
    dest_dir = os.path.join(dataset_dir, split, "good")
    shutil.copy(path, dest_dir)

print(len(os.listdir(os.path.join(dataset_dir, "train", "bad"))), "bad files in train")
print(len(os.listdir(os.path.join(dataset_dir, "train", "good"))), "good files in train")
print(len(os.listdir(os.path.join(dataset_dir, "val", "bad"))), "bad files in validation")
print(len(os.listdir(os.path.join(dataset_dir, "val", "good"))), "good files in validation")