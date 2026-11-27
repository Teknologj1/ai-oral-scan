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
3. API: em `apps/api`, crie e ative um ambiente virtual, execute `pip install -e '.[dev]'` e `uvicorn ai_oral_scan.main:app --reload`.
4. Provisione uma conta local com `python -m ai_oral_scan.commands admin@example.test state_admin state --password 'replace-this-local-password'`. Cadastro público está desativado.
5. Web: em `apps/web`, execute `npm install` e `npm run dev`.
6. Campo: em `apps/field`, execute `flutter pub get` e `flutter run` em dispositivo/emulador Android.

API docs locais: `http://localhost:8000/docs`. Endpoints iniciais: `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, `GET /api/v1/admin/ping`.

## Testes

- API: `pytest` em `apps/api`.
- Web: `npm run lint` e `npm run build` em `apps/web`.
- Campo: `flutter test` e `flutter analyze` em `apps/field`.

Não há logout com revogação de token ou MFA neste incremento. Antes de ambientes compartilhados, configure segredo forte fora do repositório e use PostgreSQL. Nunca use dados reais de estudantes no desenvolvimento.