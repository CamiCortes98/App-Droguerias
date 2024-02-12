from flask import Flask, render_template, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

    return 'Archivos subidos exitosamente!'

if __name__ == '__main__':
    app.run(debug=True)
