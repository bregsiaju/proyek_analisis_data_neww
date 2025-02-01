import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set_theme(style="dark")

final_df = pd.read_csv("final_data.csv")

datetime_columns = ["dteday"]
final_df.sort_values(by="dteday", inplace=True)
final_df.reset_index(inplace=True)
 
# Convert to datetime
for column in datetime_columns:
    final_df[column] = pd.to_datetime(final_df[column])

# Sidebar
min_date = final_df["dteday"].min()
max_date = final_df["dteday"].max()
seasons = final_df["season"].unique()
weathers = final_df["weathersit"].unique()
 
# Mapping season labels
season_labels = {
    1: "Musim Semi",
    2: "Musim Panas",
    3: "Musim Gugur",
    4: "Musim Dingin"
}

# Mapping weather labels
weather_labels = {
    1: "Cerah",
    2: "Mendung/Kabut",
    3: "Hujan/Bersalju Ringan",
    4: "Hujan/Bersalju Lebat"
}

with st.sidebar:
    st.image("pedalgo.png")
    
    st.subheader("Filter Data")
    start_date, end_date = st.date_input(
        label="Rentang Waktu",min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    season_options = ["Semua"] + [season_labels[s] for s in seasons]
    weather_options = ["Semua"] + [weather_labels[w] for w in weathers]

    selected_season_label = st.selectbox("Musim", season_options)
    selected_weather_label = st.selectbox("Cuaca", weather_options)

# Reverse mapping to get the original values
selected_season = {v: k for k, v in season_labels.items()}.get(selected_season_label, None)
selected_weather = {v: k for k, v in weather_labels.items()}.get(selected_weather_label, None)

main_df = final_df[
    (final_df["dteday"] >= str(start_date)) & 
    (final_df["dteday"] <= str(end_date))
]

if selected_season is not None:
    main_df = main_df[main_df["season"] == selected_season]

if selected_weather is not None:
    main_df = main_df[main_df["weathersit"] == selected_weather]

st.header("PedallGo Dashboard: Bike Sharing Dataset 🚵")

# Daily Orders
daily_orders_df = main_df.groupby("dteday").agg({
    "cnt": ["sum", 'mean'],
    "casual": "sum",
    "registered": "sum",
}).reset_index()

with st.container():
    st.subheader("Penyewaan Harian")

    # Metrics Section
    col1, col2, col3 = st.columns(3)

    with col1:
        total_orders = '{:,}'.format(daily_orders_df[('cnt', 'sum')].sum())
        st.metric("Total Penyewaan Keseluruhan", value=total_orders)
        
        total_orders = round(daily_orders_df[('cnt', 'sum')].mean())
        st.metric("Rata-Rata Jumlah Penyewa Harian", value=total_orders)

    with col2:
        total_casual = '{:,}'.format(daily_orders_df[('casual', 'sum')].sum())
        st.metric("Penyewaan Pengguna Kasual", value=total_casual)

    with col3:
        total_registered = '{:,}'.format(daily_orders_df[('registered', 'sum')].sum())
        st.metric("Penyewaan Pengguna Terdaftar", value=total_registered)


    tab1, tab2 = st.tabs(["Grafik Akumulasi Total", "Grafik Pengguna Kasual VS Pengguna Terdaftar"])
    
    with tab1:
        fig, ax = plt.subplots(figsize=(16, 8))
        ax.plot(
            daily_orders_df["dteday"],
            daily_orders_df["cnt", "sum"],
            marker="o", 
            linewidth=2,
            color="#FA8E20"
        )
        ax.tick_params(axis="y", labelsize=18)
        ax.tick_params(axis="x", labelsize=15)

        st.pyplot(fig)
    
    with tab2:
        fig, ax = plt.subplots(figsize=(16, 8))
        ax.plot(
            daily_orders_df["dteday"],
            daily_orders_df["registered"],
            marker="o", 
            linewidth=2,
            color="#1f77b4",
            label="Pengguna Terdaftar"
        )
        ax.plot(
            daily_orders_df["dteday"],
            daily_orders_df["casual"],
            marker="o", 
            linewidth=2,
            color="#ff7f0e",
            label="Pengguna Kasual"
        )
        ax.tick_params(axis="y", labelsize=18)
        ax.tick_params(axis="x", labelsize=15)
        ax.legend(fontsize=15)
        
        st.pyplot(fig)


# Analisis Penyewaan Per Jam
with st.container():
    st.subheader("Jam-Jam Terfavorit untuk Penyewaan Sepeda")

    hourly_orders_df = main_df.groupby("hr").agg({
        "cnt": "sum",
        "casual": "sum",
        "registered": "sum",
    }).reset_index()

    # Urutkan berdasarkan kolom 'cnt' secara menurun
    hourly_orders_df = hourly_orders_df.sort_values(by="cnt", ascending=False)
    fig, ax = plt.subplots(figsize=(16, 8))

    colors = ['#B4B4B5' if i >= 3 else 'steelblue' for i in range(len(hourly_orders_df))]

    bars = ax.bar(
        hourly_orders_df["hr"],
        hourly_orders_df["cnt"],
        color=colors
    )

    top_3 = hourly_orders_df.head(3)
    for i, bar in enumerate(bars):
        if i < 3:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f'{int(bar.get_height())}',
                ha='center',
                va='bottom',
                fontsize=12,
                color='black'
            )


    ax.tick_params(axis="y", labelsize=18)
    ax.tick_params(axis="x", labelsize=15)

    st.pyplot(fig)

    st.write("Jam-jam terfavorit untuk penyewaan sepeda adalah pukul " + ', '.join(top_3["hr"].astype(str).tolist()))

# Analisis Penyewaan berdasarkan time_category
time_category_df = main_df.groupby("time_category").agg({
    "cnt": "sum",
}).reset_index()

st.subheader("Peringkat Penyewaan Berdasarkan Rentang Waktu")

with st.container():      
    # Urutkan kategori waktu sesuai urutan yang diinginkan
    time_category_df['time_category'] = pd.Categorical(
        time_category_df['time_category'],
        categories=['Malam', 'Siang', 'Pagi', 'Dini Hari'],
        ordered=True
    )

    time_category_df = time_category_df.sort_values('cnt', ascending=True)

    fig, ax = plt.subplots(figsize=(16, 8))

    lastindex = len(time_category_df) - 1
    colors = ['#FA8E20' if i == lastindex else '#B4B4B5' for i in range(len(time_category_df))]

    bars = ax.barh(
        time_category_df["time_category"],
        time_category_df["cnt"],
        color=colors
    )
    ax.tick_params(axis="y", labelsize=18)
    ax.tick_params(axis="x", labelsize=15)
    st.pyplot(fig)

with st.expander("Lihat rentang waktu"):
    st.write(
        """
        - **Pagi**: 06:00 - 12:00
        - **Siang**: 12:00 - 18:00
        - **Malam**: 18:00 - 24:00
        - **Dini Hari**: 00:00 - 06:00
        """
    )

# Analisis Penyewaan berdasarkan hari kerja dan akhir pekan
st.subheader("Perbandingan Penyewaan Pengguna Kasual vs Terdaftar Berdasarkan Hari Kerja dan Akhir Pekan")
df_melted = main_df[['workingday', 'casual', 'registered']].melt(id_vars=['workingday'],
                                                                  var_name='User Type',
                                                                  value_name='Count')

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x='workingday', y='Count', hue='User Type', data=df_melted, palette=['#FA8E20', 'steelblue'], ax=ax)

ax.set_xlabel('Hari Kerja (0 = Libur, 1 = Kerja)')
ax.set_ylabel('Jumlah Penyewaan Rata-rata')

ax.legend(title='Tipe Pengguna')
st.pyplot(fig)

# Analisis Penyewaan berdasarkan musim
st.subheader("Peringkat Penyewaan Berdasarkan Musim")
season_df = main_df.groupby("season").agg({
    "cnt": "sum",
}).reset_index()

season_df['season'] = season_df['season'].map({
    1: "Musim Semi",
    2: "Musim Panas",
    3: "Musim Gugur",
    4: "Musim Dingin"
})

season_df = season_df.sort_values(by="cnt", ascending=False)

fig, ax = plt.subplots(figsize=(16, 8))

colors = ['steelblue' if i == 0 else '#B4B4B5' for i in range(len(season_df))]

bars = ax.bar(
    season_df["season"],
    season_df["cnt"],
    color=colors
)
ax.tick_params(axis="y", labelsize=18)
ax.tick_params(axis="x", labelsize=15)
st.pyplot(fig)

st.caption("Bregsiaju ©️ 2025")