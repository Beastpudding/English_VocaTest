import pandas as pd
import os

class MyDatabase:
    def __init__(self, fileName=''):
        dataName = fileName
        filesList = os.listdir()
        try:  # If fileName is correct, jump to ‘finally’
            if dataName not in filesList:  # If not, jump to ‘except’
                raise FileNotFoundError
        except FileNotFoundError:
            print("Can not locate data file. Select File.")
            dbList = []
            for file in filesList:  # Search excel files in the directory
                if '.xlsx' in file:
                    dbList.append(file)
            for db in dbList:  # Present excel files to user with index
                idxDB = dbList.index(db)
                print("{}. {}".format(idxDB, db))
            userSelection = int(input("Database File:"))
            dataName = dbList[userSelection]  # Define dataName with user choice
        finally:
            dataFile = pd.ExcelFile(dataName)  # Define dataFile with dataName
            self.dataFrame = self.createDataFrameForFile(dataFile)

    def createDataFrameForFile(self, dataFile):
        sheetNames = dataFile.sheet_names
        if len(sheetNames) == 1:
            return dataFile.parse(sheetNames[0])
        else:
            print("Please Select Data Table.")
        for sheet in sheetNames:
            idxSheet = sheetNames.index(sheet)
        print("{}. {}".format(idxSheet, sheet))

        userSelection = int(input("Database Table:"))
        return dataFile.parse(sheetNames[userSelection])

    def getDataList(self):
        wList = []
        for index, row in self.dataFrame.iterrows():
            tempList = []
            for index in range(0, 5):
                tempList.append(row[index])
            cleanedList = [x for x in tempList if str(x) != 'nan']
            wList.append(cleanedList)
        return wList

    def getDataDictionary(self):
        headers = list(self.dataFrame.keys())

        aDict = {}
        for index, row in self.dataFrame.iterrows():
            bDict = {}
            mainKey = row[headers[0]]
            aDict[mainKey] = bDict

            for column in headers:
                bDict[column] = row[column]
                #빈칸 없애기
        return aDict
