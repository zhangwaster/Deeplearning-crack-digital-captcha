import random
from os import path
from os.path import join
import os

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image,ImageTk
from captcha.image import ImageCaptcha,ImageFilter  # pip install captcha

import capt
from capt.cfg import gen_char_set, IMAGE_WIDTH, IMAGE_HEIGHT,predict_path,sample_path
import uuid
# 验证码一般都无视大小写；验证码长度4个字符


def random_captcha_text(
        # char_set=number + alphabet + ALPHABET,
        char_set=gen_char_set,
        # char_set=number,
        captcha_size=4):
    """
    生成随机字符串，4位
    :param char_set:
    :param captcha_size:
    :return:
    """
    captcha_text = []
    for i in range(captcha_size):
        c = random.choice(char_set)
        captcha_text.append(c)
    return captcha_text

captcha_files = []

# this has to be done first
def walk_files():
    global captcha_files
    for _, _, files in os.walk(predict_path):
        captcha_files = files
    pass

# 随机读取验证码样本
def read_captcha_text_and_image():
    """
    生成字符对应的验证码
    :return:
    """
    # 随机读取一个文件
    if len(captcha_files) == 0:
        walk_files()
    rnd = random.randint(0, len(captcha_files)-1)
    captcha_file = captcha_files[rnd]
    image_path = os.path.join(predict_path, captcha_file)
    image = Image.open(image_path)
    captcha_image = np.array(image)
    captcha_text = captcha_file[0:4]
    #print("read file:%s, text:%s" % (captcha_file, captcha_text))
    return captcha_text, captcha_image

def gen_captcha_text_and_image():
    """
    生成字符对应的验证码
    :return:
    """
    image = ImageCaptcha(IMAGE_WIDTH, IMAGE_HEIGHT)

    captcha_text = random_captcha_text()
    captcha_text = ''.join(captcha_text)

    #captcha = image.generate(captcha_text)

    #background = random_color(238, 255)
    #color = random_color(0, 200, random.randint(220, 255))
    captcha = image.create_captcha_image(captcha_text, (0,124,255), (255,255,255))
    #image.create_noise_dots(im, color)
    #image.create_noise_curve(im, color)
    #captcha = captcha.filter(ImageFilter.SMOOTH)

    #captcha_image = Image.open(captcha)
    captcha_image = np.array(captcha)
    return captcha_text, captcha_image

def wrap_gen_captcha_text_and_image():
    """
    有时生成图像大小不是(60, 160, 3)
    :return:
    """
    while True:
        text, image = read_captcha_text_and_image()#gen_captcha_text_and_image()
        if image.shape != (IMAGE_HEIGHT, IMAGE_WIDTH, 4):
            continue
        return text, image


def __gen_and_save_image():
    """
    可以批量生成验证图片集，并保存到本地，方便做本地的实验
    :return:
    """
    # 先生成50个

    for i in range(5):
        text, image = wrap_gen_captcha_text_and_image()

        im = Image.fromarray(image)

        _uuid = uuid.uuid1().hex
        image_name = '__%s__%s.png' % (text, _uuid)

        img_root = join(capt.cfg.workspace, 'train')
        image_file = path.join(img_root, image_name)
        im.save(image_file)


def __demo_show_img():
    """
    使用matplotlib来显示生成的图片
    :return:
    """
    text, image = wrap_gen_captcha_text_and_image()

    print("验证码图像channel:", image.shape)  # (60, 160, 3)

    f = plt.figure()
    ax = f.add_subplot(111)
    ax.text(0.1, 0.9, text, ha='center', va='center', transform=ax.transAxes)
    plt.imshow(image)

    plt.show()


if __name__ == '__main__':
    #__gen_and_save_image()
    read_captcha_text_and_image()
    read_captcha_text_and_image()
    read_captcha_text_and_image()
    #predict_gen_captcha_text_and_image()
    pass
