# app.py - Aplicação Flask para D&D Solo com CrewAI
from flask import Flask, render_template, request, jsonify
import json
import os
import time
from threading import Thread, Event
from queue import Queue

# Importa o sistema de jogo
from main import executar_turno

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dnd-crewai-secret'

# Filas para processar comandos de forma assíncrona
command_queue = Queue()
response_queue = Queue()
processing_event = Event()


# Função para processar comandos em background
def process_commands():
    while True:
        if not command_queue.empty():
            command_id, command_text = command_queue.get()
            processing_event.set()

            try:
                # Executa o comando no sistema de jogo
                response = executar_turno(command_text)
                response_queue.put((command_id, response, True))
            except Exception as e:
                response_queue.put((command_id, str(e), False))

            processing_event.clear()
            command_queue.task_done()

        time.sleep(0.1)


# Inicia o thread de processamento
processor_thread = Thread(target=process_commands, daemon=True)
processor_thread.start()

# Histórico da sessão
session_history = []


# Rotas da aplicação
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start', methods=['GET'])
def start_game():
    # Inicializa o jogo com uma descrição introdutória
    intro_response = executar_turno("Observar o ambiente ao entrar na cripta.")

    # Adiciona a introdução ao histórico
    session_history.append({
        'type': 'system',
        'content': '🎲 D&D 5e Solo com IA: Cripta do Coração Negro'
    })
    session_history.append({
        'type': 'system',
        'content': '🧙‍♂️ Você é Alion, um mago humano explorando as profundezas da sinistra Cripta do Coração Negro.'
    })
    session_history.append({
        'type': 'response',
        'content': intro_response
    })

    return jsonify({
        'success': True,
        'history': session_history
    })


@app.route('/command', methods=['POST'])
def process_command():
    data = request.json
    command_text = data.get('command', '')
    command_id = data.get('id', int(time.time()))

    if command_text.lower() in ['sair', 'exit', 'quit']:
        session_history.append({
            'type': 'command',
            'content': command_text
        })
        session_history.append({
            'type': 'system',
            'content': '⚰️ A sessão termina aqui. Obrigado por jogar!'
        })
        return jsonify({
            'success': True,
            'history': session_history,
            'ended': True
        })

    # Adiciona o comando ao histórico
    session_history.append({
        'type': 'command',
        'content': command_text
    })

    # Envia o comando para processamento em background
    command_queue.put((command_id, command_text))

    # Retorna imediatamente para não bloquear o cliente
    return jsonify({
        'success': True,
        'processing': True,
        'command_id': command_id,
        'history': session_history
    })


@app.route('/status/<int:command_id>', methods=['GET'])
def check_status(command_id):
    # Verifica se o comando está sendo processado
    if processing_event.is_set():
        return jsonify({
            'success': True,
            'processing': True,
            'message': 'Pensando...'
        })

    # Verifica se há uma resposta disponível
    for i in range(response_queue.qsize()):
        cid, response, success = response_queue.queue[i]
        if cid == command_id:
            # Consome a resposta da fila
            response_queue.get()

            if success:
                # Adiciona a resposta ao histórico
                session_history.append({
                    'type': 'response',
                    'content': response
                })

                return jsonify({
                    'success': True,
                    'processing': False,
                    'response': response,
                    'history': session_history
                })
            else:
                return jsonify({
                    'success': False,
                    'error': response
                })

    # Comando ainda em processamento ou não encontrado
    return jsonify({
        'success': True,
        'processing': True,
        'message': 'Aguardando resposta...'
    })


@app.route('/character', methods=['GET'])
def get_character():
    try:
        with open('personagem.json', 'r') as file:
            character = json.load(file)
        return jsonify({
            'success': True,
            'character': character
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


if __name__ == '__main__':
    app.run(debug=True)