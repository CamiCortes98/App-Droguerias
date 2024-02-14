from flask import Flask, render_template, request, send_file, jsonify
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def create_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

create_upload_folder()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    barracas_csv = request.files.get('barracas_csv')
    cofarsur_csv = request.files.get('cofarsur_csv')
    sud_csv = request.files.get('sud_csv')
    txt_file = request.files.get('txt_file')

    if barracas_csv:
        barracas_csv.save(os.path.join(app.config['UPLOAD_FOLDER'], 'barracas.csv'))
    if cofarsur_csv:
        cofarsur_csv.save(os.path.join(app.config['UPLOAD_FOLDER'], 'cofarsur.csv'))
    if sud_csv:
        sud_csv.save(os.path.join(app.config['UPLOAD_FOLDER'], 'sud.csv'))
    if txt_file:
        txt_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'archivo.txt'))

    return jsonify({'message': 'Archivos subidos exitosamente!'})

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return 'El archivo no existe'

if __name__ == '__main__':
    app.run(debug=True)
