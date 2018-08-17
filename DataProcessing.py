# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 16:40:59 2018
使用需要注意以下几点：
1.输入数据文本格式：从哪一行开始读入；读哪几列的数据；读取的数据有没有需要
  反号的（程序使用透射信号为正，反射信号为负）；
2.基本参数如几何尺寸、弹性参数的更改；
3.应力的计算公式中有面积的比，可能需要更改试样截面积的计算方式；
4.输出截取的反射波和投射波区间，时刻注意截取的效果！特别是两端是否有因为吃波
  造成的长低值平台区，如有需要更改截取区间端点的比例值。若信号变化明显，可尽量
  取小的比例值，反之取大比例值；
5.注意选取进行回归拟合的应变区间的百分比，线性段良好时可降低开始取的比例值；
"""
import os
import os.path
import shutil
import numpy as np

import Functions

K = 1.92
barWaveSpeed = 4850             #m/s
barElasticModulus = 190250       #MPa
barDiameter = 12.7               #mm
specimenLength = 2             #mm
specimenDiameter = 2.51          #mm

areaBar = barDiameter**2 * np.pi / 4
areaSpecimen = specimenDiameter**2

#currDir = os.getcwd()
currDir = os.path.split(__file__)[0]
fileName = input("Data file name is: ")
fileAbsoluteDir = os.path.join(currDir, fileName + ".txt")
dataStoreDir = os.path.join(currDir, fileName)

if not os.path.exists(dataStoreDir):
  os.mkdir(dataStoreDir)

shutil.copyfile(fileAbsoluteDir, os.path.join(dataStoreDir, fileName + ".txt"))

time, inputBarChannel, transBarChannel = Functions.ExtractDataFromFile(dataStoreDir, fileAbsoluteDir)

flag = input("Needing to reverse input bar wave?(Y/N)")
if flag == "Y":
    inputBarChannel = [-temp for temp in inputBarChannel]
    Functions.DrawChannelSignalsPlot(dataStoreDir, "Original Experimental Data.png", time, inputBarChannel, transBarChannel)

inputChannel, transChannel = Functions.MovingChannelSignals(dataStoreDir, time, inputBarChannel, transBarChannel)

timeModified, reflectWave, transWave = Functions.FindingSections(dataStoreDir, time, inputChannel, transChannel)

engStress, engStrain, engStrainRate = Functions.Calculations(timeModified, 
                reflectWave, transWave, K, barWaveSpeed, barElasticModulus, 
                areaBar, specimenLength, areaSpecimen)

trueStress, trueStrainRate, trueStrain = \
    Functions.EngineeringToTrue(engStress, engStrain, engStrainRate)

Functions.DrawStressStrainPlot(dataStoreDir, engStress, engStrain)

kEng, b = Functions.FittingStrainRate(dataStoreDir, timeModified, engStrain, False)
kTrue, b = Functions.FittingStrainRate(dataStoreDir, timeModified, trueStrain, True)

print("Strain rate is: ", kTrue)

Functions.WritingDataToExcel(dataStoreDir, timeModified, engStress, engStrain, engStrainRate, trueStress, \
                             trueStrain, trueStrainRate, kTrue, kEng)
