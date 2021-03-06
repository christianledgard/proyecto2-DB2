from flask import Flask, render_template, request, redirect, url_for, Response, flash
import json
import importlib
import sys
import os 
import glob
from index import Query
import index
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append("../merging_blocks/0.json")

app = Flask(__name__,
            static_url_path='', 
            static_folder='frontEnd/static',
            template_folder='frontEnd/templates')
app.secret_key = b'heiderEsLoMaximo/'

@app.route('/')
def home():
   return render_template('buscador.html')

@app.route('/consulta', methods = ['POST'])
def consulta():
   message = json.loads(request.data)
   words =  message['values']
   cantidad = message['cantidad']
   data = Query().query(words,cantidad)
   response = Response(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
   return response

@app.route('/upload', methods = ['POST'])
def upload():
   uploaded_files = request.files.getlist("file")
   numero_bloques = request.form.get("numeroBloques")
   
   files = glob.glob('clean/*') + glob.glob('clean_likeADict/*') + glob.glob('inverted_index/*') + glob.glob('merging_blocks/*') + glob.glob('sorted_blocks/*')
   for f in files:
      os.remove(f)

   for file in uploaded_files:
      with open("clean/"+str(file.filename), "wb") as archivo:
         archivo.write(file.read())
   
   index.Index("clean", "inverted_index", "merging_blocks", "sorted_blocks", int(numero_bloques))
   
   flash(u'Los datos se han cargado de manera correcta.',  'alert-success')
   return render_template('buscador.html')

if __name__ == '__main__':
   app.run()