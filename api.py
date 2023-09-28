from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS
from jwt_valid import write_token, validate_token
from dotenv import load_dotenv

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'usuarios'

mysql = MySQL(
    app
)

CORS(app)



@app.route("/")
def ver_usuarios():
    return jsonify(
        {
            'grupo': 4,
            'owners': [
                "Arath",
                "Carlo",
                "Gerald",
                "Roberto",
                "Luis"
            ]}), 200


@app.route("/api/verifyToken", methods=['POST'])
def verify():
    token = request.json['Authorization']
    return validate_token(token, output=True)


@app.route("/api/logUser/", methods=['POST'])
def log_user():
    try:
        data = request.json
        if 'username' in data and 'password' in data:
            username = data['username']
            password = data['password']

            cursor = mysql.connection.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()

            if user:
                token = write_token({**data, 'logged': True})
                return jsonify({"authenticated": True, "username": username, "token": token.decode('utf-8')})

            else:
                return jsonify({"authenticated": False, "message": "Credenciales incorrectas"})
        else:
            return jsonify({"error": "Faltan datos de autenticación en la solicitud"})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/api/addUser/", methods=['POST', 'GET'])
def add_user():
    if request.method == 'POST':
        data = request.json
        try:
            cursor = mysql.connection.cursor()

            cursor.execute(
                "SELECT username FROM users WHERE username = %s", (data['username'],))
            existing_username = cursor.fetchone()

            cursor.execute(
                "SELECT email FROM users WHERE email = %s", (data['email'],))
            existing_email = cursor.fetchone()

            cursor.execute(
                "SELECT dni FROM users WHERE dni = %s", (data['dni'],))
            existing_dni = cursor.fetchone()

            cursor.close()

            if existing_username:
                return jsonify({"Error": "El nombre de usuario ya existe. Elija otro nombre de usuario."})

            if existing_email:
                return jsonify({"Error": "El email ya existe. Proporcione una dirección de correo electrónico diferente."})

            if existing_dni:
                return jsonify({"Error": "El DNI ya existe. Proporcione un DNI diferente."})

            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO users (username, password, dni, email, puntaje) VALUES (%s, %s, %s, %s, %s)",
                           (data['username'], data['password'], data['dni'], data['email'], data['puntaje']))
            mysql.connection.commit()
            cursor.close()

            data = {
                "authenticated": True,
                "username": data['username'],
                "password": data['password']
            }
            token = write_token({**data, 'logged': True})
            return jsonify({"Message": "Usuario agregado exitosamente", **data, 'token': token.decode('utf-8')})

        except Exception as e:
            return jsonify({"Error": str(e)})
    else:
        return jsonify({
            "Tip": "Utilice una solicitud POST para agregar un usuario. Ejemplo de datos JSON: {'username':'ejemplo','password':'ejemplo','dni':'ejemplo','email':'ejemplo','puntaje':0}"
        })


@app.route("/api/deleteUser/", methods=["POST"])
def delete_user():
    try:
        data = request.json
        print(data)
        if 'username' in data:
            username = data['username']

            cursor = mysql.connection.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user:
                cursor.execute(
                    "DELETE FROM users WHERE username = %s", (username,))
                mysql.connection.commit()
                cursor.close()
                return jsonify({"message": f"Usuario {username} eliminado exitosamente"})
            else:
                return jsonify({"message": "Credenciales incorrectas"})
        else:
            return jsonify({"error": "Faltan datos de autenticación en la solicitud"})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/api/getPuntaje/<string:username>", methods=["GET"])
def get_user(username):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            user_dict = {
                'username': user[1],
                'puntaje': user[5]
            }
            return jsonify({'status': 200, 'user': user_dict})
        else:
            return jsonify({'status': 404, 'message': 'User not found'})

    except Exception as e:
        return jsonify({'status': 500, 'error': str(e)})


@app.route("/api/listUsers/", methods=["GET"])
def list_users():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users ORDER BY puntaje DESC LIMIT 4")
        users = cursor.fetchall()
        cursor.close()

        user_list = []

        for user in users:
            user_dict = {
                'id': user[0],
                'name': user[1],
                'puntaje': str(user[5])
            }
            user_list.append(user_dict)

        return jsonify({'status': 200, 'users': user_list})
    except Exception as e:
        return jsonify({'status': 500, 'error': str(e)})


if __name__ == "__main__":
    load_dotenv()
    app.run('0.0.0.0', port=5050, debug=True)
