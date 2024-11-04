import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Sidebar for page selection
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["RPE", "RPE [Player]"])

if page == "RPE":

    df = pd.read_csv("data_table_looker_upload.csv")

    df.drop(columns = ["Split 1", "Metric"], inplace = True)

    # Deleting Minutesx4 from Practices
    df = df[~((df["Type"] == "Practices") & (df["Metric Clean"] == "minutes4"))]

    df_total_mins = df[((df["Type"] == "Practices") & (df["Metric Clean"] == "minutes")) | ((df["Type"] == "Basketball Game") & (df["Metric Clean"] == "minutes4"))]
    df_total_srpe = df[df["Metric Clean"] == "srpe100"]

    df_total_mins = pd.DataFrame(df_total_mins.groupby(["Player", "Date Range"])["Value"].sum()).reset_index()
    df_total_srpe = pd.DataFrame(df_total_srpe.groupby(["Player", "Date Range"])["Value"].sum()).reset_index()

    df_total_mins["Type"] = "Total"
    df_total_mins["Metric Clean"] = "minutes"

    df_total_srpe["Type"] = "Total"
    df_total_srpe["Metric Clean"] = "srpe100"

    df = pd.concat([df, df_total_srpe, df_total_mins])

    df["sort_arg"] = df["Type"] + " - " + df["Metric Clean"]

    pv = pd.pivot_table(df, index = ["Type", "Metric Clean", "Date Range", "sort_arg"], columns = "Player", values = "Value", aggfunc = "max")
    pv = pv.round(decimals = 0)

    cm = sns.color_palette(palette='RdYlGn_r', as_cmap=True)

    # Dropdown menu to select date range
    date_range_options = np.array(['Last 7d', 'Last 14d', 'Last 28d', 'Total'])
    selected_date_range = st.selectbox("Select Date Range", date_range_options)


    # Filter the DataFrame based on the selected date range
    filtered_df = pv.xs(selected_date_range, level='Date Range')

    # Dropdown for metric selection based on the filtered DataFrame
    metric_options = filtered_df.index.get_level_values(2).unique()  # Unique metrics for the selected date range
    selected_metric = st.selectbox("Select metric to sort by:", metric_options)

    sort_order = st.selectbox("Select sorting order:", options=["DESC", "ASC"], index=0)
    is_descending = sort_order == "ASC"

    name_cols = filtered_df.xs(selected_metric, level = "sort_arg").squeeze(axis = 0).sort_values(ascending = is_descending).index

    sorted_filtered_df = filtered_df.reindex(columns=name_cols)

    sorted_filtered_df = sorted_filtered_df.droplevel('sort_arg')

    sorted_filtered_df = sorted_filtered_df.style.background_gradient(cmap = cm, axis = 1)

    sorted_filtered_df = sorted_filtered_df.round(0)

    # Display the filtered DataFrame
    st.dataframe(sorted_filtered_df)

elif page == "RPE [Player]":
    player_df = pd.read_csv("player_charts_data_looker_upload.csv")

    # Dropdown menu to select player
    player_options = list(player_df["Player"].unique())
    selected_player = st.selectbox("Select Player", player_options)


    # Dropdown menu to select date range
    date_range_options = np.array(['Last 7d', 'Last 14d', 'Last 28d'])
    selected_date_range = st.selectbox("Select Date Range", date_range_options)

    timeframe = selected_date_range.split(" ")[1]
    lst = list(player_df.columns)
    cols = [k for k in lst if timeframe in k]

    basic_columns = ["Player", "date_fix"]

    cols = basic_columns + cols

    player_df = player_df[cols]

    def total_srpe100(player):
        fig, ax = plt.subplots()
        ax.stackplot(player_df[player_df["Player"] == player]["date_fix"],
                      player_df[player_df["Player"] == player]["player_" + timeframe + "_total_srpe_100"],
                      colors=["lightgrey"])

        ax.set_title("TOTAL sRPE/100 (Practice + Games)")

        ax.xaxis.set_major_locator(plt.MaxNLocator(7))
        ax.tick_params(labelrotation=90)

        ax.grid(True, linewidth = 0.5, color = "gray")

        return fig

    def total_min(player):
        fig, ax = plt.subplots()
        ax.stackplot(player_df[player_df["Player"] == player]["date_fix"],
                      player_df[player_df["Player"] == player]["player_" + timeframe + "_total_min"],
                      colors=["lightgrey"])

        ax.set_title("TOTAL MIN (Practice + Games)")

        ax.xaxis.set_major_locator(plt.MaxNLocator(7))
        ax.tick_params(labelrotation=90)

        ax.grid(True, linewidth = 0.5, color = "gray")

        return fig

    def total_srpe100_practice_games(player):
        fig, ax = plt.subplots()
        ax.stackplot(player_df[player_df["Player"] == player]["date_fix"],
                      player_df[player_df["Player"] == player]["player_" + timeframe + "_srpe_100_practice"],
                      player_df[player_df["Player"] == player]["player_" + timeframe + "_srpe_100_game"],
                      labels=["sRPE100 practice", "sRPE100 game"],
                      colors=["lightgrey", "lightcoral"])


        ax.set_title("TOTAL sRPE/100 (Practice + Games)")

        ax.xaxis.set_major_locator(plt.MaxNLocator(7))
        ax.tick_params(labelrotation=90)
        ax.legend(loc="upper left")
        ax.grid(True, linewidth = 0.5, color = "gray")

        return fig

    def total_min_practice_games(player):
        fig, ax = plt.subplots()
        ax.stackplot(player_df[player_df["Player"] == player]["date_fix"],
                      player_df[player_df["Player"] == player]["player_" + timeframe + "_minutes_practice"],
                      player_df[player_df["Player"] == player]["player_" + timeframe + "_minutes_4_game"],
                      labels=["MIN practice", "MIN game"],
                      colors=["lightgrey", "lightcoral"])


        ax.set_title("TOTAL MIN (Practice + Games)")

        ax.xaxis.set_major_locator(plt.MaxNLocator(7))
        ax.tick_params(labelrotation=90)
        ax.legend(loc="upper left")
        ax.grid(True, linewidth = 0.5, color = "gray")

        return fig


    # First row: 2 columns for the first two charts
    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(total_srpe100(selected_player))
    with col2:
        st.pyplot(total_min(selected_player))

    # Second row: 2 columns for the next two charts
    col3, col4 = st.columns(2)
    with col3:
        st.pyplot(total_srpe100_practice_games(selected_player))
    with col4:
        st.pyplot(total_min_practice_games(selected_player))
