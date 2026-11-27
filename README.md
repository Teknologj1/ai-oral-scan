# AI Oral Scan

Plataforma da Teknologji para triagem odontológica escolar, continuidade de encaminhamentos e inteligência territorial. Este repositório é uma fundação de desenvolvimento: não use dados reais de estudantes. A IA clínica permanece desligada e nenhuma imagem é enviada a um modelo.

## Arquitetura

- `apps/field`: Flutter para tablets Android; shell inicial offline-capable ainda sem persistência clínica.
- `apps/web`: painel responsivo Next.js/React/TypeScript e PWA.
- `apps/api`: FastAPI, autenticação inicial, papéis e escopos territoriais.
- `compose.yaml`: PostgreSQL 16 com PostGIS para desenvolvimento local.
- `docs/architecture.md`: decisões e limites do piloto; `AGENTS.md`: regras permanentes para agentes e colaboradores.

## Requisitos

Docker Desktop, Python 3.11+, Node.js 20.9+ e Flutter 3.22+ (Android SDK para compilar o app de campo).

## Ambiente local

1. Copie `.env.example` para `.env` e substitua `JWT_SECRET` por um segredo aleatório local. Nunca reutilize credenciais de produção.
2. Inicie o banco: `docker compose up -d db`.
3. API:

   ```powershell
   cd apps/api
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -e '.[dev]'
   uvicorn ai_oral_scan.main:app --reload
   ```

4. Em outro terminal, no diretório `apps/api`, provisione usuário local (a conta inicial não é aberta por endpoint público):

   ```powershell
   $env:DATABASE_URL='postgresql+psycopg://ai_oral_scan:change-me-local-only@localhost:5432/ai_oral_scan'
   python -m ai_oral_scan.commands admin@example.test state_admin state --password 'replace-this-local-password'
   ```

5. Web: em `apps/web`, execute `npm install` e `npm run dev`. Configure `NEXT_PUBLIC_API_URL` se a API não estiver em `http://localhost:8000`.
6. Campo: em `apps/field`, execute `flutter pub get` e `flutter run` com dispositivo/emulador Android.

API docs locais: `http://localhost:8000/docs`. Endpoints iniciais: `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, `GET /api/v1/admin/ping`.

## Testes e verificações

- API: `cd apps/api; pip install -e '.[dev]'; pytest`
- Web: `cd apps/web; npm install; npm run lint; npm run build`
- Campo: `cd apps/field; flutter test; flutter analyze`

Login usa JWT curto e senha Argon2. Provisionamento é feito por comando local, nunca por cadastro público. Logout/revogação de token e MFA ainda não fazem parte deste incremento. Antes de qualquer ambiente compartilhado, configurar segredo forte fora do repositório e substituir o SQLite de fallback por PostgreSQL.
