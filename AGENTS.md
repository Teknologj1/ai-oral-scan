# AI Oral Scan — instruções permanentes

## Propósito
Plataforma de triagem odontológica escolar, continuidade de encaminhamentos e inteligência territorial. Desenvolvimento orientado por AI-First: agentes podem implementar e verificar mudanças; decisões de arquitetura, segurança e produto devem ser documentadas e revisadas por humanos.

## Regras clínicas e de dados
- Não emitir diagnóstico definitivo, prioridade ou encaminhamento por IA. Decisões clínicas pertencem ao cirurgião-dentista.
- IA clínica experimental deve permanecer desativada por padrão (`AI_CLINICAL_ENABLED=false`). Nenhum dado ou imagem real de estudante em desenvolvimento/teste.
- Dados identificáveis e analíticos ficam separados; analytics sempre agregados e com proteção contra grupos pequenos.
- Usar somente dados sintéticos em fixtures, documentação executável e screenshots.
- Não registrar segredos, tokens, nomes, documentos ou imagens em logs. Não comitar credenciais; usar `.env` local ignorado e `.env.example` sem segredos.
- Toda operação protegida valida papel e escopo territorial, nega por padrão e audita ações sensíveis.

## Engenharia
- Monorepo: `apps/web` (Next.js/TypeScript), `apps/field` (Flutter Android), `apps/api` (FastAPI), `infra` e `docs`.
- Mudanças em schema exigem migração versionada e testes. API pública fica sob `/api/v1`.
- Testes devem ser determinísticos e independentes de serviços externos. Mudanças de autenticação devem cobrir sucesso, falha, sessão inválida e autorização.
- Preferir alterações pequenas, revisáveis e documentadas. Atualizar README/ADRs quando mudar decisões estruturais.
- Antes de fechar uma tarefa, executar os testes relevantes, corrigir falhas e relatar limitações de ambiente.
