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
    st.markdown("### Descubra em que zona do ZEE-TO seu imóvel está")

st.markdown(
    "#### Informe o número do CAR e receba um resumo técnico com percentuais, restrições e oportunidades"
)
st.markdown("---")

# ─── Dicionário de descrições das zonas ────────────────────────────────
descricoes_zonas = {
    "Zonas Especiais de Unidades de Conservação de Proteção Integral": {
        "titulo": "Zonas Especiais de Unidades de Conservação de Proteção Integral (ZEPIs)",
        "categoria": "Restritiva",
        "descricao": (
            "Unidades de Conservação de uso indireto. Permite apenas pesquisa, educação ambiental e "
            "visita controlada aprovada no Plano de Manejo. Mineração, agropecuária ou qualquer "
            "exploração direta é vedada. Não existe Reserva Legal a reduzir (área pública). Grande parte "
            "coincide com APSE, mantendo prioridade absoluta de conservação."
        )
    },
    "Zonas Especiais de Unidades de Conservação de Uso Sustentável": {
        "titulo": "Zonas Especiais de Unidades de Conservação de Uso Sustentável (ZEUSs)",
        "categoria": "Restritiva",
        "descricao": (
            "Unidades de Conservação de uso sustentável. Autoriza extrativismo, agricultura tradicional, "
            "turismo ecológico e manejo florestal conforme Plano de Manejo. Atividades de maior impacto "
            "exigem licenciamento. A Reserva Legal pode ser reduzida para 50 % se o Plano da UC prever. "
            "Fragmentos de APSE internos devem ser preservados."
        )
    },
    "Zonas Especiais de Terras Indígenas": {
        "titulo": "Zonas Especiais de Terras Indígenas (ZETIs)",
        "categoria": "Restritiva",
        "descricao": (
            "Territórios de usufruto exclusivo dos povos indígenas. Usos tradicionais (caça, pesca, coleta, "
            "roça) são garantidos; qualquer projeto externo precisa de consulta prévia e autorização da "
            "comunidade e da FUNAI. Exploração por não indígenas é proibida. APP e remanescentes naturais "
            "costumam permanecer intactos; não se aplica redução de Reserva Legal."
        )
    },
    "Zonas de Desenvolvimento Integrado 1": {
        "titulo": "Zonas de Desenvolvimento Integrado 1 (ZDIs-1)",
        "categoria": "Restritiva",
        "descricao": (
            "Vocação de conservação máxima. Recomenda PSA, regeneração e RPPN; apenas agricultura/pecuária "
            "de subsistência já aberta pode continuar. Mineração, indústrias e novos desmatamentos são "
            "proibidos. Reserva Legal deve manter 80/35/20 % (sem redução). Quase toda a área costuma ser APSE."
        )
    },
    "Zonas de Desenvolvimento Integrado 2": {
        "titulo": "Zonas de Desenvolvimento Integrado 2 (ZDIs-2)",
        "categoria": "Restritiva",
        "descricao": (
            "Alta prioridade de proteção com pequenos usos já consolidados. Aceita lavouras familiares e "
            "pecuária extensiva sob manejo conservacionista. Qualquer novo projeto de impacto exige "
            "licenciamento estrito. Reserva Legal integral (sem redução). Forte presença de APSE."
        )
    },
    "Zonas de Desenvolvimento Integrado 3": {
        "titulo": "Zonas de Desenvolvimento Integrado 3 (ZDI-3)",
        "categoria": "Intermediária",
        "descricao": (
            "Permite agropecuária extensiva aprimorada, reflorestamento comercial limitado e turismo "
            "ecológico. Empreendimentos médios/altos requerem EIA/RIMA. Reserva Legal pode ser regularizada "
            "em 50 % da área em floresta (Amazônia Legal), excluindo trechos prioritários. Fragmentos de APSE "
            "existentes não admitem redução de RL."
        )
    },
    "Zonas de Desenvolvimento Integrado 4": {
        "titulo": "Zonas de Desenvolvimento Integrado 4 (ZDI-4)",
        "categoria": "Intermediária",
        "descricao": (
            "Uso produtivo extensivo tradicional: agricultura e pecuária de médio porte, extrativismo e "
            "agroindústrias locais. Projetos de maior impacto precisam de licenciamento. Reserva Legal "
            "passível de redução a 50 % para regularizar passivos (Amazônia Legal), excetuando áreas prioritárias. "
            "APSE, se presente, deve permanecer intacta."
        )
    },
    "Zonas de Consolidação Estratégica 4": {
        "titulo": "Zonas de Consolidação Estratégica 4 (ZCEs-4)",
        "categoria": "Intermediária",
        "descricao": (
            "Zona diversificada: agropecuária intensiva/extensiva, reflorestamento, mineração local, energia e "
            "indústrias regionais. Exige licenciamento rigoroso para altos impactos. Reserva Legal pode ser "
            "regularizada em 50 % na Amazônia Legal; APSE internas requerem tratamento como área protegida."
        )
    },
    "Zonas de Consolidação Estratégica 3": {
        "titulo": "Zonas de Consolidação Estratégica 3 (ZCEs-3)",
        "categoria": "Produtiva",
        "descricao": (
            "Alto potencial socioeconômico. Grandes lavouras, pecuária intensiva, silvicultura, indústria e logística "
            "são permitidos, devendo obedecer licenciamento ambiental. Reserva Legal pode ser reduzida a 50 % para "
            "passivos históricos, mantendo APP. APSE praticamente ausente; onde existir, conservação é obrigatória."
        )
    },
    "Zonas de Consolidação Estratégica 2": {
        "titulo": "Zonas de Consolidação Estratégica 2 (ZCEs-2)",
        "categoria": "Produtiva",
        "descricao": (
            "Eixo primário de desenvolvimento com agronegócio em larga escala, polos industriais e grandes obras de "
            "infraestrutura. Necessita licenciamento rigoroso. Reserva Legal pode ser regularizada em 50 %. APSE raras; "
            "pequenos fragmentos devem ser preservados."
        )
    },
    "Zonas de Consolidação Estratégica 1": {
        "titulo": "Zonas de Consolidação Estratégica 1 (ZCEs-1)",
        "categoria": "Produtiva",
        "descricao": (
            "Áreas de uso intensivo consolidado. Todas as atividades lícitas são permitidas, desde que cumpram leis "
            "ambientais e licenciamento. Reserva Legal pode chegar a 50 % para regularização; demais casos seguem 20/35 %. "
            "APSE quase inexistentes; se presentes, são mantidas via APP/RL."
        )
    }
}

# ─── Função principal ─────────────────────────────────────────────────
def analisar_intersecao(numero_car: str, path_car: str, path_zee: str, path_apse: str):
    gdf_car = gpd.read_file(path_car)
    gdf_zee = gpd.read_file(path_zee)
    gdf_ecos = gpd.read_file(path_apse)

    imovel = gdf_car[gdf_car['numero_car'] == numero_car]
    if imovel.empty:
        return {"erro": "Número do CAR não encontrado"}

    nome_imovel = imovel.iloc[0]['nom_imovel']

    if not gdf_zee.crs.is_projected:
        gdf_zee = gdf_zee.to_crs(epsg=5880)
    imovel = imovel.to_crs(gdf_zee.crs)
    gdf_ecos = gdf_ecos.to_crs(imovel.crs)

    # Intersecção com ZEE
    intersecao = gpd.overlay(imovel, gdf_zee, how='intersection')
    intersecao['area_ha'] = intersecao.geometry.area / 10_000
    area_total = imovel.geometry.area.iloc[0] / 10_000
    intersecao['percentual'] = (intersecao['area_ha'] / area_total) * 100

    zonas_resultado = []
    if not intersecao.empty and 'zona' in intersecao.columns:
        zonas_resultado = [
            {
                "zona": row["zona"],
                "percentual": f"{row['percentual']:.2f}".replace('.', ',')
            }
            for _, row in intersecao.iterrows()
        ]

    zonas_presentes = sorted(set(row["zona"] for row in zonas_resultado))

    # Intersecção com APSE
    intersecao_ecos = gpd.overlay(imovel, gdf_ecos, how='intersection')
    apses = []
    if not intersecao_ecos.empty and 'serv_ecos' in intersecao_ecos.columns:
        intersecao_ecos['area_ha'] = intersecao_ecos.geometry.area / 10_000
        intersecao_ecos['percentual'] = (
            intersecao_ecos['area_ha'] / area_total * 100
        )

        apses = [
            {
                "servico": row['serv_ecos'],
                "percentual": f"{row['percentual']:.2f}".replace('.', ',')
            }
            for _, row in intersecao_ecos.iterrows()
        ]

    return {
        "numero_car": numero_car,
        "nome_imovel": nome_imovel,
        "zonas": zonas_resultado,
        "zonas_presentes": zonas_presentes,
        "descricoes_zonas": {
            z: descricoes_zonas.get(z, {"titulo": z, "categoria": "—", "descricao": "_sem descrição_"})
            for z in zonas_presentes
        },
        "apses": apses
    }

# ─── Formulário ───────────────────────────────────────────────────────
numero_car = st.text_input("Número do CAR")

if st.button("Consultar"):
    if not numero_car:
        st.warning("Por favor, digite o número do CAR.")
        st.stop()

    resultado = analisar_intersecao(
        numero_car,
        "app/data/car.shp",
        "app/data/zee.shp",
        "app/data/servicos_ecossistemicos_4674.shp"
    )

    if "erro" in resultado:
        st.error(resultado["erro"])
        st.stop()

    st.success(f"Imóvel: {resultado['nome_imovel']}  \nCAR: {resultado['numero_car']}")

    # Tabela ZEE
    if resultado["zonas"]:
        df = pd.DataFrame(resultado["zonas"])
        df["%"] = df["percentual"].str.replace(",", ".").astype(float)
        df["%"] = df["%"].map(lambda x: f"{x:.2f}".replace('.', ','))
        df = df.rename(columns={"zona": "Zona"})[["Zona", "%"]]
        st.markdown("### Zoneamento Ecológico-Econômico (ZEE)")
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.caption(
        "Dados oficiais do Zoneamento Ecológico-Econômico do Tocantins – versão 2025. "
        "Projeto de Lei encaminhado à ALETO em 02 abr 2025."
    )

    # Descrição por zona
    st.markdown("### O que significa para você?")
    for zona in resultado["zonas_presentes"]:
        info = resultado["descricoes_zonas"][zona]
        st.markdown(f"**{info['titulo']}**")
        st.markdown(f"**Categoria:** {info['categoria']}")
        st.markdown(info["descricao"])
        st.markdown("---")

    # Tabela APSE
    st.markdown("### Áreas Prioritárias para Serviços Ecossistêmicos (APSE)")
    apses = resultado.get("apses", [])
    if apses:
        df_apse = pd.DataFrame(apses)
        df_apse["%"] = df_apse["percentual"].str.replace(",", ".").astype(float)
        df_apse["%"] = df_apse["%"].map(lambda x: f"{x:.2f}".replace('.', ','))
        df_apse = df_apse.rename(columns={"servico": "Serviço"})[["Serviço", "%"]]
        st.dataframe(df_apse, use_container_width=True, hide_index=True)

        # Bloco explicativo APSE
        st.markdown("### O que significa para você?")
        st.markdown("""
**Composição**  
Reservas Legais declaradas no CAR, remanescentes florestais nativos relevantes, fundos de vale, entorno de reservatórios, veredas, matas de galeria, áreas íngremes (> 45 %), mananciais de abastecimento e zonas estratégicas de restauração.

**Objetivo**  
Priorizar a conservação de água e biodiversidade, mantendo a provisão de serviços ecossistêmicos e possibilitando ganhos ambientais e socioeconômicos.

**Diretrizes principais**  
Conservar remanescentes prioritários; Integrar RL e APP; Monitorar e prevenir incêndios e desmatamento; Incentivar PSA e projetos REDD+; Desenvolver pesquisa e educação sobre serviços ecossistêmicos; e Estimular criação de RPPN e compensação de RL.

**Reserva Legal**  
Dentro de APSE não é permitido reduzir a RL para 50 %; deve manter os percentuais integrais (80/35/20 %), mesmo em zonas que admitam redução fora da APSE.
        """)

        # Fonte da APSE (ZEE/2025)
        st.caption(
            "Dados oficiais do Zoneamento Ecológico-Econômico do Tocantins – versão 2025. "
            "Projeto de Lei encaminhado à ALETO em 02 abr 2025."
        )

    else:
        st.info(
            "O imóvel objeto de análise não intersecta nenhuma Área Prioritária para "
            "Serviços Ecossistêmicos (APSE)."
        )

    # Contato
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
