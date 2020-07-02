import pandas as pd
import streamlit as st
import altair as alt

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

# o turno e o tipo de analise eh feita no sidebar
tipo_analise = st.sidebar.selectbox(
    'Cargo de análise',
    options=(0, 1),
    format_func=lambda o: 'Presidencia' if o == 0 else 'Governo de SP')

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
st.markdown('### Havia {} eleitores aptos a votar no {}º turno das eleições de 2018'.format(
    resumo_eleitores.loc[turno]['eleitores_aptos'], turno))
st.markdown('mas **{:d}** não compareceram. Portanto, **{:d}** participaram das eleições.'.format(
    resumo_eleitores.loc[turno]['eleitores_faltaram'], resumo_eleitores.loc[turno]['eleitores_compareceram']))
st.markdown('Total de votos em branco: {}'.format(votacao_candidato.loc[1, 'Branco']['voto_qtd'].sum()))
st.markdown('Total de votos nulos: {}'.format(votacao_candidato.loc[1, 'Nulo']['voto_qtd'].sum()))
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

# votacao por escola
st.markdown('### :house: Percentual de votos por escola')
st.markdown('Mostra o percentual de votos que o candidato deve em um escola.')
# calcula a quantidade de votos por escola para mostrar na combo
escolas_disponiveis = votacao_escola.loc[turno].groupby(
    level=0)['voto_qtd'].sum().sort_values(ascending=False)
escola = st.selectbox(
    options=escolas_disponiveis.index.to_list(), label='Escolha a escola:',
    format_func=lambda e: '{} ({} votos)'.format(e, escolas_disponiveis[e]))
if escola:
    plotar_grafico(votacao_escola, 'voto_nome', (turno, escola))

# votacao por presidente
st.markdown('## :man: Percentual de votos por candidato')
st.markdown('blá blá blá')
# calcula a quantidade de votos por candidato para mostrar na combo
candidatos_disponiveis = votacao_candidato.loc[turno].groupby(
    level=0)['voto_qtd'].sum().sort_values(ascending=False)
candidato = st.selectbox(
    options=candidatos_disponiveis.index.to_list(), label='Escolha o candidato:',
    format_func=lambda c: '{} ({} votos)'.format(c, candidatos_disponiveis[c]))
# total de votos do candidato
total = votacao_candidato.loc[turno, candidato]['voto_qtd'].sum()
st.markdown(f'** O candidato {candidato} teve {total} votos **')
if escola:
    plotar_grafico(votacao_candidato, 'escola', (turno, candidato))
