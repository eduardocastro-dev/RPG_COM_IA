// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Elementos principais
    const narrativeContainer = document.getElementById('narrative-container');
    const commandInput = document.getElementById('command-input');
    const sendCommandBtn = document.getElementById('send-command-btn');
    const startGameBtn = document.getElementById('start-game-btn');
    const statusIndicator = document.getElementById('status-indicator');
    const suggestions = document.querySelectorAll('.suggestion');

    // Variáveis de estado
    let gameStarted = false;
    let processingCommand = false;
    let currentCommandId = null;
    let pollingInterval = null;

    // Verifica colapsáveis
    const collapsibles = document.querySelectorAll('.collapsible-header');
    collapsibles.forEach(header => {
        header.addEventListener('click', function() {
            const parent = this.parentElement;
            parent.classList.toggle('active');
            // Opcional: Gerenciar ícone de expandir/colapsar
            const icon = this.querySelector('.collapse-icon');
            if (icon) {
                icon.textContent = parent.classList.contains('active') ? '-' : '+';
            }
        });
    });

    // Carrega informações do personagem inicialmente e a cada atualização relevante
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

                    // Atualiza informações básicas
                    document.getElementById('char-class').textContent = character.classe || 'N/A';
                    document.getElementById('char-race').textContent = character.raca || 'N/A';
                    document.getElementById('char-level').textContent = character.nivel || 'N/A';

                    // Atualiza barra de vida
                    const healthPercentage = (character.pv_atual / character.pv_maximo) * 100;
                    document.getElementById('health-bar-fill').style.width = `${healthPercentage}%`;
                    document.getElementById('health-text').textContent = `${character.pv_atual}/${character.pv_maximo}`;

                    // Atualiza atributos
                    document.getElementById('attr-str').textContent = character.atributos.forca;
                    document.getElementById('attr-dex').textContent = character.atributos.destreza;
                    document.getElementById('attr-con').textContent = character.atributos.constituicao;
                    document.getElementById('attr-int').textContent = character.atributos.inteligencia;
                    document.getElementById('attr-wis').textContent = character.atributos.sabedoria;
                    document.getElementById('attr-cha').textContent = character.atributos.carisma;

                    // Atualiza listas de magias e equipamento
                    const spellList = document.getElementById('spell-list');
                    spellList.innerHTML = ''; // Limpa a lista anterior
                    if (character.magias_conhecidas && character.magias_conhecidas.length > 0) {
                        character.magias_conhecidas.forEach(spell => {
                            const li = document.createElement('li');
                            li.textContent = spell;
                            spellList.appendChild(li);
                        });
                    } else {
                        spellList.innerHTML = '<li>Nenhuma magia conhecida</li>';
                    }


                    const equipmentList = document.getElementById('equipment-list');
                    equipmentList.innerHTML = ''; // Limpa a lista anterior
                    if (character.equipamento && character.equipamento.length > 0) {
                        character.equipamento.forEach(item => {
                            const li = document.createElement('li');
                            li.textContent = item;
                            equipmentList.appendChild(li);
                        });
                    } else {
                         equipmentList.innerHTML = '<li>Nenhum equipamento</li>';
                    }

                } else {
                     console.warn('Falha ao carregar dados do personagem:', data.error || 'Erro desconhecido');
                     // Poderia exibir uma mensagem para o usuário aqui
                }
            })
            .catch(error => console.error('Erro ao carregar informações do personagem:', error));
    }

    // Inicia o jogo
    function startGame() {
        // Evita inícios múltiplos
        if (gameStarted) return;

        updateStatus('Iniciando aventura...');
        startGameBtn.disabled = true; // Desabilita botão enquanto inicia

        fetch('/start')
            .then(response => {
                 if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    gameStarted = true;
                    renderHistory(data.history);
                    loadCharacterInfo(); // Carrega info do personagem no início

                    // Habilita a entrada de comandos
                    commandInput.disabled = false;
                    sendCommandBtn.disabled = false;
                    commandInput.focus();

                    updateStatus('Aventura iniciada! Digite seu comando.');

                    // Remove o botão de início ou o esconde
                    const startPrompt = document.querySelector('.start-prompt');
                    if (startPrompt) {
                       startPrompt.style.display = 'none'; // Esconde em vez de remover, caso precise depois
                    }
                     if (startGameBtn) {
                        startGameBtn.style.display = 'none'; // Esconde o botão principal
                     }

                } else {
                    throw new Error(data.error || 'Falha ao iniciar o jogo no servidor.');
                }
            })
            .catch(error => {
                console.error('Erro ao iniciar jogo:', error);
                updateStatus(`Erro ao iniciar aventura: ${error.message}. Tente recarregar a página.`);
                startGameBtn.disabled = false; // Reabilita o botão em caso de erro
            });
    }

    // Envia um comando
    function sendCommand() {
        const command = commandInput.value.trim();

        if (!command || processingCommand || !gameStarted) return;

        processingCommand = true;
        commandInput.disabled = true;
        sendCommandBtn.disabled = true;
        updateStatus('Processando comando...');

        // Adiciona o comando do jogador ao histórico imediatamente (feedback visual)
        renderHistory([{ type: 'player', content: command }]);

        // Limpa o campo de entrada
        commandInput.value = '';

        // Gera um ID para o comando (se necessário, mas a API pode gerenciar)
        currentCommandId = Date.now(); // Simples ID baseado no tempo

        fetch('/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Adicionar CSRF token se necessário
                // 'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                command: command,
                // id: currentCommandId // O backend pode não precisar disso se gerenciar estado por sessão
            })
        })
        .then(response => {
             if (!response.ok) {
                // Tenta ler o erro do corpo da resposta se disponível
                return response.json().then(errData => {
                    throw new Error(errData.error || `HTTP error! status: ${response.status}`);
                }).catch(() => {
                    // Se não conseguir ler o corpo JSON, lança erro genérico
                    throw new Error(`HTTP error! status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Renderiza a resposta do jogo (parte do histórico)
                renderHistory(data.history);
                loadCharacterInfo(); // Atualiza info do personagem após comando

                if (data.ended) {
                    // Jogo terminou
                    endGame(data.final_message || "A aventura chegou ao fim.");
                } else {
                     // Comando processado, pronto para o próximo
                     processingCommand = false;
                     commandInput.disabled = false;
                     sendCommandBtn.disabled = false;
                     commandInput.focus();
                     updateStatus('Aguardando seu próximo comando...');
                    // Não precisa de polling se a resposta for síncrona
                    // Se a resposta indicar processamento assíncrono:
                    // if (data.processing_id) {
                    //     startPolling(data.processing_id);
                    // } else { ... (código acima) }
                }
            } else {
                throw new Error(data.error || 'Erro desconhecido retornado pelo servidor.');
            }
        })
        .catch(error => {
            console.error('Erro ao enviar comando:', error);
            updateStatus(`Erro ao processar comando: ${error.message}. Tente novamente.`);
            // Renderiza mensagem de erro no histórico? Opcional.
            // renderHistory([{ type: 'error', content: `Erro: ${error.message}` }]);
            processingCommand = false;
            commandInput.disabled = false;
            sendCommandBtn.disabled = false;
            commandInput.focus(); // Permite tentar novamente
        });
    }

    // --- Polling não é mais necessário se a resposta do comando for síncrona ---
    // Se precisar de polling (comandos que demoram muito no backend):
    /*
    function startPolling(commandId) {
        // Limpa qualquer polling anterior
        clearInterval(pollingInterval);
        updateStatus('Aguardando resultado do comando...');

        pollingInterval = setInterval(() => {
            fetch(`/status/${commandId}`) // Endpoint de status
                .then(response => {
                     if (!response.ok) {
                         throw new Error(`HTTP error! status: ${response.status}`);
                     }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        if (data.processing) {
                            // Ainda processando, talvez atualize a mensagem
                            updateStatus(data.message || 'Processando...');
                        } else {
                            // Processamento completo
                            clearInterval(pollingInterval);
                            processingCommand = false;
                            commandInput.disabled = false;
                            sendCommandBtn.disabled = false;
                            commandInput.focus();

                            // Renderiza o histórico final e atualiza char info
                            renderHistory(data.history);
                            loadCharacterInfo();
                            updateStatus('Aguardando seu próximo comando...');

                            if (data.ended) {
                                endGame(data.final_message || "A aventura chegou ao fim.");
                            }
                        }
                    } else {
                        throw new Error(data.error || 'Erro ao verificar status.');
                    }
                })
                .catch(error => {
                    console.error('Erro ao verificar status:', error);
                    clearInterval(pollingInterval);
                    processingCommand = false; // Libera para tentar de novo
                    commandInput.disabled = false;
                    sendCommandBtn.disabled = false;
                    updateStatus(`Erro ao obter resultado: ${error.message}. Tente novamente.`);
                });
        }, 2000); // Verifica a cada 2 segundos
    }
    */

    // Renderiza o histórico da sessão
    // Modificado para *adicionar* ao histórico existente, em vez de limpar
    function renderHistory(historyItems) {
        if (!Array.isArray(historyItems)) {
            console.warn('renderHistory recebeu dados que não são um array:', historyItems);
            return;
        }

        // Limpa qualquer conteúdo de início, se ainda existir
        const startPrompt = narrativeContainer.querySelector('.start-prompt');
        if (startPrompt) {
            narrativeContainer.removeChild(startPrompt);
        }

        // Renderiza cada novo item do histórico
        historyItems.forEach(item => {
            const messageDiv = document.createElement('div');
            // Adiciona classe base 'message' e classe específica do tipo
            messageDiv.classList.add('message', `message-${item.type}`); // Ex: message-narrative, message-player

            // Usa textContent para segurança contra XSS
            messageDiv.textContent = item.content;

            narrativeContainer.appendChild(messageDiv);
        });

        // Rola para o final para mostrar a mensagem mais recente
        narrativeContainer.scrollTop = narrativeContainer.scrollHeight;
    }

    // Atualiza o indicador de status
    function updateStatus(message) {
        statusIndicator.textContent = message;
    }

    // Finaliza o jogo
    function endGame(finalMessage = "A aventura terminou.") {
        gameStarted = false;
        processingCommand = false;
        clearInterval(pollingInterval); // Garante que qualquer polling pare

        // Desabilita entrada de comandos permanentemente (para esta sessão)
        commandInput.disabled = true;
        sendCommandBtn.disabled = true;

        // Atualiza o status final
        updateStatus(finalMessage);

        // Opcional: Adicionar uma mensagem final clara no container da narrativa
        // A resposta do comando final já deve ter feito isso via renderHistory
        // Mas podemos adicionar uma linha extra se quisermos:
        // const endDiv = document.createElement('div');
        // endDiv.className = 'message message-system message-end'; // Classes CSS para estilização
        // endDiv.textContent = "--- FIM DO JOGO ---";
        // narrativeContainer.appendChild(endDiv);
        // narrativeContainer.scrollTop = narrativeContainer.scrollHeight;

        // Opcional: Mostrar um botão de "Jogar Novamente" que recarregue a página
        // const restartButton = document.createElement('button');
        // restartButton.textContent = 'Jogar Novamente';
        // restartButton.className = 'restart-button'; // Classe para estilizar
        // restartButton.onclick = () => window.location.reload();
        // // Adicionar o botão em algum lugar apropriado, talvez abaixo do input
        // document.querySelector('.command-area').appendChild(restartButton); // Exemplo
    }

    // --- Event Listeners ---

    // Botão Iniciar Jogo
    if (startGameBtn) {
        startGameBtn.addEventListener('click', startGame);
    } else {
         // Se o botão não existe, talvez o jogo deva começar automaticamente
         // ou já estar em andamento (verificar estado no backend?)
         console.warn("Botão 'start-game-btn' não encontrado.");
         // Poderia tentar iniciar o jogo se não encontrar o botão e o jogo não tiver começado
         // if (!gameStarted) { startGame(); } // Cuidado com loops indesejados
    }


    // Botão Enviar Comando
    if (sendCommandBtn) {
        sendCommandBtn.addEventListener('click', sendCommand);
    }

    // Input de Comando (Enter para enviar)
    if (commandInput) {
        commandInput.addEventListener('keypress', function(event) {
            // Verifica se a tecla pressionada é Enter (key code 13 ou 'Enter')
            if (event.key === 'Enter' || event.keyCode === 13) {
                 event.preventDefault(); // Previne o comportamento padrão do Enter (ex: submit de form)
                 sendCommand(); // Chama a função de enviar comando
            }
        });
    }

    // Botões de Sugestão
    suggestions.forEach(suggestion => {
        suggestion.addEventListener('click', function() {
            // Só permite usar sugestões se o jogo estiver rodando e não processando
            if (gameStarted && !processingCommand) {
                const suggestedCommand = this.getAttribute('data-command') || this.textContent;
                commandInput.value = suggestedCommand;
                commandInput.focus(); // Foca no input para que o usuário possa editar ou enviar
                // Opcional: Enviar o comando diretamente ao clicar na sugestão
                // sendCommand();
            }
        });
    });

    // --- Inicialização ---
    updateStatus('Pronto para iniciar a aventura.');
    commandInput.disabled = true; // Desabilitado até o jogo começar
    sendCommandBtn.disabled = true;
    loadCharacterInfo(); // Carrega info do personagem ao carregar a página

});

// Função auxiliar para pegar cookies (se necessário para CSRF)
/*
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
*/