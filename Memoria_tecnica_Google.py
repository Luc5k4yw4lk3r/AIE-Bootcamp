from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_pdf(filename="Memoria_Tecnica_Google_Cloud_Startups.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1A73E8'),
        spaceAfter=12
    )
    
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#202124'),
        spaceBefore=14,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#3C4043'),
        spaceAfter=8
    )

    story = []

    # Encabezado
    story.append(Paragraph("MEMORIA TÉCNICA DE SOLICITUD: GOOGLE CLOUD FOR STARTUPS", title_style))
    story.append(Paragraph("<b>Proyecto:</b> Market Radar AI — Automated Opportunity Intelligence Engine<br/>"
                           "<b>Categoría:</b> AI / Machine Learning Native Startup<br/>"
                           "<b>Programa:</b> Google Cloud for Startups (AI First Track)<br/>"
                           "<b>Fecha:</b> Septiembre 2026", body_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E0E0E0'), spaceAfter=15))

    # 1. Resumen Ejecutivo
    story.append(Paragraph("1. Resumen Ejecutivo", h2_style))
    story.append(Paragraph(
        "<b>Market Radar AI</b> es un motor de inteligencia de mercado en tiempo real diseñado para identificar, "
        "auditar y clasificar oportunidades de software B2B desatendidas mediante el análisis continuo de señales no estructuradas "
        "en foros técnicos, repositorios de código y comunidades de desarrolladores.<br/><br/>"
        "El sistema procesa diariamente miles de publicaciones dispersas, aplicando modelos de procesamiento de lenguaje natural "
        "y embedding de alta dimensión para calcular el <b>Financial Demand Index (FDI)</b>, un algoritmo propio de puntuación "
        "de viabilidad comercial y complejidad técnica.", body_style))

    # 2. Arquitectura de la Solución
    story.append(Paragraph("2. Arquitectura de la Solución y Uso de IA", h2_style))
    story.append(Paragraph(
        "La arquitectura está basada en un paradigma <b>Serverless Event-Driven</b> desplegado sobre Google Cloud Platform:<br/>"
        "• <b>Cloud Pub/Sub & Cloud Run:</b> Bus de eventos e ingesta asíncrona de Webhooks de GitHub y RSS.<br/>"
        "• <b>Vertex AI (Gemini 2.0 Flash & Gemini 1.5 Pro):</b> Clasificación rápida de dolor y auditoría de viabilidad B2B con ventana de contexto de 2M tokens.<br/>"
        "• <b>Vertex AI Vector Search:</b> Búsqueda vectorial con embeddings <code>text-embedding-004</code> para deduplicación por coseno (>0.88).", body_style))

    # 3. Distribución de Créditos (Tabla)
    story.append(Paragraph("3. Plan de Distribución y Consumo de Créditos", h2_style))
    
    table_data = [
        ['Servicio GCP', 'Función Principal', 'Consumo Est.'],
        ['Vertex AI (Gemini API)', 'Inferencia de agentes y cálculo de FDI', '45% - 50%'],
        ['Vertex AI Vector Search', 'Indexación vectorial y deduplicación (<10ms)', '15% - 20%'],
        ['Google Cloud Run', 'Ejecución de backend y microservicios', '15%'],
        ['BigQuery & Storage', 'Almacenamiento histórico y Data Lake', '10%'],
        ['Cloud SQL & Redes', 'Base de datos relacional y balanceadores', '10%']
    ]
    
    t = Table(table_data, colWidths=[150, 240, 90])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F3F4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#202124')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # 4. Hitos
    story.append(Paragraph("4. Impacto Comercial e Hitos (12 Meses)", h2_style))
    story.append(Paragraph(
        "• <b>Q1:</b> Migración de microservicios a Cloud Run y setup de Vertex AI Vector Search.<br/>"
        "• <b>Q2:</b> Escalado de ingesta a >250,000 publicaciones/día y alertas automáticas vía Webhook.<br/>"
        "• <b>Q3:</b> Apertura de API B2B para fondos de VC e ingreso al Google for Startups Accelerator.", body_style))

    doc.build(story)

if __name__ == "__main__":
    create_pdf()