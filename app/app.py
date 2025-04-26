# app.py - Aplicação Flask para D&D Solo com CrewAI
from flask import Flask, render_template, request, jsonify
import json
import os
import time
from threading import Thread, Event
from queue import Queue, Empty

# Importa o sistema de jogo
from main import processar_comando

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dnd-crewai-secret'

# Filas para processar comandos de forma assíncrona
command_queue = Queue()
# Store responses with command_id: { 'status': 'processing'/'done'/'error', 'data': ... }
response_cache = {}
processing_event = Event() # To indicate if *any* task is running

# Store original command text associated with command_id
command_texts = {}

# Função para processar comandos em background
def process_commands():
    while True:
        try:
            # Use non-blocking get
            command_id, command_text = command_queue.get_nowait()
            processing_event.set()
            response_cache[command_id] = {'status': 'processing', 'data': None}
            print(f"Processing command {command_id}: {command_text}")

            try:
                # Usa a função correta do main.py para processar o comando
                response_obj = processar_comando(command_text)
                response_str = str(response_obj)
                print(f"Response for {command_id} generated.")
                # Store successful response
                response_cache[command_id] = {
                    'status': 'done',
                    'data': response_str
                }

            except Exception as e:
                error_str = str(e)
                print(f"Error processing command {command_id}: {error_str}")
                 # Store error response
                response_cache[command_id] = {
                    'status': 'error',
                    'data': error_str
                }
            finally:
                processing_event.clear() # Clear after this specific task
                command_queue.task_done()

        except Empty:
            # Queue is empty, wait a bit
            time.sleep(0.2)
        except Exception as e:
             # Catch potential errors in the loop itself
             print(f"Error in command processing thread: {e}")
             # Optionally clear the processing event if it was set
             if processing_event.is_set():
                 processing_event.clear()
             time.sleep(1) # Wait longer after an error


# Inicia o thread de processamento
processor_thread = Thread(target=process_commands, daemon=True)
processor_thread.start()

# Histórico da sessão (in-memory, will reset on server restart)
# *** IMPORTANT: This needs proper session management for multiple users ***
# For simplicity now, it's global, but this is NOT production-ready for >1 user.
session_history = []

@app.route('/')
def index():
    global session_history, response_cache, command_texts
    session_history = []
    response_cache = {} # Clear caches for new session
    command_texts = {}
    print("New session started, history cleared.")
    return render_template('index.html')

@app.route('/start', methods=['GET'])
def start_game():
    global session_history
    session_history = [] # Ensure history is clean

    try:
        print("Starting game...")
        # Use a distinct command for intro observation
        intro_command = "Descreva a entrada da Cripta do Coração Negro e os primeiros passos de Alion dentro dela."
        # Process the command directly instead of using CrewAI here
        intro_response_str = processar_comando(intro_command)
        print("Intro response received.")

        # Add intro messages to history
        history_additions = [
            {'type': 'system','content': '🎲 D&D 5e Solo com IA: Cripta do Coração Negro'},
            {'type': 'system','content': '🧙‍♂️ Você é Alion, um mago humano explorando as profundezas da sinistra Cripta do Coração Negro.'},
            {'type': 'response', 'content': intro_response_str}
        ]
        session_history.extend(history_additions)
        print("History initialized:", session_history)

        return jsonify({
            'success': True,
            'history': session_history # Send the initial history
        })
    except Exception as e:
        print(f"Error during game start: {e}")
        return jsonify({'success': False, 'error': f'Failed to start game: {str(e)}'}), 500

@app.route('/command', methods=['POST'])
def handle_command(): # Renamed from process_command to avoid confusion
    global command_texts
    data = request.json
    command_text = data.get('command', '').strip()
    # Use frontend ID if possible, ensure uniqueness
    command_id = data.get('id', f"cmd_{int(time.time() * 1000)}_{hash(command_text)}")

    if not command_text:
         return jsonify({'success': False, 'error': 'Empty command received'}), 400

    print(f"Received command {command_id}: {command_text}")

    # Check for quit command BEFORE queuing
    if command_text.lower() in ['sair', 'exit', 'quit']:
        print(f"Quit command received.")
        # Add command and quit message to history
        history_additions = [
             {'type': 'command', 'content': command_text},
             {'type': 'system', 'content': '⚰️ A sessão termina aqui. Obrigado por jogar!'}
        ]
        session_history.extend(history_additions)
        return jsonify({
            'success': True,
            'history': session_history, # Send final history state
            'ended': True
        })

    # Store command text associated with ID for later retrieval
    command_texts[command_id] = command_text

    # Envia o comando para processamento em background
    command_queue.put((command_id, command_text))
    response_cache[command_id] = {'status': 'queued', 'data': None} # Mark as queued

    # Return immediately acknowledging receipt, indicating processing will start
    # Do NOT send history here, let /status handle updates
    return jsonify({
        'success': True,
        'processing': True, # Tell frontend to start polling
        'command_id': command_id
    })

@app.route('/status/<command_id>', methods=['GET'])
def check_status(command_id):
    global session_history, response_cache, command_texts

    print(f"Checking status for command {command_id}")
    status_info = response_cache.get(command_id)

    if not status_info:
        # Command ID not recognized or very old?
        print(f"Status check for unknown/old command ID: {command_id}")
        return jsonify({'success': False, 'error': 'Unknown command ID', 'processing': False})

    status = status_info['status']
    data = status_info['data']

    if status == 'queued' or status == 'processing':
        print(f"Command {command_id} is {status}.")
        return jsonify({
            'success': True,
            'processing': True,
            'message': 'Pensando...' if status == 'processing' else 'Na fila...'
        })
    elif status == 'done':
        print(f"Command {command_id} is done.")
        # Get the original command text
        original_command = command_texts.get(command_id, "[Comando não encontrado]")
        response_content = data

        history_additions = [
            {'type': 'command', 'content': original_command},
            {'type': 'response', 'content': response_content}
        ]
        session_history.extend(history_additions)

        return jsonify({
            'success': True,
            'processing': False,
            'history_additions': history_additions
        })
    elif status == 'error':
        print(f"Command {command_id} resulted in error.")
        original_command = command_texts.get(command_id, "[Comando não encontrado]")
        error_message = data

        history_additions = [
             {'type': 'command', 'content': original_command},
             {'type': 'error', 'content': f"Erro: {error_message}"}
        ]
        session_history.extend(history_additions)

        return jsonify({
            'success': False,
            'processing': False,
            'error': error_message,
            'history_additions': history_additions
        })
    else:
         # Should not happen
         print(f"Unknown status '{status}' for command {command_id}")
         return jsonify({'success': False, 'error': 'Internal status error', 'processing': False})


@app.route('/character', methods=['GET'])
def get_character():
    try:
        file_path = 'personagem.json'
        if not os.path.exists(file_path):
             # Try one level up if running from a subdirectory? Unlikely here.
             # file_path = os.path.join(os.path.dirname(__file__), '..', 'personagem.json')
             raise FileNotFoundError("personagem.json not found.")

        with open(file_path, 'r', encoding='utf-8') as file:
            character = json.load(file)
        return jsonify({
            'success': True,
            'character': character
        })
    except FileNotFoundError:
         print("Error: personagem.json not found at expected path.")
         return jsonify({'success': False,'error': 'Character file not found.'}), 404
    except json.JSONDecodeError as e:
        print(f"Error decoding character JSON: {e}")
        return jsonify({'success': False, 'error': f'Invalid character file format: {e}.'}), 500
    except Exception as e:
        print(f"Unexpected error loading character: {e}")
        return jsonify({'success': False, 'error': f'An internal error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True) # use_reloader might be default with debug=True