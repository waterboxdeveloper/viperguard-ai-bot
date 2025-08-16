"""
🤖 CLIENTE DE TELEGRAM - EL CORAZÓN DEL BOT

Este archivo es el INTERMEDIARIO entre Telegram y nuestro bot. Su trabajo es:

1. 📱 CONECTAR con los servidores de Telegram
2. 👂 ESCUCHAR mensajes y comandos del grupo
3. 🧠 COORDINAR con ai_analyzer.py para moderar mensajes
4. ⚡ EJECUTAR acciones (eliminar, advertir, banear)
5. 🔄 MANTENER el bot funcionando 24/7

COMPONENTES PRINCIPALES:
- TelegramBot: La clase principal que maneja todo
- _handle_start(): Responde al comando /start
- _handle_message(): Procesa TODOS los mensajes del grupo (CRÍTICO)
- start(): Inicia el bot y lo mantiene corriendo
- stop(): Detiene el bot elegantemente

FLUJO DE TRABAJO:
Telegram → _handle_message() → ai_analyzer.py → acción → Telegram

CONEXIÓN CON OTROS ARCHIVOS:
- settings.py: Para obtener el token del bot
- ai_analyzer.py: Para analizar mensajes ✅ CONECTADO
"""

import asyncio
import logging
from typing import Optional, Dict, Any

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import telegram

from ...settings import settings
#--------------------------------
# Configurar logging basado en settings

# Configurar logging de manera robusta
def get_log_level(level_str: str) -> int:
    """Convierte string de nivel a constante de logging"""
    try:
        return getattr(logging, str(level_str).upper())
    except AttributeError:
        # Si el nivel no existe, usar INFO por defecto
        return logging.INFO

log_level = get_log_level(settings.log_level)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=log_level
)
logger = logging.getLogger(__name__)

# Log inicial
logger.info("🤖 Inicializando Bot Moderador Python CDMX")
logger.info(f"📊 Configuración: {settings.environment}")
logger.info(f"🔧 Nivel de log: {settings.log_level}")
#--------------------------------

class TelegramBot:
    """
    🤖 CLASE PRINCIPAL DEL BOT DE TELEGRAM
    
    Esta clase es el NÚCLEO de todo el bot. Es quien:
    
    RESPONSABILIDADES PRINCIPALES:
    1. 🔌 Se conecta con los servidores de Telegram
    2. 📋 Registra handlers para diferentes tipos de eventos
    3. 👂 Escucha mensajes y comandos 24/7
    4. 🧠 Coordina con ai_analyzer.py para moderación ✅
    5. ⚡ Ejecuta acciones de moderación
    6. 📊 Registra todo en logs para debugging
    
    MÉTODOS PRINCIPALES:
    - initialize(): Configura la conexión con Telegram
    - _register_handlers(): Define qué hacer con cada tipo de mensaje
    - _handle_start(): Responde al comando /start
    - _handle_message(): CRÍTICO - procesa mensajes del grupo
    - start(): Inicia el bot y lo mantiene corriendo
    - stop(): Detiene el bot limpiamente
    
    ESTADO ACTUAL:
    ✅ Conecta con Telegram
    ✅ Responde a /start
    ✅ Recibe todos los mensajes
    ✅ IA conectada y moderando automáticamente
    """
    
    def __init__(self):
        """Inicializa el bot con configuración desde settings"""
        self.settings = settings
        self.application: Optional[Application] = None
        
        logger.info("🏗️ Inicializando TelegramBot")
        # Arreglar el problema del token
        token_preview = str(self.settings.telegram_bot_token)[:10] if self.settings.telegram_bot_token else "None"
        logger.debug(f"📋 Token configurado: {token_preview}...")
        
    async def initialize(self) -> None:
        """Inicializa la aplicación de Telegram"""
        try:
            logger.info("🔧 Creando aplicación de Telegram...")
            
            # Crear aplicación
            self.application = Application.builder().token(
                self.settings.telegram_bot_token
            ).build()
            
            logger.info("✅ Aplicación de Telegram creada exitosamente")
            
            # Registrar handlers
            await self._register_handlers()
            
            logger.info("✅ Handlers registrados exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error al inicializar aplicación: {e}")
            raise

    async def _register_handlers(self) -> None:
        """Registra todos los handlers del bot"""
        logger.info("📋 Registrando handlers...")
        
        # Handler para el comando /start
        self.application.add_handler(
            CommandHandler("start", self._handle_start)
        )
        
        # Handler para todos los mensajes de texto
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
        )
        
        logger.info("📋 Handlers registrados: /start, mensajes de texto")

    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Maneja el comando /start"""
        logger.info(f"🚀 Comando /start recibido de usuario: {update.effective_user.id}")
        
        welcome_message = (
            "¡Hola! 👋 Soy el bot moderador de Python CDMX.\n\n"
            "Estoy aquí para ayudar a mantener un ambiente amigable en el grupo.\n"
            "¡Escribe algo para probar que funciono! 🤖"
        )
        
        await update.message.reply_text(welcome_message)
        logger.info("✅ Mensaje de bienvenida enviado")

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        🎯 FUNCIÓN MÁS IMPORTANTE DEL BOT
        
        Esta función se ejecuta CADA VEZ que alguien envía un mensaje al grupo.
        Es aquí donde ocurre toda la magia de la moderación.
        
        PROCESO ACTUAL (BÁSICO):
        1. 📨 Recibe el mensaje de Telegram
        2. 📊 Extrae información (texto, usuario)
        3. 📝 Lo registra en logs
        4. ✅ Responde confirmación (temporal)
        
        PROCESO ACTUAL (CON IA ✅):
        1. 📨 Recibe el mensaje
        2. 🤖 Lo envía a ai_analyzer.py
        3. 📊 Recibe decisión de la IA
        4. ⚡ Ejecuta acción (eliminar, advertir, etc.)
        5. 📝 Registra resultado
        
        PARÁMETROS:
        - update: Información completa del mensaje de Telegram
        - context: Contexto del bot (para responder, eliminar, etc.)
        
        🚀 CONEXIÓN CON IA ACTIVADA:
        """
        # Extraer información del mensaje
        message_text = update.message.text
        user_id = update.effective_user.id
        
        logger.info(f"📥 Mensaje recibido de usuario {user_id}: {message_text[:50]}...")
        
        # 🤖 CONECTAR CON LA IA PARA MODERACIÓN
        try:
            # Importar la función de análisis
            from ..moderator.ai_analyzer import analyze_message, ModerationAction
            
            # Analizar el mensaje con IA
            logger.info("🧠 Enviando mensaje a la IA para análisis...")
            result = await analyze_message(message_text, user_id)
            
            logger.info(f"🎯 Decisión de IA: {result.action.value} (confianza: {result.confidence:.2f})")
            logger.info(f"📝 Razón: {result.reason}")
            
            # 🚀 EJECUTAR ACCIÓN SEGÚN LA DECISIÓN DE LA IA
            if result.action == ModerationAction.DELETE:
                # Eliminar mensaje
                await update.message.delete()
                logger.warning(f"🗑️ Mensaje eliminado de usuario {user_id}: {result.reason}")
                
                # Enviar advertencia privada (opcional)
                if self.settings.warn_before_delete:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"⚠️ Tu mensaje fue eliminado del grupo Python CDMX.\n\n"
                             f"Razón: {result.reason}\n\n"
                             f"Por favor, asegúrate de seguir las reglas del grupo."
                    )
                    
            elif result.action == ModerationAction.WARN:
                # Enviar advertencia privada
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"⚠️ Advertencia del grupo Python CDMX.\n\n"
                         f"Razón: {result.reason}\n\n"
                         f"Tu mensaje está en el límite de las reglas. "
                         f"Por favor, ten cuidado con futuros mensajes."
                )
                logger.warning(f"⚠️ Advertencia enviada a usuario {user_id}: {result.reason}")
                
            elif result.action == ModerationAction.BAN:
                # Banear usuario (casos extremos)
                await context.bot.ban_chat_member(
                    chat_id=update.effective_chat.id,
                    user_id=user_id
                )
                await update.message.delete()
                logger.error(f"🔨 Usuario {user_id} baneado: {result.reason}")
                
            elif result.action == ModerationAction.TIMEOUT:
                # Silenciar usuario temporalmente (5 minutos)
                import datetime
                until_date = datetime.datetime.now() + datetime.timedelta(minutes=5)
                await context.bot.restrict_chat_member(
                    chat_id=update.effective_chat.id,
                    user_id=user_id,
                    permissions=telegram.ChatPermissions(can_send_messages=False),
                    until_date=until_date
                )
                logger.warning(f"⏰ Usuario {user_id} silenciado 5 min: {result.reason}")
                
            elif result.action == ModerationAction.APPROVE:
                # Mensaje aprobado - no hacer nada
                logger.info(f"✅ Mensaje aprobado: {result.reason}")
                
        except Exception as e:
            # Si hay error con la IA, aprobar por seguridad
            logger.error(f"❌ Error en moderación con IA: {e}")
            logger.info("🛡️ Aprobando mensaje por seguridad ante error de IA")
        
        logger.info("✅ Mensaje procesado exitosamente")

    async def start(self) -> None:
        """
        🚀 INICIA EL BOT Y LO MANTIENE FUNCIONANDO 24/7
        
        Esta función es la que "enciende" el bot y lo deja corriendo.
        Una vez que se ejecuta, el bot estará escuchando mensajes constantemente.
        
        PROCESO:
        1. 🔧 Inicializa la conexión con Telegram
        2. 📋 Registra todos los handlers
        3. 🔄 Inicia el "polling" (escuchar mensajes)
        4. ⏳ Se queda corriendo hasta recibir Ctrl+C
        5. 🛑 Al detener, limpia todo elegantemente
        
        POLLING vs WEBHOOKS:
        - Polling = El bot pregunta a Telegram "¿hay mensajes nuevos?"
        - Webhooks = Telegram envía mensajes directamente al bot
        - Usamos polling para desarrollo (más simple)
        - En producción usaremos webhooks (más eficiente)
        """
        try:
            logger.info("🚀 Iniciando bot...")
            
            # Inicializar la aplicación
            await self.initialize()
            
            # AGREGAR: Inicializar la aplicación de Telegram
            await self.application.initialize()
            
            # Iniciar polling
            logger.info("🔄 Iniciando polling...")
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("✅ Bot iniciado exitosamente - Presiona Ctrl+C para detener")
            
            # Mantener el bot ejecutándose
            import signal
            stop_event = asyncio.Event()
            
            def signal_handler(signum, frame):
                logger.info("🛑 Señal de parada recibida")
                stop_event.set()
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # Esperar hasta que se reciba la señal de parada
            await stop_event.wait()
            
        except Exception as e:
            logger.error(f"❌ Error al iniciar bot: {e}")
            raise
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Detiene el bot"""
        if self.application:
            logger.info("🛑 Deteniendo bot...")
            # Verificar que el updater esté corriendo antes de detenerlo
            if self.application.updater.running:
                await self.application.updater.stop()
            await self.application.stop()
            # AGREGAR: Limpiar recursos
            await self.application.shutdown()
            logger.info("✅ Bot detenido")

# Instancia global del bot
bot = TelegramBot()

# Función para ejecutar el bot
async def run_bot():
    """Ejecuta el bot"""
    await bot.start()

if __name__ == "__main__":
    asyncio.run(run_bot())