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

def procesar_datos(archivos_csv, archivo_txt, entry_descuentos):
    try:
        columnas = [1, 5, 6, 9]
        dataframes = []

        for nombre_df, archivo_csv in archivos_csv.items():
            df = pd.read_csv(archivo_csv, sep=';', usecols=columnas, header=None, encoding='ISO-8859-1')
            df.columns = ["Codigo", 'Nombre', "Gramaje", 'Precio']
            df['Archivo'] = nombre_df  
            df['Precio'] = df['Precio'] * (1 - entry_descuentos[nombre_df] / 100)
            dataframes.append(df)

        for df in dataframes:
            df['Nombre Producto'] = df['Nombre'] + ' ' + df['Gramaje']

        codigo_barras_unicos = set(dataframes[0]['Codigo'])
        mejor_opcion = pd.DataFrame({'Codigo': list(codigo_barras_unicos)})

        nombres_df = dataframes[0][['Codigo', 'Nombre Producto']]
        for df in dataframes:
            mejor_precio = df.groupby('Codigo')['Precio'].min().reset_index()
            mejor_opcion = mejor_opcion.merge(mejor_precio, on='Codigo', suffixes=('', f'_{df["Archivo"].iloc[0]}'))

        mejor_opcion.rename(columns={'Precio': 'Barracas'}, inplace=True)

        for df in dataframes:
            mejor_opcion.rename(columns={f'Precio_{df["Archivo"].iloc[0]}': f'Precio_{df["Archivo"].iloc[0]}'}, inplace=True)

        mejor_opcion = mejor_opcion.merge(nombres_df, on='Codigo')

        BaseTxt = pd.read_csv(archivo_txt, sep='\t', header=None)
        BaseTxt.columns = ['Codigo', 'Producto', 'Condicion', 'CantidadDeseada', 'Cantidad']
        BaseTxt = BaseTxt[BaseTxt['Codigo'].str.isnumeric()]
        BaseTxt["Codigo"] = BaseTxt["Codigo"].astype("int64")

        mejor_opcion['Recomendado'] = mejor_opcion[['Barracas', 'Precio_Cofarsur', 'Precio_Del Sud']].idxmin(axis=1)
        mejor_opcion['Recomendado'] = mejor_opcion['Recomendado'].str.replace('Precio_', '')
        mejor_opcion['Codigo'] = mejor_opcion['Codigo'].astype('int64')

        mejor_opcion_filtrado = pd.merge(mejor_opcion, BaseTxt, on="Codigo", how="inner")

        # Guardar el DataFrame como un archivo temporal
        temp_file = os.path.join(app.config['UPLOAD_FOLDER'], 'resultado.csv')
        mejor_opcion_filtrado.to_csv(temp_file, index=False)

        return temp_file
    
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        archivos_csv = {
            'barracas.csv': request.files['barracas_csv'],
            'cofarsur.csv': request.files['cofarsur_csv'],
            'sud.csv': request.files['sud_csv']
        }
        archivo_txt = request.files['txt_file']
        entry_descuentos = {
            'barracas.csv': float(request.form.get('barracas_discount', 0)),
            'cofarsur.csv': float(request.form.get('cofarsur_discount', 0)),
            'sud.csv': float(request.form.get('sud_discount', 0))
        }

        resultado = procesar_datos(archivos_csv, archivo_txt, entry_descuentos)

        return send_file(resultado, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return 'El archivo no existe'

if __name__ == '__main__':
    app.run(debug=True)
