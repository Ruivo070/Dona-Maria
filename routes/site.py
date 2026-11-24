from flask import Blueprint, current_app, render_template, send_from_directory
from sqlalchemy import select

from models import ItemCardapio, Rodizio, db


site_bp = Blueprint("site", __name__)

NOMES_DIAS = {
    "monday": "Segunda-feira",
    "tuesday": "Terça-feira",
    "wednesday": "Quarta-feira",
    "thursday": "Quinta-feira",
    "friday": "Sexta-feira",
    "saturday": "Sábado",
    "sunday": "Domingo",
}


@site_bp.get("/")
def inicio():
    rodizios = db.session.execute(
        select(Rodizio).order_by(Rodizio.id)
    ).scalars().all()
    itens_cardapio = db.session.execute(
        select(ItemCardapio).order_by(ItemCardapio.id)
    ).scalars().all()
    categorias = list(dict.fromkeys(item.categoria for item in itens_cardapio))

    return render_template(
        "index.html",
        rodizios=rodizios,
        itens_cardapio=itens_cardapio,
        categorias=categorias,
        nomes_dias=NOMES_DIAS,
    )


@site_bp.get("/robots.txt")
def robots():
    return send_from_directory(current_app.static_folder, "robots.txt")


@site_bp.get("/sitemap.xml")
def sitemap():
    return send_from_directory(current_app.static_folder, "sitemap.xml")
