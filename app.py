import os

import click
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError
from sqlalchemy import select
from werkzeug.middleware.proxy_fix import ProxyFix

from extensions import csrf, limiter, login_manager
from models import INDICE_ADMIN_UNICO, ItemCardapio, Rodizio, Usuario, db
from routes.admin import admin_bp, criar_dono, validar_senha_dono
from routes.auth import auth_bp
from routes.reservas import reservas_bp
from routes.site import site_bp


@login_manager.user_loader
def carregar_usuario(id_usuario):
    try:
        identificador = int(id_usuario)
    except (TypeError, ValueError):
        return None
    return db.session.get(Usuario, identificador)


def criar_dados_iniciais():
    if db.session.execute(select(Rodizio.id).limit(1)).first() is None:
        rodizios = [
            Rodizio(
                dia="monday",
                nome="Sem rodízio noturno",
                preco="Não há rodízio",
                inclui="A casa funciona no almoço. Consulte pelo WhatsApp as opções à la carte disponíveis à noite.",
            ),
            Rodizio(
                dia="tuesday",
                nome="Terçaneja",
                preco="A partir de R$ 79,90",
                inclui="Noite temática. Consulte a equipe para saber o que está incluído e a programação musical.",
            ),
            Rodizio(
                dia="wednesday",
                nome="Rodízio completo",
                preco="A partir de R$ 89,90",
                inclui="Pode incluir churrasco, petiscos, pizzas, comida japonesa e bebidas selecionadas. A composição varia conforme o dia.",
            ),
            Rodizio(
                dia="thursday",
                nome="Rodízio de pizza",
                preco="A partir de R$ 69,90",
                inclui="Variedade de pizzas. Consulte os sabores e os demais itens do rodízio.",
            ),
            Rodizio(
                dia="friday",
                nome="Rodízio completo",
                preco="R$ 99,90",
                inclui="Pode incluir churrasco, petiscos, pizzas, comida japonesa e bebidas selecionadas. A composição varia conforme o dia.",
            ),
            Rodizio(
                dia="saturday",
                nome="Rodízio completo",
                preco="R$ 119,00",
                inclui="Pode incluir churrasco, petiscos, pizzas, comida japonesa e bebidas selecionadas. A composição varia conforme o dia.",
            ),
            Rodizio(
                dia="sunday",
                nome="Rodízio de pizza",
                preco="A partir de R$ 69,90",
                inclui="Variedade de pizzas. Consulte os sabores e os demais itens do rodízio.",
            ),
        ]
        db.session.add_all(rodizios)

    if db.session.execute(select(ItemCardapio.id).limit(1)).first() is None:
        itens = [
            ItemCardapio(
                categoria="Almoço",
                nome="Self-service por quilo",
                descricao="Pratos quentes, saladas e churrasco. Preço de referência; consulte o valor atual.",
                preco="R$ 49,90/kg",
            ),
            ItemCardapio(
                categoria="Pizzas",
                nome="Pizza pequena",
                descricao="Consulte os sabores disponíveis.",
                preco="A partir de R$ 65,00",
            ),
            ItemCardapio(
                categoria="Pizzas",
                nome="Pizza média",
                descricao="Consulte os sabores disponíveis.",
                preco="A partir de R$ 75,00",
            ),
            ItemCardapio(
                categoria="Pizzas",
                nome="Pizza grande",
                descricao="Consulte os sabores disponíveis.",
                preco="A partir de R$ 85,00",
            ),
            ItemCardapio(
                categoria="Porções e pratos",
                nome="Bolinho de bacalhau (10 unidades)",
                descricao="Porção com dez unidades.",
                preco="R$ 49,00",
            ),
            ItemCardapio(
                categoria="Porções e pratos",
                nome="Linguiça artesanal",
                descricao="Acompanha mandioca ou fritas.",
                preco="R$ 89,00",
            ),
            ItemCardapio(
                categoria="Porções e pratos",
                nome="Espaguete à bolonhesa",
                descricao="Massa com molho à bolonhesa.",
                preco="R$ 49,00",
            ),
            ItemCardapio(
                categoria="Porções e pratos",
                nome="Escapole de filé ao molho roti",
                descricao="Serve até duas pessoas. Nome conforme informado pelo estabelecimento.",
                preco="R$ 159,00",
            ),
            ItemCardapio(
                categoria="Bebidas",
                nome="Cervejas 600 ml",
                descricao="Original e Heineken.",
                preco="R$ 20,00 a R$ 22,00",
            ),
            ItemCardapio(
                categoria="Bebidas",
                nome="Chopp",
                descricao="Consulte os tamanhos disponíveis.",
                preco="A partir de R$ 15,00",
            ),
            ItemCardapio(
                categoria="Bebidas",
                nome="Cachaças e doses",
                descricao="Consulte as opções disponíveis.",
                preco="R$ 10,00 a R$ 15,00",
            ),
        ]
        db.session.add_all(itens)

    db.session.commit()


def criar_dono_configurado():
    email = os.environ.get("ADMIN_EMAIL", "").strip()
    senha = os.environ.get("ADMIN_PASSWORD", "")
    if not email and not senha:
        return
    if not email or not senha:
        raise RuntimeError("Defina ADMIN_EMAIL e ADMIN_PASSWORD juntos.")
    if db.session.execute(
        select(Usuario.id).where(Usuario.is_admin.is_(True))
    ).first():
        return
    try:
        criar_dono(email, senha)
    except ValueError as erro:
        raise RuntimeError(f"Não foi possível criar o dono inicial: {erro}") from erro


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    database_url = os.environ.get("DATABASE_URL", "").strip()
    producao = os.environ.get("RENDER") == "true" or os.environ.get(
        "FLASK_ENV"
    ) == "production"
    if not database_url:
        if producao:
            raise RuntimeError("Defina DATABASE_URL para usar o banco PostgreSQL em produção.")
        database_url = "sqlite:///app.db"
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+psycopg2://", 1
        )
    if producao and database_url.startswith("sqlite:"):
        raise RuntimeError("SQLite só pode ser usado localmente; defina DATABASE_URL.")

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=(
            os.environ.get("RENDER") == "true"
            or os.environ.get("FLASK_ENV") == "production"
        ),
        RATELIMIT_STORAGE_URI=os.environ.get(
            "RATELIMIT_STORAGE_URI", "memory://"
        ),
        DEBUG=False,
    )
    if test_config:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Defina SECRET_KEY nas variáveis de ambiente antes de iniciar.")

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Entre na sua conta para continuar."
    login_manager.login_message_category = "erro"
    login_manager.init_app(app)
    limiter.init_app(app)
    if os.environ.get("RENDER") == "true":
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    app.register_blueprint(site_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(reservas_bp)
    app.register_blueprint(admin_bp)

    @app.cli.command("criar-admin")
    def comando_criar_admin():
        """Cria o único usuário com acesso ao painel administrativo."""
        email = click.prompt("E-mail do dono")
        senha = click.prompt(
            "Senha do dono",
            hide_input=True,
            confirmation_prompt=True,
        )
        try:
            criar_dono(email, senha)
        except ValueError as erro:
            raise click.ClickException(str(erro)) from erro
        click.echo("Dono criado. A senha foi armazenada com hash.")

    @app.cli.command("alterar-senha-admin")
    def comando_alterar_senha_admin():
        """Troca a senha do dono existente sem exibi-la."""
        dono = db.session.execute(
            select(Usuario).where(Usuario.is_admin.is_(True))
        ).scalar_one_or_none()
        if dono is None:
            raise click.ClickException("Nenhum dono cadastrado.")
        senha = click.prompt(
            "Nova senha do dono",
            hide_input=True,
            confirmation_prompt=True,
        )
        try:
            validar_senha_dono(senha)
        except ValueError as erro:
            raise click.ClickException(str(erro)) from erro
        dono.definir_senha(senha)
        db.session.commit()
        click.echo("Senha do dono atualizada e armazenada com hash.")

    @app.after_request
    def adicionar_cabecalhos_de_seguranca(resposta):
        resposta.headers.setdefault("X-Content-Type-Options", "nosniff")
        resposta.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        resposta.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return resposta

    @app.errorhandler(403)
    def proibido(_erro):
        return render_template("error.html", codigo=403, mensagem="Você não tem permissão para acessar esta página."), 403

    @app.errorhandler(404)
    def pagina_nao_encontrada(_erro):
        return render_template("404.html"), 404

    @app.errorhandler(429)
    def muitas_tentativas(_erro):
        return render_template(
            "error.html",
            codigo=429,
            mensagem="Muitas tentativas em pouco tempo. Aguarde um minuto e tente novamente.",
        ), 429

    @app.errorhandler(CSRFError)
    def csrf_invalido(_erro):
        return render_template(
            "error.html",
            codigo=400,
            mensagem="O formulário expirou ou não pôde ser validado. Atualize a página e tente novamente.",
        ), 400

    @app.errorhandler(500)
    def erro_interno(_erro):
        return render_template("error.html", codigo=500, mensagem="Ocorreu um erro inesperado. Tente novamente mais tarde."), 500

    with app.app_context():
        db.create_all()
        INDICE_ADMIN_UNICO.create(bind=db.engine, checkfirst=True)
        criar_dados_iniciais()
        criar_dono_configurado()

    return app
