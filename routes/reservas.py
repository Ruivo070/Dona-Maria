from urllib.parse import urlencode

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import select

from models import Reserva, db
from routes.reservas_forms import ReservaForm, hoje_em_betim


reservas_bp = Blueprint("reservas", __name__)


@reservas_bp.route("/reservar", methods=["GET", "POST"])
@login_required
def reservar():
    form = ReservaForm()
    if form.validate_on_submit():
        reserva = Reserva(
            usuario_id=current_user.id,
            data=form.data_reserva.data,
            horario=form.horario.data,
            numero_pessoas=form.numero_pessoas.data,
            observacao=(form.observacao.data or "").strip(),
        )
        db.session.add(reserva)
        db.session.commit()

        mensagem = "\n".join(
            (
                "Olá! Gostaria de confirmar minha reserva no Restaurante Dona Maria.",
                f"Nome: {current_user.nome}",
                f"Data: {reserva.data.strftime('%d/%m/%Y')}",
                f"Horário: {reserva.horario.strftime('%H:%M')}",
                f"Número de pessoas: {reserva.numero_pessoas}",
                f"Observação: {reserva.observacao or 'Nenhuma'}",
                "Status: pendente de confirmação",
            )
        )
        return render_template(
            "reserva_confirmada.html",
            reserva=reserva,
            whatsapp_query=urlencode({"text": mensagem}),
        )

    return render_template(
        "reservar.html",
        form=form,
        data_minima=hoje_em_betim().isoformat(),
    )


@reservas_bp.get("/minhas-reservas")
@login_required
def minhas_reservas():
    reservas = db.session.execute(
        select(Reserva)
        .where(Reserva.usuario_id == current_user.id)
        .order_by(Reserva.data, Reserva.horario, Reserva.id)
    ).scalars().all()
    return render_template("minhas_reservas.html", reservas=reservas)


@reservas_bp.post("/minhas-reservas/<int:reserva_id>/cancelar")
@login_required
def cancelar(reserva_id):
    reserva = db.session.execute(
        select(Reserva).where(
            Reserva.id == reserva_id,
            Reserva.usuario_id == current_user.id,
        )
    ).scalar_one_or_none()
    if reserva is None:
        abort(404)

    if reserva.status != "cancelada":
        reserva.status = "cancelada"
        db.session.commit()
        flash("Reserva cancelada.", "sucesso")
    else:
        flash("Esta reserva já estava cancelada.", "erro")

    return redirect(url_for("reservas.minhas_reservas"))
