# D&D Solo com CrewAI e Flask 🎲🧙‍♂️💻

Um sistema de RPG solo baseado em D&D 5e que utiliza múltiplos agentes de IA especializados através da biblioteca CrewAI para criar uma experiência de jogo imersiva e dinâmica, servido por uma interface web com Flask.

## 📖 Visão Geral

Neste projeto, você explora a **Cripta do Coração Negro** como o mago **Alion**. A arquitetura é baseada em **agentes especializados**, coordenados por um Orquestrador Principal, cada um responsável por uma parte da narrativa, regras, ou interação com o mundo.

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

1. **Orquestrador Principal**: Coordena os demais agentes com base nas ações do jogador e contexto.
2. **Agente Mestre**: Supervisiona a narrativa geral da história.
3. **Agente Mundo**: Cria descrições ambientais e sensoriais detalhadas.
4. **Agente NPCs**: Dá vida aos personagens não-jogadores com motivações e diálogos próprios.
5. **Agente Regras**: Aplica as regras do D&D 5e com precisão.
6. **Agente Combate**: Gerencia cenas de combate, calcula danos e narra ações.
7. **Agente Narrador**: Integra todas as contribuições e gera a resposta final ao jogador.

## ✨ Recursos da Aplicação Web

- Interface construída com HTML/CSS/JS puro.
- Exibição do personagem (sidebar).
- Campo de entrada de comandos com sugestões de ações.
- Visualização da narrativa com diferenciação entre ações do jogador e respostas da IA.
- Processamento assíncrono com polling para respostas em tempo real.
- Indicador de status (iniciando, processando, aguardando comando...).

## 📊 Fluxo da Aplicação Web

1. Navegador carrega os arquivos `index.html`, `style.css`, `main.js`.
2. O JS requisita os dados do personagem via `/character`.
3. Jogador inicia a aventura via `/start`.
4. Comandos são enviados para `/command` e processados pela fila `command_queue`.
5. O servidor responde com atualizações através do endpoint `/status/<command_id>`.

## 🛠️ Requisitos

- Python 3.12+
- Flask
- crewai
- langchain-openai
- python-dotenv

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

```
🎲 D&D 5e Solo com IA: Cripta do Coração Negro
🧙‍♂️ Você é Alion, um mago humano explorando a cripta...

🎮 O que Alion faz?
> Lanço Mãos Flamejantes no esqueleto

📜 Cena:
[Descrição da cena de combate]
```

## 🔧 Personalização

Você pode personalizar:

- Os agentes (funções e prompts em `main.py`)
- A aventura e cenário
- O personagem (`personagem.json`)
- O modelo LLM usado (gpt-3.5-turbo, gpt-4...)
- A interface (`index.html`, `style.css`, `main.js`)

## 📝 Notas

- A versão atual usa variáveis globais no Flask, o que **não é ideal para múltiplos usuários simultâneos**.
- O desempenho depende da resposta da API da OpenAI.
- Monitore os custos com uso de tokens.
- Ajuste `temperature` para controlar criatividade vs. consistência narrativa.

## 🤝 Contribuições

Contribuições são bem-vindas! Abra issues ou envie pull requests.

## 📄 Licença

Licenciado sob a licença MIT.
