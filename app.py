from flask import Flask, render_template, request, send_file, jsonify
import os
import pandas as pd

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

    barracas_discount = float(request.form.get('barracas_discount', 0)) / 100
    cofarsur_discount = float(request.form.get('cofarsur_discount', 0)) / 100
    sud_discount = float(request.form.get('sud_discount', 0)) / 100

    if barracas_csv:
        barracas_csv.save(os.path.join(app.config['UPLOAD_FOLDER'], 'barracas.csv'))
        apply_discount(os.path.join(app.config['UPLOAD_FOLDER'], 'barracas.csv'), barracas_discount)  
    if cofarsur_csv:
        cofarsur_csv.save(os.path.join(app.config['UPLOAD_FOLDER'], 'cofarsur.csv'))
        apply_discount(os.path.join(app.config['UPLOAD_FOLDER'], 'cofarsur_csv'), cofarsur_discount)
    if sud_csv:
        sud_csv.save(os.path.join(app.config['UPLOAD_FOLDER'], 'sud.csv'))
        apply_discount(os.path.join(app.config['UPLOAD_FOLDER'], 'sud.csv'), sud_discount)
    if txt_file:
        txt_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'archivo.txt'))

    return jsonify({'message': 'Archivos subidos exitosamente!'})

def apply_discount(filepath, discount):
    df = pd.read_csv(filepath)
    if 'precios' in df.columns:
        df['precios'] = df['precios'] * (1 - discount)
        df.to_csv(filepath, index=False)

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return 'El archivo no existe'

if __name__ == '__main__':
    app.run(debug=True)
