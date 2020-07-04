import pandas as pd
import streamlit as st
import pydeck as pdk
from random import choice
import altair as alt
import math

from cabecalho import criar_cabelho
from grafico import customizacao_grafico

# define o tema dos graficos Altair
alt.themes.register('grafico', customizacao_grafico)
alt.themes.enable('grafico')

# carrega os datasets de presidente e governador
escola_por_presidente = pd.read_csv(
    'datasets/presidente_por_turno_escola.csv', encoding='latin1', index_col=[0, 1, 2])
escola_por_governador = pd.read_csv(
    'datasets/governador_por_turno_escola.csv', encoding='latin1', index_col=[0, 1, 2])
presidente_por_escola = pd.read_csv(
    'datasets/escola_por_turno_presidente.csv', encoding='latin1', index_col=[0, 1, 2])
governador_por_escola = pd.read_csv(
    'datasets/escola_por_turno_governador.csv', encoding='latin1', index_col=[0, 1, 2])

st.sidebar.image(image='codenation.png', use_column_width=True, format='PNG')
# o turno e o tipo de analise eh feita no sidebar
tipo_analise = st.sidebar.selectbox(
    'Cargo de análise',
    options=(0, 1),
    format_func=lambda o: 'Presidência' if o == 0 else 'Governo de SP')

turno = st.sidebar.selectbox(
    'Turno da eleição',
    options=(1, 2),
    format_func=lambda o: 'Primeiro' if o == 1 else 'Segundo')

# carrega o dataset de acordo com o tipo de analise
votacao_escola = escola_por_presidente if tipo_analise == 0 else escola_por_governador
votacao_candidato = presidente_por_escola if tipo_analise == 0 else governador_por_escola
# prepara a coluna qtd_votos + percentual
for df in [votacao_escola, votacao_candidato]:
    df['str_votos'] = df.apply(lambda row: '{} ({:.2f}%)'.format(
        row['voto_qtd'].astype(int), row['percentual_votos']), axis=1)

criar_cabelho()

# resumo dos eleitores
st.markdown('___')
resumo_eleitores = pd.read_csv('datasets/resumo_eleitores.csv', encoding='latin1', index_col=0)
st.markdown('### **{}** eleitores estavam aptos para votar no {}º turno das eleições de 2018'.format(
    resumo_eleitores.loc[turno]['eleitores_aptos'], turno))
st.markdown('mas **{:d}** não compareceram. Portanto, **{:d}** participaram das eleições.'.format(
    resumo_eleitores.loc[turno]['eleitores_faltaram'], resumo_eleitores.loc[turno]['eleitores_compareceram']))
st.markdown('Total de votos em branco: **{}**'.format(votacao_candidato.loc[1, 'Branco']['voto_qtd'].sum()))
st.markdown('Total de votos nulos: **{}**'.format(votacao_candidato.loc[1, 'Nulo']['voto_qtd'].sum()))
st.markdown('___')

def plotar_grafico(df, coluna_analise: str, indices: tuple):
    source = df[['percentual_votos', 'str_votos']].loc[indices].sort_values(
        by='percentual_votos', ascending=False).reset_index()
    grafico = alt.Chart(
        source,
    ).mark_bar().encode(
        x=alt.Y('percentual_votos', title=r'% de votos'),
        y=alt.X(coluna_analise, sort='-x', title='')
    )
    texto = grafico.mark_text(
        align='left',
        baseline='middle',
        dx=3
    ).encode(text='str_votos')
    figura = grafico + texto
    st.altair_chart(figura, use_container_width=True)

# votacao por presidente
st.markdown('## :man: Votos por candidato')
# calcula a quantidade de votos por candidato para mostrar na combo
candidatos_disponiveis = votacao_candidato.loc[turno].groupby(
    level=0)['voto_qtd'].sum().sort_values(ascending=False)
candidato = st.selectbox(
    options=candidatos_disponiveis.index.to_list(), label='',
    format_func=lambda c: '{} ({} votos)'.format(c, candidatos_disponiveis[c]))
# total de votos do candidato
total = votacao_candidato.loc[turno, candidato]['voto_qtd'].sum()
st.markdown(f'** O candidato {candidato} teve {total} votos **')
# votacao por candidato/escola para o mapa
escolas = pd.read_csv('datasets/escolas.csv', encoding='latin1', index_col=0)
votacao_lat_lon = pd.DataFrame.join(votacao_candidato.loc[turno, candidato], escolas).reset_index()
# Com a normalizacao, da impressao que a quantidade de votos eh a mesma...
# maximo, minimo = votacao_lat_lon["voto_qtd"].max(), votacao_lat_lon["voto_qtd"].min()
# votacao_lat_lon["voto_qtd_normalizado"] = (((votacao_lat_lon["voto_qtd"] - minimo) / (maximo - minimo)) + 1) * 20
# Calcula a raiz quadrada dos votos para mostrar no grafico
votacao_lat_lon["voto_qtd_normalizado"] = votacao_lat_lon["voto_qtd"].apply(lambda x: math.sqrt(x) * 2)
if candidato:
    # plota o mapa com as escolas
    # cores aleatorias
    cores = [[230, 80, 80], [80, 80, 230], [80, 230, 80], [230, 190, 80], [160, 50, 190]]
    pontos = pdk.Layer(
        "ScatterplotLayer",
        votacao_lat_lon,
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=6,
        radius_min_pixels=1,
        radius_max_pixels=100,
        line_width_min_pixels=1,
        get_position=['lon', 'lat'],
        get_radius="voto_qtd_normalizado",
        get_fill_color=choice(cores),
        get_line_color=[0, 0, 0],
    )
    mapa = pdk.ViewState(
        latitude=-20.226723, longitude=-50.275769,
        zoom=10, bearing=0, pitch=0)
    st.markdown('O tamanho dos pontos no mapa de Fernandópolis determina a quantidade de votos do candidato:')
    st.pydeck_chart(
        pdk.Deck(
            layers=[pontos],
            initial_view_state=mapa,
            tooltip={"text": "{escola}\n{voto_qtd} votos"})
    )
    # plota o grafico com os votos
    st.markdown('___')
    st.markdown(f'Divisão dos votos de {candidato} entre as escolas:')
    plotar_grafico(votacao_candidato, 'escola', (turno, candidato))

# votacao por escola
st.markdown('### :house: Votos por escola')
# calcula a quantidade de votos por escola para mostrar na combo
escolas_disponiveis = votacao_escola.loc[turno].groupby(
    level=0)['voto_qtd'].sum().sort_values(ascending=False)
escola = st.selectbox(
    options=escolas_disponiveis.index.to_list(), label='',
    format_func=lambda e: '{} ({} votos)'.format(e, escolas_disponiveis[e]))
if escola:
    st.markdown(f'Divisão dos votos na escola {escola}:')
    plotar_grafico(votacao_escola, 'voto_nome', (turno, escola))
