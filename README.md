# Kavak Commercial Agent 🚗🤖

Un agente comercial de IA desarrollado para simular el comportamiento de un asesor comercial de Kavak, la plataforma líder de autos usados en México.

## 🎯 Objetivo

Desarrollar un bot conversacional que se apoye en LLMs para proporcionar:
- Información sobre la propuesta de valor de Kavak
- Recomendaciones personalizadas de autos
- Cálculos de financiamiento
- Atención al cliente vía WhatsApp

## 🏗️ Arquitectura

### Diagrama de Alto Nivel

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WhatsApp      │    │   FastAPI       │    │   LangGraph     │
│   (Twilio)      │◄──►│   Gateway       │◄──►│   Agent         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Repository    │    │   OpenAI GPT    │
                       │   (CSV Data)    │    │   (gpt-4o)      │
                       └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Services      │    │   LangSmith     │
                       │ • Recommendations│    │   Observability │
                       │ • Financing     │    └─────────────────┘
                       │ • Search        │
                       └─────────────────┘
```

### Principios de Diseño

- **Arquitectura Limpia**: Separación clara entre domain, application, infrastructure y API
- **Principios SOLID**: 
  - Single Responsibility: Cada clase tiene una responsabilidad específica
  - Open/Closed: Extensible a través de interfaces
  - Liskov Substitution: Implementaciones intercambiables
  - Interface Segregation: Interfaces específicas y cohesivas  
  - Dependency Inversion: Dependencias sobre abstracciones

### Patrones Implementados

- **Repository Pattern**: Para acceso a datos del catálogo
- **Service Layer**: Para lógica de negocio
- **Dependency Injection**: Para desacoplar componentes
- **Strategy Pattern**: Para diferentes tipos de búsqueda
- **Observer Pattern**: Para logging y observabilidad

## 🚀 Capacidades del Agente

### ✅ Funcionalidades Implementadas

1. **Información de Kavak**
   - Propuesta de valor
   - Ubicaciones y servicios
   - Proceso de compra

2. **Recomendaciones Inteligentes**
   - Filtrado por preferencias del cliente
   - Algoritmo de scoring para ranking
   - Manejo de lenguaje natural

3. **Cálculo de Financiamiento**
   - Planes de 3-6 años
   - Tasa de interés del 10%
   - Múltiples opciones de enganche

4. **Búsqueda Avanzada**
   - Búsqueda por texto libre
   - Fuzzy matching para marcas/modelos
   - Normalización de consultas

5. **Integración WhatsApp**
   - Webhook para Twilio
   - Envío/recepción de mensajes
   - Validación de firmas

## 📁 Estructura del Proyecto

```
chat-bot/
├── src/
│   ├── domain/           # Modelos de dominio (DDD)
│   │   ├── __init__.py
│   │   └── models.py     # Car, CustomerPreferences, FinancingPlan
│   ├── application/      # Lógica de aplicación
│   │   ├── __init__.py
│   │   ├── services.py   # RecommendationService, FinancingService
│   │   └── agent.py      # KavakCommercialAgent (LangGraph)
│   ├── infrastructure/   # Infraestructura
│   │   ├── __init__.py
│   │   ├── repositories.py      # CarRepository (CSV)
│   │   ├── whatsapp.py          # Twilio integration
│   │   └── observability.py    # LangSmith integration
│   └── api/             # API REST
│       ├── __init__.py
│       └── main.py      # FastAPI endpoints
├── config/              # Configuración
│   ├── __init__.py
│   └── settings.py      # Settings con Pydantic
├── data/               # Datos
│   └── sample_caso_ai_engineer.csv
├── tests/              # Tests unitarios
├── docs/               # Documentación
├── requirements.txt    # Dependencias
├── .env               # Variables de entorno
├── main.py            # Punto de entrada
└── README.md          # Este archivo
```

## 🛠️ Instalación y Configuración

### Prerrequisitos

- Python 3.9+
- pip (gestor de paquetes de Python)

### Manual de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd chat-bot
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   
   El archivo `.env` ya está preconfigurado con valores por defecto. Para producción, modifica:
   
   ```bash
   # Twilio (para WhatsApp)
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_WHATSAPP_NUMBER=+14155238886
   
   # LangSmith (opcional)
   LANGSMITH_API_KEY=your_langsmith_key
   ```

5. **Ejecutar la aplicación**
   ```bash
   python main.py
   ```

6. **Acceder a la API**
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Chat Endpoint: http://localhost:8000/chat

## 🔧 Configuración de WhatsApp (Twilio)

### Sandbox de Twilio

1. **Crear cuenta en Twilio**
   - Registrarse en https://www.twilio.com
   - Obtener Account SID y Auth Token

2. **Configurar WhatsApp Sandbox**
   - Ir a Console > Develop > Messaging > Try it out > Send a WhatsApp message
   - Conectar tu número siguiendo las instrucciones
   - Usar el número sandbox: `+1 415 523 8886`

3. **Configurar Webhook**
   - URL del webhook: `https://your-domain.com/webhook/whatsapp`
   - Para desarrollo local, usar ngrok:
     ```bash
     ngrok http 8000
     ```

### Demo en Vivo

Para la demo, sigue estos pasos:

1. Configurar Twilio Sandbox
2. Ejecutar la aplicación
3. Configurar ngrok para exposición pública
4. Enviar mensaje a WhatsApp: "join <codigo-sandbox>"
5. Interactuar con el agente

## 📊 Diagrama de Agente/Tools

```
┌─────────────────────────────────────────────────────────────┐
│                    KavakCommercialAgent                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      LangGraph                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Agent     │  │    Tools    │  │    Model    │         │
│  │   Node      │◄─┤    Node     ├─►│  (GPT-4o)   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Tools                                  │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ get_car_        │  │ calculate_      │                  │
│  │ recommendations │  │ financing       │                  │
│  └─────────────────┘  └─────────────────┘                  │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ search_cars     │  │ get_kavak_info  │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Tests unitarios
pytest tests/

# Coverage
pytest --cov=src tests/
```

### Ejemplos de Uso

#### 1. Chat Básico
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "test_user",
       "message": "Hola, busco un auto económico"
     }'
```

#### 2. Búsqueda de Autos
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "test_user",
       "message": "Quiero un Toyota Corolla"
     }'
```

#### 3. Cálculo de Financiamiento
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "test_user",
       "message": "Calcula financiamiento para auto de $300,000 con enganche de $60,000 a 4 años"
     }'
```

## 🛣️ Roadmap para Producción

### Fase 1: Infraestructura Base (2-4 semanas)

**Prioridad Alta:**
- [ ] **Base de Datos Persistente**
  - Migrar de CSV a PostgreSQL/MongoDB
  - Implementar conexión pool y migrations
  - Agregar índices para búsquedas optimizadas

- [ ] **Autenticación y Autorización**
  - JWT tokens para API
  - Rate limiting por usuario
  - Validación de webhooks Twilio

- [ ] **Containerización**
  - Dockerfile para la aplicación
  - Docker Compose para desarrollo
  - Configuración para Kubernetes

**Prioridad Media:**
- [ ] **Cache Layer**
  - Redis para conversaciones activas
  - Cache de recomendaciones frecuentes
  - TTL configurables por tipo de dato

### Fase 2: Escalabilidad y Monitoreo (3-5 semanas)

**Prioridad Alta:**
- [ ] **Monitoreo y Observabilidad**
  - Métricas con Prometheus + Grafana
  - Logs centralizados (ELK Stack)
  - Alertas automáticas (PagerDuty)
  - Health checks robustos

- [ ] **Evaluación del Agente**
  - Métricas de calidad de respuestas
  - A/B testing de prompts
  - Feedback loop de usuarios
  - Datasets de evaluación automatizada

**Prioridad Media:**
- [ ] **Escalabilidad Horizontal**
  - Load balancer (Nginx/HAProxy)
  - Múltiples instancias de la API
  - Queue system para mensajes (RabbitMQ/Apache Kafka)

### Fase 3: Mejoras del Agente (4-6 semanas)

**Prioridad Alta:**
- [ ] **Prevención de Alucinaciones**
  - Validación de respuestas contra fuentes
  - Confidence scoring
  - Fallback a respuestas predefinidas
  - Fine-tuning con datos específicos de Kavak

- [ ] **Personalización Avanzada**
  - Historial de preferencias por usuario
  - Machine Learning para recomendaciones
  - Análisis de sentimientos
  - Segmentación de usuarios

**Prioridad Media:**
- [ ] **Multimodalidad**
  - Procesamiento de imágenes de autos
  - Mensajes de voz (WhatsApp)
  - Documentos y PDFs

### Fase 4: Integración Empresarial (2-3 semanas)

**Prioridad Alta:**
- [ ] **Integración con Sistemas Kavak**
  - CRM integration (HubSpot/Salesforce)
  - Inventory management system
  - Payment processing
  - Appointment scheduling

- [ ] **Compliance y Seguridad**
  - GDPR/LOPD compliance
  - Data encryption en reposo y tránsito
  - Audit logs
  - Backup y disaster recovery

## 🔍 Evaluación del Desempeño

### Métricas Técnicas

1. **Disponibilidad**
   - Uptime > 99.9%
   - Response time < 500ms (p95)
   - Error rate < 0.1%

2. **Calidad del Agente**
   - Accuracy de recomendaciones > 85%
   - Tasa de resolución en primer contacto > 70%
   - Customer satisfaction score > 4.2/5

3. **Observabilidad**
   - Logs estructurados con correlation IDs
   - Tracing distribuido con Jaeger
   - Métricas de negocio en tiempo real

### Herramientas de Evaluación

```python
# Ejemplo de evaluación automatizada
from langsmith import Client
from src.application.agent import KavakCommercialAgent

def evaluate_agent():
    dataset = client.list_examples(dataset_name="kavak-test-cases")
    
    for example in dataset:
        result = agent.process_message(
            user_id="test",
            message=example.inputs["message"]
        )
        
        # Evaluar calidad de respuesta
        score = evaluate_response_quality(
            expected=example.outputs["response"],
            actual=result["response"]
        )
        
        # Log resultado
        client.create_feedback(
            run_id=result["run_id"],
            score=score,
            value="accuracy"
        )
```

## 🔒 Testing de Regresión

### 1. Tests Automatizados

```python
# tests/test_agent_regression.py
import pytest
from src.application.agent import KavakCommercialAgent

class TestAgentRegression:
    """Suite de tests de regresión para el agente."""
    
    @pytest.mark.asyncio
    def test_car_recommendation_stability(self):
        """Verifica que las recomendaciones sean consistentes."""
        agent = KavakCommercialAgent(...)
        
        # Test con mismos inputs múltiples veces
        results = []
        for _ in range(5):
            result = agent.process_message(
                user_id="test",
                message="Busco un auto económico familiar"
            )
            results.append(result)
        
        # Verificar consistencia
        assert all(r["success"] for r in results)
        # Verificar que las recomendaciones sean similares
        assert similarity_score(results) > 0.8
    
    @pytest.mark.asyncio  
    def test_no_hallucination_regression(self):
        """Verifica que no haya alucinaciones en respuestas."""
        agent = KavakCommercialAgent(...)
        
        result = agent.process_message(
            user_id="test", 
            message="¿Venden autos Ferrari?"
        )
        
        # Verificar que no invente información
        assert "ferrari" not in result["response"].lower()
        assert "no tenemos" in result["response"].lower()
```

### 2. Pipeline de CI/CD

```yaml
# .github/workflows/regression.yml
name: Regression Tests

on:
  pull_request:
    branches: [main]
  
jobs:
  regression:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
        
    - name: Install dependencies
      run: pip install -r requirements.txt
      
    - name: Run regression tests
      run: |
        pytest tests/test_agent_regression.py -v
        pytest tests/test_api_regression.py -v
        
    - name: Performance baseline
      run: |
        python scripts/performance_baseline.py
        
    - name: Quality gates
      run: |
        python scripts/quality_gates.py
```

### 3. Monitoreo Continuo

```python
# scripts/quality_gates.py
def check_quality_gates():
    """Verificar gates de calidad antes de deploy."""
    
    # 1. Accuracy mínima
    accuracy = get_current_accuracy()
    assert accuracy > 0.85, f"Accuracy {accuracy} below threshold"
    
    # 2. Response time
    avg_response_time = get_avg_response_time()
    assert avg_response_time < 500, f"Response time {avg_response_time}ms too high"
    
    # 3. Error rate
    error_rate = get_error_rate()
    assert error_rate < 0.01, f"Error rate {error_rate} too high"
    
    print("✅ All quality gates passed")
```

## 🚀 Despliegue en Producción

### 1. Infraestructura

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    depends_on:
      - postgres
      - redis
      
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: kavak_agent
      
  redis:
    image: redis:alpine
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
```

### 2. Deployment Strategy

- **Blue-Green Deployment**: Para zero-downtime
- **Health Checks**: Verificación antes de switch
- **Rollback Automático**: Si falla health check
- **Gradual Traffic**: Canary deployment para nuevas versiones

## 📈 Métricas de Negocio

### KPIs Principales

1. **Conversión**: % de conversaciones que resultan en leads
2. **Engagement**: Tiempo promedio de conversación
3. **Satisfacción**: Rating de usuarios post-conversación
4. **Eficiencia**: Reducción de carga en agentes humanos

### Dashboard de Monitoreo

```python
# metrics/dashboard.py
def generate_business_metrics():
    return {
        "daily_conversations": get_conversation_count(),
        "conversion_rate": calculate_conversion_rate(),
        "avg_session_duration": get_avg_session_duration(),
        "user_satisfaction": get_satisfaction_score(),
        "top_car_requests": get_popular_car_requests(),
        "financing_calculations": get_financing_requests()
    }
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Equipo

- **Arquitectura**: Basada en Domain-Driven Design y Clean Architecture
- **AI/ML**: LangChain, LangGraph, OpenAI GPT-4o
- **Backend**: FastAPI, Pydantic, Python 3.9+
- **Integraciones**: Twilio WhatsApp, LangSmith
- **Observabilidad**: Structured logging, metrics, tracing

## 📞 Soporte

Para soporte técnico o preguntas sobre el proyecto:

- Email: tech-support@kavak.com
- Slack: #kavak-ai-agent
- Documentation: [Confluence Link]

---

**¡Transforma la experiencia de compra de autos con IA! 🚗✨**