from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def parse_indian_number(number_str):
    """Convert Indian formatted string (with commas) to float"""
    if isinstance(number_str, str):
        return float(number_str.replace(',', ''))
    return float(number_str)

def calculate_marriage_considerations(data):
    """Calculate marriage considerations with all parameters"""
    # Parse all numeric inputs
    salary = parse_indian_number(data.get('salary', 0))
    education_level = float(data.get('education', 5))
    assets = parse_indian_number(data.get('assets', 0))
    education_expense = parse_indian_number(data.get('education-expense', 0))
    social_status = float(data.get('social-status', 5))
    profession = int(data.get('profession', 2))
    marital_status = int(data.get('marital-status', 1))
    location = int(data.get('location', 2))
    
    # Multipliers
    profession_multipliers = {
        1: 0.8,    # Unemployed
        2: 1.0,    # Private Sector
        3: 1.5,    # Government Job
        4: 1.8,    # Doctor/Engineer
        5: 2.5,    # IAS/IPS/IRS
        6: 2.0,    # Business Owner
        7: 3.0     # NRI Professional
    }
    
    location_multipliers = {
        1: 0.8,    # Rural
        2: 1.2,    # Urban
        3: 2.0     # NRI
    }
    
    marital_multipliers = {
        1: 1.0,    # Never Married
        2: 0.7,    # Divorced
        3: 0.6     # Widow/Widower
    }
    
    # Calculate base components
    base_dowry = salary * 12 * 3  # 3 years salary
    assets_contribution = assets * 0.2  # 20% of assets
    education_investment = education_expense * 0.5  # 50% of education expenses
    
    # Apply multipliers
    profession_factor = profession_multipliers.get(profession, 1.0)
    location_factor = location_multipliers.get(location, 1.0)
    marital_factor = marital_multipliers.get(marital_status, 1.0)
    
    # Education and social multipliers
    education_multiplier = 1 + (education_level / 10)
    social_multiplier = 1 + (social_status / 10)
    
    # Additional factors
    car_bonus = base_dowry * 0.15 if data.get('car') == 'true' else 0
    property_bonus = base_dowry * 0.25 if data.get('property') == 'true' else 0
    foreign_degree_bonus = base_dowry * 0.2 if data.get('foreign-degree') == 'true' else 0
    
    # Calculate components
    base_value = (base_dowry + assets_contribution + education_investment) * profession_factor * marital_factor
    education_bonus = (base_value * (education_multiplier - 1)) + foreign_degree_bonus
    status_premium = (base_value * (social_multiplier - 1)) + car_bonus + property_bonus
    
    # Final calculation with location factor
    total_consideration = (base_value + education_bonus + status_premium) * location_factor
    
    return {
        'total': round(total_consideration),
        'base_value': round(base_value),
        'education_bonus': round(education_bonus),
        'status_premium': round(status_premium)
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['salary', 'education', 'assets', 'social-status']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Calculate with all parameters
        result = calculate_marriage_considerations(data)
        return jsonify({
            'dowry': result['total'],
            'breakdown': {
                'base_value': result['base_value'],
                'education_bonus': result['education_bonus'],
                'status_premium': result['status_premium']
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)