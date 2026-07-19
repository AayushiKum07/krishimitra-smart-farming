import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file

import predict
from crop_data import get_crop_info, get_sample_crops, FEATURE_LABELS, CROP_INFO
from translations import TRANSLATIONS, SUPPORTED_LANGUAGES

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'krishimitra_super_secret_key_12984')


# Context Processor for localization
@app.context_processor
def inject_translations():
    lang = session.get('lang', 'en')
    def translate(key, fallback=None):
        return TRANSLATIONS.get(lang, {}).get(key, fallback or TRANSLATIONS['en'].get(key, key))
    return dict(_t=translate, current_lang=lang, supported_languages=SUPPORTED_LANGUAGES)


# Language switch route
@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in dict(SUPPORTED_LANGUAGES):
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))


# ======================================================
# LANDING PAGE
# ======================================================
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/crops')
def crop_library():
    crops = []
    for key in sorted(CROP_INFO.keys()):
        info = dict(CROP_INFO[key])
        info['key'] = key
        crops.append(info)
    return render_template('crop_library.html', crops=crops)


# ======================================================
# CROP RECOMMENDATION (prediction only, no persistence)
# ======================================================
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        try:
            n = float(request.form.get('n', 0))
            p = float(request.form.get('p', 0))
            k = float(request.form.get('k', 0))
            ph = float(request.form.get('ph', 6.5))
            temp = float(request.form.get('temperature', 25.0))
            humidity = float(request.form.get('humidity', 70.0))
            rainfall = float(request.form.get('rainfall', 100.0))
            soil_type = request.form.get('soil_type', 'Loamy')
            farm_size = request.form.get('farm_size', 1.0)
        except (TypeError, ValueError):
            flash('Please enter valid numeric values for all fields.', 'danger')
            return redirect(url_for('recommend'))

        # Run ML model prediction
        try:
            top_crops = predict.predict_top_crops(n, p, k, temp, humidity, ph, rainfall, top_k=3)
            crop_label, confidence = top_crops[0]
            importances = predict.get_feature_importances()
        except Exception as e:
            flash(f"Prediction error: {e}. Please ensure the model file is present.", 'danger')
            return redirect(url_for('recommend'))

        # Store the result in the session (replaces the old `recommendations` DB table)
        session['last_recommendation'] = {
            'id': 1,
            'nitrogen': n,
            'phosphorus': p,
            'potassium': k,
            'ph': ph,
            'temperature': temp,
            'humidity': humidity,
            'rainfall': rainfall,
            'soil_type': soil_type,
            'farm_size': farm_size,
            'predicted_crop': crop_label,
            'confidence_score': confidence,
            'top_crops': top_crops,
            'feature_importances': importances,
        }
        return redirect(url_for('recommendation_results'))

    return render_template('crop_recommendation.html')


@app.route('/recommendation')
def recommendation_results():
    rec = session.get('last_recommendation')
    if not rec:
        flash('No recommendation found yet. Please fill in the form first.', 'danger')
        return redirect(url_for('recommend'))

    crop_info = get_crop_info(rec['predicted_crop'])

    # Top-3 ranked predictions with display-friendly crop names
    top_crops = []
    for label, conf in rec.get('top_crops', [(rec['predicted_crop'], rec['confidence_score'])]):
        info = get_crop_info(label)
        top_crops.append({'crop_name': info['crop_name'], 'confidence': conf})

    # Feature importance -> friendly labels for the "Why this crop?" panel
    feature_importance = []
    for feature_key, importance in rec.get('feature_importances', []):
        feature_importance.append({
            'label': FEATURE_LABELS.get(feature_key, feature_key),
            'importance': importance,
        })

    # NPK deficiency calculations
    deficiency_notes = []
    if rec['nitrogen'] < 40:
        deficiency_notes.append("Nitrogen (N) level is low. Add nitrogenous fertilizer like Urea to support leaf development and plant vigor.")
    if rec['phosphorus'] < 45:
        deficiency_notes.append("Phosphorus (P) level is low. Add phosphatic fertilizers like Single Super Phosphate (SSP) or DAP to boost root growth.")
    if rec['potassium'] < 40:
        deficiency_notes.append("Potassium (K) level is low. Add potash fertilizers like Muriate of Potash (MOP) to improve disease resistance and grain quality.")
    if not deficiency_notes:
        deficiency_notes.append("Nutrient levels (N, P, K) look healthy and balanced for the recommended crop!")

    # Fertilizer catalog table no longer exists (removed with MySQL) - the
    # results page already handles an empty list gracefully with a fallback message.
    fertilizers = []

    return render_template('recommendation_results.html', rec=rec, crop=crop_info,
                            fertilizers=fertilizers, deficiencies=deficiency_notes,
                            top_crops=top_crops, feature_importance=feature_importance)


@app.route('/download_pdf')
def download_pdf():
    rec = session.get('last_recommendation')
    if not rec:
        flash('No recommendation found yet. Please fill in the form first.', 'danger')
        return redirect(url_for('recommend'))

    crop_info = get_crop_info(rec['predicted_crop'])

    from io import BytesIO
    from datetime import datetime
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=22,
        textColor=colors.HexColor('#1b4332'), spaceAfter=8, alignment=1
    )
    sub_style = ParagraphStyle(
        'SubTitleStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#555555'),
        spaceAfter=20, alignment=1
    )
    h2_style = ParagraphStyle(
        'H2Style', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13,
        textColor=colors.HexColor('#40916c'), spaceBefore=10, spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyStyle', parent=styles['BodyText'], fontSize=9, leading=12
    )

    # Header
    story.append(Paragraph("KRISHIMITRA REPORT", title_style))
    story.append(Paragraph("AI-Powered Crop, Seed, & Fertilizer Recommendation System", sub_style))
    story.append(Spacer(1, 10))

    # Farm details (no farmer account system, so we show the submitted farm parameters instead)
    story.append(Paragraph("Farm Information", h2_style))
    farm_data = [
        [Paragraph("<b>Soil Type:</b>", body_style), Paragraph(str(rec['soil_type']), body_style),
         Paragraph("<b>Farm Size:</b>", body_style), Paragraph(f"{rec['farm_size']} acres", body_style)],
        [Paragraph("<b>Date & Time:</b>", body_style), Paragraph(datetime.now().strftime('%Y-%m-%d %H:%M'), body_style),
         Paragraph("", body_style), Paragraph("", body_style)]
    ]
    t_farm = Table(farm_data, colWidths=[100, 160, 90, 150])
    t_farm.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.lightgrey),
    ]))
    story.append(t_farm)
    story.append(Spacer(1, 10))

    # Soil input parameters
    story.append(Paragraph("Soil Analysis Parameters", h2_style))
    soil_data = [
        [Paragraph("<b>Nitrogen (N)</b>", body_style), Paragraph(f"{rec['nitrogen']} ppm", body_style),
         Paragraph("<b>Phosphorus (P)</b>", body_style), Paragraph(f"{rec['phosphorus']} ppm", body_style),
         Paragraph("<b>Potassium (K)</b>", body_style), Paragraph(f"{rec['potassium']} ppm", body_style)],
        [Paragraph("<b>Soil pH</b>", body_style), Paragraph(str(rec['ph']), body_style),
         Paragraph("<b>Temperature</b>", body_style), Paragraph(f"{rec['temperature']} °C", body_style),
         Paragraph("<b>Humidity</b>", body_style), Paragraph(f"{rec['humidity']} %", body_style)],
        [Paragraph("<b>Rainfall</b>", body_style), Paragraph(f"{rec['rainfall']} mm", body_style),
         Paragraph("<b>Soil Type</b>", body_style), Paragraph(str(rec['soil_type']), body_style),
         Paragraph("", body_style), Paragraph("", body_style)]
    ]
    t_soil = Table(soil_data, colWidths=[90, 80, 95, 80, 85, 80])
    t_soil.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_soil)
    story.append(Spacer(1, 10))

    # Recommendation
    story.append(Paragraph("AI Recommendation Result", h2_style))
    rec_data = [
        [Paragraph("<b>Recommended Crop:</b>", body_style),
         Paragraph(f"<b>{rec['predicted_crop'].capitalize()}</b> (Confidence: {rec['confidence_score'] * 100:.1f}%)", body_style)],
        [Paragraph("<b>Season:</b>", body_style), Paragraph(crop_info.get('season', 'N/A'), body_style)],
        [Paragraph("<b>Crop Duration:</b>", body_style), Paragraph(crop_info.get('crop_duration', 'N/A'), body_style)],
        [Paragraph("<b>Crop Description:</b>", body_style), Paragraph(crop_info.get('crop_description', 'N/A'), body_style)]
    ]
    t_rec = Table(rec_data, colWidths=[120, 380])
    t_rec.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e9')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_rec)
    story.append(Spacer(1, 10))

    # Top-3 alternative crops
    top_crops = rec.get('top_crops', [])
    if top_crops:
        story.append(Paragraph("Top 3 Recommended Crops", h2_style))
        top_rows = [[Paragraph("<b>Rank</b>", body_style), Paragraph("<b>Crop</b>", body_style), Paragraph("<b>Confidence</b>", body_style)]]
        for i, (label, conf) in enumerate(top_crops, start=1):
            top_rows.append([
                Paragraph(str(i), body_style),
                Paragraph(get_crop_info(label)['crop_name'], body_style),
                Paragraph(f"{conf * 100:.1f}%", body_style),
            ])
        t_top = Table(top_rows, colWidths=[50, 250, 200])
        t_top.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f5e9')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t_top)
        story.append(Spacer(1, 10))

    # Feature importance ("Why this crop?")
    importances = rec.get('feature_importances', [])
    if importances:
        story.append(Paragraph("Model Feature Importance", h2_style))
        story.append(Paragraph(
            "Ranking of which soil/weather factors most influence this model's predictions overall:",
            body_style))
        imp_rows = [[Paragraph("<b>Factor</b>", body_style), Paragraph("<b>Influence</b>", body_style)]]
        for feature_key, importance in importances:
            imp_rows.append([
                Paragraph(FEATURE_LABELS.get(feature_key, feature_key), body_style),
                Paragraph(f"{importance * 100:.1f}%", body_style),
            ])
        t_imp = Table(imp_rows, colWidths=[250, 250])
        t_imp.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f5e9')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t_imp)
        story.append(Spacer(1, 15))

    story.append(Paragraph("<font color='grey'>* This report is generated by KrishiMitra AI Decision Support System.</font>", body_style))

    doc.build(story)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="KrishiMitra_Report.pdf", mimetype='application/pdf')


if __name__ == '__main__':
    app.run(debug=True)
