from jwt import encode, decode
from jwt import exceptions
from os import getenv
from datetime import datetime, timedelta
from flask import jsonify

def expire_date(days:int):
	now = datetime.now()
	now += timedelta(days)

	return now

def write_token(data: dict):
	token = encode(payload = {**data, "exp": expire_date(7)}, key=getenv("SECRET_KEY"), algorithm="HS256")
	return token.encode("UTF-8")

def validate_token(token, output=False):
	try:
		if output:
			return decode(token, key=getenv("SECRET_KEY"), algorithms = ["HS256"])
		decode(token, key=getenv("SECRET_KEY"), algorithms = ["HS256"])

	except exceptions.DecodeError:
		response = jsonify({"error","Invalid token"})
		return response
	except exceptions.ExpiredSignatureError:
		response = jsonify({"error","Token expired"})
		return response