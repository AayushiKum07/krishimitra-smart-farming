# Static crop reference data.
#
# This replaces the old MySQL `crops` table. The ML model only needs
# N, P, K, temperature, humidity, ph and rainfall to produce a prediction -
# everything below is purely descriptive metadata shown on the results page,
# so it lives in code instead of a database.

CROP_INFO = {
    'rice':        {'crop_name': 'Rice', 'season': 'Kharif', 'soil_type': 'Clayey', 'crop_duration': '110-140 Days',
                     'crop_description': 'A staple cereal crop that thrives in flooded, humid conditions with high rainfall and warm temperatures.'},
    'maize':       {'crop_name': 'Maize', 'season': 'Kharif/Rabi', 'soil_type': 'Loamy', 'crop_duration': '90-120 Days',
                     'crop_description': 'A versatile cereal grown in warm climates, valued for grain, fodder and industrial uses.'},
    'chickpea':    {'crop_name': 'Chickpea', 'season': 'Rabi', 'soil_type': 'Sandy Loam', 'crop_duration': '90-120 Days',
                     'crop_description': 'A drought-tolerant legume that fixes nitrogen in the soil and prefers cooler, dry growing conditions.'},
    'kidneybeans': {'crop_name': 'Kidney Beans', 'season': 'Kharif', 'soil_type': 'Loamy', 'crop_duration': '90-110 Days',
                     'crop_description': 'A protein-rich legume that grows best in well-drained loamy soils with moderate rainfall.'},
    'pigeonpeas':  {'crop_name': 'Pigeon Peas', 'season': 'Kharif', 'soil_type': 'Red/Black', 'crop_duration': '150-180 Days',
                     'crop_description': 'A hardy, drought-resistant pulse crop suited to semi-arid regions with well-drained soils.'},
    'mothbeans':   {'crop_name': 'Moth Beans', 'season': 'Kharif', 'soil_type': 'Sandy', 'crop_duration': '65-90 Days',
                     'crop_description': 'A highly drought-tolerant legume traditionally grown in arid and semi-arid regions.'},
    'mungbean':    {'crop_name': 'Mung Bean', 'season': 'Kharif/Summer', 'soil_type': 'Loamy', 'crop_duration': '60-90 Days',
                     'crop_description': 'A fast-growing, short-duration pulse that improves soil fertility through nitrogen fixation.'},
    'blackgram':   {'crop_name': 'Black Gram', 'season': 'Kharif/Rabi', 'soil_type': 'Loamy', 'crop_duration': '70-90 Days',
                     'crop_description': 'A warm-season pulse crop valued for its high protein content and soil-enriching properties.'},
    'lentil':      {'crop_name': 'Lentil', 'season': 'Rabi', 'soil_type': 'Loamy', 'crop_duration': '100-130 Days',
                     'crop_description': 'A cool-season legume that performs well in well-drained soils with moderate moisture.'},
    'pomegranate': {'crop_name': 'Pomegranate', 'season': 'Year-round', 'soil_type': 'Loamy/Alluvial', 'crop_duration': '5-7 Months (fruiting)',
                     'crop_description': 'A hardy fruit crop tolerant of dry conditions, well suited to semi-arid climates.'},
    'banana':      {'crop_name': 'Banana', 'season': 'Year-round', 'soil_type': 'Alluvial', 'crop_duration': '10-12 Months',
                     'crop_description': 'A fast-growing tropical fruit crop requiring high humidity, warmth, and consistent moisture.'},
    'mango':       {'crop_name': 'Mango', 'season': 'Summer (fruiting)', 'soil_type': 'Alluvial', 'crop_duration': '4-5 Months (fruiting)',
                     'crop_description': 'A long-lived tropical fruit tree that thrives in warm climates with a distinct dry season.'},
    'grapes':      {'crop_name': 'Grapes', 'season': 'Year-round', 'soil_type': 'Sandy Loam', 'crop_duration': '5-6 Months (fruiting)',
                     'crop_description': 'A vine fruit crop that prefers well-drained soils and a warm, relatively dry climate.'},
    'watermelon':  {'crop_name': 'Watermelon', 'season': 'Summer', 'soil_type': 'Sandy Loam', 'crop_duration': '80-100 Days',
                     'crop_description': 'A warm-season vine crop needing plenty of sunshine, warmth, and well-drained sandy soils.'},
    'muskmelon':   {'crop_name': 'Muskmelon', 'season': 'Summer', 'soil_type': 'Sandy Loam', 'crop_duration': '80-100 Days',
                     'crop_description': 'A heat-loving vine fruit that requires warm temperatures and good soil drainage.'},
    'apple':       {'crop_name': 'Apple', 'season': 'Temperate (Rabi)', 'soil_type': 'Loamy', 'crop_duration': '4-5 Months (fruiting)',
                     'crop_description': 'A temperate fruit tree requiring cool winters and moderate rainfall, typically grown in hilly regions.'},
    'orange':      {'crop_name': 'Orange', 'season': 'Winter (fruiting)', 'soil_type': 'Loamy', 'crop_duration': '7-8 Months (fruiting)',
                     'crop_description': 'A citrus fruit crop that prefers well-drained soils and a subtropical to tropical climate.'},
    'papaya':      {'crop_name': 'Papaya', 'season': 'Year-round', 'soil_type': 'Loamy', 'crop_duration': '9-11 Months',
                     'crop_description': 'A fast-maturing tropical fruit crop that needs warm temperatures and good drainage.'},
    'coconut':     {'crop_name': 'Coconut', 'season': 'Year-round', 'soil_type': 'Sandy/Alluvial', 'crop_duration': '12 Months (year-round bearing)',
                     'crop_description': 'A tropical palm requiring high humidity, warmth, and coastal or well-irrigated conditions.'},
    'cotton':      {'crop_name': 'Cotton', 'season': 'Kharif', 'soil_type': 'Black', 'crop_duration': '150-180 Days',
                     'crop_description': 'A cash crop fibre plant that grows best in warm climates with black or well-drained soils.'},
    'jute':        {'crop_name': 'Jute', 'season': 'Kharif', 'soil_type': 'Alluvial', 'crop_duration': '100-120 Days',
                     'crop_description': 'A fibre crop that thrives in hot, humid conditions with high rainfall and fertile alluvial soil.'},
    'coffee':      {'crop_name': 'Coffee', 'season': 'Year-round', 'soil_type': 'Loamy (well-drained)', 'crop_duration': '8-9 Months (fruiting)',
                     'crop_description': 'A shade-loving tropical crop that requires consistent warmth, humidity, and well-drained fertile soil.'},
}

DEFAULT_CROP_INFO = {
    'season': 'Kharif/Rabi',
    'soil_type': 'Loamy',
    'crop_duration': '100-120 Days',
    'crop_description': 'This crop has been recommended based on your soil nutrient and weather inputs.',
}


def get_crop_info(crop_label):
    """Returns descriptive info for a predicted crop label, with a sensible fallback."""
    key = (crop_label or '').strip().lower()
    info = CROP_INFO.get(key)
    if info:
        return dict(info)
    fallback = dict(DEFAULT_CROP_INFO)
    fallback['crop_name'] = (crop_label or 'Unknown').capitalize()
    return fallback


# Friendly display names for the 7 model input features, used on the
# "Why this crop?" feature-importance panel.
FEATURE_LABELS = {
    'N': 'Nitrogen (N)',
    'P': 'Phosphorus (P)',
    'K': 'Potassium (K)',
    'temperature': 'Temperature',
    'humidity': 'Humidity',
    'ph': 'Soil pH',
    'rainfall': 'Rainfall',
}


def get_sample_crops(limit=6):
    """A handful of crops to showcase on the homepage (replaces 'SELECT * FROM crops LIMIT 6')."""
    keys = ['rice', 'maize', 'cotton', 'mango', 'watermelon', 'coffee']
    return [get_crop_info(k) for k in keys[:limit]]
