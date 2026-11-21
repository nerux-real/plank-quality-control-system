#connect AI model + vision
#Right now for test just random lemums
import time
import random
from s7 import Client, util

from ai_model import predict

client = Client()
i=1

def get_random_photo():
    import glob
    import os
    val_dataset = os.path.join(os.path.dirname(__file__), "dataset", "val")
    good_photos = glob.glob(os.path.join(val_dataset, "good", "*.jpg"))
    bad_photos = glob.glob(os.path.join(val_dataset, "bad", "*.jpg"))
    return random.choice(good_photos + bad_photos)

try:
    client.connect("127.0.0.1", 0, 1, tcp_port=1102)
    print("Savienojums ar PLC serveri izveidots.")
    while True:
        time.sleep(random.uniform(0.5, 3))
        random_bilde = get_random_photo()
        print(f"Paņemta bilde: {random_bilde}")
        verdict = predict(random_bilde)

        client.db_write(1, 0, int(verdict).to_bytes(2, byteorder='big')) #ierakstīt datus PLC atmiņā DB1, sākot no 0 baita
        client.db_write(1, 2, int(i).to_bytes(2, byteorder='big'))
        client.db_write(1, 4, (1).to_bytes(1, byteorder='big'))
        print("Dati ierakstīti PLC atmiņā.")
        start_time = time.time()
        while True:
            data = client.db_read(2, 0, 10)
            time_taken = time.time() - start_time
            if util.get_bool(data, 4, 0) and util.get_int(data, 8) == i:
                print(f"PLC serveris ir apstiprinājis dēli nr. {i}.")
                print(f"Laiks līdz apstiprinājumam: {time_taken:.2f} sekundes")
                break
            elif time_taken > 2:
                print("PLC serveris neatbild.")
                break
            else:
                time.sleep(0.05)
        i += 1
except Exception as e:
    print(f"Kļūda savienojoties ar PLC serveri: {e}")
except KeyboardInterrupt:
    print("Savienojums ar PLC serveri tiek pārtraukts.")
finally:
    client.disconnect()
