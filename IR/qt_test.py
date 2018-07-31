#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QGridLayout, QSizePolicy)

app = QApplication(sys.argv)

window = QWidget()
window.resize(1280,800)

button1 = QPushButton('1')
button1.setMaximumSize(280, 280)
button1.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
button2 = QPushButton('2')
button2.setMaximumSize(280, 280)
button2.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
button3 = QPushButton('3')
button3.setMaximumSize(280, 280)
button3.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
button4 = QPushButton('4')
button4.setMaximumSize(280, 280)
button4.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
button5 = QPushButton('5')
button5.setMaximumSize(280, 280)
button5.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
button6 = QPushButton('6')
button6.setMaximumSize(280, 280)
button6.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
button7 = QPushButton('7')
button7.setMaximumSize(280, 280)
button7.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
button8 = QPushButton('8')
button8.setMaximumSize(280, 280)
button8.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)


# ボタン配置
grbox = QGridLayout()
grbox.addWidget(button1,0,0)
grbox.addWidget(button2,0,1)
grbox.addWidget(button3,0,2)
grbox.addWidget(button4,0,3)
grbox.addWidget(button5,1,0)
grbox.addWidget(button6,1,1)
grbox.addWidget(button7,1,2)
grbox.addWidget(button8,1,3)

window.setLayout(grbox)

window.show()
sys.exit(app.exec_())
