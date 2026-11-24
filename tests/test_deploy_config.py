import os
import unittest
from unittest.mock import patch

from app import create_app


class ConfiguracaoDeployTests(unittest.TestCase):
    def test_render_exige_database_url(self):
        with patch.dict(os.environ, {"RENDER": "true"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "DATABASE_URL"):
                create_app()

    def test_render_nao_permite_sqlite(self):
        with patch.dict(
            os.environ,
            {"RENDER": "true", "DATABASE_URL": "sqlite:///app.db"},
            clear=True,
        ):
            with self.assertRaisesRegex(RuntimeError, "SQLite só pode"):
                create_app()

    def test_render_normaliza_urls_postgres_para_psycopg2(self):
        for database_url in (
            "postgres://localhost/dona_maria",
            "postgresql://localhost/dona_maria",
        ):
            with self.subTest(database_url=database_url), (
                patch.dict(
                    os.environ,
                    {
                        "RENDER": "true",
                        "DATABASE_URL": database_url,
                        "SECRET_KEY": "chave-de-teste",
                    },
                    clear=True,
                )
            ), patch("app.db.create_all"), patch(
                "app.INDICE_ADMIN_UNICO.create"
            ), patch("app.criar_dados_iniciais"), patch("app.criar_dono_configurado"):
                app = create_app()

            self.assertEqual(
                app.config["SQLALCHEMY_DATABASE_URI"],
                "postgresql+psycopg2://localhost/dona_maria",
            )


if __name__ == "__main__":
    unittest.main()
