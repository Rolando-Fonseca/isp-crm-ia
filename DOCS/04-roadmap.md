# Roadmap (SemVer)

| Versión | Contenido |
|---|---|
| `0.1.0` | Planificación y documentación inicial (este entregable). |
| `0.2.0` | Esqueleto del CRM (Next.js + Prisma + Postgres) con pipeline de leads, sin IA todavía. |
| `0.3.0` | Webhook de WhatsApp Cloud API funcionando (recibir y responder mensajes de eco, sin IA). |
| `0.4.0` | Agente clasificador de intención + creación automática de leads desde WhatsApp. |
| `0.5.0` | RAG sobre base de conocimiento de programas/universidades. |
| `0.6.0` | Cola de aprobación humana (human-in-the-loop) para acciones sensibles. |
| `0.7.0` | Plantillas de mensaje y recordatorios automáticos de documentación. |
| `1.0.0` | Release estable: pipeline completo + agente + human-in-the-loop en producción de demo. |

Cada versión minor pasa antes por: research/auditoría → debate multiagente tipo
"Predict" → auditoría Red Team, siguiendo la metodología documentada en
`Workshop 4 y 8 CRM.txt`.
