from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

@app.route('/')
def home():
   return redirect(url_for('search'))


@app.route('/search', methods=['POST', 'GET'])
def search():
   projectpath = request.form.get('searchString')
   print(projectpath)

   return render_template('buscador.html')


if __name__ == '__main__':
   app.run()