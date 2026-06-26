import cv2
import socket
import time
from ultralytics import YOLO

# --- AYARLAR ---
ESP32_IP = "192.168.4.1"
CMD_PORT = 8080
STREAM_URL = f"http://{ESP32_IP}:81/stream"

# --- YAPAY ZEKA MODELLERİ ---
print("Modeller Yükleniyor...")
model_person = YOLO('yolo11n.pt')
model_vest = YOLO('best.pt')
print("Sistem Hazır!")

# --- BAĞLANTI ---
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(2)
    client_socket.connect((ESP32_IP, CMD_PORT))
    print(">>> BAĞLANDIM!")
except:
    client_socket = None

cap = cv2.VideoCapture(STREAM_URL, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# --- DEĞİŞKENLER ---
son_komut = "X"
son_tus_zamani = time.time()
TIMEOUT = 0.3
FRAME_CENTER_X = 0  # Görüntü gelince güncellenecek

while True:
    ret, frame = cap.read()
    if not ret: continue

    if FRAME_CENTER_X == 0:
        FRAME_CENTER_X = frame.shape[1] / 2

    # --- 1. YAPAY ZEKA ANALİZ KATMANI ---
    results_p = model_person.predict(frame, classes=[0], conf=0.5, verbose=False)
    results_v = model_vest.predict(frame, conf=0.6, verbose=False)

    is_target = False
    v_center_x = 0

    for p in results_p[0].boxes:
        px1, py1, px2, py2 = map(int, p.xyxy[0])

        for v in results_v[0].boxes:
            vx1, vy1, vx2, vy2 = map(int, v.xyxy[0])
            temp_v_center_x = (vx1 + vx2) / 2
            temp_v_center_y = (vy1 + vy2) / 2

            if (px1 < temp_v_center_x < px2) and (py1 < temp_v_center_y < py2):
                is_target = True
                v_center_x = temp_v_center_x  # Takip için merkez koordinatı al
                break

        color = (0, 0, 255) if is_target else (0, 255, 0)
        label = "HEDEF" if is_target else "Sivil"
        cv2.rectangle(frame, (px1, py1), (px2, py2), color, 2)
        cv2.putText(frame, label, (px1, py1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # --- 2. OTONOM KARAR VE MOTOR KOMUTU ---
    current_komut = "X"  # Başlangıçta dur

    if is_target:
        hata_x = v_center_x - FRAME_CENTER_X

        # --- KADEMELİ KONTROL STRATEJİSİ ---
        # Hedef merkeze yakınsa (Örn: -80 ile 80 arası), SADECE İLERİ GİT.
        # Bu aralıkta robotun sağa-sola kafa atmasını engelliyoruz.

        GUVENLI_BOLGE = 80  # Bu aralıkta sadece ileri (W)
        KRITIK_BOLGE = 150  # Bu aralıkta yönelme başlasın

        if abs(hata_x) < GUVENLI_BOLGE:
            current_komut = "W"  # Hedef merkezde, düz devam

        elif hata_x < -KRITIK_BOLGE:
            current_komut = "A"  # Hedef çok solda, mecbur keskin dön

        elif hata_x > KRITIK_BOLGE:
            current_komut = "D"  # Hedef çok sağda, mecbur keskin dön

        else:
            # Hedef güvenli bölgenin hemen dışındaysa yine W gönder.
            # STM32 tarafındaki 'Bias' (Sol motoru güçlü sürme)
            # zaten bu küçük sapmayı yolda giderken kendisi düzeltecektir.
            current_komut = "W"

    # --- 3. MANUEL KONTROL (Öncelikli) ---
    key = cv2.waitKey(1) & 0xFF
    if key != 255:  # Eğer bir tuşa basıldıysa otonom komutu ez
        if key == ord('w'):
            current_komut = "W"
        elif key == ord('s'):
            current_komut = "S"
        elif key == ord('a'):
            current_komut = "A"
        elif key == ord('d'):
            current_komut = "D"
        elif key == ord('q'):
            break

    # --- 4. KOMUT GÖNDERİM MANTIĞI ---
    if current_komut != "X":
        aktarilacak_komut = current_komut
        son_tus_zamani = time.time()
    else:
        if time.time() - son_tus_zamani < TIMEOUT:
            aktarilacak_komut = son_komut
        else:
            aktarilacak_komut = "X"

    if aktarilacak_komut != son_komut:
        if client_socket:
            client_socket.send(aktarilacak_komut.encode())
            print(f"Aktif Komut: {aktarilacak_komut} | Hedef: {is_target}")
        son_komut = aktarilacak_komut

    cv2.imshow("Muhtas-2 - Otonom Hedef Takip", frame)

cap.release()
if client_socket: client_socket.close()
cv2.destroyAllWindows()