import json
import random
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from typing import Dict, List, Tuple, Optional

# Configuração da LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.8)

# Carrega a ficha do personagem
with open('personagem.json', 'r') as file:
    ficha = json.load(file)

# --------------------------
# Sistema de Dados e Mecânicas D&D
# --------------------------

class DiceSystem:
    @staticmethod
    def roll(dice_notation: str) -> Tuple[int, List[int]]:
        """
        Rola dados no formato padrão D&D (exemplo: 2d6, 1d20, 3d8+5)
        Retorna: (total, [valores individuais])
        """
        # Parse da notação de dados
        parts = dice_notation.lower().split('d')
        if len(parts) != 2:
            raise ValueError(f"Formato de dado inválido: {dice_notation}")
        
        # Lidar com modificadores (ex: 1d20+5)
        mod = 0
        if '+' in parts[1]:
            dice_parts = parts[1].split('+')
            parts[1] = dice_parts[0]
            mod = int(dice_parts[1])
        elif '-' in parts[1]:
            dice_parts = parts[1].split('-')
            parts[1] = dice_parts[0]
            mod = -int(dice_parts[1])
        
        # Converter para inteiros
        try:
            num_dice = int(parts[0]) if parts[0] else 1
            dice_type = int(parts[1])
        except ValueError:
            raise ValueError(f"Formato de dado inválido: {dice_notation}")
        
        # Realizar as rolagens
        results = [random.randint(1, dice_type) for _ in range(num_dice)]
        total = sum(results) + mod
        
        return total, results

    @staticmethod
    def attack_roll(bonus: int) -> Tuple[int, int, bool]:
        """
        Realiza uma rolagem de ataque D&D 5e
        Retorna: (total, valor do d20, crítico?)
        """
        d20_roll = random.randint(1, 20)
        total = d20_roll + bonus
        is_critical = d20_roll == 20
        return total, d20_roll, is_critical
    
    @staticmethod
    def check_roll(ability_mod: int, proficiency: int = 0) -> Tuple[int, int]:
        """
        Realiza uma rolagem de teste de habilidade D&D 5e
        Retorna: (total, valor do d20)
        """
        d20_roll = random.randint(1, 20)
        total = d20_roll + ability_mod + proficiency
        return total, d20_roll
    
    @staticmethod
    def save_roll(save_mod: int) -> Tuple[int, int]:
        """
        Realiza uma rolagem de resistência D&D 5e
        Retorna: (total, valor do d20)
        """
        d20_roll = random.randint(1, 20)
        total = d20_roll + save_mod
        return total, d20_roll


class CharacterManager:
    """Gerencia dados da ficha de personagem e cálculos"""
    
    @staticmethod
    def get_ability_modifier(ability_score: int) -> int:
        """Calcula o modificador de uma habilidade"""
        return (ability_score - 10) // 2
    
    @staticmethod
    def calculate_attack_bonus(character: Dict, weapon_name: str = None) -> int:
        """Calcula o bônus de ataque para uma arma ou magia"""
        # Para simplificar, usamos o mod de INT se for um ataque de magia
        if weapon_name and "magia" in weapon_name.lower():
            return CharacterManager.get_ability_modifier(character["atributos"]["Inteligência"]) + character["proficiencia"]
        # Para armas corpo a corpo, usamos força
        else:
            return CharacterManager.get_ability_modifier(character["atributos"]["Força"]) + character["proficiencia"]
    
    @staticmethod
    def calculate_spell_dc(character: Dict) -> int:
        """Calcula a CD de magia"""
        int_mod = CharacterManager.get_ability_modifier(character["atributos"]["Inteligência"])
        return 8 + int_mod + character["proficiencia"]
    
    @staticmethod
    def get_skill_modifier(character: Dict, skill_name: str) -> int:
        """Obtém o modificador de uma perícia específica"""
        # Mapeia perícias para atributos
        skill_to_ability = {
            "Acrobacia": "Destreza",
            "Arcanismo": "Inteligência",
            "Atletismo": "Força",
            "Atuação": "Carisma",
            "Enganação": "Carisma",
            "Furtividade": "Destreza",
            "História": "Inteligência",
            "Intimidação": "Carisma",
            "Intuição": "Sabedoria",
            "Investigação": "Inteligência",
            "Lidar com Animais": "Sabedoria",
            "Medicina": "Sabedoria",
            "Natureza": "Inteligência",
            "Percepção": "Sabedoria",
            "Persuasão": "Carisma",
            "Prestidigitação": "Destreza",
            "Religião": "Inteligência",
            "Sobrevivência": "Sabedoria"
        }
        
        ability = skill_to_ability.get(skill_name, "Inteligência")  # Default para INT se não encontrar
        ability_mod = CharacterManager.get_ability_modifier(character["atributos"][ability])
        
        # Adiciona bônus de proficiência se tiver
        proficiency_bonus = character["proficiencia"] if skill_name in character.get("pericias", []) else 0
        
        return ability_mod + proficiency_bonus


# --------------------------
# Sistema de Eventos Aleatórios
# --------------------------

class EventSystem:
    def __init__(self):
        self.encounter_chance = 5.0  # Chance inicial de 5%
        self.turn_counter = 0
        self.in_combat = False
        self.current_enemies = []
        self.current_allies = []
    
    def increment_turn(self) -> None:
        """Incrementa o contador de turnos e aumenta a chance de encontro"""
        self.turn_counter += 1
        # Incremento entre 2.5% e 5%
        self.encounter_chance += random.uniform(2.5, 5.0)
    
    def check_random_encounter(self) -> Optional[Dict]:
        """
        Verifica se ocorre um encontro aleatório
        Retorna: None ou um dicionário descrevendo o encontro
        """
        if self.in_combat:
            return None  # Já está em combate, não gerar novos encontros
            
        roll = random.random() * 100  # Porcentagem
        
        if roll <= self.encounter_chance:
            # Ocorreu um encontro! Resetar a chance
            self.encounter_chance = 5.0
            
            # Determinar o tipo de encontro (70% inimigo, 30% aliado)
            encounter_type = "inimigo" if random.random() < 0.7 else "aliado"
            
            if encounter_type == "inimigo":
                # Gerar inimigos apropriados para a Cripta
                enemy_types = [
                    "esqueleto", "zumbi", "sombra", "espectro", 
                    "cultista", "carniçal", "aparição", "ghoul"
                ]
                # Determinar quantidade com base no turno
                quantity = min(1 + self.turn_counter // 3, 4)  # Max 4 inimigos
                
                enemies = []
                for _ in range(max(1, random.randint(1, quantity))):
                    enemy_type = random.choice(enemy_types)
                    hp = random.randint(10, 30)  # HP simplificado
                    enemies.append({
                        "tipo": enemy_type,
                        "hp": hp,
                        "hp_max": hp,
                        "ca": random.randint(10, 14)
                    })
                
                self.current_enemies = enemies
                self.in_combat = True
                
                return {
                    "tipo": "encontro_hostil",
                    "inimigos": enemies,
                    "descricao": f"Encontro com {len(enemies)} {enemy_types[0] if len(enemies) == 1 else 'criaturas'}"
                }
            else:
                # Encontro com aliado
                ally_types = [
                    "aventureiro perdido", "espírito benevolente", 
                    "sobrevivente ferido", "pesquisador arcano"
                ]
                
                ally_type = random.choice(ally_types)
                ally = {
                    "tipo": ally_type,
                    "atitude": random.choice(["amigável", "cauteloso", "desesperado", "sábio"])
                }
                
                self.current_allies.append(ally)
                
                return {
                    "tipo": "encontro_amigavel",
                    "aliado": ally,
                    "descricao": f"Encontro com um {ally_type}"
                }
        
        return None
    
    def end_combat(self) -> None:
        """Finaliza o estado de combate"""
        self.in_combat = False
        self.current_enemies = []


# --------------------------
# Definição dos Agentes
# --------------------------

# Orquestrador Principal - Agora mais inteligente
orquestrador = Agent(
    name="Orquestrador",
    role="Coordenador Principal",
    goal="Analisar contextualmente a situação e determinar qual agente especializado deve assumir o controle",
    backstory="""Todas as respostas devem ser escritas em português do Brasil.
Você é um coordenador central altamente inteligente que analisa a situação atual da aventura,
o histórico recente e a intenção do jogador para determinar qual agente especializado deve
assumir o controle narrativo. Sua função é garantir transições fluidas entre diferentes
especialistas e manter uma experiência coesa e imersiva para o jogador.""",
    llm=llm
)

# Agente Mestre - Supervisiona a narrativa
mestre = Agent(
    name="Mestre",
    role="Supervisor Narrativo",
    goal="Avaliar a ação do jogador e decidir a direção da narrativa",
    backstory="""Todas as respostas devem ser escritas em português do Brasil.
Você supervisiona a narrativa para garantir coesão, continuidade e progressão da aventura.
Trabalha diretamente com o Orquestrador para determinar quais elementos narrativos precisam ser desenvolvidos.
Seu estilo é épico e envolvente, mantendo o tom de uma verdadeira aventura de D&D.""",
    llm=llm
)

# Agente Narrativo - Cria a descrição dramática
narrador = Agent(
    name="Narrador",
    role="Dramatizador",
    goal="Criar narrativa envolvente e consistente com a história",
    backstory="""Todas as respostas devem ser escritas em português do Brasil.
Você narra os acontecimentos do jogo com estilo, tensão e conexão com o arco da aventura.
Sua função é transformar decisões mecânicas em momentos memoráveis e envolventes.
Seu estilo varia conforme o contexto: épico durante exploração e mais tático durante combates.""",
    llm=llm
)

# Agente de Mundo - Especialista em ambientação
mundo = Agent(
    name="Mundo",
    role="Ambientalista",
    goal="Descrever o ambiente com detalhes sensoriais e atmosféricos",
    backstory="""Todas as respostas devem ser escritas em português do Brasil.
Você cria descrições ricas dos ambientes, focando em detalhes sensoriais, atmosfera e elementos
que podem ser relevantes para a exploração. Sua função é fazer o mundo parecer vivo e tangível.
Quando o jogador faz perguntas sobre o ambiente, você assume o controle para fornecer detalhes
imersivos que ajudam a criar uma imagem mental clara do cenário.""",
    llm=llm
)

# Agente de NPCs - Dá vida aos personagens não-jogadores
npcs = Agent(
    name="NPCs",
    role="Interpretador de Personagens",
    goal="Dar vida e personalidade aos NPCs do mundo",
    backstory="""Todas as respostas devem ser escritas em português do Brasil.
Você interpreta todos os personagens não-jogadores com personalidades distintas, motivações
claras e reações realistas. Sua função é fazer cada interação social parecer genuína.
Quando o jogador interage com um NPC, você assume o controle da narração para criar diálogos
autênticos e reações que refletem a personalidade e os objetivos desses personagens.""",
    llm=llm
)

# Agente de Regras - Aplica as mecânicas do sistema
regras = Agent(
    name="Regras",
    role="Especialista em Sistema D&D 5e",
    goal="Aplicar regras com fidelidade e equilíbrio",
    backstory="""Todas as respostas devem ser escritas em português do Brasil.
Você conhece profundamente o sistema D&D 5e e aplica as regras de forma justa e consistente.
Sua função é resolver qualquer situação mecânica mantendo o jogo fluindo.
Você garante que a ficha do personagem seja utilizada corretamente, e que os
modificadores apropriados sejam aplicados em cada situação.""",
    llm=llm
)

# Agente de Combate Aprimorado - Com sistema de rolagem de dados
combate = Agent(
    name="Combate",
    role="Mestre de Batalha",
    goal="Narrar cenas de combate dinâmicas com mecânicas precisas de D&D 5e",
    backstory="""Todas as respostas devem ser escritas em português do Brasil.
Você é especializado em gerenciar encontros de combate seguindo as regras do D&D 5e.
Seu estilo de narração muda para um tom mais tático e objetivo durante combates, similar
a uma mesa de RPG real. Você integra resultados reais de rolagens de dados nas suas descrições,
sempre explicando claramente os resultados e suas consequências. Você mantém o registro do
estado dos combatentes e garante que as ações tenham impacto mecânico adequado.""",
    llm=llm
)


# Cache para manter o histórico da aventura
cache = []
# Sistema de eventos
event_system = EventSystem()


def adicionar_ao_cache(mensagem):
    cache.append(mensagem)
    if len(cache) > 12:  # Aumentado para manter mais contexto
        cache.pop(0)


def contexto_cache():
    if not cache:
        return "Nenhum turno anterior registrado."
    return "\n".join([f"Turno {i + 1}: {msg}" for i, msg in enumerate(cache)])


# --------------------------
# Sistema de Orquestração Aprimorado
# --------------------------

def executar_turno(comando_usuario):
    # Incrementar o contador de turnos e verificar eventos aleatórios
    event_system.increment_turn()
    random_encounter = event_system.check_random_encounter()
    
    contexto = contexto_cache()
    info_estado_jogo = {
        "em_combate": event_system.in_combat,
        "inimigos_atuais": event_system.current_enemies,
        "aliados_atuais": event_system.current_allies
    }
    
    # Contexto adicional para o evento aleatório, se ocorrer
    contexto_evento = ""
    if random_encounter:
        if random_encounter["tipo"] == "encontro_hostil":
            inimigos_str = ", ".join([f"{e['tipo']} (PV: {e['hp']}/{e['hp_max']})" for e in random_encounter["inimigos"]])
            contexto_evento = f"""
EVENTO ALEATÓRIO: Encontro hostil!
Inimigos: {inimigos_str}
Este encontro inicia automaticamente um combate. O jogador deve ser informado e 
a narrativa deve incluir a aparição dos inimigos de forma fluida e surpreendente.
"""
        else:
            contexto_evento = f"""
EVENTO ALEATÓRIO: Encontro com aliado!
Aliado: {random_encounter['aliado']['tipo']} ({random_encounter['aliado']['atitude']})
Este encontro deve ser introduzido na narrativa de forma natural. O NPC pode oferecer
informações, ajuda ou ter seus próprios objetivos na Cripta.
"""

    # Fase 1: Orquestrador inteligente analisa o comando e decide qual agente deve assumir
    analise_orquestrador = Task(
        description=f"""Todas as respostas devem ser em português do Brasil.
Contexto da aventura: Um mago humano chamado Alion está explorando a Cripta do Coração Negro.
Estado atual: {"Em combate" if info_estado_jogo["em_combate"] else "Exploração"}.
Histórico recente:
{contexto}

{contexto_evento}

Ação do jogador: "{comando_usuario}"

ANALISE PROFUNDA DA SITUAÇÃO:
1. Determine a INTENÇÃO principal do jogador (combate, exploração, diálogo, etc.)
2. Identifique qual agente especializado deve LIDERAR a resposta:
   - Combate: Se a ação envolve lutar, atacar ou defender-se
   - Mundo: Se o foco é no ambiente, exploração ou observação do cenário
   - NPCs: Se envolve interagir com personagens não-jogadores
   - Regras: Se requer aplicação específica de regras complexas do D&D
   - Mestre: Se for uma decisão narrativa importante

3. Determine quais agentes AUXILIARES devem contribuir:
   - Sempre inclua o Narrador para produzir o resultado final
   - Inclua o Mestre se houver decisões narrativas
   - Inclua Regras se precisar calcular testes ou aplicar mecânicas

Formato da resposta:
{{
  "agente_lider": "combate|mundo|npcs|regras|mestre",
  "agentes_auxiliares": ["narrador", "mestre", "regras", etc.],
  "análise_situacional": "Breve análise da situação atual",
  "direcionamento": "Instruções específicas para o agente líder"
}}
""",
        agent=orquestrador,
        expected_output="JSON com agente líder, agentes auxiliares e direcionamento"
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
        agente_lider = decisao["agente_lider"].lower()
        agentes_auxiliares = [a.lower() for a in decisao["agentes_auxiliares"]]
        analise_situacional = decisao["análise_situacional"]
        direcionamento = decisao["direcionamento"]
    except:
        # Fallback em caso de erro na resposta
        agente_lider = "mestre"
        agentes_auxiliares = ["narrador", "regras"]
        analise_situacional = "Continuando a aventura."
        direcionamento = "Mantenha o foco na ação do jogador."

    # Certifique-se de que o narrador sempre está incluído
    if "narrador" not in agentes_auxiliares:
        agentes_auxiliares.append("narrador")

    # Fase 2: O agente líder processa a ação principal
    # Criar contexto de regras para qualquer uso de mecânicas
    contexto_regras = ""
    
    # Se estivermos em combate ou entrarmos em combate, preparar o contexto mecânico
    if agente_lider == "combate" or event_system.in_combat or (random_encounter and random_encounter["tipo"] == "encontro_hostil"):
        event_system.in_combat = True
        
        # Preparar as informações sobre o personagem do jogador
        atk_bonus = CharacterManager.calculate_attack_bonus(ficha, "magia")
        spell_dc = CharacterManager.calculate_spell_dc(ficha)
        
        # Informações sobre inimigos atuais
        if event_system.current_enemies:
            inimigos_str = "\n".join([f"- {e['tipo']} (PV: {e['hp']}/{e['hp_max']}, CA: {e['ca']})" for e in event_system.current_enemies])
        else:
            inimigos_str = "Nenhum inimigo ativo."
        
        contexto_regras = f"""
INFORMAÇÕES DE COMBATE:
Personagem do Jogador:
- PV Atual: {ficha.get('pontos_vida_atuais', ficha.get('pontos_vida', 0))}/{ficha.get('pontos_vida', 0)}
- Classe de Armadura: {ficha.get('classe_armadura', 10)}
- Bônus de Ataque Mágico: +{atk_bonus}
- CD de Magia: {spell_dc}

Inimigos:
{inimigos_str}

REGRAS DE COMBATE:
1. Ataques: Rolar 1d20 + bônus contra a CA do alvo
2. Dano: Depende da arma/magia
3. Resistências: Rolar 1d20 + modificador de atributo

Analise a ação do jogador e determine qual mecânica aplicar.
"""

    # Criar a tarefa para o agente líder
    agente_obj = None
    if agente_lider == "combate":
        agente_obj = combate
    elif agente_lider == "mundo":
        agente_obj = mundo
    elif agente_lider == "npcs":
        agente_obj = npcs
    elif agente_lider == "regras":
        agente_obj = regras
    else:
        agente_obj = mestre  # Default para o mestre
    
    tarefa_lider = Task(
        description=f"""Todas as respostas devem ser em português do Brasil.
Contexto da aventura: Um mago humano chamado Alion está explorando a Cripta do Coração Negro.
Histórico recente:
{contexto}

{contexto_evento if contexto_evento else ""}

Ação do jogador: "{comando_usuario}"

Análise situacional: {analise_situacional}
Direcionamento específico: {direcionamento}

{contexto_regras if contexto_regras else ""}

Como agente {agente_lider.upper()}, você foi escolhido como líder para processar esta ação.
Crie uma resposta detalhada focando na sua especialidade, sabendo que o resultado final
será integrado pelo Narrador a outras contribuições. Mantenha seu foco específico.

Se for resposta de COMBATE:
- Use um tom mais direto e tático, similar a uma sessão de RPG
- Faça rolagens explícitas mostrando os resultados
- Inclua consequências mecânicas (dano, condições, etc.)

Se for resposta de MUNDO:
- Descreva o ambiente com detalhes sensoriais e atmosféricos
- Revele elementos interativos que o jogador pode explorar
- Crie uma ambientação imersiva

Se for resposta de NPCS:
- Crie diálogos autênticos e distintos
- Mostre reações realistas às ações do jogador
- Revele sutilmente motivações e personalidades

Se for resposta do MESTRE:
- Avance a narrativa principal
- Tome decisões sobre o rumo da aventura
- Mantenha a coerência com eventos anteriores
""",
        agent=agente_obj,
        expected_output=f"Resposta detalhada como agente {agente_lider}"
    )
    
    crew_lider = Crew(
        agents=[agente_obj],
        tasks=[tarefa_lider],
        verbose=False
    )
    
    resultado_lider = crew_lider.kickoff()
    contribuicao_lider = str(resultado_lider).strip()
    
    # Fase 3: Processamento de rolagens para combate
    # Se estamos em combate, processar rolagens reais
    resultado_mecanico = None
    if agente_lider == "combate" or event_system.in_combat:
        # Analisar o comando para determinar o tipo de ação
        acao_ataque = any(termo in comando_usuario.lower() for termo in [
            "atac", "golpe", "lançar", "magica", "magia", "raio", "disparo", "tiro", "fogo", "gelo"
        ])
        
        acao_defesa = any(termo in comando_usuario.lower() for termo in [
            "defend", "esquiv", "proteg", "escud", "bloque"
        ])
        
        acao_movimento = any(termo in comando_usuario.lower() for termo in [
            "mov", "corr", "salt", "andar", "recuar", "afast", "approx"
        ])
        
        # Se for um ataque, fazer rolagem de dados
        if acao_ataque and event_system.current_enemies:
            atk_bonus = CharacterManager.calculate_attack_bonus(ficha, "magia")
            total_roll, d20_value, critical = DiceSystem.attack_roll(atk_bonus)
            
            # Selecionar alvo (simplificado)
            alvo = event_system.current_enemies[0]  # Primeiro inimigo na lista
            
            hit = total_roll >= alvo["ca"]
            
            # Rolagem de dano (assumindo magia de 1d8 para simplificar)
            if hit:
                damage_total, damage_rolls = DiceSystem.roll("1d8")
                if critical:
                    bonus_damage, _ = DiceSystem.roll("1d8")
                    damage_total += bonus_damage
                
                # Aplicar dano
                alvo["hp"] = max(0, alvo["hp"] - damage_total)
                
                # Verificar se inimigo morreu
                morto = alvo["hp"] <= 0
                
                resultado_mecanico = {
                    "tipo": "ataque",
                    "alvo": alvo["tipo"],
                    "rolagem_ataque": total_roll,
                    "valor_d20": d20_value,
                    "critico": critical,
                    "acerto": hit,
                    "dano": damage_total,
                    "hp_final": alvo["hp"],
                    "morto": morto
                }
                
                # Limpar inimigos mortos
                event_system.current_enemies = [e for e in event_system.current_enemies if e["hp"] > 0]
                
                # Verificar se o combate terminou
                if not event_system.current_enemies:
                    event_system.end_combat()
            else:
                resultado_mecanico = {
                    "tipo": "ataque",
                    "alvo": alvo["tipo"],
                    "rolagem_ataque": total_roll,
                    "valor_d20": d20_value,
                    "critico": False,
                    "acerto": False
                }
        
        elif acao_defesa:
            # Rolagem de defesa (simplificada, usando Destreza)
            dex_mod = CharacterManager.get_ability_modifier(ficha["atributos"]["Destreza"])
            total_roll, d20_value = DiceSystem.check_roll(dex_mod)
            
            resultado_mecanico = {
                "tipo": "defesa",
                "rolagem": total_roll,
                "valor_d20": d20_value,
                "sucesso": total_roll >= 12  # DC arbitrária
            }
    
    # Fase 4: Coletar contribuições dos agentes auxiliares
    contribuicoes = {agente_lider: contribuicao_lider}
    agentes_auxiliares_objs = []
    tarefas_auxiliares = []
    
    # Preparar contexto de rolagem mecânica
    contexto_mecanico = ""
    if resultado_mecanico:
        if resultado_mecanico["tipo"] == "ataque":
            if resultado_mecanico["acerto"]:
                if resultado_mecanico["critico"]:
                    contexto_mecanico = f"""
RESULTADO MECÂNICO: ATAQUE CRÍTICO!
- Rolagem de ataque: {resultado_mecanico["valor_d20"]} (CRÍTICO!) + bônus = {resultado_mecanico["rolagem_ataque"]}
- Alvo: {resultado_mecanico["alvo"]} (CA {alvo["ca"]})
- Dano causado: {resultado_mecanico["dano"]} pontos de vida
- Estado do alvo: {resultado_mecanico["hp_final"]}/{alvo["hp_max"]} PV
- {resultado_mecanico["alvo"]} está {'morto' if resultado_mecanico["morto"] else 'ferido'}
"""
                else:
                    contexto_mecanico = f"""
RESULTADO MECÂNICO: ATAQUE BEM-SUCEDIDO
- Rolagem de ataque: {resultado_mecanico["valor_d20"]} (d20) + bônus = {resultado_mecanico["rolagem_ataque"]}
- Alvo: {resultado_mecanico["alvo"]} (CA {alvo["ca"]})
- Dano causado: {resultado_mecanico["dano"]} pontos de vida
- Estado do alvo: {resultado_mecanico["hp_final"]}/{alvo["hp_max"]} PV
- {resultado_mecanico["alvo"]} está {'morto' if resultado_mecanico["morto"] else 'ferido'}
"""
                if not event_system.current_enemies:
                    contexto_mecanico += """
COMBATE ENCERRADO: Todos os inimigos foram derrotados!
O sistema de combate está sendo encerrado e você voltará ao modo de exploração.
"""
            else:
                contexto_mecanico = f"""
RESULTADO MECÂNICO: ATAQUE FALHOU
- Rolagem de ataque: {resultado_mecanico["valor_d20"]} (d20) + bônus = {resultado_mecanico["rolagem_ataque"]}
- Alvo: {resultado_mecanico["alvo"]} (CA {alvo["ca"]})
- O ataque não acertou o alvo
"""
        elif resultado_mecanico["tipo"] == "defesa":
            if resultado_mecanico["sucesso"]:
                contexto_mecanico = f"""
RESULTADO MECÂNICO: DEFESA BEM-SUCEDIDA
- Rolagem de defesa: {resultado_mecanico["valor_d20"]} (d20) + bônus = {resultado_mecanico["rolagem"]}
- A defesa foi bem-sucedida!
"""
            else:
                contexto_mecanico = f"""
RESULTADO MECÂNICO: DEFESA FALHOU
- Rolagem de defesa: {resultado_mecanico["valor_d20"]} (d20) + bônus = {resultado_mecanico["rolagem"]}
- A defesa não foi eficaz
"""

    # Executar tarefas para cada agente auxiliar
    for agente_nome in agentes_auxiliares:
        if agente_nome == agente_lider:
            continue  # Pulamos o agente líder que já processou
        
        # Escolher o agente correto
        agente_aux = None
        if agente_nome == "narrador":
            agente_aux = narrador
        elif agente_nome == "mestre":
            agente_aux = mestre
        elif agente_nome == "mundo":
            agente_aux = mundo
        elif agente_nome == "npcs":
            agente_aux = npcs
        elif agente_nome == "regras":
            agente_aux = regras
        elif agente_nome == "combate":
            agente_aux = combate
            
        if agente_aux:
            agentes_auxiliares_objs.append(agente_aux)
            tarefa_aux = Task(
                description=f"""Todas as respostas devem ser em português do Brasil.
Contexto da aventura: Um mago humano chamado Alion está explorando a Cripta do Coração Negro.
Histórico recente:
{contexto}

{contexto_evento if contexto_evento else ""}

Ação do jogador: "{comando_usuario}"

{contexto_mecanico if contexto_mecanico else ""}

Contribuição do agente líder ({agente_lider}):
{contribuicao_lider}

Como agente {agente_nome.upper()}, você foi escolhido como auxiliar na resposta.
Sua tarefa é complementar a contribuição do agente líder, adicionando elementos
específicos da sua especialidade. Seja conciso e focado no seu papel específico.

Se você for o NARRADOR:
- Integre todas as contribuições em uma narrativa final coesa
- Mantenha o tom apropriado (épico para exploração, tático para combate)
- Crie transições suaves entre diferentes elementos

Se você for MESTRE, MUNDO, NPCs ou REGRAS:
- Adicione apenas elementos relevantes da sua especialidade
- Seja breve e complementar ao agente líder
- Não repita informações já fornecidas
""",
                agent=agente_aux,
                expected_output=f"Contribuição complementar como agente {agente_nome}"
            )
            tarefas_auxiliares.append(tarefa_aux)
    
    # Executar tarefas auxiliares se houver
    if agentes_auxiliares_objs and tarefas_auxiliares:
        crew_auxiliar = Crew(
            agents=agentes_auxiliares_objs,
            tasks=tarefas_auxiliares,
            verbose=False
        )
        
        resultado_auxiliar = crew_auxiliar.kickoff()
        
        # Processar as contribuições
        i = 0
        for agente_nome in agentes_auxiliares:
            if agente_nome != agente_lider:
                contribuicoes[agente_nome] = str(resultado_auxiliar[i]).strip()
                i += 1
    
    # Fase 5: Integrar todas as contribuições em uma resposta final
    # Se o narrador está entre os agentes, deixá-lo integrar
    resposta_final = ""
    if "narrador" in contribuicoes:
        # Se tivermos um resultado mecânico, fornecer contexto especial
        contexto_integracao = ""
        if resultado_mecanico:
            contexto_integracao = f"""
INSTRUÇÕES ESPECIAIS PARA INTEGRAÇÃO:
Este é um resultado de combate. Integre os resultados mecânicos de forma natural
na narrativa. Mencione os números de rolagem de forma sutil (como um mestre de RPG faria),
sem quebrar a imersão. Exemplo: "Seu raio arcano dispara com precisão [rolagem 18] e atinge
o esqueleto, causando 7 pontos de dano e quebrando vários de seus ossos".
"""
        
        # Tarefa para o narrador integrar
        tarefa_integracao = Task(
            description=f"""Todas as respostas devem ser em português do Brasil.
Contexto da aventura: Um mago humano chamado Alion está explorando a Cripta do Coração Negro.
Estado atual: {"Em combate" if event_system.in_combat else "Exploração"}.

Ação do jogador: "{comando_usuario}"

{contexto_integracao}

CONTRIBUIÇÕES DOS AGENTES:
Agente principal ({agente_lider}):
{contribuicoes[agente_lider]}

{"".join([f"Agente {agente_nome}:\n{contribuicoes[agente_nome]}\n\n" for agente_nome in contribuicoes if agente_nome != agente_lider and agente_nome != "narrador"])}

Sua tarefa é integrar todas estas contribuições em uma narrativa final coesa e envolvente.
Mantenha o tom apropriado: épico para exploração, tático e objetivo para combate.
O resultado deve parecer uma única voz narrativa fluida, como um excelente mestre de RPG.

{"Como este é um cenário de COMBATE, use um tom mais objetivo e tático, similar a uma sessão real de D&D. Mencione os resultados das rolagens subtilmente integrados na narrativa." if event_system.in_combat else "Como este é um cenário de EXPLORAÇÃO, use um tom mais épico e imersivo, rico em detalhes sensoriais e atmosféricos."}
""",
            agent=narrador,
            expected_output="Narrativa final integrada"
        )
        
        crew_integracao = Crew(
            agents=[narrador],
            tasks=[tarefa_integracao],
            verbose=False
        )
        
        resultado_integracao = crew_integracao.kickoff()
        resposta_final = str(resultado_integracao).strip()
    else:
        # Fallback: usar a contribuição do agente líder
        resposta_final = contribuicao_lider
    
    # Adicionar ao cache para contexto futuro
    adicionar_ao_cache(resposta_final)
    
    # Ações após o turno completo
    # Se o combate terminou, atualizar o estado
    if event_system.in_combat and not event_system.current_enemies:
        event_system.end_combat()
        resposta_final += "\n\nO combate terminou e você retorna ao modo de exploração."
    
    return resposta_final


# --------------------------
# Ataques de Inimigos em Combate
# --------------------------

def processar_ataque_inimigo():
    """Processa ataques de inimigos durante o combate"""
    if not event_system.in_combat or not event_system.current_enemies:
        return None
    
    # Escolher um inimigo aleatório para atacar
    inimigo = random.choice(event_system.current_enemies)
    
    # Rolagem de ataque
    # Assumindo um bônus de ataque baseado no tipo de inimigo
    atk_bonus = 3  # Padrão básico
    if "cultista" in inimigo["tipo"].lower():
        atk_bonus = 4
    elif "espectro" in inimigo["tipo"].lower() or "aparição" in inimigo["tipo"].lower():
        atk_bonus = 5
    
    total_roll, d20_value, critical = DiceSystem.attack_roll(atk_bonus)
    
    # Classe de armadura do jogador
    ca_jogador = ficha.get("classe_armadura", 10)
    
    hit = total_roll >= ca_jogador
    
    # Processar resultado
    if hit:
        # Determinar dano base pelo tipo de inimigo
        dano_base = "1d6"  # Padrão
        if "esqueleto" in inimigo["tipo"].lower():
            dano_base = "1d6"  # Espada enferrujada
        elif "zumbi" in inimigo["tipo"].lower():
            dano_base = "1d6"  # Golpe desajeitado
        elif "cultista" in inimigo["tipo"].lower():
            dano_base = "1d8"  # Adaga ritual
        elif "espectro" in inimigo["tipo"].lower() or "aparição" in inimigo["tipo"].lower():
            dano_base = "2d4"  # Toque fantasmagórico
        elif "sombra" in inimigo["tipo"].lower():
            dano_base = "2d6"  # Dreno sombrio
        
        # Rolagem de dano
        damage_total, damage_rolls = DiceSystem.roll(dano_base)
        if critical:
            bonus_damage, _ = DiceSystem.roll(dano_base)
            damage_total += bonus_damage
        
        # Aplicar dano ao personagem
        pv_atual = ficha.get("pontos_vida_atuais", ficha.get("pontos_vida", 0))
        ficha["pontos_vida_atuais"] = max(0, pv_atual - damage_total)
        
        return {
            "inimigo": inimigo["tipo"],
            "rolagem_ataque": total_roll,
            "valor_d20": d20_value,
            "critico": critical,
            "acerto": hit,
            "dano": damage_total,
            "pv_jogador": ficha["pontos_vida_atuais"]
        }
    else:
        return {
            "inimigo": inimigo["tipo"],
            "rolagem_ataque": total_roll,
            "valor_d20": d20_value,
            "critico": False,
            "acerto": False
        }


# --------------------------
# Sistema de Loot e Recompensas
# --------------------------

def gerar_loot_combate():
    """Gera recompensas aleatórias após combate"""
    if not event_system.in_combat:
        return None
    
    # Chance de encontrar itens (70%)
    if random.random() < 0.7:
        # Tipos de itens possíveis
        itens_comuns = ["Poção de Cura Menor", "Pergaminho Arcano", "Fragmento de Gema"]
        itens_incomuns = ["Amuleto Antigo", "Grimório Parcial", "Poção de Resistência"]
        itens_raros = ["Varinha Arcana", "Essência de Magia", "Pedra de Invocação"]
        
        # Determinar raridade
        raridade_roll = random.random()
        if raridade_roll < 0.7:  # 70% comum
            item = random.choice(itens_comuns)
            valor = random.randint(5, 25)
        elif raridade_roll < 0.95:  # 25% incomum
            item = random.choice(itens_incomuns)
            valor = random.randint(25, 100)
        else:  # 5% raro
            item = random.choice(itens_raros)
            valor = random.randint(100, 500)
        
        return {
            "item": item,
            "valor": valor,
            "descricao": f"Você encontrou {item}! Este item vale aproximadamente {valor} moedas de ouro."
        }
    else:
        # Apenas ouro
        moedas = random.randint(5, 50)
        return {
            "ouro": moedas,
            "descricao": f"Você encontrou {moedas} moedas de ouro nos restos dos inimigos."
        }


# --------------------------
# Loop Principal de Processamento de Turnos
# --------------------------

def processar_turno_com_resposta_inimigo(comando_usuario):
    """Processa o turno do jogador e gera reação dos inimigos quando necessário"""
    # Executar o turno principal
    resposta_jogador = executar_turno(comando_usuario)
    
    resposta_final = resposta_jogador
    
    # Se estamos em combate, processar o ataque do inimigo
    if event_system.in_combat and event_system.current_enemies:
        ataque_inimigo = processar_ataque_inimigo()
        
        if ataque_inimigo:
            # Criar tarefa para narrar a resposta do inimigo
            descricao_ataque = ""
            if ataque_inimigo["acerto"]:
                if ataque_inimigo["critico"]:
                    descricao_ataque = f"""
O {ataque_inimigo["inimigo"]} reage ao seu ataque! Ele realiza um ataque CRÍTICO contra você.
- Rolagem de ataque: {ataque_inimigo["valor_d20"]} (CRÍTICO!) + bônus = {ataque_inimigo["rolagem_ataque"]}
- O ataque acerta você (CA {ficha.get("classe_armadura", 10)})
- Dano sofrido: {ataque_inimigo["dano"]} pontos de vida
- Seus pontos de vida: {ataque_inimigo["pv_jogador"]}/{ficha.get("pontos_vida", 0)}
                    """
                else:
                    descricao_ataque = f"""
O {ataque_inimigo["inimigo"]} reage ao seu ataque! Ele realiza um ataque contra você.
- Rolagem de ataque: {ataque_inimigo["valor_d20"]} (d20) + bônus = {ataque_inimigo["rolagem_ataque"]}
- O ataque acerta você (CA {ficha.get("classe_armadura", 10)})
- Dano sofrido: {ataque_inimigo["dano"]} pontos de vida
- Seus pontos de vida: {ataque_inimigo["pv_jogador"]}/{ficha.get("pontos_vida", 0)}
                    """
            else:
                descricao_ataque = f"""
O {ataque_inimigo["inimigo"]} tenta revidar, mas falha!
- Rolagem de ataque: {ataque_inimigo["valor_d20"]} (d20) + bônus = {ataque_inimigo["rolagem_ataque"]}
- O ataque erra você (CA {ficha.get("classe_armadura", 10)})
                """
            
            # Criar tarefa para narrar o contra-ataque
            tarefa_contra_ataque = Task(
                description=f"""Todas as respostas devem ser em português do Brasil.
Você precisa criar uma breve narração para o contra-ataque de um inimigo em um combate de D&D.
Use um estilo tático e direto, similar ao de um mestre de RPG em uma mesa real.
Integre os resultados mecânicos na narrativa de forma sutil mas informativa.

RESULTADOS MECÂNICOS DO CONTRA-ATAQUE:
{descricao_ataque}

Crie uma narração breve (2-3 frases) que descreva este contra-ataque do inimigo.
Use vocabulário vívido e detalhes táticos apropriados para o tipo de inimigo.
""",
                agent=narrador,
                expected_output="Narração do contra-ataque inimigo"
            )
            
            crew_contra_ataque = Crew(
                agents=[narrador],
                tasks=[tarefa_contra_ataque],
                verbose=False
            )
            
            resultado_contra_ataque = crew_contra_ataque.kickoff()
            
            # Adicionar o contra-ataque à resposta final
            resposta_final += f"\n\n{str(resultado_contra_ataque).strip()}"
    
    # Checar se o combate acabou e há loot
    if event_system.in_combat and not event_system.current_enemies:
        loot = gerar_loot_combate()
        
        if loot:
            # Criar tarefa para narrar o loot encontrado
            tarefa_loot = Task(
                description=f"""Todas as respostas devem ser em português do Brasil.
Você precisa criar uma breve narração para o loot/recompensa encontrada após um combate em D&D.
Use um estilo épico e recompensador, como um mestre satisfeito com a vitória dos jogadores.

LOOT ENCONTRADO:
{loot["descricao"]}

Crie uma narração breve (1-2 frases) que descreva de forma interessante e épica a descoberta deste loot.
""",
                agent=narrador,
                expected_output="Narração da descoberta de loot"
            )
            
            crew_loot = Crew(
                agents=[narrador],
                tasks=[tarefa_loot],
                verbose=False
            )
            
            resultado_loot = crew_loot.kickoff()
            
            # Adicionar o loot à resposta final
            resposta_final += f"\n\n{str(resultado_loot).strip()}"
    
    return resposta_final


# Função principal para integração com o servidor Flask
def processar_comando(comando):
    return processar_turno_com_resposta_inimigo(comando)
                    
                    