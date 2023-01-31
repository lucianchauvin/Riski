from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np, io, requests, json, random, yfinance as yf
from PIL import ImageTk, Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

risk = 0

headers = ['Type', 'Name', 'Symbol', 'CUSIP', 'Value', 'Shares', 'Interest Rate', 'Total Value', 'Notes']
typesAll =  ['Stock', 'ETF', 'Saving', 'Crypto', 'Bond', 'Option', '401k', 'Future', 'Forex', 'Other', 'NONE']

usDebt = float(json.loads(requests.get('https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny?filter=record_date:eq:2023-01-26').text)['data'][0]['debt_held_public_amt'])
usPOP = int(json.loads(requests.get('https://www.census.gov/popclock/data/population.php/us?_=1674948379627').text)["us"]["population"])
usDebtPerCap = usDebt/usPOP

response = requests.get('https://api.api-ninjas.com/v1/inflation?country=United States', headers={'X-Api-Key': '6jIzwcmGD4vPeW9+OqZ7DA==zrFuzPc75G4hVGKs'}).text
usInflation = float(json.loads(response)[0]['yearly_rate_pct'])

response = requests.get('https://api.api-ninjas.com/v1/interestrate', headers={'X-Api-Key': '6jIzwcmGD4vPeW9+OqZ7DA==zrFuzPc75G4hVGKs'})
usInterest = float(json.loads(response.text)['central_bank_rates'][0]['rate_pct'])

unemployment = 3.5 

risk += (usInflation*unemployment*usInterest)*10 +.2

def analyse(root, types, data):
    global risk
    root2 = Toplevel(root)
    root2.title("Analysis")
    root2.geometry('900x320')

    tabControl = ttk.Notebook(root2)
    overall = ttk.Frame(tabControl)
    stocksF = ttk.Frame(tabControl)
    tabControl.add(overall, text ='Overall')
    tabControl.pack(expand = 1, fill ="both")
    tabControl.add(stocksF, text ='Stocks')
    tabControl.pack(expand = 1, fill ="both")

    outPut = Text(overall, width=75, height=16)
    outPut.place(relx=.32, rely=.025)

    outPutS = Text(stocksF, width=75, height=16)
    outPutS.place(relx=.32, rely=.025)

    for x in range(len(types)):
        if x == 'NONE':
            del data[x]

    data = [[types[x]] + data[x][:4] + [float(y) if y != "required" and y != '' else 0 for y in data[x][4:-1]] + [data[x][-1]] for x in range(len(data))]
    
    totalEval = sum([float(x[headers.index('Total Value')]) if x[headers.index('Total Value')] != '' else 0 for x in data])
    data = [x + [x[headers.index('Total Value')]/totalEval] for x in data]

    byType = [sum([x[headers.index('Total Value')] if x[0] == y else 0 for x in data]) for y in typesAll]

    percents = [x/totalEval for x in byType]
    names = typesAll[:]

    iOff = 0
    for i in range(len(typesAll)):
        if percents[i-iOff] == 0:
            del percents[i-iOff]
            del names[i-iOff]
            iOff += 1
    strT = list(zip(names, percents))
    strT = [str(x[0]) + ' (' + str(round(x[1]*100, 2)) + '%)' for x in strT]

    plt.pie(percents, labels = names, radius=1)
    plt.title('Portfolio Breakdown')
    plt.legend(strT, loc='upper left', bbox_to_anchor=(-0.1, 1.))
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png') 
    im = Image.open(img_buf)
    width, height = im.size
    ratio = 290/height

    im = im.resize((int(width*ratio), 290), Image.ANTIALIAS)
    width, height = im.size
    im = im.crop((width*.15, 0, width*.85, height*.9))
    tkImg = ImageTk.PhotoImage(im)



    plot = Label(overall, image=tkImg)
    plot.image = tkImg
    plot.place(relx=0.01, rely=0.025)

    stockWorth = byType[typesAll.index('Stock')]



    #     plot = Label(stocksF, image=tkImg)
    #     plot.image = tkImg
    #     plot.place(relx=0.01, rely=0.025)
        
        


    overallLinked = list(zip(data, percents))
    overallLinked.sort(key=lambda x: x[1], reverse=True)

    notIn = [x for x in typesAll[0:9] if x not in [y[0] for y in data]]
    alrdOut = []
    outPut.insert(END, 'Overall: \n')
    any30 = False
    for x in overallLinked:
        if x[1] > .3:
            risk += .3*x[1]
            any30 = True
            if str(x[0][0]) not in alrdOut:
                if str(x[0][0]) != 'Bond' and str(x[0][0]) != 'Saving':
                    alrdOut.append(str(x[0][0]))
                    outPut.insert(END, 'You are heavily invested in ' + str(x[0][0]) + 's. Consider diversifying your portfolio by moving money into: ' + str(", ".join(notIn)) + '.\n')
                elif str(x[0][0]) == 'Savings':
                    risk -= .2*x[1]
                    alrdOut.append(str(x[0][0]))
                    outPut.insert(END, 'You are heavily invested in ' + str(x[0][0]) + 's. Allthough you are heavily invested, ' + str(x[0][0]) +  ' are generally low risk.\n')
                elif str(x[0][0]) == 'Bonds':
                    alrdOut.append(str(x[0][0]))
                    risk -= .2*x[1]
                    outPut.insert(END, 'You are heavily invested in ' + str(x[0][0]) + '. Allthough you are heavly invested, ' + str(x[0][0]) +  ' they are unlinkley to default.\n')
    if any30:
        outPut.insert(END, 'In general it is not a good idea to have more than 30% of your portfolio in one type of asset.')
    else:
        outPut.insert(END, 'The top level of your portfoli is well diversified.')

    savingData = [(x[6], x[7]) for x in data if x[0] == 'Saving']

    for x in savingData:
        if x[0] < usInterest:
            outPut.insert(END, ' The interest rate for your savings is lower than the U.S. average. Consider moving money.\n')
        elif x[0] > usInterest*1.5:
            risk += .3*usInterest
            outPut.insert(END, ' The interest rate for your savings is significantly higher than the U.S. average. Consider moving money.\n')

    if 'Stock' in names:
        stocks = [x for x in data if x[0] == 'Stock']

        for x in stocks:
            try:
                if x[7]/stockWorth > .3 or yf.Ticker(x[2]).info['beta'] > 1.2:
                    risk += .3*x[7]*yf.Ticker(x[2]).info['beta']
                    outPut.insert(END, ' High risk is coming from your stock investments. Click on the "Stocks" tab to learn more.\n')
                    if yf.Ticker(x[2]).info['beta'] > 1:
                        risk += .2*yf.Ticker(x[2]).info['beta']
                        outPutS.insert(END, 'The stock ' + x[2] + ' has a beta of ' + str(yf.Ticker(x[2]).info['beta']) + '. This means that the stock is more volatile than the market.\n')
                    if x[7]/stockWorth > .3:
                        outPutS.insert(END, 'The stock ' + x[2] + ' makes up ' + str(round(x[7]/stockWorth*100, 2)) + '% of your stock portfolio. This is a large amount of your portfolio.\n')
            except:
                pass
    percents = [x[7]/stockWorth for x in data if x[0] == 'Stock']
    names = [x[2] for x in data if x[0] == 'Stock']
    strT = list(zip(names, percents))
    strT = list(zip(names, percents))
    strT = [str(x[0]) + ' (' + str(round(x[1]*100, 2)) + '%)' for x in strT]
    plt.cla()
    plt.pie(percents, labels = names, radius=1)
    plt.title('Stock Breakdown')
    plt.legend(strT, loc='upper left', bbox_to_anchor=(-0.1, 1.))
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png') 
    im = Image.open(img_buf)
    width, height = im.size
    ratio = 290/height

    im = im.resize((int(width*ratio), 290), Image.ANTIALIAS)
    width, height = im.size
    im = im.crop((width*.15, 0, width*.85, height*.9))
    tkImg = ImageTk.PhotoImage(im)

    plot2 = Label(stocksF, image=tkImg)
    plot2.image = tkImg
    plot2.place(relx=0.01, rely=0.025)


    outPut.insert(END, f'\nYour risk score is {round(risk/totalEval, 2)} out of 1.0. A score close to or above. 1 is considered high risk.')











