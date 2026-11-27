# Modelo de dados inicial

## Fronteira entre identidade e operação

`student_identities` é uma tabela restrita para uma referência de contato cifrada; não deve conter nome/documento em claro. `student_subjects` usa identificador aleatório e só guarda faixa etária, escola e campanha. Serviços analíticos não consultam nem recebem a referência de identidade. A cifra, as chaves e a política operacional de reidentificação ainda precisam ser definidos antes de inserir dados reais.

## Território e campanha

- `municipalities` usa o código IBGE e UF.
- `regions` pertence a um município.
- `schools` pertence ao município; localização/geometria será acrescentada após definir precisão e política de acesso.
- `campaigns` delimita escola e período de campo.

## Triagem e auditoria

`screenings` vincula sujeito pseudônimo, campanha e operador, com chave idempotente para suportar sincronização offline. `audit_events` guarda ator, ação, recurso, escopo e resultado, sem payload clínico. As decisões clínicas, questionário, mídia e encaminhamentos serão migrações posteriores sob protocolo aprovado.

## Migrações

Aplicar com `alembic upgrade head` em `apps/api`. Não usar `Base.metadata.create_all()` na aplicação. Toda alteração futura de schema deve gerar migração e teste de upgrade em banco temporário.

## Acesso e sessões

`role_assignments` permite atribuir papel por escopo `state`, `municipality` ou `school`; contas sem atribuição ativa não autenticam. `auth_sessions` armazena hash do refresh token, identificador do access token atual, expiração e revogação. A renovação troca refresh token e `jti`, invalidando o access anterior; logout revoga a sessão. O migration inicial de autorização converte os papéis/escope antigos para atribuições explícitas.
