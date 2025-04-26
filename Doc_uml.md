# Documentação UML - RPG_COM_IA

## Visão Geral do Sistema

Este documento apresenta a modelagem UML do sistema RPG_COM_IA, um jogo de RPG solo baseado em D&D 5e que utiliza múltiplos agentes de IA através da biblioteca CrewAI.

## Diagrama de Componentes

```mermaid
graph TD
    subgraph Interface["Interface Web"]
        HTML["HTML/CSS/JS"]
    end
    
    subgraph Servidor["Servidor Flask"]
        APP["app.py"]
    end
    
    subgraph Motor["Motor CrewAI"]
        MAIN["main.py"]
    end
    
    subgraph Agentes["Agentes"]
        ORQ["Orquestrador"]
        MES["Mestre"]
        MUN["Mundo"]
        NPC["NPCs"]
        REG["Regras"]
        NAR["Narrador"]
        COM["Combate"]
    end
    
    subgraph Dados["Dados"]
        CHAR["personagem.json"]
    end
    
    HTML --> |HTTP| APP
    APP --> |Python Calls| MAIN
    MAIN --> ORQ
    ORQ --> MES
    ORQ --> MUN
    ORQ --> NPC
    ORQ --> REG
    ORQ --> NAR
    ORQ --> COM
    APP <--> CHAR
```

## Diagrama de Classes

```mermaid
classDiagram
    class Agent {
        +name: String
        +role: String
        +goal: String
        +backstory: String
        +verbose: Boolean
        +allow_delegation: Boolean
        +tools: List
        +execute_task(task)
    }
    
    class Orchestrator {
        +context: String
        +determine_agent()
        +process_command(command)
    }
    
    class GameMaster {
        +create_narrative()
        +advance_story()
    }
    
    class WorldAgent {
        +describe_environment()
        +handle_environment_interaction()
    }
    
    class NPCAgent {
        +manage_npcs()
        +create_dialogue()
        +determine_npc_actions()
    }
    
    class RulesAgent {
        +apply_dnd_rules()
        +calculate_modifiers()
        +validate_actions()
    }
    
    class CombatAgent {
        +manage_combat_state: Boolean
        +initiative_order: List
        +enemies: Dictionary
        +roll_dice(dice_type)
        +process_attack(attacker, target)
        +calculate_damage(roll, modifiers)
        +generate_loot()
    }
    
    class NarratorAgent {
        +integrate_contributions()
        +format_response()
    }
    
    class Character {
        +name: String
        +class: String
        +race: String  
        +level: Integer
        +attributes: Dictionary
        +hp_max: Integer
        +hp_current: Integer
        +ac: Integer
        +known_spells: List
        +equipment: List
        +languages: List
        +update_status(new_status)
    }
    
    class RandomEventSystem {
        +base_chance: Float
        +current_chance: Float
        +roll_for_event()
        +increase_chance()
        +generate_event()
    }
    
    class FlaskServer {
        +command_queue: List
        +processed_commands: Dictionary
        +character: Character
        +game_state: Dictionary
        +serve_index()
        +get_character()
        +start_game()
        +process_command(command)
        +get_status(command_id)
    }
    
    Agent <|-- Orchestrator
    Agent <|-- GameMaster
    Agent <|-- WorldAgent
    Agent <|-- NPCAgent
    Agent <|-- RulesAgent
    Agent <|-- CombatAgent
    Agent <|-- NarratorAgent
    
    Orchestrator --> GameMaster
    Orchestrator --> WorldAgent
    Orchestrator --> NPCAgent
    Orchestrator --> RulesAgent
    Orchestrator --> CombatAgent
    Orchestrator --> NarratorAgent
    
    FlaskServer --> Orchestrator
    FlaskServer --> Character
    FlaskServer --> RandomEventSystem
```

## Diagrama de Sequência: Processamento de Comando

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Flask as FlaskServer
    participant Queue as CommandQueue
    participant Orchestrator
    participant Agents as SpecializedAgents
    participant Narrator
    
    User->>Browser: Insere comando
    Browser->>Flask: POST /command
    Flask->>Queue: Adiciona comando
    Flask-->>Browser: Retorna command_id
    Browser->>Flask: Polling /status/{command_id}
    
    Flask->>Orchestrator: process_command(command)
    Orchestrator->>Orchestrator: determine_agent()
    
    alt Modo Exploração
        Orchestrator->>Agents: WorldAgent.describe_environment()
    else Interação com NPC
        Orchestrator->>Agents: NPCAgent.create_dialogue()
    else Combate
        Orchestrator->>Agents: CombatAgent.process_attack()
        Agents->>Agents: roll_dice()
        Agents->>Agents: calculate_damage()
    end
    
    Orchestrator->>Narrator: integrate_contributions()
    Narrator-->>Orchestrator: formatted_response
    
    Orchestrator-->>Flask: response
    Flask->>Queue: Atualiza status do comando
    Flask-->>Browser: Retorna resposta
    Browser-->>User: Exibe resposta
```

## Diagrama de Sequência: Sistema de Eventos Aleatórios

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Flask as FlaskServer
    participant Orchestrator
    participant EventSystem as RandomEventSystem
    participant Agents as SpecializedAgents
    
    User->>Browser: Envia comando
    Browser->>Flask: POST /command
    Flask->>Orchestrator: process_command()
    
    Orchestrator->>EventSystem: roll_for_event()
    
    alt Evento Ativado
        EventSystem->>EventSystem: increase_chance()
        EventSystem->>EventSystem: generate_event()
        EventSystem-->>Orchestrator: event_type, event_details
        
        alt Encontro Hostil
            Orchestrator->>Agents: CombatAgent.initialize_combat()
        else Encontro Amigável
            Orchestrator->>Agents: NPCAgent.create_dialogue()
        else Descoberta Ambiental
            Orchestrator->>Agents: WorldAgent.describe_discovery()
        end
    else Sem Evento
        EventSystem->>EventSystem: increase_chance()
        EventSystem-->>Orchestrator: no_event
        Orchestrator->>Agents: Process normal command
    end
    
    Orchestrator-->>Flask: response
    Flask-->>Browser: Retorna resposta
    Browser-->>User: Exibe resposta
```

## Diagrama de Atividades: Fluxo de Combate

```mermaid
stateDiagram-v2
    [*] --> VerificarInicioCombate
    
    VerificarInicioCombate --> IniciarCombate: Comando de ataque ou encontro hostil
    VerificarInicioCombate --> ProcessarComandoNormal: Outro comando
    
    ProcessarComandoNormal --> [*]
    
    IniciarCombate --> DeterminarIniciativa
    DeterminarIniciativa --> ProcessarTurnoJogador
    
    ProcessarTurnoJogador --> RolarAtaque: Ataque
    ProcessarTurnoJogador --> AplicarMagia: Magia
    ProcessarTurnoJogador --> OutraAcao: Outra ação
    
    RolarAtaque --> VerificarAcerto
    VerificarAcerto --> CalcularDano: Acerto
    VerificarAcerto --> ResultadoErro: Erro
    
    CalcularDano --> AplicarDano
    AplicarDano --> VerificarEstadoInimigo
    ResultadoErro --> VerificarEstadoInimigo
    
    AplicarMagia --> VerificarAcerto
    OutraAcao --> VerificarEstadoInimigo
    
    VerificarEstadoInimigo --> ProcessarTurnoInimigo: Inimigo vivo
    VerificarEstadoInimigo --> FinalizarCombate: Todos inimigos derrotados
    
    ProcessarTurnoInimigo --> InimigoAtaca
    InimigoAtaca --> RolarAtaqueInimigo
    RolarAtaqueInimigo --> VerificarAcertoInimigo
    
    VerificarAcertoInimigo --> CalcularDanoInimigo: Acerto
    VerificarAcertoInimigo --> ResultadoErroInimigo: Erro
    
    CalcularDanoInimigo --> AplicarDanoJogador
    AplicarDanoJogador --> VerificarEstadoJogador
    ResultadoErroInimigo --> VerificarEstadoJogador
    
    VerificarEstadoJogador --> ProximoTurno: Jogador vivo
    VerificarEstadoJogador --> GameOver: Jogador derrotado
    
    ProximoTurno --> ProcessarTurnoJogador
    
    FinalizarCombate --> GerarRecompensas
    GerarRecompensas --> AtualizarStatusJogador
    AtualizarStatusJogador --> [*]
    
    GameOver --> [*]
```

## Diagrama de Estados: Estados do Jogo

```mermaid
stateDiagram-v2
    [*] --> Iniciando
    
    Iniciando --> Exploracao: Jogo iniciado
    
    Exploracao --> Combate: Encontro hostil / Ataque
    Exploracao --> Dialogo: Encontro NPC
    Exploracao --> Descoberta: Investigar ambiente
    
    Combate --> Exploracao: Combate vencido
    Combate --> GameOver: Personagem derrotado
    
    Dialogo --> Exploracao: Diálogo encerrado
    Dialogo --> Combate: NPC se torna hostil
    
    Descoberta --> Exploracao: Descoberta processada
    
    GameOver --> [*]
```

## Diagrama Entidade-Relacionamento

```mermaid
erDiagram
    CHARACTER {
        string nome
        string classe
        string raca
        int nivel
        json atributos
        int pv_maximo
        int pv_atual
        int ca
        array magias_conhecidas
        array equipamento
        array idiomas
    }
    
    GAME_STATE {
        string current_location
        string current_scene
        boolean in_combat
        array active_npcs
        json environment_details
        float event_chance
    }
    
    NPC {
        string nome
        string tipo
        int nivel
        int pv_atual
        int ca
        json atributos
        array acoes
        string atitude
    }
    
    COMBAT_STATE {
        array initiative_order
        json enemies
        int current_round
        string current_turn
    }
    
    EVENT {
        string tipo
        string descricao
        json detalhes
        array consequencias
    }
    
    CHARACTER ||--o{ GAME_STATE : "exists in"
    GAME_STATE ||--o{ NPC : "contains"
    GAME_STATE ||--o{ EVENT : "triggers"
    GAME_STATE ||--o{ COMBAT_STATE : "may have"
    COMBAT_STATE }|--|| NPC : "involves"
```

## Requisitos do Sistema

### Requisitos Funcionais

1. **RF01** - O sistema deve permitir ao usuário criar e controlar um personagem D&D 5e.
2. **RF02** - O sistema deve processar comandos em linguagem natural do usuário em tempo real.
3. **RF03** - O sistema deve simular combates baseados nas regras D&D 5e.
4. **RF04** - O sistema deve gerar eventos aleatórios durante a exploração.
5. **RF05** - O sistema deve fornecer descrições detalhadas do ambiente.
6. **RF06** - O sistema deve simular diálogos com NPCs.
7. **RF07** - O sistema deve aplicar as regras do D&D 5e para todas as ações.
8. **RF08** - O sistema deve gerenciar o inventário e status do personagem.
9. **RF09** - O sistema deve gerar recompensas após combates vencidos.

### Requisitos Não-Funcionais

1. **RNF01** - O sistema deve responder a comandos em menos de 10 segundos.
2. **RNF02** - O sistema deve fornecer feedback visual durante o processamento.
3. **RNF03** - A interface deve ser responsiva e funcionar em diferentes dispositivos.
4. **RNF04** - O sistema deve manter estado entre sessões.
5. **RNF05** - O sistema deve tratar adequadamente erros de conexão.

## Implementação

### Tecnologias Utilizadas

- **Backend**: Python, Flask, CrewAI
- **APIs**: OpenAI API (GPT)
- **Frontend**: HTML, CSS, JavaScript puro
- **Persistência**: JSON

### Estrutura de Arquivos

```
Estrutura do Projeto RPG_COM_IA
RPG_COM_IA/
├── .idea/
├── .venv/
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css   # Estilos
│   │   └── js/
│   │       └── main.js     # Lógica frontend
│   ├── templates/
│   │   └── index.html      # Interface do usuário
│   ├── __init__.py
│   ├── app.py              # Servidor Flask
│   ├── main.py             # Motor CrewAI e agentes 
│   └── personagem.json     # Dados do personagem
├── .env                    # Variáveis de ambiente (API keys)
├── README.md               # Documentação
└── requirements.txt      
```

## Configuração e Instalação

1. **Pré-requisitos**:
   - Python 3.12+
   - Conta OpenAI com API key

2. **Instalação**:
   ```bash
   git clone https://github.com/eduardocastro-dev/RPG_COM_IA.git
   cd RPG_COM_IA
   pip install flask crewai langchain-openai python-dotenv
   ```

3. **Configuração**:
   - Crie um arquivo `.env` com sua chave API:
     ```
     OPENAI_API_KEY="sua_chave_api_aqui"
     ```

4. **Execução**:
   ```bash
   python app.py
   ```

## API RESTful

| Endpoint | Método | Descrição | Parâmetros |
|---------|--------|-----------|------------|
| `/` | GET | Página inicial | - |
| `/character` | GET | Obter dados do personagem | - |
| `/start` | GET | Iniciar jogo | - |
| `/command` | POST | Enviar comando | `command` (texto) |
| `/status/<command_id>` | GET | Verificar status do comando | `command_id` |

## Extensões e Melhorias Futuras

1. Implementação de múltiplos cenários e campanhas
2. Sistema de persistência de jogos salvos
3. Geração de mapas visuais
4. Suporte a múltiplos personagens (grupo)
5. Customização de campanhas pelo usuário
6. Interface de voz para comandos
7. Sistema de progressão e experiência expandido
