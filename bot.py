import os
import logging
import sqlite3
import datetime
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ================= TOKEN VERIFICATION =================
print("🔍 Starting environment check...")

TOKEN = os.getenv("BOT_TOKEN")

# Debug: Show available environment variables
print("📋 Available environment variables:")
for key, value in os.environ.items():
    if 'BOT' in key or 'TOKEN' in key or 'TELEGRAM' in key:
        if key == 'BOT_TOKEN':
            print(f"   {key}: {value[:10]}...")  # Show only first 10 chars for security
        else:
            print(f"   {key}: {value}")

# Final verification
if not TOKEN:
    print("❌ CRITICAL ERROR: BOT_TOKEN not found!")
    print("\n💡 RENDER SOLUTION:")
    print("1. Go to 'Environment'")
    print("2. Click 'Add Environment Variable'")
    print("3. Key: BOT_TOKEN")
    print("4. Value: YOUR_BOTFATHER_TOKEN")
    print("5. Click 'Save Changes'")
    print("6. Redeploy")
    sys.exit(1)

print(f"✅ Token loaded! First 5 chars: {TOKEN[:5]}...")

# ================= CONFIGURATION =================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

print("🔄 Starting personal assistant system...")

class PersonalAssistant:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        """Initialize database"""
        try:
            conn = sqlite3.connect('assistente.db')
            cursor = conn.cursor()
            
            # Appointments table
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
            
            # Shopping list table
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
            print("✅ Database ready")
            
        except Exception as e:
            print(f"❌ Database error: {e}")

    def process_appointment(self, user_id, text):
        """Process and save appointment"""
        try:
            date = datetime.datetime.now().strftime('%d/%m/%Y')
            time = "09:00"
            
            # Detect dates
            if 'amanhã' in text.lower() or 'tomorrow' in text.lower():
                date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%d/%m/%Y')
            elif 'segunda' in text.lower() or 'monday' in text.lower():
                today = datetime.datetime.now()
                days_to_monday = (0 - today.weekday()) % 7
                date = (today + datetime.timedelta(days=days_to_monday)).strftime('%d/%m/%Y')
            
            # Detect times
            times = {
                '8h': '08:00', '9h': '09:00', '10h': '10:00', '11h': '11:00',
                '12h': '12:00', '13h': '13:00', '14h': '14:00', '15h': '15:00', 
                '16h': '16:00', '17h': '17:00', '18h': '18:00', '19h': '19:00',
                '8:00': '08:00', '9:00': '09:00', '10:00': '10:00', '11:00': '11:00',
                '14:00': '14:00', '15:00': '15:00', '16:00': '16:00', '17:00': '17:00'
            }
            
            for time_text, time_value in times.items():
                if time_text in text.lower():
                    time = time_value
                    break
            
            # Define title
            title = "Appointment"
            if 'escola' in text.lower() or 'school' in text.lower():
                title = "Pick up kids from school"
            elif 'reunião' in text.lower() or 'meeting' in text.lower():
                title = "Work meeting"
            elif 'médico' in text.lower() or 'doctor' in text.lower():
                title = "Medical appointment"
            elif 'supermercado' in text.lower() or 'market' in text.lower():
                title = "Grocery shopping"
            
            # Save to database
            conn = sqlite3.connect('assistente.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO compromissos (user_id, titulo, data, hora) VALUES (?, ?, ?, ?)",
                (user_id, title, date, time)
            )
            conn.commit()
            conn.close()
            
            return True, title, date, time
            
        except Exception as e:
            print(f"Error processing appointment: {e}")
            return False, None, None, None

    def process_shopping_list(self, user_id, text):
        """Process and save shopping items"""
        try:
            recognized_items = []
            products = {
                'leite', 'pão', 'arroz', 'feijão', 'café', 'açúcar', 'óleo',
                'carne', 'frango', 'peixe', 'ovos', 'queijo', 'manteiga',
                'alface', 'tomate', 'cebola', 'batata', 'cenoura', 'frutas',
                'milk', 'bread', 'rice', 'eggs', 'cheese', 'fruits', 'vegetables'
            }
            
            for product in products:
                if product in text.lower():
                    recognized_items.append(product)
            
            # Save to database
            conn = sqlite3.connect('assistente.db')
            cursor = conn.cursor()
            for item in recognized_items:
                cursor.execute(
                    "INSERT OR IGNORE INTO listas_compras (user_id, item) VALUES (?, ?)",
                    (user_id, item)
                )
            conn.commit()
            conn.close()
            
            return recognized_items
            
        except Exception as e:
            print(f"Error processing list: {e}")
            return []

    def get_today_agenda(self, user_id):
        """Get today's appointments"""
        try:
            today = datetime.datetime.now().strftime('%d/%m/%Y')
            conn = sqlite3.connect('assistente.db')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT titulo, hora FROM compromissos WHERE user_id = ? AND data = ? ORDER BY hora",
                (user_id, today)
            )
            appointments = cursor.fetchall()
            conn.close()
            return appointments
        except Exception as e:
            print(f"Error getting agenda: {e}")
            return []

    def get_shopping_list(self, user_id):
        """Get shopping list"""
        try:
            conn = sqlite3.connect('assistente.db')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT item FROM listas_compras WHERE user_id = ? AND comprado = FALSE ORDER BY item",
                (user_id,)
            )
            items = cursor.fetchall()
            conn.close()
            return items
        except Exception as e:
            print(f"Error getting list: {e}")
            return []

# Initialize assistant
assistant = PersonalAssistant()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    message = f"""
👋 Hello {user.first_name}! 

I'm your personal assistant! 🤖

📅 **APPOINTMENTS:**
• `Meeting tomorrow 14h`
• `Pick up kids school 17h` 

🛒 **SHOPPING LIST:**
• `Need milk and bread`
• `Out of rice and beans`

📊 **QUERIES:**
• `My agenda today`
• `My shopping list`

Try now! ✨
    """
    await update.message.reply_text(message, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process messages"""
    user_id = update.effective_user.id
    text = update.message.text
    
    try:
        # APPOINTMENTS
        if any(word in text.lower() for word in ['agenda', 'compromisso', 'reunião', 'marcar', 'appointment', 'meeting']):
            if 'minha agenda' in text.lower() or 'my agenda' in text.lower():
                appointments = assistant.get_today_agenda(user_id)
                if appointments:
                    response = "📅 **Your agenda today:**\n\n"
                    for title, time in appointments:
                        response += f"• {title} - {time}\n"
                else:
                    response = "📅 *No appointments for today!*"
            else:
                success, title, date, time = assistant.process_appointment(user_id, text)
                if success:
                    response = f"✅ **Scheduled!**\n\n**{title}**\n🗓️ {date} ⏰ {time}"
                else:
                    response = "❌ Error scheduling. Try again."
        
        # SHOPPING LIST
        elif any(word in text.lower() for word in ['lista', 'compras', 'comprar', 'leite', 'pão', 'acabou', 'list', 'shopping', 'milk', 'bread']):
            if 'minha lista' in text.lower() or 'my list' in text.lower():
                items = assistant.get_shopping_list(user_id)
                if items:
                    response = "🛒 **Your shopping list:**\n\n"
                    for (item,) in items:
                        response += f"• {item}\n"
                else:
                    response = "🛒 *Shopping list empty!*"
            else:
                items = assistant.process_shopping_list(user_id, text)
                if items:
                    response = f"🛒 **Added to list:**\n\n" + "\n".join([f"• {item}" for item in items])
                else:
                    response = "❌ No items identified. Try: 'need milk and bread'"
        
        # GREETINGS
        elif any(word in text.lower() for word in ['oi', 'olá', 'hello', 'hi']):
            response = "👋 Hello! How can I help with your agenda or shopping list?"
        
        # HELP
        else:
            response = """
🤖 **How can I help?**

📅 **Appointments:**
`Meeting tomorrow 14h`
`Pick up kids school 17h`

🛒 **Shopping:**
`Need milk, bread and eggs`
`Out of rice and beans`

📊 **Queries:**
`My agenda today`
`My shopping list`
            """
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("❌ Temporary error. Try again.")

def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    print(f"Update {update} caused error {context.error}")

def main():
    """Main function"""
    print("🚀 Starting Personal Assistant...")
    
    try:
        # Create Application
        application = Application.builder().token(TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Start the Bot
        print("✅ Bot starting polling...")
        application.run_polling()
        
        print("✅ Bot started successfully!")
        print("🤖 Waiting for messages...")
        
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        # More detailed error information
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
