#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASSISTENTE PESSOAL - VERSÃO PRÁTICA E FUNCIONAL
Foca no que realmente importa: entender frases reais em português
"""

import os
import sqlite3
import datetime
import re
import sys

print("🤖 Iniciando Assistente Prático...")

BOT_TOKEN = "SEU_TOKEN_AQUI"

if "SEU_TOKEN" in BOT_TOKEN:
    print("❌ Configure o token!")
    sys.exit(1)

try:
    from telegram import Update
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
    print("✅ Módulos carregados")
except ImportError as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

# =============================================
# PROCESSADOR PRÁTICO - FOCO NO QUE FUNCIONA
# =============================================

class ProcessadorPortugues:
    def __init__(self):
        # VERBOS QUE IMPORTAM
        self.acoes = {
            'telefonar': 'Telefonar para',
            'ligar': 'Telefonar para', 
            'chamar': 'Telefonar para',
            'visitar': 'Visitar',
            'encontrar': 'Encontrar com',
            'buscar': 'Buscar',
            'levar': 'Levar',
            'reunir': 'Reunião com'
        }
        
        # PESSOAS COMUNS
        self.pessoas = {
            'pai', 'mãe', 'avô', 'avó', 'filho', 'filha',
            'marido', 'esposa', 'mulher', 'amigo', 'amiga', 
            'colega', 'chefe', 'cliente', 'médico', 'doutor'
        }
        
        # LOCAIS COMUNS
        self.locais = {
            'hospital', 'escola', 'trabalho', 'casa', 'escritório',
            'consultório', 'supermercado', 'mercado', 'farmácia'
        }

    def extrair_titulo_inteligente(self, texto):
        """Extrai título de forma PRÁTICA e FUNCIONAL"""
        texto_lower = texto.lower()
        
        # DETECTA AÇÃO PRINCIPAL
        acao_encontrada = None
        for acao in self.acoes:
            if acao in texto_lower:
                acao_encontrada = acao
                break
        
        # DETECTA PESSOA
        pessoa_encontrada = None
        for pessoa in self.pessoas:
            if pessoa in texto_lower:
                pessoa_encontrada = pessoa
                break
        
        # DETECTA LOCAL
        local_encontrado = None
        for local in self.locais:
            if local in texto_lower:
                local_encontrado = local
                break
        
        # CONSTRÓI TÍTULO INTELIGENTE
        if acao_encontrada and pessoa_encontrada and local_encontrado:
            return f"{self.acoes[acao_encontrada]} {pessoa_encontrada} no {local_encontrado}"
        elif acao_encontrada and pessoa_encontrada:
            return f"{self.acoes[acao_encontrada]} {pessoa_encontrada}"
        elif acao_encontrada and local_encontrado:
            return f"{self.acoes[acao_encontrada]} no {local_encontrado}"
        elif acao_encontrada:
            return f"{self.acoes[acao_encontrada]}"
        else:
            return "Compromisso"

    def extrair_data_hora_funcional(self, texto):
        """Extrai data e hora de forma CONFIÁVEL"""
        hoje = datetime.datetime.now()
        data = hoje.strftime('%d/%m/%Y')
        hora = "09:00"
        
        texto_lower = texto.lower()
        
        # DATAS SIMPLES E FUNCIONAIS
        if 'amanhã' in texto_lower:
            data = (hoje + datetime.timedelta(days=1)).strftime('%d/%m/%Y')
        elif 'hoje' in texto_lower:
            data = hoje.strftime('%d/%m/%Y')
        
        # DIAS DA SEMANA
        dias = {
            'segunda': 0, 'terça': 1, 'quarta': 2, 'quinta': 3,
            'sexta': 4, 'sábado': 5, 'domingo': 6
        }
        for dia, offset in dias.items():
            if dia in texto_lower:
                dias_diferenca = (offset - hoje.weekday()) % 7
                data_alvo = hoje + datetime.timedelta(days=dias_diferenca)
                data = data_alvo.strftime('%d/%m/%Y')
                break
        
        # HORAS - MÉTODO DIRETO E FUNCIONAL
        hora_encontrada = self._extrair_hora_direto(texto_lower)
        if hora_encontrada:
            hora = hora_encontrada
        
        return data, hora

    def _extrair_hora_direto(self, texto):
        """Extrai hora de forma DIRETA e CONFIÁVEL"""
        
        # PADRÃO 1: "2:00 da tarde" -> 14:00
        padrao1 = r'(\d{1,2})[:h]?(\d{0,2})?\s*(?:da\s+)?(tarde|noite)'
        match1 = re.search(padrao1, texto)
        if match1:
            hora_str, minuto_str, periodo = match1.groups()
            hora = int(hora_str)
            minutos = int(minuto_str) if minuto_str and minuto_str.isdigit() else 0
            
            if periodo in ['tarde', 'noite'] and hora < 12:
                hora += 12
            
            return f"{hora:02d}:{minutos:02d}"
        
        # PADRÃO 2: "11h30" -> 11:30
        padrao2 = r'(\d{1,2})[h: ]?(\d{2})'
        match2 = re.search(padrao2, texto)
        if match2:
            hora_str, minuto_str = match2.groups()
            return f"{int(hora_str):02d}:{minuto_str}"
        
        # PADRÃO 3: "14h" -> 14:00
        padrao3 = r'(\d{1,2})\s*h\s*'
        match3 = re.search(padrao3, texto)
        if match3:
            hora_str = match3.group(1)
            return f"{int(hora_str):02d}:00"
        
        # PADRÃO 4: "2 da tarde" -> 14:00
        padrao4 = r'(\d{1,2})\s+(?:horas?\s+)?da\s+(tarde|noite)'
        match4 = re.search(padrao4, texto)
        if match4:
            hora_str, periodo = match4.groups()
            hora = int(hora_str)
            if periodo in ['tarde', 'noite'] and hora < 12:
                hora += 12
            return f"{hora:02d}:00"
        
        return None

    def detectar_intencao(self, texto):
        """Detecta intenção de forma PRÁTICA"""
        texto_lower = texto.lower()
        
        if any(palavra in texto_lower for palavra in ['telefonar', 'ligar', 'visitar', 'buscar', 'encontrar', 'reunião']):
            return 'agendar'
        elif any(palavra in texto_lower for palavra in ['comprar', 'leite', 'pão', 'lista']):
            return 'compras'
        elif any(palavra in texto_lower for palavra in ['agenda', 'que tenho', 'ver']):
            return 'consultar'
        else:
            return 'outro'

# =============================================
# BANCO DE DADOS SIMPLES
# =============================================

class BancoSimples:
    def __init__(self):
        self.conn = sqlite3.connect('assistente_simples.db', check_same_thread=False)
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        print("✅ Banco pronto")
    
    def salvar_compromisso(self, user_id, titulo, data, hora):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO compromissos (user_id, titulo, data, hora) VALUES (?, ?, ?, ?)",
                (user_id, titulo, data, hora)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao salvar: {e}")
            return False
    
    def buscar_compromissos(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT titulo, data, hora FROM compromissos WHERE user_id = ? ORDER BY data, hora",
                (user_id,)
            )
            return cursor.fetchall()
        except Exception:
            return []

# =============================================
# ASSISTENTE PRINCIPAL - SIMPLES E EFETIVO
# =============================================

db = BancoSimples()
processador = ProcessadorPortugues()

def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    
    mensagem = f"""
👋 **Olá {user.first_name}!**

Sou seu **Assistente Pessoal Prático**! 🤖

🎯 **AGORA ENTENDO FRASES REAIS:**

• `"Visitar o meu pai no hospital às 2:00 da tarde"` ✅
• `"Telefonar à minha mãe amanhã 11h30"` ✅
• `"Buscar filhos na escola sexta 17h"` ✅

💡 **Fale naturalmente - eu entendo!**

**Experimente agora com uma das frases acima!** 🚀
    """
    
    update.message.reply_text(mensagem, parse_mode='Markdown')

def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    texto = update.message.text
    
    print(f"📨 Processando: '{texto}'")
    
    try:
        # DETECTA O QUE O USUÁRIO QUER
        intencao = processador.detectar_intencao(texto)
        
        if intencao == 'agendar':
            # PROCESSAMENTO INTELIGENTE
            titulo = processador.extrair_titulo_inteligente(texto)
            data, hora = processador.extrair_data_hora_funcional(texto)
            
            print(f"📅 Titulo: {titulo}")
            print(f"📅 Data: {data}, Hora: {hora}")
            
            if db.salvar_compromisso(user_id, titulo, data, hora):
                resposta = f"""✅ **AGENDADO COM SUCESSO!**

📝 **{titulo}**
🗓️ **Data:** {data}
⏰ **Hora:** {hora}

💡 _Use 'Minha agenda' para ver todos_"""
            else:
                resposta = "❌ Erro ao agendar. Tente novamente."
        
        elif intencao == 'consultar':
            compromissos = db.buscar_compromissos(user_id)
            if compromissos:
                resposta = "📅 **SUA AGENDA**\n\n"
                for titulo, data, hora in compromissos:
                    resposta += f"• **{titulo}**\n  📅 {data} ⏰ {hora}\n\n"
            else:
                resposta = "📅 *Sua agenda está vazia*"
        
        else:
            resposta = """🤖 **Como posso ajudar?**

💡 **Exemplos que funcionam:**
• `Visitar o meu pai no hospital às 2:00 da tarde`
• `Telefonar à minha mãe amanhã 11h30`
• `Buscar filhos na escola sexta 17h`

🎯 **Fale naturalmente!**"""
        
        update.message.reply_text(resposta, parse_mode='Markdown')
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        update.message.reply_text(
            "❌ **Erro de processamento.** Tente reformular.",
            parse_mode='Markdown'
        )

def main():
    print("🚀 Iniciando Assistente Prático...")
    
    try:
        updater = Updater(BOT_TOKEN, use_context=True)
        dp = updater.dispatcher
        
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        
        updater.start_polling()
        
        print("✅ Bot prático ativo!")
        print("🤖 Teste estas frases:")
        print("   • 'Visitar o meu pai no hospital às 2:00 da tarde'")
        print("   • 'Telefonar à minha mãe amanhã 11h30'")
        
        updater.idle()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
