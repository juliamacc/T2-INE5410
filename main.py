from threading import Thread, Semaphore, Lock
from excecoes import tratamento_de_excecoes
from random import randint, seed
import time

# Função para representar cada pessoa na simulação
def pessoa(id, atracao):
    global fila # precisa de um mutex

    #pega mutex
    #identifica qual a sua atração
    fila.append(atração)
    #libera mutex
    print(f"[Pessoa {id} / AT-{atracao}] Aguardando na fila.")
    
    # Simula o tempo de espera até entrar na atração
    #time.sleep(randint(1, MAX_INTERVALO))

    #espera a sua vez de entrar na atração 
    entra_na_atracao(atracao)
    
    # Entrada na atração
    print(f"[Pessoa {id} / AT-{atracao}] Entrou na NASA Experiences (quantidade = {quantidade_na_atracao[atracao - 1]+1})")
    quantidade_na_atracao[atracao - 1] += 1
    
    # Simula o tempo de permanência na atração
    time.sleep(PERMANENCIA)
    
    # Sai da atração
    sai_da_atracao(atracao)
    print(f"[Pessoa {id} / AT-{atracao}] Saiu da NASA Experiences (quantidade = {quantidade_na_atracao[atracao - 1]-1})")
    quantidade_na_atracao[atracao - 1] -= 1
    
    # Libera o semáforo após sair
    # semaforo_vagas.release()

def entra_na_atracao(atracao):
    global atracao_atual #precisa de um mutex
    global fila # precisa de um mutex
    
    # Adquire o semáforo para entrar na atração (controla vagas simultâneas)
    semaforo_vagas.acquire()

    #testa se sua atração é a em funcionamento
    if atracao_atual == 0: # não tem atração em funcionamento
        #pega mutex
        atracao_atual = atracao
        #libera mutex
        #pega mutex
        #sai da fila 
        fila.pop(0)
        #libera mutex
        return
    elif atracao_atual == atracao: # é a atração atual
        #pega mutex
        #sai da fila 
        fila.pop(0)
        #libera mutex
        return
    else: # não é a atração atual 
        #criar algum tipo de barreira pra esperar a atração anterior terminar sem ninguém mais pegar o semáforo 
        #pega mutex
        atracao_atual = atracao
        #libera mutex
        return

def sai_da_atracao(atracao):
    # Libera o semáforo após sair
    semaforo_vagas.release()
    return

# Função que cria as pessoas
def criar_pessoas():
    global identificador_atracoes
    global atracao_atual = 0
    global fila = []
    lista_pessoas = []  # Lista para armazenar as threads das pessoas
    for i in range(N_PESSOAS):
        atracao = identificador_atracoes[randint(0, N_ATRACOES - 1)]  # Escolhe a atração aleatoriamente
        # Simula o tempo de espera até entrar na atração (tem que dar um tempo entre cada thread)
        time.sleep(randint(1, MAX_INTERVALO))
        thread_pessoa = Thread(target=pessoa, args=(i + 1, atracao + 1))  # Cria uma thread para a pessoa
        thread_pessoa.start()
        lista_pessoas.append(thread_pessoa)
    
    # Aguarda todas as threads terminarem
    for thread_pessoa in lista_pessoas:
        thread_pessoa.join()

# Inicialização do programa
if __name__ == '__main__': 
    # Leitura dos parâmetros de entrada
    N_ATRACOES, N_PESSOAS, N_VAGAS, PERMANENCIA, MAX_INTERVALO, SEMENTE, UNID_TEMPO = map(int, input().split())
    
    # Tratamento de Exceções
    tratamento_de_excecoes(N_ATRACOES, N_PESSOAS, N_VAGAS, PERMANENCIA, MAX_INTERVALO, SEMENTE, UNID_TEMPO)

    print("[NASA] Simulacao iniciada.")
    # Inicializa a semente para a geração aleatória
    seed(SEMENTE)
    
    # Lista de atrações
    identificador_atracoes = [i for i in range(N_ATRACOES)]
    
    # Lista para controlar o número de pessoas em cada atração
    quantidade_na_atracao = [0] * N_ATRACOES

    # Mutexes e semáforos para controle de concorrência
    semaforo_vagas = Semaphore(N_VAGAS)

    # Thread para criar as pessoas
    thread_criar_pessoa = Thread(target=criar_pessoas)
    thread_criar_pessoa.start()

    # Aguarda a finalização de todas as threads das pessoas
    thread_criar_pessoa.join()

    # Simulação finalizada
    print("[NASA] Simulacao finalizada.")


''' Saídas necessarias
( ) Inicio da simulação: "[NASA] Simulacao iniciada."
(X) Pessoa criada: "[Pessoa X / Z] Aguardando na fila."
( ) Inicio da experiencia: "[NASA] Iniciando a experiencia Z."
( ) Pessoa ingressa na atração: "[Pessoa X / Z] Entrou na NASA Experiences (quantidade = Y)."
( ) Pessoa sai da atração: "[Pessoa X / Z] Saiu da NASA Experiences (quantidade = Y)."
( ) Experiencia pausada: "[NASA] Pausando a experiencia Z."
( ) Fim da simulação: "[NASA] Simulacao finalizada."

            >   X = 1, 2, 3, ..., N_PESSOAS (incrementa a cada pessoa criada)
            >   Y = quantidade de pessoas na atração
            >   Z = nome da atração (AT-1, AT-2, ...)

( ) "Tempo medio de espera:"
( ) "Experiencia A: X"
( ) "Experiencia B: X"
( ) "Experiencia C: X"
( ) "Taxa de ocupacao: X"
