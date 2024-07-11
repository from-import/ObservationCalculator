import sys
import os
import pandas as pd
import numpy as np
import math
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

def calculate_observations(exclude_point):
    data = {
        "点名": ["QZ1", "QZ2", "NK1", "NK2", "NK3", "SK1", "SK2", "SK3", "SK4"],
        "东坐标Y": [5812.000, 6068.195, 5564.067, 6153.703, 6503.179, 5543.226, 6493.799, 6228.198, 5361.498],
        "北坐标X": [2812.000, 3996.613, 4240.531, 4520.848, 4204.314, 2588.072, 2676.516, 2443.770, 2350.672]
    }

    A1 = 1.83
    B1 = 3.67
    C1 = 2

    df = pd.DataFrame(data)

    exclude_point_y = df.loc[df['点名'] == exclude_point, '东坐标Y'].values[0]
    exclude_point_x = df.loc[df['点名'] == exclude_point, '北坐标X'].values[0]

    df['dlt-Y'] = df['东坐标Y'] - exclude_point_y
    df['dlt-X'] = df['北坐标X'] - exclude_point_x

    df['atan(dY/dX)'] = df.apply(lambda row: math.atan(row['dlt-Y'] / row['dlt-X']) if row['dlt-X'] != 0 else (math.pi/2 if row['dlt-Y'] > 0 else 3*math.pi/2), axis=1)

    df['弧度_方位角'] = df.apply(lambda row:
                                 (math.pi/2 if row['dlt-X'] == 0 and row['dlt-Y'] > 0 else
                                  (3*math.pi/2 if row['dlt-X'] == 0 and row['dlt-Y'] < 0 else
                                  (row['atan(dY/dX)'] + math.pi if row['dlt-X'] < 0 else
                                  (row['atan(dY/dX)'] if row['dlt-Y'] > 0 else 2*math.pi + row['atan(dY/dX)'])))), axis=1)

    df['DEG_方位角'] = df['弧度_方位角'] * 180 / math.pi

    if exclude_point != 'QZ1':
        df['DEG_方向值'] = df['DEG_方位角'].apply(
            lambda x: x - df['DEG_方位角'][0] if (x - df['DEG_方位角'][0]) >= 0 else 360 + x - df['DEG_方位角'][0])
    else:
        df['DEG_方向值'] = df['DEG_方位角'].apply(
            lambda x: x - df['DEG_方位角'][1] if (x - df['DEG_方位角'][1]) >= 0 else 360 + x - df['DEG_方位角'][1])

    np.random.seed(0)
    df['秒_随机数'] = np.random.normal(0, A1, len(df))
    df.loc[df['点名'] == 'QZ1', '秒_随机数'] = np.nan

    df['DEG_方向观测'] = df['DEG_方向值'] + df['秒_随机数'] / 3600

    df['度'] = df['DEG_方向观测'].apply(lambda x: int(x) if not pd.isna(x) else 0)
    df['分'] = df['DEG_方向观测'].apply(lambda x: int((x - int(x)) * 60) if not pd.isna(x) else 0)
    df['秒'] = df['DEG_方向观测'].apply(lambda x: (x - int(x) - int((x - int(x)) * 60) / 60) * 3600 if not pd.isna(x) else 0)

    df['DMS_方向观测'] = df['度'] + df['分'] / 100 + df['秒'] / 10000

    df['距离_m'] = np.sqrt(df['dlt-Y']**2 + df['dlt-X']**2)

    df['距离随机数_mm'] = np.random.normal(0, B1 + C1 * df['距离_m'] / 1000)

    df['距离观测'] = df['距离_m'] + df['距离随机数_mm'] / 1000

    df.loc[df['点名'] == exclude_point, ['dlt-Y', 'dlt-X', 'atan(dY/dX)', '弧度_方位角', 'DEG_方位角', 'DEG_方向值', '秒_随机数', 'DEG_方向观测', '度', '分', '秒', 'DMS_方向观测', '距离_m', '距离随机数_mm', '距离观测']] = 0

    with open('result.txt', 'a', encoding='utf-8') as file:
        if exclude_point != "QZ1":
            file.write(f"{exclude_point}\n")

        for index, row in df.iterrows():
            if row['点名'] == exclude_point:
                continue
            file.write(f"{row['点名']},L,{row['DMS_方向观测']:.5f}\n")

        for index, row in df.iterrows():
            if row['点名'] == exclude_point:
                continue
            file.write(f"{row['点名']},S,{row['距离观测']:.5f}\n")
    print(f"结果已保存到result.txt，排除点: {exclude_point}")

def run_calculations():
    with open('result.txt', 'w', encoding='utf-8') as file:
        file.write("1.83,3.67,2\n")
        file.write("QZ1,5812,2812\n")
        file.write("QZ1\n")
        file.write("QZ2,A,85.25420\n")

    for i in ["QZ1", "QZ2", "NK1", "NK2", "NK3", "SK1", "SK2", "SK3", "SK4"]:
        calculate_observations(i)

    os.rename("result.txt", "result.in2")

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel('点击按钮进行计算并保存结果到文件', self)
        layout.addWidget(self.label)

        self.button = QPushButton('开始计算', self)
        self.button.clicked.connect(self.on_click)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.setWindowTitle('Observation Calculation')
        self.show()

    def on_click(self):
        run_calculations()
        self.label.setText('计算完成，结果已保存到 result.in2')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
