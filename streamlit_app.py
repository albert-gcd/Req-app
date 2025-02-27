#引入函數庫
import streamlit as st
import requests
from bs4 import BeautifulSoup 
import ast
import csv
import re
from io import StringIO
import io
import pandas as pd
import time
#

class Scraper:
    @staticmethod
    def GetView(url):
        if url.find('www.youtube.com')==-1:
            return -2
        Got=(requests.get(url))
        bs=BeautifulSoup(Got.text,"html5lib")

        for i in (bs.find_all('script')):
            index=str(i).find('var ytInitialData')
            if index!=-1:
                S=str(i).rstrip(';</script>').replace('true','True').replace('false','False')
                var=((S[(index)+20:]))
                try:
                    view_count=(ast.literal_eval(var)["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][0]["videoPrimaryInfoRenderer"]["viewCount"]["videoViewCountRenderer"]["viewCount"]['simpleText'])
                    return view_count
                except:
                    return '解析錯誤'
        return None
#

class DataHandler:
    @staticmethod
    def GetTime():#獲取時間
        t = time.time()
        t1 = time.localtime(t)
        t2 = time.strftime('%Y/%m/%d %H:%M:%S',t1)
        return t2

    @staticmethod
    def ReadCsv(Csv):#閱讀檔案
        Csv=io.TextIOWrapper(Csv,encoding='utf-8')
        reader=csv.reader(Csv)
        return [i for i in reader]

    @staticmethod
    def SaveCSV(data:list):#處存CSV
        Csv2=StringIO('')
        writer=csv.writer(Csv2)
        writer.writerows(data)
        file=Csv2.getvalue()
        Csv2.close()
        return file
    
    @staticmethod
    def UpdateData(view_count:str, data=[], url=None):
        if not view_count: return data
        view_count = re.sub(r"[^0-9]", "", view_count)
        new_data=data
        if url: new_data.append(['Url',url])
        new_data.append([DataHandler.GetTime(), view_count])
        return new_data

class StreamlitApp:
    def __init__(self):
        self.init_session_state()
    
    def init_session_state(self):
        for key, default in {
            "change": False,
            "disable": False,
            "msg": '',
            "ta": '',
            "inside": None,
            "choice": "網站使用說明"
            }.items():
            if key not in st.session_state: st.session_state[key] = default


    def Change(self):
        st.session_state['change']= True
        st.session_state['disable']=False
        for i in ['inside']: st.session_state[i]=None
    def Disable(self):
        st.session_state.disable=True
    def Clear(self):
        for i in ['ta']: st.session_state[i] = ''
        for i in ['change']: st.session_state[i] = False
    def Relode(self):
        for i in ['change','disable']: st.session_state[i] = False
        for i in ['msg','ta']: st.session_state[i] = ''
        for i in ['inside']: st.session_state[i]=None
    def Disc(self):
        st.session_state['choice']='網站使用說明'

    def UpData(self,data):
        if data: st.session_state['inside']=data
    def GetUrl(self,data:list):
        return data[0][1]
    
    def DisplayTable(self,data,container=None):
        if container:
            popover=container.popover("展示數據表格",use_container_width=True,icon=':material/description:')
            popover.table(data=data)

    def DisplayChart(self,data:list):
        chart_data =[[pd.to_datetime(i[0]),int(i[1])] for i in data[1:]]
        df =pd.DataFrame(chart_data ,columns=["date","view"])
        st.line_chart(data=df,x='date',y='view',width=700,height=1000,x_label="時間軸",y_label='觀看次數')
    
    def DisplayResult(self,view_count,url,file_name="數據",existing_data=None):
        c1,c2,c3=st.columns([1,1,1], vertical_alignment="bottom",gap='small')
        c1.link_button("前往網站",url=url,icon=":material/open_in_new:",use_container_width=True)
        if existing_data:
            updated_data=DataHandler.UpdateData(view_count=view_count,data=existing_data.copy())
            self.UpData(updated_data.copy())
            csv_data = DataHandler.SaveCSV(updated_data)
            c2.download_button("下載 CSV", file_name=f"{file_name}.csv", data=csv_data, mime="text/csv", icon=":material/download:", use_container_width=True)
            self.DisplayTable(updated_data, c3)
            self.DisplayChart(updated_data)
        else:
            data=DataHandler.UpdateData(view_count, url=url)
            csv_data = DataHandler.SaveCSV(data)
            c2.download_button("下載 CSV", file_name=f"{file_name}.csv", data=csv_data, mime="text/csv", icon=":material/download:", use_container_width=True,type='primary')

    def FirstUse(self):
        c1,c2=st.columns(2)
        c1.subheader("初次使用")
        c2.button("不知道怎麼使用?點擊觀看說明",on_click=self.Disc)
        text=st.text_area("輸入YT影片網址",value='',height=68, max_chars=None, key='ta', help="請包涵http或https", on_change=self.Change, args=None, kwargs=None, placeholder="請輸入網址", disabled=False, label_visibility="visible")
        st.button("清除",on_click=self.Clear,icon=":material/delete:")
        if st.session_state.change:
            try:
                url=text
                view_count=Scraper.GetView(url)
                if view_count == -2: st.write("這不是 YouTube 影片網址")
                else:self.DisplayResult(view_count,url)
            except requests.exceptions.MissingSchema:
                if not(st.session_state.disable): st.write(f"請問是否為https://{url}")
                c1,c2=st.columns(2)
                c1.button("否",on_click=self.Clear,disabled=st.session_state.disable,use_container_width=True,icon=":material/close:")
                if (c2.button("是",disabled=st.session_state.disable,on_click=self.Disable,use_container_width=True,icon=":material/check:")):
                    try:
                        view_count=Scraper.GetView(f"https://{url}")
                        if view_count==-2: st.write("這不是 YouTube 影片網址")
                        else: self.DisplayResult(view_count)
                    except: st.write("網址錯誤，請重新輸入")
            except:st.write("未知錯誤")
    
    def UpdateData(self):
        c1,c2=st.columns(2)
        c1.subheader("資料更新")
        c2.button("不知道怎麼使用?點擊觀看說明",on_click=self.Disc)
        uploaded_file=st.file_uploader("上傳你上次的CSV",type=['csv'],help='初次使用請切換模式',key='',on_change=self.Change)
        if st.session_state.change and uploaded_file:
            data = DataHandler.ReadCsv(uploaded_file)
            if st.button('更新資料',type='primary',icon=":material/refresh:"):
                list_data=st.session_state.inside if st.session_state.inside else data
                try:
                    url=self.GetUrl(list_data)
                    view_count=Scraper.GetView(url)
                    if view_count==-2: st.write("這不是 YouTube 影片網址")
                    else: self.DisplayResult(view_count,url,existing_data=list_data)
                except: st.write("未知錯誤")
    
    def Description(self):
        st.markdown("""
                    **這是一個app幫你抓取YT影片觀看次數並以表格和圖表呈現。**\n
                    若首次使用，請選擇**初次使用模式**:\n
                    :material/star_rate: :violet[貼上連結後輸入，即可下載一份CSV檔案並自動包含第一份數據]\n
                    若希望獲得更多數據與表格，請至**資料更新模式**:\n
                    :material/star_rate: :violet[上傳CSV檔案後即可點擊更新資料]
                    """)
    def run(self):
        mode=st.pills("模式選擇",['資料更新','初次使用','網站使用說明'],selection_mode="single",on_change=self.Relode,key='choice')
        if mode=='資料更新':
            self.UpdateData()
        elif mode=='初次使用':
            self.FirstUse()
        elif mode=='網站使用說明':
            self.Description()

app=StreamlitApp()
app.run()




    