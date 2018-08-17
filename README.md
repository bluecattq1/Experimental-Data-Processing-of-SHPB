# Experimental-Data-Processing-of-SHPB
Experimental data of ordinary material with obvious strain rate effect from SHPB test can be processed well by this program.

The outputs of program includes relative curves and EXCEL file containg stress, strain and strain data.

During the use of this program, following points need to be concerned:
* Format of input data file. Usually the first several lines in a data file are useless, these lines are not supposed to be read;
* This program regards reflect wave to be negative and transmission wave to be positive by default. You may need to change its signals;
* Basic geometrical data and material constants need to be modified manually;
* The intervals of reflect wave and transmission wave are supposed to be selected carefully (and the interactive wave plots may help you to choose a better interval maually), also similar situation for the selection of interval of strain which
are used to calculate strain rate;

---------------------------------

# 霍普金森压杆实验数据处理程序
具有明显应变率效应的普通材料的霍普金森压杆实验数据可用本程序快速处理。

程序输出在一个新建的同原始数据.txt文件名称的文件夹中，其中包含相关图像和一个有处理得到的应变、应变率和应力数据的EXCEL文件。

运行程序时注意以下几点：
* 原始数据文件的格式。为.txt文件，文件开头无用信息的行数，并在程序中做相应修改；
* 可能需要对入射杆信号反号，根据第一个输出图像确定，程序会有相应提示；
* 基本几何参数和杆的材料常数需要在程序中做相应修改；
* 若结果不合适，利用交互式波形图可手动选出一个合适的信号区间段并相应修改程序重新计算；同样进行应变率拟合时可能也有类似的问题。
