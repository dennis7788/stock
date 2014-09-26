# -*- coding: utf-8 -*-  
  
import urllib  
import  urllib2
import MySQLdb
import time
from main import dbUtil
# Add one more item at end of list for stopping parsing .  
incomeName=['營業收入','營業成本','營業毛利(毛損)','營業費用','營業淨利(淨損)','營業外收入及利益',
                '營業外費用及損失','繼續營業單位稅前淨利(淨損)','所得稅費用（利益）','繼續營業單位淨利(淨損)',
                '停業單位損益','非常損益','會計原則變動累積影響數','合併總損益','合併淨損益','少數股權損益',
                '基本每股盈餘','DennisChen']  

   
balanceName=['流動資產','基金與投資','固定資產','無形資產','其他資產','資產總計',
                '流動負債','長期負債','各項準備','其他負債','負債總計','股本','資本公積',
                '保留盈餘','股東權益其他調整項目合計','庫藏股票','少數股權','股東權益總計',
                '預收股款','母公司暨子公司所持有之母公司庫藏股股數','每股淨值','DennisChen'] 


def parsingWebContent(url, code):
    
    web = urllib.urlopen(url)  
    webContent = web.read().decode(code)
    web.close()  
    return webContent


#Only for parsing balance and income statement
def getStateData (stateNameList,state,coId,year,season):
    
    urlStatement={
    'income':'http://mops.twse.com.tw/mops/web/t05st30_c?',
    'balance':'http://mops.twse.com.tw/mops/web/t05st29_c?',
    'cash':'http://mops.twse.com.tw/mops/web/t05st39?',
    'stockholder':'http://mops.twse.com.tw/mops/web/t05st38?'}
    #const variable in url
    urlConstVar = 'step=1&firstin=true&off=1&keyword4=&code1=&TYPEK2=&checkbtn=&queryName=co_id&TYPEK=all&isnew=false&'
    urlNoConstVar ={'corp':'&co_id=',
    'year':'&year=',
    'season':'&season='}
    
    url = urlStatement[state] + urlConstVar + urlNoConstVar['corp']+coId+urlNoConstVar['year']+year+urlNoConstVar['season']+season
    
    startToPrint = 0
    incomeCou = 0
    for line in parsingWebContent(url,'utf-8').splitlines():  
        if(startToPrint > 0):
            startToPrint -= 1
            stringNum =''
            for subNum in line.split(">")[1].split("<")[0].split(","):
                stringNum += subNum
            print float(stringNum)

        if (line.find(stateNameList[incomeCou]) >=0):
            
            startToPrint = 4 
            print stateNameList[incomeCou]
            if incomeCou < len(stateNameList) -1:
                incomeCou += 1
            #print "line" + line
class incomedata:
    gross_profit = 0
    operating_profit = 0
    Pre_Tax_income = 0 
    net_profit = 50 
    # 0 '營業收入' 1 '營業毛利（毛損）淨額'  2'營業利益（損失）'
    #3'稅前淨利（淨損）' 4'綜合損益總額歸屬於母公司業主'
    orgValueList = []


def getIncome (coId,year):
    
    newIncomeName=['營業收入','營業毛利（毛損）淨額','營業利益（損失）',
               '稅前淨利（淨損）','綜合損益總額歸屬於母公司業主']
    urlIncome='http://mops.twse.com.tw/mops/web/t163sb15?'
    
    #const variable in url
    urlConstVar = 'step=1&firstin=true&off=1&keyword4=&code1=&TYPEK2=&checkbtn=&queryName=co_id&TYPEK=all&isnew=false&'
    urlNoConstVar ={'corp':'&co_id=',
    'year':'&year='}
    
    url = urlIncome + urlConstVar + urlNoConstVar['corp']+coId+urlNoConstVar['year']+year
    
 
    startToRecord = 0
    incomeCou = 0
    incomeObjlist = []
    for index in range(4):
        incomeObjlist.append(incomedata())
    
    for line in parsingWebContent(url,'utf-8').splitlines():  
       
        if( startToRecord > 0):
            
            stringNum = line.split(">")[1].split("<")[0]
            #print stringNum  
            if (stringNum.find("-") > 0):
                startToRecord = -1
            else:
                startToRecord -= 1
                valueNum = changeFormOfInt (stringNum)
                
                #incomeObjlist[incomeCou -1].orgValueList.append(float(valueNum))
                print valueNum
        
        
        if (line.find(newIncomeName[incomeCou]) >=0):
            
            startToRecord = 3 
            print newIncomeName[incomeCou]
            if incomeCou < len(newIncomeName) -1:
                incomeCou += 1
            
            stringNum =''
            for subNum in line.split(">")[3].split("<")[0].split(","):
                stringNum += subNum
            
            incomeObjlist[0].orgValueList.append(float(stringNum))
            print float(stringNum) 
            #print "line" + line

    for obj in incomeObjlist:
        print obj.orgValueList
        
        
# Change this '5,786,107' to 5786107
def changeFormOfInt (stringNum):
    combineNum = ''
    for subNum in stringNum.split(","):
        combineNum += subNum

    return combineNum

def getfromDB():
    cur = dbUtil.connectTODB()
    command = "select * from revenue_102_8" 
    cur.execute(command)
    test = cur.fetchall()
    cout = 0
    for one in test:
        cout += 1 
        print str(one[0])+" " + one[1] +"  "+  str(getStockPrice(one[0])) +"元"
        #print one[2] 
        if cout >30:
            break

    print "Total num is" + str(cout)

def downloadAllPrice():
    cur = dbUtil.connectTODB()
    command = "select * from revenue_102_12" 
    cur.execute(command)
    test = cur.fetchall()
    cout = 0
    for one in test:
        cout += 1 
        num = str(one[0])
        com = one[1]
        price = str(getStockPrice(one[0]))
        print  num +" " + com +"  "+ price +"元"
        command = "INSERT INTO stockPrice VALUES(\'"+  num +"\',\'"+ com + "\',\'" + price +"\')" 
        print command
        cur.execute(command)
       
       

    print "Total num is" + str(cout)


def parsingRevenue (year,month):
    
    # connect to database
    cur = dbUtil.connectTODB()
    url = 'http://mops.twse.com.tw/t21/sii/t21sc03_'+year+'_'+month +'_0.html'
    print url
    cout = 0
    for line in parsingWebContent(url,'big5hkscs').splitlines():
        for sub in line.split("</tr>"):
            cout += 1
            # the print message is for debugging
            #if cout < 30:
                #print sub
            
            # get name of 產業
            if sub.find('產業別') >= 0:
                sub2 = sub.split(">")[5].split("<")[0].split('：')          
                for sub3 in sub2:
                    if sub3.find('產業別') < 0:
                        print sub3
            # It is the duplicate data in this section.
            if sub.find('電子工業') > 0:
                break
            #get revenue             
            if cout > 3 and sub.find("</table>") < 0 and sub.find("IFRSs") < 0 and sub.find("合計") < 0 and sub.find("去年當月營收") < 0 :        
                sub2 = sub.split(">")
                # "if" for controlling test.
                # ide represents stockNum, name represents company name,
                # rev represents revenue for each month, 
                # increaseRate for increasing rate yearly.
                if cout < 3000 :
                    ide = sub2[2].split("<")[0]
                    name = sub2[4].split("<")[0]
                    rev = sub2[6].split("<")[0]
                   
                    # only record "ide" with stock number
                    if ide.isdigit():
                        increaseRate = sub2[14].split("<")[0]
                        # if increase rate is empty, put 0 in it.
                        if increaseRate.find(";") > 0:
                            increaseRate = '0.0'
                           
                        # Insert data into database.   
                        command = "INSERT INTO revenue_tmp VALUES(\'"+ ide +"\',\'"+ name + "\',\'" + changeFormOfInt(rev)+"\',\'"+ changeFormOfInt(increaseRate) +"\')" 
                        cur.execute(command)
                       

    tableName = "revenue_"+year+"_"+month
    #Create table for storing data
    command = "CREATE TABLE " + tableName +" (stockNum integer, company VARCHAR(30),revenue integer,increaseRate double)"
    cur.execute(command)
   
    # Delete the duplicate items, and copy to the form revenue table
    #clean tmp table
    command = "INSERT INTO " + tableName +" select * from revenue_tmp  GROUP BY stockNum"
    cur.execute(command)
    time.sleep(0.5)
    command = "truncate table revenue_tmp"
    cur.execute(command)
    
    
def getStockPrice(stockNum):
    
    print stockNum
    url = 'http://tw.stock.yahoo.com/q/q?s=' +str(stockNum)
    cout = 0
    # because the stock price is under "加到投資組合" about 2 lines, 
    # we use this tag to show start to count.
    startToCount = 0
    for line in parsingWebContent(url,'big5hkscs').splitlines():  
        if startToCount == 1:
            cout += 1
        
        if cout == 2 :
            print "stock price"  
            # parsing this line 
            # <td align="center" bgcolor="#FFFfff" nowrap><b>30.95</b></td>
            # stockPrice is a float number
           
            stockPriceCheck = line.split(">")[2].split("<")[0]
            if  stockPriceCheck.find("－") < 0:
                stockPrice = float(stockPriceCheck)
                print stockPrice
                return stockPrice
            else:
                return -1
        
        if line.find('加到投資組合') > 0 :
            #debug message print "Dennis" + line
            startToCount = 1



try:  
    
    getIncome('4906','102')
    #parsingRevenue('102','12')
    #getStockPrice(2303)
    # getStockNum()   
    #getfromDB()
    #downloadAllPrice()
    #print float("0",10)

   
except :  
    print "# Parser error : " 


print "Press enter to continue."  

#For user to insert value
raw_input()  
