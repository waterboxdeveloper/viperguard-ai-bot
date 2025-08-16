# 🐍 ViperGuard AI

**AI-Powered Telegram Moderator for Python Communities**

---

## 🎯 **¿Qué es este bot?**

**ViperGuard AI** es un **bot moderador automático** que utiliza **Inteligencia Artificial** para mantener un ambiente sano y productivo en grupos de Telegram de comunidades Python.

El bot analiza cada mensaje enviado al grupo en tiempo real y toma decisiones inteligentes sobre si debe:
- ✅ **Aprobar** el mensaje (la mayoría de casos)
- ⚠️ **Advertir** al usuario con mensaje privado
- 🗑️ **Eliminar** contenido inapropiado
- ⏰ **Silenciar** temporalmente a usuarios problemáticos
- 🔨 **Banear** en casos extremos

---

## 🧠 **Inteligencia Artificial**

El bot utiliza **Google Gemini 1.5 Flash** para analizar el contexto y contenido de cada mensaje, tomando decisiones basadas en:

### **🟢 Contenido Permitido:**
- Preguntas técnicas sobre Python y programación
- Discusiones sobre tecnología, frameworks, herramientas
- Conversaciones casuales entre miembros de la comunidad
- Información sobre eventos, meetups, conferencias
- Memes y humor relacionado con programación
- Ofertas de trabajo relacionadas con tecnología
- Presentaciones personales y networking

### **🔴 Contenido Bloqueado:**
- Insultos, ataques personales, lenguaje ofensivo
- Spam comercial repetitivo
- Contenido sexual, violento o discriminatorio
- Estafas, esquemas piramidales, MLM
- Promoción excesiva de criptomonedas/trading
- Links sospechosos o malware
- Contenido sobre JavaScript (con cariño 😄)
- Temas de política partidista, drogas, armas

---

## 🏗️ **Stack Tecnológico**

### **Lenguaje y Framework:**
- **Python 3.11+** - Lenguaje principal
- **Asyncio** - Programación asíncrona para máximo rendimiento

### **Inteligencia Artificial:**
- **Google Gemini 1.5 Flash** - Motor de IA para análisis de contenido
- **LangChain** - Framework para integración con LLMs
- **Structured Outputs** - Respuestas JSON tipadas y validadas

### **Bot de Telegram:**
- **python-telegram-bot v20+** - Librería asíncrona para Telegram
- **Webhook/Polling** - Recepción de mensajes en tiempo real

### **Gestión de Configuración:**
- **Pydantic Settings v2** - Configuración tipada y validada
- **Variables de entorno** - Manejo seguro de credenciales

### **Gestión de Dependencias:**
- **UV** - Gestor de paquetes ultra-rápido
- **Python Packaging** - Estructura moderna de proyecto

---

## ⚙️ **Características Técnicas**

### **🚀 Rendimiento:**
- **Análisis en tiempo real** - Cada mensaje procesado instantáneamente
- **Respuesta rápida** - ~1 segundo promedio por mensaje
- **Arquitectura asíncrona** - Manejo eficiente de múltiples mensajes

### **🛡️ Seguridad:**
- **Manejo seguro de tokens** - Variables de entorno
- **Validación de entrada** - Pydantic para todos los datos
- **Logging de auditoría** - Registro completo de todas las decisiones
- **Fallback inteligente** - Si falla la IA, aprueba por seguridad

### **📊 Observabilidad:**
- **Logging estructurado** - Registros detallados en JSON
- **Métricas de confianza** - Cada decisión incluye nivel de certeza
- **Tiempo de procesamiento** - Monitoreo de performance
- **Auditoría completa** - Rastreabilidad de todas las acciones

---

## 📁 **Estructura del Proyecto**

```
📁 viperguard-ai-bot/
├── 🚀 main.py                     # Punto de entrada principal
├── 📋 README.md                   # Documentación del proyecto
├── ⚙️ pyproject.toml              # Configuración y dependencias
├── 🔒 uv.lock                     # Lock de dependencias
├── 🛡️ .gitignore                 # Archivos ignorados por Git
├── 🐍 .python-version             # Versión de Python requerida
└── 📁 src/
    ├── ⚙️ settings.py             # Configuración global
    └── 📁 bot/
        ├── 📁 handlers/           # Handlers de Telegram (vacía)
        ├── 📁 moderator/
        │   └── 🧠 ai_analyzer.py  # Cerebro de IA (Gemini + LangChain)
        └── 📁 services/
            └── 🤖 telegram_client.py # Cliente de Telegram asíncrono
```

### **Componentes Principales:**

- **`ai_analyzer.py`** - Moderador con IA que analiza mensajes usando Gemini
- **`telegram_client.py`** - Cliente que maneja la comunicación con Telegram
- **`settings.py`** - Configuración centralizada y validada
- **`main.py`** - Punto de entrada para ejecutar el bot

---

## 🚀 **Instalación y Uso**

### **Prerrequisitos:**
- Python 3.11+
- Token de bot de Telegram (obtenido de @BotFather)
- API Key de Google Gemini

### **Instalación:**

```bash
# Clonar el repositorio
git clone https://github.com/waterboxdeveloper/viperguard-ai-bot.git
cd viperguard-ai-bot

# Instalar dependencias con UV
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus tokens
```

### **Configuración (.env):**

```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
GOOGLE_API_KEY=tu_api_key_aqui
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### **Ejecución:**

```bash
# Ejecutar el bot
uv run python main.py
```

---

## 📊 **Métricas y Monitoreo**

El bot genera logs detallados que incluyen:

- **Mensajes analizados** por minuto/hora/día
- **Acciones tomadas** (approve, warn, delete, ban, timeout)
- **Nivel de confianza** promedio de las decisiones
- **Tiempo de respuesta** de la IA
- **Errores y excepciones** para debugging

Ejemplo de log:
```
2025-08-16 12:52:25,523 - INFO - ✅ Análisis completado: approve (0.99)
Mensaje: "me gustaría comenzar en Python, ¿qué me recomiendan?"
Razón: "Pregunta válida sobre aprendizaje de Python"
Tiempo: 0.65s
```

---

## 🤝 **Contribuciones**

Este bot está diseñado para ser:
- **Configurable** - Fácil ajustar reglas y umbrales
- **Extensible** - Agregar nuevas funcionalidades
- **Mantenible** - Código limpio y documentado
- **Testeable** - Componentes independientes

---

## 👨‍💻 **Autor**

**Eduardo Guzmán**

**ViperGuard AI** es una **iniciativa personal** de Eduardo Guzmán, quien está explorando el desarrollo de **soluciones innovadoras con Inteligencia Artificial**. Como parte de su investigación en el campo de la IA aplicada, Eduardo decidió crear este bot moderador para **probarlo en un ambiente real** con comunidades Python, contribuyendo al mismo tiempo con una herramienta útil para los grupos.

El proyecto representa una exploración práctica de:
- Integración de LLMs en aplicaciones reales
- Procesamiento de lenguaje natural para moderación
- Arquitecturas asíncronas con Python
- Desarrollo de bots inteligentes para comunidades

---

## 📄 **Licencia**

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

## 🔗 **Enlaces**

- **Grupo Python CDMX**: [Enlace al grupo de Telegram]
- **Documentación Técnica**: [docs/](./docs/)
- **Reportar Issues**: [GitHub Issues]

---

**¡Gracias por usar ViperGuard AI! 🐍🤖**

*Desarrollado con ❤️ para las comunidades Python de todo el mundo*
