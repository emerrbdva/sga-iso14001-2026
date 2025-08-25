from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from jinja2 import Environment, FileSystemLoader
from . import services, schemas
from datetime import date # <--- ¡AÑADIR ESTA LÍNEA!

router = APIRouter()

# Configura Jinja2 para que encuentre nuestras plantillas
env = Environment(loader=FileSystemLoader("app/templates"))

class ReportRequest(schemas.BaseModel):
    company_name: str
    reporting_period: str
    start_date: date # <-- Ahora Python sabe qué es 'date'
    end_date: date   # <-- Ahora Python sabe qué es 'date'

@router.post("/reports/sustainability", tags=["Generación de Reportes"])
def generate_sustainability_report(request_data: ReportRequest):
    """
    Genera un reporte de sostenibilidad agregando datos de todos los microservicios.
    """
    # 1. Recolectar datos de todos los servicios
    policy_data = services.get_policy()
    aspects_data = services.get_significant_aspects()
    ghg_data = services.get_ghg_inventory(request_data.start_date, request_data.end_date)
    
    # 2. Ensamblar el objeto del reporte
    report_data = schemas.SustainabilityReport(
        company_name=request_data.company_name,
        reporting_period=request_data.reporting_period,
        policy=policy_data,
        significant_aspects=aspects_data,
        ghg_inventory=ghg_data
    )
    
    # 3. Renderizar la plantilla con los datos
    template = env.get_template("report.md.j2")
    report_markdown = template.render(report=report_data)
    
    return JSONResponse(content={"report_markdown": report_markdown})