# Imports the Google Cloud client library
import io
from google.cloud import vision
from google.cloud.vision import AnnotateImageResponse as ar

# Instantiates a client
client = vision.ImageAnnotatorClient()

def analyze(byteImg):

    image = vision.Image(content=byteImg)
    image_context = {"language_hints": ["pt"]}

    response = client.document_text_detection(image=image, image_context=image_context)
    if response.error.message:
        raise Exception(
            f"For more info on error messages, check: \n"
            f"https://cloud.google.com/apis/design/errors {response.error.message}")
    jsonres = ar.to_json(response)
    return jsonres

if __name__ == "__main__":
    with io.open('img_nomes.jpg', 'rb') as image_file:
        content = image_file.read()
        result = analyze(content)
        print(result)



