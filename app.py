from flask import Flask, redirect, render_template, session, request, jsonify, url_for
from datetime import timedelta
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import requests
import json

# init dotenv
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
# app.secret_key digunakan sebagai kunci rahasia untuk menandatangani cookie sesi dan mengamankan data sesi dari manipulasi.
app.secret_key = os.getenv('SECRET_KEY')

@app.before_request
def sesi():
	app.permanent_session_lifetime = timedelta(minutes=60)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

# Konfigurasi untuk tempat penyimpanan file
# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'csv', 'json'}
# MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Fungsi untuk memeriksa ekstensi file yang diizinkan
# def allowed_file(filename):
# 	return '.' in filename and \
# 		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Fungsi untuk meng-handle permintaan pengunggahan file
# @app.route('/upload', methods=['POST'])
# def upload_file():
# 	# Memeriksa apakah ada file yang dikirim dalam permintaan
# 	if 'file' not in request.files:
# 			return 'File not found', 400

# 	file = request.files['file']

# 	# Memeriksa apakah file diperbolehkan
# 	if file and allowed_file(file.filename):
# 		filename = secure_filename(file.filename)
# 		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
# 		return 'File uploaded successfully', 200
# 	else:
# 		return 'File type not allowed', 400

@app.route('/', methods=['GET', 'POST'])
def home():
	if 'username' and 'password' in session:
		return render_template('home.html')
	return redirect('/login')

@app.route("/tambah-data",  methods=['POST'])
def tambah_data():
	if 'username' and 'password' in session:
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
	return redirect('/login')

@app.route("/edit-data",  methods=['POST'])
def edit_data():
	if 'username' and 'password' in session:
		status = False
		msg = ''
		# mengambil data dari form
		_id= request.form['id-data-smartphone']
		nama = request.form['edit-nama']
		harga = request.form['edit-harga']
		ram = request.form['edit-ram']
		memoriInternal = request.form['edit-memori-internal']
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
						'memoriInternal': memoriInternal,
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
	return redirect('/login')

@app.route('/get-one-data/<string:id>', methods=['POST'])
def get_one_data(id):
	if 'username' and 'password' in session:
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

		if json_response['document'] != None:
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
	return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST':
		msg = ''

		# mengambil data dari form
		username = request.form['username']
		password = request.form['password']

		url = URL_ENDPOINT+"/action/findOne"
		payload = json.dumps({
			"dataSource": DATA_SOURCE,
			"collection": "user",
			"database": DATABASE,
			"filter": {
				"username": username,
				"password": password
			}
		})

		response = requests.request("POST", url, headers=headers, data=payload)
		json_response = response.json()

		if json_response['document'] != None:
			if username == json_response['document']['username'] and password == json_response['document']['password']:
				session['username'] = username
				session['password'] = password
				return redirect('/')
			else:
				msg = 'Username atau Password yang anda masukkan salah, silahkan coba lagi'
		else:
			msg = 'Username atau Password tidak ditemukan'
	return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
	# Menghapus data sesi
	session.pop('username', None)
	session.pop('password', None)
	# Redirect ke halaman login atau halaman beranda
	return redirect(url_for('login'))

@app.route('/indexData', methods=['POST'])
def index_data():
	if 'username' and 'password' in session:
		status = False
		data = []
		url = URL_ENDPOINT+"/action/find"
		payload = json.dumps({
			"dataSource": DATA_SOURCE,
			"collection": COLLECTION,
			"database": DATABASE,
			"filter": {},
			"sort": {"_id": -1}
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
					<td style="display: none;">{_id}</td>
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
	return redirect('/login')

@app.route('/delete-one/<string:id>', methods=['DELETE'])
def delete_one(id):
	if 'username' and 'password' in session:
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
	return redirect('/login')

@app.route("/metodesaw", methods=['GET', 'POST'])
def methode_saw():
	if 'username' and 'password' in session:
		return render_template('metode-spk-saw.html')
	return redirect('/login')

def getData(id):
	if 'username' and 'password' in session:
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
	return redirect('/login')

def getAllDataTrainig():
	if 'username' and 'password' in session:
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
					'C1':int(doc['harga']),
					'C2':int(doc['ram']),
					'C3':int(doc['memoriInternal']),
					'C4':float(doc['kameraDepan']),
					'C5':float(doc['ukuranLayar']),
				}
				_id.append({doc['_id'] : doc['namaSmartphone']})
			return {'data':data, 'id':_id}
		return redirect('/login')

@app.route("/indexRanking", methods=['POST'])
def index_ranking():
	if 'username' and 'password' in session:
		paramKriteria = request.get_json()
		test = {}
		j = 1
		for i in paramKriteria:
			test['C' + str(j)] = {'rating': i['rating'], 'atribut': i['atribut']}
			j += 1
		
		status = False
		res = []

		allData = getAllDataTrainig()
		data = allData["data"]

		if len(data) != 0:
			status = True

			kriteria = test

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
						#n = float(val)/float(C_MaxMin[i]) #menyimpan normalisasi dlam var n
						n = val/C_MaxMin[i] #menyimpan normalisasi dlam var n
					else:
						C_MaxMin.append(min(C))
					
					#menghitung vn
					vn += (n * bobot[i])
					norm.append(n)
					i+=1
				#simpan hasil normalisasi
				norms.append(norm)
				#simpan vn ke dalam vektor v
				v.append(round(vn,3))
			
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
	return redirect('/login')

@app.route("/indexRankWp", methods=['POST'])
def index_rank_wp():
	if 'username' and 'password' in session:
		paramKriteria = request.get_json()
		test = {}
		j = 1
		for i in paramKriteria:
			test['C' + str(j)] = {'rating': i['rating'], 'atribut': i['atribut']}
			j += 1
		
		status = False
		res = []

		allData = getAllDataTrainig()
		data = allData["data"]

		if len(data) != 0:
			status = True

			kriteria = test

			# mendapatkan rating kriteria 
			rating =[kriteria[i]['rating'] for i in kriteria.keys()]

			# normalisasi bobot 
			bobot = [val/sum(rating) for val in rating]

			# langkah untuk melakukan perhitungan dengan metode WP
			s = [] # list untuk menyimpan matrix normalisasi 
			for vals in data.values():
				i = 0
				sn = 1
				# langkah mendapatkan atribut kriteria
				for key, val in vals.items():
					if kriteria[key]['atribut'] == 'benefit': 
						sn *=pow(val, bobot[i])
					else:
						sn *=pow(val, -bobot[i])
					i += 1

				s.append(sn)
			
			#perangkingan
			v = [] # list untuk menyimpan vektor v 
			rank = {} #dic untuk menyimpan rangking 
			i = 0
			for key in data.keys():
				nilaiV = s[i]/sum(s)
				v.append(round(nilaiV,3))
				rank[key] =v[i]
				i +=1
			
			sorted_rank = sorted([(value, key) for (key,value) in rank.items()], reverse=True)

			sorted_rank = sorted(
				[
					(value, key) for (key, value) in rank.items()
				], reverse=True
			)

			for i in sorted_rank:
				cek = getData(i[1])
				res.append([i[0],cek])

		return jsonify({'status': status,'res': res,})
	return redirect('/login')

@app.route("/metodewp")
def methode_wp():
	if 'username' and 'password' in session:
		return render_template('metode-spk-wp.html')
	return redirect('/login')

# testing local
# if __name__ == "__main__":
# 	app.run(debug=True)