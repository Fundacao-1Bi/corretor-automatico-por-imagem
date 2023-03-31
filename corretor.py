from statistics import mean
import glob
import cv2
import numpy as np
import utils

DEBUGAR = False
NUMERO_QUESTOES = 25
NUMERO_ALTERNATIVAS = 4
LARGURA_NOME = 2000
ALTURA_LINHA = 193

def corrigir(nome_do_arquivo):
    img = cv2.imread(nome_do_arquivo)
    # Redimensiona a imagem para um tamanho padrão 3:4
    img = cv2.resize(img, (1512, 2016))
    img_copy = img.copy()

    # Pre Processamentos
    imagem_sem_sombra = utils.remover_sombra(img)
    imagem_cinza = cv2.cvtColor(imagem_sem_sombra, cv2.COLOR_BGR2GRAY)
    imagem_com_desfoque = cv2.GaussianBlur(imagem_cinza, (3, 3), 5)
    imagem_binaria = cv2.threshold(
        imagem_com_desfoque, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # Encontra os contornos das questões e o retangulo maior
    contornos, _ = cv2.findContours(
        imagem_binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    retangulos = utils.encontrar_retangulos(contornos)

    seg_maior_retangulo = retangulos[1]
    vertices_maior_retangulo = utils.encontrar_vertices(seg_maior_retangulo)
    vertices_ordenadas = utils.reordenar_pontos(vertices_maior_retangulo)

    # cv2.drawContours(img_copy, vertices_ordenadas, -1, (255, 0, 0), 60)
    # cv2.imshow("img_original", img_copy)
    # img_copy2 = img.copy()
    # cv2.drawContours(img_copy2, vertices_deslocados, -1, (255, 0, 0), 60)
    # cv2.imshow("img_deslocado", img_copy2)
    # cv2.waitKey(0)

    ## Trabalha com a parte das opções de resposta
    # Corrige perspectiva da Imagem
    vertices_float_32 = np.float32(vertices_ordenadas)
    # pinta a borda de preto para remover-la da área de interesse
    cv2.drawContours(imagem_binaria, [seg_maior_retangulo], -1, (0, 0, 0), 16)
    template_formato_retangulo = np.float32(
        [[0, 0], [267*NUMERO_ALTERNATIVAS, 0], [0, 193*NUMERO_QUESTOES], [267*NUMERO_ALTERNATIVAS, 193*NUMERO_QUESTOES]])  # shape conhecido do retangulo em pixels
    matriz_de_transformacao = cv2.getPerspectiveTransform(
        vertices_float_32, template_formato_retangulo)
    img_corrigida = cv2.warpPerspective(
        imagem_binaria, matriz_de_transformacao, (267*NUMERO_ALTERNATIVAS, 193*NUMERO_QUESTOES))
    img_bordas_cortadas = utils.cortar_imagem(
        img_corrigida, 0.99)  # corta 1% das bordas e mantém 99% da imagem

    img_linhas = utils.fatiar_vertical(img_bordas_cortadas, NUMERO_QUESTOES)
    respostas = []
    # Traduz como as respostas foram datas em letras
    for indice_linha, linha in enumerate(img_linhas):
        maior_pixels = 0
        indice_marcado = -1
        img_colunas = utils.fatiar_horizontal(linha, NUMERO_ALTERNATIVAS)
        numero_pixels_na_coluna = []
        for indice_coluna, coluna in enumerate(img_colunas):
            coluna = utils.cortar_imagem(coluna, 0.90)
            numero_de_pixels_brancos = cv2.countNonZero(coluna)
            numero_pixels_na_coluna.append(numero_de_pixels_brancos)
            # if (DEBUGAR):
                # cv2.imshow("imagem_circulo"+str(indice_linha) +
                #            "_" + str(indice_coluna)+"_"+str(numero_de_pixels_brancos), coluna)
        numero_pixels_na_coluna_sem_maior = numero_pixels_na_coluna.copy()
        numero_pixels_na_coluna_sem_maior.remove(max(numero_pixels_na_coluna))
        media_de_pixels = mean(numero_pixels_na_coluna_sem_maior)
        for indice_pixels, pixels in enumerate(numero_pixels_na_coluna):
            if (pixels > maior_pixels and pixels > media_de_pixels*(1.1+0.03*NUMERO_ALTERNATIVAS)):
                maior_pixels = pixels
                indice_marcado = indice_pixels

        alternativa_em_letra = utils.ober_alternativa_pelo_indice(
            indice_marcado)
        respostas.append(alternativa_em_letra)

    ## Trabalha com a parte dos nomes dos alunos
    # Desloca os vertices do retângulo identificado para as respostas para a esquerda
    maior_retangulo = retangulos[0]
    vertices_maior_retangulo = utils.encontrar_vertices(maior_retangulo)
    vertices_ordenadas = utils.reordenar_pontos(vertices_maior_retangulo)

    # cv2.drawContours(img_copy, vertices_ordenadas, -1, (255, 0, 0), 60)
    # cv2.imshow("img_original", img_copy)
    # img_copy2 = img.copy()
    # cv2.drawContours(img_copy2, vertices_deslocados, -1, (255, 0, 0), 60)
    # cv2.imshow("img_deslocado", img_copy2)
    # cv2.waitKey(0)

    ## Trabalha com a parte dos nomes dos alunos
    # Corrige perspectiva da Imagem
    vertices_float_32 = np.float32(vertices_ordenadas)
    # pinta a borda de preto para remover-la da área de interesse
    cv2.drawContours(imagem_sem_sombra, [maior_retangulo], -1, (0, 0, 0), 5)
    template_formato_retangulo = np.float32(
        [[0, 0], [LARGURA_NOME, 0], [0, ALTURA_LINHA*NUMERO_QUESTOES], [LARGURA_NOME, ALTURA_LINHA*NUMERO_QUESTOES]])  # shape conhecido do retangulo em pixels
    matriz_de_transformacao = cv2.getPerspectiveTransform(
        vertices_float_32, template_formato_retangulo)
    img_corrigida = cv2.warpPerspective(
        imagem_sem_sombra, matriz_de_transformacao, (LARGURA_NOME, ALTURA_LINHA*NUMERO_QUESTOES))
    img_bordas_cortadas = utils.cortar_imagem(
        img_corrigida, 0.99)  # corta 1% das bordas e mantém 99% da imagem
    cv2.imshow("img_nomes", img_corrigida)
    cv2.imwrite("img_nomes.jpg", img_corrigida)
    cv2.waitKey(0)
    # ret_esq_linhas = utils.fatiar_vertical(ret_esq_corrigido, NUMERO_QUESTOES)
    # for i in (range(0, len(ret_esq_linhas))):
    #     cv2.imshow("ret_esqq_linhas"+str(i), ret_esq_linhas[i])
    #     cv2.waitKey(0)

    # if DEBUGAR:
    #     # Imagem binária deve ter o retângulo das questões bem destacado e as opções marcadas também
    #     # Nos contornos o retângulo das questões deve ser o maior retângulo destacado da imagem
    #     copia_contornos = img.copy()
    #     cv2.drawContours(copia_contornos, contornos, -1, (0, 0, 255), 3)
    #     cv2.drawContours(copia_contornos, [
    #                      maior_retangulo], -1, (0, 255, 0), 20)
    #     utils.exibir_imagens([('img', img), ('imagem_sem_sombra', imagem_sem_sombra), (
    #         'imagem_com_desfoque', imagem_com_desfoque), ('imagem_binaria', imagem_binaria), ('contornos', copia_contornos), ('img_corrigida', img_corrigida), ('img_bordas_cortadas', img_bordas_cortadas)])
    #     print("DEBUG Respostas: ", "Arquivo: ", nome_do_arquivo,
    #           respostas)
    #     print("FIM Debug \n\n\n")
    #     cv2.waitKey(0)

    return respostas

arquivos_a_serem_corrigidos = glob.glob("diagnosticos/*.jpg")

for arquivo in arquivos_a_serem_corrigidos:
    out = corrigir(arquivo)
    nome_do_estudante = arquivo.replace("diagnosticos/", "").replace(".jpg", "").replace(".png", "").replace(".jpeg", "")
    print("Estudante: ", nome_do_estudante, "Respostas: ",out)
