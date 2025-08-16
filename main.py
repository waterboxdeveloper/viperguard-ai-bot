"""
🚀 PUNTO DE ENTRADA PRINCIPAL DEL BOT MODERADOR

Este archivo es el que ejecutas para iniciar tu bot moderador completo.

COMANDO PARA EJECUTAR:
    uv run python main.py

LO QUE HACE:
1. 📁 Configura el path para importar desde src/
2. 🤖 Importa el bot de Telegram con IA conectada
3. 🔄 Ejecuta el bot y lo mantiene corriendo 24/7
4. 🛑 Maneja interrupciones elegantemente (Ctrl+C)

FLUJO COMPLETO:
main.py → telegram_client.py → ai_analyzer.py → Gemini → acciones
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.bot.services.telegram_client import bot, run_bot

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
