// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    const narrativeContainer = document.getElementById('narrative-container');
    const commandInput = document.getElementById('command-input');
    const sendCommandBtn = document.getElementById('send-command-btn');
    const startGameBtn = document.getElementById('start-game-btn');
    const statusIndicator = document.getElementById('status-indicator');
    const suggestions = document.querySelectorAll('.suggestion');

    // Variáveis de estado
    let gameStarted = false;
    let processingCommand = false;
    let pollingInterval = null;
    const POLLING_INTERVAL_MS = 2000; // Check status every 2 seconds

    const collapsibles = document.querySelectorAll('.collapsible-header');
    collapsibles.forEach(header => {
        header.addEventListener('click', function() {
            const parent = this.parentElement;
            parent.classList.toggle('active');
            const icon = this.querySelector('.fa-chevron-down, .fa-chevron-up'); // More specific selector
            if (icon) {
                icon.classList.toggle('fa-chevron-down');
                icon.classList.toggle('fa-chevron-up');
            }
        });
    });

    function loadCharacterInfo() {
        fetch('/character')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
             })
            .then(data => {
                if (data.success) {
                    const character = data.character;
                    // Update basic info
                    document.getElementById('char-class').textContent = character.classe || 'N/A';
                    document.getElementById('char-race').textContent = character.raca || 'N/A';
                    document.getElementById('char-level').textContent = character.nivel || 'N/A';

                    // Update health bar using CORRECTED keys from personagem.json
                    const maxHealth = character.pv_maximo || 0;
                    const currentHealth = character.pv_atual || 0;
                    const healthPercentage = maxHealth > 0 ? (currentHealth / maxHealth) * 100 : 0;
                    const healthBarFill = document.getElementById('health-bar-fill');
                    const healthText = document.getElementById('health-text');

                    if(healthBarFill) healthBarFill.style.width = `${healthPercentage}%`;
                    if(healthText) healthText.textContent = `${currentHealth}/${maxHealth}`;


                    // Update attributes
                    if (character.atributos) {
                        document.getElementById('attr-str').textContent = character.atributos.forca ?? 'N/A';
                        document.getElementById('attr-dex').textContent = character.atributos.destreza ?? 'N/A';
                        document.getElementById('attr-con').textContent = character.atributos.constituicao ?? 'N/A';
                        document.getElementById('attr-int').textContent = character.atributos.inteligencia ?? 'N/A';
                        document.getElementById('attr-wis').textContent = character.atributos.sabedoria ?? 'N/A';
                        document.getElementById('attr-cha').textContent = character.atributos.carisma ?? 'N/A';
                    }

                    // Update lists using CORRECTED keys
                    const spellList = document.getElementById('spell-list');
                    if (spellList) {
                        spellList.innerHTML = ''; // Clear previous list
                        if (character.magias_conhecidas && character.magias_conhecidas.length > 0) {
                            character.magias_conhecidas.forEach(spell => {
                                const li = document.createElement('li');
                                li.textContent = spell;
                                spellList.appendChild(li);
                            });
                        } else {
                            spellList.innerHTML = '<li>Nenhuma magia conhecida</li>';
                        }
                    }

                    const equipmentList = document.getElementById('equipment-list');
                     if (equipmentList) {
                        equipmentList.innerHTML = ''; // Clear previous list
                        if (character.equipamento && character.equipamento.length > 0) {
                            character.equipamento.forEach(item => {
                                const li = document.createElement('li');
                                li.textContent = item;
                                equipmentList.appendChild(li);
                            });
                        } else {
                            equipmentList.innerHTML = '<li>Nenhum equipamento</li>';
                        }
                    }

                } else {
                     console.warn('Falha ao carregar dados do personagem:', data.error || 'Erro desconhecido');
                }
            })
            .catch(error => {
                console.error('Erro ao carregar informações do personagem:', error);
                // Display error to user?
                 const charDetails = document.querySelector('.character-details');
                 if(charDetails) charDetails.innerHTML = '<p style="color: var(--danger-color);">Erro ao carregar personagem.</p>';
            });
    }
    // --- Fim Funções de Colapsáveis e LoadCharacterInfo ---


    // Renderiza APENAS NOVOS itens no histórico
    function renderHistory(historyItems) {
        if (!Array.isArray(historyItems) || historyItems.length === 0) {

            return;
        }

        const startPrompt = narrativeContainer.querySelector('.start-prompt');
        if (startPrompt) {
            narrativeContainer.removeChild(startPrompt);
        }

        // Renderiza cada NOVO item
        historyItems.forEach(item => {
            if (!item || !item.type || !item.content) {
                 console.warn('Skipping invalid history item:', item);
                 return;
            }
            const messageDiv = document.createElement('div');
            const typeClass = String(item.type).toLowerCase().replace(/[^a-z0-9-_]/g, ''); // Sanitize type for class
            messageDiv.classList.add('message', `message-${typeClass}`); // Ex: message-system, message-command, message-response

            messageDiv.textContent = item.content;

            narrativeContainer.appendChild(messageDiv);
        });

        // Rola para o final para mostrar a mensagem mais recente
        narrativeContainer.scrollTop = narrativeContainer.scrollHeight;
    }

    // Atualiza o indicador de status
    function updateStatus(message) {
        // console.log("Status update:", message); // Debug
        statusIndicator.textContent = message;
    }

    // Inicia o jogo
    function startGame() {
        if (gameStarted) return;
        gameStarted = true; // Mark as started early to prevent double clicks

        updateStatus('Iniciando aventura...');
        if(startGameBtn) startGameBtn.disabled = true;

        fetch('/start')
            .then(response => {
                 if (!response.ok) {
                    // Try to get error message from body
                    return response.json().then(errData => {
                        throw new Error(errData.error || `HTTP error! status: ${response.status}`);
                    }).catch(() => {
                         throw new Error(`HTTP error! status: ${response.status}`);
                    });
                 }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Renderiza o histórico inicial COMPLETO recebido do /start
                    // Precisa limpar o container antes de renderizar o histórico inicial
                    narrativeContainer.innerHTML = '';
                    renderHistory(data.history);
                    loadCharacterInfo();

                    commandInput.disabled = false;
                    sendCommandBtn.disabled = false;
                    commandInput.focus();
                    updateStatus('Aventura iniciada! Digite seu comando.');

                    const startPrompt = document.querySelector('.start-prompt');
                    if (startPrompt) startPrompt.style.display = 'none';
                    if (startGameBtn) startGameBtn.style.display = 'none';

                } else {
                    throw new Error(data.error || 'Falha ao iniciar o jogo no servidor.');
                }
            })
            .catch(error => {
                console.error('Erro ao iniciar jogo:', error);
                updateStatus(`Erro ao iniciar: ${error.message}. Tente recarregar.`);
                if(startGameBtn) startGameBtn.disabled = false;
                gameStarted = false; // Reset state
            });
    }

    // Envia um comando
    function sendCommand() {
        const command = commandInput.value.trim();

        if (!command || processingCommand || !gameStarted) return;

        processingCommand = true;
        commandInput.disabled = true;
        sendCommandBtn.disabled = true;
        updateStatus('Enviando comando...');
        commandInput.value = '';

        const frontendCommandId = `fe_${Date.now()}`;

        fetch('/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command, id: frontendCommandId }) // Passando ID frontend
        })
        .then(response => {
             if (!response.ok) {
                return response.json().then(errData => {
                    throw new Error(errData.error || `HTTP error! status: ${response.status}`);
                }).catch(() => {
                    throw new Error(`HTTP error! status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                if (data.ended) {
                    renderHistory(data.history);
                    endGame("Sessão terminada.");
                } else if (data.processing && data.command_id) {
                    updateStatus('Processando comando...');
                    startPolling(data.command_id);
                } else {
                     throw new Error("Resposta inválida do servidor ao enviar comando.");
                }
            } else {
                throw new Error(data.error || 'Erro desconhecido retornado pelo servidor.');
            }
        })
        .catch(error => {
            console.error('Erro ao enviar comando:', error);
            updateStatus(`Erro: ${error.message}. Tente novamente.`);
            renderHistory([{ type: 'error', content: `Falha ao enviar comando: ${error.message}` }]);
            processingCommand = false;
            commandInput.disabled = false;
            sendCommandBtn.disabled = false;
            commandInput.focus();
        });
    }
    function startPolling(commandId) {
        console.log(`Polling started for command ID: ${commandId}`);
        // Limpa qualquer polling anterior
        clearInterval(pollingInterval);
        pollingInterval = null; // Reset interval ID

        let attempts = 0;
        const maxAttempts = 30; // Limit polling duration (e.g., 30 * 2s = 1 minute)

        const poll = () => {
            attempts++;
            if (attempts > maxAttempts) {
                console.error(`Polling timeout for command ${commandId}`);
                updateStatus('Tempo limite excedido ao buscar resposta. Tente novamente.');
                clearInterval(pollingInterval);
                pollingInterval = null;
                processingCommand = false;
                commandInput.disabled = false;
                sendCommandBtn.disabled = false;
                return;
            }

            fetch(`/status/${commandId}`)
                .then(response => {
                     if (!response.ok) {
                         console.warn(`Polling status check failed (HTTP ${response.status}) for ${commandId}. Attempt ${attempts}.`);
                         if (response.status === 404) throw new Error("Status não encontrado (ID inválido?).");
                         return null; // Indicate temporary failure, retry later
                     }
                    return response.json();
                })
                .then(data => {
                    if (!data) return; // Skip if fetch failed temporarily

                    if (data.success) {
                        if (data.processing) {
                            updateStatus(data.message || 'Processando...');
                        } else {
                            // Processamento completo!
                            console.log(`Polling complete for ${commandId}`);
                            clearInterval(pollingInterval);
                            pollingInterval = null;
                            processingCommand = false;

                            // Renderiza as *novas* partes do histórico recebidas
                            if (data.history_additions && data.history_additions.length > 0) {
                                renderHistory(data.history_additions);
                            } else {
                                console.warn("Processing complete but no history additions received.");
                            }

                            loadCharacterInfo(); // Atualiza info do personagem após turno
                            updateStatus('Aguardando seu próximo comando...');
                            // Re-enable input
                            commandInput.disabled = false;
                            sendCommandBtn.disabled = false;
                            commandInput.focus();

                        }
                    } else {
                        // Erro retornado pelo /status (ex: erro durante processamento no backend)
                        throw new Error(data.error || 'Erro ao verificar status.');
                    }
                })
                .catch(error => {
                    console.error(`Erro no polling para ${commandId}:`, error);
                    clearInterval(pollingInterval);
                    pollingInterval = null;
                    processingCommand = false;
                    updateStatus(`Erro ao buscar resposta: ${error.message}.`);
                     // Renderiza erro no histórico
                     renderHistory([{ type: 'error', content: `Erro ao buscar resultado: ${error.message}` }]);
                    commandInput.disabled = false;
                    sendCommandBtn.disabled = false;
                });
        };

        poll();
        pollingInterval = setInterval(poll, POLLING_INTERVAL_MS);
    }

    function endGame(finalMessage = "A aventura terminou.") {
        console.log("Game ending.");
        gameStarted = false;
        processingCommand = false;
        clearInterval(pollingInterval);
        pollingInterval = null;

        commandInput.disabled = true;
        sendCommandBtn.disabled = true;
        updateStatus(finalMessage);
    }

    // --- Event Listeners ---
    if (startGameBtn) {
        startGameBtn.addEventListener('click', startGame);
    } else {
         console.warn("Botão 'start-game-btn' não encontrado.");
    }

    if (sendCommandBtn) {
        sendCommandBtn.addEventListener('click', sendCommand);
    }

    if (commandInput) {
        commandInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter' || event.keyCode === 13) {
                 event.preventDefault();
                 sendCommand();
            }
        });
    }

    suggestions.forEach(suggestion => {
        suggestion.addEventListener('click', function() {
            if (gameStarted && !processingCommand) {
                // Usa 'data-command' se existir, senão textContent
                const suggestedCommand = this.dataset.command || this.textContent;
                commandInput.value = suggestedCommand;
                commandInput.focus();
            }
        });
    });

    // --- Inicialização ---
    updateStatus('Pronto para iniciar a aventura.');
    commandInput.disabled = true;
    sendCommandBtn.disabled = true;
    loadCharacterInfo(); // Carrega info inicial do personagem

});