"""
专门做预测的
"""
import time

import numpy as np
import tensorflow as tf

from capt.cfg import MAX_CAPTCHA, CHAR_SET_LEN, model_path, predict_path
from capt.cnn_sys import crack_captcha_cnn, X, keep_prob
from capt.gen_captcha import wrap_gen_captcha_text_and_image
from capt.utils import convert2gray, vec2text
from PIL import Image

def hack_function(sess, predict, captcha_image):
    """
    装载完成识别内容后，
    :param sess:
    :param predict:
    :param captcha_image:
    :return:
    """
    text_list = sess.run(predict, feed_dict={X: [captcha_image], keep_prob: 1})

    text = text_list[0].tolist()
    vector = np.zeros(MAX_CAPTCHA * CHAR_SET_LEN)
    i = 0
    for n in text:
        vector[i * CHAR_SET_LEN + n] = 1
        i += 1
    return vec2text(vector)


def batch_hack_captcha():
    """
    批量生成验证码，然后再批量进行识别
    :return:
    """

    # 定义预测计算图
    output = crack_captcha_cnn()
    predict = tf.argmax(tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)

    saver = tf.train.Saver()
    with tf.Session() as sess:
        # saver = tf.train.import_meta_graph(save_model + ".meta")
        # https://github.com/jikexueyuanwiki/tensorflow-zh/blob/master/SOURCE/api_docs/python/state_ops.md#latest_checkpoint
        saver.restore(sess, tf.train.latest_checkpoint(model_path))

        stime = time.time()
        task_cnt = 1000
        right_cnt = 0

        for i in range(task_cnt):
            text, image = wrap_gen_captcha_text_and_image()
            text = text.upper()
            image = convert2gray(image)
            image = image.flatten() / 255
            predict_text = hack_function(sess, predict, image)
            if text == predict_text:
                right_cnt += 1
                print("正确预测:标记: {}  预测: {}".format(text, predict_text))
            else:
                print("错误预测:标记: {}  预测: {}".format(text, predict_text))
                pass
                # print("标记: {}  预测: {}".format(text, predict_text))
        print('task:', task_cnt, ' cost time:', (time.time() - stime), 's')
        print('right/total-----', right_cnt, '/', task_cnt)
    pass


class cl_captcha(object):

    def __init__(self):
        self.output = crack_captcha_cnn()
        self.predict = tf.argmax(tf.reshape(self.output, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
        self.saver = tf.train.Saver()
        self.sess = tf.Session()
        self.saver.restore(self.sess, tf.train.latest_checkpoint(model_path))

    def hack_capt(self, image):
        image = Image.open(image)
        image = np.array(image)
        image = convert2gray(image)
        image = image.flatten() / 255
        return hack_function(self.sess, self.predict, image)

    def __del__(self):
        self.sess.close()

    pass


def predict_captcha(image):
    image = Image.open(image)
    image = np.array(image)
    image = convert2gray(image)
    image = image.flatten() / 255

    output = crack_captcha_cnn()
    predict = tf.argmax(tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
    saver = tf.train.Saver()
    with tf.Session() as sess:
        # restore only once
        saver.restore(sess, tf.train.latest_checkpoint(model_path))
        text = hack_function(sess, predict, image)
        return text


if __name__ == '__main__':
    batch_hack_captcha()
    print('end...')
