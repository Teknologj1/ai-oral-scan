# Arquitetura inicial

O sistema é um monólito modular na API e dois clientes: aplicativo Flutter Android para campo e painel web Next.js instalável como PWA. Os clientes usam a API versionada FastAPI. PostgreSQL/PostGIS armazena registros e objetos privados serão integrados depois por interface Object Storage. O módulo clínico de IA está fora do fluxo inicial e permanece `AI_CLINICAL_ENABLED=false`.

## Modelo de dados inicial

O primeiro incremento implementa somente `users` e base de autenticação. As próximas migrações devem introduzir: territórios (`state`, `municipality`, `region`), `school`, `class_group`, `campaign`, separação `student_identity`/`student_subject`, `screening`, `questionnaire_response`, `image_asset`, `clinical_review`, `referral`, `care_follow_up`, `ai_analysis` experimental e `audit_event`. Chaves UUID, timestamps UTC, dados sintéticos em teste. Analytics não carrega identificadores diretos; resultados incluem cobertura e denominadores, com supressão de grupos pequenos.

## Autorização

Papéis previstos: `state_admin`, `municipal_manager`, `field_operator`, `dentist`, `analyst`. A conta é provisionada fora da API pública. Toda rota de domínio deve conferir papel e escopo territorial; a rota `/admin/ping` demonstra apenas a checagem de papel, ainda sem dados operacionais.

## Decisões pendentes

Hospedagem/região, identidade gerenciada e MFA, protocolo clínico, acordos com PSE/APS, gestão de dispositivos offline, retenção de imagens e interface de acompanhamento da rede pública. Registrar decisões estruturais em ADRs antes de implementar esses fluxos.
