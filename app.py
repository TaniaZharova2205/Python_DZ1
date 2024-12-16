import streamlit as st
import pandas as pd
import requests

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
    if st.checkbox("Показать описательную статистику"):
        st.write(data[data['city']==city].describe())

citites = []
st.title("Анализ данных с использованием Streamlit")

st.header("Загрузка исторических данных")

uploaded_file = st.file_uploader("Выберите CSV-файл", type=["csv"])
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.write("Превью данных:")
    st.dataframe(data)
    city = choose_city(data)
    key = input_key(city)
    describe_data(city)
    if key:
        pass
else:
    st.write("Пожалуйста, загрузите CSV-файл.")

