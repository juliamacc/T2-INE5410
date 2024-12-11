from threading import Thread, Semaphore, Lock, Condition
from random import randint, seed
import time
import argparse
from time import time as get_time
import heapq

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
    with mutex_fila:
        # Adiciona pessoa na fila
        fila.append([id,atracao])
    print(f"[Pessoa {id+1} / AT-{atracao+1}] Aguardando na fila.")

    entrou_na_atracao(id, atracao, tempo_chegada)

def entrou_na_atracao(id, atracao, tempo_chegada):
    global fila, atual_atracao, tempo_ocupado, pessoas_por_atracao, tempo_inicio_atracao
    
    mutex_fila.acquire()
    while id != fila[0][0]:
    	novo_primeiro.wait()
    mutex_fila.release()
        
    # Nenhuma atração começou ainda
    mutex_atual_atracao.acquire()
    
    if atual_atracao == -1:
    	atual_atracao = atracao
    	print(f"[NASA] Iniciando a experiencia AT-{atracao+1}.")

    elif atual_atracao != atracao:
    	mudou_atracao.wait()
    	atual_atracao = atracao
    	print(f"[NASA] Iniciando a experiencia AT-{atracao+1}.")
    
    mutex_atual_atracao.release()
    
    # Remove o primeiro da fila (esse)
    mutex_fila.acquire()
    fila.pop(0)
    if fila != []:
        novo_primeiro.notify_all()
    mutex_fila.release()
    	
    # entra na atração
    semaforo.acquire()
        
    # Marca início para calcular ocupação
    tempo_inicio_atracao = get_time()  
        
    mutex_pessoas_atracao.acquire()
    pessoas_por_atracao += 1
    mutex_pessoas_atracao.release()
    
    print(f"[Pessoa {id+1} / AT-{atracao+1}] Entrou na NASA Experiences (quantidade = {pessoas_por_atracao})")
        
    with mutex_tempos_espera:
        # Registra tempo que pessoa esperou na fila
        tempo_espera = get_time() - tempo_chegada
        tempos_espera[atracao][0] += tempo_espera 
        tempos_espera[atracao][1] += 1
        
    # Simula tempo de permanência na atração
    time.sleep(PERMANENCIA * UNID_TEMPO/1000)
    	
    saiu_da_atracao(id, atracao)
    
    
def saiu_da_atracao(id, atracao):
    global fila, atual_atracao, ultima_pausa, pessoas_por_atracao, tempo_ocupado, tempo_inicio_atracao

    mutex_pessoas_atracao.acquire()
    pessoas_por_atracao -= 1
    qtd_atual = pessoas_por_atracao
    mutex_pessoas_atracao.release()
    

    print(f"[Pessoa {id+1} / AT-{atracao+1}] Saiu da NASA Experiences (quantidade = {qtd_atual})")
        

    if qtd_atual == 0:
        print(f"[NASA] Pausando a experiencia AT-{atracao+1}")
        mutex_atual_atracao.acquire()
        mutex_fila.acquire()
        if fila == []:
           atual_atracao = -1
        elif atual_atracao != fila[0][1]:
           mudou_atracao.notify_all()
        mutex_fila.acquire()
        mutex_atual_atracao.release()

        mutex_tempo.acquire()
        if tempo_inicio_atracao is not None:
           tempo_ocupado += get_time() - tempo_inicio_atracao
           tempo_inicio_atracao = None
        mutex_tempo.release()
    semaforo.release()

def criar_pessoas():
    global inicio_simulacao
    
    inicio_simulacao = get_time()
    lista_pessoas = []
    
    # Cria N_PESSOAS threads, cada uma representando uma pessoa
    for i in range(N_PESSOAS):
        atracao = randint(0, N_ATRACOES - 1)  # Escolhe atração aleatoriamente
        thread_pessoa = Thread(target=pessoa, args=(i, atracao))
        lista_pessoas.append(thread_pessoa)
        thread_pessoa.start()
        # Espera intervalo aleatório antes de criar próxima pessoa
        time.sleep(randint(0, MAX_INTERVALO) * UNID_TEMPO/1000)
        
    for thread_pessoa in lista_pessoas:
        thread_pessoa.join()

def imprimir_estatisticas():
    tempo_total = get_time() - inicio_simulacao
    
    print("\nTempo medio de espera:")
    with mutex_tempos_espera:
        for atracao in range(N_ATRACOES):
            if tempos_espera[atracao][1] > 0:
                media = tempos_espera[atracao][0]/ tempos_espera[atracao][1] * 1000
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
    
    # Variáveis de controle de sincronização
    fila = []
    atual_atracao = -1
    # Variáveis para estatísticas
    tempos_espera = [[0.0, 0]]*N_ATRACOES  # Armazena tempos de espera e pessoas por atração
    pessoas_por_atracao = 0  # Conta pessoas em cada atração
    inicio_simulacao = 0
    tempo_ocupado = 0  # Tempo total em que as atrações ficaram funcionando
    tempo_inicio_atracao = None  # Marca quando uma atração começa a funcionar
    
    # Cria semáforos para controlar vagas em cada atração
    semaforo = Semaphore(N_VAGAS)

    # Mutexes para proteção das variáveis globais
    mutex_fila = Lock()
    mutex_atual_atracao = Lock()
    mutex_tempos_espera = Lock()
    mutex_pessoas_atracao = Lock()
    mutex_tempo = Lock()
    mudou_atracao = Condition(mutex_atual_atracao)
    novo_primeiro = Condition(mutex_fila)

    thread_criar_pessoa = Thread(target=criar_pessoas)
    thread_criar_pessoa.start()
    thread_criar_pessoa.join()

    print("[NASA] Simulacao finalizada.")
    imprimir_estatisticas()
