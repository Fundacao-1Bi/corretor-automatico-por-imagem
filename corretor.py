from statistics import mean
import glob
import cv2
import numpy as np
import utils

DEBUGAR = False
gabarito = ["a", "b", "c", "d", "e", "a", "b", "c", "d", "e"]


def corrigir(nome_do_arquivo):
    img = cv2.imread(nome_do_arquivo)
    # Redimensiona a imagem para um tamanho padrão 3:4
    img = cv2.resize(img, (1512, 2016))
    img_copy = img.copy()

    # Pre Processamentos
    imagem_sem_sombra = utils.remover_sombra(img)
    imagem_cinza = cv2.cvtColor(imagem_sem_sombra, cv2.COLOR_BGR2GRAY)
    imagem_com_desfoque = cv2.GaussianBlur(imagem_cinza, (11, 11), 16)
    imagem_binaria = cv2.threshold(
        imagem_com_desfoque, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Encontra os contornos das questões e o retangulo maior
    contornos, _ = cv2.findContours(
        imagem_binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    retangulos = utils.encontrar_retangulos(contornos)
    maior_retangulo = retangulos[0]
    vertices_maior_retangulo = utils.encontrar_vertices(maior_retangulo)
    vertices_ordenadas = utils.reordenar_pontos(vertices_maior_retangulo)

    cv2.drawContours(img_copy, vertices_ordenadas, -1, (255, 0, 0), 60)
    cv2.imshow("img_copy", img_copy)

    # Corrige perspectiva da Imagem

    vertices_float_32 = np.float32(vertices_ordenadas)
    template_formato_retangulo = np.float32(
        [[0, 0], [267*NUMERO_ALTERNATIVAS, 0], [0, 193*NUMERO_QUESTOES], [267*NUMERO_ALTERNATIVAS, 193*NUMERO_QUESTOES]])  # shape conhecido do retangulo em pixels
    matriz_de_transformacao = cv2.getPerspectiveTransform(
        vertices_float_32, template_formato_retangulo)
    img_corrigida = cv2.warpPerspective(
        imagem_binaria, matriz_de_transformacao, (267*NUMERO_ALTERNATIVAS, 193*NUMERO_QUESTOES))
    img_bordas_cortadas = utils.cortar_imagem(
        img_corrigida, 0.94)  # corta 6% das bordas e mantém 94% da imagem

    img_linhas = utils.fatiar_vertical(img_bordas_cortadas, NUMERO_QUESTOES)

    respostas = []
    pontuacao = 0
    for indice_linha, linha in enumerate(img_linhas):
        maior_pixels = 0
        indice_marcado = -1
        img_colunas = utils.fatiar_horizontal(linha, NUMERO_ALTERNATIVAS)
        numero_pixels_na_coluna = []
        for indice_coluna, coluna in enumerate(img_colunas):
            numero_de_pixels_brancos = cv2.countNonZero(coluna)
            numero_pixels_na_coluna.append(numero_de_pixels_brancos)
            if (DEBUGAR):
                cv2.imshow("imagem_circulo"+str(indice_linha) +
                           "_" + str(indice_coluna)+"_"+str(numero_de_pixels_brancos), coluna)
        numero_pixels_na_coluna_sem_maior = numero_pixels_na_coluna.copy()
        numero_pixels_na_coluna_sem_maior.remove(max(numero_pixels_na_coluna))
        media_de_pixels = mean(numero_pixels_na_coluna_sem_maior)
        for indice_pixels, pixels in enumerate(numero_pixels_na_coluna):
            if (pixels > maior_pixels and pixels > media_de_pixels*(1.2+0.01*NUMERO_ALTERNATIVAS)):
                maior_pixels = pixels
                indice_marcado = indice_pixels

        alternativa_em_letra = utils.ober_alternativa_pelo_indice(
            indice_marcado)
        respostas.append(alternativa_em_letra)
        if (len(gabarito) == NUMERO_QUESTOES and indice_marcado == utils.obter_indice_da_alternativa(gabarito[indice_linha])):
            pontuacao += 1

    if DEBUGAR:
        # Imagem binária deve ter o retângulo das questões bem destacado e as opções marcadas também
        # Nos contornos o retângulo das questões deve ser o maior retângulo destacado da imagem
        copia_contornos = img.copy()
        cv2.drawContours(copia_contornos, contornos, -1, (0, 0, 255), 3)
        cv2.drawContours(copia_contornos, [
                         maior_retangulo], -1, (0, 255, 0), 20)
        utils.exibir_imagens([('img', img), ('imagem_sem_sombra', imagem_sem_sombra), (
            'imagem_com_desfoque', imagem_com_desfoque), ('imagem_binaria', imagem_binaria), ('contornos', copia_contornos), ('img_corrigida', img_corrigida), ('img_bordas_cortadas', img_bordas_cortadas)])
        print("DEBUG Respostas: ", "Arquivo: ", nome_do_arquivo,
              respostas, "nota: ", pontuacao, "/ 10")
        print("FIM Debug \n\n\n")
        cv2.waitKey(0)

    return respostas, pontuacao


# Experiência padrão de gabarito, configurar NUMERO_QUESTOES = 10 e NUMERO_ALTERNATIVAS = 5
NUMERO_QUESTOES = 10
NUMERO_ALTERNATIVAS = 5
arquivos_a_serem_corrigidos = glob.glob("gabaritos/*")

# Experiência de diagnóstico com 7 linhas, configurar NUMERO_QUESTOES = 7 e NUMERO_ALTERNATIVAS = 3
# NUMERO_QUESTOES = 7
# NUMERO_ALTERNATIVAS = 3
# arquivos_a_serem_corrigidos = glob.glob("diagnosticos/7*")

# Experiência de diagnóstico com 14 linhas, configurar NUMERO_QUESTOES = 7 e NUMERO_ALTERNATIVAS = 3
# NUMERO_QUESTOES = 14
# NUMERO_ALTERNATIVAS = 3
# arquivos_a_serem_corrigidos = glob.glob("diagnosticos/14*")

for arquivo in arquivos_a_serem_corrigidos:
    respostas, pontuacao = corrigir(arquivo)
    nome_do_estudante = arquivo.replace(
        "gabaritos/", "").replace(".jpg", "").replace(".png", "").replace(".jpeg", "")
    print("Estudante: ", nome_do_estudante, "Respostas: ",
          respostas, "Nota: ", pontuacao, "/ 10")
