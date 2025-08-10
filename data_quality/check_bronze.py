import pandas as pd
from sqlalchemy import create_engine
import great_expectations as ge

# 1. Conexión a Postgres
engine = create_engine(
    "postgresql://postgres:posgtresadmin@postgres-destination:5432/postgres"
)

# 2. Cargar la tabla bronze_clean
df = pd.read_sql("SELECT * FROM public.bronze_clean", engine)

# 3. Convertir a dataset de Great Expectations
gdf = ge.from_pandas(df)

# 4. Validaciones básicas
gdf.expect_column_to_exist("UserID")
gdf.expect_column_values_to_not_be_null("UserID")
gdf.expect_column_values_to_match_regex("UserID", r"^\d+$")  # si son números

gdf.expect_column_values_to_not_be_null("Eta")
gdf.expect_column_to_exist("Destination")
gdf.expect_column_values_to_not_be_null("Destination")

# 5. Mostrar reporte rápido en consola
results = gdf.validate()
print(results)

# 6. Guardar reporte HTML
from great_expectations.render.renderer import ValidationResultsPageRenderer
from great_expectations.render.view import DefaultJinjaPageView

renderer = ValidationResultsPageRenderer()
document = renderer.render(results)
html = DefaultJinjaPageView().render(document)
with open("data_quality/bronze_clean_report.html", "w") as f:
    f.write(html)
