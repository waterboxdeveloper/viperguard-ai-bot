"""
⚙️ CONFIGURACIÓN GLOBAL DEL BOT MODERADOR

Este archivo es el CENTRO DE CONTROL de todo el bot. Aquí se define:

1. 🔑 Tokens y API keys (Telegram, Gemini)
2. 🤖 Configuración de la IA (modelo, temperatura, etc.)
3. 🛡️ Reglas de moderación (cuándo banear, advertir, etc.)
4. 🌍 Configuración del entorno (desarrollo, producción)
5. 📊 Límites y umbrales de moderación

CÓMO FUNCIONA:
- Lee automáticamente el archivo .env
- Valida que todos los valores sean correctos
- Proporciona valores por defecto inteligentes
- Permite cambiar configuración sin tocar código

ARCHIVOS QUE LO USAN:
- ai_analyzer.py: Para configurar Gemini
- telegram_client.py: Para token del bot
- Cualquier parte que necesite configuración
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field
from typing import Optional, List
import os
from pathlib import Path

class Settings(BaseSettings):
    """
    🎛️ CONFIGURACIÓN PRINCIPAL DEL BOT MODERADOR
    
    Esta clase maneja TODA la configuración del bot usando Pydantic Settings v2.
    
    CARACTERÍSTICAS PRINCIPALES:
    - 📁 Carga automática desde archivo .env
    - ✅ Validación automática de tipos y valores
    - 🔧 Valores por defecto inteligentes
    - 🧮 Campos calculados dinámicamente
    - 🛡️ Validación de seguridad
    
    CÓMO USAR:
    from settings import settings
    token = settings.telegram_bot_token
    model = settings.ai_model
    """
    
    # ===================================================================
    # 🤖 CONFIGURACIÓN DE TELEGRAM
    # ===================================================================
    
    telegram_bot_token: str = Field(
        ...,  # Campo requerido (debe estar en .env)
        description="🔑 Token del bot obtenido de @BotFather en Telegram"
        # Ejemplo en .env: TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
    )
    
    telegram_chat_id: Optional[str] = Field(
        default=None,
        description="📱 ID del grupo donde operará el bot (opcional para desarrollo)"
        # Ejemplo en .env: TELEGRAM_CHAT_ID=-1001234567890
    )
    
    # ===================================================================
    # 🧠 CONFIGURACIÓN DE GOOGLE GEMINI (INTELIGENCIA ARTIFICIAL)
    # ===================================================================
    
    google_api_key: str = Field(
        ...,  # Campo requerido
        description="🔑 API key de Google AI para acceder a Gemini"
        # Obtener en: https://makersuite.google.com/
        # Ejemplo en .env: GOOGLE_API_KEY=AIzaSyA1f8ETWihOGjTmmNGEZhB2X0HzXuEDqM0
    )
    
    # ===================================================================
    # 🤖 CONFIGURACIÓN DEL MODELO DE IA
    # ===================================================================
    
    ai_model: str = Field(
        default="gemini-1.5-flash",
        description="🧠 Modelo de IA a utilizar para moderación"
        
    )
    
    ai_temperature: float = Field(
        default=0.3,  # Muy bajo = respuestas consistentes
        ge=0.0,       # Mínimo 0.0
        le=1.0,       # Máximo 1.0
        description="🌡️ Creatividad del modelo (0.0=determinístico, 1.0=creativo)"
        # 0.1 = Respuestas muy consistentes (recomendado para moderación)
        # 0.5 = Balance entre consistencia y variedad
        # 1.0 = Máxima creatividad (no recomendado para moderación)
    )
    
    ai_max_tokens: int = Field(
        default=1000,  # Suficiente para respuestas de moderación
        gt=0,          # Debe ser mayor a 0
        le=8192,       # Límite máximo de Gemini
        description="📝 Máximo número de tokens (palabras) en la respuesta"
        # 1000 tokens ≈ 750 palabras (perfecto para moderación)
    )
    
    # === ENVIRONMENT CONFIGURATION ===
    environment: str = Field(
        default="development",
        pattern=r"^(development|staging|production)$",
        description="Entorno de ejecución (development, staging, production)"
    )
    
    log_level: str = Field(
        default="DEBUG",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    # ===================================================================
    # 🛡️ CONFIGURACIÓN DE MODERACIÓN 
    # ===================================================================
    
    moderation_enabled: bool = Field(
        default=True,
        description="🔄 Activar/desactivar la moderación automática"
        # True = El bot modera automáticamente
        # False = Solo observa, no toma acciones (modo desarrollo)
    )
    
    delete_spam_messages: bool = Field(
        default=True,
        description="🗑️ Eliminar mensajes identificados como spam"
        # True = Elimina spam automáticamente
        # False = Solo marca como spam en logs
    )
    
    warn_before_delete: bool = Field(
        default=True,
        description="⚠️ Enviar advertencia privada antes de eliminar mensaje"
        # True = Envía mensaje privado explicando por qué se eliminó
        # False = Elimina silenciosamente
    )
    
    max_warnings: int = Field(
        default=3,        # Después de 3 advertencias = ban
        gt=0,            # Mínimo 1 advertencia
        le=10,           # Máximo 10 advertencias
        description="📊 Número máximo de advertencias antes de ban automático"
        # 3 = Valor equilibrado (recomendado)
        # 1 = Muy estricto (ban inmediato)
        # 5+ = Muy permisivo
    )
    
    # === ADMIN CONFIGURATION ===
    admin_user_ids: Optional[str] = Field(
        default=None,
        description="IDs de usuarios administradores (separados por comas)"
    )
    
    # === RATE LIMITING ===
    rate_limit_enabled: bool = Field(
        default=True,
        description="Activar limitación de tasa de mensajes"
    )
    
    max_messages_per_minute: int = Field(
        default=10,
        gt=0,
        le=60,
        description="Máximo número de mensajes por minuto por usuario"
    )
    
    # === CONTENT FILTERING ===
    filter_spam: bool = Field(
        default=True,
        description="Filtrar mensajes de spam"
    )
    
    filter_nsfw: bool = Field(
        default=True,
        description="Filtrar contenido NSFW"
    )
    
    filter_off_topic: bool = Field(
        default=True,
        description="Filtrar mensajes fuera de tema"
    )
    
    # ===================================================================
    # 🧮 CAMPOS CALCULADOS AUTOMÁTICAMENTE (Pydantic v2)
    # ===================================================================
    # Estos campos se calculan automáticamente basándose en otros campos
    # No necesitas configurarlos en .env - se generan solos
    
    @computed_field
    @property
    def admin_ids_list(self) -> List[int]:
        """
        📋 Convierte la cadena de admin_user_ids en lista de enteros
        
        Si tienes en .env: ADMIN_USER_IDS=123456,789012,345678
        Este método devuelve: [123456, 789012, 345678]
        
        Uso: settings.admin_ids_list para obtener lista de admins
        """
        if not self.admin_user_ids:
            return []
        try:
            return [int(uid.strip()) for uid in self.admin_user_ids.split(",")]
        except (ValueError, AttributeError):
            return []
    
    @computed_field
    @property
    def is_development(self) -> bool:
        """
        🔧 Verifica si estamos en entorno de desarrollo
        
        True = Modo desarrollo (logs detallados, sin restricciones)
        False = Modo producción o staging
        """
        return str(self.environment).lower() == "development"
    
    @computed_field
    @property
    def is_production(self) -> bool:
        """
        🚀 Verifica si estamos en entorno de producción
        
        True = Modo producción (logs mínimos, máxima seguridad)
        False = Modo desarrollo o staging
        """
        return str(self.environment).lower() == "production"
    
    @computed_field
    @property
    def is_staging(self) -> bool:
        """
        🧪 Verifica si estamos en entorno de staging (pruebas)
        
        True = Modo staging (testing antes de producción)
        False = Modo desarrollo o producción
        """
        return str(self.environment).lower() == "staging"
    
    # ===================================================================
    # 🔗 COMPATIBILIDAD CON LANGCHAIN 
    # ===================================================================
    
    @computed_field
    @property
    def langchain_gemini_config(self) -> dict:
        """
        🤖 Configuración completa para LangChain ChatGoogleGenerativeAI
        
        Este método es CRÍTICO - convierte nuestra configuración en el formato
        que necesita LangChain para conectarse con Gemini.
        
        ai_analyzer.py usa esto directamente para inicializar el modelo:
        
        self.llm = ChatGoogleGenerativeAI(**settings.langchain_gemini_config)
        
        Returns:
            dict: Configuración lista para usar con LangChain
        """
        return {
            "google_api_key": str(self.google_api_key),        # API key de Google
            "model": str(self.ai_model),                       # gemini-1.5-flash
            "temperature": float(self.ai_temperature),         # 0.1 (consistente)
            "max_output_tokens": int(self.ai_max_tokens),      # 1000 tokens máximo
            "max_retries": 3,                                  # Reintentos si falla
            "timeout": 30,                                     # 30 segundos timeout
        }
    
    # === HELPER METHODS ===
    def get_admin_list(self) -> List[int]:
        """Método alternativo para obtener lista de admins"""
        return self.admin_ids_list
    
    def is_admin(self, user_id: int) -> bool:
        """Verifica si un usuario es administrador"""
        return user_id in self.admin_ids_list
    
    def get_log_config(self) -> dict:
        """Configuración para logging"""
        return {
            "level": self.log_level,
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            "diagnose": self.is_development,
            "backtrace": self.is_development,
        }
    
    def get_moderation_config(self) -> dict:
        """Configuración para el módulo de moderación"""
        return {
            "enabled": self.moderation_enabled,
            "delete_spam": self.delete_spam_messages,
            "warn_before_delete": self.warn_before_delete,
            "max_warnings": self.max_warnings,
            "rate_limit": {
                "enabled": self.rate_limit_enabled,
                "max_per_minute": self.max_messages_per_minute,
            },
            "filters": {
                "spam": self.filter_spam,
                "nsfw": self.filter_nsfw,
                "off_topic": self.filter_off_topic,
            }
        }
    
    # === VALIDATION METHODS ===
    def validate_tokens(self) -> bool:
        """Valida que los tokens estén configurados correctamente"""
        return bool(self.telegram_bot_token and self.google_api_key)
    
    def get_env_info(self) -> dict:
        """Información del entorno actual"""
        return {
            "environment": self.environment,
            "is_development": self.is_development,
            "is_production": self.is_production,
            "is_staging": self.is_staging,
            "log_level": self.log_level,
            "moderation_enabled": self.moderation_enabled,
            "admin_count": len(self.admin_ids_list),
        }
    
    # Configuración moderna de Pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
        # Configuración adicional para estabilidad
        str_strip_whitespace=True,
        validate_assignment=True,
        # Prefijo para variables de entorno
        env_prefix="",
    )

# Instancia global de configuración
settings = Settings()

# Test para verificar que funciona
if __name__ == "__main__":
    print("🔧 Testing settings...")
    try:
        print(f"✅ AI Model: {settings.ai_model}")
        print(f"✅ Environment: {settings.environment}")
        print(f"✅ Moderation: {settings.moderation_enabled}")
        print(f"✅ Admin IDs: {settings.admin_ids_list}")
        print(f"✅ Is Development: {settings.is_development}")
        print(f"✅ LangChain Config: {settings.langchain_gemini_config}")
        print(f"✅ Tokens Valid: {settings.validate_tokens()}")
        print(f"✅ Env Info: {settings.get_env_info()}")
        print(f"✅ Settings loaded successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()



