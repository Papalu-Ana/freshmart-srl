import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

st.set_page_config(
    page_title="FreshMart SRL",
    page_icon="🛒",
    layout="wide"
)

@st.cache_data
def load_data():
    df_produse = pd.read_csv("produse.csv")
    df_clienti = pd.read_csv("clienti.csv")
    df_vanzari = pd.read_csv("vanzari.csv")
    df_produse["valoare_stoc"] = df_produse["pret_unitar"] * df_produse["stoc_initial"]
    df_full = df_vanzari.merge(
        df_produse[["id_produs","nume_produs","categorie","pret_unitar"]],
        on="id_produs", how="left"
    ).merge(
        df_clienti[["id_client","nume","oras","tip_card","puncte_fidelitate"]],
        on="id_client", how="left"
    )
    df_full["valoare_vanzare"] = (
        df_full["pret_unitar"] * df_full["cantitate"] *
        (1 - df_full["discount_procent"] / 100)
    ).round(2)
    return df_produse, df_clienti, df_vanzari, df_full

df_produse, df_clienti, df_vanzari, df_full = load_data()

st.sidebar.title(" FreshMart SRL")
st.sidebar.markdown("**Pachete Software — CSIE Anul III**")
st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Navigare",
    ["Dashboard Vânzări", "Analiza Clienților"]
)
st.sidebar.markdown("---")
st.sidebar.metric("Produse", len(df_produse))
st.sidebar.metric("Clienți", len(df_clienti))
st.sidebar.metric("Tranzacții", len(df_vanzari))

if pagina == "Dashboard Vânzări":
    st.title("Dashboard Vânzări — FreshMart SRL 2024")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Valoare totală", f"{df_full['valoare_vanzare'].sum():,.2f} RON")
    col2.metric("Cantitate totală", f"{df_full['cantitate'].sum():,} unități")
    col3.metric("Nr. tranzacții", len(df_full))
    col4.metric("Val. medie", f"{df_full['valoare_vanzare'].mean():.2f} RON")
    st.markdown("---")
    luni_selectate = st.multiselect(
        "Selectează lunile:",
        options=list(range(1,13)),
        default=list(range(1,13)),
        format_func=lambda x: ["Ian","Feb","Mar","Apr","Mai","Iun","Iul","Aug","Sep","Oct","Nov","Dec"][x-1]
    )
    df_filtrat = df_full[df_full["luna"].isin(luni_selectate)]
    st.markdown("---")
    st.subheader("Vânzări lunare")
    vanzari_lunare = df_filtrat.groupby("luna")["valoare_vanzare"].sum().reindex(range(1,13), fill_value=0)
    luni_ro = ["Ian","Feb","Mar","Apr","Mai","Iun","Iul","Aug","Sep","Oct","Nov","Dec"]
    fig1, ax1 = plt.subplots(figsize=(12,4))
    ax1.bar(luni_ro, vanzari_lunare.values, color="#2E86AB", edgecolor="white")
    ax1.set_title("Vânzări lunare (RON)", fontweight="bold")
    ax1.set_ylabel("Valoare (RON)")
    st.pyplot(fig1)
    plt.close()
    st.markdown("---")
    st.subheader("Structura pe categorii")
    vanzari_cat = df_filtrat.groupby("categorie")["valoare_vanzare"].sum()
    fig2, ax2 = plt.subplots(figsize=(6,5))
    ax2.pie(vanzari_cat.values, labels=vanzari_cat.index, autopct="%1.1f%%", startangle=140)
    ax2.set_title("Ponderea categoriilor", fontweight="bold")
    st.pyplot(fig2)
    plt.close()

elif pagina == "Analiza Clienților":
    st.title("Analiza Clienților — FreshMart SRL")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total clienți", len(df_clienti))
    col2.metric("Gold", len(df_clienti[df_clienti["tip_card"]=="Gold"]))
    col3.metric("Silver", len(df_clienti[df_clienti["tip_card"]=="Silver"]))
    col4.metric("Bronze", len(df_clienti[df_clienti["tip_card"]=="Bronze"]))
    st.markdown("---")
    st.subheader("Distribuția cardurilor")
    card_dist = df_clienti["tip_card"].value_counts()
    fig3, ax3 = plt.subplots(figsize=(5,4))
    ax3.bar(card_dist.index, card_dist.values, color=["#FFD700","#C0C0C0","#CD7F32"], edgecolor="white")
    ax3.set_title("Clienți per tip card", fontweight="bold")
    st.pyplot(fig3)
    plt.close()
    st.markdown("---")
    st.subheader("Clasament clienți")
    df_display = df_clienti[["nume","oras","tip_card","puncte_fidelitate"]].sort_values("puncte_fidelitate", ascending=False)
    st.dataframe(df_display.reset_index(drop=True), use_container_width=True)