def tratamento_de_excecoes(N_ATRACOES, N_PESSOAS, N_VAGAS, PERMANENCIA, MAX_INTERVALO, SEMENTE, UNID_TEMPO):

    #Booleano para indicar entradas inválidas
    entrada_invalida = False

    if (N_ATRACOES < 1):
        print("O número de atrações deve ser maior ou igual 1.")
        entrada_invalida = True

    if (N_PESSOAS < 1):
        print("O número de pessoas deve ser maior ou igual 1.")
        entrada_invalida = True

    if (N_VAGAS < 1):
        print("O número de vagas deve ser maior ou igual 1.")
        entrada_invalida = True

    if (PERMANENCIA < 1):
        print("O tempo de permanência deve ser maior ou igual 1.")
        entrada_invalida = True

    if (MAX_INTERVALO < 1):
        print("O intervalo máximo deve ser maior ou igual 1.")
        entrada_invalida = True

    if (SEMENTE < 1):
        print("O valor para semente deve ser maior ou igual 1.")
        entrada_invalida = True

    if (UNID_TEMPO < 1):
        print("O tempo de simulação deve ser maior ou igual 1.")
        entrada_invalida = True

    if (entrada_invalida):
        print('Programa encerrado.')
        exit(1)