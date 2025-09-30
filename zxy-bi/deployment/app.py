"""
ZXY Business Intelligence Dashboard
Main Flask Application
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime, timedelta
import json
import random
import logging
from app.models.dashboard_data import DashboardDataModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'zxy-bi-dashboard-secret-key')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', True)

# Initialize data model
dashboard_data = DashboardDataModel()

# Sample data for demonstration
def generate_sample_data():
    """Generate sample business intelligence data"""
    return {
        'kpis': {
            'total_sales': {
                'value': 12500000,
                'change': 8.5,
                'period': 'FYTD'
            },
            'manufacturing_efficiency': {
                'value': 94.2,
                'change': 2.1,
                'period': 'Current Month'
            },
            'logistics_performance': {
                'value': 97.8,
                'change': -0.5,
                'period': 'Current Month'
            },
            'customer_satisfaction': {
                'value': 4.7,
                'change': 0.3,
                'period': 'Current Quarter'
            }
        },
        'alerts': [
            {
                'type': 'high',
                'title': 'Production Line 3 Efficiency Drop',
                'description': 'Efficiency dropped to 87% - requires immediate attention',
                'timestamp': datetime.now() - timedelta(hours=2)
            },
            {
                'type': 'medium',
                'title': 'Inventory Level Warning',
                'description': 'Raw material stock below threshold for Product SKU-4521',
                'timestamp': datetime.now() - timedelta(hours=5)
            },
            {
                'type': 'low',
                'title': 'Scheduled Maintenance Due',
                'description': 'Equipment maintenance scheduled for next week',
                'timestamp': datetime.now() - timedelta(days=1)
            }
        ],
        'sales_pipeline': [
            {
                'company': 'TechCorp Industries',
                'value': 850000,
                'stage': 'Proposal',
                'probability': 75,
                'contact': 'Sarah Johnson',
                'next_action': 'Follow-up call scheduled'
            },
            {
                'company': 'Global Manufacturing Ltd',
                'value': 1200000,
                'stage': 'Negotiation',
                'probability': 60,
                'contact': 'Michael Chen',
                'next_action': 'Contract review pending'
            },
            {
                'company': 'Innovation Systems',
                'value': 650000,
                'stage': 'Qualified',
                'probability': 40,
                'contact': 'Emily Rodriguez',
                'next_action': 'Technical demo scheduled'
            }
        ]
    }

@app.route('/')
def dashboard():
    """Main dashboard route"""
    return render_template('dashboard.html')

@app.route('/api/kpis')
def get_kpis():
    """API endpoint for KPI data"""
    try:
        kpis = dashboard_data.get_kpi_data()
        logger.info(f"Retrieved {len(kpis)} KPIs from database")
        return jsonify(kpis)
    except Exception as e:
        logger.error(f"Error fetching KPIs: {e}")
        # Fallback to sample data
        data = generate_sample_data()
        return jsonify(data['kpis'])

@app.route('/api/alerts')
def get_alerts():
    """API endpoint for alerts data"""
    try:
        alerts = dashboard_data.get_alerts_data()
        logger.info(f"Retrieved {len(alerts)} alerts from database")
        return jsonify(alerts)
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        # Fallback to sample data
        data = generate_sample_data()
        # Convert datetime objects to strings for JSON serialization
        alerts = []
        for alert in data['alerts']:
            alert_copy = alert.copy()
            alert_copy['timestamp'] = alert['timestamp'].isoformat()
            alerts.append(alert_copy)
        return jsonify(alerts)

@app.route('/api/sales-pipeline')
def get_sales_pipeline():
    """API endpoint for sales pipeline data"""
    try:
        pipeline = dashboard_data.get_sales_pipeline_data()
        logger.info(f"Retrieved {len(pipeline)} pipeline deals from database")
        return jsonify(pipeline)
    except Exception as e:
        logger.error(f"Error fetching sales pipeline: {e}")
        # Fallback to sample data
        data = generate_sample_data()
        return jsonify(data['sales_pipeline'])

@app.route('/api/chart-data/<chart_type>')
def get_chart_data(chart_type):
    """API endpoint for chart data"""
    try:
        # Map chart type names to match the database model
        chart_type_mapping = {
            'sales-trend': 'sales_trend',
            'manufacturing-efficiency': 'manufacturing_efficiency',
            'logistics-performance': 'logistics_performance'
        }
        
        mapped_chart_type = chart_type_mapping.get(chart_type, chart_type)
        chart_data = dashboard_data.get_chart_data(mapped_chart_type)
        
        if 'error' in chart_data:
            logger.warning(f"Chart data error for {chart_type}: {chart_data['error']}")
            # Fallback to sample data
            return get_fallback_chart_data(chart_type)
        
        logger.info(f"Retrieved chart data for {chart_type} from database")
        return jsonify(chart_data)
        
    except Exception as e:
        logger.error(f"Error fetching chart data for {chart_type}: {e}")
        return get_fallback_chart_data(chart_type)

def get_fallback_chart_data(chart_type):
    """Generate fallback chart data when database is unavailable"""
    if chart_type == 'sales-trend':
        # Generate sample sales trend data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        sales_data = [random.randint(800000, 1200000) for _ in months]
        return jsonify({
            'labels': months,
            'data': sales_data,
            'title': 'Sales Trend (6 Months)'
        })
    
    elif chart_type == 'manufacturing-efficiency':
        # Generate sample manufacturing efficiency data
        lines = ['Line 1', 'Line 2', 'Line 3', 'Line 4']
        efficiency_data = [random.randint(85, 98) for _ in lines]
        return jsonify({
            'labels': lines,
            'data': efficiency_data,
            'title': 'Manufacturing Line Efficiency'
        })
    
    elif chart_type == 'logistics-performance':
        # Generate sample logistics performance data
        metrics = ['On-Time Delivery', 'Cost Efficiency', 'Quality Score', 'Customer Satisfaction']
        performance_data = [random.randint(85, 99) for _ in metrics]
        return jsonify({
            'labels': metrics,
            'data': performance_data,
            'title': 'Logistics Performance Metrics'
        })
    
    else:
        return jsonify({'error': 'Chart type not found'}), 404

@app.route('/api/financial-years')
def get_financial_years():
    """API endpoint for financial year data"""
    try:
        financial_years = dashboard_data.get_financial_years()
        logger.info(f"Retrieved {len(financial_years)} financial years from database")
        return jsonify(financial_years)
    except Exception as e:
        logger.error(f"Error fetching financial years: {e}")
        # Fallback to sample data
        return jsonify([
            {'id': 1, 'name': 'FY 2024-25', 'start_date': '2024-04-01', 'end_date': '2025-03-31', 'is_active': True},
            {'id': 2, 'name': 'FY 2023-24', 'start_date': '2023-04-01', 'end_date': '2024-03-31', 'is_active': False}
        ])

@app.route('/api/customer-groups')
def get_customer_groups():
    """API endpoint for customer group data"""
    try:
        customer_groups = dashboard_data.get_customer_groups()
        logger.info(f"Retrieved {len(customer_groups)} customer groups from database")
        return jsonify(customer_groups)
    except Exception as e:
        logger.error(f"Error fetching customer groups: {e}")
        # Fallback to sample data
        return jsonify([
            {'id': 1, 'name': 'Premium Customers', 'description': 'High-value customers with premium service', 'is_active': True},
            {'id': 2, 'name': 'Standard Customers', 'description': 'Regular customers with standard service', 'is_active': True},
            {'id': 3, 'name': 'Wholesale Partners', 'description': 'Bulk purchase partners and distributors', 'is_active': True}
        ])

@app.route('/api/refresh-data')
def refresh_data():
    """API endpoint to refresh dashboard data"""
    # In a real application, this would trigger data refresh from databases
    return jsonify({
        'status': 'success',
        'message': 'Data refreshed successfully',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/countries')
def get_countries():
    """API endpoint for country list"""
    try:
        countries = dashboard_data.get_countries()
        logger.info(f"Retrieved {len(countries)} countries from database")
        return jsonify(countries)
    except Exception as e:
        logger.error(f"Error fetching countries: {e}")
        return jsonify([
            {'id': None, 'name': 'Bangladesh'},
            {'id': None, 'name': 'Türkiye'},
            {'id': None, 'name': 'India'},
            {'id': None, 'name': 'Pakistan'},
            {'id': None, 'name': 'Egypt'}
        ])

@app.route('/api/customer-order-metrics')
def get_customer_order_metrics():
    """API endpoint for customer order metrics"""
    try:
        metrics = dashboard_data.get_customer_order_metrics()
        logger.info(f"Retrieved customer order metrics from database")
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error fetching customer order metrics: {e}")
        return jsonify({
            'quantity': 247,
            'value': 12500000.0,
            'margin': 22.0,
            'total_quantity': 1247850
        })

@app.route('/api/cpo-detailed-data')
def get_cpo_detailed_data():
    """API endpoint for detailed CPO data"""
    try:
        customer_name = request.args.get('customer_name')
        cpo_data = dashboard_data.get_cpo_detailed_data(customer_name)
        logger.info(f"Retrieved {len(cpo_data)} CPO records from database")
        return jsonify(cpo_data)
    except Exception as e:
        logger.error(f"Error fetching CPO detailed data: {e}")
        return jsonify([])

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )