import geopandas as gpd

# Dicionário a ser preenchido depois com os textos das zonas
ZONA_CATEGORIA = {
    # "zona": {"categoria": "Produtiva", "descricao": "Texto descritivo..."},
}

def analisar_intersecao(numero_car: str, path_car: str, path_zee: str):
    gdf_car = gpd.read_file(path_car)
    gdf_zee = gpd.read_file(path_zee)

    imovel = gdf_car[gdf_car['numero_car'] == numero_car]
    if imovel.empty:
        return {"erro": "Número do CAR não encontrado"}

    nome_imovel = imovel.iloc[0]['nom_imovel']

    # Garantir CRS projetado (em metros)
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

    # Retornar apenas percentual e nome da zona
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
        "zonas_presentes": zonas_presentes
    }
