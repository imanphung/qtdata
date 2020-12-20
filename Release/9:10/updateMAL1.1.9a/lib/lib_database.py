def get_data_finance_yahoo(stock, start, end, frequency):
    import time
    from datetime import datetime
    import requests
    import pandas as pd
    import lxml.html as lh
    from openpyxl import load_workbook
    # Set Up
    start = int(time.mktime(time.strptime(start, "%m/%d/%Y")))
    end = int(time.mktime(time.strptime(end, "%m/%d/%Y")))
    assert frequency in ['daily', 'weekly', 'monthly'], 'Frequency has to be daily, weekly, or monthly'
    if frequency == 'daily':
        frequency = '1d'
    elif frequency == 'weekly':
        frequency = '1wk'
    else:
        frequency = '1m'
    
    # Get Data
    YahooFinance = 'https://query1.finance.yahoo.com/v7/finance/download/{stock}?period1={start}&period2={end}&interval={frequency}&events=history&crumb=Vp5JJJIY4i/'
        
    arr_table = [
                'https://finance.yahoo.com/quote/{stock}/key-statistics?p={stock}',
                'https://finance.yahoo.com/quote/{stock}/analysis?p={stock}',
                'https://finance.yahoo.com/quote/{stock}/profile?p={stock}',
                'https://finance.yahoo.com/quote/{stock}/holders?p={stock}',
                'https://finance.yahoo.com/quote/{stock}/insider-roster?p={stock}',
                'https://finance.yahoo.com/quote/{stock}/insider-transactions?p={stock}'
                ]
    arr_sheet = ['Statistics','Analysis','Profile','Holders','Insider-roster','Insider-transactions']
    financial =  'https://finance.yahoo.com/quote/{stock}/financials?p={stock}'
    chart_comment = 'https://finance.yahoo.com/quote/{stock}/chart?p={stock}'

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
        'cookie': 'B=a2qoc01dom2ob&b=3&s=hv; GUC=AQEBAQFbyD5cnEIe4gR7&s=AQAAAKXb1OzH&g=W8bwqg; PRF=t%3DNFLX%252BSPY%252BRTY%253DF%252BRUTH%252B%255EIXIC%26fin-trd-cue%3D1',
        'pragma': 'no-cache',
        'referer': 'https://finance.yahoo.com/quote/{stock}/history?period1={start}&period2={end}&interval={frequency}&filter=history&frequency={frequency}'.format(stock=stock, frequency = frequency, start=start, end=end),
        'upgrade-insecure-requests': '1'
    }
    
    url = YahooFinance.format(stock=stock, frequency = frequency, start=start, end=end)
    response = requests.get(url, headers=headers)
    text = response.text
    lines =  text.split('\n')
    Date = []
    Open = []
    High = []
    Low = []
    Close = []
    Adj_Close = []
    Volume = []

    for line in lines[1:-1]:
        [d,o,h,l,c,ac,v] = line.split(',')
        Date.append(d)
        Open.append(float(o))
        High.append(float(h))
        Low.append(float(l))
        Close.append(float(c))
        Adj_Close.append(float(ac))
        Volume.append(float(v))
    df = pd.DataFrame({'Date': Date,
                        'Open': Open,
                        'High': High,
                        'Low': Low,
                        'Close': Close,
                        'Adj_Close': Adj_Close,
                        'Volume': Volume
                        }, columns=['Date','Open','High','Low','Close','Adj_Close','Volume'])
    df = df.sort_index()
    excelName = 'finance_yahoo.xlsx_{}.xlsx'.format(datetime.now().strftime('%H%M%S'))
    writer = pd.ExcelWriter(excelName)
    df.to_excel(writer, sheet_name = "History", index = False)
    writer.save()
    book = load_workbook(excelName)
    writer = pd.ExcelWriter(excelName, engine = 'openpyxl')
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

    for i,s in zip(arr_table,arr_sheet):
        url = i.format(stock=stock)
        page = requests.get(url)
        #Store the contents of the website under doc
        doc = lh.fromstring(page.content)
        #Parse data that are stored between <tr>..</tr> of HTML
        tr_elements = doc.xpath('//tr')
        #Check the length of the first 12 rows
        [len(T) for T in tr_elements[:12]]
        tr_elements = doc.xpath('//tr')
        #Create empty list
        col=[]
        i=0
        #For each row, store each first element (header) and an empty list
#        if arr_table[3] is False:
        for t in tr_elements[0]:
            i+=1
            name=t.text_content()
            col.append((name,[]))    
        #Since out first row is the header, data is stored on the second row onwards
        for j in range(len(tr_elements)):
            #T is our j'th row
            T=tr_elements[j]   
            #If row is not of size col, the //tr data is not from our table 
            if len(T)!=len(col):  
                break   
            #i is the index of our column
            i=0  
            #Iterate through each element of the row
            for t in T.iterchildren():
                data=t.text_content() 
                #Check if row is empty
                if i>0:
                #Convert any numerical value to integers
                    try:
                        data=int(data)
                    except:
                        pass
                #Append the data to the empty list of the i'th column
                col[i][1].append(data)
                #Increment i for the next column
                i+=1
        [len(C) for (title,C) in col]
        Dict={title:column for (title,column) in col}   
        df=pd.DataFrame(Dict)
        if s == 'Statistics':
            df = df[df.columns[::-1]]
        content = []
        div_elements = doc.xpath('//div[@class="Pt(10px) smartphone_Pt(20px) Lh(1.7)"]//text()')
        section_elements_1 = doc.xpath('//section[@class="quote-sub-section Mt(30px)"]//text()')
        section_elements_2 = doc.xpath('//section[@class="Mt(30px) corporate-governance-container"]//text()')
        content.append(",".join(div_elements))
        content.append(",".join(section_elements_1))
        content.append(",".join(section_elements_2))
        content = {'Content': content}

        urls = financial.format(stock=stock)
        pages = requests.get(urls)
        #Store the contents of the website under doc
        docs = lh.fromstring(pages.content)
        div_elements_hea = docs.xpath('//div[@class="D(tbhg)"]//text()')

        div_elements_content = docs.xpath('//div[@class="D(tbrg)"]//text()')
        a = []
        k=0
        x = len(div_elements_content)
        for i in range(0, x//6):
            a.append([])
            for j in range(0, 6):
                if k == x:
                  break
                a[i].append(div_elements_content[k])
                k += 1
                
        df.to_excel(writer, sheet_name = s, index = False)
        
        urles = chart_comment.format(stock=stock)
        contention = requests.get(urles)
        #Store the contents of the website under doc
        document = lh.fromstring(contention.content)
        #Parse data that are stored between <tr>..</tr> of HTML
        doc_content = document.xpath('//li[@class="js-stream-content Pos(r)"]')
        r = []
        for i in doc_content:
            r.append(i.text_content().split('\n'))
        df=pd.DataFrame(r)
        df.to_excel(writer, sheet_name = 'Chart_Comments', index = False)
        if s == 'Profile' :
            df=pd.DataFrame(content)
            df.to_excel(writer, sheet_name = 'Profile',startrow = 7, startcol = 0, index = False)
        
        df=pd.DataFrame(a,columns=div_elements_hea)
        df.to_excel(writer, sheet_name = 'Financials', index = False)    
            
        writer.save()