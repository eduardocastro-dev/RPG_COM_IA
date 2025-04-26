# D&D Solo com CrewAI e Flask 🎲🧙‍♂️💻

Um sistema de RPG solo baseado em D&D 5e que utiliza múltiplos agentes de IA especializados através da biblioteca CrewAI para criar uma experiência de jogo imersiva e dinâmica, servido por uma interface web com Flask.

## 📖 Visão Geral

Neste projeto, você explora a **Cripta do Coração Negro** como o mago **Alion**. A arquitetura é baseada em **agentes especializados**, coordenados por um Orquestrador Inteligente, cada um responsável por uma parte específica da narrativa, regras, ou interação com o mundo.

### Diagrama de Arquitetura

```
┌─────────────────┐
│  Navegador Web  │  ← HTML/CSS/JS
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  Servidor Flask │  ← app.py
└────────┬────────┘
         │ Python Calls
         ▼
┌─────────────────┐
│  Motor CrewAI   │  ← main.py
└─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ Agentes: Orquestrador, Mestre, Mundo, NPCs, Regras, │
│ Narrador, Combate                                   │
└─────────────────────────────────────────────────────┘
```

## 🧩 Agentes Especializados

O sistema utiliza **sete agentes** com funções bem definidas:

1. **Orquestrador Inteligente**: Analisa a situação atual e determina dinamicamente qual agente deve liderar a interação, garantindo transições fluidas e naturais durante a narrativa.
2. **Agente Mestre**: Supervisiona a narrativa geral da história.
3. **Agente Mundo**: Cria descrições ambientais e sensoriais detalhadas quando o jogador explora ou faz perguntas sobre o cenário.
4. **Agente NPCs**: Dá vida aos personagens não-jogadores com motivações e diálogos próprios, assumindo o controle quando há interações com personagens.
5. **Agente Regras**: Aplica as regras do D&D 5e com precisão e auxilia nos cálculos baseados na ficha do personagem.
6. **Agente Combate**: Gerencia cenas de combate, calcula danos, executa rolagens automáticas e narra ações em estilo tático.
7. **Agente Narrador**: Integra todas as contribuições e gera a resposta final ao jogador em uma narrativa coesa.

## 🎲 Sistema de Combate Aprimorado

O modo de combate agora apresenta uma experiência mais completa:

- **Transição automática**: O sistema identifica quando o jogador inicia ou entra em combate.
- **Estilo de chat de batalha de D&D**: Narração tática e objetiva com foco nas mecânicas.
- **Rolagens automáticas**: Implementação das rolagens de dados (d20, d8, etc.) no código usando `random` conforme as regras do D&D 5e.
- **Verificações baseadas em atributos**: Os atributos e bônus do personagem são considerados em todos os cálculos.
- **Resolução dinâmica**: Os resultados das rolagens influenciam diretamente os eventos (acertos, falhas, danos).
- **Gerenciamento de inimigos**: O sistema processa automaticamente os ataques e ações dos adversários.
- **Sistema de recompensas**: Geração de loot aleatório após o combate, com diferentes níveis de raridade.

## 🎭 Eventos Aleatórios

- **Encontros dinâmicos**: Chance de aparecimento de NPCs (aliados ou inimigos) de forma aleatória.
- **Probabilidade crescente**: Começa com 5% no primeiro turno e aumenta entre 2,5% e 5% a cada nova interação.
- **Impacto narrativo**: Os encontros alteram o fluxo da narrativa automaticamente, iniciando novos eventos, diálogos ou combates.
- **Tipos variados**: Inclui encontros hostis e amigáveis, integrados naturalmente à história.

## ✨ Recursos da Aplicação Web

- Interface construída com HTML/CSS/JS puro.
- Exibição do personagem (sidebar).
- Campo de entrada de comandos com sugestões de ações.
- Visualização da narrativa com diferenciação entre ações do jogador e respostas da IA.
- Processamento assíncrono com polling para respostas em tempo real.
- Indicador visual de carregamento durante o processamento de comandos.
- Feedback mecânico transparente (resultados das rolagens) integrado à narrativa.
- Tratamento aprimorado de erros de conexão.
- Confirmação ao sair do jogo.
- Indicador de status (iniciando, processando, aguardando comando...).

## 📊 Fluxo da Aplicação Web

1. Navegador carrega os arquivos `index.html`, `style.css`, `main.js`.
2. O JS requisita os dados do personagem via `/character`.
3. Jogador inicia a aventura via `/start`.
4. Comandos são enviados para `/command` e processados pela fila `command_queue`.
5. O servidor responde com atualizações através do endpoint `/status/<command_id>`.
6. Durante o processamento, é exibido um indicador "typing..." para melhor experiência do usuário.

## 🛠️ Requisitos

- Python 3.12+
- Flask
- crewai
- langchain-openai
- python-dotenv
- random (biblioteca padrão, para rolagens de dados)

Instale com:

```bash
pip install flask crewai langchain-openai python-dotenv
```

## 🔑 Configuração

1. Clone o repositório:

   ```bash
   git clone <url-do-repo>
   cd <nome-do-projeto>
   ```

2. Crie um ambiente virtual (opcional):

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # ou .\.venv\Scripts\activate no Windows
   ```

3. Instale as dependências (caso não tenha `requirements.txt`):

   ```bash
   pip install flask crewai langchain-openai python-dotenv
   ```

4. Configure a chave da OpenAI:

   Crie um arquivo `.env` na raiz:

   ```dotenv
   OPENAI_API_KEY="sua_chave_api_aqui"
   ```

5. Crie o arquivo `personagem.json` com o seu personagem.

## 📝 Exemplo de `personagem.json`

```json
{
  "nome": "Alion",
  "classe": "Mago",
  "raca": "Humano",
  "nivel": 5,
  "atributos": {
    "forca": 8,
    "destreza": 14,
    "constituicao": 12,
    "inteligencia": 18,
    "sabedoria": 14,
    "carisma": 10
  },
  "pv_maximo": 28,
  "pv_atual": 28,
  "ca": 12,
  "magias_conhecidas": [
    "Prestidigitação",
    "Raio de Gelo",
    "Luz",
    "Mísseis Mágicos",
    "Sono",
    "Escudo Arcano",
    "Bola de Fogo",
    "Identificação"
  ],
  "equipamento": [
    "Cajado Arcano",
    "Grimório",
    "Bolsa de Componentes",
    "Poção de Cura",
    "Varinha da Guerra",
    "10 PO"
  ],
  "idiomas": ["Comum", "Élfico", "Dracônico"]
}
```

## 🚀 Uso

Para rodar com Flask:

```bash
python app.py
```

Para rodar diretamente com terminal (sem interface):

```bash
python main.py
```

O servidor ficará disponível em `http://127.0.0.1:5000`.

## 🎮 Exemplo de Interação

**Modo Exploração:**
```
🎲 D&D 5e Solo com IA: Cripta do Coração Negro
🧙‍♂️ Você é Alion, um mago humano explorando a cripta...

🎮 O que Alion faz?
> Examinar a sala em busca de armadilhas

📜 [Agente Mundo] A sala é pouco iluminada, com apenas algumas tochas bruxuleantes nas paredes de pedra antiga. O ar é pesado e empoeirado. Você nota vários ladrilhos no chão que parecem ligeiramente desalinhados. Ao examinar mais de perto, identifica pequenos orifícios nas paredes, provavelmente para dardos ou outro tipo de projetil. Esta sala certamente tem armadilhas.
```

**Modo Combate:**
```
🎮 O que Alion faz?
> Lanço Raio de Gelo no esqueleto

⚔️ [Agente Combate] Alion ergue sua mão, concentrando energia arcana...
🎲 Rolagem de ataque: 15 (d20) + 6 (mod INT + bônus) = 21
✅ Acerto! (CA do Esqueleto: 13)
🎲 Dano: 3d8 = 5 + 3 + 7 = 15 de dano de frio
❄️ O esqueleto é atingido em cheio pelo raio de gelo, que cristaliza seus ossos. Ele cambaleia, severamente danificado.

O esqueleto avança, brandindo sua cimitarra...
🎲 Rolagem de ataque do esqueleto: 11 (d20) + 4 (mod) = 15
✅ Acerto! (Sua CA: 12)
🎲 Dano: 1d6 + 2 = 5 de dano cortante
💥 A lâmina enferrujada corta seu ombro. Seus PV atuais: 23/28
```

**Evento Aleatório:**
```
🎮 O que Alion faz?
> Continuo pelo corredor escuro

🎲 [Evento Aleatório Ativado - Chance: 15%]
👤 [Agente NPCs] Enquanto avança pelo corredor, você ouve passos apressados. Uma figura encapuzada surge das sombras - um halfling com vestes manchadas de sangue.

"Psiu, mago! Por aqui, rápido!" ele sussurra, acenando freneticamente. "As criaturas estão vindo, e não quero estar aqui quando chegarem!"
```

## 🔧 Personalização

Você pode personalizar:

- Os agentes (funções e prompts em `main.py`)
- A aventura e cenário
- O personagem (`personagem.json`)
- O modelo LLM usado (gpt-3.5-turbo, gpt-4...)
- A interface (`index.html`, `style.css`, `main.js`)
- Probabilidades e tipos de eventos aleatórios
- Tabelas de loot e recompensas

## 📝 Notas

- A versão atual usa variáveis globais no Flask, o que **não é ideal para múltiplos usuários simultâneos**.
- O desempenho depende da resposta da API da OpenAI.
- Monitore os custos com uso de tokens.
- Ajuste `temperature` para controlar criatividade vs. consistência narrativa.
- O sistema de eventos aleatórios aumenta a imprevisibilidade e a rejogabilidade da aventura.

## 🤝 Contribuições

Contribuições são bem-vindas! Abra issues ou envie pull requests.

## 📄 Licença

Licenciado sob a licença MIT.