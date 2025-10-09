#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASSISTENTE PESSOAL - VERSÃO CORRIGIDA
Correções: Reconhecimento de verbos + Horários corretos + Lembretes
"""

import os
import sqlite3
import datetime
import time
import sys
import re

print("🤖 Iniciando Assistente Pessoal Aprimorado...")

# TOKEN - JÁ DEVE ESTAR CONFIGURADO!
BOT_TOKEN = "SEU_TOKEN_AQUI"  # ← Já substituído por você

if "SEU_TOKEN" in BOT_TOKEN:
    print("❌ ERRO: Token não configurado corretamente!")
    sys.exit(1)

print("✅ Token verificado! Carregando módulos...")

try:
    from telegram import Update
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
    print("✅ Módulos Telegram carregados com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar: {e}")
    sys.exit(1)

# =============================================
# BANCO DE DADOS APRIMORADO
# =============================================

class BancoDados:
    def __init__(self):
        self.conn = sqlite3.connect('assistente.db', check_same_thread=False)
        self.criar_tabelas()
    
    def criar_tabelas(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compromissos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                titulo TEXT,
                data TEXT,
                hora TEXT,
                tipo TEXT,
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lembretes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                chat_id INTEGER,
                mensagem TEXT,
                data_hora TEXT,
                enviado BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        print("✅ Banco de dados aprimorado pronto")
    
    def salvar_compromisso(self, user_id, titulo, data, hora, tipo="pessoal"):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO compromissos (user_id, titulo, data, hora, tipo) VALUES (?, ?, ?, ?, ?)",
                (user_id, titulo, data, hora, tipo)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao salvar compromisso: {e}")
            return False
    
    def salvar_lembrete(self, user_id, chat_id, mensagem, data_hora):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO lembretes (user_id, chat_id, mensagem, data_hora) VALUES (?, ?, ?, ?)",
                (user_id, chat_id, mensagem, data_hora)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao salvar lembrete: {e}")
            return False

    def buscar_compromissos_hoje(self, user_id):
        try:
            hoje = datetime.datetime.now().strftime('%d/%m/%Y')
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT titulo, hora FROM compromissos WHERE user_id = ? AND data = ? ORDER BY hora",
                (user_id, hoje)
            )
            return cursor.fetchall()
        except Exception:
            return []
    
    def buscar_lista_compras(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT item FROM listas_compras WHERE user_id = ? AND comprado = FALSE ORDER BY item",
                (user_id,)
            )
            return cursor.fetchall()
        except Exception:
            return []
    
    def salvar_item_lista(self, user_id, item):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM listas_compras WHERE user_id = ? AND item = ? AND comprado = FALSE", 
                          (user_id, item))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO listas_compras (user_id, item) VALUES (?, ?)",
                    (user_id, item)
                )
                self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao salvar item: {e}")
            return False
    
    def marcar_comprado(self, user_id, item):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE listas_compras SET comprado = TRUE WHERE user_id = ? AND item = ?",
                (user_id, item)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception:
            return False

# =============================================
# PROCESSADOR DE MENSAGENS APRIMORADO
# =============================================

class ProcessadorMensagens:
    def __init__(self):
        self.produtos = {
            'leite', 'pão', 'arroz', 'feijão', 'café', 'açúcar', 'óleo', 'sal',
            'carne', 'frango', 'peixe', 'ovos', 'queijo', 'manteiga', 'iogurte',
            'alface', 'tomate', 'cebola', 'batata', 'cenoura', 'frutas'
        }
        
        # VERBOS DE AÇÃO RECONHECIDOS
        self.verbos_acao = {
            'telefonar', 'ligar', 'call', 'chamar',
            'visitar', 'encontrar', 'ver', 'encontrar',
            'buscar', 'apanhar', 'pegar', 'levar',
            'comprar', 'ir ao', 'passar no',
            'marcar', 'agendar', 'marcação'
        }
    
    def extrair_data_hora(self, texto):
        """EXTRAI DATA E HORA CORRETAMENTE - CORRIGIDO"""
        hoje = datetime.datetime.now()
        data = hoje.strftime('%d/%m/%Y')
        hora = None  # Inicia como None para detectar se encontrou hora
        
        texto_lower = texto.lower()
        
        # DATAS - CORRIGIDO
        if 'amanhã' in texto_lower:
            data = (hoje + datetime.timedelta(days=1)).strftime('%d/%m/%Y')
        elif 'hoje' in texto_lower:
            data = hoje.strftime('%d/%m/%Y')
        
        # DIAS DA SEMANA
        dias_semana = {
            'segunda': 0, 'terça': 1, 'quarta': 2, 'quinta': 3,
            'sexta': 4, 'sábado': 5, 'domingo': 6
        }
        
        for dia, offset in dias_semana.items():
            if dia in texto_lower:
                dias_diferenca = (offset - hoje.weekday()) % 7
                data_alvo = hoje + datetime.timedelta(days=dias_diferenca)
                data = data_alvo.strftime('%d/%m/%Y')
                break
        
        # HORÁRIOS - CORREÇÃO PRINCIPAL
        # Padrão para 10h00, 10h, 10:00, etc.
        padrao_hora = r'(\d{1,2})[h: ]?(\d{0,2})'
        matches = re.findall(padrao_hora, texto)
        
        for match in matches:
            hora_str, minuto_str = match
            if hora_str and 0 <= int(hora_str) <= 23:
                hora = f"{int(hora_str):02d}:{minuto_str if minuto_str else '00'}"
                break
        
        # Se não encontrou hora específica, usa padrões de texto
        if not hora:
            horarios_texto = {
                '8h': '08:00', '9h': '09:00', '10h': '10:00', '11h': '11:00',
                '12h': '12:00', '13h': '13:00', '14h': '14:00', '15h': '15:00', 
                '16h': '16:00', '17h': '17:00', '18h': '18:00', '19h': '19:00',
                '20h': '20:00', '21h': '21:00', '22h': '22:00'
            }
            
            for h_text, h_valor in horarios_texto.items():
                if h_text in texto_lower:
                    hora = h_valor
                    break
        
        # SE NENHUMA HORA FOI ENCONTRADA, USA 09:00 COMO PADRÃO
        if not hora:
            hora = "09:00"
        
        return data, hora
    
    def extrair_titulo(self, texto):
        """EXTRAI TÍTULO MELHORADO - RECONHECE VERBOS"""
        texto_lower = texto.lower()
        
        # RECONHECIMENTO DE VERBOS DE AÇÃO - NOVO!
        for verbo in self.verbos_acao:
            if verbo in texto_lower:
                if 'telefonar' in texto_lower or 'ligar' in texto_lower:
                    return "Telefonar para contato"
                elif 'visitar' in texto_lower:
                    return "Visita"
                elif 'buscar' in texto_lower or 'apanhar' in texto_lower:
                    return "Buscar alguém"
                elif verbo in texto_lower:
                    return f"{verbo.title()}"  # Usa o verbo como título
        
        # TÍTULOS TRADICIONAIS
        if 'escola' in texto_lower or 'creche' in texto_lower:
            return "Buscar filhos na escola"
        elif 'reunião' in texto_lower:
            return "Reunião de trabalho"
        elif 'médico' in texto_lower or 'dentista' in texto_lower or 'consulta' in texto_lower:
            return "Consulta médica"
        elif 'supermercado' in texto_lower or 'mercado' in texto_lower:
            return "Supermercado"
        else:
            # Tenta extrair as primeiras palavras como título
            palavras = texto.split()[:4]
            return " ".join(palavras).title()
    
    def extrair_itens_compras(self, texto):
        texto_lower = texto.lower()
        itens = []
        
        for produto in self.produtos:
            if produto in texto_lower:
                itens.append(produto)
        
        return itens

# =============================================
# SISTEMA DE LEMBRETES - NOVO!
# =============================================

class SistemaLembretes:
    def __init__(self, updater, db):
        self.updater = updater
        self.db = db
        self.job_queue = updater.job_queue
    
    def agendar_lembrete(self, user_id, chat_id, titulo, data, hora):
        """Agenda lembrete para enviar notificação"""
        try:
            # Converter data e hora para datetime
            data_obj = datetime.datetime.strptime(data, '%d/%m/%Y')
            hora_obj = datetime.datetime.strptime(hora, '%H:%M').time()
            data_hora = datetime.datetime.combine(data_obj, hora_obj)
            
            # Agendar 15 minutos antes
            lembrete_time = data_hora - datetime.timedelta(minutes=15)
            
            # Se for para hoje/hora futura, agenda
            if lembrete_time > datetime.datetime.now():
                mensagem = f"⏰ LEMBRETE: {titulo} às {hora}"
                
                # Salvar no banco
                self.db.salvar_lembrete(user_id, chat_id, mensagem, data_hora.strftime('%Y-%m-%d %H:%M:%S'))
                
                # Agendar job
                self.job_queue.run_once(
                    self.enviar_lembrete,
                    lembrete_time,
                    context={'chat_id': chat_id, 'mensagem': mensagem}
                )
                return True
            return False
        except Exception as e:
            print(f"Erro ao agendar lembrete: {e}")
            return False
    
    def enviar_lembrete(self, context):
        """Envia o lembrete agendado"""
        try:
            job = context.job
            context.bot.send_message(
                chat_id=job.context['chat_id'],
                text=job.context['mensagem']
            )
            print(f"✅ Lembrete enviado: {job.context['mensagem']}")
        except Exception as e:
            print(f"❌ Erro ao enviar lembrete: {e}")

# =============================================
# ASSISTENTE PRINCIPAL APRIMORADO
# =============================================

db = BancoDados()
processador = ProcessadorMensagens()
sistema_lembretes = None  # Será inicializado depois

def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    
    mensagem = f"""
👋 **Olá {user.first_name}!**

Sou seu **Assistente Pessoal Aprimorado**! 🤖✨

🎯 **AGORA COM NOVAS FUNCIONALIDADES:**

📅 **AGENDA INTELIGENTE:**
• `Telefonar ao pai às 10h` ✅
• `Buscar filhos escola 17h` 
• `Reunião amanhã 14h`
• `Consulta médica segunda 10h`

⏰ **LEMBRETES AUTOMÁTICOS:**
• Recebe notificações antes dos compromissos
• Lembra você 15 minutos antes

🛒 **LISTA DE COMPRAS:**
• `Preciso de leite e pão`
• `Acabou o arroz e feijão`

💡 **Fale naturalmente em português!**

**Experimente as novas funcionalidades!** 🚀
    """
    
    update.message.reply_text(mensagem, parse_mode='Markdown')

def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    texto = update.message.text
    
    print(f"📨 Mensagem de {user_id}: {texto}")
    
    try:
        # AGENDA E COMPROMISSOS - APRIMORADO
        if any(palavra in texto.lower() for palavra in ['telefonar', 'ligar', 'visitar', 'buscar', 'marcar', 'agendar', 'reunião', 'compromisso']):
            data, hora = processador.extrair_data_hora(texto)
            titulo = processador.extrair_titulo(texto)
            
            if db.salvar_compromisso(user_id, titulo, data, hora):
                # TENTAR AGENDAR LEMBRETE - NOVO!
                if sistema_lembretes:
                    sistema_lembretes.agendar_lembrete(user_id, chat_id, titulo, data, hora)
                    mensagem_lembrete = "\n⏰ _Lembrete agendado! Você receberá uma notificação 15 minutos antes._"
                else:
                    mensagem_lembrete = ""
                
                resposta = f"""✅ **COMPROMISSO AGENDADO!**

📅 **{titulo}**
🗓️ **Data:** {data}
⏰ **Hora:** {hora}
{mensagem_lembrete}

💡 _Use 'Minha agenda' para ver todos_"""
            else:
                resposta = "❌ **Erro ao agendar compromisso.** Tente novamente."
        
        # LISTA DE COMPRAS
        elif any(palavra in texto.lower() for palavra in ['lista', 'compras', 'comprar', 'leite', 'pão', 'acabou', 'preciso de']):
            if 'minha lista' in texto.lower():
                itens = db.buscar_lista_compras(user_id)
                if itens:
                    resposta = "🛒 **SUA LISTA DE COMPRAS**\n\n"
                    for (item,) in itens:
                        resposta += f"• {item}\n"
                    resposta += f"\n📦 Total: {len(itens)} item(ns)"
                else:
                    resposta = "🛒 **SUA LISTA DE COMPRAS**\n\n🎉 *Lista vazia! Tudo em dia!*"
            
            else:
                itens = processador.extrair_itens_compras(texto)
                if itens:
                    for item in itens:
                        db.salvar_item_lista(user_id, item)
                    
                    itens_texto = "\n".join([f"• {item}" for item in itens])
                    resposta = f"""🛒 **ITENS ADICIONADOS!**

{itens_texto}

📋 _Use 'Minha lista' para ver todos os itens_"""
                else:
                    resposta = """❌ **Não identifiquei itens para adicionar.**

💡 **Tente assim:**
• `Preciso de leite e pão`
• `Acabou o arroz e feijão`"""
        
        # MARCAR ITENS COMPRADOS
        elif texto.lower().startswith('comprei '):
            item = texto.lower().replace('comprei ', '').strip()
            if db.marcar_comprado(user_id, item):
                resposta = f"✅ **{item.title()} marcado como COMPRADO!** 🎉\n\n_Item removido da lista._"
            else:
                resposta = f"❌ **{item.title()}** não encontrado na lista."
        
        # CONSULTAS
        elif any(palavra in texto.lower() for palavra in ['que tenho', 'minha agenda', 'ver agenda']):
            compromissos = db.buscar_compromissos_hoje(user_id)
            if compromissos:
                resposta = "📅 **SUA AGENDA DE HOJE**\n\n"
                for titulo, hora in compromissos:
                    resposta += f"• {titulo} - {hora}\n"
                resposta += f"\n📊 Total: {len(compromissos)} compromisso(s)"
            else:
                resposta = "📅 **SUA AGENDA DE HOJE**\n\n🎉 *Nenhum compromisso para hoje!*"
        
        # CUMprimentos
        elif any(palavra in texto.lower() for palavra in ['oi', 'olá']):
            resposta = "👋 Olá! Em que posso ajudar? Experimente: 'Telefonar ao pai às 10h' ou 'Preciso de leite'"
        
        else:
            resposta = """🤖 **Como posso ajudar?**

📅 **Agendar compromissos:**
`Telefonar ao pai às 10h` ✅
`Reunião amanhã 14h`
`Buscar filhos escola 17h`

🛒 **Lista de compras:**
`Preciso de leite e pão`

📊 **Consultar:**
`Minha agenda hoje`
`Minha lista`"""
        
        update.message.reply_text(resposta, parse_mode='Markdown')
        
    except Exception as e:
        print(f"❌ Erro ao processar mensagem: {e}")
        update.message.reply_text("❌ **Erro temporário.** Tente novamente.", parse_mode='Markdown')

def error_handler(update: Update, context: CallbackContext):
    print(f"⚠️ Erro: {context.error}")

def main():
    print("🎯 Iniciando bot Telegram Aprimorado...")
    
    try:
        # Criar updater
        updater = Updater(BOT_TOKEN, use_context=True)
        
        # Inicializar sistema de lembretes - NOVO!
        global sistema_lembretes
        sistema_lembretes = SistemaLembretes(updater, db)
        
        # Registrar handlers
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        dp.add_error_handler(error_handler)
        
        # Iniciar bot
        updater.start_polling()
        
        print("✅ Bot aprimorado iniciado com sucesso!")
        print("🤖 Aguardando mensagens no Telegram...")
        print("✨ Novas funcionalidades ativas:")
        print("   • Reconhecimento de verbos (telefonar, visitar, etc)")
        print("   • Horários extraídos corretamente") 
        print("   • Sistema de lembretes automáticos")
        
        # Manter rodando
        updater.idle()
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
