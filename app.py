import streamlit as st
import pandas as pd
import geopandas as gpd
import base64
from pathlib import Path

st.set_page_config(page_title="Consulta CAR x ZEE", layout="centered")

# ─── Cabeçalho com logo ───────────────────────────────────────────────
logo_path = Path("logo_empresa.png")
col1, col2 = st.columns([1, 4])

with col1:
    if logo_path.exists():
        img_base64 = base64.b64encode(logo_path.read_bytes()).decode()
        st.markdown(
            f'<img src="data:image/png;base64,{img_base64}" style="width:120px; margin-top:10px;">',
            unsafe_allow_html=True
        )
    else:
        st.warning("Logo não encontrada.")

with col2:
    st.markdown("### Descubra em que zona do ZEE‑TO seu imóvel está")

st.markdown("#### Informe o número do CAR e receba um resumo técnico com percentuais, restrições e oportunidades")
st.markdown("---")

# ─── Função de interseção ─────────────────────────────────────────────
def analisar_intersecao(numero_car: str, path_car: str, path_zee: str):
    gdf_car = gpd.read_file(path_car)
    gdf_zee = gpd.read_file(path_zee)

    imovel = gdf_car[gdf_car['numero_car'] == numero_car]
    if imovel.empty:
        return {"erro": "Número do CAR não encontrado"}

    nome_imovel = imovel.iloc[0]['nom_imovel']

    if not gdf_zee.crs.is_projected:
        gdf_zee = gdf_zee.to_crs(epsg=5880)
    imovel = imovel.to_crs(gdf_zee.crs)

    intersecao = gpd.overlay(imovel, gdf_zee, how='intersection')

    if intersecao.empty:
        return {"erro": "O imóvel não intersecta com nenhuma zona do ZEE."}

    if 'zona' not in intersecao.columns:
        return {"erro": "Campo 'zona' não encontrado no shapefile do ZEE."}

    intersecao['area_ha'] = intersecao.geometry.area / 10_000
    area_total = imovel.geometry.area.iloc[0] / 10_000
    intersecao['percentual'] = (intersecao['area_ha'] / area_total) * 100

    zonas_resultado = [
        {
            "zona": row["zona"],
            "percentual": f"{row['percentual']:.2f}".replace('.', ',')
        }
        for _, row in intersecao.iterrows()
    ]

    zonas_presentes = sorted(set(row["zona"] for row in zonas_resultado))

    return {
        "numero_car": numero_car,
        "nome_imovel": nome_imovel,
        "zonas": zonas_resultado,
        "zonas_presentes": zonas_presentes,
        "descricoes_zonas": {
            z: {
                "categoria": "—",
                "descricao": "_Descrição ainda não informada._"
            } for z in zonas_presentes
        }
    }

# ─── Formulário ───────────────────────────────────────────────────────
numero_car = st.text_input("Número do CAR")

if st.button("Consultar"):
    if not numero_car:
        st.warning("Por favor, digite o número do CAR.")
        st.stop()

    resultado = analisar_intersecao(numero_car, "app/data/car.shp", "app/data/zee.shp")

    if "erro" in resultado:
        st.error(resultado["erro"])
        st.stop()

    st.success(f"Imóvel: {resultado['nome_imovel']}  \nCAR: {resultado['numero_car']}")

    df = pd.DataFrame(resultado["zonas"])
    df["%"] = df["percentual"].str.replace(",", ".").astype(float)
    df["%"] = df["%"].map(lambda x: f"{x:.2f}".replace('.', ','))
    df = df.rename(columns={"zona": "Zona"})[["Zona", "%"]]
    st.dataframe(df, use_container_width=True)

    st.caption(
        "Dados oficiais do Zoneamento Ecológico‑Econômico do Tocantins – versão 2025. "
        "Projeto de Lei encaminhado à ALETO em 02 abr 2025."
    )

    st.markdown("### O que significa para você?")
    for zona in resultado["zonas_presentes"]:
        info = resultado["descricoes_zonas"].get(zona, {})
        categoria = info.get("categoria", "—")
        desc = info.get("descricao", "_sem descrição_")
        st.markdown(f"**{zona}** — Categoria: **{categoria}**  \n{desc}")

    st.markdown("---")
    st.markdown("#### Fale com a Plêiade", unsafe_allow_html=True)
    st.markdown(
        '''
        <a href="https://wa.me/5563981017774" target="_blank">
            <button style="background-color:#25D366;color:white;border:none;
            padding:10px 20px;font-size:16px;border-radius:5px;cursor:pointer;">
                📞 WhatsApp
            </button>
        </a>
        ''',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        "Aviso legal: “Este resultado é orientativo e não substitui análise técnica nem "
        "licenciamento ambiental. Consulte um profissional habilitado.”"
    )
    st.caption("Atualizado em 05/06/2025")
