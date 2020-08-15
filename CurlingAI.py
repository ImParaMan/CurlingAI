
# ####
# -*- coding: utf-8 -*-
import socket
import time
import random
import csv

# 参赛团队名称(长度不能超过6个汉字)
name = "调参侠"

# 服务器IP地址及端口号(TCP通信)
host = '127.0.0.1'
port = 7788

# 尺寸数据(单位: m)
House_R = 1.870
Stone_R = 0.145
aim_x = 2.375
aim_y = 4.88
#查表文件
file_findcsv = 'paraman_precession_handle.csv'
file_findcsv_hit = 'paraman_hit_handle.csv'
# 中区边区分界线是中轴线左右0.75m
middle_R = 0.875

# 初始化
# 玩家编号
order = "Player1"
# 位置坐标
position = []
# 比赛状态
setstate = []
# 累计分差
scorediff = 0

# 与大本营中心距离的平方
def get_dist2(x, y):
    return (x - aim_x) ** 2 + (y - aim_y) ** 2

# 查表法得初速度, 水平偏移, 初角速度
def findCSV(target, position_float, order, setstate, mode):#mode = 0, 精确旋进  mode = 1, 选择得分方法旋进 mode = 2, 往占位壶后面旋进 #mode = 4, 往中心旋进且得分
    # 读取训练数据
    # with open('new111111_short.csv', 'r') as f:
    with open(file_findcsv, 'r', encoding='UTF-8') as f:
        reader = csv.reader(f)
        csv_data = list(reader)
    row = len(csv_data)
    # 实际点与轨迹的最小距离
    choose_offset = 0  
    choose_v = 3
    choose_omiga = 0
    no_trail = 1
    if mode == 0:
            # 阈值
        min_thresh = 0.295
        # print('mode = 0')
        # 初始化
        # print('target ' + str(target))
        min_distance0 = 50
        for q in range(10):
            for i in range(row):
                x = float(csv_data[i][1])
                sx = float(csv_data[i][3])
                sy = float(csv_data[i][4])
                mx = float(csv_data[i][5]) 
                my = float(csv_data[i][6])
                tx = float(csv_data[i][7]) 
                ty = float(csv_data[i][8])
                delta_x = target[0] - tx  + 0.018 * q * (-1)**(q + 1)           #横坐标与目标对其需平移的距离
                add_y = target[1] - ty             #纵坐标与目标的距离
                offset = x + delta_x                 #平移后的偏置
                x1 = sx + delta_x                 #平移后的起点横坐标
                y1 = sy
                x2 = mx + delta_x
                y2 = my
                x6 = tx + delta_x
                y6 = ty
                if abs(offset) > 2.35:   
                    continue
                if abs(tx-aim_x) >2.35:
                    continue
                if abs(tx - target[0]) < 0.25 and abs(ty - target[1]) < 0.4:     #横坐标范围不能再小，纵坐标根据要求
                    # 初始化最小距离
                    min_distance = 50
                    for j in range(15):    #遍历16个壶
                        if position_float[2 * j] == 0 or position_float[2 * j + 1] == 0 or\
                            ((position_float[2 * j] - tx) ** 2 + (position_float[2 * j + 1] - ty) ** 2) ** 0.5 < 0.2:
                            continue
                        if abs(float(csv_data[i][2])) < 0.6:     #角速度小于0.6近似为直线
                            x_mean = (x1 + x2) / 2
                            distance = abs(x_mean - position_float[2 * j])
                            if distance < min_distance:
                                min_distance = distance
                        else:
                            point_ball = [position_float[2 * j], position_float[2 * j + 1]]    # 场上第j个冰壶的坐标
                            delta_y = (y2 - y6) / 4     #取1/4点
                            k1 = (y1 - y2) / (x1 - x2)   #第一段直线的斜率
                            ks1 = (y2 - y6) / (x2 - x6)  #辅助线斜率
                            k2 = (k1 + 3 * ks1) / 4          #第二段直线斜率
                            y3 = y2 - delta_y            #1/4处节点y
                            x3 = x2 - (y2 - y3) / k2     #1/4处节点x
                            ks2 = (y6 - y3) / (x6 - x3)  #辅助线斜率
                            k3 = (k2 + 3 * ks2) / 4          #第三段直线斜率
                            y4 = y3 - delta_y            #1/2处节点y
                            x4 = x3 - (y3 - y4) / k3     #1/2处节点x
                            ks3 = (y6 - y4) / (x6 - x4)  #辅助线斜率
                            k4 = (k3 + 3 * ks3) / 4          #第四段直线斜率
                            y5 = y4 - delta_y            #3/4处节点y
                            x5 = x4 - (y4 - y5) / k4     #3/4处节点x
                            k5 = (y6 - y5) / (x6 - x5)  #辅助线斜率
                            for k in range(101):
                                # 将第一段轨迹100等分
                                t = (x3 - x2) / 100
                                x_test = x2 + k * t
                                y_test = k2 * (x_test - x2) + y2
                                point_test = [x_test, y_test]    #轨迹上第k个点的坐标
                                distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                            # 找到场上冰壶与该轨迹的最短距离
                                if distance < min_distance:
                                    min_distance = distance
                            for k in range(101):
                                # 将第二段轨迹100等分
                                t = (x4 - x3) / 100
                                x_test = x3 + k * t
                                y_test = k3 * (x_test - x3) + y3
                                point_test = [x_test, y_test]    #轨迹上第k个点的坐标
                                distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                            # 找到场上冰壶与该轨迹的最短距离
                                if distance < min_distance:
                                    min_distance = distance
                            for k in range(101):
                                # 将第三段轨迹100等分
                                t = (x5 - x4) / 100
                                x_test = x4 + k * t
                                y_test = k4 * (x_test - x4) + y4
                                point_test = [x_test, y_test]     #轨迹上第k个点的坐标
                                distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                            # 找到场上冰壶与该轨迹的最短距离
                                if distance < min_distance:
                                    min_distance = distance
                            for k in range(101):
                                # 将第四段轨迹100等分
                                t = (x6 - x5) / 100
                                x_test = x5 + k * t
                                y_test = k5 * (x_test - x5) + y5
                                point_test = [x_test, y_test]     #轨迹上第k个点的坐标
                                distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                            # 找到场上冰壶与该轨迹的最短距离
                                if distance < min_distance:
                                    min_distance = distance
                    # 对比各轨迹的最短距离, 保留距离目标点最近的那组数据
                    distance0 = ((target[0] - tx) ** 2 + (target[1] - ty) ** 2) ** 0.5
                    if min_distance > min_thresh and min_distance0 > distance0:
                        min_distance0 = distance0
                        # print('min_distance ' + str(min_distance))
                        # print('min_distance0 ' + str(min_distance0))
                        choose_offset = offset
                        choose_v = float(csv_data[i][0]) - add_y * 4 / 35
                        choose_omiga = float(csv_data[i][2])
                        if  min_distance > 0.34 and min_distance0 < 0.08:
                            # print('break')
                            break
            if min_distance0 < 10:
                no_trail = 0
                v_init = choose_v
                offset = choose_offset
                w_init = choose_omiga
                break        
            else:
                no_trail = 1
                # print('notrail')
                v_init = choose_v
                offset = choose_offset
                w_init = choose_omiga
   
    elif mode == 1:
        # print('mode == 1')
        min_thresh = 0.308
        min_distance0 = 50
        nearest_distance2 = 1000
        for j in range(8):   #找到场上对方冰壶离中心最近的距离
            if InitiativeOrGote(order, setstate):   #后手
                point_ball = [position_float[4 * j], position_float[4 * j + 1]]
                point_distance2 = (point_ball[0] - aim_x) ** 2 + (point_ball[1] - aim_y) ** 2
                if point_distance2 < nearest_distance2:
                    nearest_distance2 = point_distance2
            else:
                point_ball = [position_float[4 * j + 2], position_float[4 * j + 3]]
                point_distance2 = (point_ball[0] - aim_x) ** 2 + (point_ball[1] - aim_y) ** 2
                if point_distance2 < nearest_distance2:
                    nearest_distance2 = point_distance2
        # print('nearest_distance2 ' + str(nearest_distance2))
        bk = []
        min_distance0 = 50
        for i in range(15):
            if(position_float[2 * i + 1] > 6.75):
                bk.append(position_float[2 * i])
        l = len(bk)
        if l == 0:
            bk.append(2.37)
        for i in range(row):
            offset = float(csv_data[i][1])
            sx = float(csv_data[i][3])
            sy = float(csv_data[i][4])
            mx = float(csv_data[i][5]) 
            my = float(csv_data[i][6])
            tx = float(csv_data[i][7]) 
            ty = float(csv_data[i][8])

            x1 = sx
            y1 = sy
            x2 = mx
            y2 = my
            x6 = tx
            y6 = ty
            delta_y = (y2 - y6) / 4     #取1/4点
            if abs(offset) > 2.23:   
                continue
            if abs(tx-aim_x) >2.35:
                continue
            # 寻找可以得分的打法
            th = 1.5
            if nearest_distance2 > 1:
                th = 1
            else:
                th = nearest_distance2 / 1.5
            if float(tx - aim_x) ** 2 + (ty - aim_y) ** 2 < th and float(tx - aim_x) ** 2 + (ty - aim_y) ** 2 < 3.5:
                # 初始化最小距离
                min_distance = 44.5
                for j in range(16):    #遍历16个壶
                    if position_float[2 * j] == 0 or position_float[2 * j + 1] == 0:
                        continue
                    if abs(float(csv_data[i][2])) < 0.8:     #角速度小于1近似为直线
                        x_mean = (x1 + x2) / 2
                        distance = abs(x_mean - position_float[2 * j])
                        if distance < min_distance:
                            min_distance = distance
                    else:
                        k1 = (y1 - y2) / (x1 - x2)   #第一段直线的斜率
                        ks1 = (y2 - y6) / (x2 - x6)  #辅助线斜率
                        k2 = (k1 + 3 * ks1) / 4          #第二段直线斜率
                        y3 = y2 - delta_y            #1/4处节点y
                        x3 = x2 - (y2 - y3) / k2     #1/4处节点x
                        ks2 = (y6 - y3) / (x6 - x3)  #辅助线斜率
                        k3 = (k2 + 3 * ks2) / 4          #第三段直线斜率
                        y4 = y3 - delta_y            #1/2处节点y
                        x4 = x3 - (y3 - y4) / k3     #1/2处节点x
                        ks3 = (y6 - y4) / (x6 - x4)  #辅助线斜率
                        k4 = (k3 + 3 * ks3) / 4          #第四段直线斜率
                        y5 = y4 - delta_y            #3/4处节点y
                        x5 = x4 - (y4 - y5) / k4     #3/4处节点x
                        k5 = (y6 - y5) / (x6 - x5)  #辅助线斜率
                        point_ball = [position_float[2 * j], position_float[2 * j + 1]]    # 场上第j个冰壶的坐标
                        for k in range(101):
                            # 将第一段轨迹100等分
                            t = (x3 - x2) / 100
                            x_test = x2 + k * t
                            y_test = k2 * (x_test - x2) + y2
                            point_test = [x_test, y_test]    #轨迹上第k个点的坐标
                            distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                        # 找到场上冰壶与该轨迹的最短距离
                            if distance < min_distance:
                                min_distance = distance
                        for k in range(101):
                            # 将第二段轨迹100等分
                            t = (x4 - x3) / 100
                            x_test = x3 + k * t
                            y_test = k3 * (x_test - x3) + y3
                            point_test = [x_test, y_test]    #轨迹上第k个点的坐标
                            distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                        # 找到场上冰壶与该轨迹的最短距离
                            if distance < min_distance:
                                min_distance = distance
                        for k in range(101):
                            # 将第三段轨迹100等分
                            t = (x5 - x4) / 100
                            x_test = x4 + k * t
                            y_test = k4 * (x_test - x4) + y4
                            point_test = [x_test, y_test]     #轨迹上第k个点的坐标
                            distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                        # 找到场上冰壶与该轨迹的最短距离
                            if distance < min_distance:
                                min_distance = distance
                        for k in range(101):
                            # 将第四段轨迹100等分
                            t = (x6 - x5) / 100
                            x_test = x5 + k * t
                            y_test = k5 * (x_test - x5) + y5
                            point_test = [x_test, y_test]     #轨迹上第k个点的坐标
                            distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                        # 找到场上冰壶与该轨迹的最短距离
                            if distance < min_distance:
                                min_distance = distance
                # 对比各轨迹的最短距离, 保留最小距离最大的那组数据
                distance0 = 50   #初始化
                if l == 0:
                    distance0 = 0
                else:
                    for a in range(l):
                        distance_x = abs(bk[a] - tx)
                        if distance0 > distance_x:
                            distance0 = distance_x
                if min_distance > min_thresh and min_distance0 >= distance0:    #不碰撞且横坐标离占位球更近
                    min_distance0 = distance0
                    choose_offset = offset
                    choose_v = float(csv_data[i][0])
                    choose_omiga = float(csv_data[i][2])
                    # print('min_distance ' + str(min_distance))
                    # print('min_distance0 ' + str(min_distance0))
                    if  min_distance > 0.32 and min_distance0 < 0.06:
                        # print('break')
                        break
                    if  min_distance > 0.34 and min_distance0 < 0.08:
                        # print('break')
                        break
                    if  min_distance > 0.38 and min_distance0 < 0.14:
                        # print('break')
                        break
        if min_distance0 <10:
            no_trail = 0        
        else:
            no_trail = 1
            # print('notrail')
        v_init = choose_v
        offset = choose_offset
        w_init = choose_omiga
   
    elif mode == 2:
        # print('mode = 2')
        min_thresh = 0.308
        bk = []
        max_score = 0
        no_trail = 1
        no_better = 1
        # 找占位
        for i in range(16):
            if(position_float[2 * i + 1] > 6.75):
                bk.append(position_float[2 * i])
        l = len(bk)
        if l == 0:
            bk.append(2.37)
        # 找大本营里
        AvoidOffset = []
        for p in range(16): 
            point_ball = [position_float[2 * p], position_float[2 * p + 1]]
            if ((point_ball[0] - aim_x) ** 2 + (point_ball[1] - aim_y) ** 2) < 3.5:
                AvoidOffset.append(position_float[2 * p])
        length = len(AvoidOffset)
        if length == 0:
            AvoidOffset.append(0)
        for i in range(row):
            offset = float(csv_data[i][1])
            sx = float(csv_data[i][3])
            sy = float(csv_data[i][4])
            mx = float(csv_data[i][5]) 
            my = float(csv_data[i][6])
            tx = float(csv_data[i][7]) 
            ty = float(csv_data[i][8])
            x1 = sx
            y1 = sy
            x2 = mx
            y2 = my
            x6 = tx
            y6 = ty
            if abs(offset) > 2.35:   
                continue
            if abs(tx-aim_x) >2.35:
                continue
            # 寻找横坐标离大本营壶较远的位置
            flag = 0
            for a in range(length):
                if abs(tx - AvoidOffset[a]) < 0.15:
                    flag = 1
                    break
            if flag == 1:
                continue
            # 寻找占位壶后面的位置
            b = 0
            for a in range(l):
                if a > 0:
                    if abs(bk[a - 1] - bk[a]) < 0.2:
                        continue 
                b = b + 1 # 不超过五个，容易出错
                if b > 5:
                    break 
                if (tx - aim_x) ** 2 + (ty - aim_y) ** 2 < 3.5 and abs(tx - bk[a]) < 0.25:
                    # 初始化最小距离
                    min_distance = 50
                    for j in range(15):    #遍历16个壶
                        if position_float[2 * j] == 0 or position_float[2 * j + 1] == 0 or\
                            ((position_float[2 * j] - tx) ** 2 + (position_float[2 * j + 1] - ty) ** 2) ** 0.5 < 0.2:
                            continue
                        if abs(float(csv_data[i][2])) < 1:     #角速度小于1近似为直线
                            x_mean = (x1 + x2) / 2
                            distance = abs(x_mean - position_float[2 * j])
                            if distance < min_distance:
                                min_distance = distance
                        else:
                            point_ball = [position_float[2 * j], position_float[2 * j + 1]]    # 场上第j个冰壶的坐标
                            delta_y = (y2 - y6) / 4     #取1/4点
                            k1 = (y1 - y2) / (x1 - x2)   #第一段直线的斜率
                            ks1 = (y2 - y6) / (x2 - x6)  #辅助线斜率
                            k2 = (k1 + 3 * ks1) / 4          #第二段直线斜率
                            y3 = y2 - delta_y            #1/4处节点y
                            x3 = x2 - (y2 - y3) / k2     #1/4处节点x
                            ks2 = (y6 - y3) / (x6 - x3)  #辅助线斜率
                            k3 = (k2 + 3 * ks2) / 4          #第三段直线斜率
                            y4 = y3 - delta_y            #1/2处节点y
                            x4 = x3 - (y3 - y4) / k3     #1/2处节点x
                            ks3 = (y6 - y4) / (x6 - x4)  #辅助线斜率
                            k4 = (k3 + 3 * ks3) / 4          #第四段直线斜率
                            y5 = y4 - delta_y            #3/4处节点y
                            x5 = x4 - (y4 - y5) / k4     #3/4处节点x
                            k5 = (y6 - y5) / (x6 - x5)  #辅助线斜率
                            for k in range(101):
                                # 将第一段轨迹100等分
                                t = (x3 - x2) / 100
                                x_test = x2 + k * t
                                y_test = k2 * (x_test - x2) + y2
                                point_test = [x_test, y_test]    #轨迹上第k个点的坐标
                                distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                            # 找到场上冰壶与该轨迹的最短距离
                                if distance < min_distance:
                                    min_distance = distance
                            for k in range(101):
                                # 将第二段轨迹100等分
                                t = (x4 - x3) / 100
                                x_test = x3 + k * t
                                y_test = k3 * (x_test - x3) + y3
                                point_test = [x_test, y_test]    #轨迹上第k个点的坐标
                                distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                            # 找到场上冰壶与该轨迹的最短距离
                                if distance < min_distance:
                                    min_distance = distance
                            for k in range(101):
                                # 将第三段轨迹100等分
                                t = (x5 - x4) / 100
                                x_test = x4 + k * t
                                y_test = k4 * (x_test - x4) + y4
                                point_test = [x_test, y_test]     #轨迹上第k个点的坐标
                                distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                            # 找到场上冰壶与该轨迹的最短距离
                                if distance < min_distance:
                                    min_distance = distance
                            for k in range(101):
                                # 将第四段轨迹100等分
                                t = (x6 - x5) / 100
                                x_test = x5 + k * t
                                y_test = k5 * (x_test - x5) + y5
                                point_test = [x_test, y_test]     #轨迹上第k个点的坐标
                                distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                            # 找到场上冰壶与该轨迹的最短距离
                                if distance < min_distance:
                                    min_distance = distance
                    # 对比各轨迹的最短距离, 保留距离目标点纵坐标最近的那组数据
                    distanceY = abs(aim_y - ty)
                    if abs(bk[a] - tx) < 0.14 and distanceY < 1.4 and min_distance > min_thresh:
                        score = (min_distance - min_thresh) * 2 - abs(bk[a] - tx)
                        if max_score < score:
                            no_trail = 0
                            max_score = score
                            choose_offset = offset
                            choose_v = float(csv_data[i][0])
                            choose_omiga = float(csv_data[i][2])
                            # print('min_distance ' + str(min_distance))
                            # print('max_score ' +  str(max_score))
                            if aim_y - ty < 0.2:
                                if  (min_distance > 0.32 and abs(tx - aim_x) < 0.5) or (min_distance > 0.36):
                                    # print('break')
                                    v_init = choose_v
                                    offset = choose_offset
                                    w_init = choose_omiga  
                                    return v_init, offset, w_init, no_trail
                            else:
                                if  (min_distance > 0.32 and distanceY < 0.35) or (min_distance > 0.34 and distanceY < 0.5):
                                    no_better = 0
                                    re_offset = offset
                                    re_v = float(csv_data[i][0])
                                    re_omiga = float(csv_data[i][2])
        if no_better == 0:
            v_init = re_offset
            offset = re_v
            w_init = re_omiga  
        elif no_trail == 0:
            v_init = choose_v
            offset = choose_offset
            w_init = choose_omiga  
        else:
            # print('notrail')
            v_init = 3
            offset = 0
            w_init = 0
   
    return v_init, offset, w_init, no_trail

#往中心旋
def FindCSVToAim(position_float, order, setstate):
    # 读取训练数据
    # with open('new111111_short.csv', 'r') as f:
    with open(file_findcsv, 'r', encoding='UTF-8') as f:
        reader = csv.reader(f)
        csv_data = list(reader)
    row = len(csv_data)
    # 初始化
    choose_offset = 0  
    choose_v = 3
    choose_omiga = 0
    no_trail1 = 0
    no_trail2 = 0
    distance0 = 0
    min_thresh = 0.308
    min_distance0 = 50
    nearest_distance2 = 1000
    nearest_y = aim_y
    for j in range(8):   #找到场上对方冰壶离中心最近的距离
        if InitiativeOrGote(order, setstate):   #后手
            point_ball = [position_float[4 * j], position_float[4 * j + 1]]
            point_distance2 = (point_ball[0] - aim_x) ** 2 + (point_ball[1] - aim_y) ** 2
            if point_distance2 < nearest_distance2:
                nearest_distance2 = point_distance2
                nearest_y = point_ball[1]
        else:
            point_ball = [position_float[4 * j + 2], position_float[4 * j + 3]]
            point_distance2 = (point_ball[0] - aim_x) ** 2 + (point_ball[1] - aim_y) ** 2
            if point_distance2 < nearest_distance2:
                nearest_distance2 = point_distance2
                nearest_y = point_ball[1]
    # print('nearest_distance2 ' + str(nearest_distance2))
    if nearest_distance2 < 0.4 and aim_y - nearest_y < 0.2:  # 对方壶在中心，输出notrail1
        # print('notrail1')
        no_trail1 = 1
        v_init = choose_v
        offset = choose_offset
        w_init = choose_omiga
        return v_init, offset, w_init, no_trail1, no_trail2
    min_distance0 = 50
    for i in range(row):
        offset = float(csv_data[i][1])
        sx = float(csv_data[i][3])
        sy = float(csv_data[i][4])
        mx = float(csv_data[i][5]) 
        my = float(csv_data[i][6])
        tx = float(csv_data[i][7]) 
        ty = float(csv_data[i][8])

        x1 = sx
        y1 = sy
        x2 = mx
        y2 = my
        x6 = tx
        y6 = ty
        delta_y = (y2 - y6) / 4     #取1/4点
        if abs(offset) > 2.23:   
            continue
        if abs(tx-aim_x) >2.35:
            continue
        # 寻找可以得分的打法
        th = 1.5
        if nearest_distance2 > 1:
            th = 1
        else:
            th = nearest_distance2 / 1.5
        if float(tx - aim_x) ** 2 + (ty - aim_y) ** 2 < th and float(tx - aim_x) ** 2 + (ty - aim_y) ** 2 < 3.5:
            # 初始化最小距离
            min_distance = 44.5
            for j in range(16):    #遍历16个壶
                if position_float[2 * j] == 0 and position_float[2 * j + 1] == 0:
                    continue
                if abs(float(csv_data[i][2])) < 0.8:     #角速度小于1近似为直线
                    x_mean = (x1 + x2) / 2
                    distance = abs(x_mean - position_float[2 * j])
                    if distance < min_distance:
                        min_distance = distance
                else:
                    k1 = (y1 - y2) / (x1 - x2)   #第一段直线的斜率
                    ks1 = (y2 - y6) / (x2 - x6)  #辅助线斜率
                    k2 = (k1 + 3 * ks1) / 4          #第二段直线斜率
                    y3 = y2 - delta_y            #1/4处节点y
                    x3 = x2 - (y2 - y3) / k2     #1/4处节点x
                    ks2 = (y6 - y3) / (x6 - x3)  #辅助线斜率
                    k3 = (k2 + 3 * ks2) / 4          #第三段直线斜率
                    y4 = y3 - delta_y            #1/2处节点y
                    x4 = x3 - (y3 - y4) / k3     #1/2处节点x
                    ks3 = (y6 - y4) / (x6 - x4)  #辅助线斜率
                    k4 = (k3 + 3 * ks3) / 4          #第四段直线斜率
                    y5 = y4 - delta_y            #3/4处节点y
                    x5 = x4 - (y4 - y5) / k4     #3/4处节点x
                    k5 = (y6 - y5) / (x6 - x5)  #辅助线斜率
                    point_ball = [position_float[2 * j], position_float[2 * j + 1]]    # 场上第j个冰壶的坐标
                    for k in range(101):
                        # 将第一段轨迹100等分
                        t = (x3 - x2) / 100
                        x_test = x2 + k * t
                        y_test = k2 * (x_test - x2) + y2
                        point_test = [x_test, y_test]    #轨迹上第k个点的坐标
                        distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                    # 找到场上冰壶与该轨迹的最短距离
                        if distance < min_distance:
                            min_distance = distance
                    for k in range(101):
                        # 将第二段轨迹100等分
                        t = (x4 - x3) / 100
                        x_test = x3 + k * t
                        y_test = k3 * (x_test - x3) + y3
                        point_test = [x_test, y_test]    #轨迹上第k个点的坐标
                        distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                    # 找到场上冰壶与该轨迹的最短距离
                        if distance < min_distance:
                            min_distance = distance
                    for k in range(101):
                        # 将第三段轨迹100等分
                        t = (x5 - x4) / 100
                        x_test = x4 + k * t
                        y_test = k4 * (x_test - x4) + y4
                        point_test = [x_test, y_test]     #轨迹上第k个点的坐标
                        distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                    # 找到场上冰壶与该轨迹的最短距离
                        if distance < min_distance:
                            min_distance = distance
                    for k in range(101):
                        # 将第四段轨迹100等分
                        t = (x6 - x5) / 100
                        x_test = x5 + k * t
                        y_test = k5 * (x_test - x5) + y5
                        point_test = [x_test, y_test]     #轨迹上第k个点的坐标
                        distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                    # 找到场上冰壶与该轨迹的最短距离
                        if distance < min_distance:
                            min_distance = distance
            # 对比各轨迹的最短距离, 保留最小距离最大的那组数据
            distance0 = ((tx - aim_x) ** 2 + (ty - aim_y) ** 2) ** 0.5
            if min_distance > min_thresh and min_distance0 >= distance0:    #不碰撞且横坐标离占位球更近
                min_distance0 = distance0
                choose_offset = offset
                choose_v = float(csv_data[i][0])
                choose_omiga = float(csv_data[i][2])
                if min_distance > 0.32 and min_distance0 < 0.2:
                    break
                # print('min_distance ' + str(min_distance))
                # print('min_distance0 ' + str(min_distance0))
    if min_distance0 <10:
        no_trail2 = 0        
    else:
        no_trail2 = 1
        # print('notrail2')
    v_init = choose_v
    offset = choose_offset
    w_init = choose_omiga
    return v_init, offset, w_init, no_trail1, no_trail2

def FindCSVAvoid(position_float, order, setstate):    # 得分且躲开自己的壶
    # 读取训练数据
    with open(file_findcsv, 'r', encoding='UTF-8') as f:
        reader = csv.reader(f)
        csv_data = list(reader)
    row = len(csv_data)
    # 初始化
    choose_offset = 0  
    choose_v = 3
    choose_omiga = 0
    no_trail = 0
    min_thresh = 0.31
    maxall = 0
    nearest_distance2 = 1000
    MyOffset = []
    for j in range(8):   #找到场上对方冰壶离中心最近的距离
        if InitiativeOrGote(order, setstate):   #后手
            point_ball = [position_float[4 * j], position_float[4 * j + 1]]
            my_ball = [position_float[4 * j +2], position_float[4 * j + 3]]
            if ((my_ball[0] - aim_x) ** 2 + (my_ball[1] - aim_y) ** 2) < 3.5:
                MyOffset.append(position_float[4 * j])
            point_distance2 = (point_ball[0] - aim_x) ** 2 + (point_ball[1] - aim_y) ** 2
            if point_distance2 < nearest_distance2:
                nearest_distance2 = point_distance2
        else:
            point_ball = [position_float[4 * j + 2], position_float[4 * j + 3]]
            my_ball = [position_float[4 * j], position_float[4 * j + 1]]
            if ((my_ball[0] - aim_x) ** 2 + (my_ball[1] - aim_y) ** 2) < 3.5:
                MyOffset.append(position_float[4 * j])
            point_distance2 = (point_ball[0] - aim_x) ** 2 + (point_ball[1] - aim_y) ** 2
            if point_distance2 < nearest_distance2:
                nearest_distance2 = point_distance2
    l = len(MyOffset)
    if l == 0:
        MyOffset.append(0)
    # print('nearest_distance2 ' + str(nearest_distance2))
    min_distance0 = 50
    for i in range(row):
        offset = float(csv_data[i][1])
        sx = float(csv_data[i][3])
        sy = float(csv_data[i][4])
        mx = float(csv_data[i][5]) 
        my = float(csv_data[i][6])
        tx = float(csv_data[i][7]) 
        ty = float(csv_data[i][8])

        x1 = sx
        y1 = sy
        x2 = mx
        y2 = my
        x6 = tx
        y6 = ty
        delta_y = (y2 - y6) / 4     #取1/4点
        if abs(offset) > 2.23:   
            continue
        if abs(tx-aim_x) >2.35:
            continue
        # 寻找可以得分的打法
        th = 1.5
        if nearest_distance2 > 1:
            th = 1
        else:
            th = nearest_distance2 / 1.5
        
        # 寻找横坐标离己方壶较远的位置
        flag = 0
        for a in range(l):
            if abs(tx - MyOffset[a]) < 0.2:
                flag = 1
                break
        if flag == 1:
            continue

        if float(tx - aim_x) ** 2 + (ty - aim_y) ** 2 < th and float(tx - aim_x) ** 2 + (ty - aim_y) ** 2 < 3.5:
            # 初始化最小距离
            min_distance = 44.5
            for j in range(16):    #遍历16个壶
                if position_float[2 * j] == 0 or position_float[2 * j + 1] == 0:
                    continue
                if abs(float(csv_data[i][2])) < 0.8:     #角速度小于1近似为直线
                    x_mean = (x1 + x2) / 2
                    distance = abs(x_mean - position_float[2 * j])
                    if distance < min_distance:
                        min_distance = distance
                else:
                    k1 = (y1 - y2) / (x1 - x2)   #第一段直线的斜率
                    ks1 = (y2 - y6) / (x2 - x6)  #辅助线斜率
                    k2 = (k1 + 3 * ks1) / 4          #第二段直线斜率
                    y3 = y2 - delta_y            #1/4处节点y
                    x3 = x2 - (y2 - y3) / k2     #1/4处节点x
                    ks2 = (y6 - y3) / (x6 - x3)  #辅助线斜率
                    k3 = (k2 + 3 * ks2) / 4          #第三段直线斜率
                    y4 = y3 - delta_y            #1/2处节点y
                    x4 = x3 - (y3 - y4) / k3     #1/2处节点x
                    ks3 = (y6 - y4) / (x6 - x4)  #辅助线斜率
                    k4 = (k3 + 3 * ks3) / 4          #第四段直线斜率
                    y5 = y4 - delta_y            #3/4处节点y
                    x5 = x4 - (y4 - y5) / k4     #3/4处节点x
                    k5 = (y6 - y5) / (x6 - x5)  #辅助线斜率
                    point_ball = [position_float[2 * j], position_float[2 * j + 1]]    # 场上第j个冰壶的坐标
                    for k in range(101):
                        # 将第一段轨迹100等分
                        t = (x3 - x2) / 100
                        x_test = x2 + k * t
                        y_test = k2 * (x_test - x2) + y2
                        point_test = [x_test, y_test]    #轨迹上第k个点的坐标
                        distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                    # 找到场上冰壶与该轨迹的最短距离
                        if distance < min_distance:
                            min_distance = distance
                    for k in range(101):
                        # 将第二段轨迹100等分
                        t = (x4 - x3) / 100
                        x_test = x3 + k * t
                        y_test = k3 * (x_test - x3) + y3
                        point_test = [x_test, y_test]    #轨迹上第k个点的坐标
                        distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                    # 找到场上冰壶与该轨迹的最短距离
                        if distance < min_distance:
                            min_distance = distance
                    for k in range(101):
                        # 将第三段轨迹100等分
                        t = (x5 - x4) / 100
                        x_test = x4 + k * t
                        y_test = k4 * (x_test - x4) + y4
                        point_test = [x_test, y_test]     #轨迹上第k个点的坐标
                        distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                    # 找到场上冰壶与该轨迹的最短距离
                        if distance < min_distance:
                            min_distance = distance
                    for k in range(101):
                        # 将第四段轨迹100等分
                        t = (x6 - x5) / 100
                        x_test = x5 + k * t
                        y_test = k5 * (x_test - x5) + y5
                        point_test = [x_test, y_test]     #轨迹上第k个点的坐标
                        distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                    # 找到场上冰壶与该轨迹的最短距离
                        if distance < min_distance:
                            min_distance = distance
            maxdistance = 0
            for a in range(l):
                mydistance = abs(tx - MyOffset[a])
                if maxdistance < mydistance:
                    maxdistance = mydistance
            # 对比各轨迹的最短距离, 保留最小距离最大的那组数据
            if min_distance > min_thresh and maxdistance > maxall:    #不碰撞
                min_distance0 = min_distance
                maxall = maxdistance
                choose_offset = offset
                choose_v = float(csv_data[i][0])
                choose_omiga = float(csv_data[i][2])
                #print('maxall ' + str(maxall))
    if min_distance0 < 10:
        no_trail = 0        
    else:
        no_trail = 1
        # print('notrail')
    v_init = choose_v
    offset = choose_offset
    w_init = choose_omiga
    return v_init, offset, w_init, no_trail

# 查表法推
def findCSV_push(target, position_float,delta):   #delta：表示推的距离
    # print('target ' + str(target))
    # print('delta ' + str(delta))
    with open(file_findcsv, 'r') as f:
        reader = csv.reader(f)
        csv_data = list(reader)
    row = int(len(csv_data))
    # 初始化
    choose_offset = 0  
    choose_v = 3
    choose_omiga = 0
    min_thresh = 0.305            #理论点与轨迹的最小距离
    distance0 = 50   #初始化
    min_distance0 = 50    #初始化与目标壶的最小距离
    for i in range(row):   #遍历表格中的每一行
        x = float(csv_data[i][1])            #初始偏置
        omiga = float(csv_data[i][2])
        mx = float(csv_data[i][5]) 
        my = float(csv_data[i][6])
        tx = float(csv_data[i][7]) 
        ty = float(csv_data[i][8])
        delta_x = target[0] - tx             #横坐标与目标对其需平移的距离
        offset = x + delta_x                 #平移后的偏置
        x1 = aim_x + offset                  #平移后的起点横坐标
        y1 = 32.48
        x2 = mx + delta_x
        y2 = my
        x6 = tx + delta_x
        y6 = ty
        if delta > 1.2:
            delta = 1.2
        delta_v = 0.1 + delta / 1.5
        delta_offset = delta_v * omiga / 400
        if abs(offset) > 2.1:   
            continue
        if abs(ty - target[1]) < 0.5:   #寻找目标点附近的打法
            min_distance = 50
            for j in range(16):    #遍历16个壶0
                if position_float[2 * j] == 0 and position_float[2 * j + 1] == 0:
                    continue
                if abs(position_float[2 * j] - target[0]) < 0.1 and abs(position_float[2 * j + 1] - target[1]) < 0.2:
                    continue
                if abs(float(csv_data[i][2])) <= 1:     #角速度小于1近似为直线
                    x_mean = (x1 + x2) / 2
                    distance = abs(x_mean - position_float[2 * j])
                    if distance < min_distance:
                        min_distance = distance
                else:
                    point_ball = [position_float[2 * j], position_float[2 * j + 1]]    # 场上第j个冰壶的坐标
                    delta_y = (y2 - y6) / 4     #取1/4点
                    k1 = (y1 - y2) / (x1 - x2)   #第一段直线的斜率
                    ks1 = (y2 - y6) / (x2 - x6)  #辅助线斜率
                    k2 = (k1 + 3 * ks1) / 4          #第二段直线斜率
                    y3 = y2 - delta_y            #1/4处节点y
                    x3 = x2 - (y2 - y3) / k2     #1/4处节点x
                    ks2 = (y6 - y3) / (x6 - x3)  #辅助线斜率
                    k3 = (k2 + 3 * ks2) / 4          #第三段直线斜率
                    y4 = y3 - delta_y            #1/2处节点y
                    x4 = x3 - (y3 - y4) / k3     #1/2处节点x
                    ks3 = (y6 - y4) / (x6 - x4)  #辅助线斜率
                    k4 = (k3 + 3 * ks3) / 4          #第四段直线斜率
                    y5 = y4 - delta_y            #3/4处节点y
                    x5 = x4 - (y4 - y5) / k4     #3/4处节点x
                    k5 = (y6 - y5) / (x6 - x5)  #辅助线斜率delta_y = (y2 - y6) / 4     #取1/4点
                    k1 = (y1 - y2) / (x1 - x2)   #第一段直线的斜率
                    ks1 = (y2 - y6) / (x2 - x6)  #辅助线斜率
                    k2 = (k1 + 3 * ks1) / 4          #第二段直线斜率
                    y3 = y2 - delta_y            #1/4处节点y
                    x3 = x2 - (y2 - y3) / k2     #1/4处节点x
                    ks2 = (y6 - y3) / (x6 - x3)  #辅助线斜率
                    k3 = (k2 + 3 * ks2) / 4          #第三段直线斜率
                    y4 = y3 - delta_y            #1/2处节点y
                    x4 = x3 - (y3 - y4) / k3     #1/2处节点x
                    ks3 = (y6 - y4) / (x6 - x4)  #辅助线斜率
                    k4 = (k3 + 3 * ks3) / 4          #第四段直线斜率
                    y5 = y4 - delta_y            #3/4处节点y
                    x5 = x4 - (y4 - y5) / k4     #3/4处节点x
                    k5 = (y6 - y5) / (x6 - x5)  #辅助线斜率
                    for k in range(101):
                        # 将第一段轨迹100等分
                        t = (x3 - x2) / 100
                        x_test = x2 + k * t
                        y_test = k2 * (x_test - x2) + y2
                        point_test = [x_test, y_test]    #轨迹上第k个点的坐标
                        distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                    # 找到场上冰壶与该轨迹的最短距离
                        if distance < min_distance:
                            min_distance = distance
                    for k in range(101):
                        # 将第二段轨迹100等分
                        t = (x4 - x3) / 100
                        x_test = x3 + k * t
                        y_test = k3 * (x_test - x3) + y3
                        point_test = [x_test, y_test]    #轨迹上第k个点的坐标
                        distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                    # 找到场上冰壶与该轨迹的最短距离
                        if distance < min_distance:
                            min_distance = distance
                    for k in range(101):
                        # 将第三段轨迹100等分
                        t = (x5 - x4) / 100
                        x_test = x4 + k * t
                        y_test = k4 * (x_test - x4) + y4
                        point_test = [x_test, y_test]     #轨迹上第k个点的坐标
                        distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                    # 找到场上冰壶与该轨迹的最短距离
                        if distance < min_distance:
                            min_distance = distance
                    for k in range(101):
                        # 将第四段轨迹100等分
                        t = (x6 - x5) / 100
                        x_test = x5 + k * t
                        y_test = k5 * (x_test - x5) + y5
                        point_test = [x_test, y_test]     #轨迹上第k个点的坐标
                        distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                    # 找到场上冰壶与该轨迹的最短距离
                        if distance < min_distance:
                            min_distance = distance
            distance0 = abs(target[1] - ty)
            if min_distance > min_thresh and min_distance0 > distance0:        #对比各轨迹，保留距离目标壶最小的那组数据
                min_distance0 = distance0
                # print('min_distance ' + str(min_distance))
                # print('min_distance0 ' + str(min_distance0))
                # print('delta_v ' + str(delta_v))
                # print('delta_offset ' + str(delta_offset))
                choose_offset = offset + delta_offset
                choose_v = float(csv_data[i][0]) + delta_v
                choose_omiga = omiga
    if min_distance0 < 10:
        no_trail = 0        
        v_init = choose_v
        offset = choose_offset
        w_init = choose_omiga
    else:
        no_trail = 1
        # print('notrail')
        v_init = 3
        offset = 0
        w_init = 0
    return v_init, offset, w_init, no_trail

# 函数思路：通过撞击后落位的坐标判断球往左，往右还是打定，根据要求得到符合的参数
def findCSV_hit(target, position_float,roll = 0):     #roll:0=打定   1：打飞
    # print("findCSV_hit")
    with open(file_findcsv_hit, 'r') as f:
        reader = csv.reader(f)
        csv_data = list(reader)
    row = int(len(csv_data))
    # 初始化
    choose_offset = 0  
    choose_v = 3
    choose_omiga = 0
    min_thresh = 0.308            #理论点与轨迹的最小距离
    distance0 = 50   #初始化
    min_distance0 = 50    #初始化与目标壶的最小距离
    if roll == 0:  #打定
        for i in range(row):   #遍历表格中的每一行
            x = float(csv_data[i][1])            #初始偏置
            mx = float(csv_data[i][3]) 
            my = float(csv_data[i][4])
            tx = float(csv_data[i][5]) 
            ty = float(csv_data[i][6])
            flag = float(csv_data[i][9])
            delta_x = target[0] - tx             #横坐标与目标对其需平移的距离
            offset = x + delta_x                 #平移后的偏置
            x1 = aim_x + offset                  #平移后的起点横坐标
            y1 = 32.48
            x2 = mx + delta_x
            y2 = my
            x6 = tx + delta_x
            y6 = ty
            if abs(offset) > 2.23:   
                continue
            if abs(ty - target[1]) < 0.5 and flag == 1:   #寻找目标点附近的打法
                min_distance = 50
                for j in range(16):    #遍历16个壶0
                    if position_float[2 * j] == 0 and position_float[2 * j + 1] == 0:
                        continue
                    if abs(position_float[2 * j] - target[0]) < 0.1 and abs(position_float[2 * j + 1] - target[1]) < 0.2:
                        continue
                    if abs(float(csv_data[i][2])) <= 1:     #角速度小于1近似为直线
                        x_mean = (x1 + x2) / 2
                        distance = abs(x_mean - position_float[2 * j])
                        if distance < min_distance:
                            min_distance = distance
                    else:
                        point_ball = [position_float[2 * j], position_float[2 * j + 1]]    # 场上第j个冰壶的坐标
                        delta_y = (y2 - y6) / 4     #取1/4点
                        k1 = (y1 - y2) / (x1 - x2)   #第一段直线的斜率
                        ks1 = (y2 - y6) / (x2 - x6)  #辅助线斜率
                        k2 = (k1 + 3 * ks1) / 4          #第二段直线斜率
                        y3 = y2 - delta_y            #1/4处节点y
                        x3 = x2 - (y2 - y3) / k2     #1/4处节点x
                        ks2 = (y6 - y3) / (x6 - x3)  #辅助线斜率
                        k3 = (k2 + 3 * ks2) / 4          #第三段直线斜率
                        y4 = y3 - delta_y            #1/2处节点y
                        x4 = x3 - (y3 - y4) / k3     #1/2处节点x
                        ks3 = (y6 - y4) / (x6 - x4)  #辅助线斜率
                        k4 = (k3 + 3 * ks3) / 4          #第四段直线斜率
                        y5 = y4 - delta_y            #3/4处节点y
                        x5 = x4 - (y4 - y5) / k4     #3/4处节点x
                        k5 = (y6 - y5) / (x6 - x5)  #辅助线斜率
                        for k in range(101):
                            # 将第一段轨迹100等分
                            t = (x3 - x2) / 100
                            x_test = x2 + k * t
                            y_test = k2 * (x_test - x2) + y2
                            point_test = [x_test, y_test]    #轨迹上第k个点的坐标
                            distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                        # 找到场上冰壶与该轨迹的最短距离
                            if distance < min_distance:
                                min_distance = distance
                        for k in range(101):
                            # 将第二段轨迹100等分
                            t = (x4 - x3) / 100
                            x_test = x3 + k * t
                            y_test = k3 * (x_test - x3) + y3
                            point_test = [x_test, y_test]    #轨迹上第k个点的坐标
                            distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                        # 找到场上冰壶与该轨迹的最短距离
                            if distance < min_distance:
                                min_distance = distance
                        for k in range(101):
                            # 将第三段轨迹100等分
                            t = (x5 - x4) / 100
                            x_test = x4 + k * t
                            y_test = k4 * (x_test - x4) + y4
                            point_test = [x_test, y_test]     #轨迹上第k个点的坐标
                            distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                        # 找到场上冰壶与该轨迹的最短距离
                            if distance < min_distance:
                                min_distance = distance
                        for k in range(101):
                            # 将第四段轨迹100等分
                            t = (x6 - x5) / 100
                            x_test = x5 + k * t
                            y_test = k5 * (x_test - x5) + y5
                            point_test = [x_test, y_test]     #轨迹上第k个点的坐标
                            distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                        # 找到场上冰壶与该轨迹的最短距离
                            if distance < min_distance:
                                min_distance = distance
                distance0 = abs(target[1] - ty)
                if min_distance > min_thresh and min_distance0 > distance0:        #对比各轨迹，保留距离目标壶最小的那组数据
                    min_distance0 = distance0
                    choose_offset = offset
                    choose_v = float(csv_data[i][0])
                    choose_omiga = float(csv_data[i][2])
                    # print('row '+ str(i))
                    # print(str(x3)+' '+str(y3)+' '+str(x4)+' '+str(y4)+' '+str(x5)+' '+str(y5))
                    # print('k1 '+str(k1)+'k2 '+str(k2)+'k3 '+str(k3)+'k4 '+str(k4))
                    # print('min_distance ' + str(min_distance))
                    # print('min_distance0 ' + str(min_distance0))
        if min_distance0 < 10:
            no_trail = 0        
            v_init = choose_v
            offset = choose_offset
            w_init = choose_omiga
        else:
            roll = 1
            v_init = 3
            offset = 0
            w_init = 0
    if roll == 1:  #打飞
        # print('roll1')
        #初始化
        max_choose = 0
        q = 0 # 在可以打飞的情况下左右偏移，增加找到路径的概率 
        for q in range(5):
            for i in range(row):   #遍历表格中的每一行
                x = float(csv_data[i][1])            #初始偏置
                mx = float(csv_data[i][3]) 
                my = float(csv_data[i][4])
                tx = float(csv_data[i][5]) 
                ty = float(csv_data[i][6])
                delta_x = target[0] - tx + 0.015 * (q - 2)            #横坐标与目标对其需平移的距离
                offset = x + delta_x                 #平移后的偏置
                x1 = aim_x + offset                  #平移后的起点横坐标
                y1 = 32.48
                x2 = mx + delta_x
                y2 = my
                x6 = tx + delta_x
                y6 = ty
                if abs(offset) > 2.23:   
                    continue
                if abs(ty - target[1]) < 0.5:   #寻找目标点附近的打法
                    # 初始化最小距离
                    min_distance = 50
                    for j in range(15):    #遍历16个壶
                        if position_float[2 * j] == 0 or position_float[2 * j + 1] == 0 or\
                            ((position_float[2 * j] - aim_x) ** 2 + (position_float[2 * j + 1] - aim_y) ** 2) ** 0.5 < 0.2:
                            continue
                        if abs(float(csv_data[i][2])) < 1:     #角速度小于1近似为直线
                            x_mean = (x1 + x2) / 2
                            distance = abs(x_mean - position_float[2 * j])
                            if distance < min_distance:
                                min_distance = distance
                        else:
                            point_ball = [position_float[2 * j], position_float[2 * j + 1]]    # 场上第j个冰壶的坐标
                            delta_y = (y2 - y6) / 4     #取1/4点
                            k1 = (y1 - y2) / (x1 - x2)   #第一段直线的斜率
                            ks1 = (y2 - y6) / (x2 - x6)  #辅助线斜率
                            k2 = (k1 + 3 * ks1) / 4          #第二段直线斜率
                            y3 = y2 - delta_y            #1/4处节点y
                            x3 = x2 - (y2 - y3) / k2     #1/4处节点x
                            ks2 = (y6 - y3) / (x6 - x3)  #辅助线斜率
                            k3 = (k2 + 3 * ks2) / 4          #第三段直线斜率
                            y4 = y3 - delta_y            #1/2处节点y
                            x4 = x3 - (y3 - y4) / k3     #1/2处节点x
                            ks3 = (y6 - y4) / (x6 - x4)  #辅助线斜率
                            k4 = (k3 + 3 * ks3) / 4          #第四段直线斜率
                            y5 = y4 - delta_y            #3/4处节点y
                            x5 = x4 - (y4 - y5) / k4     #3/4处节点x
                            k5 = (y6 - y5) / (x6 - x5)  #辅助线斜率
                            for k in range(101):
                                # 将第一段轨迹100等分
                                t = (x3 - x2) / 100
                                x_test = x2 + k * t
                                y_test = k2 * (x_test - x2) + y2
                                point_test = [x_test, y_test]    #轨迹上第k个点的坐标
                                distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                            # 找到场上冰壶与该轨迹的最短距离
                                if distance < min_distance:
                                    min_distance = distance
                            for k in range(101):
                                # 将第二段轨迹100等分
                                t = (x4 - x3) / 100
                                x_test = x3 + k * t
                                y_test = k3 * (x_test - x3) + y3
                                point_test = [x_test, y_test]    #轨迹上第k个点的坐标
                                distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                            # 找到场上冰壶与该轨迹的最短距离
                                if distance < min_distance:
                                    min_distance = distance
                            for k in range(101):
                                # 将第三段轨迹100等分
                                t = (x5 - x4) / 100
                                x_test = x4 + k * t
                                y_test = k4 * (x_test - x4) + y4
                                point_test = [x_test, y_test]     #轨迹上第k个点的坐标
                                distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                            # 找到场上冰壶与该轨迹的最短距离
                                if distance < min_distance:
                                    min_distance = distance
                            for k in range(101):
                                # 将第四段轨迹100等分
                                t = (x6 - x5) / 100
                                x_test = x5 + k * t
                                y_test = k5 * (x_test - x5) + y5
                                point_test = [x_test, y_test]     #轨迹上第k个点的坐标
                                distance = ((point_ball[0] - point_test[0]) ** 2 + (point_ball[1] - point_test[1]) ** 2) ** 0.5
                            # 找到场上冰壶与该轨迹的最短距离
                                if distance < min_distance:
                                    min_distance = distance
                    # 对比各轨迹的最短距离, 保留距离中心最近的那组数据
                    if min_distance > max_choose:
                        max_choose = min_distance
                        choose_offset = offset
                        choose_v = float(csv_data[i][0])
                        choose_omiga = float(csv_data[i][2])
                        # print('row '+ str(i))
                        # print(str(x1)+' '+str(y1)+' '+str(x2)+' '+str(y2)+str(x3)+' '+str(y3)+' '+str(x4)+' '+str(y4)+' '+str(x5)+' '+str(y5)+str(x6)+' '+str(y6))
                        # print('k1 '+str(k1)+'k2 '+str(k2)+'k3 '+str(k3)+'k4 '+str(k4))
                        # print('min_distance ' + str(min_distance))
                        # print('min_distance0 ' + str(min_distance0))
            if max_choose >min_thresh:
                no_trail = 0        
                v_init = choose_v
                offset = choose_offset
                w_init = choose_omiga
            else:
                no_trail = 1
                # print('notrail')
                v_init = 3
                offset = 0
                w_init = 0
    return v_init, offset, w_init, no_trail

# 传击函数
def Pass(target,block):
    # print('target ' + str(target))
    # print('block ' + str(block)) 
    delta = 0
    no_trail = 0
    if (target[1] - block[1]) > 6:
        # print('cant pass')
        no_trail = 1
        v_int = 3
        offset = 0
        omiga = 0
        return v_int, offset, omiga, no_trail
    k = (target[0] - block[0]) / (target[1] - block[1])      #dx/dy
    if k < -0.448 or k > 0.448:  #以下为经验参数
        no_trail = 1
        # print('cant pass')
    elif k < -0.374:
        delta = (k + 0.448) / (-0.374+0.448) * (-0.074+0.0865) - 0.0865
    elif k < -0.329:
        delta = (k + 0.374) / (-0.329+0.374) * (-0.066+0.074) - 0.074
    elif k < -0.280:
        delta = (k + 0.329) / (-0.280+0.329) * (-0.052+0.066) - 0.066
    elif k < -0.187:
        delta = (k + 0.280) / (-0.187+0.280) * (-0.0285+0.052) - 0.052
    elif k < -0.0934:
        delta = (k + 0.187) / (-0.0934+0.187) * (0.002+0.0285) - 0.0285
    elif  k < -0.028:
        delta = (k + 0.0934) / (-0.028+0.0934) * (0.014+0.002) + 0.002
    elif k < 0:
        delta = (k + 0.028) / (0+0.028) * (0.023-0.014) + 0.014
    elif k < 0.0374:
        delta = (k - 0) / (0.0374 - 0) * (0.045-0.023) + 0.023
    elif k < 0.0747:
        delta = (k - 0.0374) / (0.0747-0.0374) * (0.05-0.045) + 0.045
    elif k < 0.112:
        delta = (k - 0.0747) / (0.112-0.0747) * (0.065-0.05) + 0.05
    elif k < 0.187:
        delta = (k - 0.112) / (0.187-0.112) * (0.078-0.065) + 0.065
    elif k < 0.299:
        delta = (k - 0.187) / (0.299-0.187) * (0.109-0.078) + 0.078
    elif k < 0.374:
        delta = (k - 0.299) / (0.374-0.299) * (0.124-0.109) + 0.109
    elif k < 0.448:
        delta = (k + 0.374) / (0.448+0.374) * (0.1314-0.124) + 0.124
    # print('k ' + str(k))
    v_int = 8
    offset = block[0] + delta - 2.375
    omiga = 0
    return v_int, offset, omiga, no_trail

# 返回没有占位球的本方离中心最近的球的坐标
def Score_block(position,order,setstate):
    block = []
    IsnotBlocked_block = []
    near_IsnotBlocked_block = []
    opposite_block = []
    near_opposite_block = []
    min_x = House_R
    no_trail = 0
    if InitiativeOrGote(order,setstate) == 0:
        for i in range(8):
            if get_dist2(float(position[0][4*i+2]),float(position[0][4*i+3])) <= House_R*House_R :
                if get_dist2(float(position[0][4*i+2]),float(position[0][4*i+3])) > 2*Stone_R*2*Stone_R:
                    opposite_block.append([get_dist2(float(position[0][4*i+2]),float(position[0][4*i+3]))-2*Stone_R])
                else:
                    no_trail = 1
                    # print('no_trail1')
                    return 0,0,no_trail
        near_opposite_block = sorted(opposite_block)
        if near_opposite_block == []:
            min_x = House_R - Stone_R
        else:
            min_x = float(near_opposite_block[0][0])
        for i in range(8):
            if float(position[0][4*i + 1]) > aim_y and abs(float(position[0][4*i]) - aim_x) <= min_x:
                block.append([float(position[0][4*i]), float(position[0][4*i + 1])])                    #所有在前面的壶的坐标
    else:
        for i in range(8):
            if get_dist2(float(position[0][4*i]),float(position[0][4*i+1])) <= House_R*House_R:
                if get_dist2(float(position[0][4*i]),float(position[0][4*i+1])) > 2*Stone_R*2*Stone_R:
                    opposite_block.append([get_dist2(float(position[0][4*i]),float(position[0][4*i+1]))-2*Stone_R])
                else:
                    no_trail = 1
                    # print('no_trail2 ')
                    return 0,0,no_trail
        near_opposite_block = sorted(opposite_block)
        if near_opposite_block == []:
            min_x = House_R - Stone_R
        else:
            min_x = float(near_opposite_block[0][0])
        for i in range(8):
            # print('for3')
            if float(position[0][4*i + 3]) > aim_y and abs(float(position[0][4*i+2]) - aim_x) <= min_x:
                block.append([float(position[0][4*i+2]), float(position[0][4*i + 3])])                    #所有在前面的壶的坐标
    for i in range(len(block)):
        # print('for1')
        if IsBlockedAll(block[i][0],block[i][1],position) == False:
            IsnotBlocked_block.append([block[i][0],block[i][1]])
            # print('IsnotBlocked_block ' + str(IsnotBlocked_block))
    for i in range(len(IsnotBlocked_block)):
        # print('for2')
        near_IsnotBlocked_block.append([abs(float(IsnotBlocked_block[i][0])-aim_x),IsnotBlocked_block[i][0],IsnotBlocked_block[i][1]])
    near_IsnotBlocked_block = sorted(near_IsnotBlocked_block)
    if near_IsnotBlocked_block == []:
        # print('no_trail3 ')
        no_trail = 1
        near_IsnotBlocked_block.append([0,0,0])
    else:
        no_trail = 0
    return near_IsnotBlocked_block[0][1],near_IsnotBlocked_block[0][2],no_trail

#number_curling = 0表示没有靠着目标球的球，返回目标球的坐标，number_curling=1表示有靠着目标球的球，返回最前面的球的坐标
def Stick(x,y,position):
    flag = 0
    position_stick = []
    number_curling = 0
    for i in range(16):
        if (float(position[0][2*i])-x)**2+(float(position[0][2*i+1])-y)**2 < 0.35*0.35 and (float(position[0][2*i])-x) < 0.145 and\
             float(position[0][2*i]) != x and float(position[0][2*i+1]) != y:
             position_stick.append([float(position[0][2*i+1]),float(position[0][2*i])])
             flag = flag+1
    if flag == 0:
        number_curling = 0
    else:
        number_curling = 1
    position_stick.append([y,x])
    position_stick = sorted(position_stick,reverse = True)
    return position_stick[0][1],position_stick[0][0],number_curling

# 大本营内是否有球
def is_in_house(x, y):
    if get_dist2(x, y) < (House_R + Stone_R) ** 2:
        return True
    else:
        return False

# 壶前是否有占位
def IsBlocked(x, y, position):
    for i in range(16):
        if float(position[0][2 * i + 1]) > y + 0.3 and abs(float(position[0][2 * i]) - x) < 2 * Stone_R+0.01:
            return True
    return False
#将壶半径放大后壶前是否有占位
def IsBlocked_large(x,y,delta_x,position):
    for i in range(16):
        if float(position[0][2 * i + 1]) > y + 0.3 and abs(float(position[0][2 * i]) - (x+delta_x)) < 2 * Stone_R+0.01:
            return True
    return False

def IsBlockedAll(x, y, position):
    for i in range(16):
        if float(position[0][2*i + 1]) > aim_y - 2 * Stone_R and abs(float(position[0][2*i]) - x) <= 0.32 and abs(y - float(position[0][2*i + 1])) > 0.001:
            return True
    return False
# 壶前是否有部分占位
def IsPartBlocked(x, y, position):
    for i in range(16):
        if float(position[0][2 * i + 1]) > y + 0.3 and abs(float(position[0][2 * i]) - x) < 0.75 * Stone_R:
            return True
    return False
           
# 目标点前空隙情况
def gapinfo(position_float, x, y):
    flag = ''
    left,ml,mr,right,mid = 0,0,0,0,0
    for i in range(16):
        if position_float[2*i+1]>y - Stone_R:
            if (position_float[2*i]>-2.23-Stone_R) and (position_float[2*i]<=x-8*Stone_R):
                left += 1
            elif (position_float[2*i]<=x-2*Stone_R):
                ml += 1
            elif (position_float[2*i]<x+2*Stone_R):
                mid += 1
            elif (position_float[2*i]<=x+8*Stone_R):
                mr += 1
            elif (position_float[2*i]<2.23+Stone_R):
                right += 1
    if right and mid and left:
        flag = "NON"
    if (not left) and (ml):
        flag = flag + "LEFT"
    if not mid:
        flag = flag + "MID"
    if (not right) and (mr):
        flag = flag + "RIGHT"
    if not ml:
        flag = flag + "ML"
    if not mr:
        flag = flag + "MR"
    return flag

# 场上实时得分情况(己方得分，己方得分壶分布，对方得分壶分布)
def scoref(order,posi,state):
    #posi = position; state = setstate
    i,num,mid,left,right= 0,0,0,0,0
    dist1 = []
    dist2 = []
    while i<29:    
        dist1.append([(float(posi[0][i])-2.375)**2 +(float(posi[0][i+1])-4.88)**2,num])
        dist2.append([(float(posi[0][i+2])-2.375)**2 +(float(posi[0][i+3])-4.88)**2,num])
        i += 4
        num += 1
    dist1.sort()
    dist2.sort()
    i,sc1,sc2,score = 0,0,0,0
    if dist1[0]<dist2[0]:
        while (dist1[i][0]<dist2[0][0])and(dist1[i][0]<(1.870)**2)and(i<num):
            if float(posi[0][4*dist1[i][1]])<-0.5*Stone_R + aim_x:
                left += 1
            elif float(posi[0][4*dist1[i][1]])<0.5*Stone_R + aim_x:
                mid += 1
            else:
                right += 1
            i += 1
            sc1 = i
    else:
        while (dist2[i][0]<dist1[0][0])and(dist2[i][0]<(1.870)**2)and(i<num):
            if float(posi[0][4*dist2[i][1]+2])<-0.5*Stone_R + aim_x:
                left += 1
            elif float(posi[0][4*dist2[i][1]+2])<0.5*Stone_R + aim_x:
                mid += 1
            else: 
                right += 1
            i += 1
            sc2 = i
    if mid>=left and mid>=right:
        flag = "MID"
    elif left<=mid:
        flag = "RIGHT"
    elif right<=mid:
        flag = "LEFT"
    elif left<right:
        flag = "RIGHT"
    else:
        flag = "LEFT"
    if mid==0 and left==0 and right==0:
        flag = "NON"
        mysc = flag
        opsc = flag
    if ((order == 'Player1') and (int(state[0][0]) % 2 == int(state[0][3]))) \
            or ((order == 'Player2') and ((int(state[0][0]) + 1) % 2 == int(state[0][3]))):
        #如果先手，dist1是调参侠的结果
        if sc1>sc2:
            score = sc1
            opsc = "NON"
            mysc = flag
        else:
            score = -sc2
            mysc = "NON"
            opsc = flag
        if dist1[0][0]<(1.870)**2:
            mypo = [float(posi[0][4*dist1[0][1]]),float(posi[0][4*dist1[0][1]+1])]
        else:
            mypo = [0,0]
        if dist2[0][0]<(1.870)**2:
            oppo = [float(posi[0][4*dist2[0][1]+2]),float(posi[0][4*dist2[0][1]+3])]
        else:
            oppo = [0,0]
    else:
        if sc1>sc2:
            score = -sc1
            mysc = "NON"
            opsc = flag
        else:
            score = sc2
            opsc = "NON"
            mysc = flag
        if dist1[0][0]<(1.870)**2:
            oppo = [float(posi[0][4*dist1[0][1]]),float(posi[0][4*dist1[0][1]+1])]
        else:
            oppo = [0,0]
        if dist2[0][0]<(1.870)**2:
            mypo = [float(posi[0][4*dist2[0][1]+2]),float(posi[0][4*dist2[0][1]+3])]
        else:
            mypo = [0,0]
    # print(IsBlocked(oppo[0], oppo[1], posi))
    if int(state[0][0]) == 16:
        if score > 0:
            score = -score - 20
        else:
            score = -score + 20
    if int(state[0][0] == 16):
        score = 0
    # print(dist1)
    # print(dist2)
    # print(score,' m ',mysc,' o ',opsc)
    return score, mysc, mypo, opsc, oppo

# 本局先手或后手(0先手, 1后手)
def InitiativeOrGote(order, setstate):
    flag = not(((order == 'Player1') and (int(setstate[0][0]) % 2 == int(setstate[0][3]))) \
        or ((order == 'Player2') and ((int(setstate[0][0]) + 1) % 2 == int(setstate[0][3]))))
    return flag

# 局内形势分析
def analysis(order, setstate, position):
    nearest = []
    block = []
    nearest_enemy = []
    flag = 0
    for i in range(0, 30, 2):
        x_i, y_i = float(position[0][i]), float(position[0][i + 1])
        if (not ((is_in_house(x_i, y_i)) or ((y_i > aim_y) and (abs(x_i - aim_x) <= House_R + Stone_R)))):
            flag += 1
        else:
            flag = -1
            break
    # 大本营和自由防守区无壶
    if flag == 15:
        condition = 1
        sorted_res = []
    # 大本营和自由防守区有壶
    else:
        res = []
        sorted_res = []
        for i in range(0, 30, 2):
            if float(position[0][i + 1]) > aim_y and abs(float(position[0][i]) - aim_x) <= House_R + 2 * Stone_R:
                block.append([float(position[0][i]), float(position[0][i + 1])])
            if is_in_house(float(position[0][i]), float(position[0][i + 1])):
                res.append(i)
        # 只有自由防守区有壶
        if not res:
            flag_middle = 0
            flag_border = 0
            for i in range(0, 30, 2):
                if float(position[0][i]) != 0:
                    if abs(float(position[0][i]) - aim_x) <= middle_R:
                        flag_middle += 1
                    else:
                        flag_border += 1
            # 中区有壶, 边区没壶
            if flag_border == 0:
                condition = 2
            # 中区没壶, 边区有壶
            elif flag_middle == 0:
                condition = 11
            # 中区有壶, 边区有壶
            else:
                condition = 12
        # 大本营有壶
        else:
            for i in res:
                sorted_res.append([get_dist2(float(position[0][i]), float(position[0][i + 1])), i])
            sorted_res = sorted(sorted_res)
            nearest = [float(position[0][sorted_res[0][1]]), float(position[0][sorted_res[0][1] + 1])]
            # 我方得分(离大本营中心最近的球是自己的)
            if sorted_res[0][1] % 4 == InitiativeOrGote(order, setstate) * 2:
                res_enemy = []
                sorted_res_enemy = []
                flag = 0
                for i in range(0, 30, 2):
                    if i % 4 != InitiativeOrGote(order, setstate) * 2 and \
                        is_in_house(float(position[0][i]), float(position[0][i + 1])):
                        res_enemy.append(i)
                if res_enemy:
                    for i in res_enemy:
                        sorted_res_enemy.append([get_dist2(float(position[0][i]), float(position[0][i + 1])), i])
                    sorted_res_enemy = sorted(sorted_res_enemy)
                    nearest_enemy = [float(position[0][sorted_res_enemy[0][1]]), float(position[0][sorted_res_enemy[0][1] + 1])]
                    count = 0
                    for i in range(0, 30, 2):
                        if (not(is_in_house(float(position[0][i]), float(position[0][i + 1])))) \
                            and float(position[0][i + 1]) > max(aim_y, nearest_enemy[1]) \
                                and abs(float(position[0][i]) - aim_x) <= House_R \
                                    and abs(float(position[0][i]) - nearest_enemy[0]) <= 2 * Stone_R:
                            break
                        else:
                            count += 1
                    if count == 15:
                        flag = 1
                # 敌方最近壶没有占位
                if flag \
                    and (abs(nearest[0] - nearest_enemy[0]) > 2 * Stone_R):
                    # 有占位
                    if IsBlocked(nearest[0], nearest[1], position):
                        # 中区
                        if abs(nearest[0] - 2.375) < middle_R:
                            condition = 13
                        # 边区
                        else:
                            condition = 14
                    # 无占位
                    else:
                        # 中区
                        if abs(nearest[0] - 2.375) < middle_R:
                            condition = 15
                        # 边区
                        else:
                            condition = 16
                # 其他情况
                else:
                    # 有占位
                    if IsBlocked(nearest[0], nearest[1], position):
                        # 中区
                        if abs(nearest[0] - 2.375) < middle_R:
                            condition = 3
                        # 边区
                        else:
                            condition = 4
                    # 无占位
                    else:
                        # 中区
                        if abs(nearest[0] - 2.375) < middle_R:
                            condition = 5
                        # 边区
                        else:
                            condition = 6
            # 敌方得分(离大本营中心最近的球是对方的)
            else:
                # 有占位
                if IsBlocked(nearest[0], nearest[1], position):
                    # 中区
                    if abs(nearest[0] - aim_x) < middle_R:
                        condition = 7
                    # 边区
                    else:
                        condition = 8
                # 无占位
                else:
                    # 中区
                    if abs(nearest[0] - aim_x) < middle_R:
                        condition = 9
                    # 边区
                    else:
                        condition = 10
    
    # block_actual -> action 9需要
    block_actual = [aim_x, aim_y + House_R * 2]
    # 有得分壶 -> 与最近壶1条线且最近
    if nearest:
        block_temp = []
        sorted_block_temp = []
        for i in range(len(block)):
            if block[i][1] > nearest[1] and abs(block[i][0] - nearest[0]) < 2 * Stone_R:
                block_temp.append(i)
        if block_temp:
            for i in block_temp:
                sorted_block_temp.append([(block[i][0] - nearest[0]) ** 2 + (block[i][1] - nearest[1]) ** 2, i])
            sorted_block_temp = sorted(sorted_block_temp,reverse=True)
            block_actual = [block[sorted_block_temp[0][1]][0], block[sorted_block_temp[0][1]][1]]
    # 无得分壶
    else:
        # 中区有球, 边区无球
        if condition == 2:
            sorted_block = []
            for i in range(len(block)):
                sorted_block.append([get_dist2(block[i][0], block[i][1]), i])
            sorted_block = sorted(sorted_block,reverse=True)
            block_actual = [block[sorted_block[0][1]][0], block[sorted_block[0][1]][1]]
        # 中区无球, 边区有球
        elif condition == 11:
            sorted_block = []
            for i in range(len(block)):
                sorted_block.append([get_dist2(block[i][0], block[i][1]), i])
            sorted_block = sorted(sorted_block, reverse=True)
            block_actual = [block[sorted_block[0][1]][0], block[sorted_block[0][1]][1]]
        # 中区有球, 边区有球
        elif condition == 12:
            # 本局先手 -> 中区离大本营最近
            if not InitiativeOrGote(order, setstate):
                block_temp = []
                sorted_block_temp = []
                for i in range(len(block)):
                    if abs(block[i][0] - aim_x) <= middle_R:
                        block_temp.append(i)
                if block_temp:
                    for i in block_temp:
                        sorted_block_temp.append\
                            ([get_dist2(block[i][0], block[i][1]), i])
                    sorted_block_temp = sorted(sorted_block_temp, reverse=True)
                    block_actual = [block[sorted_block_temp[0][1]][0], block[sorted_block_temp[0][1]][1]]
            # 本局后手 -> 边区离大本营最近
            else:
                block_temp = []
                sorted_block_temp = []
                for i in range(len(block)):
                    if abs(block[i][0] - aim_x) > middle_R:
                        block_temp.append(i)
                if block_temp:
                    for i in block_temp:
                        sorted_block_temp.append\
                            ([get_dist2(block[i][0], block[i][1]), i])
                    sorted_block_temp = sorted(sorted_block_temp,reverse=True)
                    block_actual = [block[sorted_block_temp[0][1]][0], block[sorted_block_temp[0][1]][1]]
    return condition, nearest, nearest_enemy, block, block_actual

# 根据位置和策略确定出手初速度, 水平偏移, 初角速度
def action(choice, mode, nearest, nearest_enemy, block, block_actual, position, order, setstate):
    PositiveOrNegative = random.randrange(-1, 2, 2)
    position_float = []
    for i in range(32):
        position_float.append(float(position[0][i]))
    # print(position_float)
    v_init = 3
    offset = 0
    w_init = 0
    # draw-中区低占位(主动选择无需信息)
    if choice == 1:
        target = [0, 0]
        v_init, offset, w_init = 2.6, -0.075+0.025, 0
    # draw - 中区低占位(主动选择无需信息)
    elif choice == 2:
        target = [0, 0]
        v_init, offset, w_init = 2.75, 0.09+0.025, 0
    # draw - 中区高占位(主动选择无需信息)
    elif choice == 3:
        target = [0, 0]
        v_init, offset, w_init = 2.6, -0.075+0.025, 0
    # draw - 边区占位(主动选择无需信息)
    elif choice == 4:
        target = [0, 0]
        v_init, offset, w_init = 2.6, 0.9+0.025, 0
    # draw - 边区双占位(主动选择无需信息)
    elif choice == 5:
        target = [0, 0]
        v_init, offset, w_init = 2.6, -0.9+0.025, 0
    # draw - 为得分壶占位(已进行轨迹规划)
    elif choice == 6:
        number = random.uniform(-0.12,+0.12)
        target = [nearest[0]+number, nearest[1] + 2.3]
        mode = 0
        v_init, offset, w_init, no_trail = findCSV(target, position_float, order, setstate, mode)
        if no_trail:
            v_init = 2.6
            offset = float(nearest[0] - aim_x)+0.025
            w_init = 0
    # draw - 中区旋进(已加入避障信息，已加入得分信息)
    elif choice == 7:
        target = [aim_x, aim_y]
        score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
        # print("score",score,'mysc',mysc,'mypo',mypo,'oppo',oppo)
        bias = 0
        if mysc == "RIGHT":
            bias = -Stone_R
        elif mysc == "LEFT":
            bias = Stone_R
        gap = gapinfo(position_float,target[0]+bias,target[1])
        if gap.find("MID") != -1:
            v_init, offset, w_init = 2.98, bias, 0
        elif gap.find("ML") != -1:
            v_init, offset, w_init = 3.03, -1.65+bias, 10
        elif gap.find("MR") != -1:
            v_init, offset, w_init = 3.03, 1.65+bias, -10
        else:
            v_init, offset, w_init, no_trail = findCSV(target, position_float, order, setstate, mode)
            if no_trail:
                if score<-1:
                    v_init, offset, w_init = 8, block_actual[0] + 0.02 * PositiveOrNegative, 0 * PositiveOrNegative
                else:
                    v_init = 3
                    offset = 0.5 * PositiveOrNegative
                    w_init = -4 * PositiveOrNegative
    # draw - 边区旋进(查表)
    elif choice == 8:
        score,mysc,mypo,opsc,oppo = scoref(order,position,setstate)
        target = [aim_x + 1.2 * PositiveOrNegative, aim_y]
        if mysc == "LEFT":
            target = [aim_x + 1.2, aim_y]
        elif mysc == "RIGHT":
            target = [aim_x - 1.2, aim_y]
        v_init, offset, w_init, no_trail = findCSV(target, position_float, order, setstate, mode)
        if no_trail:
            v_init, offset, w_init = 3.03, 0.1 * PositiveOrNegative, -8 * PositiveOrNegative
    # draw - 查表旋进（）
    elif choice == 9:                                                                                                  #no_trail!!!!!!!!!!!!!!!!!!!!!!
        if InitiativeOrGote(order, setstate):
            target = [block_actual[0], aim_y]
        else:
            target = [aim_x, aim_y]
        # print('target ' +  str(target))
        v_init, offset, w_init, no_trail = findCSV(target, position_float, order, setstate, mode)
        if no_trail:
            if int(setstate[0][0]) == 0 or int(setstate[0][0]) == 1 or int(setstate[0][0]) == 2 or int(setstate[0][0]) == 3 or int(setstate[0][0]) == 4:
                gap_target_9 = []
                min_gap_9 = 2*1.875/19
                for i in range(20):
                    if IsBlockedAll(aim_x-1.875+i*min_gap_9,aim_y,position) == False:
                        gap_target_9.append([abs(-1.875+i*min_gap_9),(-1.875+i*min_gap_9)])
                gap_target_9 = sorted(gap_target_9)
                if gap_target_9 == []:
                    v_init = 3
                    offset = 1+0.025
                    w_init = 0
                else:
                    v_init = 3
                    offset = float(gap_target_9[0][1])+0.025
                    w_init = 0
            else:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score > 0:
                    target_1 = [nearest[0], nearest[1] + 3.35]
                    mode = 0
                    v_init, offset, w_init, no_trail_1 = findCSV(target_1, position_float, order, setstate, mode)
                    if no_trail_1:
                        v_init = 2.44
                        offset = float(nearest[0] - aim_x)+0.025
                        w_init = 0
                elif score < 0:                                                                                       
                    target = [nearest[0], nearest[1]]
                    roll = 0
                    v_init, offset, w_init, no_trail = findCSV_hit(target, position_float,roll)
                    if no_trail:
                        roll = 1
                        v_init, offset, w_init, no_trail_1 = findCSV_hit(target, position_float,roll)
                        if no_trail_1:
                            block = [block_actual[0], block_actual[1]]
                            v_init, offset, w_init, no_trail = Pass(target, block)
                            if no_trail:
                                v_init = 8
                                offset = float(block_actual[0] - aim_x)+0.025
                                w_init = 0  
                else:
                    block_all = []
                    flag_block = 0
                    for i in range(16):
                        if IsBlockedAll(float(position[0][2*i]),float(position[0][2*i+1]),position) == False and float(position[0][2*i]) != 0 and float(position[0][2*i+1]) != 0 and float(position[0][2*i+1]) > aim_y \
                            and abs(float(position[0][2*i])-aim_x) < 1.5:
                            block_all.append([position[0][2*i],position[0][2*i+1]])
                            flag_block = flag_block+1
                    if flag_block == 0:
                        for i in range(16):
                            block_all.append([position[0][2*i + 1],position[0][2*i]])
                        block_all = sorted(block_all,reverse=True)
                        target_1 = [float(block_all[0][1]),float(block_all[0][0])]
                        roll = 0
                        v_init, offset, w_init, no_trail_2 = findCSV_hit(target_1, position_float,roll)
                        if no_trail_2:
                            roll = 1
                            v_init, offset, w_init, no_trail_1 = findCSV_hit(target_1, position_float,roll)
                            if no_trail_1:
                                v_init = 8
                                offset = float(block_all[0][1]) - aim_x+0.025
                                w_init = 0
                    else:
                        v_init = 2.55+0.2*float(block_all[0][1])
                        offset = float(block_all[0][0])-aim_x+0.025
                        w_init = 0           
    # draw - 旋推
    elif choice == 10:
        target = [nearest[0], nearest[1]]
        if nearest[1]>aim_y:
            delta_y = -aim_y+nearest[1]+0.3
        else:
            delta_y = 0.2
        v_init, offset, w_init, no_trail = findCSV_push(target, position_float,delta_y)
        if no_trail:
            if int(setstate[0][0]) == 0 or int(setstate[0][0]) == 1 or int(setstate[0][0]) == 2 or int(setstate[0][0]) == 3 or int(setstate[0][0]) == 4:
                gap_target_9 = []
                min_gap_9 = 2*1.875/19
                for i in range(20):
                    if IsBlockedAll(aim_x-1.875+i*min_gap_9,aim_y,position) == False:
                        gap_target_9.append([aim_x-1.875+i*min_gap_9])
                gap_target_9 = sorted(gap_target_9,reverse = True)
                if gap_target_9 == []:
                    v_init = 3
                    offset = 1+0.025
                    w_init = 0
                else:
                    v_init = 3
                    offset = float(gap_target_9[0][0])-aim_x+0.025
                    w_init = 0
            else:
                target = [nearest[0], nearest[1]]
                block = [block_actual[0], block_actual[1]]
                v_init, offset, w_init, no_trail_1 = Pass(target, block)
                if no_trail_1:
                    v_init = 8
                    offset = float(block_actual[0] - aim_x)+0.025
                    w_init = 0
    # hit - 击打(需要信息)   
    elif choice == 11:
        num_front = 0
        if InitiativeOrGote(order,setstate) == 0:                  #先手
            for i in range(8):
                if abs(float(position[0][4*i])-aim_x) <= House_R and float(position[0][4*i+1]) > aim_y:
                    num_front = num_front+1
        else:
            for i in range(8):
                if abs(float(position[0][4*i+2])-aim_x) <= House_R and float(position[0][4*i+3]) > aim_y:
                    num_front = num_front+1
        if nearest[1] >= aim_y+4*Stone_R and InitiativeOrGote(order,setstate) == 1 and num_front != 0:    #若被击打的球在下半区且后手我方前场有球的时候不打甩
            if get_dist2(nearest[0],nearest[1])<(1.2+Stone_R)*(1.2+Stone_R):
                v_init = 6
                offset = float(nearest[0] - aim_x)+0.025
                w_init = 0
            elif get_dist2(nearest[0],nearest[1])>(1.2+Stone_R)*(1.2+Stone_R) and get_dist2(nearest[0],nearest[1])<(House_R+Stone_R)*(House_R+Stone_R) and\
                abs(nearest[0]-aim_x)<1.4 and nearest[1]>aim_y:                    #1.4可改
                    x,y,number_curling = Stick(nearest[0],nearest[1],position)
                    if number_curling == 0:
                        v_init = 2.58+0.2*float(nearest[1])
                        offset = float(nearest[0]-aim_x)+0.025
                        w_init = 0
                    else:
                        v_init = 1.5 + 0.51 * float(y)
                        offset = float(x)-aim_x+0.025
                        w_init = 0
            else:
                if InitiativeOrGote(order,setstate) == 0:               #先手
                    v_init = 6
                    offset = float(nearest[0] - aim_x)+0.025
                    w_init = 0
                else:
                    mode = 1
                    target = [aim_x,aim_y]
                    v_init, offset, w_init, no_trail = findCSV(target, position_float, order, setstate, mode)
                    gap_target = []
                    if no_trail:
                        min_xx = get_dist2(nearest[0],nearest[1])
                        min_gap = 2*min_xx/19
                        for i in range(20):
                            if IsBlockedAll(aim_x-min_xx+i*min_gap,aim_y,position) == False:
                                gap_target.append([aim_x-min_xx+i*min_gap])
                        gap_target = sorted(gap_target)
                        if gap_target == []:
                            v_init = 6
                            offset = float(nearest[0] - aim_x)+0.025
                            w_init = 0
                        else:
                            v_init = 3
                            offset = float(gap_target[0][0])-aim_x+0.025
                            w_init = 0    
        else:
            delta_x = -1*(nearest[0]-aim_x)
            offset_x = + ( 0.0768 *delta_x + 0.0004615) / (delta_x*delta_x +  -0.02452*delta_x + 0.6271)
            if IsBlocked_large(nearest[0],nearest[1],offset_x,position) == False:
                if get_dist2(nearest[0],nearest[1])<(1.2+Stone_R)*(1.2+Stone_R):
                    v_init = 6
                    delta_x = -1*(nearest[0]-aim_x)
                    offset = float(nearest[0] - aim_x)+0.025 + ( 0.0768 *delta_x + 0.0004615) / (delta_x*delta_x +  -0.02452*delta_x + 0.6271)
                    w_init = 0
                elif get_dist2(nearest[0],nearest[1])>(1.2+Stone_R)*(1.2+Stone_R) and get_dist2(nearest[0],nearest[1])<(House_R+Stone_R)*(House_R+Stone_R) and\
                    abs(nearest[0]-aim_x)<1.4 and nearest[1]>aim_y:                    #1.4可改
                    x,y,number_curling = Stick(nearest[0],nearest[1],position)
                    if number_curling == 0:
                        v_init = 2.58+0.2*float(nearest[1])
                        offset = float(nearest[0]-aim_x)+0.025
                        w_init = 0
                    else:
                        v_init = 1.5 + 0.51 * float(y)
                        offset = float(x)-aim_x+0.025
                        w_init = 0
                else:
                    if InitiativeOrGote(order,setstate) == 0:               #先手
                        v_init = 6
                        delta_x = -1*(nearest[0]-aim_x)
                        offset = float(nearest[0] - aim_x)+0.025 + ( 0.0768 *delta_x + 0.0004615) / (delta_x*delta_x +  -0.02452*delta_x + 0.6271)
                        w_init = 0
                    else:
                        mode = 1
                        target = [aim_x,aim_y]
                        v_init, offset, w_init, no_trail = findCSV(target, position_float, order, setstate, mode)
                        gap_target = []
                        if no_trail:
                            min_xx = get_dist2(nearest[0],nearest[1])
                            min_gap = 2*min_xx/15
                            for i in range(16):
                                if IsBlockedAll(aim_x-min_xx+i*min_gap,aim_y,position) == False:
                                    gap_target.append([aim_x-min_xx+i*min_gap])
                            gap_target = sorted(gap_target)
                            if gap_target == []:
                                v_init = 6
                                delta_x = -1*(nearest[0]-aim_x)
                                offset = float(nearest[0] - aim_x)+0.025 + ( 0.0768 *delta_x + 0.0004615) / (delta_x*delta_x +  -0.02452*delta_x + 0.6271)
                                w_init = 0
                            else:
                                v_init = 3
                                offset = float(gap_target[0][0])-aim_x+0.025
                                w_init = 0    
            else:
                if get_dist2(nearest[0],nearest[1])<(1.2+Stone_R)*(1.2+Stone_R):
                    v_init = 6
                    offset = float(nearest[0] - aim_x)+0.025
                    w_init = 0
                elif get_dist2(nearest[0],nearest[1])>(1.2+Stone_R)*(1.2+Stone_R) and get_dist2(nearest[0],nearest[1])<(House_R+Stone_R)*(House_R+Stone_R) and\
                    abs(nearest[0]-aim_x)<1.4 and nearest[1]>aim_y:                    #1.4可改
                    x,y,number_curling = Stick(nearest[0],nearest[1],position)
                    if number_curling == 0:
                        v_init = 2.58+0.2*float(nearest[1])
                        offset = float(nearest[0]-aim_x)+0.025
                        w_init = 0
                    else:
                        v_init = 1.5 + 0.51 * float(y)
                        offset = float(x)-aim_x+0.025
                        w_init = 0
                else:
                    if InitiativeOrGote(order,setstate) == 0:               #先手
                        v_init = 6
                        offset = float(nearest[0] - aim_x)+0.025
                        w_init = 0
                    else:
                        mode = 1
                        target = [aim_x,aim_y]
                        v_init, offset, w_init, no_trail = findCSV(target, position_float, order, setstate, mode)
                        gap_target = []
                        if no_trail:
                            min_xx = get_dist2(nearest[0],nearest[1])
                            min_gap = 2*min_xx/19
                            for i in range(20):
                                if IsBlockedAll(aim_x-min_xx+i*min_gap,aim_y,position) == False:
                                    gap_target.append([aim_x-min_xx+i*min_gap])
                            gap_target = sorted(gap_target)
                            if gap_target == []:
                                v_init = 6
                                offset = float(nearest[0] - aim_x)+0.025
                                w_init = 0
                            else:
                                v_init = 3
                                offset = float(gap_target[0][0])-aim_x+0.025
                                w_init = 0         
    # hit - 传击
    elif choice == 12:
        target = [nearest[0], nearest[1]]
        block = [block_actual[0], block_actual[1]]
        v_init, offset, w_init, no_trail = Pass(target, block)
        if no_trail:
            v_init = 8
            offset = float(block_actual[0] - aim_x)+0.025
            w_init = 0     
    # draw-边区旋进2
    elif choice == 13:
        target = [0, 0]
        v_init, offset, w_init = 3.05, 0.8 * PositiveOrNegative, -10 * PositiveOrNegative
    # HIT-查表击打
    elif choice == 14:
        target = [nearest[0], nearest[1]]
        roll = 0
        v_init, offset, w_init, no_trail = findCSV_hit(target, position_float,roll)
        if no_trail:
            roll = 1
            v_init, offset, w_init, no_trail_1 = findCSV_hit(target, position_float,roll)
            if no_trail_1:
                block = [block_actual[0], block_actual[1]]
                v_init, offset, w_init, no_trail = Pass(target, block)
                if no_trail:
                    v_init = 8
                    offset = float(block_actual[0] - aim_x)+0.025
                    w_init = 0   
    # 击打敌方最近壶
    elif choice == 15:
        v_init = 6
        offset = float(nearest_enemy[0] - aim_x)+0.025
        w_init = 0
        if nearest_enemy[1] > aim_y + 1.5:
            v_init = 4
    #旋至大本营正前方边缘
    elif choice == 16:  
        v_init = 2.78
        offset = 0+0.025
        w_init = 0 
    #边区进入
    elif choice == 17:
        v_init = 3
        offset = 1.25+0.025
        w_init = 0
    # 左边往右旋进去
    elif choice == 18:
        target = [0, 0]
        v_init, offset, w_init = 3.05, -0.78+0.025, 10
    # 左中区占位
    elif choice == 19:
        target = [0, 0]
        v_init, offset, w_init = 2.6, -0.5+0.025, 0
    # 右中区占位
    elif choice == 20:
        target = [0, 0]
        v_init, offset, w_init = 2.6, 0.5+0.025, 0
    # 为得分壶高占位
    elif choice == 21:
        number = random.uniform(-0.12,+0.12)
        target = [nearest[0]+number, nearest[1] + 4]
        mode = 0
        v_init, offset, w_init, no_trail = findCSV(target, position_float, order, setstate, mode)
        if no_trail:
            v_init = 2.44
            offset = float(nearest[0] - aim_x)+0.025
            w_init = 0
    #留一手
    elif choice == 22:
        x_block, y_block, no_trail_block = Score_block(position,order,setstate)
        v_init = 2.41 + 0.203 * y_block
        offset = x_block-aim_x+0.025
        w_init = 0        
    #旋入中心得分
    elif choice == 23:                          #敌方未得分时使用向中心旋进
        v_init, offset, w_init, no_trail1, no_trail2 = FindCSVToAim(position_float, order, setstate)
        if no_trail1:                             #中心有球导致路径规划失败，必为我方球得分，占位
            target = [nearest[0], nearest[1] + 2.3]
            mode = 0
            v_init, offset, w_init, no_trail = findCSV(target, position_float, order, setstate, mode)
            if no_trail:
                v_init = 2.6
                offset = float(nearest[0] - aim_x)+0.025
                w_init = 0
        elif no_trail2:                           #轨迹规划失败，有可能为我方得分或都没得分
            score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
            if score > 0:                        #轨迹规划失败且我方得分，占位
                target = [nearest[0], nearest[1] + 2.3]
                mode = 0
                v_init, offset, w_init, no_trail3 = findCSV(target, position_float, order, setstate, mode)
                if no_trail3:
                    v_init = 2.6
                    offset = float(nearest[0] - aim_x)+0.025
                    w_init = 0
            elif score == 0:                    #轨迹规划失败，双方都没有得分
                block_all = []
                flag_block = 0
                for i in range(16):
                    if IsBlockedAll(float(position[0][2*i]),float(position[0][2*i+1]),position) == False and float(position[0][2*i]) != 0 and float(position[0][2*i+1]) != 0 and float(position[0][2*i+1]) > aim_y \
                        and abs(float(position[0][2*i])-aim_x) < 1.5:
                        block_all.append([abs(float(position[0][2*i])-aim_x),float(position[0][2*i])-aim_x,float(position[0][2*i+1])])
                        flag_block = flag_block+1
                if flag_block == 0:                 #没有可推的球，插空
                    gap_target_23 = []
                    min_gap_23 = 2*1.875/19
                    for i in range(20):
                        if IsBlockedAll(aim_x-1.875+i*min_gap_23,aim_y,position) == False:
                            gap_target_23.append([abs(-1.875+i*min_gap_23),(-1.875+i*min_gap_23)])
                    gap_target_23 = sorted(gap_target_23)
                    if gap_target_23 == []:
                        v_init = 3
                        offset = 1+0.025
                        w_init = 0
                    else:
                        v_init = 3
                        offset = float(gap_target_23[0][1])+0.025
                        w_init = 0
                else:                               #有可推的球，推壶
                    block_all = sorted(block_all)          #按绝对值排序
                    # print('block_all '+(block_all[0][1]+aim_x)+','+block_all[0][2])
                    v_init = 2.55+0.2*float(block_all[0][2])
                    offset = float(block_all[0][1])+0.025
                    w_init = 0

    #找空隙
    elif choice == 24:
        gap_target_23 = []
        min_gap_23 = 2*1.875/19
        for i in range(20):
            if IsBlockedAll(aim_x-1.875+i*min_gap_23,aim_y,position) == False:
                gap_target_23.append([abs(-1.875+i*min_gap_23),(-1.875+i*min_gap_23)])
        gap_target_23 = sorted(gap_target_23)
        if gap_target_23 == []:
            v_init = 3
            offset = 1+0.025
            w_init = 0
        else:
            v_init = 3
            offset = float(gap_target_23[len(gap_target_23)-1][1])+0.025
            w_init = 0

    #放弃球
    # elif choice == 25:
    #     v_init = 1
    #     offset = 0
    #     w_init = 0

    #直着推(无叠壶)
    elif choice == 26:
        target = [nearest[0],nearest[1]]
        if nearest[1] >= aim_y-2*Stone_R:
            v_init = 2.55+0.2*nearest[1]
            offset = nearest[0]-aim_x+0.025
            w_init = 0
        else:
            v_init = 3.05
            offset = nearest[0]-aim_x+0.025
            w_init = 0

    #得分且避开自己的壶的纵坐标(那必须得是自己得分)
    elif choice == 27:
        target = [nearest[0],nearest[1]+2.3]
        v_init, offset, w_init, no_trail = FindCSVAvoid(position_float, order, setstate)
        if no_trail:
            mode = 0
            v_init, offset, w_init, no_trail_1 = findCSV(target, position_float, order, setstate, mode)
            if no_trail_1:
                v_init = 2.6
                offset = float(nearest[0] - aim_x)+0.025
                w_init = 0

    #直着推（有叠壶）
    elif choice == 28:
        target = [nearest[0],nearest[1]]
        x,y,number_curling = Stick(nearest[0],nearest[1],position)
        v_init = 1.5 + 0.51 * float(y)
        offset = float(x)-aim_x+0.025
        w_init = 0

    #离中线最近的空隙放占位球
    elif choice == 29:
        gap_target_29 = []
        min_gap_29 = 2*1.875/19
        for i in range(20):
            if IsBlockedAll(aim_x-1.875+i*min_gap_29,aim_y,position) == False:
                gap_target_29.append([abs(-1.875+i*min_gap_29),(-1.875+i*min_gap_29)])
        gap_target_29 = sorted(gap_target_29)
        if gap_target_29 == []:
            v_init = 2.42
            offset = 1+0.025
            w_init = 0
        else:
            v_init = 2.42
            offset = float(gap_target_29[0][1])+0.025
            w_init = 0
    # 
    elif choice == 30:
        v_init, offset, w_init, no_trail1, no_trail2 = FindCSVToAim(position_float, order, setstate)
        if no_trail1 or no_trail2:
            target = [nearest[0], nearest[1]]
            roll = 0
            v_init, offset, w_init, no_trail = findCSV_hit(target, position_float,roll)
            if no_trail:
                roll = 1
                v_init, offset, w_init, no_trail_1 = findCSV_hit(target, position_float,roll)
                if no_trail_1:
                    block = [block_actual[0], block_actual[1]]
                    v_init, offset, w_init, no_trail = Pass(target, block)
                    if no_trail:
                        v_init = 8
                        offset = float(block_actual[0] - aim_x)+0.025
                        w_init = 0

    # 给出投掷信息(注意: 这里的offset = x - 2.375, 即相对中心的偏移量,  而非赛场坐标系下的x)
    shot = "BESTSHOT " + str(v_init) + ' ' + str(offset) + ' ' + str(w_init)
    return shot

# 投掷策略
def strategy(order, setstate, position, scorediff):
    condition, nearest,nearest_enemy, block, block_actual = analysis(order, setstate, position)
    choice = 0
    mode = 0
    delta_y = 0

    # 第1局，后手
    if int(setstate[0][1]) == 0 and InitiativeOrGote(order, setstate):
        # 第1球
        if int(setstate[0][0]) == 1:
            choice = 4
        # 第2球
        elif int(setstate[0][0]) == 3:         
            choice = 9
            mode = 2
        # 第3~4球
        elif int(setstate[0][0]) == 5 or int(setstate[0][0]) == 7 :
            if condition == 1:
                choice = 4
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 27#23
            elif condition == 4:
                choice = 27#23
            elif condition == 5:
                choice = 27#23
            elif condition == 6:
                choice = 27#23
            elif condition == 7:
                choice = 10
            elif condition == 8:
                choice = 10
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 15
            elif condition == 14:
                choice = 27
            elif condition == 15:
                choice = 15
            elif condition == 16:
                choice = 27
        # 第5~6球
        elif int(setstate[0][0]) == 9 or int(setstate[0][0]) == 11:
            if condition == 1:
                choice = 4
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 27#23
            elif condition == 4:
                choice = 27#23
            elif condition == 5:
                choice = 27#23
            elif condition == 6:
                choice = 27#23
            elif condition == 7:
                choice = 14
                roll = 0
            elif condition == 8:
                choice = 14
                roll = 0
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 15
            elif condition == 14:
                choice = 27
            elif condition == 15:
                choice = 27
            elif condition == 16:
                choice = 27
        # 第7球
        elif int(setstate[0][0]) == 13:
            if condition == 1:
                choice = 4
            elif condition == 2:
                choice = 24
            elif condition == 3:
                choice = 27#23
            elif condition == 4:
                choice = 29#23
            elif condition == 5:
                choice = 27#23
            elif condition == 6:
                choice = 29#23
            elif condition == 7:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score < -1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 8:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score < -1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 24
            elif condition == 12:
                choice = 24
            elif condition == 13:
                choice = 27
            elif condition == 14:
                choice = 29
            elif condition == 15:
                choice = 27
            elif condition == 16:
                choice = 29
        # 第8球
        elif int(setstate[0][0]) == 15:
            x_block,y_block,no_trail_block=Score_block(position,order,setstate)
            if no_trail_block == 0:
                choice = 22
            else:
                if condition == 1:
                    choice = 23
                elif condition == 2:
                    choice = 17
                elif condition == 3:
                    choice = 27
                elif condition == 4:
                    choice = 27
                elif condition == 5:
                    choice = 27
                elif condition == 6:
                    choice = 27
                elif condition == 7:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    if score < -1:
                        choice = 30
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 14
                            roll = 0
                        elif flag_mynoinhouse == 6:
                            x, y, number_curling = Stick(nearest[0], nearest[1], position)
                            if number_curling == 0:
                                choice = 14
                                roll = 0
                            else:
                                choice = 10
                        else:
                            choice = 14
                            roll = 0
                elif condition == 8:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    if score < -1:
                        choice = 9
                        mode = 1
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 14
                            roll = 0
                        elif flag_mynoinhouse == 6:
                            x, y, number_curling = Stick(nearest[0], nearest[1], position)
                            if number_curling == 0:
                                choice = 14
                                roll = 0
                            else:
                                choice = 9
                                mode = 1
                        else:
                            choice = 30
                elif condition == 9:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    x, y, number_curling = Stick(nearest[0], nearest[1], position)
                    if score < -1:
                        if number_curling == 0:
                            choice = 26
                        else:
                            choice = 28
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分                      
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 11
                        elif flag_mynoinhouse == 6:
                            if number_curling == 1:
                                choice = 28
                            else:
                                choice = 11
                        else:
                            choice = 11
                elif condition == 10:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    x, y, number_curling = Stick(nearest[0], nearest[1], position)
                    if score < -1:
                        if number_curling == 0:
                            choice = 26
                        else:
                            choice = 28
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分                      
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 11
                        elif flag_mynoinhouse == 6:
                            if number_curling == 1:
                                choice = 28
                            else:
                                choice = 11
                        else:
                            choice = 11
                elif condition == 11:
                    choice = 23
                elif condition == 12:
                    choice = 23
                elif condition == 13:
                    choice = 27
                elif condition == 14:
                    choice = 27
                elif condition == 15:
                    choice = 27
                elif condition == 16:
                    choice = 27

    # 第8局，后手，平局或领先
    if int(setstate[0][1]) == 7 and scorediff >= 0 and InitiativeOrGote(order, setstate):
        # 第1球
        if int(setstate[0][0]) == 1:
            if condition == 1:
                choice = 18
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
        # 第2球
        elif int(setstate[0][0]) == 3:
            if condition == 1:
                choice = 13
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 27#23
            elif condition == 4:
                choice = 27#23
            elif condition == 5:
                choice = 27#23
            elif condition == 6:
                choice = 27#23
            elif condition == 7:
                choice = 10
            elif condition == 8:
                choice = 10
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 15
            elif condition == 14:
                choice = 15
            elif condition == 15:
                choice = 15
            elif condition == 16:
                choice = 15        
        # 第3~5球
        elif int(setstate[0][0]) == 5 or int(setstate[0][0]) == 7 or int(setstate[0][0]) == 9:
            if condition == 1:
                choice = 13
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 27
            elif condition == 4:
                choice = 27
            elif condition == 5:
                choice = 27#23
            elif condition == 6:
                choice = 27#23
            elif condition == 7:
                choice = 14
                roll = 0
            elif condition == 8:
                choice = 14
                roll = 0
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 15
            elif condition == 14:
                choice = 27
            elif condition == 15:
                choice = 15
            elif condition == 16:
                choice = 27 
        # 第6~7球
        elif int(setstate[0][0]) == 13 or int(setstate[0][0]) == 11:
            if condition == 1:
                choice = 24
            elif condition == 2:
                choice = 24
            elif condition == 3:
                choice = 9
                mode = 1
            elif condition == 4:
                choice = 9
                mode = 1
            elif condition == 5:
                choice = 27#23
            elif condition == 6:
                choice = 27#23
            elif condition == 7:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score <-1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 8:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score <-1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 24
            elif condition == 12:
                choice = 24
            elif condition == 13:
                choice = 15
            elif condition == 14:
                choice = 15
            elif condition == 15:
                choice = 27
            elif condition == 16:
                choice = 27
        #第8球
        elif int(setstate[0][0]) == 15:
            x_block, y_block, no_trail_block=Score_block(position,order,setstate)
            if no_trail_block == 0:
                choice = 22
            else:
                if condition == 1:
                    choice = 23
                elif condition == 2:
                    choice = 17
                elif condition == 3:
                    choice = 1
                elif condition == 4:
                    choice = 1
                elif condition == 5:
                    choice = 1
                elif condition == 6:
                    choice = 1
                elif condition == 7:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    if score < -1:
                        choice = 30
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 14
                            roll = 0
                        elif flag_mynoinhouse == 6:
                            x, y, number_curling = Stick(nearest[0], nearest[1], position)
                            if number_curling == 0:
                                choice = 14
                                roll = 0
                            else:
                                choice = 10
                        else:
                            choice = 14
                            roll = 0
                elif condition == 8:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    if score < -1:
                        choice = 9
                        mode = 1
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 14
                            roll = 0
                        elif flag_mynoinhouse == 6:
                            x, y, number_curling = Stick(nearest[0], nearest[1], position)
                            if number_curling == 0:
                                choice = 14
                                roll = 0
                            else:
                                choice = 9
                                mode = 1
                        else:
                            choice = 30
                elif condition == 9:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    x, y, number_curling = Stick(nearest[0], nearest[1], position)
                    if score < -1:
                        if number_curling == 0:
                            choice = 26
                        else:
                            choice = 28
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分                      
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 11
                        elif flag_mynoinhouse == 6:
                            if number_curling == 1:
                                choice = 28
                            else:
                                choice = 11
                        else:
                            choice = 11
                elif condition == 10:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    x, y, number_curling = Stick(nearest[0], nearest[1], position)
                    if score < -1:
                        if number_curling == 0:
                            choice = 26
                        else:
                            choice = 28
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分                      
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 11
                        elif flag_mynoinhouse == 6:
                            if number_curling == 1:
                                choice = 28
                            else:
                                choice = 11
                        else:
                            choice = 11
                elif condition == 11:
                    choice = 23
                elif condition == 12:
                    choice = 9
                    mode = 1
                elif condition == 13:
                    choice = 1
                elif condition == 14:
                    choice = 1
                elif condition == 15:
                    choice = 1
                elif condition == 16:
                    choice = 1

    # 第2~8局，领先2分及以上, 先手
    if scorediff >= 2 and (not InitiativeOrGote(order, setstate)) and int(setstate[0][1]) > 0:
        # 第1球
        if int(setstate[0][0]) == 0:
                choice = 23
        # 第2~3球
        elif int(setstate[0][0]) == 2 or int(setstate[0][0]) == 4:
            if condition == 1:
                choice = 23
            elif condition == 2:
                choice = 9
                mode = 2 
            elif condition == 3:
                choice = 21
            elif condition == 4:
                choice = 27
            elif condition == 5:
                choice = 6
            elif condition == 6:
                choice = 6
            elif condition == 7:
                choice = 10
            elif condition == 8:
                choice = 10
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 15
            elif condition == 14:
                choice = 15
            elif condition == 15:
                choice = 21
            elif condition == 16:
                choice = 21
        # 第4~5球
        elif int(setstate[0][0]) == 6 or int(setstate[0][0]) == 8:
            if condition == 1:
                choice = 23
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 9
                mode = 1
            elif condition == 4:
                choice = 9
                mode = 1
            elif condition == 5:
                choice = 27
            elif condition == 6:
                choice = 27
            elif condition == 7:
                choice = 14
                roll = 0
            elif condition == 8:
                choice = 14
                roll = 0
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 15
            elif condition == 14:
                choice = 15
            elif condition == 15:
                choice = 21
            elif condition == 16:
                choice = 21
        # 第6~7球
        elif int(setstate[0][0]) == 12  or int(setstate[0][0]) == 10:
            if condition == 1:
                choice = 23
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 23
            elif condition == 4:
                choice = 23
            elif condition == 5:
                choice = 23
            elif condition == 6:
                choice = 23
            elif condition == 7:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score <-1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 8:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score <-1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 9:
                x, y, number_curling = Stick(nearest[0], nearest[1], position)
                if number_curling == 0:
                    choice = 11
                else:
                    choice = 28
            elif condition == 10:
                x, y, number_curling = Stick(nearest[0], nearest[1], position)
                if number_curling == 0:
                    choice = 11
                else:
                    choice = 28
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 23
            elif condition == 14:
                choice = 23
            elif condition == 15:
                choice = 23
            elif condition == 16:
                choice = 23
        # 第8球
        elif int(setstate[0][0]) == 14:
            if condition == 1:
                choice = 16
            elif condition == 2:
                choice = 23
            elif condition == 3:
                choice = 23
            elif condition == 4:
                choice = 23
            elif condition == 5:
                choice = 23
            elif condition == 6:
                choice = 23
            elif condition == 7:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score <-1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 8:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score <-1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 9:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                x, y, number_curling = Stick(nearest[0], nearest[1], position)
                if score < -1:
                    if number_curling == 0:
                        choice = 26
                    else:
                        choice = 28
                else:
                    if number_curling == 1:
                        choice = 28
                    else:
                        choice = 11
            elif condition == 10:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    x, y, number_curling = Stick(nearest[0], nearest[1], position)
                    if score < -1:
                        if number_curling == 0:
                            choice = 26
                        else:
                            choice = 28
                    else:
                        if number_curling == 1:
                            choice = 28
                        else:
                            choice = 11
            elif condition == 11:
                choice = 23
            elif condition == 12:
                choice = 23
            elif condition == 13:
                choice = 23
            elif condition == 14:
                choice = 23
            elif condition == 15:
                choice = 23
            elif condition == 16:
                choice = 23

    # 第2~7局，领先, 后手
    elif scorediff > 0 and InitiativeOrGote(order, setstate) and int(setstate[0][1]) > 0 and int(setstate[0][1]) < 7:
        # 第1球
        if int(setstate[0][0]) == 1:
            if condition == 1:
                choice = 18
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
        # 第2球
        elif int(setstate[0][0]) == 3:
            if condition == 1:
                choice = 13
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 27
            elif condition == 4:
                choice = 27
            elif condition == 5:
                choice = 27
            elif condition == 6:
                choice = 27
            elif condition == 7:
                choice = 9
                mode = 2
            elif condition == 8:
                choice = 9
                mode = 2
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 27
            elif condition == 14:
                choice = 27
            elif condition == 15:
                choice = 27
            elif condition == 16:
                choice = 27
        # 第3~5球
        elif int(setstate[0][0]) == 5 or int(setstate[0][0]) == 7 or int(setstate[0][0]) == 9:
            if condition == 1:
                choice = 13
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 27
            elif condition == 4:
                choice = 27
            elif condition == 5:
                choice = 27#23
            elif condition == 6:
                choice = 27#23
            elif condition == 7:
                choice = 14
                roll = 0
            elif condition == 8:
                choice = 14
                roll = 0
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 15
            elif condition == 14:
                choice = 15
            elif condition == 15:
                choice = 27
            elif condition == 16:
                choice = 27      
        # 第6~7球
        elif int(setstate[0][0]) == 13 or int(setstate[0][0]) == 11:
            if condition == 1:
                choice = 24
            elif condition == 2:
                choice = 24
            elif condition == 3:
                choice = 9
                mode = 1
            elif condition == 4:
                choice = 9
                mode = 1
            elif condition == 5:
                choice = 27
            elif condition == 6:
                choice = 27
            elif condition == 7:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score <-1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 8:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score <-1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 24 
            elif condition == 12:
                choice = 24
            elif condition == 13:
                choice = 15
            elif condition == 14:
                choice = 15
            elif condition == 15:
                choice = 27
            elif condition == 16:
                choice = 27           
        #第8球
        elif int(setstate[0][0]) == 15:
            x_block, y_block, no_trail_block=Score_block(position,order,setstate)
            if no_trail_block == 0:
                choice = 22
            else:
                if condition == 1:
                    choice = 23
                elif condition == 2:
                    choice = 17
                elif condition == 3:
                    choice = 27
                elif condition == 4:
                    choice = 27
                elif condition == 5:
                    choice = 27
                elif condition == 6:
                    choice = 27
                elif condition == 7:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    if score < -1:
                        choice = 30
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 14
                            roll = 0
                        elif flag_mynoinhouse == 6:
                            x, y, number_curling = Stick(nearest[0], nearest[1], position)
                            if number_curling == 0:
                                choice = 14
                                roll = 0
                            else:
                                choice = 10
                        else:
                            choice = 14
                            roll = 0
                elif condition == 8:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    if score < -1:
                        choice = 9
                        mode = 1
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 14
                            roll = 0
                        elif flag_mynoinhouse == 6:
                            x, y, number_curling = Stick(nearest[0], nearest[1], position)
                            if number_curling == 0:
                                choice = 14
                                roll = 0
                            else:
                                choice = 9
                                mode = 1
                        else:
                            choice = 30
                elif condition == 9:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    x, y, number_curling = Stick(nearest[0], nearest[1], position)
                    if score < -1:
                        if number_curling == 0:
                            choice = 26
                        else:
                            choice = 28
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分                      
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 11
                        elif flag_mynoinhouse == 6:
                            if number_curling == 1:
                                choice = 28
                            else:
                                choice = 11
                        else:
                            choice = 11
                elif condition == 10:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    x, y, number_curling = Stick(nearest[0], nearest[1], position)
                    if score < -1:
                        if number_curling == 0:
                            choice = 26
                        else:
                            choice = 28
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分                      
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 11
                        elif flag_mynoinhouse == 6:
                            if number_curling == 1:
                                choice = 28
                            else:
                                choice = 11
                        else:
                            choice = 11
                elif condition == 11:
                    choice = 23
                elif condition == 12:
                    choice = 9
                    mode = 1
                elif condition == 13:
                    choice = 9
                    mode = 1
                elif condition == 14:
                    choice = 9
                    mode = 1
                elif condition == 15:
                    choice = 9
                    mode = 1
                elif condition == 16:
                    choice = 9
                    mode = 1
    
    # 第2~8局, 落后，先手
    elif scorediff < 0 and (not InitiativeOrGote(order, setstate)) and int(setstate[0][1]) > 0:
        # 第1球
        if int(setstate[0][0]) == 0:
                choice = 2
        # 第2球
        elif int(setstate[0][0]) == 2: 
                choice = 1
        # 第3球
        elif int(setstate[0][0]) == 4: 
                choice = 9
                mode = 1
        # 第4~5球
        elif int(setstate[0][0]) == 6 or int(setstate[0][0]) == 8:
            if condition == 1:
                choice = 1
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 21
            elif condition == 4:
                choice = 27
            elif condition == 5:
                choice = 21
            elif condition == 6:
                choice = 21
            elif condition == 7:
                choice = 10
            elif condition == 8:
                choice = 10
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 21
            elif condition == 14:
                choice = 23
            elif condition == 15:
                choice = 21
            elif condition == 16:
                choice = 21
        #第6球
        elif int(setstate[0][0]) == 10:
            if condition == 1:
                choice = 1
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 27
            elif condition == 4:
                choice = 27
            elif condition == 5:
                choice = 21
            elif condition == 6:
                choice = 21
            elif condition == 7:
                choice = 10
            elif condition == 8:
                choice = 10
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 15
            elif condition == 14:
                choice = 15
            elif condition == 15:
                choice = 15
            elif condition == 16:
                choice = 15                     
        # 第7球
        elif int(setstate[0][0]) == 12:
            if condition == 1:
                choice = 3
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 23
            elif condition == 4:
                choice = 23
            elif condition == 5:
                choice = 23
            elif condition == 6:
                choice = 23
            elif condition == 7:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score <-1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 8:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score <-1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 9:
                x, y, number_curling = Stick(nearest[0], nearest[1], position)
                if number_curling == 0:
                    choice = 11
                else:
                    choice = 28
            elif condition == 10:
                x, y, number_curling = Stick(nearest[0], nearest[1], position)
                if number_curling == 0:
                    choice = 11
                else:
                    choice = 28
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 23
            elif condition == 14:
                choice = 23
            elif condition == 15:
                choice = 23
            elif condition == 16:
                choice = 23
        # 第8球
        elif int(setstate[0][0]) == 14:
            if condition == 1:
                choice = 16
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 23
            elif condition == 4:
                choice = 23
            elif condition == 5:
                choice = 23
            elif condition == 6:
                choice = 23
            elif condition == 7:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score < -1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 8:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score < -1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 9:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    x, y, number_curling = Stick(nearest[0], nearest[1], position)
                    if score < -1:
                        if number_curling == 0:
                            choice = 26
                        else:
                            choice = 28
                    else:
                        if number_curling == 1:
                            choice = 28
                        else:
                            choice = 11
            elif condition == 10:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    x, y, number_curling = Stick(nearest[0], nearest[1], position)
                    if score < -1:
                        if number_curling == 0:
                            choice = 26
                        else:
                            choice = 28
                    else:
                        if number_curling == 1:
                            choice = 28
                        else:
                            choice = 11
            elif condition == 11:
                choice = 23
            elif condition == 12:
                choice = 23
            elif condition == 13:
                choice = 23
            elif condition == 14:
                choice = 23
            elif condition == 15:
                choice = 23
            elif condition == 16:
                choice = 23

    # 第2~8局，落后大于1分, 后手
    elif scorediff < -1 and InitiativeOrGote(order, setstate) and int(setstate[0][1]) > 0:
        # 第1球
        if int(setstate[0][0]) == 1:
            choice = 4
        # 第2球
        elif int(setstate[0][0]) == 3:        
            choice = 5
        # 第3~4球
        elif int(setstate[0][0]) == 7 or int(setstate[0][0]) == 5:
            if condition == 1:
                choice = 4
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 27
            elif condition == 4:
                choice = 27
            elif condition == 5:
                choice = 27#6
            elif condition == 6:
                choice = 27#6
            elif condition == 7:
                choice = 14
                roll = 0
            elif condition == 8:
                choice = 14
                roll = 0
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 15
            elif condition == 14:
                choice = 15
            elif condition == 15:
                choice = 15
            elif condition == 16:
                choice = 15      
        # 第5~6球
        elif int(setstate[0][0]) == 9 or int(setstate[0][0]) == 11:
            if condition == 1:
                choice = 4
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 27
            elif condition == 4:
                choice = 27
            elif condition == 5:
                choice = 27
            elif condition == 6:
                choice = 27
            elif condition == 7:
                choice = 14
                roll = 0
            elif condition == 8:
                choice = 14
                roll = 0
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 15
            elif condition == 14:
                choice = 15
            elif condition == 15:
                choice = 15
            elif condition == 16:
                choice = 15            
        # 第7球
        elif int(setstate[0][0]) == 13:
            if condition == 1:
                choice = 4
            elif condition == 2:
                choice = 24
            elif condition == 3:
                choice = 27
            elif condition == 4:
                choice = 29
            elif condition == 5:
                choice = 27
            elif condition == 6:
                choice = 29
            elif condition == 7:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score <-1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 8:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score <-1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 24
            elif condition == 12:
                choice = 24
            elif condition == 13:
                choice = 27
            elif condition == 14:
                choice = 27
            elif condition == 15:
                choice = 27
            elif condition == 16:
                choice = 27
        # 第8球
        elif int(setstate[0][0]) == 15:
            x_block,y_block,no_trail_block=Score_block(position,order,setstate)
            if no_trail_block == 0:
                choice = 22
            else:
                if condition == 1:
                    choice = 23
                elif condition == 2:
                    choice = 17
                elif condition == 3:
                    choice = 27
                elif condition == 4:
                    choice = 27
                elif condition == 5:
                    choice = 27
                elif condition == 6:
                    choice = 27
                elif condition == 7:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    if score < -1:
                        choice = 30
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 14
                            roll = 0
                        elif flag_mynoinhouse == 6:
                            x, y, number_curling = Stick(nearest[0], nearest[1], position)
                            if number_curling == 0:
                                choice = 14
                                roll = 0
                            else:
                                choice = 10
                        else:
                            choice = 14
                            roll = 0
                elif condition == 8:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    if score < -1:
                        choice = 9
                        mode = 1
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 14
                            roll = 0
                        elif flag_mynoinhouse == 6:
                            x, y, number_curling = Stick(nearest[0], nearest[1], position)
                            if number_curling == 0:
                                choice = 14
                                roll = 0
                            else:
                                choice = 9
                                mode = 1
                        else:
                            choice = 30
                elif condition == 9:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    x, y, number_curling = Stick(nearest[0], nearest[1], position)
                    if score < -1:
                        if number_curling == 0:
                            choice = 26
                        else:
                            choice = 28
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分                      
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 11
                        elif flag_mynoinhouse == 6:
                            if number_curling == 1:
                                choice = 28
                            else:
                                choice = 11
                        else:
                            choice = 11
                elif condition == 10:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    x, y, number_curling = Stick(nearest[0], nearest[1], position)
                    if score < -1:
                        if number_curling == 0:
                            choice = 26
                        else:
                            choice = 28
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分                      
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 11
                        elif flag_mynoinhouse == 6:
                            if number_curling == 1:
                                choice = 28
                            else:
                                choice = 11
                        else:
                            choice = 11
                elif condition == 11:
                    choice = 23
                elif condition == 12:
                    choice = 9
                    mode = 1
                elif condition == 13:
                    choice = 27
                elif condition == 14:
                    choice = 27
                elif condition == 15:
                    choice = 27
                elif condition == 16:
                    choice = 27
           
    # 第1~8局，平局或领先1分, 先手
    elif (scorediff == 0 or scorediff ==1) and (not InitiativeOrGote(order, setstate)) and int(setstate[0][1]) >= 0:
        # 第1球
        if int(setstate[0][0]) == 0:
                choice = 1
        # 第2球
        elif int(setstate[0][0]) == 2:
            if condition == 7 or condition == 8:
                choice = 10
            elif condition == 9 or condition == 10:
                choice = 11
            else:
                choice = 9
                mode = 2
        # 第3球
        elif int(setstate[0][0]) == 4:
            if condition == 1:
                choice = 1
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 27
            elif condition == 4:
                choice = 27
            elif condition == 5:
                choice = 27
            elif condition == 6:
                choice = 27
            elif condition == 7:
                choice = 10
            elif condition == 8:
                choice = 10
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 27
            elif condition == 14:
                choice = 27
            elif condition == 15:
                choice = 27
            elif condition == 16:
                choice = 27
        #第4~5球
        elif int(setstate[0][0]) == 6 or int(setstate[0][0]) == 8 :
            if condition == 1:
                choice = 1
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 27
            elif condition == 4:
                choice = 27
            elif condition == 5:
                choice = 21
            elif condition == 6:
                choice = 21
            elif condition == 7:
                choice = 14
                roll = 0
            elif condition == 8:
                choice = 14
                roll = 0
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 27
            elif condition == 14:
                choice = 27
            elif condition == 15:
                choice = 15
            elif condition == 16:
                choice = 15           
        # 第6~7球
        elif int(setstate[0][0]) == 12 or int(setstate[0][0]) == 10:
            if condition == 1:
                choice = 16
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 23
            elif condition == 4:
                choice = 23
            elif condition == 5:
                choice = 23
            elif condition == 6:
                choice = 23
            elif condition == 7:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score < -1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 8:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score < -1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 9:
                x, y, number_curling = Stick(nearest[0], nearest[1], position)
                if number_curling == 0:
                    choice = 11
                else:
                    choice = 28
            elif condition == 10:
                x, y, number_curling = Stick(nearest[0], nearest[1], position)
                if number_curling == 0:
                    choice = 11
                else:
                    choice = 28
            elif condition == 11:
                choice = 23
            elif condition == 12:
                choice = 23
            elif condition == 13:
                choice = 23
            elif condition == 14:
                choice = 23
            elif condition == 15:
                choice = 23
            elif condition == 16:
                choice = 23         
        # 第8球
        elif int(setstate[0][0]) == 14:
            if condition == 1:
                choice = 16
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 23
            elif condition == 4:
                choice = 23
            elif condition == 5:
                choice = 23
            elif condition == 6:
                choice = 23
            elif condition == 7:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score < -1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 8:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score < -1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 9:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    x, y, number_curling = Stick(nearest[0], nearest[1], position)
                    if score < -1:
                        if number_curling == 0:
                            choice = 26
                        else:
                            choice = 28
                    else:
                        if number_curling == 1:
                            choice = 28
                        else:
                            choice = 11
            elif condition == 10:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    x, y, number_curling = Stick(nearest[0], nearest[1], position)
                    if score < -1:
                        if number_curling == 0:
                            choice = 26
                        else:
                            choice = 28
                    else:
                        if number_curling == 1:
                            choice = 28
                        else:
                            choice = 11
            elif condition == 11:
                choice = 23
            elif condition == 12:
                choice = 23
            elif condition == 13:
                choice = 23
            elif condition == 14:
                choice = 23
            elif condition == 15:
                choice = 23
            elif condition == 16:
                choice = 23

    # 第2~8局，平局落后1分, 后手
    elif (scorediff == 0 or scorediff == -1) and InitiativeOrGote(order, setstate) and int(setstate[0][1]) > 0 and int(setstate[0][1]) <= 7:
        # 第1球
        if int(setstate[0][0]) == 1:
            choice = 4
        # 第2球
        elif int(setstate[0][0]) == 3:       
                choice = 9
                mode = 2
        # 第3~4球
        elif int(setstate[0][0]) == 5 or int(setstate[0][0]) == 7 :
            if condition == 1:
                choice = 4
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 27
            elif condition == 4:
                choice = 27
            elif condition == 5:
                choice = 27
            elif condition == 6:
                choice = 27
            elif condition == 7:
                choice = 10
            elif condition == 8:
                choice = 10
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 27
            elif condition == 14:
                choice = 27
            elif condition == 15:
                choice = 15
            elif condition == 16:
                choice = 15
        # 第5~6球
        elif int(setstate[0][0]) == 9 or int(setstate[0][0]) == 11:
            if condition == 1:
                choice = 4
            elif condition == 2:
                choice = 9
                mode = 2
            elif condition == 3:
                choice = 27
            elif condition == 4:
                choice = 27
            elif condition == 5:
                choice = 27
            elif condition == 6:
                choice = 27
            elif condition == 7:
                choice = 14
                roll = 0
            elif condition == 8:
                choice = 14
                roll = 0
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 9
                mode = 2
            elif condition == 12:
                choice = 9
                mode = 2
            elif condition == 13:
                choice = 27
            elif condition == 14:
                choice = 27
            elif condition == 15:
                choice = 15
            elif condition == 16:
                choice = 15
        # 第7球
        elif int(setstate[0][0]) == 13:
            if condition == 1:
                choice = 4
            elif condition == 2:
                choice = 24
            elif condition == 3:
                choice = 27
            elif condition == 4:
                choice = 29
            elif condition == 5:
                choice = 27
            elif condition == 6:
                choice = 29
            elif condition == 7:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score < -1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 8:
                score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                if score < -1:
                    choice = 10
                else:
                    choice = 14
                    roll = 0
            elif condition == 9:
                choice = 11
            elif condition == 10:
                choice = 11
            elif condition == 11:
                choice = 24
            elif condition == 12:
                choice = 24
            elif condition == 13:
                choice = 27
            elif condition == 14:
                choice = 29
            elif condition == 15:
                choice = 27
            elif condition == 16:
                choice = 29
        # 第8球
        elif int(setstate[0][0]) == 15:
            x_block,y_block,no_trail_block=Score_block(position,order,setstate)
            if no_trail_block == 0:
                choice = 22
            else:
                if condition == 1:
                    choice = 23
                elif condition == 2:
                    choice = 17
                elif condition == 3:
                    choice = 27
                elif condition == 4:
                    choice = 27
                elif condition == 5:
                    choice = 27
                elif condition == 6:
                    choice = 27
                elif condition == 7:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    if score < -1:
                        choice = 30
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 14
                            roll = 0
                        elif flag_mynoinhouse == 6:
                            x, y, number_curling = Stick(nearest[0], nearest[1], position)
                            if number_curling == 0:
                                choice = 14
                                roll = 0
                            else:
                                choice = 10
                        else:
                            choice = 14
                            roll = 0
                elif condition == 8:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    if score < -1:
                        choice = 9
                        mode = 1
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 14
                            roll = 0
                        elif flag_mynoinhouse == 6:
                            x, y, number_curling = Stick(nearest[0], nearest[1], position)
                            if number_curling == 0:
                                choice = 14
                                roll = 0
                            else:
                                choice = 9
                                mode = 1
                        else:
                            choice = 30
                elif condition == 9:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    x, y, number_curling = Stick(nearest[0], nearest[1], position)
                    if score < -1:
                        if number_curling == 0:
                            choice = 26
                        else:
                            choice = 28
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分                      
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 11
                        elif flag_mynoinhouse == 6:
                            if number_curling == 1:
                                choice = 28
                            else:
                                choice = 11
                        else:
                            choice = 11
                elif condition == 10:
                    score, mysc, mypo, opsc, oppo = scoref(order,position,setstate)
                    x, y, number_curling = Stick(nearest[0], nearest[1], position)
                    if score < -1:
                        if number_curling == 0:
                            choice = 26
                        else:
                            choice = 28
                    else:
                        # 对方只有一个得分壶，后手最后一壶要判断自己大本营内有几个壶，如果有壶则打掉对方得分壶，否则直接进去得分                      
                        flag_mynoinhouse = 0
                        for i in range(7):
                            if not(is_in_house(float(position[0][4 * i + 2]), float(position[0][4 * i + 3]))):
                                flag_mynoinhouse += 1
                        if flag_mynoinhouse <= 5:
                            choice = 11
                        elif flag_mynoinhouse == 6:
                            if number_curling == 1:
                                choice = 28
                            else:
                                choice = 11
                        else:
                            choice = 11
                elif condition == 11:
                    choice = 23
                elif condition == 12:
                    choice = 9
                    mode = 2
                elif condition == 13:
                    choice = 27
                elif condition == 14:
                    choice = 27
                elif condition == 15:
                    choice = 27
                elif condition == 16:
                    choice = 27

    # 给出投掷信息(注意: 这里的offset = x - 2.375, 即相对中心的偏移量, 而非赛场坐标系下的x)
    shot = action(choice, mode, nearest, nearest_enemy, block, block_actual, position, order,setstate)
    # print('condition ' + str(condition))
    # print('choice ' + str(choice))
    # print('mode ' + str(mode))
    return shot

# 擦冰策略(有待改进!!!)
def sweepStrategy():
    # 擦冰与否
    if False:
        sweep_or_not = 1
    else:
        sweep_or_not = 0
    # 擦冰距离
    if sweep_or_not == 1:
        sweep_distance = 4
    else:
        sweep_distance = 0
    return sweep_or_not, sweep_distance

# TCP通信
def tcpLink(host, port):
    obj = socket.socket()
    obj.connect((host, port))
    return obj

# 接收消息
def recvMessage(obj):
    ret = str(obj.recv(1024), encoding = 'utf-8')
    if ret:
        print("recv: " + ret)
    return ret

# 发送消息
def sendMessage(obj, message):
    obj.send(bytes(message, encoding = 'utf-8'))
    print("send: " + message)

# 处理消息
def processMessage(ret, order, setstate, position, scorediff):
    messageList = ret.split(" ")
    
    # NAME
    if messageList[0] == "NAME":
        order = messageList[1]
        # if order == str("Player1"):
        #     print("玩家1，首局先手")
        # else:
        #     print("玩家2，首局后手")

    # ISREADY -> 服务器准备完毕
    if messageList[0] == "ISREADY":
        time.sleep(0.5)
        # 准备完毕
        sendMessage(obj, "READYOK")
    
    # POSITION -> 16个冰壶球的当前坐标((0,0)表示未投掷或已出界)
    if messageList[0] == "POSITION":
        if position:
            position = []
        position.append(ret.split(" ")[1:-1])
    
    # SETSTATE -> 当前完成投掷数-当前完成对局数-总对局数-预备投掷者(0为持蓝色球者,1为持红色球者)
    if messageList[0] == "SETSTATE":
        if setstate:
            setstate = []
        setstate.append(ret.split(" ")[1:-1])
        #score,mysc,opsc = scoref(order,position,setstate)
    
    # GO -> 请求执行动作
    if (messageList[0] == "GO") or (ret.find('GO') != -1):
        shot = strategy(order, setstate, position, scorediff)
        sendMessage(obj, shot)
    
    # MOTIONINFO -> 赛道中间时运动状态信息
    if messageList[0] == "MOTIONINFO":
        # x_coordinate = float(messageList[1])
        # y_coordinate = float(messageList[2])
        # x_velocity = float(messageList[3])
        # y_velocity = float(messageList[4])
        # angular_velocity = float(messageList[5])
        
        # 擦冰
        sweep_or_not, sweep_distance = sweepStrategy()
        if sweep_or_not == 1:
            sweepCommand = str("SWEEP " + str(sweep_distance))
            sendMessage(obj, sweepCommand)

    # SCORE -> 本局比赛得分
    if messageList[0] == "SCORE":
        # 累计分差
        scorediff += int(messageList[1])

    return order, setstate, position, scorediff

# 主函数
if __name__ == '__main__':
    # TCP通信
    obj = tcpLink(host, port)
    # 发送消息: NAME -> 姓名
    sendMessage(obj, "NAME " + name)
    while True:
        # 接收消息
        ret = recvMessage(obj)
        # 处理(并发送)消息
        order, setstate, position, scorediff = processMessage(ret, order, setstate, position, scorediff)