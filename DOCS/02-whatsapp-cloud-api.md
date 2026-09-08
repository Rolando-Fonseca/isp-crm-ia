# Integración con Meta WhatsApp Cloud API

Decisión: usar la **Cloud API de Meta** directamente (no Twilio ni otro BSP), para no
depender de un tercero y porque el nivel gratuito de conversaciones es suficiente para
un proyecto de portafolio.

## Setup necesario (Meta for Developers)

1. Crear una app en [developers.facebook.com](https://developers.facebook.com/) de tipo
   "Business".
2. Añadir el producto **WhatsApp** a la app.
3. En el panel de WhatsApp > "Primeros pasos" obtenemos, para pruebas:
   - Un número de prueba (test number) gratuito.
   - `Phone Number ID` y `WhatsApp Business Account ID`.
   - Un token temporal (24h) para pruebas rápidas con `curl`/Postman.
4. Para desarrollo continuo, crear un **System User** en Meta Business Suite y generar
   un **token permanente** con los permisos `whatsapp_business_messaging` y
   `whatsapp_business_management`.
5. Configurar el **webhook**:
   - URL pública (en local, usar `ngrok`/`cloudflared` para exponer el servicio de
     agentes durante desarrollo).
   - `Verify Token` propio (string secreto que define el propio proyecto).
   - Suscribirse al campo `messages`.

## Variables de entorno (servicio de agentes)

```
META_WHATSAPP_TOKEN=            # token permanente del System User
META_PHONE_NUMBER_ID=
META_WABA_ID=                   # WhatsApp Business Account ID
META_WEBHOOK_VERIFY_TOKEN=      # definido por nosotros, usado en la verificación GET
META_APP_SECRET=                # para validar la firma X-Hub-Signature-256 del webhook
```

## Flujo técnico

- **Entrante**: Meta hace `POST` al webhook con el mensaje. Hay que responder `200 OK`
  rápido (procesar de forma asíncrona) y validar la firma `X-Hub-Signature-256` con
  `META_APP_SECRET` para confirmar que la petición viene de Meta.
- **Saliente**: se envía vía `POST` a
  `https://graph.facebook.com/v{version}/{PHONE_NUMBER_ID}/messages`.

## Reglas importantes que afectan el diseño del agente

- **Ventana de servicio de 24 horas**: solo se pueden enviar mensajes de texto libre
  dentro de las 24h siguientes al último mensaje del usuario. Pasado ese plazo, solo se
  pueden enviar **plantillas (templates)** pre-aprobadas por Meta. Esto condiciona los
  recordatorios automáticos de documentación (deben usar templates).
- **Plantillas de mensaje** deben crearse y aprobarse en Meta Business Manager antes de
  usarse (aprobación puede tardar horas). Diseñar con antelación las plantillas de
  recordatorio de documentos, confirmación de cita, etc.
- **Rate limits** y **tier de mensajería** escalan según calidad del número y volumen;
  no es un problema para el volumen de un proyecto de portafolio pero hay que
  documentarlo como limitación conocida.
- **Pricing por conversación** (no por mensaje): conversaciones iniciadas por el
  usuario son gratis dentro de ciertos límites; las iniciadas por la empresa
  (templates) tienen costo. Relevante para el diseño de recordatorios automáticos.

## Pendiente de definir

- Proveedor de túnel para desarrollo local (`ngrok` vs `cloudflared`).
- Catálogo inicial de plantillas necesarias para el MVP.
