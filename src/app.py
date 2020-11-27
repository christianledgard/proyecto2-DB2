from flask import Flask, render_template, request, redirect, url_for, Response
import json
import importlib
import sys
import os 
from index import Query
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append("../merging_blocks/0.json")
import index

app = Flask(__name__,template_folder='frontEnd/templates')

@app.route('/')
def home():
   return render_template('buscador.html')

@app.route('/consulta', methods = ['POST'])
def consulta():
   message = json.loads(request.data)
   print(message)
   words =  message['values']
   cantidad = message['cantidad']
   data = Query().query(words,cantidad)
   print(words)
   print(cantidad)
   return Response("Working", status=200, mimetype='application/json')

@app.route('/upload', methods = ['POST'])
def upload():
   file = request.files['file']
   #print(file.read())
   return render_template('buscador.html')

if __name__ == '__main__':
   app.run()