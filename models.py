from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Demanda(db.Model):
    __tablename__ = 'demandas'
    __table_args__ = {'sqlite_autoincrement': True}

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.Text, nullable=False)
    descricao = db.Column(db.Text)
    solicitante = db.Column(db.Text)
    prioridade = db.Column(db.Text, server_default='')
    status = db.Column(db.Text, server_default='Aberto')
    data_criacao = db.Column(db.Text)


class Comentario(db.Model):
    __tablename__ = 'comentarios'
    __table_args__ = {'sqlite_autoincrement': True}

    id = db.Column(db.Integer, primary_key=True)
    demanda_id = db.Column(db.Integer, db.ForeignKey('demandas.id'), nullable=False)
    comentario = db.Column(db.Text)
    autor = db.Column(db.Text)
    data = db.Column(db.Text)


class Requester(db.Model):
    __tablename__ = 'requesters'
    __table_args__ = {'sqlite_autoincrement': True}

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    cargo = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.Text, nullable=False)
