class SelectCurve(object):
    def __init__(self, ax):
        self.ax = ax
        self.text = self.ax.text(0.05, 0.05, "", ha = "left", va = "bottom", 
                                transform = ax.transAxes)
        
        ax.figure.canvas.mpl_connect('motion_notify_event', self.on_move)
        
    def WriteCoordinates(self, target, event):
        if target is not None:
            time = target.get_xdata(orig = True)
            xdata = float(event.xdata)
            ydata = float(event.ydata)
            n = int((xdata - time[0]) / (time[1] - time[0]))
            info = "Time: {:.7f}\nVoltage: {:.10f}\nNumber of index:{}".format(xdata, ydata, n)
        else:
            info = ""    

        self.text.set_text(info)
        self.ax.figure.canvas.draw_idle()
    
    def on_move(self, event):
        ax = self.ax
        #以下写法将在鼠标离开曲线后清空数据点信息文本框

        target = None
        for line in ax.lines:
            if line.contains(event)[0]:
                target = line
                break
        
        self.WriteCoordinates(target, event)


        #以下写法将在鼠标离开曲线后保持显示离开之前的数据点的信息
        """
        for line in ax.lines:
            if line.contains(event)[0]:
                self.WriteCoordinates(line, event)
                break
        """
