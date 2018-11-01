# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 16:37:04 2018
"""
import numpy as np
import matplotlib.pyplot as plt
import os.path
from scipy import optimize
from xlwt import Workbook

from InteractiveClass import SelectCurve

def ExtractDataFromFile(dataStoreDir, fileName):
    #从.txt文件提取数据
    outputf = open(fileName, 'r')
    lines = outputf.readlines()
    #inputf = open("write.txt", 'w')
    
    time = []
    inputBarChannel = []
    transBarChannel = []
    
    for line in lines[6: ]:
        data = line.split()
        time.append(float(data[0]))
        inputBarChannel.append(float(data[1]))
        transBarChannel.append(-float(data[4]))
      
    outputf.close()

    time = np.array(time)
    inputBarChannel = np.array(inputBarChannel)
    transBarChannel = np.array(transBarChannel)
    
    DrawChannelSignalsPlot(dataStoreDir, "Original Experimental Data.png", time, 
                        inputBarChannel, transBarChannel)
    
    return time, inputBarChannel, transBarChannel


def DrawChannelSignalsPlot(dataStoreDir, plotName, time, inputBarChannel, transBarChannel):
    #绘制信号图
    plt.close('all')
    
    fig = plt.figure(figsize = (8, 4))
    ax = fig.add_subplot(111)

    ax.plot(time, inputBarChannel, label="Input Bar", color="red", linewidth=2)
    ax.plot(time, transBarChannel, label="Transmission Bar", color="b", linewidth=2)
    
    ch = SelectCurve(ax)

    plt.xlabel("Time/$s$")
    plt.ylabel("Voltage/$v$")
    plt.legend()
    plt.title(plotName.split(".")[0])
    
    filePath = os.path.join(dataStoreDir, plotName)
    plt.savefig(filePath, dpi=240)

    plt.show()

def DrawWavePlot(dataStoreDir, plotName, time, inputWave, reflectWave, transWave):
    stressBalance = inputWave + reflectWave

    # 绘制波形图
    plt.close('all')

    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(111)

    ax.plot(time, inputWave, label="Input Wave", color="red", linewidth=2)
    ax.plot(time, reflectWave, label="Reflect Wave", color="b", linewidth=2)
    ax.plot(time, transWave, label="Transmission Wave", color="y", linewidth=2)
    ax.plot(time, stressBalance, label="Stress Balance Examination Curve", color="green", linestyle="dashed",
            linewidth=1.5)

    ch = SelectCurve(ax)

    plt.xlabel("Time/$s$")
    plt.ylabel("Voltage/$v$")
    plt.legend()
    plt.title(plotName.split(".")[0])

    filePath = os.path.join(dataStoreDir, plotName)
    plt.savefig(filePath, dpi=240)

    plt.show()
    
def MovingChannelSignals(dataStoreDir, time, inputBarChannel, transBarChannel): 
    #上下平移入射波和投射波——归零
    recordInput = inputBarChannel[0]
    recordTrans = transBarChannel[0]
    
    inputChannel = inputBarChannel - recordInput
    transChannel = transBarChannel - recordTrans
    
    DrawChannelSignalsPlot(dataStoreDir, "Moving Singals Plot.png", 
                           time, inputChannel, transChannel)
    
    return inputChannel, transChannel


def FindEndPoints(saddlePoint, saddlePointPos, data):
    #寻找信号波的区间端点
    global startPoint, endPoint
    for counter, value in enumerate(data[saddlePointPos: 0: -1]):
        if abs(value / saddlePoint) <= 0.05:
            startPoint = saddlePointPos - counter
            break
        
    for counter, value in enumerate(data[saddlePointPos: len(data)]):
        if abs(value / saddlePoint) <= 0.05:
            endPoint = saddlePointPos + counter
            break
        
    return startPoint, endPoint


def FindingSections(dataStoreDir, time, inputChannel, transChannel):
    """
    寻找入射波、反射波和投射波
    """
    saddleInput = np.max(inputChannel)
    saddleInputPos = np.argmax(inputChannel)

    saddleReflect = np.min(inputChannel)
    saddleReflectPos = np.argmin(inputChannel)
    
    saddleTrans = np.max(transChannel)
    saddleTransPos = np.argmax(transChannel)
    
    startInput, endInput = FindEndPoints(saddleInput, saddleInputPos, inputChannel)
    startReflect, endReflect = FindEndPoints(saddleReflect, saddleReflectPos, inputChannel)
    startTrans, endTrans = FindEndPoints(saddleTrans, saddleTransPos, transChannel)

    keyIn = input("Starting point of input wave(Press ENTER to use default value):")
    if keyIn != "":
        startInput = int(keyIn)

    keyIn = input("Starting point of reflect wave(Press ENTER to use default value):")
    if keyIn != "":
        startInput = int(keyIn)

    keyIn = input("Starting point of transmission wave(Press ENTER to use default value):")
    if keyIn != "":
        startInput = int(keyIn)


    startLength = endInput - startInput
    reflectLength = endReflect - startReflect
    transLength = endTrans - startTrans

    timeLength = startLength if startLength <= reflectLength else reflectLength
    timeLength = transLength if transLength <= timeLength else timeLength
    print(timeLength)
    
    inputWave = inputChannel[startInput: startInput + timeLength]
    reflectWave = inputChannel[startReflect: startReflect + timeLength]
    transWave = transChannel[startTrans: startTrans + timeLength]
    timeSpace = time[1] - time[0]
    timeModified = np.arange(0, timeLength * timeSpace, timeSpace)

    DrawWavePlot(dataStoreDir, "Input, Reflect and Transmission Wave.png", timeModified, inputWave, reflectWave, transWave)
    
    return timeModified, inputWave, reflectWave, transWave

def Calculations(time, reflectWave, transWave, K, barWaveSpeed, 
                 barElasticModulus, areaBar, specimenLength, 
                 areaSpecimen):
    #计算应力、应变、应变率
    reflectStrain = -(2100 / (K * 1000)) * (reflectWave - reflectWave[0]) / (30 - reflectWave + reflectWave[0])
    transStrain = (2100 / (K * 1000)) * ((transWave - transWave[0]) / (30 - transWave + transWave[0]))
    
    engStrainRate = 2 * barWaveSpeed * 1000 * reflectStrain / specimenLength
    engStress = barElasticModulus * (areaBar / areaSpecimen) * transStrain
    
    engStrain = np.zeros_like(time)
    timeSpace = time[1] - time[0]
    for i in np.arange(1, len(time), 1):
        engStrain[i] = engStrain[i - 1] + (engStrainRate[i] + engStrainRate[i - 1]) * timeSpace / 2
        
    return engStress, engStrain, engStrainRate

def residuals(p, X, Y):
    k, b = p
    return Y - k * X - b

def FittingStrainRate(dataStoreDir,time, strain, flag):
    #拟合时间-应变曲线，获得应变率
    for counter, temp in enumerate(strain):
        if temp >= 0.05 * max(strain):
            markStart = counter
            break
    
    X = time[markStart: -1]
    Y = strain[markStart: -1]
    #将除p以外的参数打包至args中
    r = optimize.leastsq(residuals, [60, 3], args = (X, Y))
    k, b = r[0]
    
    if flag == True:
        YFitting = [k * temp + b for temp in X]

        plt.close('all')

        fig, ax = plt.subplots(figsize = (8, 4))
        ax.plot(time, strain, "r_", label = "Calculated strain", linewidth = 2)
        ax.plot(X, YFitting, "b--", label = "Fitting curve", linewidth = 2)
        ax.text(0.98, 0.05, 
                 'Fitting linear equation:\n $\\varepsilon = {}t{:+.3f}$'.format(round(k, 3), round(b, 3)),
                 horizontalalignment = 'right', verticalalignment = 'bottom', 
                 transform = ax.transAxes, 
                 bbox = {"facecolor": "blue", "alpha": 0.15})
        plt.xlabel("Time/$s$")
        plt.ylabel("Strain $\\varepsilon$")
        plt.title("Strain - Time curve")
        plt.legend()
        
        filePath = os.path.join(dataStoreDir, "Strain-Time and Fitting Curve.png")
        plt.savefig(filePath, dpi = 240)
        
        plt.show()
    
    return k, b

def DrawStressStrainPlot(dataStoreDir, stress, strain):
    #绘制应变-应力曲线
    
    #如果直接写stressReverse = stress, 对stressReverse的操作也会改变stress!!!
    stressReverse = stress.copy()[::-1]
    for counter, temp in enumerate(stressReverse, 1):
        if temp >= 0.5 * max(stress):
            markEnd = len(stress) - counter
            break

    plt.close('all')

    plt.figure(figsize = (8, 4))
    plt.plot(strain[1: markEnd], stress[1: markEnd], color = "red", 
             linewidth = 2)
    plt.xlabel("Engineering Strain $\\varepsilon$")
    plt.ylabel("Engineering Stress $\\sigma/MPa$")
    plt.title("$\\sigma$-$\\varepsilon$ curve")
    
    filePath = os.path.join(dataStoreDir, "Stress-Strain Curve.png")
    plt.savefig(filePath, dpi=240)

    plt.show()
    
def EngineeringToTrue(engStress, engStrain, engStrainRate):
    #工程数据转换成真实数据
    
    trueStress = (1 - engStrain) * engStress
    trueStrainRate = engStrainRate / (1 - engStrain)
    trueStrain = -np.log(1 - engStrain)
    
    return trueStress, trueStrainRate, trueStrain

def WritingDataToExcel(dataStoreDir, time, inputWave, reflectWave, transWave, engStress, engStrain, engStrainRate, \
                       trueStress, trueStrain, trueStrainRate, kTrue, kEng):
    w = Workbook()
    ws = w.add_sheet("Result Data")
    
    WritingExcelColumn(ws, "Time/s", 0, time)
    WritingExcelColumn(ws, "Input Wave", 1, inputWave)
    WritingExcelColumn(ws, "Reflect Wave", 2, reflectWave)
    WritingExcelColumn(ws, "Transmission Wave", 3, transWave)
    WritingExcelColumn(ws, "Input Wave + Refelct Wave", 4, inputWave + reflectWave)
    WritingExcelColumn(ws, "Engineering Strain Rate/s^-1", 5, engStrainRate)
    WritingExcelColumn(ws, "Engineering Strain", 6, engStrain)
    WritingExcelColumn(ws, "Engineering Stress/MPa", 7, engStress)
    WritingExcelColumn(ws, "True Strain Rate/s^-1", 8, trueStrainRate)
    WritingExcelColumn(ws, "True Strain", 9, trueStrain)
    WritingExcelColumn(ws, "True Stress/MPa", 10, trueStress)
    
    ws.write(4, 12, "Engineering Strain Rate/s^-1: ")
    ws.write(5, 12, kEng)
    ws.write(6, 12, "True Strain Rate/s^-1: ")
    ws.write(7, 12, kTrue)
    
    filePath = os.path.join(dataStoreDir, 'ResultData.xls')
    w.save(filePath)
    
def WritingExcelColumn(workSheet, columnName, columnNumber, data):
    ws = workSheet
    ws.write(0, columnNumber, columnName)
    for counter, value in enumerate(data, 1):
        ws.write(counter, columnNumber, value)