import unittest

from app import create_app
from models import ItemCardapio, db


class SitePublicoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "chave-de-teste",
                "SQLALCHEMY_DATABASE_URI": "sqlite://",
            }
        )
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.engine.dispose()

    def test_pagina_inicial_usa_dados_do_banco_e_escapa_texto(self):
        resposta = self.client.get("/")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data.count(b'class="rodizio-card"'), 7)
        self.assertEqual(resposta.data.count(b'class="menu-item"'), 11)
        resposta.close()

        with self.app.app_context():
            item = db.session.get(ItemCardapio, 1)
            item.nome = "<script>alert(1)</script>"
            db.session.commit()

        resposta = self.client.get("/")
        self.assertIn(b"&lt;script&gt;alert(1)&lt;/script&gt;", resposta.data)
        self.assertNotIn(b"<script>alert(1)</script>", resposta.data)

    def test_arquivos_estaticos_e_erro_404(self):
        for caminho in (
            "/static/css/style.css",
            "/static/js/script.js",
            "/static/img/favicon.svg",
            "/robots.txt",
            "/sitemap.xml",
        ):
            with self.subTest(caminho=caminho):
                resposta = self.client.get(caminho)
                self.assertEqual(resposta.status_code, 200)
                resposta.close()

        resposta = self.client.get("/pagina-que-nao-existe")
        self.assertEqual(resposta.status_code, 404)
        self.assertIn("não foi encontrada".encode("utf-8"), resposta.data)


if __name__ == "__main__":
    unittest.main()
