from datetime import datetime

from sqlalchemy import func, select

from .database import Base, SessionLocal, engine
from .models import Assessment, Question, Submission

# Perguntas tecnicas reescritas a partir de material de treinamento real de
# manutencao industrial (moinhos e equipamentos vibratorios) -- SEM nome de
# participante real, SEM marca/logo da empresa. As alternativas erradas
# (distratores) foram escritas por nos; a alternativa correta reflete o
# conteudo tecnico original do treinamento.
QUESTIONS: dict[str, list[tuple[str, list[str], int]]] = {
    "MO_VERTMILL": [
        ("Utiliza-se esferas de aço de pequeno diâmetro como corpos moedores no Vertimill.",
         ["Verdadeiro", "Falso"], 1),
        ("O redutor foi projetado para que a própria carcaça esteja apta a armazenar todo o óleo lubrificante, não sendo necessário reservatório externo.",
         ["Verdadeiro", "Falso"], 0),
        ("O sistema de lubrificação do redutor possui 02 filtros para garantir a qualidade do óleo lubrificante.",
         ["Verdadeiro", "Falso"], 0),
        ("A válvula \"DART\" está montada no Tanque de Separação.",
         ["Verdadeiro", "Falso"], 0),
        ("O Vertimill pode operar normalmente sem carga de bolas.",
         ["Verdadeiro", "Falso"], 1),
        ("Na parada normal (programada) do moinho, deve-se primeiro cortar a alimentação de minério e água, desligar o motor e só depois a lubrificação do redutor.",
         ["Verdadeiro", "Falso"], 0),
        ("O revestimento da rosca deve ser inspecionado trimestralmente.",
         ["Verdadeiro", "Falso"], 0),
        ("A medição estática da carga de bolas deve ser feita diariamente.",
         ["Verdadeiro", "Falso"], 1),
    ],
    "EQUIP_VIB": [
        ("Com que frequência devemos trocar o óleo dos mecanismos ML80?",
         ["500h", "1000h", "2000h", "5000h"], 1),
        ("Qual o tipo de movimento da grelha MXH e da peneira MF?",
         ["Circular / linear", "Somente linear", "Somente circular", "Elíptico"], 0),
        ("Em um equipamento vibratório, o que acontece se aumentarmos a rotação?",
         ["Aumenta a aceleração", "Reduz a amplitude a zero", "Não altera nada", "Reduz a frequência"], 0),
        ("Na necessidade de troca de molas quebradas, o que devemos fazer?",
         ["Trocar só a mola quebrada", "Trocar todas as molas dos apoios direito e esquerdo",
          "Trocar só as molas do lado oposto", "Reforçar a mola quebrada com solda"], 1),
        ("Qual a tolerância para rolamento/mancal e para rolamento/eixo dos mecanismos vibratórios?",
         ["P6 / f6", "H7 / g6", "P9 / j5", "N6 / h6"], 0),
        ("Com que frequência devemos conferir o torque dos parafusos dos mecanismos vibratórios?",
         ["250h", "500h", "1000h", "2000h"], 2),
        ("Quantas vezes podemos reutilizar os parafusos de fixação de um mecanismo?",
         ["Até 2 vezes", "Até 5 vezes", "Nunca", "Sem limite, se limpos"], 2),
        ("Qual a ferramenta correta para torque dos parafusos de fixação dos mecanismos?",
         ["Chave de impacto pneumática", "Torqueadeira hidráulica", "Chave de boca comum", "Talha manual"], 1),
    ],
    "MO_BOLAS": [
        ("Qual a finalidade de realizar o Runout Radial e Axial nas engrenagens?",
         ["Medir o desgaste do óleo lubrificante",
          "Visualizar os desvios radiais e axiais e corrigir a concentricidade e alinhamento",
          "Verificar a temperatura da engrenagem", "Calcular o consumo de energia do moinho"], 1),
        ("Qual a função das bombas de pistão no sistema hidráulico do moinho de bolas?",
         ["Resfriar o óleo do sistema",
          "Direcionar óleo em alta pressão pras sapatas radiais antes do moinho operar",
          "Filtrar impurezas do óleo", "Medir a pressão das sapatas"], 1),
        ("Para que servem as sapatas de empuxo?",
         ["Reduzir o ruído do moinho",
          "Manter o moinho estabilizado e alinhado com eixos pinhões, spout feeder e mancais principais",
          "Aumentar a rotação do moinho", "Resfriar o motor principal"], 1),
        ("O que você entende por Backlash?",
         ["A folga na parte de trás do dente do eixo pinhão no contato com o dente da engrenagem",
          "A velocidade de rotação da engrenagem", "O desgaste total do dente da engrenagem",
          "A pressão hidráulica no sistema de lubrificação"], 0),
        ("Como definimos os mancais dos eixos pinhões e os mancais principais?",
         ["Mancais duplos e mancais simples", "Mancais livres e mancais fixos",
          "Mancais radiais e mancais axiais", "Mancais hidráulicos e mancais mecânicos"], 1),
        ("Qual o valor máximo permitido de variação de pressão entre as sapatas?",
         ["100 Psi", "250 Psi", "500 Psi", "1000 Psi"], 2),
        ("Qual é a faixa ideal de temperatura durante a operação dos mancais principais?",
         ["10°C a 25°C", "32°C a 52°C", "60°C a 80°C", "90°C a 110°C"], 1),
        ("Quantas lâminas de calços em Inox são recomendadas sob as bases dos equipamentos?",
         ["1 lâmina", "2 lâminas", "3 lâminas", "5 lâminas"], 2),
    ],
    "BR_MAND_C": [
        ("Qual das práticas abaixo NÃO deve ser feita durante a manutenção do britador de mandíbulas?",
         ["Bloquear e sinalizar o equipamento antes de iniciar o serviço", "Utilizar EPI adequado",
          "Executar manutenção com a máquina em funcionamento", "Seguir o procedimento de bloqueio (LOTO)"], 2),
        ("Ao solicitar uma peça de reposição para o britador, qual informação NÃO é necessária?",
         ["Número de série do equipamento", "Código da peça no catálogo",
          "Cor da tinta do britador", "Modelo do britador"], 2),
        ("Qual dos itens abaixo NÃO é um componente típico de um britador de mandíbulas Linha C?",
         ["Mandíbula móvel", "Mandíbula fixa", "Bojo", "Placa lateral"], 2),
        ("Como é chamada a região onde é feita a regulagem da abertura do britador de mandíbula Linha C, com a máquina parada?",
         ["APF", "APA", "ASF", "AJP"], 1),
        ("Qual dos itens abaixo NÃO faz parte das fixações das mandíbulas?",
         ["Placa de aperto", "Cunha de fixação", "Abanadeira", "Parafuso de fixação"], 2),
        ("Qual NÃO é uma característica do britador de mandíbulas da Linha C?",
         ["Alta rotação, acima de 1200 RPM", "Britagem primária", "Câmara tipo mandíbula",
          "Regulagem de abertura via sistema hidráulico"], 0),
        ("Em qual situação NÃO se deve alterar o APF (ajuste) do britador pelo sistema hidráulico?",
         ["Com o britador parado e travado", "Durante a partida, sem carga",
          "Com o motor do britador em funcionamento com carga", "Na troca de mandíbulas"], 2),
        ("Qual o tipo de óleo hidráulico recomendado para temperatura ambiente entre -10°C e +35°C?",
         ["ISO VG 15", "ISO VG 32", "ISO VG 68", "ISO VG 150"], 1),
    ],
    # BR_CON_HP: sem print de origem enviado pelo usuario -- perguntas de
    # conhecimento tecnico GENERICO sobre britadores conicos linha HP (padrao
    # da industria, nao especifico/confidencial da Metso).
    "BR_CON_HP": [
        ("Qual a função do anel de ajuste (adjustment ring) num britador cônico HP?",
         ["Resfriar o óleo do sistema", "Ajustar a abertura de saída (CSS) do britador",
          "Aumentar a velocidade do eixo excêntrico", "Filtrar o minério na entrada"], 1),
        ("O que é o sistema de liberação Tramp (Tramp Release System) num britador cônico?",
         ["Sistema de lubrificação automática",
          "Sistema hidráulico que permite a passagem de material não britável sem danificar o equipamento",
          "Sistema de resfriamento do motor", "Sistema de alimentação do britador"], 1),
        ("Com que frequência normalmente se recomenda a troca do óleo lubrificante em britadores cônicos HP (uso padrão)?",
         ["A cada 250h", "A cada 1000h", "A cada 4000-8000h (conforme análise de óleo)", "Nunca precisa trocar"], 2),
        ("Qual parâmetro deve ser monitorado continuamente durante a operação para evitar sobrecarga do britador?",
         ["Cor do óleo", "Potência do motor (amperagem)", "Temperatura ambiente", "Velocidade do vento"], 1),
        ("O que caracteriza a câmara de britagem tipo \"cônica\"?",
         ["Duas placas planas que se aproximam",
          "Um cone móvel (manto) girando excentricamente dentro de uma carcaça fixa (bowl)",
          "Um rolo cilíndrico girando contra uma tela", "Um martelo rotativo golpeando o material"], 1),
        ("Qual o objetivo de manter a câmara de britagem sempre \"afogada\" (choke fed) em britadores cônicos?",
         ["Reduzir o consumo de energia", "Melhorar a forma do produto britado e reduzir o desgaste do revestimento",
          "Diminuir a produção", "Aumentar a folga entre manto e bowl"], 1),
        ("O que é CSS (Closed Side Setting) num britador cônico?",
         ["A velocidade de rotação do eixo principal",
          "A menor distância entre manto e bowl durante o ciclo de britagem",
          "A pressão do sistema hidráulico", "O diâmetro do britador"], 1),
        ("Qual é uma prática recomendada antes de qualquer manutenção mecânica no britador cônico?",
         ["Bloquear e sinalizar (LOTO) o equipamento", "Aumentar a rotação para facilitar a inspeção",
          "Remover as proteções de segurança para melhor acesso", "Iniciar o serviço com o motor ligado"], 0),
    ],
}


ASSESSMENTS = [
    ("BR_CON_HP", "Britadores Cônicos HP", "Britador cônico", 70),
    ("BR_MAND_C", "Britadores de Mandíbulas Linha C", "Britador de mandíbulas", 70),
    ("MO_BOLAS", "Moinho de Bolas", "Moinho", 70),
    ("EQUIP_VIB", "Equipamentos Vibratórios", "Peneira vibratória", 70),
    ("MO_VERTMILL", "Moinho Vertical (Vertimill)", "Moinho vertical", 70),
]

SCORES = [
    ("BR_CON_HP", "ALU-001", "Cliente A", "Instrutor 1", 90, "2026-05-12T14:10:00"),
    ("BR_CON_HP", "ALU-002", "Cliente A", "Instrutor 1", 80, "2026-05-12T14:14:00"),
    ("BR_CON_HP", "ALU-003", "Cliente A", "Instrutor 1", 60, "2026-05-12T14:18:00"),
    ("BR_MAND_C", "ALU-004", "Cliente B", "Instrutor 2", 65, "2026-06-03T16:05:00"),
    ("BR_MAND_C", "ALU-005", "Cliente B", "Instrutor 2", 75, "2026-06-03T16:08:00"),
    ("MO_BOLAS", "ALU-006", "Cliente C", "Instrutor 1", 95, "2026-06-20T11:30:00"),
    ("MO_BOLAS", "ALU-007", "Cliente C", "Instrutor 1", 90, "2026-06-20T11:34:00"),
    ("MO_BOLAS", "ALU-008", "Cliente C", "Instrutor 1", 85, "2026-06-20T11:38:00"),
    ("EQUIP_VIB", "ALU-009", "Cliente D", "Instrutor 3", 70, "2026-07-08T15:20:00"),
    ("EQUIP_VIB", "ALU-010", "Cliente D", "Instrutor 3", 55, "2026-07-08T15:24:00"),
    ("MO_VERTMILL", "ALU-011", "Cliente E", "Instrutor 2", 88, "2026-08-16T10:11:00"),
    ("MO_VERTMILL", "ALU-012", "Cliente E", "Instrutor 2", 92, "2026-08-16T10:14:00"),
]


def seed_database() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.scalar(select(func.count()).select_from(Assessment)):
            items = {}
            for code, title, equipment, passing_score in ASSESSMENTS:
                item = Assessment(
                    code=code,
                    title=title,
                    equipment=equipment,
                    passing_score=passing_score,
                )
                db.add(item)
                items[code] = item
            db.flush()
            for code, participant, client, instructor, score, date in SCORES:
                db.add(
                    Submission(
                        assessment_id=items[code].id,
                        participant_code=participant,
                        client=client,
                        instructor=instructor,
                        score=score,
                        submitted_at=datetime.fromisoformat(date),
                    )
                )
            db.commit()

        # roda sempre (nao so na 1a vez) -- assim uma prova adicionada depois
        # de o banco ja existir tambem ganha as perguntas, sem precisar
        # apagar dados ja coletados.
        assessments_by_code = {a.code: a for a in db.scalars(select(Assessment)).all()}
        for code, question_list in QUESTIONS.items():
            assessment = assessments_by_code.get(code)
            if assessment is None:
                continue
            existing = db.scalar(
                select(func.count()).select_from(Question).where(Question.assessment_id == assessment.id)
            )
            if existing:
                continue
            for order, (text, options, correct_index) in enumerate(question_list, start=1):
                db.add(
                    Question(
                        assessment_id=assessment.id,
                        order=order,
                        text=text,
                        options=options,
                        correct_index=correct_index,
                    )
                )
        db.commit()

