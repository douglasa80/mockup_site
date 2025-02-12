from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, Noticia  # Importa o banco de dados e o modelo

app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Rota da página inicial
@app.route('/')
def home():
    noticias = Noticia.query.all()
    return render_template('index.html', noticias=noticias)

# Rota para adicionar notícias
@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar_noticia():
    if request.method == 'POST':
        titulo = request.form['titulo']
        data = request.form['data']
        resumo = request.form['resumo']
        conteudo = request.form['conteudo']
        imagem = request.form['imagem']

        nova_noticia = Noticia(
            titulo=titulo,
            data=data,
            resumo=resumo,
            conteudo=conteudo,
            imagem=imagem
        )

        db.session.add(nova_noticia)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('adicionar.html')

# Rota para exibir um artigo
@app.route('/artigo/<int:noticia_id>')
def artigo(noticia_id):
    noticia = Noticia.query.get_or_404(noticia_id)
    return render_template('artigo.html', noticia=noticia)

if __name__ == '__main__':
    app.run(debug=True)