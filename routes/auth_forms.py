import re

from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, PasswordField, StringField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    InputRequired,
    Length,
    ValidationError,
)


PADRAO_TELEFONE = re.compile(
    r"(?:\([1-9][1-9]\)|[1-9][1-9])\s?9?[0-9]{4}-?[0-9]{4}"
)


def validar_telefone(_form, campo):
    if not PADRAO_TELEFONE.fullmatch((campo.data or "").strip()):
        raise ValidationError("Informe um telefone com DDD, como (31) 99327-0377.")


def validar_senha(_form, campo):
    senha = campo.data or ""
    if not re.search(r"[A-Za-z]", senha) or not re.search(r"[0-9]", senha):
        raise ValidationError("A senha deve conter pelo menos uma letra e um número.")


class CadastroForm(FlaskForm):
    nome = StringField(
        "Nome",
        filters=[lambda valor: valor.strip() if valor else valor],
        validators=[DataRequired(message="Informe seu nome."), Length(max=120)],
    )
    email = StringField(
        "E-mail",
        filters=[lambda valor: valor.strip() if valor else valor],
        validators=[
            DataRequired(message="Informe seu e-mail."),
            Email(message="Informe um e-mail válido."),
            Length(max=254, message="O e-mail deve ter até 254 caracteres."),
        ],
    )
    telefone = StringField(
        "Telefone com DDD",
        validators=[
            DataRequired(message="Informe seu telefone."),
            validar_telefone,
        ],
    )
    senha = PasswordField(
        "Senha",
        validators=[
            DataRequired(message="Informe uma senha."),
            Length(min=8, message="A senha deve ter pelo menos 8 caracteres."),
            validar_senha,
        ],
    )
    confirmar_senha = PasswordField(
        "Confirme sua senha",
        validators=[
            DataRequired(message="Confirme sua senha."),
            EqualTo("senha", message="As senhas não conferem."),
        ],
    )
    consentimento = BooleanField(
        validators=[
            InputRequired(
                message="É necessário concordar com o uso dos dados para criar a conta."
            )
        ]
    )


class LoginForm(FlaskForm):
    email = StringField(
        "E-mail",
        filters=[lambda valor: valor.strip() if valor else valor],
        validators=[DataRequired(message="E-mail ou senha inválidos.")],
    )
    senha = PasswordField(
        "Senha",
        validators=[DataRequired(message="E-mail ou senha inválidos.")],
    )
    next = HiddenField()
