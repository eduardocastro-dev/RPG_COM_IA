import json
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# Configuração da LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.8)

# Carrega a ficha do personagem
with open('personagem.json', 'r') as file:
    ficha = json.load(file)

# --------------------------
# Definição dos Agentes
# --------------------------

# Orquestrador Principal - Coordena todos os outros agentes
orquestrador = Agent(
    name="Orquestrador",
    role="Coordenador Principal",
    goal="Coordenar todos os agentes especializados e manter a coerência da aventura",
    backstory="""Todas as respostas devem ser escritas em português do Brasil.
Você é o coordenador central que decide quais agentes especializados devem ser acionados 
em cada momento da aventura. Sua função é garantir uma experiência coesa e imersiva,
delegando tarefas aos agentes apropriados conforme necessário.""",
    llm=llm
)

# Agente Mestre - Supervisiona a narrativa
mestre = Agent(
    name="Mestre",
    role="Supervisor Narrativo",
    goal="Avaliar a ação do jogador e decidir a direção da narrativa",
    backstory="""Todas as respostas devem ser escritas em português do Brasil.
Você supervisiona a narrativa para garantir coesão, continuidade e progressão da aventura.
Trabalha diretamente com o Orquestrador para determinar quais elementos narrativos precisam ser desenvolvidos.""",
    llm=llm
)

# Agente Narrativo - Cria a descrição dramática
narrador = Agent(
    name="Narrador",
    role="Dramatizador",
    goal="Criar narrativa envolvente e consistente com a história",
    backstory="""Todas as respostas devem ser escritas em português do Brasil.
Você narra os acontecimentos do jogo com estilo, tensão e conexão com o arco da aventura.
Sua função é transformar decisões mecânicas em momentos memoráveis e envolventes.""",
    llm=llm
)

# Agente de Mundo - Especialista em ambientação
mundo = Agent(
    name="Mundo",
    role="Ambientalista",
    goal="Descrever o ambiente com detalhes sensoriais e atmosféricos",
    backstory="""Todas as respostas devem ser escritas em português do Brasil.
Você cria descrições ricas dos ambientes, focando em detalhes sensoriais, atmosfera e elementos
que podem ser relevantes para a exploração. Sua função é fazer o mundo parecer vivo e tangível.""",
    llm=llm
)

# Agente de NPCs - Dá vida aos personagens não-jogadores
npcs = Agent(
    name="NPCs",
    role="Interpretador de Personagens",
    goal="Dar vida e personalidade aos NPCs do mundo",
    backstory="""Todas as respostas devem ser escritas em português do Brasil.
Você interpreta todos os personagens não-jogadores com personalidades distintas, motivações
claras e reações realistas. Sua função é fazer cada interação social parecer genuína.""",
    llm=llm
)

# Agente de Regras - Aplica as mecânicas do sistema
regras = Agent(
    name="Regras",
    role="Especialista em Sistema D&D 5e",
    goal="Aplicar regras com fidelidade e equilíbrio",
    backstory="""Todas as respostas devem ser escritas em português do Brasil.
Você conhece profundamente o sistema D&D 5e e aplica as regras de forma justa e consistente.
Sua função é resolver qualquer situação mecânica mantendo o jogo fluindo.""",
    llm=llm
)

# Novo Agente de Combate - Especialista em sequências de ação
combate = Agent(
    name="Combate",
    role="Mestre de Batalha",
    goal="Narrar cenas de combate dinâmicas e calcular danos com precisão",
    backstory="""Todas as respostas devem ser escritas em português do Brasil.
Você é especializado em transformar rolagens de dados e mecânicas de combate em cenas de
ação cinematográficas. Você descreve os golpes, danos causados e sofridos, e mantém o
registro do estado dos combatentes durante conflitos.""",
    llm=llm
)

# Cache para manter o histórico da aventura
cache = []


def adicionar_ao_cache(mensagem):
    cache.append(mensagem)
    if len(cache) > 10:  # Aumentado para manter mais contexto
        cache.pop(0)


def contexto_cache():
    if not cache:
        return "Nenhum turno anterior registrado."
    return "\n".join([f"Turno {i + 1}: {msg}" for i, msg in enumerate(cache)])


# --------------------------
# Sistema de Orquestração
# --------------------------

def executar_turno(comando_usuario):
    contexto = contexto_cache()

    # Fase 1: Orquestrador analisa o comando e decide quais agentes serão necessários
    analise_orquestrador = Task(
        description=f"""Todas as respostas devem ser em português do Brasil.
Contexto da aventura: Um mago humano chamado Alion está explorando a Cripta do Coração Negro.
Histórico recente:
{contexto}

Ação do jogador: "{comando_usuario}"

Analise a ação do jogador e determine quais agentes especializados devem ser invocados:
- Mestre: Para avaliar a direção narrativa (sempre utilizado)
- Mundo: Se for necessária descrição detalhada do ambiente
- NPCs: Se houver interação com personagens não-jogadores
- Regras: Se for necessário aplicar mecânicas específicas do sistema
- Combate: Se a ação envolver lutas, danos ou conflitos físicos
- Narrador: Para finalização dramática (sempre utilizado)

Formato da resposta:
{{
  "agentes_necessarios": ["mestre", "narrador", ...outros conforme necessário],
  "contexto_adicional": "Informações relevantes para os agentes considerarem"
}}
""",
        agent=orquestrador,
        expected_output="JSON com agentes necessários e contexto adicional"
    )

    crew_orquestradora = Crew(
        agents=[orquestrador],
        tasks=[analise_orquestrador],
        verbose=False
    )

    # Executa a orquestração inicial
    resultado_orquestrador = crew_orquestradora.kickoff()

    try:
        # Parseia o resultado do orquestrador
        decisao = json.loads(str(resultado_orquestrador).strip())
        agentes_necessarios = decisao["agentes_necessarios"]
        contexto_adicional = decisao["contexto_adicional"]
    except:
        # Fallback em caso de erro na resposta
        agentes_necessarios = ["mestre", "narrador"]
        contexto_adicional = "Mantenha o foco na ação do jogador."

    # Fase 2: Coleta análises e contribuições dos agentes selecionados
    contribuicoes = {}
    agentes_selecionados = []
    tarefas = []

    # Sempre inclui o Mestre
    if "mestre" in agentes_necessarios:
        agentes_selecionados.append(mestre)
        tarefa_mestre = Task(
            description=f"""Todas as respostas devem ser em português do Brasil.
Contexto da aventura: Um mago humano chamado Alion está explorando a Cripta do Coração Negro.
Histórico recente:
{contexto}

Ação do jogador: "{comando_usuario}"
Contexto adicional: {contexto_adicional}

Como Mestre, avalie esta ação e forneça direcionamento narrativo.
Concentre-se apenas no aspecto de desenvolvimento da história e progressão da aventura.
""",
            agent=mestre,
            expected_output="Direcionamento narrativo para esta ação"
        )
        tarefas.append(tarefa_mestre)

    # Adiciona o agente Mundo se necessário
    if "mundo" in agentes_necessarios:
        agentes_selecionados.append(mundo)
        tarefa_mundo = Task(
            description=f"""Todas as respostas devem ser em português do Brasil.
Contexto da aventura: Um mago humano chamado Alion está explorando a Cripta do Coração Negro.
Histórico recente:
{contexto}

Ação do jogador: "{comando_usuario}"
Contexto adicional: {contexto_adicional}

Como especialista em ambientação, descreva o cenário atual com foco em detalhes 
sensoriais e elementos que podem ser relevantes para a ação do jogador.
""",
            agent=mundo,
            expected_output="Descrição detalhada do ambiente"
        )
        tarefas.append(tarefa_mundo)

    # Adiciona o agente NPCs se necessário
    if "npcs" in agentes_necessarios:
        agentes_selecionados.append(npcs)
        tarefa_npcs = Task(
            description=f"""Todas as respostas devem ser em português do Brasil.
Contexto da aventura: Um mago humano chamado Alion está explorando a Cripta do Coração Negro.
Histórico recente:
{contexto}

Ação do jogador: "{comando_usuario}"
Contexto adicional: {contexto_adicional}

Como especialista em personagens não-jogadores, desenvolva as reações, 
diálogos e comportamentos dos NPCs envolvidos nesta cena.
""",
            agent=npcs,
            expected_output="Reações e diálogos dos NPCs"
        )
        tarefas.append(tarefa_npcs)

    # Adiciona o agente Regras se necessário
    if "regras" in agentes_necessarios:
        agentes_selecionados.append(regras)
        tarefa_regras = Task(
            description=f"""Todas as respostas devem ser em português do Brasil.
Contexto da aventura: Um mago humano chamado Alion está explorando a Cripta do Coração Negro.
Histórico recente:
{contexto}

Ação do jogador: "{comando_usuario}"
Contexto adicional: {contexto_adicional}

Como especialista no sistema D&D 5e, determine quais regras se aplicam a esta situação,
quais testes devem ser feitos e os resultados mecânicos das ações.
""",
            agent=regras,
            expected_output="Aplicação de regras e resolução mecânica"
        )
        tarefas.append(tarefa_regras)

    # Adiciona o agente Combate se necessário
    if "combate" in agentes_necessarios:
        agentes_selecionados.append(combate)
        tarefa_combate = Task(
            description=f"""Todas as respostas devem ser em português do Brasil.
Contexto da aventura: Um mago humano chamado Alion está explorando a Cripta do Coração Negro.
Histórico recente:
{contexto}

Ação do jogador: "{comando_usuario}"
Contexto adicional: {contexto_adicional}

Como especialista em combate, descreva a sequência de ação, calcule os danos causados e sofridos,
e mantenha o registro do estado dos combatentes. Seja cinematográfico nas descrições dos golpes,
defesas e efeitos especiais de magias ou habilidades.
""",
            agent=combate,
            expected_output="Resolução detalhada do combate com descrição de danos"
        )
        tarefas.append(tarefa_combate)

    # Executa as tarefas dos agentes selecionados
    if agentes_selecionados and tarefas:
        crew_especialistas = Crew(
            agents=agentes_selecionados,
            tasks=tarefas,
            verbose=False
        )

        resultados_especialistas = crew_especialistas.kickoff()

        # Interpreta os resultados como uma lista correspondente às tarefas
        if isinstance(resultados_especialistas, list):
            for i, resultado in enumerate(resultados_especialistas):
                tipo_agente = agentes_necessarios[i]
                contribuicoes[tipo_agente] = str(resultado).strip()
        else:
            # Se apenas um agente foi usado
            contribuicoes[agentes_necessarios[0]] = str(resultados_especialistas).strip()

    # Fase 3: Narrador integra todas as contribuições em uma narrativa coesa
    # Sempre incluímos o narrador para finalização

    # Prepara o contexto para o narrador com todas as contribuições coletadas
    contexto_narrador = "\n\n".join([
        f"Contribuição do {agente.capitalize()}: {contribuicoes.get(agente.lower(), 'Não solicitado')}"
        for agente in ["mestre", "mundo", "npcs", "regras", "combate"]
        if agente in contribuicoes
    ])

    tarefa_narrador = Task(
        description=f"""Todas as respostas devem ser em português do Brasil.
Contexto da aventura: Um mago humano chamado Alion está explorando a Cripta do Coração Negro.
Histórico recente:
{contexto}

Ação do jogador: "{comando_usuario}"
Contexto adicional: {contexto_adicional}

Contribuições dos especialistas:
{contexto_narrador}

Como Narrador, integre todas essas contribuições em uma narrativa coesa e envolvente.
Sua resposta será apresentada diretamente ao jogador, então certifique-se de que seja
completa e dramática, incorporando todos os elementos relevantes das diferentes análises.
""",
        agent=narrador,
        expected_output="Narrativa final integrada e envolvente"
    )

    crew_narrativa = Crew(
        agents=[narrador],
        tasks=[tarefa_narrador],
        verbose=False
    )

    resultado_final = crew_narrativa.kickoff()

    # Adiciona ao cache para contexto futuro
    adicionar_ao_cache(f"> {comando_usuario}\n{resultado_final}")

    return resultado_final


# CLI
if __name__ == "__main__":
    print("🎲 D&D 5e Solo com IA: Cripta do Coração Negro")
    print("🧙‍♂️ Você é Alion, um mago humano explorando as profundezas da sinistra Cripta do Coração Negro.")

    # Introdução da aventura com todos os agentes
    intro = executar_turno("Observar o ambiente ao entrar na cripta.")
    print(f"\n📜 Introdução:\n{intro}")

    # Loop principal do jogo
    while True:
        comando = input("\n🎮 O que Alion faz?\n> ")
        if comando.lower() in ['sair', 'exit', 'quit']:
            print("⚰️ A sessão termina aqui. Obrigado por jogar!")
            break

        resposta = executar_turno(comando)
        print(f"\n📜 Cena:\n{resposta}")