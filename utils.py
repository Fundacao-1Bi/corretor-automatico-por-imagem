from statistics import mean
import cv2
import numpy as np

def remover_sombra(img):
    planos_rgb = cv2.split(img)
    planos_normalizados = []
    for plano in planos_rgb:
        img_dilatada = cv2.dilate(plano, np.ones((7, 7), np.uint8))
        img_fundo = cv2.medianBlur(img_dilatada, 41)
        diff_img = 255 - cv2.absdiff(plano, img_fundo)
        norm_img = cv2.normalize(
            diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        planos_normalizados.append(norm_img)
    imagem_sem_sombra = cv2.merge(planos_normalizados)
    return imagem_sem_sombra

def binarize(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 5)
    binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    return binary

def encontrar_vertices(contorno):
    perimetro = cv2.arcLength(contorno, True)
    vertices = cv2.approxPolyDP(contorno, 0.02 * perimetro, True)
    return vertices


def encontrar_retangulos(contornos, minArea=100):
    retangulos = []
    for contorno in contornos:
        area = cv2.contourArea(contorno)
        if area > minArea:  # Seleciona apenas os contornos que possuem área suficientemente grande
            vertices = encontrar_vertices(contorno)
            if len(vertices) == 4:  # Seleciona apenas os contornos que possuem 4 vértices
                retangulos.append(contorno)
    retangulos = sorted(retangulos, key=cv2.contourArea, reverse=True)
    return retangulos


def reordenar_pontos(pontos):
    pontos = pontos.reshape((4, 2))
    pontos_ordenados = np.zeros((4, 1, 2), np.int32)
    somatorio = pontos.sum(axis=1)
    pontos_ordenados[0] = pontos[np.argmin(somatorio)]
    pontos_ordenados[3] = pontos[np.argmax(somatorio)]
    diff = np.diff(pontos, axis=1)
    pontos_ordenados[1] = pontos[np.argmin(diff)]
    pontos_ordenados[2] = pontos[np.argmax(diff)]
    return pontos_ordenados

def duplicar_pontos_esquerda(vertices):
    vertices = vertices.reshape((4, 2))
    pontos_a_esquerda = np.zeros((4, 1, 2), np.int32)
    x = 0
    y = 1
    a = vertices[0]
    c = vertices[2]
    d = vertices[3]
    e = np.zeros(2, np.int32)
    f = np.zeros(2, np.int32)
    e[x] = round((c[x] - 1.5*(d[x] - c[x])))
    e[y] = c[y]
    f[x] = round((a[x] - 1.5*(d[x] - a[x])))
    f[y] = a[y]
    pontos_a_esquerda[0][0] = f
    pontos_a_esquerda[1][0] = e
    pontos_a_esquerda[2][0] = c
    pontos_a_esquerda[3][0] = a
    return pontos_a_esquerda

def calcular_maximos(vertices):
    vertices = vertices.reshape((4, 2))
    a = vertices[0]
    b = vertices[1]
    c = vertices[2]
    d = vertices[3]
    largura_AD = np.sqrt(((a[0] - d[0]) ** 2) + ((a[1] - d[1]) ** 2))
    largura_BC = np.sqrt(((b[0] - c[0]) ** 2) + ((b[1] - c[1]) ** 2))
    maxLargura = max(int(largura_AD), int(largura_BC))
    altura_AB = np.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2))
    altura_CD = np.sqrt(((c[0] - d[0]) ** 2) + ((c[1] - d[1]) ** 2))
    maxAltura = max(int(altura_AB), int(altura_CD))
    return (maxLargura, maxAltura)

def cortar_imagem(img, fator_corte):
    largura, altura = img.shape[1], img.shape[0]
    crop_largura = (largura*fator_corte) if (largura *
                                             fator_corte) < img.shape[1] else img.shape[1]
    crop_altura = altura*fator_corte if altura * \
        fator_corte < img.shape[0] else img.shape[0]
    mid_x, mid_y = int(largura/2), int(altura/2)
    cw2, ch2 = int(crop_largura/2), int(crop_altura/2)
    crop_img = img[mid_y-ch2:mid_y+ch2, mid_x-cw2:mid_x+cw2]
    return crop_img

def crop(img, contour):
    x, y, w, h = cv2.boundingRect(contour)
    crop_img = img[y:y+h, x:x+w]
    return crop_img

def warp(img, contour, h, w):
    vertices = encontrar_vertices(contour)
    v_np32 = np.float32(vertices)
    rect = np.float32(
        [[0, 0], [w, 0], [0, h], [w, h]])
    matrix = cv2.getPerspectiveTransform(v_np32, rect)
    warped = cv2.warpPerspective(img, matrix, (w, h))
    return warped

def fatiar_vertical(img, partes):
    # Para dividir é necessário que as partes sejam iguais
    # Por isso é feito resize da imagem para que a altura seja múltiplo de partes
    largura, altura = img.shape[1], img.shape[0]
    divisao_inteira = altura//partes
    nova_altura_multipla = divisao_inteira*partes
    imagem_altura_multipla = cv2.resize(
        img, (largura, nova_altura_multipla))
    fatias = np.vsplit(imagem_altura_multipla, partes)
    return fatias


def fatiar_horizontal(img, partes):
    # Para dividir é necessário que as partes sejam iguais
    # Por isso é feito resize da imagem para que a largura seja múltiplo de partes
    largura, altura = img.shape[1], img.shape[0]
    divisao_inteira = largura//partes
    nova_largura_multipla = divisao_inteira*partes
    imagem_largura_multipla = cv2.resize(
        img, (nova_largura_multipla, altura))
    fatias = np.hsplit(imagem_largura_multipla, partes)
    return fatias


def exibir_imagens(lista_imagens):
    for imagem in lista_imagens:
        cv2.imshow(imagem[0], imagem[1])


def obter_indice_da_alternativa(alternativa):
    alternativa_minuscula = alternativa.lower()
    return ["a", "b", "c", "d", "e"].index(alternativa_minuscula)


def ober_alternativa_pelo_indice(indice):
    if indice < 0:
        return "N/A"
    else:
        return ["A", "B", "C", "D", "E"][indice]

def read_qr(img):
    detector = cv2.QRCodeDetector()
    data, bbox, straight_qrcode = detector.detectAndDecode(img)
    return data

def compute_answers(answers_rect, lines_n, columns_n):
    lines = fatiar_vertical(answers_rect, lines_n)
    #Traduz como as respostas foram datas em letras
    respostas = []
    for i, linha in enumerate(lines):
        maior_pixels = 0
        indice_marcado = -1
        img_colunas = fatiar_horizontal(linha, columns_n)
        numero_pixels_na_coluna = []
        for j, coluna in enumerate(img_colunas):
            coluna = cortar_imagem(coluna, 0.90)
            numero_de_pixels_brancos = cv2.countNonZero(coluna)
            numero_pixels_na_coluna.append(numero_de_pixels_brancos)
        numero_pixels_na_coluna_sem_maior = numero_pixels_na_coluna.copy()
        numero_pixels_na_coluna_sem_maior.remove(max(numero_pixels_na_coluna))
        media_de_pixels = mean(numero_pixels_na_coluna_sem_maior)
        for indice_pixels, pixels in enumerate(numero_pixels_na_coluna):
            if (pixels > maior_pixels and pixels > media_de_pixels*(1.1+0.03*columns_n)):
                maior_pixels = pixels
                indice_marcado = indice_pixels

        alternativa_em_letra = ober_alternativa_pelo_indice(
            indice_marcado)
        respostas.append(alternativa_em_letra)
    return respostas