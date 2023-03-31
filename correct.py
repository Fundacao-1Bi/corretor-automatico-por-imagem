import glob
import cv2
import utils

COLUMNS = 4
LINES = 25
NAME_WIDTH = 2000
LINE_HEIGHT = 193

def correct(filename):
    # Read the image
    img = cv2.imread(filename)
    img = cv2.resize(img, (1512, 2016))

    # Process the image
    no_s = utils.remover_sombra(img)
    gray = cv2.cvtColor(no_s, cv2.COLOR_BGR2GRAY)
    img_b = utils.binarize(img)

    # Find the contours
    contours, _ = cv2.findContours(img_b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = utils.encontrar_retangulos(contours)

    copy = img.copy()
    cv2.drawContours(copy, rects, -1, (255, 0, 0), 2)
    cv2.imshow("copy", copy)
    cv2.waitKey(0)

    # Crop rectangles
    names_rect = rects[0]
    names = utils.warp(gray, names_rect, )

    answers_rect = rects[1]



    # answers_rect = utils.warp(img_b, rects[1])
    # # Format output
    # answers = utils.compute_answers(answers_rect, LINES, COLUMNS)
    # print("Respostas: " , answers)
    # template_type = utils.read_qr(qrcode)
    # print("Template: ", template_type)

    for i, img in enumerate(cropped_rects):
        cv2.imshow(f"img{i}", img)
        print(img.shape)
        cv2.waitKey(0)

if __name__ == "__main__":
    for file in glob.glob('diagnosticos/*.jpg'):
        correct(file)