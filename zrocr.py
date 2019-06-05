#! /usr/bin/python3
from PIL import Image
from io import BytesIO
import requests
import numpy as np
from skimage import morphology
from sklearn.cluster import KMeans
import pickle

# configure
image_width = 30
model_path = 'train/LR.pickle'


headers = {
    'user-agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'}


def img_get(url):
    res = requests.get(url, headers=headers)
    memio = BytesIO()
    memio.write(res.content)
    return memio


def ocr(position, url):
    image_file = img_get(url)
    image = Image.open(image_file)
    images = []
    for i in range(10):
        im = image.crop((image_width*i, 0, image_width *
                         (i+1), image.size[1])).convert('L')
        images.append(im)
    model = None
    with open(model_path, 'rb') as fr:
        model = pickle.load(fr)
    numbers = []
    for image in images:
        number = predict(model, image)
        numbers.append(number)
    value = []
    for pos in position:
        value.append(str(numbers[pos]))
    return int(''.join(value))


def convert_PIL(image):
    image = Image.fromarray(image).convert('L')
    return image


def thresholding(image):
    predicted = KMeans(n_clusters=2, random_state=9).fit_predict(
        image.reshape((image.shape[0]*image.shape[1], 1)))
    image = predicted.reshape((image.shape[0], image.shape[1]))
    return image


def thin(image):
    image = thresholding(np.array(image))
    thin_image = morphology.skeletonize(image)
    return thin_image


def predict(model, image):
    image = thin(image)
    return model.predict(image.reshape((1, -1)))[0]


if __name__ == '__main__':
    url = 'http://static8.ziroom.com/phoenix/pc/images/price/9bbd4bf71c11e7c8149485d9f1ec5adbs.png'
    print(ocr([7, 5, 4, 0], url))
