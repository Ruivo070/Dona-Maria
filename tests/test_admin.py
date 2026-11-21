import os
import unittest
from datetime import date, time
from unittest.mock import patch

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app import create_app, criar_dono_configurado
from models import ItemCardapio, Reserva, Rodizio, Usuario, db


class PainelDonoTests(unittest.TestCase):
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
        with self.app.app_context():
            self.dono = self.criar_usuario("dono@example.com", "Dono do Restaurante", True)
            self.cliente = self.criar_usuario("cliente@example.com", "Cliente Teste")
            self.reserva = Reserva(
                usuario=self.cliente,
                data=date(2030, 1, 7),
                horario=time(12, 30),
                numero_pessoas=4,
                observacao="Aniversário",
            )
            db.session.add(self.reserva)
            db.session.commit()
            self.reserva_id = self.reserva.id
            self.dono_id = self.dono.id

        self.cliente_http = self.app.test_client()
        self.dono_http = self.app.test_client()
        self.entrar(self.cliente_http, "cliente@example.com")
        self.entrar(self.dono_http, "dono@example.com")

    def criar_usuario(self, email, nome, is_admin=False):
        usuario = Usuario(
            nome=nome,
            email=email,
            telefone="31999999999",
            is_admin=is_admin,
        )
        usuario.definir_senha("SenhaForte123")
        db.session.add(usuario)
        return usuario

    def entrar(self, cliente, email):
        resposta = cliente.post(
            "/login",
            data={"email": email, "senha": "SenhaForte123"},
        )
        self.assertEqual(resposta.status_code, 302)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose()

    def test_painel_exige_dono_e_nao_administra_cliente(self):
        anonimo = self.app.test_client()
        self.assertEqual(anonimo.get("/admin/").status_code, 302)
        pagina_login = anonimo.get("/admin/", follow_redirects=True)
        self.assertIn(
            "Entre na sua conta para continuar.",
            pagina_login.get_data(as_text=True),
        )
        self.assertEqual(self.cliente_http.get("/admin/").status_code, 403)
        proibido = self.cliente_http.post(
            "/admin/cardapio/novo",
            data={
                "categoria": "Serviços",
                "nome": "Item proibido",
                "descricao": "Não deve ser adicionado.",
                "preco": "R$ 1,00",
            },
        )
        self.assertEqual(proibido.status_code, 403)
        self.assertEqual(self.dono_http.get("/admin/").status_code, 200)

    def test_dono_filtra_e_altera_reserva_rodizio_e_cardapio(self):
        self.assertEqual(self.dono_http.get("/admin/?aba=rodizios").status_code, 200)
        self.assertEqual(self.dono_http.get("/admin/?aba=cardapio").status_code, 200)
        reservas = self.dono_http.get("/admin/?aba=reservas&data=2030-01-07")
        self.assertIn("Aniversário", reservas.get_data(as_text=True))
        sem_reserva = self.dono_http.get("/admin/?aba=reservas&data=2030-01-08")
        self.assertIn("Nenhuma reserva encontrada", sem_reserva.get_data(as_text=True))

        resposta = self.dono_http.post(
            f"/admin/reservas/{self.reserva_id}/status",
            data={"status": "confirmada"},
        )
        self.assertEqual(resposta.status_code, 302)
        with self.app.app_context():
            self.assertEqual(db.session.get(Reserva, self.reserva_id).status, "confirmada")
            rodizio_id = db.session.execute(
                select(Rodizio.id).order_by(Rodizio.id).limit(1)
            ).scalar_one()

        resposta = self.dono_http.post(
            f"/admin/rodizios/{rodizio_id}",
            data={
                "nome": "Rodízio atualizado",
                "preco": "R$ 120,00",
                "inclui": "Descrição atualizada",
            },
        )
        self.assertEqual(resposta.status_code, 302)
        pagina = self.dono_http.get("/").get_data(as_text=True)
        self.assertIn("Rodízio atualizado", pagina)

        resposta = self.dono_http.post(
            "/admin/cardapio/novo",
            data={
                "categoria": "Serviços",
                "nome": "Evento especial",
                "descricao": "Atendimento para eventos.",
                "preco": "Sob consulta",
            },
        )
        self.assertEqual(resposta.status_code, 302)
        pagina = self.dono_http.get("/").get_data(as_text=True)
        self.assertIn("Serviços", pagina)
        self.assertIn("Evento especial", pagina)
        with self.app.app_context():
            item = db.session.execute(
                select(ItemCardapio).where(ItemCardapio.nome == "Evento especial")
            ).scalar_one()
            item_id = item.id

        resposta = self.dono_http.post(
            f"/admin/cardapio/{item_id}",
            data={
                "categoria": "Serviços",
                "nome": "Evento atualizado",
                "descricao": "Descrição nova.",
                "preco": "R$ 200,00",
            },
        )
        self.assertEqual(resposta.status_code, 302)
        with self.app.app_context():
            self.assertEqual(db.session.get(ItemCardapio, item_id).nome, "Evento atualizado")

        resposta = self.dono_http.post(f"/admin/cardapio/{item_id}/remover")
        self.assertEqual(resposta.status_code, 302)
        with self.app.app_context():
            self.assertIsNone(db.session.get(ItemCardapio, item_id))

    def test_lista_de_usuarios_nao_exibe_hash_de_senha(self):
        with self.app.app_context():
            hash_dono = db.session.get(Usuario, self.dono_id).senha_hash

        pagina = self.dono_http.get("/admin/?aba=usuarios").get_data(as_text=True)
        self.assertIn("cliente@example.com", pagina)
        self.assertNotIn(hash_dono, pagina)
        self.assertNotIn("senha_hash", pagina)

    def test_banco_impede_um_segundo_dono(self):
        with self.app.app_context():
            outro_dono = self.criar_usuario("outro@example.com", "Outro Dono", True)
            with self.assertRaises(IntegrityError):
                db.session.commit()
            db.session.rollback()
            self.assertIsNotNone(db.session.get(Usuario, self.dono_id))
            self.assertIsNotNone(outro_dono)

    def test_comando_cria_dono_com_senha_oculta_e_hash(self):
        with patch.dict(
            os.environ,
            {"ADMIN_EMAIL": "", "ADMIN_PASSWORD": ""},
        ):
            app = create_app(
                {
                    "TESTING": True,
                    "SECRET_KEY": "chave-cli",
                    "SQLALCHEMY_DATABASE_URI": "sqlite://",
                    "WTF_CSRF_ENABLED": False,
                    "RATELIMIT_STORAGE_URI": "memory://",
                }
            )
        try:
            resultado = app.test_cli_runner().invoke(
                args=["criar-admin"],
                input="dono-cli@example.com\nSenhaForte123\nSenhaForte123\n",
            )
            self.assertEqual(resultado.exit_code, 0, resultado.output)
            with app.app_context():
                dono = db.session.execute(
                    select(Usuario).where(Usuario.email == "dono-cli@example.com")
                ).scalar_one()
                self.assertTrue(dono.is_admin)
                self.assertNotEqual(dono.senha_hash, "SenhaForte123")
                self.assertTrue(dono.conferir_senha("SenhaForte123"))

            resultado = app.test_cli_runner().invoke(
                args=["alterar-senha-admin"],
                input="SenhaNova456\nSenhaNova456\n",
            )
            self.assertEqual(resultado.exit_code, 0, resultado.output)
            with app.app_context():
                dono = db.session.execute(
                    select(Usuario).where(Usuario.email == "dono-cli@example.com")
                ).scalar_one()
                self.assertFalse(dono.conferir_senha("SenhaForte123"))
                self.assertTrue(dono.conferir_senha("SenhaNova456"))
        finally:
            with app.app_context():
                db.session.remove()
                db.engine.dispose()

    def test_variaveis_de_ambiente_criam_apenas_um_dono(self):
        with patch.dict(
            os.environ,
            {
                "ADMIN_EMAIL": "dono-env@example.com",
                "ADMIN_PASSWORD": "SenhaForte123",
            },
        ):
            app = create_app(
                {
                    "TESTING": True,
                    "SECRET_KEY": "chave-env",
                    "SQLALCHEMY_DATABASE_URI": "sqlite://",
                    "WTF_CSRF_ENABLED": False,
                    "RATELIMIT_STORAGE_URI": "memory://",
                }
            )
            try:
                with app.app_context():
                    criar_dono_configurado()
                    donos = db.session.execute(
                        select(Usuario).where(Usuario.is_admin.is_(True))
                    ).scalars().all()
                    self.assertEqual(len(donos), 1)
                    self.assertEqual(donos[0].email, "dono-env@example.com")
                    self.assertTrue(donos[0].conferir_senha("SenhaForte123"))
            finally:
                with app.app_context():
                    db.session.remove()
                    db.engine.dispose()


if __name__ == "__main__":
    unittest.main()
