from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, Index
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class Rodizio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dia = db.Column(db.String(10), nullable=False, unique=True)
    nome = db.Column(db.String(120), nullable=False)
    preco = db.Column(db.String(80), nullable=False)
    inclui = db.Column(db.Text, nullable=False)


class ItemCardapio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(80), nullable=False)
    nome = db.Column(db.String(160), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    preco = db.Column(db.String(80), nullable=False)


class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), nullable=False, unique=True, index=True)
    telefone = db.Column(db.String(20), nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    consentimento_em = db.Column(db.DateTime(timezone=True), nullable=True)
    criado_em = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def conferir_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    reservas = db.relationship(
        "Reserva",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )


class Reserva(db.Model):
    __table_args__ = (
        CheckConstraint(
            "status IN ('pendente', 'confirmada', 'cancelada')",
            name="ck_reserva_status",
        ),
        CheckConstraint(
            "numero_pessoas BETWEEN 1 AND 20",
            name="ck_reserva_numero_pessoas",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id"),
        nullable=False,
        index=True,
    )
    data = db.Column(db.Date, nullable=False)
    horario = db.Column(db.Time, nullable=False)
    numero_pessoas = db.Column(db.Integer, nullable=False)
    observacao = db.Column(db.String(500), nullable=False, default="")
    status = db.Column(db.String(12), nullable=False, default="pendente")
    criada_em = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    usuario = db.relationship("Usuario", back_populates="reservas")


INDICE_ADMIN_UNICO = Index(
    "uq_usuario_unico_admin",
    Usuario.is_admin,
    unique=True,
    sqlite_where=Usuario.is_admin.is_(True),
    postgresql_where=Usuario.is_admin.is_(True),
)
