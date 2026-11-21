import cv2
from ai_model import predict_image

ALLOWED_MARGIN = 0.01

def crop_delis(image):
    merogs_x=400/image.shape[1]
    merogs_y=225/image.shape[0]
    image=cv2.resize(image, None, fx=merogs_x, fy=merogs_y)

    gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    otsu_value, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best=None
    best_area=0
    H, W = thresh.shape
    for cnt in contours:
        area=cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        if x <= 2 or y <= 2 or x + w >= W - 2 or y + h >= H - 2:
            continue
        if area>W*H*0.9:
            continue
        if area/(W*H)<0.02:
            continue
        if area>best_area:
            best_area=area
            best=cnt
    return image, merogs_x, merogs_y, thresh, best

print("Available cameras:")
for i in range(10):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        print(f"Camera {i}: Available")
        cap.release()
    else:
        print(f"Camera {i}: Not available")

CAMERA_ID=0

#cap=cv2.VideoCapture(CAMERA_ID, cv2.CAP_DSHOW)
cap=cv2.VideoCapture("http://10.144.169.207:4747/video")
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

def crop_rotated(img, rect):
    (cx, cy), (w, h), ang = rect
    if w > h:
        w, h = h, w
        ang += 90
    w *= 1 + ALLOWED_MARGIN * 2
    h *= 1 + ALLOWED_MARGIN * 2
    M = cv2.getRotationMatrix2D((cx, cy), ang, 1.0)
    rot = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_REPLICATE)
    x0, y0 = int(max(cx - w / 2, 0)), int(max(cy - h / 2, 0))
    x1, y1 = int(min(cx + w / 2, img.shape[1])), int(min(cy + h / 2, img.shape[0]))
    return rot[y0:y1, x0:x1]

try:
    if not cap.isOpened():
        print("Kamera nav pieejama.")
        exit(1)
    while True:
        ok, frame=cap.read()
        if not ok:
            print("Neizdevās nolasīt kadru no kameras.")
            break

        cropped_frame, merogs_x, merogs_y, thresh, best=crop_delis(frame)
        if best is not None:
            cv2.drawContours(cropped_frame, [best], -1, (0, 255, 0), 2)
            (cx, cy), (w, h), ang = cv2.minAreaRect(best)
            cx /= merogs_x
            cy /= merogs_y
            w /= merogs_x
            h /= merogs_y
            plank = crop_rotated(frame, ((cx, cy), (w, h), ang))
            result = predict_image(plank)
            cv2.putText(cropped_frame, "PASS" if result == 1 else "REJECT", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if result == 1 else (0, 0, 255), 2)
            cv2.imshow("Delis", plank)
        cv2.imshow("Kamera", cropped_frame)
        cv2.imshow("Maska", thresh)

        key=cv2.waitKey(1) & 0xFF
        if key==ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()