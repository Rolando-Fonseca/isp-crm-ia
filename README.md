# ISP CRM IA

CRM con inteligencia artificial y canal de WhatsApp para gestión de leads de
estudiantes internacionales (consulta → documentación → aplicación → visado →
matrícula).

> **Proyecto de portafolio, independiente de producción.** Este repositorio se
> desarrolla en paralelo a `international-student-platform` y **no lo modifica ni
> depende de él**. No contiene ni contendrá datos reales de convenios, alumnos ni
> instituciones. Si el resultado madura lo suficiente, se evaluará integrarlo al
> proyecto real más adelante.

## Estado

`v0.3.0-dev` — CRM en `crm-web/` (Next.js + Tailwind + Prisma) conectado a
Postgres local real vía Docker. Pipeline de leads leyendo y sembrado desde la
base de datos. Falta el canal de WhatsApp.

## Desarrollo local

```bash
# 1. Levantar Postgres local (puerto 5434, ver docker-compose.yml)
docker compose up -d

# 2. CRM
cd crm-web
npm install
cp .env.example .env   # ya viene apuntando a localhost:5434
npx prisma migrate dev  # crea las tablas
npx prisma db seed      # carga leads de ejemplo
npm run dev
```

Abre [http://localhost:3002](http://localhost:3002). Puerto fijo `3002` (rango
académico 3001-3008, ver `DOCS`). Postgres local en `5434` — nunca usar los
puertos de producción de V1 (3000, 4000, 5433, 5555, 6379), que están corriendo
en el mismo Docker de la máquina.

**Importante:** este proyecto usa **npm**, no pnpm. Existe un `pnpm-workspace.yaml`
en `C:\Users\liand` que puede interferir con la instalación si se usa pnpm dentro
de este árbol (mismo problema documentado en HappiTrip).

## Visión

Automatizar el primer contacto y el seguimiento de leads por WhatsApp con agentes de
IA, dejando siempre una aprobación humana antes de cualquier acción destructiva o
envío masivo (human-in-the-loop), y centralizando todo en un CRM propio en vez de
depender de herramientas externas tipo HubSpot/Klaviyo.

## Arquitectura (resumen)

Dos servicios desacoplados, comunicados por API/webhooks:

1. **CRM web** — Next.js + Prisma + PostgreSQL + Tailwind. Pipeline de leads,
   fichas de estudiante, dashboard, gestión de tareas.
2. **Servicio de agentes IA** ("Hermes") — Python (FastAPI), contenedor
   independiente. Recibe webhooks de WhatsApp Cloud API, clasifica intención,
   consulta al CRM, responde o escala a un humano.

Detalle completo en [`DOCS/01-arquitectura.md`](DOCS/01-arquitectura.md).

## Documentación

- [`DOCS/01-arquitectura.md`](DOCS/01-arquitectura.md) — arquitectura general y flujo de datos.
- [`DOCS/02-whatsapp-cloud-api.md`](DOCS/02-whatsapp-cloud-api.md) — integración con Meta WhatsApp Cloud API.
- [`DOCS/03-mvp-scope.md`](DOCS/03-mvp-scope.md) — alcance propuesto del MVP (borrador, pendiente de validar).
- [`DOCS/04-roadmap.md`](DOCS/04-roadmap.md) — hoja de ruta por versiones (SemVer desde 0.1.0).
- [`Workshop 4  y 8 CRM.txt`](Workshop%204%20%20y%208%20CRM.txt) — notas originales de Codeiando que inspiran el diseño (Hermes, Git Flow, Predict, Red Team).

## Flujo de trabajo (Git Flow)

- `main` — solo releases estables, protegida.
- `develop` — integración de todo el desarrollo.
- Ramas de feature/fix desde `develop`, merge por PR.
- Versionado semántico desde `0.1.0`.

## Stack propuesto

| Área | Herramienta |
|---|---|
| Frontend/CRM | Next.js, Tailwind |
| Base de datos | PostgreSQL + Prisma |
| Canal de mensajería | Meta WhatsApp Cloud API |
| Orquestación de agentes | Python + FastAPI + LangGraph/CrewAI |
| Búsqueda semántica (RAG) | pgvector |
| Testing | Vitest |
| Infraestructura | Docker + EasyPanel (self-hosted) |
