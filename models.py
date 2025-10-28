from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# -------------------------------
#  USUÁRIO
# -------------------------------
class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)

    # Relacionamentos
    criancas = db.relationship("Crianca", backref="usuario", lazy=True, cascade="all, delete-orphan")
    categorias = db.relationship("Categoria", backref="usuario", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Usuario {self.nome}>"


# -------------------------------
#  CRIANÇA
# -------------------------------
class Crianca(db.Model):
    __tablename__ = "criancas"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    nome = db.Column(db.String(100), nullable=False)
    idade = db.Column(db.String(20))
    genero = db.Column(db.String(20))
    observacao = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Crianca {self.nome}>"


# -------------------------------
#  CATEGORIA
# -------------------------------
class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    nome = db.Column(db.String(120), nullable=False)
    cor = db.Column(db.String(16), default="#7c3aed")
    ordem = db.Column(db.Integer, default=0)

    # Relacionamento com os cards
    cards = db.relationship("Card", backref="categoria", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Categoria {self.nome}>"


# -------------------------------
#  CARD
# -------------------------------
class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)

    label = db.Column(db.String(120), nullable=False)  # texto do card
    emoji = db.Column(db.String(8))                    # ex: 😊, 🧃, 🍎
    cor   = db.Column(db.String(16))                   # cor do card
    fala  = db.Column(db.String(240))                  # frase que será lida no TTS
    ordem = db.Column(db.Integer, default=0)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Card {self.label}>"
