import base64

from flask import request, url_for, make_response, Response
from flask import Flask, url_for
from flask_api import FlaskAPI, status, exceptions
from flask import abort
from Crypto.Cipher import AES
from Crypto.Hash import SHA512, SHA256
from Crypto.PublicKey import RSA
import requests
import json as JSON

from services.Cipher import AESCipher, decrypt_aes, decrypt_rsa, verify_rsa, ds_check, encrypt_aes, encrypt_rsa, \
	sign_message
from services.converter import bytes_to_array, json
from services.keys import *
from Crypto import Random


app = Flask(__name__)

@app.route("/test", methods=["POST", "GET"])
def test():
	# if not request.json:
	# 	abort(400)

	#Fetch data
	data = request.form.to_dict()
	b64_authdata_encrypted = data.get('b64_authdata_encrypted', '')
	b64_k3_encrypted = data.get('b64_k3_encrypted')
	b64_authdata_signature = data.get('b64_authdata_signature')

	#Decode base64
	k3_encrypted = base64.b64decode(b64_k3_encrypted)
	authdata_encrypted = base64.b64decode(b64_authdata_encrypted)
	authdata_signature = base64.b64decode(b64_authdata_signature)

	#decrypt k3
	krpg = paymentgateway
	k3 = decrypt_rsa(krpg, k3_encrypted)

	#decrypt authdata
	aes = AESCipher(k3)
	authdata = aes.decrypt(authdata_encrypted)
	print("authdata", authdata)

	#verify hash_authdata_signature
	kum = merchant.publickey()
	if verify_rsa(kum, authdata, authdata_signature):
		#fetch data
		gateway_part_encrypted = data.get('gateway_part_encrypted')
		k2_encrypted = data.get('k2_encrypted')
		iv2 = data.get('iv2')
		iv1 = data.get('iv1')
		b64_k1_encrypted = data.get('b64_k1_encrypted')
		k1_encrypted = base64.b64decode(b64_k1_encrypted)

		#Decrypt k2_encrypted
		krpg = paymentgateway
		k2 = decrypt_rsa(krpg, bytes.fromhex(k2_encrypted))
		print("k2", k2, bytes_to_array(k2))

		#Decrypt gateway_part_encrypted
		gateway_part = decrypt_aes(k2, iv2, gateway_part_encrypted)
		gateway_part = JSON.loads(gateway_part)
		print("gateway_part", gateway_part)

		#Fetch from gateway_part
		pi = gateway_part.get('pi')
		oimd = gateway_part.get('oimd')
		ds = gateway_part.get('ds')

		#Decrypt k1
		k1 = decrypt_rsa(krpg, k1_encrypted)
		print("k1", k1, bytes_to_array(k1))

		if ds_check(oimd, pi, ds, k1, iv1, merchant=False):
			response = requests.post("http://0.0.0.0:8003/api/authorization", data={'authdata': authdata,'pi': pi})
			if response.status_code == 200:
				print("bank_response", response.json())
				bank_response = response.json()['data']

				authresponse = bank_response.get('authresponse')
				bankcertificate = bank_response.get('bankcertificate')
				b64_kuis = bank_response.get('b64_kuis')

				#Encrypt authresponse
				k4 = Random.get_random_bytes(16)
				authresponse_encrypted = encrypt_aes(k4, authresponse)

				#Encrypt K4
				k4_encrypted = encrypt_rsa(kum,k4)

				#Sign authresponse
				authresponse_signature = sign_message(krpg, authresponse.encode())

				print("authresponse_signature", authresponse_signature)
				print("k4_encrypted", k4_encrypted)
				print("authresponse_encrypted", authresponse_encrypted)
				print("bankcertificate", bankcertificate)

				#Encode Base64
				b64_authresponse_encrypted = base64.b64encode(authresponse_encrypted)
				b64_k4_encrypted = base64.b64encode(k4_encrypted)
				b64_authresponse_signature = base64.b64encode(authresponse_signature)
				b64_bankcertificate = base64.b64encode(bankcertificate.encode())
				print("b64_authresponse_encrypted", b64_authresponse_encrypted)
				print("b64_k4_encrypted", b64_k4_encrypted)
				print("b64_authresponse_signature", b64_authresponse_signature)
				print("b64_bankcertificate", b64_bankcertificate)

				return make_response(json({'b64_authresponse_signature': b64_authresponse_signature.decode(),
										   'b64_k4_encrypted': b64_k4_encrypted.decode(),
										   'b64_authresponse_encrypted': b64_authresponse_encrypted.decode(),
										   'b64_bankcertificate': b64_bankcertificate.decode(),
										   'b64_kuis': b64_kuis}))
		else:
			msg = 'message went wrong during transmission, hashes dont match'
			return make_response(json({'message': msg}))
	else:
		msg = 'Authdata went wrong during transmission, failed to verify signature'
		return make_response(json(msg))
	return "OK"


@app.route("/password", methods=["POST"])
def password():
	data = request.form.to_dict()

	# Fetch data
	b64_pwd_kuisencrypted_and_hashed_k6encrypted = data.get('b64_pwd_kuisencrypted_and_hashed_k6encrypted')
	b64_k7_encrypted_kupg = data.get('b64_k7_encrypted_kupg')
	b64_authdata_signature = data.get('b64_authdata_signature')
	b64_authdata_encrypted_k7 = data.get('b64_authdata_encrypted_k7')
	b64_k6_encrypted_kupg = data.get('b64_k6_encrypted_kupg')
	b64_iv6 = data.get('b64_iv6')

	#Decode Base64
	pwd_kuisencrypted_and_hashed_k6encrypted = base64.b64decode(b64_pwd_kuisencrypted_and_hashed_k6encrypted)
	k7_encrypted_kupg = base64.b64decode(b64_k7_encrypted_kupg)
	authdata_signature = base64.b64decode(b64_authdata_signature)
	authdata_encrypted_k7 = base64.b64decode(b64_authdata_encrypted_k7)
	k6_encrypted_kupg = base64.b64decode(b64_k6_encrypted_kupg)
	iv6 = base64.b64decode(b64_iv6)

	#Decrypt K7
	krpg = paymentgateway
	print("k7_encrypted_kupg", k7_encrypted_kupg)
	k7 = decrypt_rsa(krpg,k7_encrypted_kupg)

	#Decrypt AuthData
	authdata = AESCipher(k7).decrypt(authdata_encrypted_k7)

	# verify authdata_signature
	kum = merchant.publickey()
	if not verify_rsa(kum, authdata, authdata_signature):
		msg = 'message went wrong during transmission, hashes dont match'
		return make_response(json({'message': msg}))

	#Decrypt K6 with Krpg
	print("k6_encrypted_kupg", k6_encrypted_kupg)

	from Crypto.Cipher import PKCS1_OAEP
	k6 = PKCS1_OAEP.new(krpg).decrypt(bytes.fromhex(k6_encrypted_kupg.decode()))

	print("pwd_kuisencrypted_and_hashed_k6encrypted", pwd_kuisencrypted_and_hashed_k6encrypted)
	#Decrypt pwd_kuisencrypted_and_hashed_k6encrypted
	pwd_kuisencrypted_and_hashed = decrypt_aes(k6,iv6.decode(), pwd_kuisencrypted_and_hashed_k6encrypted.decode())
	pwd_kuisencrypted = pwd_kuisencrypted_and_hashed[:-32]
	hashed = pwd_kuisencrypted_and_hashed[len(pwd_kuisencrypted):]

	#Hash pwd_kuisencrypted
	pwd_kuisencrypted_hashed = SHA256.new(pwd_kuisencrypted).hexdigest()
	pwd_kuisencrypted_hashed = bytes.fromhex(pwd_kuisencrypted_hashed)
	if not pwd_kuisencrypted_hashed == hashed:
		msg = 'message went wrong during transmission, hashes dont match'
		return make_response(json({'message': msg}))

	print("authdata", authdata)

	#Base64 Encode
	b64_authdata = base64.b64encode(authdata)
	b64_pwd_kuisencrypted = base64.b64encode(pwd_kuisencrypted)

	bank_response = requests.post("http://0.0.0.0:8003/api/password",
								  data={'b64_authdata': b64_authdata,
										'b64_pwd_kuisencrypted': b64_pwd_kuisencrypted})
	if not bank_response.status_code == 200:
		msg = "Can't communicate with issue banker"
		return make_response(json({'message': msg}))
	print("bank_response.content", bank_response.content)
	msg = "OK"
	return make_response(json({'message': msg}))

@app.route("/start", methods=["POST"])
def start():
	if not request.json:
		abort(400)

	authdata = request['authdata']
	k3 = request['k3']
	hash_authdata = request['hash_authdata']
	pi = request['pi']
	k2 = request['k2']
	iv2 = request['iv2']
	iv3 = request['iv3']
	iv5 = request['iv5']

	k2 = paymentgateway.decrypt(k2)
	aes = AES.new(k2, AES.MODE_CFB, iv3)
	pi = aes.decrypt(pi)
	oimd  = pi[-128:]
	aes = AES.new(k2, AES.MODE_CFB, iv2)
	pomd2 = aes.decrypt(pi[-256:-128])
	payment_information = pi[:-256]

	if SHA512.new(oimd+SHA512(payment_information)).hexdigest() != pomd2:
		return 'hashes dont match, dual signature corrupted'

	aes = AES.new(k3, AES.MODE_CFB, iv5)
	authdata = aes.decrypt(authdata)

	if SHA512.new(authdata).hexdigest() != hash_authdata:
		return 'hashes dont match'

	authrequest = "hi this guy wants to transact"

	response = requests.post("http://localhost:/8003/start", data = {'authrequest': authrequest, 'pi': pi})

	data = response.json()

	if data['authresponse'] != 'cool, here is my certificate':
		return 'error'

	if not data.has_key('bankcertificate'):
		return 'error'

	k4 = Random.get_random_bytes(16)
	iv = Random.get_random_bytes(16)
	authdata = 'everything is good'
	signature = paymentgateway.sign(SHA512.new(authdata).hexdigest())
	aes = AES.new(k4, AES.MODE_CFB, iv)
	authdata = aes.encrypt()
	k4 = paymentgateway.encrypt(k4)

	data = {'authdata': authdata, 'k4': k4, 'iv': iv, 'signature': signature, 'certificate': data['certificate']}

	return data

@app.route("/password1", methods=["POST"])
def password1():
	if not request.json:
		abort(400)

	k7 = paymentgateway.decrypt(request['k7'])
	i7 = request['i7']
	authdata = request['authdata']
	hash_authdata = request['hash_authdata']
	epassword  = request['epassword']
	k5 = paymentgateway.decrypt(request['k5'])
	i5 = request['i5']

	aes = AES.new(k7, AES.MODE_CFB, i7)
	authdata = aes.decrypt(authdata)

	if SHA512.new(authdata).hexdigest() != SHA512.hash_authdata:
		return 'auth data doesnt verify hash'

	aes = AES.new(k5, AES.MODE_CFB, i5)
	password = aes.decrypt(epassword)

	pas_auth = password[-128:]
	encryptedpassword = password[:-128]

	# if SHA512.new(encrypted_otp) != encryptedpassword:
	# 	return 'password corrupted while sending'

	# response = request.post("http://localhost:8003/password", {'encryptedpassword': encryptedpassword, 'authdata': 'hello'})

	data = request.json()
	authdata = data['authdata']

	if authdata != 'the passwords match':
		return 'error, passwords dont match'

	authdata = 'everything is good'
	signature = paymentgateway.sign(SHA512.new(authdata).hexdigest)
	k1 = Random.get_random_bytes(16)
	i1 = Random.get_random_bytes(16)
	aes = AES.new(k1, AES.MODE_CFB, i1)
	encrypted_authdata =aes.encrypt(authdata)
	k1 = paymentgateway.encrypt(k1)

	return {'authdata': authdata, 'k4': k1, 'i4': i1, 'signature': signature}

@app.route("/otp", methods=["POST"])
def otp():
	if not request.json:
		abort(400)

	k11 = paymentgateway.decrypt(request['k11'])
	i11 = request['i11']
	authdata = request['authdata']
	hash_authdata = request['hash_authdata']
	eotp  = request['eotp']
	k9 = paymentgateway.decrypt(request['k9'])
	i9 = request['i9']

	aes = AES.new(k11, AES.MODE_CFB, i11)
	authdata = aes.decrypt(authdata)

	if SHA512.new(authdata).hexdigest() != SHA512.hash_authdata:
		return 'auth data doesnt verify hash'

	# aes = AES.new(k5, AES.MODE_CFB, i5)
	# otp = aes.decrypt(eotp)

	pas_auth = otp[-128:]
	encrypted_otp = otp[:-128]


	if SHA512.new(encrypted_otp) != pas_auth:
		return 'otp corrupted while sending'


	response = request.post("http://localhost:8003/otp", {'encrypted_otp': encrypted_otp, 'authdata': 'hello'})

	data = request.json()
	authdata = data['authdata']

	if authdata != 'the otp matches':
		return 'error, otp dont match'

	authdata = 'everything is good'
	signature = paymentgateway.sign(SHA512.new(authdata).hexdigest)
	k1 = Random.get_random_bytes(16)
	i1 = Random.get_random_bytes(16)
	aes = AES.new(k1, AES.MODE_CFB, i1)
	encrypted_authdata =aes.encrypt(authdata)
	k1 = paymentgateway.encrypt(k1)

	return {'authdata': authdata, 'kx': k1, 'iv': i1, 'signature': signature}


if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True, port=8002)