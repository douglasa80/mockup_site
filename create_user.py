from app import app, db
from models import Usuario

def criar_admin():
    with app.app_context():
        # Verifica se o banco de dados já foi criado
        db.create_all()

        # Cria o usuário administrador
        username = "admin"
        password = "123"
        usuario_existente = Usuario.query.filter_by(username=username).first()
        if usuario_existente:
            print(f"Erro: O usuário '{username}' já existe.")
        else:
            novo_admin = Usuario(username=username)
            novo_admin.set_password(password)
            db.session.add(novo_admin)
            db.session.commit()
            print(f"Administrador '{username}' adicionado com sucesso!")

if __name__ == '__main__':
    criar_admin()