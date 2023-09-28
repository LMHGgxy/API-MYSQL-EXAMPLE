from flask import Flask, send_file

app = Flask(__name__)

import os

@app.route('/descargar-zip')
def descargar_zip():
    filename = os.path.abspath('19ff1c69-60c1-451f-91df-02c8a8569788.tar.gz')
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run('0.0.0.0',port=5035,debug=True)