# AI Oral Scan — Arquitetura e plano inicial

**Status:** proposta para revisão antes da implementação  
**Produto:** Teknologji · piloto estadual em escolas públicas

## Visão do produto e premissas do piloto

O AI Oral Scan deve conectar avaliação odontológica escolar, encaminhamento e confirmação de acesso ao cuidado. Os painéis apoiarão o planejamento da rede com indicadores agregados e cobertura explícita, sem expor a identidade dos estudantes. A plataforma terá desenho expansível, mas a validação começa em piloto controlado. O PSE e a APS são o contexto institucional de articulação; adesão, responsabilidades e fluxos precisam ser pactuados com cada ente participante.

Como referência de dimensionamento, o projeto executivo sugere 10 escolas em 2 a 3 municípios, até 2.000 estudantes elegíveis, duas equipes móveis com cirurgião-dentista e nove meses. São premissas de planejamento sujeitas à pactuação, capacidade de encaminhamento e orçamento, não metas aprovadas. O estudo proposto é de viabilidade com seleção intencional; seus resultados não devem ser extrapolados automaticamente para todo o Estado.

## 1. Objetivo e limites do primeiro ciclo

Construir a fundação de uma plataforma web responsiva, instalável como PWA, para operação de triagem odontológica escolar e produção posterior de indicadores agregados. A primeira entrega deve estabelecer um repositório executável, ambientes local e de teste, modelo de dados inicial, autenticação e documentação.

O piloto começa sem análise clínica por IA: o recurso experimental fica explicitamente desativado por padrão. Não serão usados dados reais de estudantes no desenvolvimento. Nesta fase não serão implementados todos os módulos operacionais, fluxos clínicos, dashboards ou integrações de produção.

## 2. Arquitetura proposta

Começar com um **monólito modular**, implantável com serviços separados para web, API e banco. Isso reduz o custo operacional do piloto e mantém limites claros para futura extração de serviços quando houver necessidade comprovada.

```text
App Flutter (tablet Android; operação offline de campo)
Painel web Next.js/React (gestão, revisão e relatórios)
          │ HTTPS / API versionada
          ▼
FastAPI (autenticação, autorização, domínio, auditoria)
     ├── PostgreSQL + PostGIS
     ├── Object Storage (imagens; interface compatível S3)
     └── Porta de IA (sem provedor ativo no primeiro ciclo)

Ambiente local: Docker Compose · web + API + PostgreSQL/PostGIS + storage local
CI: lint, tipos, testes e verificações de migração com dados sintéticos
```

### Fronteiras dos módulos

- **Identidade e acesso:** usuários, papéis, escopo territorial e sessões.
- **Gestão pública:** estado, municípios, regiões administrativas, escolas, turmas, campanhas e equipes.
- **Registro clínico:** estudante pseudonimizado, triagem e questionário.
- **Mídia:** metadados, autorização de acesso e referência a objetos privados.
- **Revisão odontológica:** avaliação humana, prioridade e encaminhamentos.
- **Encaminhamentos e continuidade:** acompanhamento do fluxo até a confirmação de atendimento, sem importar prontuários da rede no MVP.
- **Inteligência territorial:** indicadores agregados com denominadores, cobertura, série temporal e proteção contra reidentificação.
- **Auditoria:** eventos append-only de acesso e ações relevantes.
- **IA:** interface substituível de provedor, resultados experimentais versionados e recurso desligado por configuração.

Os módulos ficam inicialmente no mesmo backend, mas com pacotes, contratos e regras de dependência definidos para não misturar identidade, dados clínicos, mídia e analytics.

## 3. Decisões técnicas propostas

- **Aplicativo de campo:** Flutter para tablets Android, offline-first, com armazenamento local protegido, fila idempotente, estado visível de sincronização, reconciliação e expiração. Não guardar imagens localmente sem decisão de segurança para o dispositivo.
- **Painel web:** Next.js + React + TypeScript + Tailwind CSS, responsivo e instalável como PWA para gestão, revisão e relatórios. Ambos os clientes usam a API versionada.
- **Backend:** Python + FastAPI, API `/api/v1`, validação de entrada e documentação OpenAPI.
- **Persistência:** PostgreSQL + PostGIS; migrações versionadas. PostGIS fica disponível desde o início, embora coordenadas exatas de escolas sejam tratadas como dado sensível e não sejam expostas em agregados públicos.
- **Imagens:** Object Storage privado, acesso por URLs assinadas de curta duração emitidas após autorização. O banco guarda metadados e chaves de objeto, não blobs.
- **Autenticação inicial:** login por e-mail e senha com hash moderno, tokens de curta duração e refresh revogável em cookie seguro quando suportado. Papéis iniciais: administrador estadual, gestor municipal, operador de campo, cirurgião-dentista e analista. Toda autorização também verifica o escopo territorial; papel sozinho não concede acesso a todos os municípios.
- **IA:** contrato de provedor independente; configuração `AI_CLINICAL_ENABLED=false` como padrão. Sem envio de imagens para provedores no primeiro ciclo. Respostas futuras serão achados auxiliares, nunca diagnóstico ou prioridade final.
- **Execução local:** Docker Compose, `.env.example` sem segredos, dados de demonstração sintéticos e comandos documentados.
- **Testes:** Vitest/Testing Library no frontend; pytest no backend; testes de API e migrações com banco de teste. CI em GitHub Actions após criação/conexão do repositório.

## 4. Modelo de dados inicial

Separar esquemas ou, no mínimo, módulos de persistência distintos para identidade e dados de operação. A separação lógica não substitui controles de acesso, criptografia, auditoria ou revisão de privacidade.

| Entidade | Campos e relações principais |
|---|---|
| `user` | e-mail normalizado, hash de senha, estado, datas; sem dados de estudante |
| `role_assignment` | usuário, papel, escopo (estado/município/escola), validade |
| `state`, `municipality`, `region` | códigos oficiais e relações territoriais; geometrias PostGIS apenas quando necessárias |
| `school` | município, código externo, nome, localização restrita e estado |
| `campaign` | escola/município, período, estado e responsáveis |
| `class_group` | escola, turma e período letivo; identificação operacional mínima |
| `student_identity` | vínculo escolar, dados mínimos identificáveis necessários ao contato; acesso separado e restrito |
| `student_subject` | UUID pseudônimo e vínculo à identidade por tabela/serviço restrito; sem nome ou documento nos dados analíticos |
| `screening` | sujeito pseudônimo, campanha, operador, data, estado e chave de idempotência |
| `questionnaire_response` | triagem, versão do instrumento e respostas tipadas |
| `image_asset` | triagem, chave privada do objeto, tipo, checksum, metadados de captura, retenção e estado de consentimento/autorização |
| `clinical_review` | triagem, dentista revisor, observações, prioridade validada, versão e data; registro de decisão humana |
| `referral` | revisão, destino/tipo, status e datas; mínimo necessário para acompanhamento |
| `care_follow_up` | encaminhamento, status de contato/atendimento, fonte da confirmação e data; dados mínimos |
| `ai_analysis` | triagem/imagem, provedor e versão, configuração experimental, saída estruturada, incerteza e status; nunca decisão clínica final |
| `audit_event` | ator, ação, recurso, escopo, data, resultado e correlação; sem copiar conteúdo clínico desnecessário |

Chaves primárias UUID; datas em UTC; timestamps de criação/atualização; exclusão lógica somente onde houver justificativa e política de retenção definida. Restrições e chaves estrangeiras serão aplicadas no banco. Dados analíticos serão derivados de consultas agregadas e não incluirão identificadores diretos. Indicadores exibirão numerador, denominador e cobertura; prevalências serão calculadas entre os efetivamente examinados e apresentadas com a cobertura correspondente. Evitar rankings estigmatizantes de escolas e comunidades e suprimir grupos pequenos.

As categorias P1 urgente, P2 prioritária, P3 programada e P4 preventiva são apenas uma proposta de protocolo. Cirurgiões-dentistas e gestores devem aprovar critérios, prazos e fluxos de urgência. Sintomas como dor e febre exigem questionário e avaliação profissional: não podem ser inferidos somente da imagem. A classificação final e o encaminhamento são decisões do dentista.

## 5. Segurança e governança no desenho

- Negar acesso por padrão, validar papel **e** escopo em cada operação e registrar acessos sensíveis.
- Não colocar nomes, documentos, imagens ou tokens em logs, fixtures públicas ou telemetria.
- Segredos somente por variáveis de ambiente/secret manager; `.env` ignorado pelo Git.
- Object Storage privado; TLS em trânsito; criptografia em repouso conforme infraestrutura escolhida.
- Rotas e consultas de analytics devem agregar resultados e definir limiar mínimo de grupo para reduzir risco de reidentificação.
- Offline implica risco de dispositivo perdido: persistir apenas o mínimo, proteger armazenamento, limitar retenção e permitir revogação/limpeza após sincronização.
- Antes de produção: avaliação de privacidade e segurança, política de retenção, base legal e consentimentos/autorização aplicáveis a menores, contratos de hospedagem e análise regulatória da finalidade clínica.

## 6. Plano de implementação por etapas

### Etapa 0 — Revisão desta proposta
Confirmar arquitetura, autenticação e escolhas de implantação. Registrar decisões pendentes antes de codificar os fundamentos.

### Etapa 1 — Fundação do repositório
Criar `AGENTS.md`, estrutura `apps/web`, `apps/api`, `infra`, `docs`; Docker Compose; exemplos de ambiente; lint, formatação e CI; comandos de desenvolvimento. Documentar decisões em ADRs curtos.

### Etapa 2 — Persistência e contrato da API
Criar migrações iniciais para identidade, território mínimo, campanhas, estudantes pseudonimizados, triagem e auditoria. Gerar esquema OpenAPI e validar migrações em banco descartável.

### Etapa 3 — Autenticação e autorização
Implementar login, logout, renovação/revogação, hashing de senha, papéis e escopo territorial. Cobrir tentativas inválidas, usuário desativado, sessão revogada e acesso entre escopos.

### Etapa 4 — Clientes e experiência de acesso
Criar shell autenticado do painel web e base do app de campo. Validar instalação PWA no painel e preparar o aplicativo Android. A captura clínica e a fila offline completa entram em etapa posterior, após requisitos de dispositivo, retenção local e segurança aprovados.

### Etapa 5 — Verificação e handoff
Executar suíte local e CI, corrigir falhas, documentar instalação, variáveis, migrações, criação de usuário local e limitações conhecidas. Só então avançar para cadastro e fluxo de triagem.

## 7. Critérios de conclusão do primeiro incremento

- Repositório sobe localmente com um comando documentado e configuração de exemplo.
- Web e API se comunicam; migrações criam o schema em PostgreSQL/PostGIS.
- Login funciona com dados sintéticos e autorização bloqueia acesso sem papel/escopo.
- `AI_CLINICAL_ENABLED` permanece falso e não existe envio de imagem para IA.
- Testes de frontend, API, autenticação/autorização e migração passam no ambiente local/CI.
- `AGENTS.md`, README e documentação explicam arquitetura, convenções, testes, dados sintéticos e limites clínicos.

## 8. Decisões que permanecem abertas

1. **Provedor de identidade:** autenticação própria mínima no piloto ou serviço OIDC gerenciado. A proposta acima assume autenticação própria inicial para manter o setup reproduzível; antes de produção, avaliar IdP gerenciado e MFA.
2. **Hospedagem:** nuvem e região ainda não escolhidas. A arquitetura evita dependência de fornecedor e usa interface S3 para objetos.
3. **Identificadores de estudante:** campos estritamente necessários e regras de retenção devem ser definidos com a operação e responsáveis por privacidade antes dos formulários reais.
4. **Offline:** definir dispositivos Android gerenciados, proteção do armazenamento local e prazo máximo para dados não sincronizados antes de persistir dados clínicos no tablet.
5. **IA clínica:** provedor, finalidade, protocolo de validação e aprovação regulatória ficam fora do primeiro incremento.
6. **Operação do piloto:** confirmar território, escolas, dimensionamento, cliente institucional e recursos da rede para receber os encaminhamentos; valores do documento executivo são parâmetros iniciais, não compromissos.
7. **Validação profissional:** definir responsáveis clínicos, protocolo, consentimentos/autorização aplicáveis e fluxo de urgência antes do campo.
8. **Aplicativo de campo:** Flutter é a referência do projeto executivo para operação Android offline; isso implica manter dois clientes (Flutter e Next.js). Revalidar custo e escopo antes da fundação do repositório.

## 9. Direção alinhada ao material de referência

Esta proposta adota AI-First Development: Codex como agente principal para implementar, documentar e executar verificações, com revisão humana das decisões de arquitetura, segurança e clínica. Isso é distinto da IA dentro do produto: o módulo de visão computacional começa em ambiente controlado e modo observacional (shadow mode), sem diagnosticar, priorizar ou alterar a decisão do dentista. O desenho de referência usa Flutter no campo, painel Next.js/React, FastAPI, PostgreSQL/PostGIS e Object Storage. O piloto tem escala limitada e não deve ser usado para alegações epidemiológicas estaduais. Seleção de modelos clínicos e qualquer uso assistivo dependem de protocolo, governança, evidência e avaliação regulatória.
