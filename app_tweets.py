
import pandas as pd
import altair as alt
from shiny import ui, input, render
from shinywidgets import render_altair


def load_actual_data():
    all_dfs = []
    
    filename_mensal = "T01VEGAN_NTWEETS_TBL_mm.xlsx"
    filename_anual = "T01VEGAN_NTWEETS_TBL_yyyy.xlsx"

    try:
        df_anual = pd.read_excel(filename_anual)
        # USA a coluna 'created_at' que existe no arquivo
        id_vars_anual = ['created_at'] 
        value_vars_anual = ['total', 'posted', 'retweeted', 'replied'] # Colunas a serem visualizadas

        df_anual_long = pd.melt(df_anual, id_vars=id_vars_anual, value_vars=value_vars_anual, var_name="Tipo_de_Tweet", value_name="Quantidade")
        df_anual_long["Data"] = pd.to_datetime(df_anual_long['created_at'], format='%Y')
        df_anual_long["Periodicidade"] = "Anual"
        all_dfs.append(df_anual_long)
    except Exception as e:
        print(f"Erro ao processar arquivo anual: {e}")

    # --- Processamento do Arquivo Mensal ---
    try:
        df_mensal = pd.read_excel(filename_mensal)
        # USA a coluna 'created_at' que existe no arquivo
        id_vars_mensal = ['created_at'] 
        value_vars_mensal = ['total', 'posted', 'retweeted', 'replied'] # Colunas a serem visualizadas

        df_mensal_long = pd.melt(df_mensal, id_vars=id_vars_mensal, value_vars=value_vars_mensal, var_name="Tipo_de_Tweet", value_name="Quantidade")
        # Extrai o ano e mês da coluna 'created_at' (ex: '2021-02')
        df_mensal_long["Data"] = pd.to_datetime(df_mensal_long['created_at'])
        df_mensal_long["Periodicidade"] = "Mensal"
        all_dfs.append(df_mensal_long)
    except Exception as e:
        print(f"Erro ao processar arquivo mensal: {e}")

    if not all_dfs:
        return pd.DataFrame()

    df_final = pd.concat(all_dfs, ignore_index=True)
    df_final["Tipo_de_Tweet"] = df_final["Tipo_de_Tweet"].astype(str).str.capitalize()
    
    return df_final


df_completo = load_actual_data()

ui.tags.style("body { font-family: sans-serif; }")

with ui.layout_sidebar():
    with ui.sidebar(title="Controles"):
        ui.input_radio_buttons(
            "periodicidade", 
            "Periodicidade", 
            choices={"Anual": "Anual", "Mensal": "Mensal"}, 
            selected="Anual"
        )

    ui.h4("Métrica de Tweets", style="font-weight: bold;")
    ui.p("Fonte: Rede X/Twitter - de 2012 a 2022")

    @render_altair
    def grafico_volume_tweets():
        if df_completo.empty:
            return alt.Chart(pd.DataFrame()).mark_text(text="Dados não encontrados.").encode()

        periodicidade = input.periodicidade()
        df_filtrado = df_completo[df_completo["Periodicidade"] == periodicidade]
        
        formato_eixo_x = "%Y" if periodicidade == "Anual" else "%b %Y"

        chart = alt.Chart(df_filtrado).mark_line().encode(
            x=alt.X("Data:T", title="Tempo", axis=alt.Axis(format=formato_eixo_x, labelAngle=0, grid=False)),
            y=alt.Y("Quantidade:Q", title="Número de Tweets", axis=alt.Axis(format='~s', gridColor='#e0e0e0')),
            color=alt.Color("Tipo_de_Tweet:N", title="Tipo de Tweet", legend=alt.Legend(orient='bottom', columns=4)),
            tooltip=[
                alt.Tooltip("Data:T", title="Data", format="%B de %Y"),
                alt.Tooltip("Tipo_de_Tweet:N", title="Tipo"),
                alt.Tooltip("Quantidade:Q", title="Quantidade", format=",.0f")
            ]
        ).properties(height=400).configure_view(stroke=None).interactive()

        return chart