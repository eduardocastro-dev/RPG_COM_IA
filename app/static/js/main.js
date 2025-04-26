// static/js/main.js

document.addEventListener('DOMContentLoaded', function () {
    const narrativeContainer = document.getElementById('narrative-container');
    const commandInput = document.getElementById('command-input');
    const sendCommandBtn = document.getElementById('send-command-btn');
    const startGameBtn = document.getElementById('start-game-btn');
    const statusIndicator = document.getElementById('status-indicator');
    const typingIndicator = document.getElementById('typing-indicator');
    const suggestions = document.querySelectorAll('.suggestion');

    let gameStarted = false;
    let processingCommand = false;
    let pollingInterval = null;
    const POLLING_INTERVAL_MS = 2000;

    const collapsibles = document.querySelectorAll('.collapsible-header');
    collapsibles.forEach(header => {
        header.addEventListener('click', function () {
            const parent = this.parentElement;
            parent.classList.toggle('active');
            const icon = this.querySelector('.fa-chevron-down, .fa-chevron-up');
            if (icon) {
                icon.classList.toggle('fa-chevron-down');
                icon.classList.toggle('fa-chevron-up');
            }
        });
    });

    function appendMessage(type, content) {
        const msg = document.createElement('div');
        msg.classList.add('message');
        msg.classList.add(`message-${type}`);
        msg.innerHTML = content;
        narrativeContainer.appendChild(msg);
        narrativeContainer.scrollTop = narrativeContainer.scrollHeight;
    }

    function startPolling(commandId) {
        if (pollingInterval) clearInterval(pollingInterval);

        pollingInterval = setInterval(() => {
            fetch(`/status/${commandId}`)
                .then(response => response.json())
                .then(data => {
                    if (!data.success && !data.processing) {
                        clearInterval(pollingInterval);
                        pollingInterval = null;
                        statusIndicator.textContent = 'Erro ao processar.';
                        statusIndicator.className = 'status-indicator status-error';
                        return;
                    }

                    if (!data.processing) {
                        clearInterval(pollingInterval);
                        pollingInterval = null;
                        statusIndicator.textContent = 'Pronto para o próximo comando';
                        statusIndicator.className = 'status-indicator status-ready';
                        processingCommand = false;

                        if (data.history_additions && Array.isArray(data.history_additions)) {
                            data.history_additions.forEach(msg => appendMessage(msg.type, msg.content));
                        }
                    } else {
                        typingIndicator.style.display = 'inline-block';
                    }
                })
                .catch(error => {
                    console.error('Erro no polling:', error);
                    clearInterval(pollingInterval);
                    pollingInterval = null;
                    statusIndicator.textContent = 'Erro de conexão.';
                    statusIndicator.className = 'status-indicator status-error';
                });
        }, POLLING_INTERVAL_MS);
    }

    startGameBtn.addEventListener('click', function () {
        if (gameStarted || processingCommand) return;

        statusIndicator.textContent = 'Iniciando aventura...';
        statusIndicator.className = 'status-indicator status-processing';

        fetch('/start')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    gameStarted = true;
                    statusIndicator.textContent = 'Aventura iniciada!';
                    statusIndicator.className = 'status-indicator status-ready';

                    if (data.history && Array.isArray(data.history)) {
                        data.history.forEach(msg => appendMessage(msg.type, msg.content));
                    }

                    commandInput.disabled = false;
                    sendCommandBtn.disabled = false;
                } else {
                    statusIndicator.textContent = 'Erro ao iniciar.';
                    statusIndicator.className = 'status-indicator status-error';
                }
            })
            .catch(error => {
                console.error('Erro ao iniciar o jogo:', error);
                statusIndicator.textContent = 'Erro de conexão.';
                statusIndicator.className = 'status-indicator status-error';
            });
    });

    sendCommandBtn.addEventListener('click', function () {
        if (!gameStarted || processingCommand) return;
        const command = commandInput.value.trim();
        if (!command) return;

        processingCommand = true;
        typingIndicator.style.display = 'inline-block';
        statusIndicator.textContent = 'Processando comando...';
        statusIndicator.className = 'status-indicator status-processing';

        const payload = {
            command: command
        };

        fetch('/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.processing && data.command_id) {
                    startPolling(data.command_id);
                } else {
                    processingCommand = false;
                    statusIndicator.textContent = 'Erro ao enviar comando';
                    statusIndicator.className = 'status-indicator status-error';
                }
            })
            .catch(error => {
                console.error('Erro ao enviar comando:', error);
                processingCommand = false;
                statusIndicator.textContent = 'Erro de conexão.';
                statusIndicator.className = 'status-indicator status-error';
            });

        commandInput.value = '';
    });

    suggestions.forEach(suggestion => {
        suggestion.addEventListener('click', function () {
            if (!gameStarted || processingCommand) return;
            const command = this.dataset.command;
            commandInput.value = command;
            sendCommandBtn.click();
        });
    });

    function getAttributeSafe(attributes, attrName) {
        // Caso o atributo exista exatamente como solicitado
        if (attributes[attrName] !== undefined) {
            return attributes[attrName];
        }

        // Busca case-insensitive
        for (const key in attributes) {
            if (key.toLowerCase() === attrName.toLowerCase() ||
                key.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "") ===
                attrName.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")) {
                return attributes[key];
            }
        }

        return 'N/A';
    }

    function loadCharacterInfo() {
        fetch('/character')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const character = data.character;
                    document.getElementById('char-class').textContent = character.classe || 'N/A';
                    document.getElementById('char-race').textContent = character.raca || 'N/A';
                    document.getElementById('char-level').textContent = character.nivel || 'N/A';

                    const maxHealth = character.pv_maximo || 0;
                    const currentHealth = character.pv_atual || 0;
                    const healthPercentage = maxHealth > 0 ? (currentHealth / maxHealth) * 100 : 0;
                    const healthBarFill = document.getElementById('health-bar-fill');
                    const healthText = document.getElementById('health-text');

                    if (healthBarFill) healthBarFill.style.width = `${healthPercentage}%`;
                    if (healthText) healthText.textContent = `${currentHealth}/${maxHealth}`;

                    // Modifique esta parte no loadCharacterInfo() para usar os nomes corretos dos atributos
                    if (character.atributos) {
                        document.getElementById('attr-str').textContent = getAttributeSafe(character.atributos, "Força") ?? 'N/A';
                        document.getElementById('attr-dex').textContent = getAttributeSafe(character.atributos, "Destreza") ?? 'N/A';
                        document.getElementById('attr-con').textContent = getAttributeSafe(character.atributos, "Constituição") ?? 'N/A';
                        document.getElementById('attr-int').textContent = getAttributeSafe(character.atributos, "Inteligência") ?? 'N/A';
                        document.getElementById('attr-wis').textContent = getAttributeSafe(character.atributos, "Sabedoria") ?? 'N/A';
                        document.getElementById('attr-cha').textContent = getAttributeSafe(character.atributos, "Carisma") ?? 'N/A';
                    }

                    const spellList = document.getElementById('spell-list');
                    if (spellList) {
                        spellList.innerHTML = '';
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
                        equipmentList.innerHTML = '';
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
                }
            })
            .catch(error => {
                console.error('Erro ao carregar informações do personagem:', error);
            });
    }

    loadCharacterInfo();
});