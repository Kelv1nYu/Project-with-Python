import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import *
from decimal import Decimal
import re
import xlrd

class PrePage(tk.Toplevel):

    def __init__(self):
        super().__init__()
        self.title("导入信息")
        self.geometry('%dx%d' % (300,200))
        self.DataFile_Path = StringVar()
        self.OptFile_Path = StringVar()
        self.createPage()

    def getData(self):
        Datafile_path = filedialog.askopenfilename()
        self.DataFile_Path.set(Datafile_path)

        #print(Datafile_path)

    def getOpt(self):
        Optfile_path = filedialog.askopenfilename()
        self.OptFile_Path.set(Optfile_path)

        #print(Optfile_path)

    def confirm(self):
        DataFilePath = self.DataFile_Path.get()
        OptFilePath = self.OptFile_Path.get()

        if DataFilePath != '' and OptFilePath != '':
            self.dataPath = [DataFilePath, OptFilePath]
            self.destroy()
        else:
            showinfo(title = "错误", message = "请先添加文件")

    def cancel(self):
        self.dataPath = None
        self.destroy()

    def createPage(self):
        self.page = Frame(self)  # 创建Frame
        self.page.pack()
        Label(self.page).grid(row=0, stick=W)
        Button(self.page, text='导入数据: ', command = self.getData).grid(row=1, stick=W, pady=10)
        Entry(self.page, textvariable= self.DataFile_Path).grid(row=1, column=1, stick=E)
        Button(self.page, text='导入操作: ', command = self.getOpt).grid(row=2, stick=W, pady=10)
        Entry(self.page, textvariable=self.OptFile_Path).grid(row=2, column=1, stick=E)
        Button(self.page, text='确认', command=self.confirm).grid(row=3, stick=W, pady=10)
        Button(self.page, text='取消', command=self.cancel).grid(row=3, column=1, stick=E)

class MainPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.geometry('%dx%d' % (600, 320))  # 设置窗口大小
        self.sharesId = StringVar()
        self.noneOptResult = StringVar()
        self.OptSum = StringVar()
        self.OptNumOfShares = StringVar()
        self.createPage()

    def createNewPage(self):
        FilePath = PrePage()
        self.wait_window(FilePath)
        return FilePath.dataPath

    def startCalculate(self):
        SharesId = self.sharesId.get()
        initNumOfShare = Decimal(100000.0)
        if SharesId == '':
            showinfo("错误", "请先输入股票代码")
        elif re.match('^\d{6}$', SharesId) == None:
            showinfo("错误", "请输入6位的股票代码")
        else:
            res = self.createNewPage()
            if res is None :
                return
            DataFileName, OptFileName = res
            dataFile = xlrd.open_workbook(DataFileName)
            data = dataFile.sheet_by_index(0)
            sharesCols = data.col_values(0)
            shareId = list()
            for shares in sharesCols:
                shareId.append(shares[:-3])
            if SharesId not in shareId:
                showinfo("错误", "未能找到匹配的股票")
                return
            #print(sharesCols)
            dataTimeCols = data.col_values(2)
            valueCols = data.col_values(3)
            optFile = xlrd.open_workbook(OptFileName)
            opt = optFile.sheet_by_index(1)
            timeCols = opt.col_values(0)
            optCols = opt.col_values(1)
            lastTime = timeCols[-1]
            sharesIndex = list()
            for index in range(len(sharesCols)):
                #print(type(shares[:-3]))
                if sharesCols[index][:-3] == SharesId :
                    sharesIndex.append(index)

            for index in sharesIndex:
                #print(index)
                if dataTimeCols[index] == lastTime :
                    #print(valueCols[index])
                    #print(type(valueCols[index]))
                    noneOptResult = Decimal(str(valueCols[index])) * initNumOfShare
                    self.noneOptResult.set(float(noneOptResult))

            optSum = Decimal('0.0')
            numOfShare = Decimal('0.0')
            resMoney = Decimal('0.0')

            if optCols[1] == "买入":
                for index in sharesIndex:
                    if dataTimeCols[index] == timeCols[2]:
                        optSum = initNumOfShare * Decimal(str(valueCols[index]))
                for i in range(3, len(optCols)):
                    if optCols[i] == "买入":
                        time = timeCols[i]
                        for index in sharesIndex:
                            if dataTimeCols[index] == time:
                                numOfShare = (Decimal(str(optSum)) // Decimal(str(valueCols[index])) // Decimal('100.0')) * Decimal('100.0')
                                #resMoney = optSum % valueCols[index] + ((optSum // valueCols[index]) % 100.0) * valueCols[index]
                                resMoney = Decimal(str(optSum)) - (Decimal(str(numOfShare)) * Decimal(str(valueCols[index])))
                                #print(resMoney)
                                #print(resMoney2)
                    elif optCols[i] == "卖出":
                        for index in sharesIndex:
                            if dataTimeCols[index] == timeCols[i]:
                                optSum = Decimal(str(numOfShare)) * Decimal(str(valueCols[index])) + Decimal(str(resMoney))
            elif optCols[1] == "卖出":
                for index in sharesIndex:
                    if dataTimeCols[index] == timeCols[1]:
                        optSum = Decimal(str(valueCols[index])) * initNumOfShare
                for i in range(2, len(optCols)):
                    if optCols[i] == "买入":
                        for index in sharesIndex:
                            if dataTimeCols[index] == timeCols[i]:
                                numOfShare = (Decimal(str(optSum)) // Decimal(str(valueCols[index])) // Decimal('100.0')) * Decimal('100.0')
                                resMoney = Decimal(str(optSum)) - (Decimal(str(numOfShare)) * Decimal(str(valueCols[index])))
                    elif optCols[i] == "卖出":
                        for index in sharesIndex:
                            if dataTimeCols[index] == timeCols[i]:
                                optSum = Decimal(str(numOfShare)) * Decimal(str(valueCols[index])) + Decimal(str(resMoney))

            self.OptSum.set(float(optSum))
            self.OptNumOfShares.set(float(numOfShare))

    def clearResult(self):
        self.noneOptResult.set("")
        self.OptSum.set("")
        self.OptNumOfShares.set("")

    def createPage(self):
        self.page = Frame(self)  # 创建Frame
        self.page.pack()
        Label(self.page).grid(row = 0, stick = W)
        Label(self.page, text = "输入股票代码",).grid(row = 1, stick = W, pady = 10)
        Entry(self.page, textvariable = self.sharesId).grid(row = 1, column = 1, stick = E)
        Label(self.page, text = "无操作输出：").grid(row = 2, stick = W, pady = 10)
        Label(self.page, text = "市值").grid(row = 3, stick = W, pady = 10)
        Label(self.page, textvariable = self.noneOptResult, relief = "ridge", width = 20, height = 1).grid(row = 3, column = 1, stick = E)
        Label(self.page, text="有操作输出：").grid(row = 4, stick = W, pady = 10)
        Label(self.page, text="市值").grid(row = 5, stick = W, pady = 10)
        Label(self.page, textvariable = self.OptSum, relief ="ridge", width = 20, height = 1).grid(row = 5, column = 1, stick=E)
        Label(self.page, text="股数").grid(row = 6, stick = W, pady = 10)
        Label(self.page, textvariable = self.OptNumOfShares, relief="ridge", width = 20, height = 1).grid(row = 6, column = 1, stick = E)
        Button(self.page, text='开始计算', command = self.startCalculate).grid(row = 7, stick = W, pady = 10)
        Button(self.page, text='清除结果', command = self.clearResult).grid(row = 7, column = 1, pady=10)
        Button(self.page, text='退出', command = self.page.quit).grid(row = 7, stick = E, column = 2, pady = 10)


if __name__ == '__main__':
  app = MainPage()
  app.mainloop()
