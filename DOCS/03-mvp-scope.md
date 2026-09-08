# Alcance del MVP (borrador — pendiente de validar con Rolando)

Este documento es un punto de partida para la conversación de alcance, no una
decisión cerrada.

## Propuesta de alcance v1.0

**Pipeline de leads (5 etapas):**
1. Consulta
2. Documentación
3. Aplicación
4. Visa
5. Matrícula

**Canal:**
- Solo WhatsApp (Meta Cloud API) para v1. Email/Telegram quedan fuera del MVP.

**Agente IA — capacidades mínimas:**
- Clasificar intención del mensaje entrante.
- Responder preguntas frecuentes usando RAG sobre una base de conocimiento de
  programas/universidades (datos ficticios para el portafolio).
- Crear/actualizar el lead en el CRM automáticamente a partir de la conversación.
- Escalar a un humano cuando la confianza es baja o el usuario lo pide explícitamente.

**Fuera de alcance del MVP** (quedan en roadmap):
- Envío de recordatorios automáticos por plantillas (requiere catálogo de templates aprobado).
- Lead scoring avanzado.
- Multilenguaje.
- Dashboard de métricas avanzado.
- Integración con Telegram/email.

## Preguntas abiertas para definir con Rolando

- ¿Cuántos "programas/universidades" ficticios necesitamos para que el RAG tenga sentido en la demo?
- ¿El asesor humano aprueba desde el propio CRM o desde WhatsApp Business App?
- ¿Se necesita autenticación multiusuario en el MVP o alcanza con un solo asesor demo?
