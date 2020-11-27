from flask import Flask, render_template, request, redirect, url_for, Response
import json
import importlib
import sys
import os 
from index import Query
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append("../merging_blocks/0.json")
import index

app = Flask(__name__,
            static_url_path='', 
            static_folder='frontEnd/static',
            template_folder='frontEnd/templates')

@app.route('/')
def home():
   return render_template('buscador.html')

@app.route('/consulta', methods = ['POST'])
def consulta():
   message = json.loads(request.data)
   words =  message['values']
   cantidad = message['cantidad']
   data = Query().query(words,cantidad)
   print(data)
   response = Response(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
   return response

@app.route('/upload', methods = ['POST'])
def upload():
   uploaded_files = request.files.getlist("file")

   for file in uploaded_files:
      with open("clean/"+str(file.filename), "wb") as archivo:
         archivo.write(file.read())
   return render_template('buscador.html')

if __name__ == '__main__':
   app.run()