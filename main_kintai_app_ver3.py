from datetime import datetime
import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import time
from glob import glob
#import datetime

st.title('勤怠表')

st.sidebar.write('勤務時間入力')

with st.sidebar.form(key='kintai_form',clear_on_submit=False):

    #入力項目----------------------------------------------------------------------------
    #勤務日を入力（勤務日から曜日を算出）
    kinmu_date = st.date_input('勤務日を入力して下さい')
    youbi = kinmu_date.weekday()
    #出勤時間を入力
    start_time = st.text_input('出勤時間を入力して下さい(7時30分だったら7:30)')
    #退勤時間を入力
    finish_time = st.text_input('退勤時間を入力して下さい(12時30分だったら12:30)')
    #集計したい開始日を入力
    start_date = st.date_input('表示　or 集計したい開始日を選択して下さい')
    #集計したい終了日を入力
    finish_date = st.date_input('表示　or 集計したい終了日を選択して下さい')

    col1,col2 = st.columns(2)
    with col1:
        btn_touroku = st.form_submit_button('登録')
        btn_hyouji = st.form_submit_button('表示')
    with col2:
        btn_hyouji_shitei = st.form_submit_button('日時指定表示')
        btn_result_shitei = st.form_submit_button('日時指定結果')

    btn_cancel = st.form_submit_button('キャンセル')
 
if btn_touroku:
    fmt='%H:%M'
    kinmu_mae = datetime.strptime(start_time,fmt)
    kinmu_go = datetime.strptime(finish_time,fmt)
    kinmu_time = kinmu_go - kinmu_mae
    kinmu_time_sec=kinmu_time.seconds
    kinmu_time_hour=round(kinmu_time_sec/3600,2)
    kinmu_time_str = str(kinmu_time_hour)
    #入力項目に対し計算
    import jpholiday

    if youbi == 5 or youbi == 6 or jpholiday.is_holiday(kinmu_date):
        jikyu = 1050                #時給
        kansan = kinmu_time.seconds #秒に換算
        kyuuyo = round(kansan/60/60*jikyu)
        kyuuyo_str = str(kyuuyo)
    else:
        jikyu = 1000                #時給
        kansan = kinmu_time.seconds #秒に換算
        kyuuyo = round(kansan/60/60*jikyu)
        kyuuyo_str = str(kyuuyo)
    #データ読み込み
    df = pd.read_csv('kintai_mari_ver2.csv',parse_dates=['日付'])
    df.loc[df['日付'] == kinmu_date.strftime("%Y-%m-%d"),'出勤時間']=start_time
    df.loc[df['日付'] == kinmu_date.strftime("%Y-%m-%d"),'退勤時間']=finish_time
    df.loc[df['日付'] == kinmu_date.strftime("%Y-%m-%d"),'勤務時間']=kinmu_time_str
    df.loc[df['日付'] == kinmu_date.strftime("%Y-%m-%d"),'給与']=kyuuyo_str
    #タイプ変換
    df['給与']=df['給与'].astype(float)
    df['給与']=df['給与'].round()
    df = df.fillna(0)
    df['勤務時間']=df['勤務時間'].astype(float)
    df['時']=df['勤務時間'].astype('int')
    df['分']=round((df['勤務時間']-df['時'])*60,0)
    df['分']=round(df['分'],0)
    df=df[['日付','曜日', '出勤時間', '退勤時間', '勤務時間', '時', '分', '給与']]
    df.to_csv('kintai_mari_ver2.csv',index=False,encoding='utf_8_sig')
    st.dataframe(df) 

if btn_hyouji:
    df = pd.read_csv('kintai_mari_ver2.csv',parse_dates=['日付'])
    df['日付']=pd.to_datetime(df['日付'],format='%Y-%m-%d')
    df['勤務時間']=df['勤務時間'].astype(float)
    df = df.fillna(0)
    df=df.set_index('日付')
    df['時']=df['勤務時間'].astype('int')
    df['分']=round((df['勤務時間']-df['時'])*60,0)
    df['分']=round(df['分'],0)
    df=df[['曜日', '出勤時間', '退勤時間', '勤務時間', '時', '分', '給与']]
    year = kinmu_date.year
    month = kinmu_date.month
    d=str(year)+'-'+str(month)
    df_hyouji=df[d]
    st.dataframe(df_hyouji) 

if btn_hyouji_shitei:
    df = pd.read_csv('kintai_mari_ver2.csv',parse_dates=['日付'])
    df['日付']=pd.to_datetime(df['日付'],format='%Y-%m-%d')
    df['勤務時間']=df['勤務時間'].astype(float)
    df=df.set_index('日付')
    df = df.fillna(0)
    df['時']=df['勤務時間'].astype('int')
    df['分']=round((df['勤務時間']-df['時'])*60,0)
    df['分']=round(df['分'],0)
    df=df[['曜日', '出勤時間', '退勤時間', '勤務時間', '時', '分', '給与']]
    fmt_2='%Y-%m-%d'
    kaishi_date = start_date.strftime(fmt_2)
    shuryou_date = finish_date.strftime(fmt_2)
    df_hyouji_shitei=df[kaishi_date:shuryou_date]
    st.dataframe(df_hyouji_shitei)

if btn_result_shitei:
    df = pd.read_csv('kintai_mari_ver2.csv',parse_dates=['日付'])
    df['日付']=pd.to_datetime(df['日付'],format='%Y-%m-%d')
    df=df.set_index('日付')
    df=df[['勤務時間']]
    fmt_2='%Y-%m-%d'
    kaishi_date = start_date.strftime(fmt_2)
    shuryou_date = finish_date.strftime(fmt_2)
    df_result_shitei=df[kaishi_date:shuryou_date].sum()
    df_result_shitei_ji=df_result_shitei.astype(int)
    df_result_shitei_fun=round((df_result_shitei-df_result_shitei_ji)*60,0)
    df_result_shitei_fun=df_result_shitei_fun.astype(int)
    start_date,'から',finish_date,'までの合計勤務時間は、:',df_result_shitei,'時間です。'
    start_date,'から',finish_date,'までの合計勤務時間は、：',df_result_shitei_ji,'時間',df_result_shitei_fun,'分です。'
    
    df = pd.read_csv('kintai_mari_ver2.csv',parse_dates=['日付'])
    df['日付']=pd.to_datetime(df['日付'],format='%Y-%m-%d')
    df=df.set_index('日付')
    df=df[['給与']]
    fmt_2='%Y-%m-%d'
    kaishi_date = start_date.strftime(fmt_2)
    shuryou_date = finish_date.strftime(fmt_2)
    df_kyuuyo_shitei=df[kaishi_date:shuryou_date].sum()
    df_kyuuyo_shitei=df_kyuuyo_shitei.astype(int)
    start_date,'から',finish_date,'までの給与合計は、:',df_kyuuyo_shitei,'円です。'

