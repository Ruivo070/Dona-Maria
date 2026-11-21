from datetime import datetime, timezone
from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from extensions import limiter
from models import Usuario, db
from routes.auth_forms import CadastroForm, LoginForm


auth_bp = Blueprint("auth", __name__)


def destino_local_seguro(destino):
    if not destino or "\\" in destino:
        return None

    partes = urlsplit(destino)
    if partes.scheme or partes.netloc or not partes.path.startswith("/"):
        return None
    if partes.path.startswith("//"):
        return None
    return destino


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for("site.inicio"))

    form = CadastroForm()
    if form.validate_on_submit():
        email = form.email.data.casefold()
        usuario_existente = db.session.execute(
            select(Usuario).where(Usuario.email == email)
        ).scalar_one_or_none()
        if usuario_existente:
            form.email.errors.append("Este e-mail já está cadastrado.")
        else:
            usuario = Usuario(
                nome=form.nome.data,
                email=email,
                telefone="".join(filter(str.isdigit, form.telefone.data)),
                consentimento_em=datetime.now(timezone.utc),
            )
            usuario.definir_senha(form.senha.data)
            db.session.add(usuario)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                form.email.errors.append("Este e-mail já está cadastrado.")
            else:
                flash("Conta criada com sucesso. Agora você pode entrar.", "sucesso")
                return redirect(url_for("auth.login"))

    return render_template("cadastro.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    form = LoginForm()
    if request.method == "GET":
        form.next.data = request.args.get("next", "")

    if form.validate_on_submit():
        email = form.email.data.casefold()
        usuario = db.session.execute(
            select(Usuario).where(Usuario.email == email)
        ).scalar_one_or_none()
        if usuario is None or not usuario.conferir_senha(form.senha.data):
            flash("E-mail ou senha inválidos.", "erro")
        else:
            login_user(usuario)
            flash("Login realizado com sucesso.", "sucesso")
            destino = destino_local_seguro(form.next.data)
            return redirect(destino or url_for("site.inicio"))

    return render_template("login.html", form=form)


@auth_bp.post("/sair")
@login_required
def sair():
    logout_user()
    flash("Você saiu da sua conta.", "sucesso")
    return redirect(url_for("site.inicio"))


@auth_bp.get("/privacidade")
def privacidade():
    return render_template("privacidade.html")
