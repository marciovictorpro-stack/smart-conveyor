import streamlit as st
import pandas as pd
import random
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Sistema Logístico Inteligente",
    page_icon="🚢",
    layout="wide"
)

# CSS personalizado
st.markdown("""
<style>
.main {
    background-color: #0E1117;
    color: white;
}

.metric-card {
    background-color: #1c1f26;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.5);
}

.section-title {
    font-size:22px;
    font-weight: bold;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚢 Sistema Logístico Inteligente</h1>", unsafe_allow_html=True)



# ---------------- LISTAS BASE ----------------
tipos = ["Container", "Granel", "Perecível", "Químico"]
clientes = ["Maersk", "Evergreen", "ONE"]
origens = ["China", "Brasil", "EUA", "Alemanha"]
destinos = ["Navio A", "Navio B", "Armazém 1", "Armazém 2"]
rotas = ["Rota 1", "Rota 2", "Rota 3"]

# ---------------- FUNÇÕES ----------------
def gerar_carga(id):
    tipo = random.choice(tipos)
    cliente = random.choice(clientes)

    # prioridade por empresa
    if cliente == "Maersk":
        prioridade = "Alta"
    elif cliente == "Evergreen":
        prioridade = random.choice(["Média", "Alta"])
    else:
        prioridade = "Alta"

    # tempo
    tempo = random.randint(5, 15) if tipo == "Perecível" else random.randint(10, 50)

    atraso = random.choice([True, False, False])
    status = "Atrasado" if atraso else "Em processamento"

    return {
        "ID": id,
        "Tipo": tipo,
        "Cliente": cliente,
        "Origem": random.choice(origens),
        "Destino": random.choice(destinos),
        "Prioridade": prioridade,
        "Tempo_Restante": tempo,
        "Status": status,
        "Rota": random.choice(rotas),
        "Timestamp": datetime.now()
    }

def atualizar(df):
    if df.empty:
        return df

    # reduzir tempo das cargas em processamento
    mask = df["Status"] == "Em processamento"
    df.loc[mask, "Tempo_Restante"] -= 1

    # cargas concluídas
    df.loc[df["Tempo_Restante"] <= 0, "Status"] = "Concluído"

    # chance de atraso
    atraso_mask = (df["Status"] == "Em processamento") & (pd.Series([random.random() for _ in range(len(df))]) < 0.03)
    df.loc[atraso_mask, "Status"] = "Atrasado"

    # chance de recuperar atraso
    recupera_mask = (df["Status"] == "Atrasado") & (pd.Series([random.random() for _ in range(len(df))]) < 0.2)
    df.loc[recupera_mask, "Status"] = "Em processamento"

    return df

# ---------------- ESTADO ----------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame([gerar_carga(i) for i in range(10)])
    st.session_state.id_counter = 10

df = st.session_state.df

# ---------------- SIMULAÇÃO ----------------
if random.random() < 0.4:
    nova = gerar_carga(st.session_state.id_counter)
    st.session_state.df = pd.concat([df, pd.DataFrame([nova])], ignore_index=True)
    st.session_state.id_counter += 1

st.session_state.df = atualizar(st.session_state.df)
df = st.session_state.df

# ---------------- KPIs ----------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"<div class='metric-card'>Total<br><h2>{len(df)}</h2></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='metric-card'>Processando<br><h2>{(df['Status']=='Em processamento').sum()}</h2></div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div class='metric-card'>Atrasadas<br><h2>{(df['Status']=='Atrasado').sum()}</h2></div>", unsafe_allow_html=True)

with col4:
    st.markdown(f"<div class='metric-card'>Concluídas<br><h2>{(df['Status']=='Concluído').sum()}</h2></div>", unsafe_allow_html=True)

# ---------------- GRÁFICOS ----------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='section-title'>📦 Cargas por Cliente</div>", unsafe_allow_html=True)
    st.bar_chart(df["Cliente"].value_counts())

with col2:
    st.markdown("<div class='section-title'>📊 Status das Cargas</div>", unsafe_allow_html=True)
    st.bar_chart(df["Status"].value_counts())

# ---------------- INSIGHTS ----------------
st.markdown("<div class='section-title'>🧠 Inteligência Operacional</div>", unsafe_allow_html=True)

if not df.empty:

    atraso_pct = (df["Status"] == "Atrasado").mean() * 100

    # 🔴 BLOCO VISUAL PRINCIPAL
    if atraso_pct > 30:
        cor = "#ff4b4b"
        msg = "🚨 Alto risco operacional"
    elif atraso_pct > 15:
        cor = "#ffa500"
        msg = "⚠️ Atenção ao aumento de atrasos"
    else:
        cor = "#00c853"
        msg = "✅ Operação estável"

    st.markdown(f"""
    <div style='background-color:{cor}; padding:15px; border-radius:10px; text-align:center'>
        <h3>{msg}</h3>
        <p>{atraso_pct:.1f}% das cargas estão atrasadas</p>
    </div>
    """, unsafe_allow_html=True)

    # 📦 CLIENTE TOP
    cliente_top = df["Cliente"].value_counts().idxmax()

    st.markdown(f"""
    <div style='background-color:#1c1f26; padding:15px; border-radius:10px; margin-top:10px;'>
        📦 Maior volume atual: <b>{cliente_top}</b>
    </div>
    """, unsafe_allow_html=True)

    # 🚦 RISCO FUTURO
    media_tempo = df["Tempo_Restante"].mean()

    if media_tempo > 25:
        st.error("🚧 Possível congestionamento logístico")
    else:
        st.success("Fluxo dentro da normalidade")

# ---------------- PREVISÃO ----------------
st.subheader("📈 Previsão de Fluxo")

if not df.empty:

    media_tempo = df["Tempo_Restante"].mean()
    st.metric("Tempo médio estimado", f"{media_tempo:.1f}")

    cargas_ativas = df[df["Status"] == "Em processamento"]

    if len(cargas_ativas) > 20:
        st.warning("🚦 Alto volume → risco de congestionamento")

    if media_tempo > 25:
        st.error("🚨 Forte tendência de atraso sistêmico")
    elif media_tempo > 18:
        st.warning("⚠️ Tendência de aumento no tempo")
    else:
        st.success("✅ Fluxo dentro da normalidade")

# ---------------- GRÁFICO FINAL ----------------
st.subheader("📊 Tempo médio por cliente")

if not df.empty:
    tempo_cliente = df.groupby("Cliente")["Tempo_Restante"].mean()
    st.bar_chart(tempo_cliente)

# ---------------- TABELA ----------------
st.markdown("<div class='section-title'>📋 Monitoramento em Tempo Real</div>", unsafe_allow_html=True)

# selecionar colunas importantes
colunas = ["ID", "Cliente", "Tipo", "Status", "Tempo_Restante", "Rota"]

df_view = df[colunas].sort_values(by="Tempo_Restante", ascending=False)

# função de cor
def cor_status(val):
    if val == "Atrasado":
        return "color: red"
    elif val == "Em processamento":
        return "color: orange"
    else:
        return "color: green"

st.dataframe(
    df_view.head(20),
    use_container_width=True,
    height=300
)

# ---------------- AUTO REFRESH ----------------
st.caption("Atualizando automaticamente...")
st.rerun()