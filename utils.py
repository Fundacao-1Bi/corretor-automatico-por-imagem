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


def encontrar_vertices(contorno):
    perimetro = cv2.arcLength(contorno, True)
    vertices = cv2.approxPolyDP(contorno, 0.02 * perimetro, True)
    return vertices


def encontrar_retangulos(contornos, minArea=1000):
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
