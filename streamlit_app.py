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
            return '非YT'
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
    
    @staticmethod
    def GetSubscribtion(url):
        if url.find('www.youtube.com')==-1:
            return '非YT'
        Got=(requests.get(url))
        bs=BeautifulSoup(Got.text,"html5lib")

        for i in (bs.find_all('script')):
            index=str(i).find('var ytInitialData')
            if index!=-1:
                S=str(i).rstrip(';</script>').replace('true','True').replace('false','False')
                var=((S[(index)+20:]))
                try:
                    count=(ast.literal_eval(var))["header"]["pageHeaderRenderer"]["content"]["pageHeaderViewModel"]["metadata"]["contentMetadataViewModel"]["metadataRows"][1]["metadataParts"][0]["text"]["content"]
                    return count
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
    def UpdateData(view_count_list:list, data=[]):
        if not view_count_list: return data
        for index,view_count in enumerate(view_count_list):
            view_count_list[index] = re.sub(r"[^0-9]", "", view_count)
        new_data=[]
        for view_count in view_count_list:
            new_data.append(DataHandler.GetTime())
            new_data.append(view_count)
        data.append(new_data)
        return data
    
    @staticmethod
    def UpdateDataForSub(view_count_list:list, data=[]):
        if not view_count_list: return data
        # for index,view_count in enumerate(view_count_list):
        #     view_count_list[index] = re.sub(r"[^0-9]", "", view_count)
        new_data=[]
        for view_count in view_count_list:
            new_data.append(DataHandler.GetTime())
            new_data.append(view_count)
        data.append(new_data)
        return data
    
    @staticmethod
    def UpdateUrlData(url:list,data=[]):
        a_list=[]
        for i in url:
            a_list.append('URL')
            a_list.append(i)
        data.append(a_list)
        return data

class BackgroundSessionState:

    def init_session_state(self):
        for key, default in {
            "change": False,
            "disable": False,
            "msg": '',
            "ta": '',
            "inside": None,
            "choice": "網站使用說明",
            'url_cheak':False
            }.items():
            if key not in st.session_state: st.session_state[key] = default

    def Change(self):
        st.session_state['change']= True
        st.session_state['disable']=False
        st.session_state['url_cheak']=False
        for i in ['inside']: st.session_state[i]=None
    def Disable(self):
        st.session_state.disable=True
    def Clear(self):
        for i in ['ta']: st.session_state[i] = ''
        for i in ['change']: st.session_state[i] = False
        st.session_state['url_cheak']=False
    def Relode(self):
        for i in ['change','disable']: st.session_state[i] = False
        for i in ['msg','ta']: st.session_state[i] = ''
        for i in ['inside']: st.session_state[i]=None
        st.session_state['url_cheak']=False
    def Disc(self):
        st.session_state['choice']='網站使用說明'

    def UpData(self,data):
        if data: st.session_state['inside']=data


class StreaamlitFuntion:
    def GetUrlList(self,data:list):
        return data[0]
    
    def DealChartData(self,data:list):
        chart_data=[]
        for list_data in data[1:]:
            len_list_data,len_chart_data=int(len(list_data)/2),len(chart_data)
            if (len_chart_data<len_list_data): 
                for i in range(len_list_data-len_chart_data): chart_data.append([]) 
            for index,value in enumerate((list_data)):
                if (index%2==0):
                    data=[pd.to_datetime(value),int(list_data[index+1])]
                    chart_data[int(index/2)].append(data)
        return chart_data

    def DisplayTable(self,data,container=None):
        if container:
            popover=container.popover("展示數據表格",use_container_width=True,icon=':material/description:')
            popover.table(data=data)
        else:
            popover=st.popover("展示數據表格",use_container_width=True,icon=':material/description:')
            popover.table(data=data)
##############修
    def DisplayChart(self,data:list):
        chart_data=self.DealChartData(data)
        
        df=pd.DataFrame({
            'col1':[data[0]  for one_video in chart_data for data in one_video],
            'col2':[data[1]  for one_video in chart_data for data in one_video],
            'col3':[str(i) for i in range(len(chart_data)) for j in range(len(chart_data[i]))]
        })

        st.line_chart(data=df,x='col1',y='col2',color='col3',width=700,height=1000,x_label="時間軸",y_label='觀看次數')

class UrlDealer:
    def DealUrlList(self,url:list,urldata=[],newurl=[]):
        for i in url:
            if i.find('http')==-1:urldata.append(i)
            else: newurl.append(i)
        
        new_data=self.UrlCheak(urldata)
        if new_data is None:new_data=[]
        return newurl+new_data

    def UrlCheak(self,url:list):
        if not url: return None
        df=pd.DataFrame([{'change':i,'changed':f'https://{i}','cheak_box':True} for i in url])
        edited_df=st.data_editor(
            df,
            column_config={
                'change':'未包含[https://]，無法執行',
                'changed':'更改後',
                'cheak_box':'請勾選要更改的項目(未勾選的選項將自動刪除)'},
        disabled=["change", "changed"],
        hide_index=True
        )
        
        true_indices = edited_df[edited_df['cheak_box']]
        true_indices=true_indices['changed'].tolist()

        return true_indices

    def DealViewCountError(self,url):
        view_count_list=[Scraper.GetView(i) for i in url]
        for index,value in enumerate(view_count_list):
            if value == '非YT' or value=='解析錯誤' or value is None:
                if value == '非YT': st.write(f"{url[index]}不是 YouTube 影片網址，自動刪除")
                elif value=='解析錯誤' or value is None: st.write(f'{url[index]}解析錯誤，自動刪除')
                url.remove(url[index])
                view_count_list.remove(value)
        return url,view_count_list
    
    def DealSubCountError(self,url):
        view_count_list=[Scraper.GetSubscribtion(i) for i in url]
        for index,value in enumerate(view_count_list):
            if value == '非YT' or value=='解析錯誤' or value is None:
                if value == '非YT': st.write(f"{url[index]}不是 YouTube 影片網址，自動刪除")
                elif value=='解析錯誤' or value is None: st.write(f'{url[index]}解析錯誤，自動刪除')
                url.remove(url[index])
                view_count_list.remove(value)
        return url,view_count_list


class StreamlitApp(BackgroundSessionState,UrlDealer,StreaamlitFuntion):
    def __init__(self):
        self.init_session_state()


    def DisplayResult(self,view_count,url,file_name="數據",existing_data=None,mode=None):
        c1,c2,c3=st.columns([1,1,1], vertical_alignment="bottom",gap='small')
        #######################待更
        #c1.link_button("前往網站",url=url,icon=":material/open_in_new:",use_container_width=True)
        if mode=="UP":
            updated_data=DataHandler.UpdateData(view_count_list=view_count,data=existing_data.copy())
            self.UpData(updated_data.copy())
            csv_data = DataHandler.SaveCSV(updated_data)
            c2.download_button("下載 CSV", file_name=f"{file_name}.csv", data=csv_data, mime="text/csv", icon=":material/download:", use_container_width=True)
            self.DisplayTable(updated_data, c3)
            self.DisplayChart(updated_data)
        elif mode=="FV":  
            data=DataHandler.UpdateUrlData(url)
            data=DataHandler.UpdateData(view_count,data=data)
            csv_data = DataHandler.SaveCSV(data)
            c2.download_button("下載 CSV", file_name=f"{file_name}.csv", data=csv_data, mime="text/csv", icon=":material/download:", use_container_width=True,type='primary')

        elif mode=="FS":
            data=DataHandler.UpdateUrlData(url)
            data=DataHandler.UpdateDataForSub(view_count,data=data)
            csv_data = DataHandler.SaveCSV(data)
            c2.download_button("下載 CSV", file_name=f"{file_name}.csv", data=csv_data, mime="text/csv", icon=":material/download:", use_container_width=True,type='primary')

        else: st.write("錯誤模式選項")

    def FirstUse(self):
        c1,c2=st.columns(2)
        c1.subheader("初次使用")
        c2.button("不知道怎麼使用?點擊觀看說明",on_click=self.Disc)
        text=st.text_area("輸入YT影片網址",value='',height=68, max_chars=None, key='ta', help="請包涵http或https，若需要多個影片請用[;]區隔", on_change=self.Change, args=None, kwargs=None, placeholder="請輸入網址，若需要多個影片，請中間使用[;](分號)分隔", disabled=False, label_visibility="visible")
        st.button("清除",on_click=self.Clear,icon=":material/delete:")
        if st.session_state.change:
            try:
                url=text.split(";")
                url=dict.fromkeys(url)
                url=[i for i in url if i !='']
#                print(f'URL:{url}')
                url=self.DealUrlList(url)
                if st.button('確認選擇',icon=":material/done_outline:",on_click=self.Disable):
                    
                    url,view_count_list=self.DealViewCountError(url)
                    if view_count_list : self.DisplayResult(view_count_list,url,mode="FV")
                    else:st.write("無資料")
            except:st.write("未知錯誤")
    
    def UpdateData(self): 
        c1,c2=st.columns(2)
        c1.subheader("資料更新")
        c2.button("不知道怎麼使用?點擊觀看說明",on_click=self.Disc)
        uploaded_file=st.file_uploader("上傳你上次的CSV",type=['csv'],help='初次使用請切換模式',key='',on_change=self.Change)
        if st.session_state.change and uploaded_file:
            try:
                data = DataHandler.ReadCsv(uploaded_file)
            except: print("無法讀取檔案")
            if st.button('更新資料',type='primary',icon=":material/refresh:"):
                try:
                    list_data=st.session_state.inside if st.session_state.inside else data
                
                    url=[i for i in self.GetUrlList(list_data) if (i !='URL')] #
                    view_count_list=[Scraper.GetView(i) for i in url]
    ##################
                    if view_count_list : self.DisplayResult(view_count_list,url,existing_data=list_data,mode="UP")
                except: st.write("未知錯誤")
    
    def Description(self):
        st.markdown("""
                    **這是一個app幫你抓取YT影片觀看次數並以表格和圖表呈現。**\n
                    若首次使用，請選擇**初次使用模式**:\n
                    :material/star_rate: :violet[貼上連結後輸入(ctrl+enter)，即可下載一份CSV檔案並自動包含第一份數據，若需要多個影片請用分號區隔]\n
                    若希望獲得更多數據與表格，請至**資料更新模式**:\n
                    :material/star_rate: :violet[上傳CSV檔案後即可點擊更新資料]
                    """)
        
    def FirstUseChannel(self):
        c1,c2=st.columns(2)
        c1.subheader("初次使用_頻道模式")
        c2.button("不知道怎麼使用?點擊觀看說明",on_click=self.Disc)
        text=st.text_area("輸入YT頻道",value='',height=68, max_chars=None, key='ta', help="請包涵http或https，若需要多個頻道請用[;]區隔", on_change=self.Change, args=None, kwargs=None, placeholder="請輸入網址，若需要多個頻道，請中間使用[;](分號)分隔", disabled=False, label_visibility="visible")
        st.button("清除",on_click=self.Clear,icon=":material/delete:")
        if st.session_state.change:
            try:
                url=text.split(";")
                url=dict.fromkeys(url)
                url=[i for i in url if i !='']
#                print(f'URL:{url}')
                url=self.DealUrlList(url)
                if st.button('確認選擇',icon=":material/done_outline:",on_click=self.Disable):
                    
                    url,sub_count_list=self.DealSubCountError(url)
                    if sub_count_list : self.DisplayResult(sub_count_list,url,mode="FS")
                    else:st.write("無資料")
            except:st.write("未知錯誤")





    
    def run(self):
        mode=st.pills("模式選擇",['資料更新','初次使用','網站使用說明'],selection_mode="single",on_change=self.Relode,key='choice')
        if mode=='資料更新':
            self.UpdateData()
        elif mode=='初次使用':
            self.FirstUse()
        elif mode=='網站使用說明':
            self.Description()
        # elif mode=='頻道模式初次':
        #     self.FirstUseChannel()

app=StreamlitApp()
app.run()




    