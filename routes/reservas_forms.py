from datetime import datetime, time
from zoneinfo import ZoneInfo

from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, TextAreaField, TimeField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, ValidationError


HORARIOS_FUNCIONAMENTO = {
    0: ((time(11), time(15)),),
    1: ((time(11), time(15)), (time(18), time(23))),
    2: ((time(11), time(15)), (time(18), time(23))),
    3: ((time(11), time(15)), (time(18), time(23))),
    4: ((time(11), time(15)), (time(18), time(23))),
    5: ((time(11, 30), time(15, 30)), (time(18), time(23))),
    6: ((time(11, 30), time(15, 30)), (time(18), time(23))),
}


def hoje_em_betim():
    return datetime.now(ZoneInfo("America/Sao_Paulo")).date()


class ReservaForm(FlaskForm):
    data_reserva = DateField(
        "Data",
        format="%Y-%m-%d",
        validators=[DataRequired(message="Escolha a data da reserva.")],
    )
    horario = TimeField(
        "Horário",
        format="%H:%M",
        validators=[DataRequired(message="Escolha o horário da reserva.")],
    )
    numero_pessoas = IntegerField(
        "Número de pessoas",
        validators=[
            InputRequired(message="Informe o número de pessoas."),
            NumberRange(
                min=1,
                max=20,
                message="A reserva deve ser para 1 a 20 pessoas.",
            ),
        ],
    )
    observacao = TextAreaField(
        "Observação",
        validators=[Length(max=500, message="A observação deve ter até 500 caracteres.")],
    )

    def validate_data_reserva(self, campo):
        if campo.data and campo.data < hoje_em_betim():
            raise ValidationError("A data da reserva não pode estar no passado.")

    def validate_horario(self, campo):
        if not campo.data or not self.data_reserva.data:
            return

        faixas = HORARIOS_FUNCIONAMENTO[self.data_reserva.data.weekday()]
        if not any(abertura <= campo.data < fechamento for abertura, fechamento in faixas):
            raise ValidationError(
                "Escolha um horário dentro do funcionamento do restaurante."
            )
