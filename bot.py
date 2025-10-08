import os
import logging
import sqlite3
import datetime
import sys

# ================= VERIFICAÇÃO DO AMBIENTE =================
print("🔍 Verificando ambiente...")

TOKEN = os.getenv("BOT_TOKEN")

# Debug
print("📋 Variáveis de ambiente:")
for key, value in os.environ.items():
    if 'BOT' in key or 'TOKEN' in key:
        print(f"   {key}: {value[:10]}...")

if not TOKEN:
    print("❌ ERRO: BOT_TOKEN não encontrado!")
    sys.exit(1)

print(f"✅ Token carregado! Iniciando...")

# ================= CONFIGURAÇÃO =================
logging.basicConfig(level=logging.INFO)

print("🔄 Iniciando assistente pessoal...")

class AssistentePessoal:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        """Inicializar banco de dados"""
        try:
            conn = sqlite3.connect('assistente.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compromissos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    titulo TEXT,
                    data TEXT,
                    hora TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS listas_compras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    item TEXT,
                    comprado BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Banco de dados pronto")
            
        except Exception as e:
            print(f"❌ Erro no banco: {e}")

    def processar_compromisso(self, user_id, texto):
        """Processar compromisso"""
        try:
            data = datetime.datetime.now().strftime('%d/%m/%Y')
            hora = "09:00"
            
            if 'amanhã' in texto.lower():
                data = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%d/%m/%Y')
            
            horarios = {
                '8h': '08:00', '9h': '09:00', '10h': '10:00', '11h': '11:00',
                '12h': '12:00', '13h': '13:00', '14h': '14:00', '15h': '15:00', 
                '16h': '16:00', '17h': '17:00', '18h': '18:00', '19h': '19:00'
            }
            
            for h_text, h_valor in horarios.items():
                if h_text in texto.lower():
                    hora = h_valor
                    break
            
            titulo = "Compromisso"
            if 'escola' in texto.lower():
                titulo = "Buscar filhos na escola"
            elif 'reunião' in texto.lower():
                titulo = "Reunião de trabalho"
            elif 'médico' in texto.lower():
                titulo = "Consulta médica"
            elif 'supermercado' in texto.lower():
                titulo = "Supermercado"
            
            conn = sqlite3.connect('assistente.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO compromissos (user_id, titulo, data, hora) VALUES (?, ?, ?, ?)",
                (user_id, titulo, data, hora)
            )
            conn.commit()
            conn.close()
            
            return True, titulo, data, hora
            
        except Exception as e:
            print(f"Erro ao processar compromisso: {e}")
            return False, None, None, None

    def processar_lista_compras(self, user_id, texto):
        """Processar lista de compras"""
        try:
            itens_reconhecidos = []
            produtos = {
                'leite', 'pão', 'arroz', 'feijão', 'café', 'açúcar', 'óleo',
                'carne', 'frango', 'peixe', 'ovos', 'queijo', 'manteiga',
                'alface', 'tomate', 'cebola', 'batata', 'cenoura', 'frutas'
            }
            
            for produto in produtos:
                if produto in texto.lower():
                    itens_reconhecidos.append(produto)
            
            conn = sqlite3.connect('assistente.db')
            cursor = conn.cursor()
            for item in itens_reconhecidos:
                cursor.execute(
                    "INSERT OR IGNORE INTO listas_compras (user_id, item) VALUES (?, ?)",
                    (user_id, item)
                )
            conn.commit()
            conn.close()
            
            return itens_reconhecidos
            
        except Exception as e:
            print(f"Erro ao processar lista: {e}")
            return []

    def obter_agenda_hoje(self, user_id):
        """Obter agenda de hoje"""
        try:
            hoje = datetime.datetime.now().strftime('%d/%m/%Y')
            conn = sqlite3.connect('assistente.db')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT titulo, hora FROM compromissos WHERE user_id = ? AND data = ? ORDER BY hora",
                (user_id, hoje)
            )
            compromissos = cursor.fetchall()
            conn.close()
            return compromissos
        except Exception as e:
            print(f"Erro ao obter agenda: {e}")
            return []

    def obter_lista_compras(self, user_id):
        """Obter lista de compras"""
        try:
            conn = sqlite3.connect('assistente.db')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT item FROM listas_compras WHERE user_id = ? AND comprado = FALSE ORDER BY item",
                (user_id,)
            )
            itens = cursor.fetchall()
            conn.close()
            return itens
        except Exception as e:
            print(f"Erro ao obter lista: {e}")
            return []

# Inicializar assistente
assistente = AssistentePessoal()

# AGORA importamos o telegram (depois de verificar o token)
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    print("✅ Módulos Telegram carregados com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar módulos Telegram: {e}")
    sys.exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    user = update.effective_user
    mensagem = f"""
👋 Olá {user.first_name}! 

Sou seu assistente pessoal! 🤖

📅 **AGENDA:**
• `Reunião amanhã 14h`
• `Buscar filhos escola 17h` 

🛒 **LISTA DE COMPRAS:**
• `Preciso de leite e pão`
• `Acabou o arroz e feijão`

📊 **CONSULTAS:**
• `Minha agenda hoje`
• `Minha lista de compras`
    """
    await update.message.reply_text(mensagem, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processar mensagens"""
    user_id = update.effective_user.id
    texto = update.message.text
    
    try:
        if any(palavra in texto.lower() for palavra in ['agenda', 'compromisso', 'reunião', 'marcar']):
            if 'minha agenda' in texto.lower():
                compromissos = assistente.obter_agenda_hoje(user_id)
                if compromissos:
                    resposta = "📅 **Sua agenda hoje:**\n\n"
                    for titulo, hora in compromissos:
                        resposta += f"• {titulo} - {hora}\n"
                else:
                    resposta = "📅 *Nenhum compromisso para hoje!*"
            else:
                sucesso, titulo, data, hora = assistente.processar_compromisso(user_id, texto)
                if sucesso:
                    resposta = f"✅ **Agendado!**\n\n**{titulo}**\n🗓️ {data} ⏰ {hora}"
                else:
                    resposta = "❌ Erro ao agendar."
        
        elif any(palavra in texto.lower() for palavra in ['lista', 'compras', 'comprar', 'leite', 'pão', 'acabou']):
            if 'minha lista' in texto.lower():
                itens = assistente.obter_lista_compras(user_id)
                if itens:
                    resposta = "🛒 **Sua lista de compras:**\n\n"
                    for (item,) in itens:
                        resposta += f"• {item}\n"
                else:
                    resposta = "🛒 *Lista de compras vazia!*"
            else:
                itens = assistente.processar_lista_compras(user_id, texto)
                if itens:
                    resposta = f"🛒 **Adicionado:**\n\n" + "\n".join([f"• {item}" for item in itens])
                else:
                    resposta = "❌ Não identifiquei itens. Tente: 'preciso de leite e pão'"
        
        elif any(palavra in texto.lower() for palavra in ['oi', 'olá']):
            resposta = "👋 Olá! Como posso ajudar?"
        
        else:
            resposta = "🤖 Diga: 'reunião amanhã 14h' ou 'preciso de leite'"
        
        await update.message.reply_text(resposta, parse_mode='Markdown')
        
    except Exception as e:
        print(f"Erro: {e}")
        await update.message.reply_text("❌ Erro temporário. Tente novamente.")

def main():
    """Função principal"""
    print("🚀 Iniciando Assistente Pessoal...")
    
    try:
        app = Application.builder().token(TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Bot iniciado com sucesso!")
        print("🤖 Aguardando mensagens...")
        
        app.run_polling()
        
    except Exception as e:
        print(f"❌ Erro ao iniciar bot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
