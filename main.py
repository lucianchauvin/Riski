from tkinter import ttk
from tkinter import *
from riskAnalysis import analyse
import requests, json, yfinance as yf, tkinter.font, tkinter as tk

class Table:
     
    def __init__(self,root,total_rows,total_columns):
        self.data = []
         
        # code for creating table
        for i in range(total_rows):
            row = []
            for j in range(total_columns):
                 
                self.e = ttk.Entry(root, width=(9 if j != total_columns-1 else 15),
                               font=('Arial',12))
                 
                self.e.grid(row=i, column=j)
                self.e.insert(END, "")
                self.e.bind("<FocusIn>", clear)
                row.append(self.e)
            self.data.append(row)
    def getData(self):
        data = []
        for row in self.data:
            data.append([e.get() for e in row])
        return data

# find total number of rows and
# columns in list



root = tk.Tk()
style = ttk.Style(root)

# tell tcl where to find the awthemes packages
root.tk.eval("""
set base_theme_dir C:/Users/lucia/Downloads/awthemes-10.4.0/awthemes-10.4.0

package ifneeded awthemes 10.4.0 \
    [list source [file join $base_theme_dir awthemes.tcl]]
package ifneeded colorutils 4.8 \
    [list source [file join $base_theme_dir colorutils.tcl]]
package ifneeded awdark 7.12 \
    [list source [file join $base_theme_dir awdark.tcl]]
package ifneeded awlight 7.6 \
    [list source [file join $base_theme_dir awlight.tcl]]
""")
# load the awdark and awlight themes
root.tk.call("package", "require", 'awdark')
root.tk.call("package", "require", 'awlight')
style.theme_use('awlight')

root.geometry('1200x555')
root.resizable(False, False)
root.title('Riski')

def syLookUp():
    def getSymbol(symbol):
        data = yf.Ticker(symbol).history(period='1d')
        stData.delete(1.0, END)
        stData.insert(END, str(data))
    root3 = Toplevel(root)
    root3.title("Symbol Lookup")
    root3.geometry(f'{16*67}x{9*15}')

    labelS = tk.Label(root3, text = 'Symbol:')
    labelS.place(relx=.01, rely=.02)

    symbol = tk.Entry(root3, width=40)
    symbol.place(relx=.15, rely=.02)

    buttoS = tk.Button(root3, height=0, width=8, text = 'Search', command=lambda: getSymbol(symbol.get()))
    buttoS.place(relx=.8, rely=.01)

    stData = tk.Text(root3, width=130, height=6, wrap=WORD)
    stData.place(relx=.01, rely=.21)


tabControl = ttk.Notebook(root)
tab1 = ttk.Frame(tabControl)
tabControl.add(tab1, text ='Portfolio 1')
tabControl.pack(expand = 1, fill ="both")

riskAnal = tk.Button(tab1, text = 'ANALYSE RISK', font='Ariel 25 bold', width = 40, fg="green", command= lambda: analyse(root, [x.get() for x in types],table.getData()))
riskAnal.place(relx=.3, y=442)

syLook = tk.Button(tab1, text = 'Symbol Lookup', font='Ariel 25 bold', width = 15, command=syLookUp)
syLook.place(relx=.01, y=442)

tab2 = ttk.Frame(tabControl)
tabControl.add(tab2, text ='Portfolio 2')
tabControl.pack(expand = 1, fill ="both")

sideBar = ttk.Frame(tab1, width = 200, height = 420, relief = tk.SUNKEN)
sideBar.place(relx=0.01, rely=0.02)

usInfo = tk.Text(sideBar, width=22, height=23, font='Helvetica 12', wrap=WORD)
# usInfo.place(relx=0, rely=0)
usInfo.pack()



usDebt = float(json.loads(requests.get('https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny?filter=record_date:eq:2023-01-26').text)['data'][0]['debt_held_public_amt'])
usPOP = int(json.loads(requests.get('https://www.census.gov/popclock/data/population.php/us?_=1674948379627').text)["us"]["population"])
usDebtPerCap = usDebt/usPOP

response = requests.get('https://api.api-ninjas.com/v1/inflation?country=United States', headers={'X-Api-Key': '6jIzwcmGD4vPeW9+OqZ7DA==zrFuzPc75G4hVGKs'}).text
usInflation = float(json.loads(response)[0]['yearly_rate_pct'])

response = requests.get('https://api.api-ninjas.com/v1/interestrate', headers={'X-Api-Key': '6jIzwcmGD4vPeW9+OqZ7DA==zrFuzPc75G4hVGKs'})
usInterest = float(json.loads(response.text)['central_bank_rates'][0]['rate_pct'])




usInfo.insert(END, f"US Economy Information \n\n General: \n Unemployment: 3.5% \n GDP Per Cap: 70.148k \n Inflation: {usInflation:.2f}% \n FR Interest Rate: {usInterest}% \n\n NYSE: \n NASDAQ Composite: \n ${yf.Ticker('^IXIC').history(period='1d')['Close'][0]:.2f} \n S&P 500: ${yf.Ticker('^GSPC').history(period='1d')['Close'][0]:.2f} \n Russell 2000: ${yf.Ticker('^RUT').history(period='1d')['Close'][0]:.2f} \n\n Forex: \n USD/EUR: {yf.Ticker('EUR=X').history(period='1d')['Close'][0]:.2f} \n USD/CNY: {yf.Ticker('CNY=X').history(period='1d')['Close'][0]:.2f} \n USD/RUB: {yf.Ticker('RUB=X').history(period='1d')['Close'][0]:.2f} \n USD/MNX: {yf.Ticker('MXN=X').history(period='1d')['Close'][0]:.2f} \n\n Debt per capita: \n ${usDebtPerCap:.2f}")

usInfo.config(state=DISABLED)

mainFrame = ttk.Frame(tab1, width = 960, height = 425)
mainFrame.place(relx=.185, rely=0.01)

headersFrame = ttk.Frame(mainFrame, width = 930, height = 25)
headersFrame.place(relx=0, rely=0)
numLabels = ttk.Label(headersFrame, font='Helvetica 12', text = '#',anchor='center')
numLabels.place(relx=0, y=0)

headers = ['Name', 'Symbol', 'CUSIP', 'Value', 'Shares', 'Interest Rate', 'Total Value', 'Notes']
headerLabel = ttk.Label(headersFrame, font='Helvetica 12', text = "Type",anchor='center')
headerLabel.place(relx=.045, y=0)

for i in headers:
    headerLabel = ttk.Label(headersFrame, font='Helvetica 12', text = i,anchor='center')
    headerLabel.place(relx=.155, x = headers.index(i)*95, y=0)


lineNumbers = ttk.Frame(mainFrame, width = 30, height = 420)
lineNumbers.place(relx=0, rely=.075)


def clear(e):
    if e.widget.get() == 'required':
        e.widget.delete(0, END)

def getReq(i, rType, tData):
    rType = rType.get()
    # ['Name', 'Symbol', 'CUSIP', 'Value', 'Shares', 'Interest Rate', 'Total Value', 'Notes']z
    reHash = {
        'Stock': ['required','required', '', 'required', 'required','', 'required'],
        'ETF': ['required','required', '', 'required','required','','required'],
        'Crypto': ['required','required','', 'required','','','required'],
        'Bond': ['required','', 'required', 'required', '', '', 'required'],
        'Option': ['required','', '', 'required', '', '', 'required'],
        '401k': ['required','', '', 'required', '', '', 'required'],
        'Future': ['required','', '', 'required', '', '', 'required'],
        'Forex': ['required','required', '', 'required', '', '', 'required'],
        'Other': ['required','', '', '','','','required'],
        'NONE': ['','','', ''],
        'Saving': ['required','','', 'required', '', 'required', 'required']
    }
    for j in range(8):
        try:
            tData[i][j].delete(0,END)
            tData[i][j].insert(0,reHash[rType][j])
        except IndexError:
            pass


tableFrame = ttk.Frame(mainFrame, width = 930, height = 420)
tableFrame.place(relx=.15, rely=.075)

table = Table(tableFrame,16,8)
types = []

for i in range(16):
    lineLabel = ttk.Label(lineNumbers, font='Helvetica 12', text = i+1)
    lineLabel.place(relx=0, y=24*i)

    rType = ttk.Combobox(mainFrame, textvariable=tk.StringVar(), width=10, state='readonly', height=100)
    rType['values'] = ('Stock', 'ETF', 'Saving', 'Crypto', 'Bond', 'Option', '401k', 'Future', 'Forex', 'Other', 'NONE')
    rType.place(relx=.045, rely= .075, y=24*i)
    rType.set('NONE')
    rType.bind("<<ComboboxSelected>>", lambda event, i=i, rType=rType, tData=table.data: getReq(i, rType, tData))
    types.append(rType)

root.mainloop()
