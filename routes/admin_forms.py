from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError


class RodizioAdminForm(FlaskForm):
    nome = StringField(
        "Nome",
        validators=[DataRequired(message="Informe o nome."), Length(max=120)],
    )
    preco = StringField(
        "Preço",
        validators=[DataRequired(message="Informe o preço."), Length(max=80)],
    )
    inclui = TextAreaField(
        "Descrição",
        validators=[DataRequired(message="Informe a descrição."), Length(max=3000)],
    )


class ItemCardapioAdminForm(FlaskForm):
    categoria = StringField(
        "Categoria",
        validators=[DataRequired(message="Informe a categoria."), Length(max=80)],
    )
    nome = StringField(
        "Nome",
        validators=[DataRequired(message="Informe o nome."), Length(max=160)],
    )
    descricao = TextAreaField(
        "Descrição",
        validators=[DataRequired(message="Informe a descrição."), Length(max=3000)],
    )
    preco = StringField(
        "Preço",
        validators=[DataRequired(message="Informe o preço."), Length(max=80)],
    )


class StatusReservaAdminForm(FlaskForm):
    status = StringField(
        "Status",
        validators=[DataRequired(message="Escolha um status.")],
    )

    def validate_status(self, campo):
        if campo.data not in {"pendente", "confirmada", "cancelada"}:
            raise ValidationError("Escolha um status válido.")
