from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, Noticia

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

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

@app.route('/editar/<int:noticia_id>', methods=['GET', 'POST'])
def editar_noticia(noticia_id):
    noticia = Noticia.query.get_or_404(noticia_id)

    if request.method == 'POST':
        noticia.titulo = request.form['titulo']
        noticia.data = request.form['data']
        noticia.resumo = request.form['resumo']
        noticia.conteudo = request.form['conteudo']
        noticia.imagem = request.form['imagem']

        db.session.commit()
        return redirect(url_for('home'))

    return render_template('editar.html', noticia=noticia)

@app.route('/remover/<int:noticia_id>', methods=['POST'])
def remover_noticia(noticia_id):
    noticia = Noticia.query.get_or_404(noticia_id)
    db.session.delete(noticia)
    db.session.commit()
    return redirect(url_for('home'))

# Rota para exibir um artigo
@app.route('/artigo/<int:noticia_id>')
def artigo(noticia_id):
    noticia = Noticia.query.get_or_404(noticia_id)
    return render_template('artigo.html', noticia=noticia)

if __name__ == '__main__':
    app.run(debug=True)