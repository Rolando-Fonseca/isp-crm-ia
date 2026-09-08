# Roadmap (SemVer)

| Versión | Contenido | Estado |
|---|---|---|
| `0.1.0` | Planificación y documentación inicial. | Hecho |
| `0.2.0` | Esqueleto del CRM (Next.js + Prisma + Postgres) con pipeline de leads, sin IA. | Hecho |
| `0.3.0` | Postgres real vía Docker, migraciones y seed. | Hecho |
| `0.4.0` | Servicio de agentes (FastAPI): webhook de WhatsApp Cloud API con validación de firma, creación automática de leads en el CRM y acuse de recibo. | En curso |
| `0.5.0` | Agente clasificador de intención (consulta / quiere aplicar / visado / hablar con humano) que reemplaza el acuse fijo. | |
| `0.6.0` | RAG sobre base de conocimiento de programas/universidades (pgvector). | |
| `0.7.0` | Cola de aprobación humana (human-in-the-loop) para acciones sensibles. | |
| `0.8.0` | Plantillas de mensaje y recordatorios automáticos de documentación. | |
| `1.0.0` | Release estable: pipeline completo + agente + human-in-the-loop, desplegado en EasyPanel. | |

Cada versión minor pasa antes por: research/auditoría → debate multiagente tipo
"Predict" → auditoría Red Team, siguiendo la metodología documentada en
`Workshop 4 y 8 CRM.txt`.

## Decisiones tomadas por el camino

- **Prisma 6 en vez de 7.** Prisma 7 elimina `url` del datasource y obliga a
  `prisma.config.ts` + driver adapters; se pospone la migración hasta que el
  proyecto lo justifique.
- **Teléfonos en E.164** (`+5491155550101`), el mismo formato del `wa_id` de
  WhatsApp, para que el upsert por teléfono no duplique leads.
- **Idempotencia por `waMessageId`.** Meta reintenta entregas del webhook; el
  CRM ignora mensajes ya registrados.
