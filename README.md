# Sistem Pendukung Keputuan Pemilihan Smartphone
	Saya dan kelompok saya membuat SPK ini untuk memenuhi TA mata kuliah Decission support system
## Syarat
> Mempunyai akun mongodb dengan nama database : **spkPemilihanSmartphone** dan nama collection : **smartphone, user**
## Langkah - langkah untuk menggunakan repo ini:
* Clone repo <br>
	`git clone https://github.com/mohamadburhan151/Flask-SPK-Pemilihan_smartphone.git`
* Buat virtual environments <br>
	`py -m venv nama_env`
* Aktifkan env <br>
	di windows : `nama_env\Scripts\activate`
	di linux : `source nama_env\bin\activate`
* Install library yang dibutuhkan <br>
	di windows : `pip install -r requirements.txt`
* Buat file .env <br>
	yang berisi : <br>
	* URL_ENDPOINT
	* API_KEY
	* DATABASE
	* DATA_SOURCE
	* COLLECTION
* menjalankan aplikasi di local <br>
	di windows : `flask run`
