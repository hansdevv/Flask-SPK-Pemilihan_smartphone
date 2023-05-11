from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

URL_ENDPOINT = os.getenv('URL_ENDPOINT')
API_KEY = os.getenv('API_KEY')
DATA_SOURCE = os.getenv('DATA_SOURCE')
DATABASE = os.getenv('DATABASE')
COLLECTION = os.getenv('COLLECTION')

headers = {
	'Content-Type': 'application/json',
	'Access-Control-Request-Headers': '*',
	'api-key': API_KEY, 
}

app = Flask(__name__)

# Konfigurasi untuk tempat penyimpanan file
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'json'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Fungsi untuk memeriksa ekstensi file yang diizinkan
def allowed_file(filename):
	return '.' in filename and \
					filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Fungsi untuk meng-handle permintaan pengunggahan file
@app.route('/upload', methods=['POST'])
def upload_file():
	# Memeriksa apakah ada file yang dikirim dalam permintaan
	if 'file' not in request.files:
			return 'File not found', 400

	file = request.files['file']

	# Memeriksa apakah file diperbolehkan
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		return 'File uploaded successfully', 200
	else:
		return 'File type not allowed', 400

@app.route("/")
def home():
	return render_template('home.html')

@app.route("/tambah-data",  methods=['POST'])
def tambah_data():
	# mengambil data dari form
	nama = request.form['nama']
	harga = request.form['harga']
	ram = request.form['ram']
	memoriInternal = request.form['memori-internal']
	kamera_depan = request.form['kamera-depan']
	ukuran_layar = request.form['ukuran-layar']

	if nama != '' and harga != 0 and ram != 0 and kamera_depan != 0 and ukuran_layar != 0:
		url = URL_ENDPOINT+"/action/insertOne"
		payload = json.dumps({
			"dataSource": DATA_SOURCE,
			"collection": COLLECTION,
			"database": DATABASE,
			"document": {
				'namaSmartphone': nama,
				'harga': harga,
				'ram': ram,
				'memoriInternal': memoriInternal,
				'kameraDepan': kamera_depan,
				'ukuranLayar': ukuran_layar,
			}
		})
		
		response = requests.request("POST", url, headers=headers, data=payload)
		json_response = response.json()
		if json_response['insertedId'] != '':
			return jsonify({
				'status': True,
				'msg':'Data berhasil ditambahkan'
			})
		return jsonify({
			'status': False,
			'msg':'Data gagal ditambahkan'
		})
	return jsonify({
		'status':False,
		'msg':'Inputan data tidak valid, mohon inputkan data dengan sesuai'
	})

@app.route("/edit-data",  methods=['POST'])
def edit_data():
	status = False
	msg = ''
	# mengambil data dari form
	_id= request.form['id-data-smartphone']
	nama = request.form['edit-nama']
	harga = request.form['edit-harga']
	ram = request.form['edit-ram']
	kamera_depan = request.form['edit-kamera-depan']
	ukuran_layar = request.form['edit-ukuran-layar']

	if nama != '' and harga != 0 and ram != 0 and kamera_depan != 0 and ukuran_layar != 0:
		url = URL_ENDPOINT+"/action/updateOne"
		payload = json.dumps({
			"dataSource": DATA_SOURCE,
			"collection": COLLECTION,
			"database": DATABASE,
			"filter": {
				"_id": {"$oid":_id},
			},
			"update": {
				"$set":
					{
					'namaSmartphone': nama,
					'harga': harga,
					'ram': ram,
					'kameraDepan': kamera_depan,
					'ukuranLayar': ukuran_layar,
				}
			}
		})
		
		response = requests.request("POST", url, headers=headers, data=payload)
		if response.status_code == 200:
			json_response = response.json()
			if json_response['matchedCount'] != 1:
				msg = 'Edit data gagal karena id data tidak ditemukan!'
				return
			elif json_response['modifiedCount'] != 1:
				msg = 'data ditemukan, tetapi gagal melakukan edit data!'
				return
			else:
				status = True
				msg = 'Berhasil melakukan edit data :)'
		else:
			msg = f'''Gagal melakukan edit data dengan status code {response.status_code}'''
	return jsonify({
		'status': status,
		'msg': msg,
	})

@app.route('/get-one-data/<string:id>', methods=['POST'])
def get_one_data(id):
	status = False
	msg = ''
	data = {}
	url = URL_ENDPOINT+"/action/findOne"
	payload = json.dumps({
		"dataSource": DATA_SOURCE,
		"collection": COLLECTION,
		"database": DATABASE,
		"filter": {
			"_id": {"$oid":id},
		}
	})

	response = requests.request("POST", url, headers=headers, data=payload)
	json_response = response.json()

	if json_response['document'] != 'null':
		status = True
		data = json_response['document']
	else:
		msg = 'Data not found'
	data = {
		'status' : status,
		'msg': msg,
		'data': data,
	}
	return jsonify(data)

@app.route('/indexData', methods=['POST'])
def index_data():
	status = False
	data = []
	url = URL_ENDPOINT+"/action/find"
	payload = json.dumps({
		"dataSource": DATA_SOURCE,
		"collection": COLLECTION,
		"database": DATABASE,
		"filter": {}
	})
	response = requests.request("POST", url, headers=headers, data=payload)
	json_response = response.json()

	if json_response != 'undefined':
		text = ''
		documents = json_response['documents']
		for doc in documents:
			_id = doc['_id']
			namaSmartphone = doc['namaSmartphone']
			hargaSmartphone = doc['harga']
			ram = doc['ram']
			memoriInternal = doc['memoriInternal']
			kameraDepan = doc['kameraDepan']
			ukuranLayar = doc['ukuranLayar']

			text += f'''
			<tr>
			<td>{namaSmartphone}</td>
			<td>{hargaSmartphone}</td>
			<td>{ram}</td>
			<td>{memoriInternal}</td>
			<td>{kameraDepan}</td>
			<td>{ukuranLayar}</td>
			<td>
				<div class="button-group">
					<button id="{_id}" class="btn btn-info btn-edit"><i class="fas fa-edit" title="Edit Data"></i></button>
					<button id="{_id}" class="btn btn-danger btn-hapus"><i class="fas fa-trash" title="Hapus Data"></i></button>
				</div>
			</td>
			</tr>
			'''
			status = True

	data = {
		'status' : status,
		'res': text,
		'documents': documents,
	}
	return data

@app.route('/delete-one/<string:id>', methods=['DELETE'])
def delete_one(id):
	status = False
	msg = ''

	url = URL_ENDPOINT+"/action/deleteOne"
	payload = json.dumps({
		"dataSource": DATA_SOURCE,
		"collection": COLLECTION,
		"database": DATABASE,
		"filter": {
			"_id": {"$oid":id},
		}
	})

	response = requests.request("POST", url, headers=headers, data=payload)
	json_res = response.json()
	if json_res['deletedCount'] == 1:
		status = True
		msg = 'Data Berhasil dihapus'
		return jsonify(
			{
				'status':status,
				'msg':msg,
			}
		)
	return jsonify(
		{
			'status':status,
			'msg':msg,
		}
	)

@app.route("/metodesaw", methods=['GET', 'POST'])
def methode_saw():
	return render_template('metode-spk-saw.html')

def getData(id):
	url = URL_ENDPOINT+"/action/findOne"
	payload = json.dumps({
		"dataSource": DATA_SOURCE,
		"collection": COLLECTION,
		"database": DATABASE,
		"filter": {
			"_id": {"$oid":id},
		}
	})

	response = requests.request("POST", url, headers=headers, data=payload)
	json_response = response.json()
	return json_response['document']

def getAllDataTrainig():
	data = {}
	_id = []

	url = URL_ENDPOINT+"/action/find"
	payload = json.dumps({
		"dataSource": DATA_SOURCE,
		"collection": COLLECTION,
		"database": DATABASE,
		"filter": {}
	})
	response = requests.request("POST", url, headers=headers, data=payload)
	json_response = response.json()
	if json_response != 'undefined':
		documents = json_response['documents']
		for doc in documents:
			data[doc['_id']]={
				'C1':doc['harga'],
				'C2':doc['ram'],
				'C3':doc['memoriInternal'],
				'C4':doc['kameraDepan'],
				'C5':doc['ukuranLayar'],
			}
			_id.append({doc['_id'] : doc['namaSmartphone']})
		return {'data':data, 'id':_id}

@app.route("/indexRanking", methods=['POST'])
def index_ranking():
	status = False
	res = []

	allData = getAllDataTrainig()
	data = allData["data"]

	if len(data) != 0:
		status = True

		kriteria = {
			'C1' : {'rating' : 25, 'atribut' : 'cost'},
			'C2' : {'rating' : 20, 'atribut' : 'benefit'},
			'C3' : {'rating' : 20, 'atribut' : 'benefit'},
			'C4' : {'rating' : 20, 'atribut' : 'benefit'},
			'C5' : {'rating' : 15, 'atribut' : 'benefit'},
			'C5' : {'rating' : 15, 'atribut' : 'benefit'}
		}

		# mendapatkan rating kriteria 
		rating =[kriteria[i]['rating'] for i in kriteria.keys()]

		# normalisasi bobot 
		bobot = [val/sum(rating) for val in rating]

		C_MaxMin = []

		#perulangan utk dpt atribut kriteria
		for key in kriteria.keys():
			C = [
				data[i][key] for i in data.keys()
			]

			#periksa atribut apkah cost / benefit
			if kriteria[key]['atribut'] == 'benefit':
				C_MaxMin.append(max(C))
			else:
				C_MaxMin.append(min(C))
		
		#normalisasi
		norms = []
		v = []
		n=0
		for vals in data.values():
			norm = []
			i = 0
			vn = 0
			#langkah mendapat atribut kriteria
			for key, val in vals.items():
				#cek atribut apakah cost / benefit
				if kriteria[key]['atribut'] == 'benefit':
					n = float(val)/float(C_MaxMin[i]) #menyimpan normalisasi dlam var n
				else:
					C_MaxMin.append(min(C))
				
				#menghitung vn
				vn += (n * bobot[i])
				norm.append(n)
				i+=1
			#simpan hasil normalisasi
			norms.append(norm)
			#simpan vn ke dalam vektor v
			v.append(vn)
		
		# #langkah perangkingan
		rank = {}
		i = 0
		for key in data.keys():
			rank[key] = v[i]
			i+=1

		sorted_rank = sorted(
			[
				(value, key) for (key, value) in rank.items()
			], reverse=True
		)

		for i in sorted_rank:
			cek = getData(i[1])
			res.append([i[0],cek])

	return jsonify({'status': status,'res': res,})

@app.route("/metodewp")
def methode_wp():
	return render_template('metode-spk-wp.html')

# testing local
# if __name__ == "__main__":
# 	app.run(debug=True)