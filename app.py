from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Noticia, Usuario
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'minha_chave_secreta_super_segura_123'  # Chave secreta para gerenciar sessões

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração para upload de imagens
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'media')  # Pasta onde as imagens serão salvas
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Extensões permitidas

db.init_app(app)

# Função para verificar se a extensão do arquivo é permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Decorador para verificar se o usuário está autenticado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@login_required
def admin():
    # Ordena as notícias pela data de forma decrescente
    noticias = Noticia.query.order_by(Noticia.data.desc()).all()
    return render_template('admin.html', noticias=noticias)

# Rota da página inicial
@app.route('/')
def home():
    # Ordena as notícias pela data de forma decrescente
    noticias = Noticia.query.order_by(Noticia.data.desc()).all()
    return render_template('index.html', noticias=noticias)

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and usuario.check_password(password):
            session['usuario_id'] = usuario.id  # Armazena o ID do usuário na sessão
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')

    return render_template('login.html')

# Rota de logout
@app.route('/logout')
def logout():
    session.pop('usuario_id', None)  # Remove o ID do usuário da sessão
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('home'))

# Rota para adicionar notícias (protegida)

@app.route('/adicionar', methods=['GET', 'POST'])
@login_required
def adicionar_noticia():
    if request.method == 'POST':
        titulo = request.form['titulo']
        data_str = request.form['data']  # Recebe a data como string
        resumo = request.form['resumo']
        conteudo = request.form['conteudo']
        imagem = request.files['imagem']

        # Converte a string da data para um objeto datetime
        try:
            data = datetime.strptime(data_str, '%Y-%m-%d')  # Converte 'YYYY-MM-DD' para datetime
        except ValueError:
            flash('Formato de data inválido. Use o formato YYYY-MM-DD.', 'danger')
            return redirect(url_for('adicionar_noticia'))

        if imagem and allowed_file(imagem.filename):
            filename = secure_filename(imagem.filename)
            caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagem.save(caminho_imagem)

            nova_noticia = Noticia(
                titulo=titulo,
                data=data,  # Agora é um objeto datetime
                resumo=resumo,
                conteudo=conteudo,
                imagem=filename
            )

            db.session.add(nova_noticia)
            db.session.commit()
            flash('Notícia adicionada com sucesso!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Formato de arquivo não permitido. Use apenas imagens (png, jpg, jpeg, gif).', 'danger')

    return render_template('form_noticia.html', titulo='Adicionar Notícia', action_url=url_for('adicionar_noticia'), botao='Adicionar')

# Rota para editar notícias (protegida)
@app.route('/editar/<int:noticia_id>', methods=['GET', 'POST'])
@login_required
def editar_noticia(noticia_id):
    noticia = Noticia.query.get_or_404(noticia_id)

    if request.method == 'POST':
        noticia.titulo = request.form['titulo']
        data_str = request.form['data']
        noticia.resumo = request.form['resumo']
        noticia.conteudo = request.form['conteudo']

        try:
            noticia.data = datetime.strptime(data_str, '%Y-%m-%d')  # Converte 'YYYY-MM-DD' para datetime
        except ValueError:
            flash('Formato de data inválido. Use o formato YYYY-MM-DD.', 'danger')
            return redirect(url_for('editar_noticia', noticia_id=noticia.id))

        if 'imagem' in request.files:
            imagem = request.files['imagem']
            if imagem.filename != '' and allowed_file(imagem.filename):
                if noticia.imagem:
                    caminho_imagem_antiga = os.path.join(app.config['UPLOAD_FOLDER'], noticia.imagem)
                    if os.path.exists(caminho_imagem_antiga):
                        os.remove(caminho_imagem_antiga)

                filename = secure_filename(imagem.filename)
                caminho_imagem_nova = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagem.save(caminho_imagem_nova)
                noticia.imagem = filename

        db.session.commit()
        flash('Notícia editada com sucesso!', 'success')
        return redirect(url_for('admin'))

    data_formatada = noticia.data.strftime('%Y-%m-%d') if noticia.data else ''
    return render_template('form_noticia.html', titulo='Editar Notícia', noticia=noticia, data_formatada=data_formatada, botao='Salvar Alterações')

# Rota para remover notícias (protegida)
@app.route('/remover/<int:noticia_id>', methods=['POST'])
@login_required
def remover_noticia(noticia_id):
    noticia = Noticia.query.get_or_404(noticia_id)
    db.session.delete(noticia)
    db.session.commit()
    flash('Notícia removida com sucesso!', 'success')
    return redirect(url_for('admin'))

# Rota para exibir um artigo
@app.route('/artigo/<int:noticia_id>')
def artigo(noticia_id):
    noticia = Noticia.query.get_or_404(noticia_id)
    return render_template('artigo.html', noticia=noticia)

if __name__ == '__main__':
    app.run(debug=True)