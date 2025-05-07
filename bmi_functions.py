bmi_category_adult = {
    (0, 18.5): 'Underweight',
    (18.5, 24.9): 'Normal weight',
    (25.0, 29.9): 'Overweight',
    (30.0, 34.9): 'Obesity Class I',
    (35.0, 39.9): 'Obesity Class II',
    (40.0, float('inf')): 'Obesity Class III (severe)'
}
ONE_KG_TO_POUNDS = 2.20462
ONE_FEET_TO_METERS = 0.3048
ONE_INCH_TO_METERS = 0.0254
ONE_METER_TO_INCHES = 39.3701

def classify_bmi_category(bmi):
    for (low, high), category in bmi_category_adult.items():
        if low <= bmi <= high:
            return category
    return "Unknown"

# Conversion functions
def kgs_to_pounds(kgs):
    return kgs * ONE_KG_TO_POUNDS

def lbs_to_kgs(lbs):
    return lbs / ONE_KG_TO_POUNDS

def feet_inches_to_meters(feet, inches):
    return (feet * ONE_FEET_TO_METERS) + (inches * ONE_INCH_TO_METERS)

def meters_to_feet_inches(m):
    total_inches = m * ONE_METER_TO_INCHES
    feet = int(total_inches // 12)
    inches = round(total_inches % 12)
    return feet, inches