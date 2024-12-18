import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objs as go

data = []

def choose_city(data):
    st.header("Шаг 2: Выбор города")
    try:
        citites = data['city'].unique()
        city = st.selectbox("Выберите город", citites)
        return city
    except Exception as e:
        print("Exception (find):", e)
        return

def input_key(city):
    st.header("Шаг 3: Ввод ключа")
    key = st.text_input("Введите ключ")
    if key:
        try:
            res_wether = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&APPID={key}")
            data_temp = res_wether.json()
            return data_temp['main']['temp']
        except Exception as e: 
            st.write({"cod":401, "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."})
            return

def describe_data(city):
    if st.checkbox("Показать описательные статистики"):
        st.write(data[data['city']==city].describe())

def analyze_data(city, key):
    df = data[data["city"]==city].reset_index(drop=True).copy()
    df["rolling_mean"] = df.set_index('timestamp')['temperature'].rolling(window='30D', min_periods=1).mean().reset_index(drop=True)
    df['mean_temperature'] = df.groupby(['city', 'season'])['temperature'].transform(lambda x: x.mean())
    df['std_temperature'] = df.groupby(['city', 'season'])['temperature'].transform(lambda x: x.std())
    df['anomaly'] = df.apply(lambda x: True if(x["temperature"]>2*x['std_temperature']) | (x["temperature"]<-2*x['std_temperature']) else False, axis=1)
    season = get_season()
    std_now = data[data["city"]=="Moscow"].groupby(['season'])['temperature'].apply(lambda x: x.std()).loc[season]
    st.write(f"Сейчас в {city} {key} градусов")
    if key<=std_now*2 and key>=-std_now*2:
        st.write("Данная температура нормальная для данного сезона")
    else:
        st.write(f"Данная температура аномальная для данного сезона, так как обычно температура в это время года от {(-std_now*2):.2f} до {(std_now*2):.2f}")
    graph(df)

def get_season():
    month = datetime.now().month
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "autumn"

def graph(df):
    df_anomaly = df[df['anomaly']==True]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature'], name="Температура из исторической справки"))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['rolling_mean'], name="Скользящее среднеее температуры"))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['mean_temperature'], name="Средняя температура за сезон"))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['std_temperature']*2, name="2σ"))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=-df['std_temperature']*2, name="-2σ"))
    fig.add_trace(go.Scatter(x=df_anomaly['timestamp'], y=df_anomaly['temperature'], mode='markers', marker=dict(size=4, symbol='circle'),name="Аномальные значения температуры"))
    fig.update_layout(
        legend_orientation="h",
        title={
            'text' : "Температура и скользящее среднее температуры с интервалом ±2σ",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Дата",
        yaxis_title="Температура",
        margin=dict(l=0, r=0, t=100, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)

citites = []
st.title("Анализ данных с использованием Streamlit")

st.header("Загрузка исторических данных")

uploaded_file = st.file_uploader("Выберите CSV-файл", type=["csv"])
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    data["timestamp"] = pd.to_datetime(data['timestamp'], format='%Y-%m-%d')
    st.write("Превью данных:")
    st.dataframe(data)
    city = choose_city(data)
    key = input_key(city)
    describe_data(city)
    if key:
        st.write("Температура и скользящее среднее температуры с интервалом ±2σ")
        analyze_data(city, key)
else:
    st.write("Пожалуйста, загрузите CSV-файл.")

