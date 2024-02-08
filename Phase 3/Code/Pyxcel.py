import re
from copy import deepcopy

TablesDictionary = dict()

def string_to_number(s):
    ans = 0
    pow = 0
    for i in s[::-1]:
        ans += (ord(i)-64)*(26**pow)
        pow += 1
    return ans-1

def number_to_string(n):
    lstAns = list()
    ans = str()
    n += 1
    while n > 0:
        lstAns.append((n-1)%26)
        n = (n-1) // 26
    for i in lstAns[::-1]:
        ans += chr(i+65)
    return ans

def evalStrVersion2(s):
    mul_div_pattern = r'(\d+)([*/])(\d+)'
    patternList = [r'(\d+)\s*([+\-])\s*(\"[A-Z]+\")\s*',
                r'(\"[A-Z]+\")\s*([+\-])\s*(\d+)\s*',
                r'(\d+)\s*([+\-])\s*(\d+)\s*',
                r'(\".*\")\s*([+\-])\s*(\".*\")\s*']
                # index 0 for ns
                # index 1 for sn
                # index 2 for nn
                # index 3 for ss

    def purgeMulDiv(s, mul_div_pattern):
        def recursiveFunc(exp, mul_div_pattern):
            matches = list(re.compile(mul_div_pattern).finditer(exp))
            if matches[0].group(2) == "*":
                exp = int(matches[0].group(1))*int(matches[0].group(3))
            elif matches[0].group(2) == "/":
                exp = int(matches[0].group(1))//int(matches[0].group(3))
            return str(int(exp))

        if "*" in s or "/" in s:
            mul_div_matches = list(re.compile(mul_div_pattern).finditer(s))
            exp = recursiveFunc(mul_div_matches[0].group(0), mul_div_pattern)
            s = re.sub(mul_div_pattern, exp, s, 1)
            return purgeMulDiv(s, mul_div_pattern)
        else:
            return s

    def getExp(s):
        def simplize(s, patternList, exp):
            msg = "unsupported operand"
            ns = re.compile(patternList[0])
            sn = re.compile(patternList[1])
            nn = re.compile(patternList[2])
            ss = re.compile(patternList[3])

            if re.search(ss, exp):
                grouplist = list(ss.finditer(exp))
                s1 = grouplist[0].group(1)
                s2 = grouplist[0].group(3)
                if grouplist[0].group(2) == "+":
                    s = s.replace(exp, '\"' + str(s1[1:len(s1)-1] + s2[1:len(s2)-1]) + '\"', 1)
                    return s
                else: return msg

            if re.search(nn, exp):
                grouplist = list(nn.finditer(exp))
                num1 = int(grouplist[0].group(1))
                num2 = int(grouplist[0].group(3))
                if grouplist[0].group(2) == "+":
                    s = re.sub(nn, str(num1+num2), s, 1)
                    return s
                else:
                    s = re.sub(nn, str(num1-num2), s, 1)
                    return s

            if re.search(sn, exp):
                grouplist = list(sn.finditer(exp))
                col = grouplist[0].group(1)
                num = int(grouplist[0].group(3))
                col = int(string_to_number(col[1:len(col)-1]))
                if grouplist[0].group(2) == "+":
                    s = re.sub(sn, str('\"' + number_to_string(num+col)) + '\"', s, 1)
                    return s
                else: 
                    s = re.sub(sn,'\"' + str(number_to_string(col-num)) + '\"', s, 1)
                    return s

            if re.search(ns, exp):
                grouplist = list(ns.finditer(exp))
                col = grouplist[0].group(3)
                num = int(grouplist[0].group(1))
                col = string_to_number(col[1:len(col)-1])
                if grouplist[0].group(2) == "+":
                    s = re.sub(ns, str(col+num), s, 1)
                    return s
                else:
                    s = re.sub(ns, str(num-col), s, 1)
                    return s

            if re.search(r'(\"?[^\"\-+*/]+\"?)', s) and ("+" or "-" or "*" or "/") not in s:
                return s

            else:
                return msg
        pat = re.compile(r"(\s*\"?[^\"\-+*/]*\"?\s*[+\-]\s*\"?[^\"\-+*/]*\"?\s*)")
        if re.search(pat, s) == None:
            return s
        else:
            matchList = list(pat.finditer(s))
            exp = matchList[0].group(1)
            s = simplize(s, patternList, exp)
            return getExp(s)

    s = purgeMulDiv(s, mul_div_pattern)
    s = getExp(s)
    return s

def evalStrVersion3(s, table=[], variablesDictionary={}, f1=True, f2=True, f3=True, f4=True, f5=True, f6=True):

    def replaceVariables(s, variablesDictionary={}):
        splitPattern = re.compile(r'[+\-/*<>\]\[]|and|or|={2}')
        splitedBy = list(re.findall(splitPattern, s))
        splited = list(re.split(splitPattern, s))

        s = ""
        for i in range(len(splited)):
            if splited[i].strip() in variablesDictionary.keys():
                splited[i] = variablesDictionary[splited[i].strip()]
        for i in range(len(splited)):
            if i >= len(splitedBy):
                s = s + splited[i].strip()
            else:
                s = s + splited[i].strip() + splitedBy[i].strip()
        return s

    def simplizeInsideTheBrackets(s):
        patternForInsideTheBrackets = re.compile(r'\s*\[([^\[\]]+)\]\s*')
        bracketMatches = list(patternForInsideTheBrackets.finditer(s))
        for i in bracketMatches:
            exp = evalStrVersion2(i.group(1))
            if exp == "unsupported operand":
                print(exp)
                quit()
            s = s.replace(i.group(1), exp, 1)
        return s

    def replaceWithTable(s, table=[]):
        pattern = re.compile(r'\s*([A-Z]+)(\d+)\s*')
        matches = list(pattern.finditer(s))
        for i in matches:
            col = int(string_to_number(i.group(1)))
            row = int(i.group(2))-1
            s = s.replace(i[0], table[row+1][col+1], 1)
        return s

    def purgeBrackets(s, table=[]):
        patternToPurgebrackets = re.compile(r'\[\"([A-Z]+)\"\]\[(\d+)\]')
        if re.search(patternToPurgebrackets, s):
            matches = list(patternToPurgebrackets.finditer(s))
            col = int(string_to_number(matches[0].group(1)))
            row = int(matches[0].group(2))-1
            s = re.sub(patternToPurgebrackets, table[row+1][col+1], s, 1)
            return purgeBrackets(s, table)
        return s

    if f1: s = replaceVariables(s, variablesDictionary) #1

    if f2: s = simplizeInsideTheBrackets(s)             #2

    if f3: s = replaceWithTable(s, table)               #3

    if f4: s = purgeBrackets(s, table)                  #4

    if f5: s = replaceWithTable(s, table)               #5
    
    #if f6 and "None" not in s: s = evalStrVersion2(s)   #6

    return s

def printError():
    print("Error")
    quit()

def evalBoolean(s, table=[], variablesDictionary={}):
    s = evalStrVersion3(s, table, variablesDictionary)

    ERR1 = re.compile(r'\s*\"\s*[0-9a-zA-Z]+\s*\"\s*(<|>|={2})\s*\d+\s*')
    ERR2 = re.compile(r'\s*\d+\s*(<|>|={2})\s*\"[0-9a-zA-Z]+\s*\"\s*')

    if re.search(ERR1, s): printError()
    if re.search(ERR2, s): printError()


    def evalNN(s):
        nn = re.compile(r'\s*(\d+)\s*(>|<|={2})\s*(\d+)\s*')
        NvsNlist = list(nn.finditer(s))

        if re.search(nn, s):
            x, y = int(NvsNlist[0].group(1)), int(NvsNlist[0].group(3))

            if NvsNlist[0].group(2) == '>':
                if x > y: s = re.sub(nn, ' true ', s, 1)
                else: s = re.sub(nn, ' false ', s, 1)
                
            elif NvsNlist[0].group(2) == '<':
                if x < y: s = re.sub(nn, ' true ', s, 1)
                else: s = re.sub(nn, ' false ', s, 1)

            elif NvsNlist[0].group(2) == '==':
                if x == y: s = re.sub(nn, ' true ', s, 1)
                else: s = re.sub(nn, ' false ', s, 1)   

            return evalNN(s)
        return s
    def evalSS(s):
        ss = re.compile(r'(?!and|or)\"\s*(\w+)\s*\"\s*(>|<|={2})\s*\"\s*(\w+)\s*\"')
        SvsSlist = list(ss.finditer(s))

        if re.search(ss, s):

            if SvsSlist[0].group(2) == '>':
                if SvsSlist[0].group(1) > SvsSlist[0].group(3):
                    s = re.sub(ss, ' true ', s, 1)
                else:
                    s = re.sub(ss, ' false ', s, 1)

            elif SvsSlist[0].group(2) == '<':
                if SvsSlist[0].group(1) < SvsSlist[0].group(3):
                    s = re.sub(ss, ' true ', s, 1)
                else:
                    s = re.sub(ss, ' false ', s, 1)
            
            elif SvsSlist[0].group(2) == '==':
                if SvsSlist[0].group(1) == SvsSlist[0].group(3):
                    s = re.sub(ss, ' true ', s, 1)
                else:
                    s = re.sub(ss, ' false ', s, 1)
            
            return evalSS(s)
        return s

    def evalBooleanExp(x, y, z):
        if x == "true" or x == "True": x = True
        elif x == "false" or x == "False": x = False

        if z == "true" or z == "True": z = True
        elif z == "false" or z == "False": z = False

        if y == "and": return x and z
        elif y == "or": return x or z

    def evalBooleansList(splitedList):
        if len(splitedList) == 1:
            return splitedList[0]
        elif len(splitedList) == 2 or len(splitedList) == 0:
            printError()
        else:
            x = splitedList[0]
            y = splitedList[1]
            z = splitedList[2]
            splitedList.pop(0)
            splitedList.pop(0)
            splitedList.pop(0)
            splitedList.insert(0, evalBooleanExp(x, y, z))
            return evalBooleansList(splitedList)

    s = evalNN(s)
    s = evalSS(s)

    splitedList = list(s.strip().split())
    ans = evalBooleansList(splitedList)
    if ans == 'false' or ans == False:
        return False
    else:
        return True

class Table(list):
    Table = []

    def __init__(self, name, column, row):
        self.name = name
        self.Table = [["None" for _ in range(column)] for _ in range(row)]
        tmp = []
        for i in range(len(self.Table[0])):
            tmp.append(number_to_string(i))
        self.Table.insert(0, tmp)
        for i in range(len(self.Table)):
            self.Table[i].insert(0, str(i))


    def setFunc(self, column, row, relation):
        column = int(string_to_number(column))
        row = int(row)-1
        self.Table[row+1][column+1] = relation
    

    def changeValue(self, column, row, value):
        column = int(string_to_number(column))
        row = int(row)-1

        if row+1 >= len(self.Table) or column+1 >= len(self.Table[0]): printError()

        self.Table[row+1][column+1] = value


    def display(self, variablesDictionary):

        def printer(tblCopy):
            lens = [max(map(len, col)) for col in zip(*tblCopy)]
            fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
            tbl = [fmt.format(*row) for row in tblCopy]
            print('\n'.join(tbl))

        tblCopy = deepcopy(self.Table)
        for i in range(1, len(tblCopy)):
            for j in range(1, len(tblCopy[i])):
                s = str(tblCopy[i][j])
                tblCopy[i][j] = evalStrVersion3(s, tblCopy, variablesDictionary)

        for i in range(1, len(tblCopy)):
            for j in range(1, len(tblCopy[i])):
                if "None" in tblCopy[i][j]: tblCopy[i][j] = "None"
                tblCopy[i][j] = str(tblCopy[i][j])
        printer(tblCopy)


patternsList = [re.compile(r'\s*(create)\s*\(\s*([a-zA-Z0-9]+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)(\s*\$.+)?'),
                re.compile(r'\s*(context)\s*\(\s*([a-zA-Z0-9]+)\s*\)(\s*\$.+)?'),
                re.compile(r'\s*(display)\s*\(\s*([a-zA-Z0-9]+)\s*\)(\s*\$.+)?'),
                re.compile(r'\s*(setFunc)\s*\(\s*([A-Z]+)(\d+)\s*,\s*([A-Z0-9+\-*/\s]+)\s*(\s*\$.+)?'),
                re.compile(r'\s*(print)\s*\(([a-zA-Z0-9+\-*/\s\"\s:\[\]]+)\)\s*(\s*\$.+)?'),
                re.compile(r'\s*([A-Z]+)(\d+)\s*=\s*([A-Za-z0-9+\-*/\"\s]+)\s*(\s*\$.+)?'),
                re.compile(r'\s*([a-z][a-zA-Z0-9]*)\s*=\s*([A-Za-z0-9+\-*/\"\s\[\]]+)\s*(\s*\$.+)?'),
                re.compile(r'\s*\[([a-zA-Z0-9+\-/*\s\"]+)\]\s*\[([a-zA-Z0-9+\-/*\s\"]+)\]\s*=\s*([a-zA-Z0-9+\-/*\s\"\[\]]+)(\s*\$.+)?'),
                re.compile(r'\s*(setFunc)\s*\(\s*([a-zA-Z0-9\"\[\]+\-*/\s]+)\s*,\s*([a-zA-Z0-9\"\[\]+\-*/\s]+)\s*\)(\s*\$.+)?'),
                re.compile(r'(\s*\$.+)'),
                re.compile(r'\s*(if)\s*\(([^\(\)]+)\)\s*\{\s*(\s*\$.+)?'),
                re.compile(r'\s*(while)\s*\(\s*([^\(\)]+)\)\s*\{(\s*\$.+)?'),
                re.compile(r'\s*\}\s*'),
                re.compile(r'\n\s*\n')]
                # index 0 for create command
                # index 1 for context command
                # index 2 for display command
                # index 3 for setFunc command
                # index 4 for print command
                # index 5 for quantify a cell
                # index 6 for variables
                # index 7 for variables
                # index 8 for setFunc with complicate expersions
                # index 9 for Comments
                # index 10 for if command
                # index 11 for while loop
                # index 12 for closed curly braces
                # index 13 for blank lines


curTable = None
variablesDictionary = {}
def CommandsFunctions(commandsList):
    global variablesDictionary
    global curTable

    def createCommand(i):
        matchList = list(patternsList[0].finditer(commandsList[i]))
        tableName = matchList[0].group(2)
        TablesDictionary.update({tableName:Table(matchList[0].group(2), int(matchList[0].group(3)), int(matchList[0].group(4)))})

    def contextCommand(i, curTable):
        matchList = list(patternsList[1].finditer(commandsList[i]))
        tableName = matchList[0].group(2)
        for tbl in TablesDictionary.keys():
            if tableName == tbl:
                curTable = TablesDictionary[tbl]
                return curTable
        if tableName not in TablesDictionary.keys(): printError()

    def displayCommand(i, curTable):
        matchList = list(patternsList[2].finditer(commandsList[i]))
        tableName = matchList[0].group(2)
        tmp = []
        for tbl in TablesDictionary.keys():
            if tableName == tbl:
                tmp = TablesDictionary[tbl]
                tmp.display(variablesDictionary)
                break
        if tableName not in TablesDictionary.keys(): printError()

    def setFuncCommand1(i, curTable):
        if curTable == None: printError()
        matchList = list(patternsList[3].finditer(commandsList[i]))
        curTable.setFunc(matchList[0].group(2), matchList[0].group(3), matchList[0].group(4))
        return curTable

    def printCommand(i, curTable):
        matchList = list(patternsList[4].finditer(commandsList[i]))
        exp = matchList[0].group(2)
        exp = evalStrVersion3(exp, curTable.Table if curTable != None else [], variablesDictionary)
        print("out:"+exp)

    def changeValueCommand(i, curTable):
        if curTable == None: printError()
        matchList = list(patternsList[5].finditer(commandsList[i]))
        column = matchList[0].group(1)
        row = matchList[0].group(2)

        val = matchList[0].group(3)
        val = evalStrVersion3(val, curTable.Table if curTable != None else [], variablesDictionary)
        curTable.changeValue(column, row, val)
        return curTable

    def variablesCommand1(i, curTable):
        matchList = list(patternsList[6].finditer(commandsList[i]))
        var = matchList[0].group(1)
        exp = matchList[0].group(2)
        exp = evalStrVersion3(exp, curTable.Table if curTable != None else [], variablesDictionary)
        variablesDictionary.update({var: exp})

    def variablesCommand2(i, curTable):
        if curTable == None: printError()
        matchList = list(patternsList[7].finditer(commandsList[i]))
        column = matchList[0].group(1)
        column = evalStrVersion3(column, curTable.Table if curTable != None else [], variablesDictionary)
        row = matchList[0].group(2)
        row = evalStrVersion3(row, curTable.Table if curTable != None else [], variablesDictionary)
        if '\"' in column: column = column[1:len(column)-1]
        if '\"' in row: row = row[1:len(row)-1]
        val = matchList[0].group(3)
        val = evalStrVersion3(val, curTable.Table if curTable != None else [], variablesDictionary)
        curTable.changeValue(column, row, val)
        return curTable

    def setFuncCommand2(i, curTable):
        if curTable == None: printError()
        matchList = list(patternsList[8].finditer(commandsList[i]))
        cell = matchList[0].group(2)
        cell = evalStrVersion3(cell, curTable.Table if curTable != None else [], variablesDictionary, True, True, False, False, False, False)

        pat = re.compile(r'\s*\[([\"A-Z]+)\]\s*\[([0-9]+)\]\s*')
        matches = list(pat.finditer(cell))
        column = matches[0].group(1)
        row = matches[0].group(2)
        if '\"' in column: column = column[1:len(column)-1]
        if '\"' in row: row = row[1:len(row)-1]

        exp = matchList[0].group(3)
        exp = evalStrVersion3(exp, curTable.Table if curTable != None else [], variablesDictionary, True, True, False, False, False, False)
        
        matches = list(pat.finditer(exp))
        for i in range(len(matches)):
            x, y = matches[i].group(1), matches[i].group(2)
            if '\"' in x: x = x[1:len(x)-1]
            if '\"' in y: y = y[1:len(y)-1]
            exp = re.sub(pat, str(x)+str(y), exp, 1)

        curTable.setFunc(column, row, exp)
        return curTable

    def ifCommandFunction(i, curTable):
        matchList = list(patternsList[10].finditer(commandsList[i]))
        condition = matchList[0].group(2)
        if evalBoolean(condition, curTable.Table if curTable != None else [], variablesDictionary):
            ifPointer = i + 1
            curlyBraceCounter = 1
            ifCommandsList = []
            while curlyBraceCounter != 0:
                if re.search(patternsList[10], commandsList[ifPointer]): curlyBraceCounter += 1
                if re.search(patternsList[11], commandsList[ifPointer]): curlyBraceCounter += 1
                if re.search(patternsList[12], commandsList[ifPointer]): curlyBraceCounter -= 1
                ifCommandsList.append(commandsList[ifPointer])
                ifPointer += 1
            
            ifCommandsList.pop()
            CommandsFunctions(ifCommandsList)
            return ifPointer
        
        else:
            ifPointer = i + 1
            curlyBraceCounter = 1
            while curlyBraceCounter != 0:
                if re.search(patternsList[10], commandsList[ifPointer]): curlyBraceCounter += 1
                if re.search(patternsList[11], commandsList[ifPointer]): curlyBraceCounter += 1
                if re.search(patternsList[12], commandsList[ifPointer]): curlyBraceCounter -= 1
                ifPointer += 1
            return ifPointer

    def whileLoopCommandFunction(i, curTable):
        matchList = list(patternsList[11].finditer(commandsList[i]))
        condition = matchList[0].group(2)
        if evalBoolean(condition, curTable.Table if curTable != None else [], variablesDictionary):
            whilePointer = i + 1
            curlyBraceCounter = 1
            whileCommandsList = []
            while curlyBraceCounter != 0:
                if re.search(patternsList[10], commandsList[whilePointer]): curlyBraceCounter += 1
                if re.search(patternsList[11], commandsList[whilePointer]): curlyBraceCounter += 1
                if re.search(patternsList[12], commandsList[whilePointer]): curlyBraceCounter -= 1
                whileCommandsList.append(commandsList[whilePointer])
                whilePointer += 1

            whileCommandsList.pop()

            while evalBoolean(condition, curTable.Table if curTable != None else [], variablesDictionary):
                CommandsFunctions(whileCommandsList)
            return whilePointer

        else:
            whilePointer = i + 1
            curlyBraceCounter = 1
            while curlyBraceCounter != 0:
                if re.search(patternsList[10], commandsList[whilePointer]): curlyBraceCounter += 1
                if re.search(patternsList[11], commandsList[whilePointer]): curlyBraceCounter += 1
                if re.search(patternsList[12], commandsList[whilePointer]): curlyBraceCounter -= 1
                whilePointer += 1
            return whilePointer

    i = 0
    while i != len(commandsList):

        if re.search(patternsList[0]   , commandsList[i]): createCommand(i); i += 1
        elif re.search(patternsList[1] , commandsList[i]): curTable = contextCommand(i, curTable); i += 1
        elif re.search(patternsList[2] , commandsList[i]): displayCommand(i, curTable); i += 1
        elif re.search(patternsList[3] , commandsList[i]): curTable = setFuncCommand1(i, curTable); i += 1
        elif re.search(patternsList[4] , commandsList[i]): printCommand(i, curTable); i += 1
        elif re.search(patternsList[5] , commandsList[i]): curTable = changeValueCommand(i, curTable); i += 1
        elif re.search(patternsList[6] , commandsList[i]): variablesCommand1(i, curTable); i += 1
        elif re.search(patternsList[7] , commandsList[i]): curTable = variablesCommand2(i, curTable); i += 1
        elif re.search(patternsList[8] , commandsList[i]): curTable = setFuncCommand2(i, curTable); i += 1
        elif re.search(patternsList[9] , commandsList[i]): i += 1
        elif re.search(patternsList[10], commandsList[i]): i = ifCommandFunction(i, curTable)
        elif re.search(patternsList[11], commandsList[i]): i = whileLoopCommandFunction(i, curTable)
        elif re.search(patternsList[13], commandsList[i]): i += 1
        else: i += 1
    
    return curTable.Table





#commandsList = []
#n = int(input())
#for _ in range(n):
#    commandsList.append(input())
#CommandsFunctions(commandsList)