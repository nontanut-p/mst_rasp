#!/usr/bin/env python
# -*- coding: utf-8 -*-

from termios import PARMRK
import tkinter as tk
from tkinter import Message, ttk
from tkinter.constants import TRUE
import serial
import serial.tools.list_ports
import sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import keyboard
import time
import datetime
import csv
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


gauth = GoogleAuth()
gauth.LoadClientConfigFile('client_secrets.json')
drive = GoogleDrive(gauth)


class ParentClass:
    time_start = ''
    macd_thredshold = 1.25
    short_MV = 50
    fileName = 'test'
    portName = '/dev/ttyUSB0'
    connection_status = False
    baudrate = 9600
    baudrates = [9600,
                 14400, 19200, 38400, 57600, 115200, 128000, 256000]
  #  smovingAverage_List = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
  #  lmovingAverage_List = [50, 70, 90, 110, 130, 150, 170, 200, 230, 250, 300]
  #  thresholds = [1.0, 1.10, 1.15, 1.20, 1.25, 1.30, 1.35,
  #                1.40, 1.45, 1.50, 1.60, 1.70, 1.80, 1.90, 2.0]
  #  st_dt = [0,50, 100, 150, 200, 250, 300]
    short_ma = 50
    long_ma = 150
    threshold = 1.25
    start_dt = 200
    dt_interval = 50
    string_data = ''
    frontData = []
    backData = []
    shortback = []
    longback = []
    shortfront = []
    longfront = []
    mstfront = []
    mstback = []
    interval_temp = 0
    detectStatus = 1  
    start = False
    plot = False
    mst = 0

    def __init__(self, root, title):
        self.root = root
        self.root.title(title)
        self.root.geometry("890x580")
        self.root.configure(bg='light steel blue')
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor('lightsteelblue')
        self.ax.set_title('LATEX Mechanical Stability Time Detection')
        self.ax.set_xlabel('TIME (s)')
        self.ax.set_ylabel('Distance (mm)')
        #self.ax.set_facecolor('blue')
        #self.ax.set_ylim(0, 60)
        #self.lines = self.ax.plot([], [])[0]
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().place(x=1, y=20, width=750, height=500)
        self.canvas.draw()
    def readSetting(self):
        print('something')
        
    def start_stop(self,connect,start):
        if self.connection_status == False:
            tk.messagebox.showinfo(
                title='START/STOP ', message="Please try to Connect with device again")
        if connect == True and start == False: 
            self.start = True
            self.l10 = tk.Label(self.root, bg='lime', width=50,
                                    text='CONNECTED : WATING FOR START COMMAND').place(x=150, y=525)
            self.plotting()
        elif connect == True and start == True : 
             self.l10 = tk.Label(self.root, bg='lime', width=50,
                                    text='Plotting').place(x=150, y=525)
            

    def on_select(self, event=None):
        # get selection from event
        self.select_portName = event.widget.get()
        st = self.select_portName.find('/')
        ed = self.select_portName.find(' ')
        print("selection port",self.select_portName[st:ed])
        self.portName = self.select_portName[st:ed]
        print("change port to: ", self.portName)

    def select(self, event=None, *name):
        # get selection from event
        name = event.widget.get()
        
    def end_process_clear_save(self):
        now = datetime.datetime.now()
        print('end_process_clear_save :',self.fileName, ':fileName')
        
        name = self.fileName
        figure_png = name
        
        print('fileName:', figure_png , 'Name:', name, 'type:', type(figure_png))
        
        print('figure_png:',figure_png, ':figure_png')
        
        name = ''
        for i in range(len(figure_png)):
            print(i, ":", figure_png[i], ", ", ord(figure_png[i]))
            if ord(figure_png[i]) != 0:
                name = name + figure_png[i]
        print('name:', name, ', len:', len(name))
        self.fig.savefig(name, format='png')
        csv_name = 'test2' + '.csv'
        e = open(csv_name, "a")
        writer =csv.writer(e)
        writer.writerow(['RAW', 'Filter Short' , 'Filter Long'])
        
        for i in range(len(self.frontData)):
            #print(self.frontData[i])
            writer.writerow([str(self.frontData[i]),str(self.shortfront[i]) , str(self.longfront[i])])
            #.write(',')
        e.close()  
      


        self.clearplot()

    def connect(self):
        self.time_start = datetime.datetime.now()
        print('self portName', self.portName, self.baudrate)
        self.ser = serial.Serial(self.portName, self.baudrate)
        self.connection_status = True
        time.sleep(1)
        self.ser.flush()
        self.ser.flush()
        self.ser.reset_input_buffer()
        message_tx = 'Connected to ' + \
            str(self.portName) + ' with baudrate ' + str(self.baudrate)
        tk.messagebox.showinfo(title='Connection ',
                               message=message_tx)
        print('Connected to ', self.portName,
              ' with baudrate ', self.baudrate)
        if self.ser.isOpen() == True :
            self.start_stop(True, False)
        else : self.start_stop(False, False)

    def plotting(self):
        #print('reading')
        if self.start == True:
    
            if self.ser.in_waiting > 0:
                self.tmp = self.ser.readline().decode("Ascii")
                
                print(self.tmp , 'reading data')
                if "START" in self.tmp:
                    print("test",self.tmp)
                    # FIND : FILENAME AFTER THE START WAS FOUND
                    self.fileName = str(self.tmp[6:-2])
                    st = 'fileName:' + str(self.fileName) +': found start'
                    print(st)
                    self.start_stop(True, True)
                    self.plot = True
                elif "STOP" in self.tmp :
                    #self.clearplot()
                    print('STOP:',self.fileName, ':after found stop')
                    self.plot = False
                    self.end_process_clear_save() # New -> Change to wating for Start Command
                    self.start_stop(True , False)
                #self.string_data = self.string_data + self.tmp
		        #print('try to ploting')
                # print(dataSplit[1])
                #self.clearplot()
                if self.plot == True :

                    try:
                        data_input = float(self.tmp)
                        #string_data = self.tmp.split()
                        #print(float(string_data[1]))
                        self.frontData.append(data_input)  # Data ชุดหน้า
                        print(data_input)   #self.backData.append(
                        #    float(string_data[1]))  # Data ชุดหลัง
                        # self.lines.set_ydata(self.frontData)
                        # self.lines.set_xdata(self.frontData)
                        if len(self.frontData) <= self.short_ma :
                            self.shortfront.append(sum(self.frontData)/len(self.frontData))
                            self.longfront.append(sum(self.frontData)/len(self.frontData))
                            print('appending' , sum(self.frontData)/len(self.frontData))
                        if len(self.frontData) > self.short_ma and len(self.frontData) < self.long_ma :
                            self.shortfront.append(sum(self.frontData[-self.short_ma:])/self.short_ma)
                            self.longfront.append(sum(self.frontData)/len(self.frontData))
                        if len(self.frontData) >= self.long_ma :
                            self.shortfront.append(sum(self.frontData[-self.short_ma:])/self.short_ma)
                            self.longfront.append(sum(self.frontData[-self.long_ma:])/self.long_ma)
                            ## Detection interval ##
                            try:
                                macd_temp = self.shortfront[-1:][0] - self.longfront[-1:][0]
                                print("MACD",macd_temp)
                            except:
                                print('can not calculated ') 
                        if len(self.frontData) >= 1000:
                            self.threshold = 1.0 
                        if len(self.frontData) > self.start_dt and macd_temp > self.threshold and self.detectStatus == 1:
                            self.mstfront.append(len(self.frontData))
                            print('MST DETECTED AT : ', len(self.longfront))
                            self.interval_temp = 0
                            self.detectStatus = 0
                        if self.interval_temp < self.dt_interval and self.detectStatus == 0:
                            self.interval_temp = self.interval_temp + 1    
                            print('interval temp ++ ', self.interval_temp) 
                        if self.interval_temp == self.dt_interval :
                            self.detectStatus = 1
                        if len(self.mstfront) > 0 :
                            for i in range(len(self.mstfront)) :
                                self.ax.axvline(x = self.mstfront[i], color = 'b', label = 'axvline - full height')
                                self.ax.text(self.mstfront[i]-20, 5, str(self.mstfront[i]), style ='italic',
        fontsize = 11, color ="green")
                        if len(self.frontData) % 10 == 0 :
                            self.ax.clear()
                            self.ax.set_title('LATEX Mechanical Stability Time Detection')
                            self.ax.set_xlabel('TIME (s)')
                            self.ax.set_ylabel('Distance (mm)')
                        '''
                        if data lenght < short  --> add moving average but its number of data
                        if data lenght > short but < long --> add short moving average  
                        if data lenbght > short and > long --> add short, long moving average and start detection
                        '''
                        #PLOTING
                        #plt.xticks(np.arange(0, 51, 5))
                        self.ax.plot(self.frontData, color='yellow')
                        self.ax.plot(self.shortfront, color='red')
                        self.ax.plot(self.longfront, color='green')
                        #self.ax.set_xlim(0, (len(self.frontData)+50))
                        print('must print out')
                        self.canvas.draw()
                        
        

                    except:
                        pass

        self.root.after(1, self.plotting)

    def on_select_bb(self, event=None):
        self.baudrate = event.widget.get()
        print(event.widget.get())
        print("Baudrate has changed : ", self.baudrate)

    def serial_ports(self):
        return serial.tools.list_ports.comports()

    def agreement_changed(self):
        tk.messagebox.showinfo(title='Result',
                               message=self.agreement.get())

    def clearplot(self):
        self.ax.clear()
        self.frontData.clear()
        self.backData.clear()
        self.shortfront.clear()
        self.longfront.clear()
        self.mstfront.clear()
        self.ax.clear()
        self.ax.set_title('LATEX Mechanical Stability Time Detection')
        self.ax.set_xlabel('TIME (s)')
        self.ax.set_ylabel('Distance (mm)')
        self.canvas.draw()
        print('plot cleared')

    def create_program(self):
        self.var1 = tk.IntVar()
        self.agreement = tk.StringVar()
        #self.root = root
        self.l10 = tk.Label(self.root, bg='white', width=20,
                            text='STATUS :').place(x=0, y=525)
        self.cb = ttk.Combobox(self.root, values=self.serial_ports())
        self.cb_br = ttk.Combobox(self.root, values=self.baudrates)
        self.cb.grid(row=1, column=1, ipadx="100")
        self.cb_br.grid(row=1, column=2, ipadx="50")
        self.cb.bind('<<ComboboxSelected>>', self.on_select)
        self.cb_br.bind('<<ComboboxSelected>>', self.on_select_bb)
        self.reload = tk.Button(self.root, text='Reload', command=lambda:  self.reload_port()).grid(
            row=1, column=3, ipadx="10")
        self.Connect = tk.Button(self.root, text='Connect', command=lambda:  self.connect()).grid(
            row=1, column=4, ipadx="10")


    def reload_port(self):
        self.cb = ttk.Combobox(self.root, values=self.serial_ports())
        self.cb.grid(row=1, column=1, ipadx="100")


def main():
    root = tk.Tk()
    program = ParentClass(root, 'MST')
    #program.create_program(root)
    program.create_program()
    root.mainloop()



if __name__ == '__main__':
    main()
