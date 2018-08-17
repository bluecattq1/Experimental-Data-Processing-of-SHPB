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
        transBarChannel.append(-float(data[2]))
      
    outputf.close()
    
    DrawChannelSignalsPlot(dataStoreDir, "Original Experimental Data.png", 
                           time, inputBarChannel, transBarChannel)
    
    return time, inputBarChannel, transBarChannel

def DrawChannelSignalsPlot(dataStoreDir, plotName, time, inputBarChannel, transBarChannel):
    #绘制信号图
    plt.close('all')
    
    fig = plt.figure(figsize = (8, 4))
    ax = fig.add_subplot(111)
    
    ax.plot(time, inputBarChannel, label = "InputBar", color = "red", linewidth = 2)
    ax.plot(time, transBarChannel, label = "TransmissionBar", color = "b", linewidth = 2)
    
    ch = SelectCurve(ax)
    
    plt.xlabel("Time/$s$")
    plt.ylabel("Voltage/$v$")
    plt.legend()
    plt.title(plotName.split(".")[0])
    
    filePath = os.path.join(dataStoreDir, plotName)
    plt.savefig(filePath, dpi = 240)
    
    plt.show()
    
def MovingChannelSignals(dataStoreDir, time, inputBarChannel, transBarChannel): 
    #上下平移入射波和投射波——归零
    recordInput = inputBarChannel[0]
    recordTrans = transBarChannel[0]
    
    inputChannel = [tempInput - recordInput for tempInput in inputBarChannel]
    transChannel = [tempTrans - recordTrans for tempTrans in transBarChannel]
    
    DrawChannelSignalsPlot(dataStoreDir, "Moving Singals Plot.png", 
                           time, inputChannel, transChannel)
    
    return inputChannel, transChannel

def FindEndPoints(saddlePoint, saddlePointPos, data):
    #寻找信号波的区间端点
    for counter, value in enumerate(data[saddlePointPos: 0: -1]):
        if abs(value / saddlePoint) <= 0.005:
            startPoint = saddlePointPos - counter
            break
        
    for counter, value in enumerate(data[saddlePointPos: len(data)]):
        if abs(value / saddlePoint) <= 0.2:
            endPoint = saddlePointPos + counter
            break
        
    return startPoint, endPoint

def FindingSections(dataStoreDir, time, inputChannel, transChannel):
    #寻找入射波和投射波
    saddleReflect = min(inputChannel)
    saddleReflectPos = inputChannel.index(saddleReflect)
    
    saddleTrans = max(transChannel)
    saddleTransPos = transChannel.index(saddleTrans)
    
    startReflect, endReflect = FindEndPoints(saddleReflect, 
                                             saddleReflectPos, inputChannel)
    startTrans, endTrans = FindEndPoints(saddleTrans, 
                                         saddleTransPos, transChannel)
    
    reflectLength = endReflect - startReflect
    transLength = endTrans - startTrans
    timeLength = reflectLength if reflectLength <= transLength else transLength
    print(timeLength)
    
    reflectWave = inputChannel[startReflect: startReflect + timeLength]
    transWave = transChannel[startTrans: startTrans + timeLength]
    timeSpace = time[1] - time[0]
    timeModified = np.arange(0, timeLength * timeSpace, timeSpace)
    
    DrawChannelSignalsPlot(dataStoreDir, "Reflect Wave and Transmission Wave.png", 
                           timeModified, reflectWave, transWave)
    
    return timeModified, reflectWave, transWave

def Calculations(time, reflectWave, transWave, K, barWaveSpeed, 
                 barElasticModulus, areaBar, specimenLength, 
                 areaSpecimen):
    #计算应力、应变、应变率
    reflectStrain = [-(2100 / (K * 1000)) * (temp - reflectWave[0]) 
    / (30 - temp + reflectWave[0]) for temp in reflectWave]
    transStrain = [(2100 / (K * 1000)) * ((temp - transWave[0]) 
    / (30 - temp + transWave[0])) for temp in transWave]
    
    engStrainRate = [2 * barWaveSpeed * 1000 * temp / specimenLength 
                  for temp in reflectStrain]
    engStress = [barElasticModulus * (areaBar / areaSpecimen) * temp for temp in transStrain]
    
    engStrain = [0 for i in time]
    timeSpace = time[1] - time[0]
    for i in np.arange(1, len(time), 1):
        engStrain[i] = engStrain[i - 1] + \
        (engStrainRate[i] + engStrainRate[i - 1]) * timeSpace / 2
        
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
        
        fig, ax = plt.figure(figsize = (8, 4))
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
    stressReverse = [temp for temp in stress]
    stressReverse.reverse()
    for counter, temp in enumerate(stressReverse, 1):
        if temp >= 0.5 * max(stress):
            markEnd = len(stress) - counter
            break
    
    plt.close('all')
    
    plt.figure(figsize = (8, 4))
    plt.plot(strain[1: markEnd], stress[1: markEnd], color = "red", 
             linewidth = 2)
    plt.xlabel("Engineering Strain$\\varepsilon$")
    plt.ylabel("Engineering Stress$\\sigma/MPa$")
    plt.title("$\\sigma$-$\\varepsilon$ curve")
    
    filePath = os.path.join(dataStoreDir, "Stress-Strain Curve.png")
    plt.savefig(filePath, dpi = 240)

    plt.show()
    
def EngineeringToTrue(engStress, engStrain, engStrainRate):
    #工程数据转换成真实数据
    
    tempList = np.arange(0, len(engStress), 1)
    
    trueStress = [(1 - engStrain[i]) * engStress[i] for 
                  i in tempList]
    trueStrainRate = [engStrainRate[i] / (1 - engStrain[i]) for 
                      i in tempList]
    trueStrain = [-np.log(1 - temp) for temp in engStrain]
    
    return trueStress, trueStrainRate, trueStrain

def WritingDataToExcel(dataStoreDir, time, engStress, engStrain, engStrainRate, \
                       trueStress, trueStrain, trueStrainRate, kTrue, kEng):
    w = Workbook()
    ws = w.add_sheet("Result Data")
    
    WritingExcelColumn(ws, "Time/s", 0, time)
    WritingExcelColumn(ws, "Egineering Strain Rate/s^-1", 1, engStrainRate)
    WritingExcelColumn(ws, "Egineering Strain", 2, engStrain)
    WritingExcelColumn(ws, "Egineering Stress/MPa", 3, engStress)
    WritingExcelColumn(ws, "True Strain Rate/s^-1", 4, trueStrainRate)
    WritingExcelColumn(ws, "True Strain", 5, trueStrain)
    WritingExcelColumn(ws, "True Stress/MPa", 6, trueStress)
    
    ws.write(4, 8, "Engineering Strain Rate: ")
    ws.write(5, 8, kEng)
    ws.write(6, 8, "True Strain Rate: ")
    ws.write(7, 8, kTrue)
    
    filePath = os.path.join(dataStoreDir, 'ResultData.xls')
    w.save(filePath)
    
def WritingExcelColumn(workSheet, columnName, columnNumber, data):
    ws = workSheet
    ws.write(0, columnNumber, columnName)
    for counter, value in enumerate(data, 1):
        ws.write(counter, columnNumber, value)
