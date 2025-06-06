from fastapi import FastAPI
from process import analisar_intersecao, ZONA_CATEGORIA

app = FastAPI()

@app.get("/consulta/{numero_car}")
def consulta(numero_car: str):
    path_car = "app/data/car.shp"
    path_zee = "app/data/zee.shp"
    resultado = analisar_intersecao(numero_car, path_car, path_zee)

    if "erro" in resultado:
        return resultado

    resultado["descricoes_zonas"] = {
        zona: ZONA_CATEGORIA.get(zona, {
            "categoria": "—",
            "descricao": "_Descrição ainda não informada._"
        }) for zona in resultado["zonas_presentes"]
    }

    return resultado
