#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import tkinter as tk
from tkinter import ttk
from PIL import Image,ImageTk
from capt.cfg import predict_path,sample_path
import os
import shutil

list_size = 10
class tk_recog_ui(object):

    def __init__(self):
        self.top = tk.Tk()
        self.labels = None
        self.inputs = None
        self.files = None

    def read_photos(self):
        if self.files is not None:
            del self.files
        files = [None]*list_size
        count = 0
        for file in os.listdir(predict_path):
            file_path = os.path.join(predict_path, file)
            files[count] = file_path
            count += 1
            if(count >= list_size):
                break
        pass
        return files

    def load_image(self):

        self.files = self.read_photos()
        if self.labels is not None:
            del self.labels
        if self.inputs is not None:
            del self.inputs
        self.labels = [None]*list_size
        self.inputs = [None]*list_size
        for num in range(list_size):
            file = self.files[num]
            #print(file)
            image = Image.open(file)
            photo = ImageTk.PhotoImage(image)
            self.labels[num] = tk.Label(self.top, image=photo)
            self.labels[num].image = photo
            self.labels[num].grid(row=num%5,column=num//5*2,columnspan=1, rowspan=1)
            self.inputs[num] = tk.Entry(self.top)
            self.inputs[num].grid(row=num%5,column=num//5*2+1,columnspan=1, rowspan=1)
        pass

        #self.top.update()

    def manual_check_captha(self):

        self.top.title("请识别图中的验证码")
        self.top.geometry('800x600')

        button = tk.Button(self.top, text="确定", width=30, height=4)
        button.bind('<Button-1>', self.on_click)
        button.grid(row=5, column=3)

        self.load_image()
        # 进入消息循环
        self.top.mainloop()

    def on_click(self, event):
        # 保存文件到新目录
        self.save_files()
        # 读取下一批文件
        self.load_image()
        pass

    def save_files(self):
        # get file names and labels
        for num in range(list_size):
            old_file = self.files[num]
            text = self.inputs[num].get()
            name = os.path.basename(old_file)
            new_name = text + '_' + name
            new_file = os.path.join(sample_path, new_name)

            print("old_file:%s, text:%s" % (old_file, text))
            print("new_file:%s" % new_file)
            # copy to the new place
            shutil.move(old_file, new_file)
            # remove the old_file

        pass

if __name__ == '__main__':
    ui = tk_recog_ui()
    ui.manual_check_captha()
    pass

