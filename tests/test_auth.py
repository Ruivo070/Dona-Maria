import unittest

from sqlalchemy import select

from app import create_app
from models import Usuario, db


class AutenticacaoTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "chave-de-teste",
                "SQLALCHEMY_DATABASE_URI": "sqlite://",
                "WTF_CSRF_ENABLED": False,
                "RATELIMIT_STORAGE_URI": "memory://",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose()

    def dados_de_cadastro(self, **alteracoes):
        dados = {
            "nome": "Maria Silva",
            "email": "Maria@example.com",
            "telefone": "(31) 99327-0377",
            "senha": "SenhaForte123",
            "confirmar_senha": "SenhaForte123",
            "consentimento": "y",
        }
        dados.update(alteracoes)
        return dados

    def test_cadastro_hash_login_menu_e_logout(self):
        resposta = self.client.post(
            "/cadastro",
            data=self.dados_de_cadastro(),
            follow_redirects=True,
        )
        self.assertIn("Conta criada com sucesso", resposta.get_data(as_text=True))

        with self.app.app_context():
            usuario = db.session.execute(
                select(Usuario).where(Usuario.email == "maria@example.com")
            ).scalar_one()
            self.assertNotEqual(usuario.senha_hash, "SenhaForte123")
            self.assertTrue(usuario.conferir_senha("SenhaForte123"))
            self.assertEqual(usuario.telefone, "31993270377")
            self.assertIsNotNone(usuario.consentimento_em)

        resposta = self.client.post(
            "/login?next=//outro-site.example",
            data={
                "email": "MARIA@example.com",
                "senha": "SenhaForte123",
                "next": "//outro-site.example",
            },
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(resposta.headers["Location"], "/")

        pagina = self.client.get("/").get_data(as_text=True)
        self.assertIn("Olá, Maria", pagina)
        self.assertIn("Minhas reservas", pagina)
        self.assertIn("Sair", pagina)
        self.assertEqual(self.client.get("/minhas-reservas").status_code, 200)

        resposta = self.client.post("/sair")
        self.assertEqual(resposta.status_code, 302)
        pagina = self.client.get("/").get_data(as_text=True)
        self.assertIn("Criar conta", pagina)
        self.assertIn("Entrar", pagina)

    def test_validacoes_de_cadastro_e_mensagem_generica_de_login(self):
        resposta = self.client.post(
            "/cadastro",
            data=self.dados_de_cadastro(
                telefone="telefone (31) 99327-0377 inválido",
                senha="curta",
                confirmar_senha="diferente",
                consentimento="",
            ),
        )
        conteudo = resposta.get_data(as_text=True)
        self.assertIn("telefone com DDD", conteudo)
        self.assertIn("pelo menos 8 caracteres", conteudo)
        self.assertIn("As senhas não conferem", conteudo)
        self.assertIn("É necessário concordar", conteudo)

    def test_senha_precisa_de_letra_e_numero_e_email_e_unico(self):
        self.client.post("/cadastro", data=self.dados_de_cadastro())

        resposta = self.client.post(
            "/cadastro",
            data=self.dados_de_cadastro(email="MARIA@example.com"),
        )
        self.assertIn(
            "Este e-mail já está cadastrado",
            resposta.get_data(as_text=True),
        )

        resposta = self.client.post(
            "/cadastro",
            data=self.dados_de_cadastro(
                email="outra@example.com",
                senha="12345678",
                confirmar_senha="12345678",
            ),
        )
        self.assertIn(
            "pelo menos uma letra",
            resposta.get_data(as_text=True),
        )

        resposta = self.client.post(
            "/login",
            data={"email": "nao-existe@example.com", "senha": "qualquer"},
        )
        self.assertIn(
            "E-mail ou senha inválidos.",
            resposta.get_data(as_text=True),
        )

    def test_limita_login_a_cinco_tentativas_por_minuto(self):
        for _ in range(5):
            resposta = self.client.post(
                "/login",
                data={"email": "nao-existe@example.com", "senha": "errada"},
            )
            self.assertEqual(resposta.status_code, 200)

        resposta = self.client.post(
            "/login",
            data={"email": "nao-existe@example.com", "senha": "errada"},
        )
        self.assertEqual(resposta.status_code, 429)
        self.assertIn("Aguarde um minuto", resposta.get_data(as_text=True))

    def test_protege_formularios_com_csrf(self):
        app_com_csrf = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "chave-csrf",
                "SQLALCHEMY_DATABASE_URI": "sqlite://",
                "WTF_CSRF_ENABLED": True,
                "RATELIMIT_STORAGE_URI": "memory://",
            }
        )
        try:
            resposta = app_com_csrf.test_client().post(
                "/cadastro",
                data=self.dados_de_cadastro(),
            )
            self.assertEqual(resposta.status_code, 400)
            self.assertIn("formulário expirou", resposta.get_data(as_text=True))
        finally:
            with app_com_csrf.app_context():
                db.session.remove()
                db.engine.dispose()


if __name__ == "__main__":
    unittest.main()
