# D&D Solo com CrewAI 🎲🧙‍♂️

Um sistema de RPG solo baseado em D&D 5e que utiliza múltiplos agentes de IA especializados através da biblioteca CrewAI para criar uma experiência de jogo imersiva e dinâmica.

## 📖 Visão Geral

Este projeto implementa um sistema de aventura solo para D&D 5e, onde um jogador pode explorar a "Cripta do Coração Negro" como o mago Alion. A arquitetura principal utiliza o conceito de "agentes especializados", cada um com um papel específico na experiência narrativa, todos coordenados por um Orquestrador Principal.

### Diagrama de Arquitetura

```
┌─────────────────┐
│  Orquestrador   │
│    Principal    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│                                                     │
├─────────┬─────────┬─────────┬─────────┬─────────┬───┴─────┐
│ Agente  │ Agente  │ Agente  │ Agente  │ Agente  │ Agente  │
│ Mestre  │ Mundo   │  NPCs   │ Regras  │Narrativo│ Combate │
└─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
                           │
                           ▼
                    ┌─────────────────┐
                    │   Interface     │
                    │   do Usuário    │
                    └─────────────────┘
```

## 🧩 Agentes Especializados

O sistema utiliza sete agentes com papéis bem definidos:

1. **Orquestrador Principal**: Coordena todos os agentes especializados, decidindo quais devem ser acionados em cada momento.

2. **Agente Mestre**: Supervisiona a narrativa e decide a direção da história.

3. **Agente Mundo**: Especialista em descrições ambientais detalhadas e atmosféricas.

4. **Agente NPCs**: Dá vida aos personagens não-jogadores com personalidades distintas.

5. **Agente Regras**: Aplica as mecânicas do sistema D&D 5e com precisão.

6. **Agente Narrador**: Cria a narrativa final integrando as contribuições dos outros agentes.

7. **Agente Combate**: Especialista em sequências de ação, calculando danos e narrando cenas de batalha.

## 🛠️ Requisitos

- Python 3.8+
- Dependências (instale via pip):
  - crewai
  - langchain_openai
  - json (biblioteca padrão)

## 🔑 Configuração

1. Clone este repositório
2. Instale as dependências:
   ```
   pip install crewai langchain_openai
   ```
3. Configure sua chave API da OpenAI no ambiente:
   ```
   export OPENAI_API_KEY=sua_chave_aqui
   ```
4. Crie um arquivo `personagem.json` na pasta raiz com os dados do seu personagem

## 📝 Exemplo de Personagem JSON

Crie um arquivo `personagem.json` com o seguinte formato:

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
  "pv_atual": 28,
  "pv_maximo": 28,
  "magias_conhecidas": [
    "Mísseis Mágicos", 
    "Escudo Arcano", 
    "Bola de Fogo", 
    "Raio de Gelo",
    "Identificação"
  ],
  "equipamento": [
    "Cajado Arcano", 
    "Grimório", 
    "Bolsa de Componentes", 
    "Poção de Cura", 
    "Varinha da Guerra"
  ]
}
```

## 🚀 Uso

Execute o script principal:

```bash
python main.py
```

O jogo iniciará com uma introdução à Cripta do Coração Negro. Digite suas ações como Alion e veja como a história se desenvolve! Para sair, digite "sair", "exit" ou "quit".

## 📊 Fluxo do Sistema

1. **Análise da Ação**: O Orquestrador analisa a ação do jogador e decide quais agentes são necessários.
2. **Coleta de Contribuições**: Os agentes selecionados contribuem com sua especialidade.
3. **Integração Narrativa**: O Narrador integra todas as contribuições em uma narrativa coesa.
4. **Saída para o Jogador**: A narrativa final é apresentada ao jogador.

## 🎮 Exemplo de Interação

```
🎲 D&D 5e Solo com IA: Cripta do Coração Negro
🧙‍♂️ Você é Alion, um mago humano explorando as profundezas da sinistra Cripta do Coração Negro.

📜 Introdução:
[Descrição inicial da cripta]

🎮 O que Alion faz?
> Lanço Mãos Flamejantes no esqueleto

📜 Cena:
[Descrição da cena de combate]
```

## ✨ Recursos Adicionais

- **Cache de Contexto**: O sistema mantém um histórico das últimas interações para garantir continuidade narrativa.
- **Tratamento de Erros**: Mecanismos para garantir que o jogo continue mesmo em caso de falhas nas respostas da IA.
- **Integração Multi-agente**: As contribuições dos diferentes especialistas são combinadas para uma experiência rica.

## 🔧 Personalização

Você pode personalizar:

- Os agentes e suas descrições
- A aventura e cenário
- O personagem do jogador
- O modelo LLM utilizado (alterando a linha `llm = ChatOpenAI(...)`)

## 📝 Notas

- Este sistema foi projetado para aventuras solo, mas pode ser adaptado para múltiplos jogadores.
- O desempenho depende da qualidade do modelo LLM utilizado.
- Considere ajustar o `temperature` para balancear criatividade e consistência narrativa.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests com melhorias.

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

---

Criado com CrewAI e LangChain 🧠✨