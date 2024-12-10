from threading import Thread, Semaphore, Lock
from random import randint, seed
import time
import argparse
from time import time as get_time

# Variáveis de controle de sincronização
fila = []
atual_atracao = None

# Variáveis para estatísticas
tempos_espera = {}  # Dicionário para armazenar tempos de espera por atração
pessoas_por_atracao = {}  # Dicionário para contar pessoas em cada atração
inicio_simulacao = 0
tempo_ocupado = 0
ultima_pausa = 0

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
    global fila, atual_atracao, tempos_espera
    
    tempo_chegada = get_time()
    print(f"[Pessoa {id+1} / AT-{atracao+1}] Aguardando na fila.")

    with mutex_fila:
        fila.append((id, atracao, tempo_chegada))
        fila.sort(key=lambda x: x[2])  # Ordena por tempo de chegada

    while True:
        with mutex_fila:
            minha_posicao = fila.index((id, atracao, tempo_chegada))
            
            # Verifica se há alguém antes de mim querendo outra atração
            for i in range(minha_posicao):
                if fila[i][1] != atracao:
                    break
            else:  # Se não encontrou ninguém querendo outra atração
                i = minha_posicao

            if (i == minha_posicao and  # Ninguém antes de mim quer outra atração
                (atual_atracao is None or atual_atracao == atracao) and  # Atração disponível
                (pessoas_por_atracao.get(atual_atracao, 0) == 0 or atual_atracao == atracao) and  # Atração vazia ou é a minha
                semaforos[atracao]._value > 0):  # Tem vaga
                break
                
        time.sleep(UNID_TEMPO/1000)

    entrou_na_atracao(id, atracao, tempo_chegada)

def entrou_na_atracao(id, atracao, tempo_chegada):
    global atual_atracao, tempo_ocupado, ultima_pausa, pessoas_por_atracao
    
    with mutex_fila:
        # Se está iniciando uma nova atração
        if atual_atracao != atracao:
            print(f"[NASA] Iniciando a experiencia AT-{atracao+1}.")
            atual_atracao = atracao
            if ultima_pausa:
                tempo_ocupado += get_time() - ultima_pausa
                ultima_pausa = 0
        
        # Incrementa contador de pessoas na atração
        if atracao not in pessoas_por_atracao:
            pessoas_por_atracao[atracao] = 0
        pessoas_por_atracao[atracao] += 1

    with semaforos[atracao]:
        # Registra tempo de espera
        tempo_espera = get_time() - tempo_chegada
        if atracao not in tempos_espera:
            tempos_espera[atracao] = []
        tempos_espera[atracao].append(tempo_espera)
        
        print(f"[Pessoa {id+1} / AT-{atracao+1}] Entrou na NASA Experiences (quantidade = {pessoas_por_atracao[atracao]})")
        time.sleep(PERMANENCIA * UNID_TEMPO/1000)

    saiu_da_atracao(id, atracao)

def saiu_da_atracao(id, atracao):
    global atual_atracao, ultima_pausa, pessoas_por_atracao

    with mutex_fila:
        # Atualiza contadores
        pessoas_por_atracao[atracao] -= 1
        qtd = pessoas_por_atracao[atracao]
        print(f"[Pessoa {id+1} / AT-{atracao+1}] Saiu da NASA Experiences (quantidade = {qtd})")
        
        # Remove a pessoa da fila
        for i, (pid, patr, _) in enumerate(fila):
            if pid == id and patr == atracao:
                fila.pop(i)
                break
        
        # Verifica se precisa pausar a atração
        if not fila:  # Se não tem mais ninguém na fila
            atual_atracao = None
            ultima_pausa = get_time()
        elif qtd == 0:  # Se a atração atual esvaziou
            proxima_atracao = fila[0][1]
            if proxima_atracao != atracao:  # E a próxima pessoa quer uma atração diferente
                atual_atracao = None

def criar_pessoas():
    global inicio_simulacao
    
    inicio_simulacao = get_time()
    lista_pessoas = []
    
    for i in range(N_PESSOAS):
        seed(SEMENTE)
        atracao = randint(0, N_ATRACOES - 1)
        thread_pessoa = Thread(target=pessoa, args=(i, atracao))
        lista_pessoas.append(thread_pessoa)
        thread_pessoa.start()
        seed(SEMENTE)
        time.sleep(randint(0, MAX_INTERVALO) * UNID_TEMPO/1000)
        
    for thread_pessoa in lista_pessoas:
        thread_pessoa.join()

def imprimir_estatisticas():
    tempo_total = get_time() - inicio_simulacao
    
    print("\nTempo medio de espera:")
    for atracao in range(N_ATRACOES):
        if atracao in tempos_espera and tempos_espera[atracao]:
            media = sum(tempos_espera[atracao]) / len(tempos_espera[atracao]) * 1000
            print(f"Experiencia {atracao+1}: {media:.2f}")
        else:
            print(f"Experiencia {atracao+1}: 0.00")
    
    taxa_ocupacao = tempo_ocupado / tempo_total
    print(f"\nTaxa de ocupacao: {taxa_ocupacao}")

if __name__ == '__main__':
    args = parse_arguments()
    
    # Inicialização das variáveis globais
    N_ATRACOES = args.N_ATRACOES
    N_PESSOAS = args.N_PESSOAS
    N_VAGAS = args.N_VAGAS
    PERMANENCIA = args.PERMANENCIA
    MAX_INTERVALO = args.MAX_INTERVALO
    SEMENTE = args.SEMENTE
    UNID_TEMPO = args.UNID_TEMPO

    seed(SEMENTE)
    semaforos = [Semaphore(N_VAGAS) for _ in range(N_ATRACOES)]
    mutex_fila = Lock()

    thread_criar_pessoa = Thread(target=criar_pessoas)
    thread_criar_pessoa.start()
    thread_criar_pessoa.join()

    print("[NASA] Simulacao finalizada.")
    imprimir_estatisticas()
