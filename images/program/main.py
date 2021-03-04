import RPi.GPIO as GPIO
import servo # servo.py
import rfid  # rfid.py
import ultra # ultra.py
import time
import kamerarevisi as kamera
import requests
GPIO.setwarnings(False)

while True:
    #baca tag rfid
    idRfid, textRfid = rfid.tempel()
    print("id kartu adalah = ", idRfid)
    print("text kartu adalah = ", textRfid)

    # ambil foto
    nomor_pelat = kamera.plate_recognition(idRfid)

    # kirim data
    data = {
    "id_rfid_tag":idRfid,
    "nomor_plat":nomor_pelat
    }
    response = requests.post(
    'http://localhost:5000/apimasuk',
    data=data
    )

    if responsejson['status'] == 'terdaftar' \
            and responsejson['tempat_parkir'] == 'tersedia':
        print('masuk atau keluar')
        nomor_pelat = ""

        # buka palang
        servo.bukaServo()

        # periksa keberadaan mobil
        ultra.jarakMobil(7, 400)

        # tutup palang
        time.sleep(1)
        servo.tutupServo()
            
        GPIO.cleanup()

    elif responsejson['status'] == 'terdaftar' \
            and responsejson['tempat_parkir'] ==\
                 'tidak tersedia':
        print('id terdaftar dan parkir tidak tersedia')
    else :
        print('id tidak terdaftar')