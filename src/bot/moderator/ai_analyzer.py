"""
🛡️ MODERADOR CON INTELIGENCIA ARTIFICIAL

Este es el 'CEREBRO' del bot moderador. Su trabajo es:

1. 📨 Recibir mensajes del grupo de Telegram
2. 🤖 Analizarlos con Google Gemini (IA)
3. 🎯 Decidir qué acción tomar (aprobar, advertir, eliminar, etc.)
4. 📊 Devolver el resultado con explicación y nivel de confianza

COMPONENTES PRINCIPALES:
- ModerationAction: Las 5 acciones posibles (APPROVE, WARN, DELETE, BAN, TIMEOUT)
- ModerationResult: El resultado completo del análisis
- ContentModerator: La clase principal que hace todo el trabajo
- analyze_message(): Función simple para usar desde otros archivos

FLUJO DE TRABAJO:
mensaje → Gemini API → análisis → decisión → acción
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

# Configuración local
from ...settings import settings

class ModerationAction(Enum):
    """
    🎯 LAS 5 ACCIONES POSIBLES DEL MODERADOR
    
    Estas son todas las decisiones que puede tomar la IA:
    
    APPROVE  = Mensaje está bien, no hacer nada
    WARN     = Enviar advertencia privada al usuario
    DELETE   = Eliminar el mensaje del grupo
    BAN      = Banear al usuario permanentemente
    TIMEOUT  = Silenciar al usuario por un tiempo
    
    La IA elige una de estas basándose en qué tan grave considera el mensaje.
    """
    APPROVE = "approve"      # ✅ Mensaje aprobado - no hacer nada
    WARN = "warn"           # ⚠️ Advertencia al usuario - mensaje privado
    DELETE = "delete"       # 🗑️ Eliminar mensaje - borrar del grupo
    BAN = "ban"             # 🔨 Banear usuario - expulsar permanentemente
    TIMEOUT = "timeout"     # ⏰ Timeout temporal - silenciar por X tiempo

@dataclass
class ModerationResult:
    """
    📊 RESULTADO COMPLETO DEL ANÁLISIS DE IA
    
    Esto es lo que devuelve la IA después de analizar un mensaje.
    Contiene toda la información necesaria para tomar una decisión.
    
    Campos:
    - action: Qué hacer (APPROVE, WARN, DELETE, BAN, TIMEOUT)
    - reason: Por qué la IA tomó esa decisión (explicación humana)
    - confidence: Qué tan segura está la IA (0.0 = insegura, 1.0 = muy segura)
    - message_analyzed: El mensaje original que se analizó
    - timestamp: Cuándo se hizo el análisis
    - processing_time: Cuántos segundos tardó en analizarlo
    
    Ejemplo de uso:
    if result.action == ModerationAction.DELETE and result.confidence > 0.8:
        await message.delete()  # Solo eliminar si está muy segura
    """
    action: ModerationAction    # Qué acción tomar
    reason: str                 # Por qué se tomó esa decisión
    confidence: float          # Nivel de confianza (0.0 a 1.0)
    message_analyzed: str      # El mensaje original
    timestamp: datetime        # Cuándo se analizó
    processing_time: float     # Segundos que tardó 

# Configurar logging específico para moderación
logger = logging.getLogger(__name__)

# Configurar formato de logging más detallado para moderación
def setup_moderation_logging():
    """Configura logging específico para moderación"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [MODERADOR] %(message)s'
    )
    
    # Handler para archivo de moderación
    file_handler = logging.FileHandler('moderation.log')
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    # Arreglar el problema del FieldInfo
    logger.setLevel(getattr(logging, str(settings.log_level).upper()))

# Inicializar logging
setup_moderation_logging()

class ContentModerator:
    """
    🧠 CEREBRO PRINCIPAL DEL BOT MODERADOR
    
    Esta clase es el componente más importante. Es quien hace todo el trabajo:
    
    RESPONSABILIDADES:
    1. 🔌 Conectarse con Google Gemini (IA)
    2. 📝 Configurar las reglas de moderación (prompt)
    3. 📨 Recibir mensajes para analizar
    4. 🤖 Enviar mensajes a la IA para análisis
    5. 📊 Procesar la respuesta de la IA
    6. ✅ Devolver el resultado final
    
    MÉTODOS PRINCIPALES:
    - initialize(): Conecta con Gemini y configura el prompt
    - analyze_message(): Analiza un mensaje específico (LA MÁS IMPORTANTE)
    
    FLUJO INTERNO:
    mensaje → prompt + IA → respuesta JSON → ModerationResult
    """
    
    def __init__(self):
        """Inicializa el moderador con configuración desde settings"""
        self.settings = settings
        self.llm: Optional[ChatGoogleGenerativeAI] = None
        self.prompt_template: Optional[ChatPromptTemplate] = None
        
        logger.info("🛡️ Inicializando ContentModerator")
        logger.info(f"📊 Modelo: {self.settings.ai_model}")
        logger.info(f"🔧 Moderación habilitada: {self.settings.moderation_enabled}") 

    async def initialize(self) -> None:
        """
        Inicializa la conexión con Gemini y configura las chains.
        """
        try:
            logger.info("🔧 Inicializando conexión con Gemini...")
            
            # Inicializar ChatGoogleGenerativeAI con LangChain
            self.llm = ChatGoogleGenerativeAI(
                model=self.settings.ai_model,
                google_api_key=self.settings.google_api_key,
                temperature=self.settings.ai_temperature,
                max_output_tokens=self.settings.ai_max_tokens,
                max_retries=3,  # Valor por defecto
                timeout=30      # Valor por defecto
            )
            
            # Configurar el prompt template para moderación
            await self._setup_moderation_prompt()
            
            logger.info("✅ Gemini inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error al inicializar Gemini: {e}")
            raise 

    async def _setup_moderation_prompt(self) -> None:
        """
        🧠 CONFIGURACIÓN DEL PROMPT - EL ALMA DEL MODERADOR
        
        Esto es SÚPER IMPORTANTE de entender:
        
        El "prompt" es como las INSTRUCCIONES que le damos a la IA.
        Es como contratar a un moderador humano y explicarle:
        - Cuál es su trabajo
        - Qué reglas debe seguir  
        - Cómo debe responder
        
        Si cambias este prompt, cambias completamente el comportamiento del bot.
        """
        
        # 📋 INSTRUCCIONES PARA LA IA (esto es lo que "lee" Gemini)
        system_prompt = """
        Eres un moderador experto para el grupo de Python CDMX en Telegram.
        Tu trabajo es mantener un ambiente sano y respetuoso, pero SIN ser restrictivo con conversaciones normales de una comunidad técnica.
        
        🟢 COMPLETAMENTE PERMITIDO (SIEMPRE APPROVE):
        - Preguntas técnicas sobre Python, programación, desarrollo
        - Discusiones sobre tecnología, frameworks, herramientas
        - Compartir recursos, tutoriales, artículos técnicos
        - Ayuda con código, debugging, errores
        - Ofertas de trabajo relacionadas con programación
        - Conversaciones casuales entre miembros de la comunidad
        - Información sobre eventos, meetups, conferencias
        - Presentaciones personales ("Hola, soy nuevo")
        - Agradecimientos, felicitaciones, celebraciones
        - Memes y humor relacionado con programación (incluso si mencionan otros lenguajes)
        - Discusiones sobre otros lenguajes de programación (R, Java, etc.)
        - Preguntas sobre carrera profesional en tech
        - Compartir proyectos personales (sin spam excesivo)
        
        🔴 PROHIBIDO (DELETE/WARN/BAN según gravedad):
        - Insultos directos, ataques personales, lenguaje ofensivo
        - Contenido sexual explícito, pornografía
        - Drogas ilegales, armas, contenido violento
        - Política partidista, debates políticos divisivos
        - Estafas, esquemas piramidales, MLM obvios
        - Spam comercial repetitivo (más de 2 veces el mismo producto)
        - Links sospechosos, malware, phishing
        - Contenido racista, discriminatorio, hate speech
        - Promoción  de criptomonedas/trading 
        - Doxxing, información personal de otros sin permiso
        -Javascript
        -Hacking
        
        ⚠️ CRITERIO PARA ACCIONES:
        - APPROVE: 95% de los casos (sé muy permisivo)
        - WARN: Solo para contenido borderline o primera ofensa menor
        - DELETE: Para spam claro, contenido inapropiado obvio
        - TIMEOUT: Para usuarios que insisten después de advertencia
        - BAN: Solo para casos extremos (spam masivo, contenido muy ofensivo)
        
        IMPORTANTE: 
        - SÉ MUY PERMISIVO con conversaciones normales
        - Solo actúa contra contenido claramente problemático
        - La comunidad debe sentirse libre de conversar
        - Responde SOLO con un JSON válido:
        
        {{
            "action": "APPROVE|WARN|DELETE|BAN|TIMEOUT",
            "reason": "Explicación breve y clara en español",
            "confidence": 0.95
        }}
        """
        
        # 🔗 CREAR EL TEMPLATE DE CONVERSACIÓN
        # Esto combina las instrucciones del sistema con el mensaje del usuario
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),  # Las instrucciones para la IA
            ("human", "Analiza este mensaje:\n\n{message}")  # El mensaje a analizar
        ]) 

    async def analyze_message(self, message: str, user_id: Optional[int] = None) -> ModerationResult:
        """
        🎯 FUNCIÓN MÁS IMPORTANTE DEL BOT
        
        Esta función hace TODO el trabajo de moderación:
        
        PROCESO PASO A PASO:
        1. 📥 Recibe el mensaje de texto
        2. ⏱️ Inicia el cronómetro para medir velocidad
        3. 🔍 Verifica que todo esté inicializado
        4. 🤖 Crea la "chain" (prompt + IA) usando LangChain
        5. 📤 Envía el mensaje a Gemini para análisis
        6. 📥 Recibe la respuesta JSON de Gemini
        7. 🔧 Parsea y valida la respuesta
        8. ✅ Devuelve el resultado completo
        9. ❌ Si hay error, devuelve APPROVE por seguridad
        
        Args:
            message (str): El texto del mensaje a analizar
            user_id (Optional[int]): ID del usuario (para logs)
        
        Returns:
            ModerationResult: Decisión completa con acción, razón y confianza
            
        Ejemplo:
            result = await analyze_message("¿Cómo instalar Django?")
            # result.action = APPROVE
            # result.reason = "Pregunta técnica apropiada"
            # result.confidence = 0.95
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"🔍 Analizando mensaje de usuario {user_id}")
            logger.debug(f"📝 Mensaje: {message[:100]}...")
            
            # Verificar que el moderador esté inicializado
            if not self.llm or not self.prompt_template:
                raise ValueError("Moderador no inicializado. Llama a initialize() primero.")
            
            # Crear la chain: prompt + LLM
            moderation_chain = self.prompt_template | self.llm
            
            # Ejecutar la chain
            logger.debug("🤖 Enviando mensaje a Gemini...")
            response = await moderation_chain.ainvoke({
                "message": message
            })
            
            logger.debug(f"📨 Respuesta de Gemini: {response.content}")
            
            # Parsear la respuesta JSON
            result = await self._parse_moderation_response(
                response.content, 
                message, 
                start_time
            )
            
            logger.info(f"✅ Análisis completado: {result.action.value} ({result.confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en análisis: {e}")
            # Devolver resultado de error
            return ModerationResult(
                action=ModerationAction.APPROVE,  # En caso de error, aprobar
                reason=f"Error en análisis: {str(e)}",
                confidence=0.0,
                message_analyzed=message,
                timestamp=datetime.now(),
                processing_time=asyncio.get_event_loop().time() - start_time
            )

    async def _parse_moderation_response(
        self, 
        response_content: str, 
        original_message: str, 
        start_time: float
    ) -> ModerationResult:
        """
        Parsea la respuesta JSON de Gemini y la convierte en ModerationResult.
        """
        import json
        
        try:
            # Limpiar la respuesta (a veces Gemini agrega texto extra)
            response_content = response_content.strip()
            
            # Buscar JSON en la respuesta
            start_idx = response_content.find('{')
            end_idx = response_content.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No se encontró JSON válido en la respuesta")
            
            json_str = response_content[start_idx:end_idx]
            parsed_response = json.loads(json_str)
            
            # Validar campos requeridos
            action_str = parsed_response.get('action', '').upper()
            reason = parsed_response.get('reason', 'Sin razón especificada')
            confidence = float(parsed_response.get('confidence', 0.5))
            
            # Convertir string a enum
            try:
                action = ModerationAction(action_str.lower())
            except ValueError:
                logger.warning(f"⚠️ Acción desconocida: {action_str}, usando APPROVE")
                action = ModerationAction.APPROVE
            
            # Crear resultado
            result = ModerationResult(
                action=action,
                reason=reason,
                confidence=min(max(confidence, 0.0), 1.0),  # Clamp entre 0 y 1
                message_analyzed=original_message,
                timestamp=datetime.now(),
                processing_time=asyncio.get_event_loop().time() - start_time
            )
            
            logger.debug(f"📊 Resultado parseado: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error parseando respuesta: {e}")
            # Respuesta de fallback
            return ModerationResult(
                action=ModerationAction.APPROVE,
                reason=f"Error parseando respuesta: {str(e)}",
                confidence=0.0,
                message_analyzed=original_message,
                timestamp=datetime.now(),
                processing_time=asyncio.get_event_loop().time() - start_time
            ) 



# =============================================================================
# INSTANCIA GLOBAL Y FUNCIÓN DE CONVENIENCIA
# =============================================================================

# Instancia global del moderador (patrón singleton)
# Esto permite reutilizar la misma instancia en toda la aplicación
# sin tener que inicializar múltiples veces la conexión con Gemini
moderator = ContentModerator()

async def analyze_message(message: str, user_id: Optional[int] = None) -> ModerationResult:
    """
    🎯 FUNCIÓN PRINCIPAL PARA USAR DESDE OTROS MÓDULOS
    
    Esta es la función que llamarás desde telegram_client.py para moderar mensajes.
    
    Args:
        message (str): El texto del mensaje a analizar
        user_id (Optional[int]): ID del usuario que envió el mensaje (para logs)
    
    Returns:
        ModerationResult: Resultado completo del análisis con:
            - action: APPROVE, WARN, DELETE, BAN, o TIMEOUT
            - reason: Explicación de por qué se tomó esa decisión
            - confidence: Nivel de confianza (0.0 a 1.0)
            - message_analyzed: El mensaje original
            - timestamp: Cuándo se hizo el análisis
            - processing_time: Cuánto tardó en procesarse
    
    Ejemplo de uso:
        from .moderator.ai_analyzer import analyze_message
        
        result = await analyze_message("¿Cómo instalar Django?", user_id=12345)
        
        if result.action == ModerationAction.DELETE:
            await message.delete()
        elif result.action == ModerationAction.WARN:
            await context.bot.send_message(chat_id=user_id, text="⚠️ Advertencia...")
    """
    # Si el moderador no está inicializado, lo inicializamos automáticamente
    if not moderator.llm:
        logger.info("🔧 Inicializando moderador automáticamente...")
        await moderator.initialize()
    
    # Llamar al método de análisis de la instancia global
    return await moderator.analyze_message(message, user_id) 