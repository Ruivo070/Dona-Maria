from datetime import date
from functools import wraps

from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from models import INDICE_ADMIN_UNICO, ItemCardapio, Reserva, Rodizio, Usuario, db
from routes.admin_forms import (
    ItemCardapioAdminForm,
    RodizioAdminForm,
    StatusReservaAdminForm,
)


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def exigir_dono(funcao):
    @wraps(funcao)
    def decorada(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return funcao(*args, **kwargs)

    return decorada


def validar_senha_dono(senha):
    if len(senha or "") < 8 or not any(c.isalpha() for c in senha) or not any(
        c.isdigit() for c in senha
    ):
        raise ValueError("A senha deve ter ao menos 8 caracteres, uma letra e um número.")


def criar_dono(email, senha):
    try:
        email = validate_email(
            (email or "").strip(),
            check_deliverability=False,
        ).normalized.casefold()
    except EmailNotValidError as erro:
        raise ValueError("Informe um e-mail válido para o dono.") from erro

    validar_senha_dono(senha)

    if db.session.execute(
        select(Usuario.id).where(Usuario.is_admin.is_(True))
    ).first():
        raise ValueError("Já existe um dono cadastrado.")

    if db.session.execute(
        select(Usuario.id).where(Usuario.email == email)
    ).first():
        raise ValueError("Este e-mail já pertence a uma conta.")

    dono = Usuario(
        nome="Dono do restaurante",
        email=email,
        telefone="",
        senha_hash=generate_password_hash(senha),
        is_admin=True,
    )
    db.session.add(dono)
    try:
        db.session.commit()
    except IntegrityError as erro:
        db.session.rollback()
        raise ValueError("Já existe um dono cadastrado ou esta conta.") from erro
    return dono


def mensagens_de_erro(form):
    return "; ".join(
        erro
        for erros_campo in form.errors.values()
        for erro in erros_campo
    )


@admin_bp.route("/", methods=["GET"])
@login_required
@exigir_dono
def painel():
    aba = request.args.get("aba", "reservas")
    if aba not in {"reservas", "rodizios", "cardapio", "usuarios"}:
        abort(404)

    contexto = {"aba": aba}
    if aba == "reservas":
        data_texto = request.args.get("data", "").strip()
        data_filtro = None
        if data_texto:
            try:
                data_filtro = date.fromisoformat(data_texto)
            except ValueError:
                flash("Informe uma data válida para filtrar as reservas.", "erro")

        consulta = select(Reserva).order_by(
            Reserva.data,
            Reserva.horario,
            Reserva.id,
        )
        if data_filtro:
            consulta = consulta.where(Reserva.data == data_filtro)
        contexto.update(
            reservas=db.session.execute(consulta).scalars().all(),
            data_filtro=data_texto,
        )
    elif aba == "rodizios":
        contexto["rodizios"] = db.session.execute(
            select(Rodizio).order_by(Rodizio.id)
        ).scalars().all()
    elif aba == "cardapio":
        contexto["itens"] = db.session.execute(
            select(ItemCardapio).order_by(ItemCardapio.categoria, ItemCardapio.nome)
        ).scalars().all()
    else:
        contexto["usuarios"] = db.session.execute(
            select(
                Usuario.id,
                Usuario.nome,
                Usuario.email,
                Usuario.telefone,
                Usuario.is_admin,
                Usuario.criado_em,
            ).order_by(Usuario.criado_em.desc(), Usuario.id.desc())
        ).all()

    return render_template("admin.html", **contexto)


@admin_bp.post("/reservas/<int:reserva_id>/status")
@login_required
@exigir_dono
def alterar_status_reserva(reserva_id):
    reserva = db.session.get(Reserva, reserva_id)
    if reserva is None:
        abort(404)

    form = StatusReservaAdminForm()
    if not form.validate_on_submit():
        flash(mensagens_de_erro(form) or "Status de reserva inválido.", "erro")
    else:
        reserva.status = form.status.data
        db.session.commit()
        flash("Status da reserva atualizado.", "sucesso")

    return redirect(url_for("admin.painel", aba="reservas"))


@admin_bp.post("/rodizios/<int:rodizio_id>")
@login_required
@exigir_dono
def editar_rodizio(rodizio_id):
    rodizio = db.session.get(Rodizio, rodizio_id)
    if rodizio is None:
        abort(404)

    form = RodizioAdminForm()
    if not form.validate_on_submit():
        flash(mensagens_de_erro(form) or "Não foi possível salvar o rodízio.", "erro")
    else:
        rodizio.nome = form.nome.data.strip()
        rodizio.preco = form.preco.data.strip()
        rodizio.inclui = form.inclui.data.strip()
        db.session.commit()
        flash("Rodízio atualizado.", "sucesso")
    return redirect(url_for("admin.painel", aba="rodizios"))


@admin_bp.post("/cardapio/novo")
@login_required
@exigir_dono
def criar_item_cardapio():
    form = ItemCardapioAdminForm()
    if not form.validate_on_submit():
        flash(mensagens_de_erro(form) or "Não foi possível adicionar o item.", "erro")
    else:
        item = ItemCardapio(
            categoria=form.categoria.data.strip(),
            nome=form.nome.data.strip(),
            descricao=form.descricao.data.strip(),
            preco=form.preco.data.strip(),
        )
        db.session.add(item)
        db.session.commit()
        flash("Item adicionado ao cardápio.", "sucesso")
    return redirect(url_for("admin.painel", aba="cardapio"))


@admin_bp.post("/cardapio/<int:item_id>")
@login_required
@exigir_dono
def editar_item_cardapio(item_id):
    item = db.session.get(ItemCardapio, item_id)
    if item is None:
        abort(404)

    form = ItemCardapioAdminForm()
    if not form.validate_on_submit():
        flash(mensagens_de_erro(form) or "Não foi possível salvar o item.", "erro")
    else:
        item.categoria = form.categoria.data.strip()
        item.nome = form.nome.data.strip()
        item.descricao = form.descricao.data.strip()
        item.preco = form.preco.data.strip()
        db.session.commit()
        flash("Item do cardápio atualizado.", "sucesso")
    return redirect(url_for("admin.painel", aba="cardapio"))


@admin_bp.post("/cardapio/<int:item_id>/remover")
@login_required
@exigir_dono
def remover_item_cardapio(item_id):
    item = db.session.get(ItemCardapio, item_id)
    if item is None:
        abort(404)
    db.session.delete(item)
    db.session.commit()
    flash("Item removido do cardápio.", "sucesso")
    return redirect(url_for("admin.painel", aba="cardapio"))
