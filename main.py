from threading import Thread

# Entrada
entrada = N_ATRACOES, N_PESSOAS, N_VAGAS, PERMANENCIA, MAX_INTERVALO, SEMENTE, UNID_TEMPO = map(int, input().split())

# Thread de pessoas
def pessoa(id):
    print(f"[Pessoa X / Z] Aguardando na fila.") # rascunho
    # ...

#Thread para criar pessoas
def criar_pessoas():
    lista_pessoas = [] # lista p/ armazenar as threads pessoas
    for i in range(N_PESSOAS):
        thread_pessoa = Thread(target=pessoa, args=(i,))
        thread_pessoa.start()
        lista_pessoas.append(thread_pessoa)

thread_criar_pessoa = Thread(target=criar_pessoas)
thread_criar_pessoa.start()
# ...
thread_criar_pessoa.join()




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

'''