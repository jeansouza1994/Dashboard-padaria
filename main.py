import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

#conecta ao banco de dados SQLite
conn = sqlite3.connect("notas_fiscais.db")

#query SQL para obter todos os dados da nota fiscal
query = """
SELECT
    id_nfe,
    numero_nf,
    data_emissao,
    valor_nf,
    item_descricao,
    item_valor_total,
    item_quantidade,
    item_valor_unit,
    item_codigo,
    strftime('%Y', data_emissao) AS ano,
    strftime('%m', data_emissao) AS mes,
    strftime('%d', data_emissao) AS dia,
    tipo_pagamento
FROM notas
WHERE data_emissao IS NOT NULL
"""
df = pd.read_sql(query, conn)
conn.close()

# converte colunas do dataFrame para tipos melhores de se manipular
df['data_emissao'] = pd.to_datetime(df['data_emissao'])
df['ano'] = df['ano'].astype(int)
df['mes'] = df['mes'].astype(int)
df['dia'] = df['dia'].astype(int)

# início da configuração Streamlit
st.title("Dashboard NF-e")

# gráfico 1 - Vendas Totais ao Longo do Tempo(anos e meses)
st.subheader("Vendas Totais ao Longo do Tempo")

df_vendas_mes = (
    df.groupby(["ano", "mes"])["valor_nf"]
    .sum()
    .reset_index()
    .sort_values(["ano", "mes"])
)

df_vendas_mes["data"] = pd.to_datetime(
    df_vendas_mes["ano"].astype(str) + "-" +
    df_vendas_mes["mes"].astype(str).str.zfill(2) + "-01"
)


# muda o dataframe para incluir nomes dos meses em português
meses_pt = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
]

df_vendas_mes["mes_pt"] = df_vendas_mes["mes"].apply(lambda m: meses_pt[m - 1])
df_vendas_mes["data_formatada"] = (
    df_vendas_mes["mes_pt"].str.capitalize() + ", " + df_vendas_mes["ano"].astype(str)
)

df_vendas_mes["valor_formatado"] = df_vendas_mes["valor_nf"].apply(
    lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

fig1 = px.line(
    df_vendas_mes,
    x="data",
    y="valor_nf",
    markers=True,
    title="Vendas Totais ao Longo do Tempo",
)

fig1.update_traces(
    hovertemplate=
        "Data: %{customdata[0]}<br>" +
        "Valor vendido: %{customdata[1]}",
    customdata=df_vendas_mes[["data_formatada", "valor_formatado"]]
)

st.plotly_chart(fig1, use_container_width=True)


# gráfico 2 - Top 10 Produtos por ano e mês

st.subheader("Top 10 Produtos por Ano e Mês")

meses_pt = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
]

df["mes_pt"] = df["mes"].apply(lambda m: meses_pt[m - 1].capitalize())

anos_disponiveis = sorted(df["ano"].unique())
ano_filtro = st.selectbox("Selecione o Ano:", anos_disponiveis)

df_ano = df[df["ano"] == ano_filtro]

meses_disponiveis = sorted(df_ano["mes"].unique())
mes_filtro = st.selectbox(
    "Selecione o mês (opcional):",
    [""] + [meses_pt[m - 1].capitalize() for m in meses_disponiveis]
)

if mes_filtro == "":
    df_filtrado = df_ano
    titulo_mes = "Todos os meses"
else:
    numero_mes = meses_pt.index(mes_filtro.lower()) + 1
    df_filtrado = df_ano[df_ano["mes"] == numero_mes]
    titulo_mes = mes_filtro


# gráfico 3 - Top 10 Produtos
df_produtos = (
    df_filtrado.groupby("item_descricao")["item_valor_total"]
    .sum()
    .reset_index()
    .rename(columns={"item_descricao": "Produtos", "item_valor_total": "Valor vendido"})
    .sort_values("Valor vendido", ascending=False)
    .head(10)
)

fig2 = px.bar(
    df_produtos,
    x="Produtos",
    y="Valor vendido",
    title=f"Top 10 Produtos - {titulo_mes}/{ano_filtro}",
)

# formatação para moeda ficar em BRL no hover
fig2.update_traces(
    hovertemplate="Produto: %{x}<br>Valor vendido: R$ %{customdata}"
)

df_produtos["brl"] = df_produtos["Valor vendido"].apply(
    lambda v: f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

fig2.update_traces(customdata=df_produtos["brl"])

fig2.update_yaxes(tickformat=",.2f")

st.plotly_chart(fig2, use_container_width=True)


# gráfico 4 - Top 3 Produtos(grafico de pizza)
df_top3 = df_produtos.head(3).copy()

# formatação para moeda ficar em BRL no hover
def br_currency(v):
    s = f"{v:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"

df_top3["hover_text"] = df_top3["Valor vendido"].apply(br_currency)

fig3 = px.pie(
    df_top3,
    names="Produtos",
    values="Valor vendido",
    title=f"Top 3 Produtos - {titulo_mes}/{ano_filtro}",
)

fig3.update_traces(
    customdata=df_top3[["hover_text"]].values,
    hovertemplate="Produto: %{label}<br>Valor vendido: %{customdata[0]}<extra></extra>"
)

st.plotly_chart(fig3, use_container_width=True)

# gráfico 4 - Vendas por Forma de Pagamento
st.subheader("Vendas por Forma de Pagamento")

formas_pagamento = {
    "01": "Dinheiro",
    "02": "Cheque",
    "03": "Cartão de crédito",
    "04": "Cartão de débito",
    "05": "Crédito Loja",
    "10": "Vale Alimentação",
    "11": "Vale Refeição",
    "12": "Vale Presente",
    "13": "Vale Combustível",
    "99": "Outros"
}

df_filtrado = df_filtrado.copy()
df_filtrado["Forma de pagamento"] = (
    df_filtrado["tipo_pagamento"].astype(str)
    .map(formas_pagamento)
    .fillna("Outro")
)

df_pag = (
    df_filtrado.groupby("Forma de pagamento")["valor_nf"]
    .sum()
    .reset_index()
    .rename(columns={"valor_nf": "Valor vendido"})
    .sort_values("Valor vendido", ascending=False)
)

# formatação para moeda ficar em BRL no hover
def format_brl(x):
    try:
        x = float(x)
    except Exception:
        return "R$ 0,00"
    sign = "-" if x < 0 else ""
    x = abs(x)
    s = f"{x:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sign}R$ {s}"

df_pag["valor_br"] = df_pag["Valor vendido"].apply(format_brl)

fig4 = px.bar(
    df_pag,
    x="Forma de pagamento",
    y="Valor vendido",
    title="Vendas por Forma de Pagamento",
)

fig4.update_traces(
    customdata=df_pag[["valor_br"]].values,
    hovertemplate="Forma: %{x}<br>Valor vendido: %{customdata[0]}<extra></extra>",
)

st.plotly_chart(fig4, use_container_width=True)
