from flask import Flask, render_template, url_for, \
    request, redirect, jsonify
from flask_mysqldb import MySQL
from flask_api import FlaskAPI, status, exceptions
from random import randint
from math import ceil
import datetime
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'raspberry'
app.config['MYSQL_DB'] = 'skripsi'

mysql = MySQL(app)

@app.route("/", methods=['GET', 'POST'])
def myapp():
    return render_template('main_layout.html')
    # return redirect('/index.html')

@app.route("/parkir.html", methods=['GET', 'POST'])
def layout_parkir():
    plat = ""
    posisi_parkir = ""
    saldo = ""
    table_parkir = load_table_parkir()
    table_rfid_tag = load_table_rfid_tag()
    tempat_parkir = load_table_tempat_parkir()
    text_keterangan = ""
    keterangan = ""
    
    if len(table_parkir) > 0 :
        last = table_parkir[-1]

        waktu_sekarang = datetime.datetime.now()
        if last["waktu_keluar"] == None:
            waktu_masuk = datetime.datetime.\
                strptime(str(last["waktu_masuk"]), \
                    '%Y-%m-%d %H:%M:%S')
            waktu_masuk_5detik = waktu_masuk \
                + datetime.timedelta(seconds=5)
            if waktu_sekarang < waktu_masuk_5detik:
                plat = last["nomor_plat"]
                posisi_parkir = last["id_tempat_parkir"]
                for data in table_rfid_tag:
                    if data["id"] == last["id_rfid_tag"]:
                        saldo = f"Rp. {data['saldo']}"
                        text_keterangan="Posisi"
                        keterangan = posisi_parkir
                        break

        else :
            waktu_keluar = datetime.datetime.\
                strptime(str(last["waktu_keluar"]), \
                    '%Y-%m-%d %H:%M:%S')
            waktu_keluar_5detik = waktu_keluar \
                + datetime.timedelta(seconds=5)
            if waktu_sekarang < waktu_keluar_5detik:
                # print(last)
                tarif = hitung_tarif2(last, last, tempat_parkir)
                plat = last["nomor_plat"]
                posisi_parkir = last["id_tempat_parkir"]
                for data in table_rfid_tag:
                    if data["id"] == last["id_rfid_tag"]:
                        saldo = f"Rp. {data['saldo']}"
                        text_keterangan = "Tarif"
                        keterangan = tarif
                        break
            
    
    
    return render_template('index.html', tempat_parkir \
        = tempat_parkir, keterangan=keterangan, text_keterangan\
            =text_keterangan, posisi_parkir=posisi_parkir, \
                plat=plat, saldo=saldo, time = \
                    str(datetime.datetime.now()))
    

def tentukan_tempat_parkir(tempat_parkir, jenis_kendaraan):
    slot_tersedia = 0
    tempat_parkir_tersedia = []
    for tempat in tempat_parkir:
        if tempat["jenis"] == jenis_kendaraan and\
             tempat["status"] == "Tersedia":
            slot_tersedia = slot_tersedia + 1
            tempat_parkir_tersedia.append(tempat)
    
    if slot_tersedia == 0 :
        return "Penuh"
    index = randint(0,slot_tersedia-1)
    return tempat_parkir_tersedia[index]


@app.route("/pengguna")
def pengguna():
    pengguna = load_table_rfid_tag()
    return render_template("pengguna.html", result=pengguna \
        ,panjangResult=len(pengguna))


def load_table_rfid_tag():
    cur = mysql.connection.cursor()
    cur.execute("select * from rfid_tag")
    tuple_rfid_tag = cur.fetchall()
    mysql.connection.commit()
    cur.close()

    result = []
    for data in tuple_rfid_tag:
        rfid_tag = {
            "id":"",
            "jenis_kendaraan":"",
            "saldo":""
        }
        rfid_tag["id"] = data[0]
        rfid_tag["jenis_kendaraan"] = data[1]
        rfid_tag["saldo"] = data[2]
        result.append(rfid_tag)
    return result


def load_table_tempat_parkir():
    cur = mysql.connection.cursor()
    cur.execute("select * from tempat_parkir")
    tuple_tempat_parkir = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    
    result = []
    for data in tuple_tempat_parkir:
        tempat_parkir = {
            "id":"",
            "jenis":"",
            "tarif":"",
            "status":""
        }
        tempat_parkir["id"] = data[0]
        tempat_parkir["jenis"] = data[1]
        tempat_parkir["tarif"] = data[2]
        tempat_parkir["status"] = data[3]
        result.append(tempat_parkir)
    return result

@app.route("/table_parkir")
def table_parkir():
    table_parkir = load_table_parkir()
    return render_template("table_parkir.html", \
        result=table_parkir ,panjangResult=len(table_parkir))

def load_table_parkir():
    cur = mysql.connection.cursor()
    cur.execute("select * from parkir")
    tuple_parkir = cur.fetchall()
    mysql.connection.commit()
    cur.close()

    result = []
    for data in tuple_parkir:
        parkir = {
            "id":"",
            "id_rfid_tag":"",
            "nomor_plat":"",
            "id_tempat_parkir":"",
            "waktu_masuk":"",
            "waktu_keluar":""
        }
        parkir["id"] = data[0]
        parkir["id_rfid_tag"] = data[1]
        parkir["nomor_plat"] = data[2]
        parkir["id_tempat_parkir"] = data[3]
        parkir["waktu_masuk"] = data[4]
        parkir["waktu_keluar"] = data[5]
        result.append(parkir)
    return result

def update_status_tempat_parkir(tempat_parkir, status):
    cur = mysql.connection.cursor()
    # print("ini status = ",status)
    # print(type(status))
    # print("ini tempat_parkir = ",tempat_parkir)
    # print(type(tempat_parkir))
    cur.execute(f"update tempat_parkir set status='{status}' \
        where id='{tempat_parkir}';")
    mysql.connection.commit()
    cur.close()

def save_table_parkir(kendaraan, tempat_parkir, waktu_masuk \
     = "NULL", waktu_keluar = "NULL"):
    id_rfid_tag = kendaraan["id_rfid_tag"]
    nomor_plat = kendaraan["nomor_plat"]
    
    
    cur = mysql.connection.cursor()
    # masuk
    if waktu_masuk != "NULL":
        id_tempat_parkir = tempat_parkir["id"]
        cur.execute(f"insert into parkir(id_rfid_tag, \
            nomor_plat, id_tempat_parkir, waktu_masuk, \
                waktu_keluar) values ('{id_rfid_tag}', \
                    '{nomor_plat}', '{id_tempat_parkir}', \
                        {waktu_masuk}, NULL) ;")
    # keluar
    elif waktu_keluar != "NULL":
        cur.execute(f"update parkir set waktu_keluar\
            ={waktu_keluar} where id_rfid_tag={id_rfid_tag}\
                 AND id_tempat_parkir='{tempat_parkir}'\
                      AND waktu_keluar is NULL;")
    mysql.connection.commit()
    cur.close()



def save_table_kendaraan(kendaraan):
    nomor_plat = kendaraan["nomor_plat"]
    id_rfid_tag = kendaraan["id_rfid_tag"]

    cur = mysql.connection.cursor()
    cur.execute(f"insert into kendaraan(nomor_plat, \
        id_rfid_tag) values ('{nomor_plat}', \
            '{id_rfid_tag}');")
    mysql.connection.commit()
    cur.close()
    
# @app.route("/test_api", methods=["POST", "GET"])
# def test_api():
#     no_id = request.form["id_rfid_tag"]
#     dd = request.form["nomor_plat"]
#     cek_rfid_tefdaftar=load_table_rfid_tag()
#     for data in cek_rfid_tefdaftar:
#         if data["id"] == no_id:
#             r = {'status':'terdaftar'}
#             return jsonify(r), 200
    
#     print("dari app id tdk terdaftar")
#     r = {'status':'tidak terdaftar','test':'juga'}
#     return jsonify(r)
    

@app.route("/apimasuk", methods=["POST", "GET"])
def api_masuk():
    kendaraan = {
        "id_rfid_tag":"",
        "nomor_plat":"",
        "jenis_kendaraan":""
    }
    kendaraan["id_rfid_tag"] = request.form["id_rfid_tag"]
    kendaraan["nomor_plat"] = request.form["nomor_plat"]

    # table rfid_tag
    table_rfid_tag = load_table_rfid_tag()

    # cek id terdaftar 
    terdaftar = False
    for data in table_rfid_tag:
        if data["id"] == kendaraan["id_rfid_tag"]:
            terdaftar = True
            break

    # id tidak terdaftar
    if not terdaftar:
        cur = mysql.connection.cursor()
        cur.execute("update reload_id set uid = %s \
            where id = 1;", (kendaraan["id_rfid_tag"],))
        # cur.execute("delete from user_id;")
        mysql.connection.commit()
        cur.close()

        r = {'status':'tidak terdaftar', \
            'tempat_parkir':'tidak tersedia'}
        return jsonify(r)
    
    # cek jenis kendaraan
    for rfid_tag in table_rfid_tag:
        id_rfid = rfid_tag["id"]
        jenis_kendaraan = rfid_tag["jenis_kendaraan"]
        if kendaraan["id_rfid_tag"] == id_rfid:
            kendaraan["jenis_kendaraan"] = jenis_kendaraan
            break

    # cek apakah kendaraan masuk atau keluar
    table_parkir = load_table_parkir()
    cek_keluar = False
    for data in table_parkir:
        if data["id_rfid_tag"] == kendaraan["id_rfid_tag"]\
             and data["waktu_keluar"] == None:
            cek_keluar = True
            break
    
    activity = ""
    # Parkir Keluar
    if cek_keluar:
        # cek ini saldo
        tarif = hitung_tarif(kendaraan, table_parkir)

        # update saldo kendaraan
        update_saldo(kendaraan, tarif)  

        tempat_parkir = []
        for data in table_parkir:
            # cocokkan waktu keluar
            if data["id_rfid_tag"] == kendaraan["id_rfid_tag"]\
                 and data["waktu_keluar"] == None: 
                tempat_parkir.append(data)
                break
        
        # update status tempat parkir di table 
        # tempat_parkir menjadi tersedia
        update_status_tempat_parkir(tempat_parkir[0]\
            ['id_tempat_parkir'], "Tersedia")

        # update waktu keluar
        waktu_keluar = "now()"
        save_table_parkir(kendaraan, tempat_parkir[0]\
            ['id_tempat_parkir'], waktu_keluar=waktu_keluar)
        activity = "keluar"
    
    # Parkir Masuk
    else:
        # menentukan tempat parkir
        table_tempat_parkir = load_table_tempat_parkir()
        tempat_parkir = tentukan_tempat_parkir\
            (table_tempat_parkir,kendaraan["jenis_kendaraan"])

        # cek parkir penuh
        if tempat_parkir == "Penuh":
            r = {'status':'terdaftar', 'tempat_parkir'\
                :'tidak tersedia'}
            return jsonify(r)

        # update table parkir
        waktu_masuk = "now()"
        save_table_parkir(kendaraan, tempat_parkir, \
            waktu_masuk=waktu_masuk)

        # update status tempat parkir di table 
        # tempat_parkir menjadi terpakai
        update_status_tempat_parkir(tempat_parkir["id"], \
            "Terpakai")

        # update table kendaraan
        save_table_kendaraan(kendaraan)
        activity = "masuk"
        
    r = {'status':'terdaftar', 'tempat_parkir':'tersedia', \
        'aktivitas':activity}
    return jsonify(r)
        
# ini keluar
def hitung_tarif(kendaraan, table_parkir):
    # print(kendaraan)
    table_tempat_parkir = load_table_tempat_parkir()
    tarif = 0
    for data in table_parkir:
        for tempat_parkir in table_tempat_parkir:
            if data["id_rfid_tag"] == kendaraan["id_rfid_tag"]\
                 and data["waktu_keluar"] == None and \
                    data["id_tempat_parkir"] == \
                        tempat_parkir["id"]: 
                waktu_masuk = datetime.datetime.strptime\
                    (str(data["waktu_masuk"]), \
                        '%Y-%m-%d %H:%M:%S')
                waktu_keluar = datetime.datetime.now()
                durasi = waktu_keluar - waktu_masuk
                durasikonversi = ceil(durasi.total_seconds()\
                    /3600)
                tarif = durasikonversi * int(tempat_parkir\
                    ["tarif"])
                return tarif

    return tarif

def hitung_tarif2(kendaraan, data, table_tempat_parkir):
    tarif = 0
    waktu_masuk = datetime.datetime.strptime(str\
        (data["waktu_masuk"]), '%Y-%m-%d %H:%M:%S')
    waktu_keluar = datetime.datetime.now()
    durasi = waktu_keluar - waktu_masuk
    durasikonversi = ceil(durasi.total_seconds()/3600)
    for tempat_parkir in table_tempat_parkir:
        if tempat_parkir["id"] == data["id_tempat_parkir"]:
            tarif = durasikonversi * int(tempat_parkir\
                ["tarif"])
            break
    return tarif

# ini keluar
def update_saldo(kendaraan, tarif):
    id_rfid = kendaraan["id_rfid_tag"]
    cur = mysql.connection.cursor()
    cur.execute(f"select saldo from rfid_tag \
        where id = {id_rfid};")
    saldoAwal = cur.fetchall()
    # return render_template('test.html', \
    # saldoAwal = saldoAwal[0][0])

    saldoSekarang = saldoAwal[0][0] - int(tarif)

    cur.execute(f"update rfid_tag set saldo=\
        {saldoSekarang} where id={id_rfid};")
    mysql.connection.commit()
    cur.close()


@app.route("/isi_data", methods=["POST", "GET"])
def isi_data():
    if request.method == "POST":
        idRFID = request.form["idRFID"]
        jenis_kendaraan = request.form["jenis_kendaraan"]
        saldo = request.form["saldo"]

        cur = mysql.connection.cursor()
        cur.execute(f"insert into rfid_tag(id, \
            jenis_kendaraan, saldo) values \
                ({idRFID}, '{jenis_kendaraan}', {saldo});")
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("layout_parkir"))
    return render_template('isi_data.html')

@app.route("/reload_id", methods=["GET", "POST"])
def proses():
    cur = mysql.connection.cursor()
    cur.execute("select * from reload_id ;")
    user = cur.fetchone()
    cur.close()

    # print(user[1])
    # print(type(user))
    # return jsonify({'id':user})

    if user == None:
        return jsonify({'id':'otomatis terisi'})

    return jsonify({'id':user[1]})

@app.route("/isi_saldo", methods=["POST", "GET"])
def isi_saldo():
    if request.method == "POST":
        idRFID = request.form["idRFID"]
        saldoIsi = request.form["saldo"]

        cur = mysql.connection.cursor()
        cur.execute(f"select saldo from rfid_tag where id =\
             {idRFID};")
        saldoAwal = cur.fetchall()
        # return render_template('test.html', saldoAwal =\
        #  saldoAwal[0][0])

        saldoSekarang = int(saldoIsi) + saldoAwal[0][0]

        cur.execute(f"update rfid_tag set saldo=\
            {saldoSekarang} where id={idRFID};")
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("layout_parkir"))
    return render_template('isi_saldo.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")