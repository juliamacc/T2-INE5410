from threading import Thread, Semaphore, Lock, Condition
from random import randint, seed
import time
import argparse
from time import time as get_time
import heapq

# Variáveis de controle de sincronização
fila = []
atual_atracao = None

# Mutexes para proteção das variáveis globais
mutex_fila = Lock()
mutex_atual_atracao = Lock()
mutex_tempos_espera = Lock()
mutex_pessoas_atracao = Lock()
mutex_tempo = Lock()

# Variáveis para estatísticas
tempos_espera = {}  # Armazena tempos de espera por atração
pessoas_por_atracao = {}  # Conta pessoas em cada atração
inicio_simulacao = 0
tempo_ocupado = 0  # Tempo total em que as atrações ficaram funcionando
tempo_inicio_atracao = None  # Marca quando uma atração começa a funcionar

# Adicionar nova variável global
condition_atracao = Condition()
condition_entrada = Condition()

def parse_arguments():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('N_ATRACOES', type=int, help="Número de atrações")
    parser.add_argument('N_PESSOAS', type=int, help="Número de pessoas")
    parser.add_argument('N_VAGAS', type=int, help="Número de vagas por atração")
    parser.add_argument('PERMANENCIA', type=int, help="Tempo de permanência em cada atração")
    parser.add_argument('MAX_INTERVALO', type=int, help="Tempo máximo de espera")
    parser.add_argument('SEMENTE', type=int, help="Semente para aleatoriedade")
    parser.add_argument('UNID_TEMPO', type=int, help="Unidade de tempo para espera")

    return parser.parse_args()

def pessoa(id, atracao):
    tempo_chegada = get_time()
    print(f"[Pessoa {id+1} / AT-{atracao+1}] Aguardando na fila.")

    with mutex_fila:
        heapq.heappush(fila, (tempo_chegada, id, atracao))
    
    while True:
        with condition_entrada:
            permitido_entrar = False
            with mutex_fila, mutex_atual_atracao:
                # Verifica se há alguém na frente querendo outra atração
                conflito_atracao = any(t < tempo_chegada and a != atracao 
                                     for t, _, a in fila)
                
                # Condições para entrar na atração:
                # 1. Ninguém na frente quer outra atração
                # 2. Atração está livre ou é a mesma que queremos
                # 3. Há vagas disponíveis
                if (not conflito_atracao and  
                    (atual_atracao is None or atual_atracao == atracao) and  
                    semaforos[atracao]._value > 0):
                    permitido_entrar = True
            
            if permitido_entrar:
                break
                    
            condition_entrada.wait()

    entrou_na_atracao(id, atracao, tempo_chegada)

def entrou_na_atracao(id, atracao, tempo_chegada):
    global atual_atracao, tempo_ocupado, pessoas_por_atracao, tempo_inicio_atracao
    
    # Semáforo controla número máximo de pessoas simultâneas na atração
    semaforos[atracao].acquire()
    try:
        with mutex_atual_atracao, mutex_tempo, mutex_pessoas_atracao:
            # Se é uma nova atração iniciando
            if atual_atracao != atracao:
                print(f"[NASA] Iniciando a experiencia AT-{atracao+1}.")
                atual_atracao = atracao
                tempo_inicio_atracao = get_time()  # Marca início para calcular ocupação
            
            # Atualiza contadores e estatísticas
            if atracao not in pessoas_por_atracao:
                pessoas_por_atracao[atracao] = 0
            pessoas_por_atracao[atracao] += 1

            with mutex_tempos_espera:
                # Registra tempo que pessoa esperou na fila
                tempo_espera = get_time() - tempo_chegada
                if atracao not in tempos_espera:
                    tempos_espera[atracao] = []
                tempos_espera[atracao].append(tempo_espera)
            
            print(f"[Pessoa {id+1} / AT-{atracao+1}] Entrou na NASA Experiences (quantidade = {pessoas_por_atracao[atracao]}).")
        
        # Simula tempo de permanência na atração
        time.sleep(PERMANENCIA * UNID_TEMPO/1000)
        
    finally:
        saiu_da_atracao(id, atracao)
        semaforos[atracao].release()

def saiu_da_atracao(id, atracao):
    global atual_atracao, pessoas_por_atracao, tempo_ocupado, tempo_inicio_atracao

    with mutex_fila, mutex_atual_atracao, mutex_tempo, mutex_pessoas_atracao:
        pessoas_por_atracao[atracao] -= 1
        qtd_atual = pessoas_por_atracao[atracao]
        print(f"[Pessoa {id+1} / AT-{atracao+1}] Saiu da NASA Experiences (quantidade = {qtd_atual}).")
        
        # Remove da fila
        fila_atualizada = []
        while fila:
            t, i, a = heapq.heappop(fila)
            if not (i == id and a == atracao):
                fila_atualizada.append((t, i, a))
        for item in fila_atualizada:
            heapq.heappush(fila, item)
        
        if not fila:
            print(f"[NASA] Pausando a experiencia AT-{atracao+1}.")
            if tempo_inicio_atracao is not None:
                tempo_ocupado += get_time() - tempo_inicio_atracao
                tempo_inicio_atracao = None
            atual_atracao = None
        elif qtd_atual == 0:
            if fila:
                proxima_atracao = fila[0][2]
                if proxima_atracao != atracao:
                    if tempo_inicio_atracao is not None:
                        tempo_ocupado += get_time() - tempo_inicio_atracao
                        tempo_inicio_atracao = None
                    atual_atracao = None

    # Notifica fora dos locks para evitar deadlock
    with condition_atracao:
        condition_atracao.notify_all()
    with condition_entrada:
        condition_entrada.notify_all()

def criar_pessoas():
    global inicio_simulacao
    
    inicio_simulacao = get_time()
    lista_pessoas = []
    
    # Cria N_PESSOAS threads, cada uma representando uma pessoa
    for i in range(N_PESSOAS):
        # Escolhe atração aleatoriamente (1 a N_ATRACOES)
        atracao = randint(0, N_ATRACOES - 1)
        
        thread_pessoa = Thread(target=pessoa, args=(i, atracao))
        lista_pessoas.append(thread_pessoa)
        thread_pessoa.start()
        
        # Se não for a última pessoa, espera um tempo aleatório antes da próxima
        if i < N_PESSOAS - 1:
            intervalo = randint(0, MAX_INTERVALO)
            time.sleep(intervalo)
        
    for thread_pessoa in lista_pessoas:
        thread_pessoa.join()

def imprimir_estatisticas():
    tempo_total = get_time() - inicio_simulacao
    
    print("\nTempo medio de espera:")
    with mutex_tempos_espera:
        for atracao in range(N_ATRACOES):
            if atracao in tempos_espera and tempos_espera[atracao]:
                media = sum(tempos_espera[atracao]) / len(tempos_espera[atracao])
                print(f"Experiencia {atracao+1}: {media:.2f}")
            else:
                print(f"Experiencia {atracao+1}: 0.00")
    
    with mutex_tempo:
        taxa_ocupacao = tempo_ocupado / tempo_total
        print(f"\nTaxa de ocupacao: {taxa_ocupacao:.2f}")

if __name__ == '__main__':
    args = parse_arguments()
    
    # Inicialização das variáveis globais com argumentos da linha de comando
    N_ATRACOES = args.N_ATRACOES
    N_PESSOAS = args.N_PESSOAS
    N_VAGAS = args.N_VAGAS
    PERMANENCIA = args.PERMANENCIA
    MAX_INTERVALO = args.MAX_INTERVALO
    SEMENTE = args.SEMENTE
    UNID_TEMPO = args.UNID_TEMPO

    # Inicializa gerador de números aleatórios com a seed fornecida
    seed(SEMENTE)

    print("[NASA] Simulacao iniciada.")
    
    # Cria semáforos para controlar vagas em cada atração
    semaforos = [Semaphore(N_VAGAS) for _ in range(N_ATRACOES)]
    mutex_fila = Lock()

    thread_criar_pessoa = Thread(target=criar_pessoas)
    thread_criar_pessoa.start()
    thread_criar_pessoa.join()

    print("[NASA] Simulacao finalizada.")
    imprimir_estatisticas()