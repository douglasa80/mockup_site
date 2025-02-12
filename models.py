from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Noticia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    data = db.Column(db.String(20), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    resumo = db.Column(db.String(200), nullable=False)
    imagem = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Noticia('{self.titulo}', '{self.data}')"