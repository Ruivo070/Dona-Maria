# Restaurante Dona Maria Betim

Aplicação Flask em desenvolvimento por etapas. A página pública mantém o visual e as interações do site original; rodízios e cardápio vêm do banco. Cadastro e login estão disponíveis, com proteção CSRF e limite de tentativas. A pasta `docs/` contém os documentos do projeto e não faz parte dos arquivos servidos pelo site.

## Rodar localmente

Requer Python 3.12.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Gere uma chave secreta com `python -c "import secrets; print(secrets.token_hex(32))"` e preencha `SECRET_KEY` no `.env`. Deixe `DATABASE_URL` vazio para usar `instance/app.db` localmente. Em seguida, execute:

```powershell
flask --app app run
```

Abra `http://127.0.0.1:5000`. Quando `DATABASE_URL` estiver vazio ou não definido, o Flask cria `instance/app.db`, as tabelas da aplicação e inclui os dados iniciais de rodízios e cardápio.

## Publicar no Render

1. Envie a raiz deste projeto para um repositório Git.
2. No Render, escolha **New + → Blueprint** e conecte o repositório.
3. O `render.yaml` configura um **Web Service** Python, instala `requirements.txt` e inicia `gunicorn wsgi:app`.
4. O Blueprint cria um PostgreSQL e associa sua URL a `DATABASE_URL`; também gera `SECRET_KEY` automaticamente.
5. Confira os logs do serviço e acesse a URL criada. As tabelas são criadas no primeiro início do app.

O SQLite é usado somente localmente. Em produção, o app exige `DATABASE_URL` e recusa iniciar com SQLite. O banco PostgreSQL do Render persiste os dados entre reinicializações.

## Dados do cardápio

O seed inicial reproduz os rodízios e o cardápio que estavam no JavaScript do site estático. Os valores continuam sendo referências e devem ser confirmados pelo restaurante.

## Testes

```powershell
python -m unittest discover -s tests -v
```

## Cadastro, login e privacidade

As páginas `/cadastro`, `/login`, `/sair` e `/privacidade` usam formulários com CSRF. As senhas são armazenadas com hash. O login limita tentativas a cinco por minuto por endereço IP. O armazenamento de limite padrão é em memória; se o serviço for escalado para vários processos ou instâncias, configure `RATELIMIT_STORAGE_URI` para um armazenamento compartilhado, como Redis.

Usuários cadastrados podem criar reservas em `/reservar` e consultar ou cancelar suas próprias reservas em `/minhas-reservas`. O servidor valida datas, horários de funcionamento e quantidade de pessoas; a confirmação oferece um link para enviar os dados ao restaurante pelo WhatsApp.

## Painel do dono

O painel fica em `/admin` e permite filtrar e atualizar reservas, editar rodízios e adicionar, alterar ou remover itens e serviços do cardápio. A aba de usuários exibe somente dados de cadastro, nunca hashes de senha. O banco impede mais de uma conta de dono.

Para criar o dono em uma instalação sem conta administrativa, execute `flask --app app criar-admin`. O comando solicita o e-mail e a senha sem exibi-la; a senha é armazenada somente como hash. Para trocar a senha depois, use `flask --app app alterar-senha-admin`. Também é possível definir `ADMIN_EMAIL` e `ADMIN_PASSWORD` no ambiente antes do primeiro início do app. No Render, configure essas variáveis na página do serviço; elas não ficam gravadas no repositório. O dono é criado uma única vez e mudanças posteriores nas variáveis não trocam a senha existente. A conta já foi criada no banco SQLite local deste ambiente; antes de publicar, prefira uma senha forte e exclusiva.
