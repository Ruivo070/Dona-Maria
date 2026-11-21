import re
import unittest
from datetime import timedelta
from html import unescape
from urllib.parse import parse_qs, urlsplit

from sqlalchemy import select

from app import create_app
from models import Reserva, Usuario, db
from routes.reservas_forms import hoje_em_betim


class ReservasTests(unittest.TestCase):
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
            self.usuario = self.criar_usuario("ana@example.com", "Ana Silva")
            self.outro_usuario = self.criar_usuario("bia@example.com", "Bia Souza")
            db.session.commit()
            self.usuario_id = self.usuario.id
            self.outro_usuario_id = self.outro_usuario.id

        self.client = self.app.test_client()
        self.outro_cliente = self.app.test_client()
        self.entrar(self.client, "ana@example.com")
        self.entrar(self.outro_cliente, "bia@example.com")

    def criar_usuario(self, email, nome):
        usuario = Usuario(
            nome=nome,
            email=email,
            telefone="31999999999",
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

    def data_de_segunda_futura(self):
        hoje = hoje_em_betim()
        dias_ate_segunda = (0 - hoje.weekday()) % 7 or 7
        return (hoje + timedelta(days=dias_ate_segunda)).isoformat()

    def dados_de_reserva(self, **alteracoes):
        dados = {
            "data_reserva": self.data_de_segunda_futura(),
            "horario": "12:30",
            "numero_pessoas": "4",
            "observacao": "Aniversário",
        }
        dados.update(alteracoes)
        return dados

    def test_cria_reserva_e_mensagem_whatsapp_com_dados(self):
        resposta = self.client.post(
            "/reservar",
            data=self.dados_de_reserva(),
        )
        self.assertEqual(resposta.status_code, 200)
        pagina = resposta.get_data(as_text=True)
        self.assertIn("Reserva pendente", pagina)
        self.assertIn("Enviar pelo WhatsApp", pagina)

        link = re.search(r'href="(https://wa\.me/[^"]+)"', pagina)
        self.assertIsNotNone(link)
        mensagem = parse_qs(urlsplit(unescape(link.group(1))).query)["text"][0]
        self.assertIn("Nome: Ana Silva", mensagem)
        self.assertIn("Horário: 12:30", mensagem)
        self.assertIn("Número de pessoas: 4", mensagem)
        self.assertIn("Observação: Aniversário", mensagem)

        with self.app.app_context():
            reserva = db.session.execute(select(Reserva)).scalar_one()
            self.assertEqual(reserva.usuario_id, self.usuario_id)
            self.assertEqual(reserva.status, "pendente")

        minhas = self.client.get("/minhas-reservas").get_data(as_text=True)
        self.assertIn("Aniversário", minhas)
        outras = self.outro_cliente.get("/minhas-reservas").get_data(as_text=True)
        self.assertNotIn("Aniversário", outras)
        self.assertIn("Você ainda não tem reservas", outras)

    def test_valida_data_horario_e_quantidade(self):
        ontem = (hoje_em_betim() - timedelta(days=1)).isoformat()
        resposta = self.client.post(
            "/reservar",
            data=self.dados_de_reserva(data_reserva=ontem),
        )
        self.assertIn("não pode estar no passado", resposta.get_data(as_text=True))

        resposta = self.client.post(
            "/reservar",
            data=self.dados_de_reserva(horario="16:00"),
        )
        self.assertIn(
            "dentro do funcionamento",
            resposta.get_data(as_text=True),
        )

        resposta = self.client.post(
            "/reservar",
            data=self.dados_de_reserva(numero_pessoas="21"),
        )
        self.assertIn("1 a 20 pessoas", resposta.get_data(as_text=True))

    def test_usuario_nao_cancela_reserva_de_outra_pessoa(self):
        resposta = self.client.post(
            "/reservar",
            data=self.dados_de_reserva(),
        )
        self.assertEqual(resposta.status_code, 200)
        with self.app.app_context():
            reserva = db.session.execute(select(Reserva)).scalar_one()
            reserva_id = reserva.id

        resposta = self.outro_cliente.post(
            f"/minhas-reservas/{reserva_id}/cancelar"
        )
        self.assertEqual(resposta.status_code, 404)

        resposta = self.client.post(
            f"/minhas-reservas/{reserva_id}/cancelar"
        )
        self.assertEqual(resposta.status_code, 302)
        with self.app.app_context():
            reserva = db.session.get(Reserva, reserva_id)
            self.assertEqual(reserva.usuario_id, self.usuario_id)
            self.assertNotEqual(reserva.usuario_id, self.outro_usuario_id)
            self.assertEqual(reserva.status, "cancelada")


if __name__ == "__main__":
    unittest.main()
