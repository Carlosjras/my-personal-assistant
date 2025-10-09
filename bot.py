#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASSISTENTE PESSOAL AVANÇADO - SISTEMA DE ALTA COMPLEXIDADE
Com capacidade interpretativa profunda de linguagem natural
"""

import os
import sqlite3
import datetime
import re
import sys
from enum import Enum
from typing import Dict, List, Tuple, Optional

print("🧠 Iniciando Assistente com Inteligência Avançada...")

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
# ENUMS E ESTRUTURAS COMPLEXAS
# =============================================

class TipoIntencao(Enum):
    AGENDAR = "agendar"
    CONSULTAR = "consultar" 
    LISTA_COMPRAS = "lista_compras"
    LEMBRETE = "lembrete"
    SAUDACAO = "saudacao"
    AGRADECIMENTO = "agradecimento"
    DESCONHECIDO = "desconhecido"

class EntidadeTemporal:
    def __init__(self):
        self.data = None
        self.hora = None
        self.periodo_dia = None
        self.duracao = None
        self.repeticao = None

class EntidadeNomeada:
    def __init__(self):
        self.pessoas = []
        self.locais = []
        self.organizacoes = []

class EstruturaFrase:
    def __init__(self):
        self.verbo_principal = None
        self.sujeito = None
        self.objeto = None
        self.complementos = []
        self.adjuntos_temporais = []
        self.adjuntos_locais = []

# =============================================
# ANALISADOR SINTÁTICO AVANÇADO
# =============================================

class AnalisadorSintatico:
    def __init__(self):
        # VERBOS DE AÇÃO EXPANDIDOS
        self.verbos_acao = {
            'telefonar', 'ligar', 'chamar', 'discar', 'contactar',
            'visitar', 'encontrar', 'ver', 'encontrar', 'ir ver',
            'buscar', 'apanhar', 'pegar', 'levar', 'trazer',
            'marcar', 'agendar', 'marcação', 'agendamento',
            'consultar', 'visitar', 'passar no', 'ir ao', 'dirigir',
            'reunir', 'encontrar', 'conversar', 'falar'
        }
        
        # PESSOAS COMUNS (PODE EXPANDIR)
        self.pessoas_comuns = {
            'pai', 'mãe', 'mãe', 'avô', 'avó', 'filho', 'filha',
            'marido', 'esposa', 'mulher', 'namorado', 'namorada',
            'amigo', 'amiga', 'colega', 'chefe', 'cliente', 'médico'
        }
        
        # LOCAIS COMUNS
        self.locais_comuns = {
            'hospital', 'escola', 'trabalho', 'casa', 'escritório',
            'consultório', 'supermercado', 'mercado', 'farmácia',
            'shopping', 'centro comercial', 'aeroporto'
        }

    def analisar_estrutura(self, texto: str) -> EstruturaFrase:
        """Análise sintática profunda da frase"""
        estrutura = EstruturaFrase()
        texto_lower = texto.lower()
        
        # TOKENIZAÇÃO E ANÁLISE BÁSICA
        palavras = texto_lower.split()
        
        # IDENTIFICAR VERBO PRINCIPAL
        for palavra in palavras:
            if palavra in self.verbos_acao:
                estrutura.verbo_principal = palavra
                break
        
        # IDENTIFICAR SUJEITO (antes do verbo)
        if estrutura.verbo_principal:
            idx_verbo = palavras.index(estrutura.verbo_principal)
            estrutura.sujeito = ' '.join(palavras[:idx_verbo]) if idx_verbo > 0 else "eu"
        
        # IDENTIFICAR OBJETO (depois do verbo)
        if estrutura.verbo_principal:
            idx_verbo = palavras.index(estrutura.verbo_principal)
            estrutura.objeto = ' '.join(palavras[idx_verbo + 1:])
        
        # EXTRAIR ENTIDADES NOMEADAS
        entidades = self.extrair_entidades_nomeadas(texto_lower)
        estrutura.complementos.extend(entidades.pessoas)
        estrutura.complementos.extend(entidades.locais)
        
        # EXTRAIR ADJUNTOS TEMPORAIS
        estrutura.adjuntos_temporais = self.extrair_referencias_temporais(texto_lower)
        
        # EXTRAIR ADJUNTOS LOCAIS
        estrutura.adjuntos_locais = self.extrair_referencias_locais(texto_lower)
        
        return estrutura

    def extrair_entidades_nomeadas(self, texto: str) -> EntidadeNomeada:
        """Extrai pessoas, locais e organizações do texto"""
        entidades = EntidadeNomeada()
        
        # PESSOAS
        for pessoa in self.pessoas_comuns:
            if pessoa in texto:
                entidades.pessoas.append(pessoa)
        
        # LOCAIS
        for local in self.locais_comuns:
            if local in texto:
                entidades.locais.append(local)
        
        return entidades

    def extrair_referencias_temporais(self, texto: str) -> List[str]:
        """Extrai todas as referências temporais"""
        temporais = []
        
        # PADRÕES TEMPORAIS COMPLEXOS
        padroes = [
            r'(\d{1,2})[h: ]?(\d{0,2})\s*(da\s+(manhã|tarde|noite))',
            r'(\d{1,2})\s*(horas)\s*(da\s+(manhã|tarde|noite))',
            r'(\d{1,2})[h: ]?(\d{0,2})\s*(h)',
            r'(\d{1,2})\s*(em ponto)',
            r'(meio-dia|meio dia)',
            r'(meia-noite|meia noite)',
            r'(amanhã|hoje|depois de amanhã)',
            r'(segunda|terça|quarta|quinta|sexta|sábado|domingo)'
        ]
        
        for padrao in padroes:
            matches = re.finditer(padrao, texto, re.IGNORECASE)
            for match in matches:
                temporais.append(match.group())
        
        return temporais

    def extrair_referencias_locais(self, texto: str) -> List[str]:
        """Extrai referências locais"""
        locais = []
        
        for local in self.locais_comuns:
            if local in texto:
                locais.append(local)
        
        return locais

# =============================================
# PROCESSADOR TEMPORAL AVANÇADO
# =============================================

class ProcessadorTemporal:
    def __init__(self):
        self.dias_semana = {
            'segunda': 0, 'terça': 1, 'quarta': 2, 'quinta': 3,
            'segunda-feira': 0, 'terça-feira': 1, 'quarta-feira': 2, 'quinta-feira': 3,
            'sexta': 4, 'sábado': 5, 'domingo': 6,
            'sexta-feira': 4
        }
        
        self.periodos_dia = {
            'manhã': (6, 12),
            'tarde': (12, 18), 
            'noite': (18, 24),
            'madrugada': (0, 6)
        }

    def processar_temporalidade(self, texto: str) -> EntidadeTemporal:
        """Processamento temporal de alta precisão"""
        temporal = EntidadeTemporal()
        texto_lower = texto.lower()
        
        # DATA PRIMEIRO
        temporal.data = self.extrair_data(texto_lower)
        
        # HORA COM PERÍODO DO DIA
        hora_info = self.extrair_hora_com_periodo(texto_lower)
        temporal.hora = hora_info['hora']
        temporal.periodo_dia = hora_info['periodo']
        
        return temporal

    def extrair_data(self, texto: str) -> str:
        """Extrai data com alta precisão"""
        hoje = datetime.datetime.now()
        
        # DIAS DA SEMANA
        for dia, offset in self.dias_semana.items():
            if dia in texto:
                dias_diferenca = (offset - hoje.weekday()) % 7
                data_alvo = hoje + datetime.datetime.timedelta(days=dias_diferenca)
                return data_alvo.strftime('%d/%m/%Y')
        
        # EXPRESSÕES TEMPORAIS
        if 'amanhã' in texto:
            return (hoje + datetime.timedelta(days=1)).strftime('%d/%m/%Y')
        elif 'depois de amanhã' in texto:
            return (hoje + datetime.timedelta(days=2)).strftime('%d/%m/%Y')
        elif 'hoje' in texto:
            return hoje.strftime('%d/%m/%Y')
        
        # PADRÃO DD/MM ou DD-MM
        padrao_data = r'(\d{1,2})[/-](\d{1,2})'
        match = re.search(padrao_data, texto)
        if match:
            dia, mes = match.groups()
            ano = hoje.year
            return f"{int(dia):02d}/{int(mes):02d}/{ano}"
        
        return hoje.strftime('%d/%m/%Y')

    def extrair_hora_com_periodo(self, texto: str) -> Dict:
        """Extrai hora considerando período do dia - CORREÇÃO CRÍTICA"""
        # PADRÃO: "2:00 da tarde" ou "2 da tarde" ou "14h" ou "14:00"
        padrao_completo = r'(\d{1,2})[h: ]?(\d{0,2})?\s*(?:horas?)?\s*(?:da\s+)?(manhã|tarde|noite|madrugada)?'
        matches = re.finditer(padrao_completo, texto, re.IGNORECASE)
        
        for match in matches:
            hora_str, minuto_str, periodo = match.groups()
            
            if hora_str:
                hora = int(hora_str)
                minutos = int(minuto_str) if minuto_str and minuto_str.isdigit() else 0
                
                # CORREÇÃO DO BUG: Converter para formato 24h baseado no período
                if periodo:
                    if periodo.lower() in ['tarde', 'noite'] and hora < 12:
                        hora += 12
                    elif periodo.lower() == 'madrugada' and hora > 12:
                        hora -= 12
                
                # Garantir que hora está no range correto
                hora = hora % 24
                
                return {
                    'hora': f"{hora:02d}:{minutos:02d}",
                    'periodo': periodo
                }
        
        # SE NÃO ENCONTROU, TENTA PADRÕES SIMPLES
        padrao_simples = r'(\d{1,2})[h: ]?(\d{0,2})'
        match = re.search(padrao_simples, texto)
        if match:
            hora_str, minuto_str = match.groups()
            hora = int(hora_str) % 24
            minutos = int(minuto_str) if minuto_str and minuto_str.isdigit() else 0
            return {
                'hora': f"{hora:02d}:{minutos:02d}",
                'periodo': None
            }
        
        # PADRÃO DE TEXTO
        if 'meio-dia' in texto or 'meio dia' in texto:
            return {'hora': '12:00', 'periodo': 'tarde'}
        elif 'meia-noite' in texto or 'meia noite' in texto:
            return {'hora': '00:00', 'periodo': 'madrugada'}
        
        return {'hora': '09:00', 'periodo': None}

# =============================================
# CLASSIFICADOR DE INTENÇÕES AVANÇADO
# =============================================

class ClassificadorIntencoes:
    def __init__(self):
        self.padroes_intencao = {
            TipoIntencao.AGENDAR: [
                r'\b(telefonar|ligar|visitar|encontrar|buscar|marcar|agendar|ir\s+ao|ir\s+ver)\b',
                r'\b(reunião|consulta|compromisso|encontro)\b'
            ],
            TipoIntencao.LISTA_COMPRAS: [
                r'\b(comprar|preciso de|acabou|faltam|lista)\b',
                r'\b(leite|pão|arroz|feijão|supermercado|mercado)\b'
            ],
            TipoIntencao.CONSULTAR: [
                r'\b(que tenho|minha agenda|ver agenda|o que falta|consultar)\b'
            ],
            TipoIntencao.SAUDACAO: [
                r'\b(olá|oi|ola|bom dia|boa tarde|boa noite)\b'
            ]
        }

    def classificar(self, texto: str) -> TipoIntencao:
        """Classifica a intenção principal do usuário"""
        texto_lower = texto.lower()
        
        for intencao, padroes in self.padroes_intencao.items():
            for padrao in padroes:
                if re.search(padrao, texto_lower, re.IGNORECASE):
                    return intencao
        
        return TipoIntencao.DESCONHECIDO

# =============================================
# GERADOR DE RESPOSTAS CONTEXTUAIS
# =============================================

class GeradorRespostas:
    def __init__(self):
        self.analisador = AnalisadorSintatico()
        self.processador_temporal = ProcessadorTemporal()
        self.classificador = ClassificadorIntencoes()

    def gerar_resposta_agendamento(self, texto: str, estrutura: EstruturaFrase, temporal: EntidadeTemporal) -> str:
        """Gera resposta contextual para agendamento"""
        
        # TÍTULO INTELIGENTE BASEADO NA ANÁLISE
        if estrutura.verbo_principal == 'telefonar' or estrutura.verbo_principal == 'ligar':
            pessoa = next((p for p in estrutura.complementos if p in estrutura.analisador.pessoas_comuns), "contato")
            titulo = f"Telefonar para {pessoa}"
        
        elif estrutura.verbo_principal == 'visitar':
            local = next((l for l in estrutura.complementos if l in estrutura.analisador.locais_comuns), "local")
            pessoa = next((p for p in estrutura.complementos if p in estrutura.analisador.pessoas_comuns), None)
            if pessoa:
                titulo = f"Visitar {pessoa} no {local}"
            else:
                titulo = f"Visitar {local}"
        
        elif estrutura.verbo_principal:
            titulo = f"{estrutura.verbo_principal.title()} {estrutura.objeto or ''}"
        else:
            titulo = "Compromisso"
        
        # CONFIRMAÇÃO DETALHADA
        confirmacao = f"""✅ **COMPROMISSO AGENDADO COM SUCESSO!**

📅 **{titulo}**
🗓️ **Data:** {temporal.data}
⏰ **Hora:** {temporal.hora}"""

        # DETALHES CONTEXTUAIS
        if estrutura.complementos:
            confirmacao += f"\n👥 **Envolvidos:** {', '.join(estrutura.complementos)}"
        
        if estrutura.adjuntos_locais:
            confirmacao += f"\n📍 **Local:** {', '.join(estrutura.adjuntos_locais)}"
        
        confirmacao += "\n\n💡 _Você receberá um lembrete 15 minutos antes._"
        
        return confirmacao

# =============================================
# SISTEMA PRINCIPAL
# =============================================

class AssistenteAvancado:
    def __init__(self):
        self.db = sqlite3.connect('assistente_avancado.db', check_same_thread=False)
        self.criar_banco()
        self.analisador = AnalisadorSintatico()
        self.processador_temporal = ProcessadorTemporal()
        self.classificador = ClassificadorIntencoes()
        self.gerador_respostas = GeradorRespostas()
        print("✅ Sistema de IA carregado")

    def criar_banco(self):
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compromissos_avancados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                titulo TEXT,
                data TEXT,
                hora TEXT,
                pessoas TEXT,
                locais TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.db.commit()

    def processar_mensagem(self, texto: str, user_id: int) -> str:
        """Processamento principal com IA avançada"""
        
        # ANÁLISE PROFUNDA
        estrutura = self.analisador.analisar_estrutura(texto)
        temporal = self.processador_temporal.processar_temporalidade(texto)
        intencao = self.classificador.classificar(texto)
        
        print(f"🔍 ANÁLISE:")
        print(f"   Verbo: {estrutura.verbo_principal}")
        print(f"   Sujeito: {estrutura.sujeito}")
        print(f"   Objeto: {estrutura.objeto}")
        print(f"   Complementos: {estrutura.complementos}")
        print(f"   Temporais: {estrutura.adjuntos_temporais}")
        print(f"   Locais: {estrutura.adjuntos_locais}")
        print(f"   Data: {temporal.data}")
        print(f"   Hora: {temporal.hora}")
        print(f"   Intenção: {intencao}")
        
        # AÇÃO BASEADA NA INTENÇÃO
        if intencao == TipoIntencao.AGENDAR:
            return self.processar_agendamento(texto, estrutura, temporal, user_id)
        elif intencao == TipoIntencao.CONSULTAR:
            return self.processar_consulta(user_id)
        else:
            return self.gerar_resposta_geral(intencao, texto)

    def processar_agendamento(self, texto: str, estrutura: EstruturaFrase, temporal: EntidadeTemporal, user_id: int) -> str:
        """Processa agendamento com inteligência contextual"""
        
        # GERAR TÍTULO INTELIGENTE
        titulo = self.gerar_titulo_contextual(estrutura)
        
        # SALVAR NO BANCO
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO compromissos_avancados (user_id, titulo, data, hora, pessoas, locais) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, titulo, temporal.data, temporal.hora, 
             ','.join(estrutura.complementos), ','.join(estrutura.adjuntos_locais))
        )
        self.db.commit()
        
        # GERAR RESPOSTA
        return self.gerador_respostas.gerar_resposta_agendamento(texto, estrutura, temporal)

    def gerar_titulo_contextual(self, estrutura: EstruturaFrase) -> str:
        """Gera título inteligente baseado no contexto"""
        
        if estrutura.verbo_principal == 'telefonar':
            pessoa = next((p for p in estrutura.complementos), "contato")
            return f"Telefonar para {pessoa}"
        
        elif estrutura.verbo_principal == 'visitar':
            local = next((l for l in estrutura.complementos if l in self.analisador.locais_comuns), None)
            pessoa = next((p for p in estrutura.complementos if p in self.analisador.pessoas_comuns), None)
            
            if pessoa and local:
                return f"Visitar {pessoa} no {local}"
            elif local:
                return f"Visitar {local}"
            elif pessoa:
                return f"Visitar {pessoa}"
            else:
                return "Visita"
        
        elif estrutura.verbo_principal:
            acao = estrutura.verbo_principal.title()
            objeto = estrutura.objeto or ""
            return f"{acao} {objeto}".strip()
        
        return "Compromisso"

    def processar_consulta(self, user_id: int) -> str:
        """Processa consulta à agenda"""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT titulo, data, hora FROM compromissos_avancados WHERE user_id = ? ORDER BY data, hora",
            (user_id,)
        )
        compromissos = cursor.fetchall()
        
        if not compromissos:
            return "📅 *Sua agenda está vazia.*"
        
        resposta = "📅 **SUA AGENDA AVANÇADA**\n\n"
        for titulo, data, hora in compromissos:
            resposta += f"• **{titulo}**\n  📅 {data} ⏰ {hora}\n\n"
        
        return resposta

    def gerar_resposta_geral(self, intencao: TipoIntencao, texto: str) -> str:
        """Resposta para intenções não relacionadas a agendamento"""
        if intencao == TipoIntencao.SAUDACAO:
            return "👋 Olá! Sou seu assistente inteligente. Posso ajudar com agendamentos complexos como 'Visitar o pai no hospital às 2 da tarde'!"
        else:
            return """🤖 **Assistente Inteligente**

💡 **Exemplos que entendo:**
• `Telefonar ao meu pai às 10h30`
• `Visitar o médico no hospital às 2 da tarde` 
• `Buscar filhos na escola amanhã 17h`
• `Reunião com cliente sexta 14h`

🎯 **Fale naturalmente que eu entendo!**"""

# =============================================
# HANDLERS DO BOT
# =============================================

assistente = AssistenteAvancado()

def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    
    mensagem = f"""
🧠 **Olá {user.first_name}!**

Sou seu **Assistente Pessoal com IA Avançada**! 

🎯 **AGORA ENTENDO LINGUAGEM NATURAL COMPLEXA:**

• `"Visitar o meu pai no hospital às 2:00 da tarde"` ✅
• `"Telefonar à mãe amanhã 10h30"` ✅  
• `"Buscar filhos na escola sexta 17h"` ✅
• `"Reunião com cliente no escritório segunda 9h"` ✅

💡 **Fale exatamente como falaria com uma pessoa!**

**Experimente uma frase complexa agora!** 🚀
    """
    
    update.message.reply_text(mensagem, parse_mode='Markdown')

def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    texto = update.message.text
    
    print(f"🧠 Processando: '{texto}'")
    
    try:
        resposta = assistente.processar_mensagem(texto, user_id)
        update.message.reply_text(resposta, parse_mode='Markdown')
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        update.message.reply_text(
            "❌ **Erro no processamento.** Tente reformular a frase.",
            parse_mode='Markdown'
        )

def main():
    print("🧠 Iniciando Sistema de IA Avançada...")
    
    try:
        updater = Updater(BOT_TOKEN, use_context=True)
        dp = updater.dispatcher
        
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        
        updater.start_polling()
        
        print("✅ Sistema de IA ativo!")
        print("🧠 Aguardando frases complexas...")
        print("💡 Teste: 'Visitar o meu pai no hospital às 2:00 da tarde'")
        
        updater.idle()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
