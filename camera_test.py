import cv2

CAMERA=0 #Kameras ID

cap = cv2.VideoCapture(CAMERA, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

if not cap.isOpened():
    print(f"Kamera ar ID {CAMERA} nav pieejama.")
    exit(1)

try:
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Neizdevās nolasīt kadru no kameras.")
            break
        cv2.imshow("Kamera", frame)

        key=cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()