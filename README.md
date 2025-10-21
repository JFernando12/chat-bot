# 🤖 Kavak AI Sales Agent

Bot inteligente de ventas integrado con WhatsApp usando LangChain, LangGraph y FastAPI.

## 📋 Características

- 🎯 Clasificación inteligente de intenciones del usuario
- 📦 Agente de catálogo para consulta de productos
- 💰 Agente financiero para cotizaciones y financiamiento
- 💬 Agente general para preguntas comunes
- 📱 Integración con WhatsApp vía Twilio
- 🚀 API REST con FastAPI
- 🐳 Dockerizado para fácil despliegue

## 🏗️ Arquitectura

```
WhatsApp (Twilio) → FastAPI → Services → Agents (LangGraph) → LLM (OpenAI)
```

### Componentes

- **Routers**: Endpoints HTTP (chat, whatsapp)
- **Services**: Lógica de negocio y orquestación
- **Agents**: Agentes especializados con LangGraph
- **Domain**: Modelos de datos y estado

## 🚀 Inicio Rápido con Docker

### Prerrequisitos

- Docker y Docker Compose instalados
- Cuenta de OpenAI con API key
- Cuenta de Twilio (para WhatsApp)

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/JFernando12/chat-bot.git
cd chat-bot
```

2. **Configurar variables de entorno**
```bash
cp .env.example .env
```

Editar `.env` y agregar tus credenciales:
```env
OPENAI_API_KEY=sk-your-key-here
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

3. **Construir y ejecutar con Docker Compose**
```bash
docker-compose up --build
```

4. **La aplicación estará disponible en:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

## 🛠️ Desarrollo Local (sin Docker)

### Prerrequisitos

- Python 3.11+
- pip

### Instalación

1. **Crear entorno virtual**
```bash
python -m venv venv
```

2. **Activar entorno virtual**

Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

Linux/Mac:
```bash
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

5. **Ejecutar la aplicación**
```bash
python -m src.main
```

## 📱 Configuración de WhatsApp con Twilio

### Paso 1: Crear cuenta en Twilio

1. Ir a [Twilio.com](https://www.twilio.com/)
2. Crear cuenta gratuita
3. Verificar email y teléfono

### Paso 2: Activar WhatsApp Sandbox

1. En el dashboard de Twilio, ir a **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Seguir las instrucciones para unirse al sandbox
3. Enviar el código desde tu WhatsApp al número de Twilio

### Paso 3: Configurar Webhook

Para desarrollo local, necesitas exponer tu servidor:

1. **Instalar ngrok**
```bash
# Windows (con Chocolatey)
choco install ngrok

# O descargar desde https://ngrok.com/download
```

2. **Exponer tu servidor local**
```bash
ngrok http 8000
```

3. **Copiar la URL HTTPS generada** (ej: https://abc123.ngrok.io)

4. **Configurar en Twilio**:
   - Ir a **Messaging** → **Settings** → **WhatsApp Sandbox Settings**
   - En "When a message comes in", pegar: `https://tu-url-ngrok.ngrok.io/api/whatsapp/webhook`
   - Guardar

### Paso 4: Probar

Envía un mensaje de WhatsApp al número del sandbox y el bot responderá.

## 🔧 Comandos Docker Útiles

```bash
# Construir la imagen
docker-compose build

# Ejecutar en modo detached
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down

# Reconstruir y ejecutar
docker-compose up --build

# Ejecutar comandos dentro del contenedor
docker-compose exec chatbot bash
```

## 📊 API Endpoints

### Chat
```bash
POST /api/chat
Body: {"user_id": "123", "message": "Hola"}
```

### WhatsApp Webhook
```bash
POST /api/whatsapp/webhook
# Recibe mensajes de Twilio
```

### Health Check
```bash
GET /api/health
```

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=src tests/
```

## 📁 Estructura del Proyecto

```
chat-bot/
├── src/
│   ├── api/
│   │   ├── routers/         # Endpoints HTTP
│   │   └── fastapi_app.py   # Aplicación FastAPI
│   ├── application/
│   │   ├── agents/          # Agentes LangGraph
│   │   └── services/        # Lógica de negocio
│   ├── config/              # Configuración
│   ├── domain/              # Modelos de dominio
│   └── main.py              # Entry point
├── data/
│   └── sample_caso_ai_engineer.csv
├── tests/                   # Tests unitarios
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## 🔐 Seguridad

- ✅ Usuario no-root en Docker
- ✅ Variables de entorno para secretos
- ⚠️ Implementar validación de firma de Twilio en producción
- ⚠️ Agregar rate limiting

## 📈 Monitoreo

El contenedor incluye health checks para monitoreo:

```bash
# Verificar health manualmente
curl http://localhost:8000/api/health
```

## 🚀 Despliegue a Producción

Ver documento `docs/roadmap.md` para plan detallado de producción.

### Checklist rápido:
- [ ] Configurar variables de entorno en servidor
- [ ] Usar base de datos persistente
- [ ] Implementar logging centralizado
- [ ] Configurar CI/CD
- [ ] Agregar monitoring (Prometheus/Grafana)
- [ ] Implementar rate limiting
- [ ] SSL/HTTPS obligatorio
- [ ] Backups automáticos

## 🤝 Contribuir

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto está bajo la licencia MIT.

## 👥 Autor

JFernando12

## 📞 Soporte

Para preguntas o soporte, crear un issue en GitHub.
