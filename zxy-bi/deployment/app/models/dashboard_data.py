"""
Dashboard data models and queries for ZXY Business Intelligence Dashboard
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from config.database import get_database

logger = logging.getLogger(__name__)

class DashboardDataModel:
    """Data model for dashboard operations"""
    
    def __init__(self):
        self.db = get_database()
    
    def get_kpi_data(self) -> List[Dict[str, Any]]:
        """Get KPI data for the dashboard"""
        try:
            # Sample KPI queries - adjust these based on your actual database schema
            kpi_queries = {
                'total_sales': """
                    SELECT 
                        COALESCE(SUM(amount), 0) as value,
                        'Total Sales' as label,
                        'sales' as icon_type,
                        '+15%' as trend
                    FROM sales_data 
                    WHERE date >= DATEADD(month, -1, GETDATE())
                """,
                'active_prospects': """
                    SELECT 
                        COUNT(*) as value,
                        'Active Prospects' as label,
                        'sales' as icon_type,
                        '+8%' as trend
                    FROM prospects 
                    WHERE status = 'active'
                """,
                'pipeline_value': """
                    SELECT 
                        COALESCE(SUM(value), 0) as value,
                        'Pipeline Value' as label,
                        'sales' as icon_type,
                        '+23%' as trend
                    FROM sales_pipeline 
                    WHERE status IN ('qualified', 'proposal', 'negotiation')
                """,
                'factory_utilization': """
                    SELECT 
                        COALESCE(AVG(utilization_rate), 0) as value,
                        'Factory Utilization' as label,
                        'manufacturing' as icon_type,
                        '+5%' as trend
                    FROM manufacturing_metrics 
                    WHERE date >= DATEADD(day, -7, GETDATE())
                """,
                'on_time_delivery': """
                    SELECT 
                        COALESCE(
                            (COUNT(CASE WHEN delivery_date <= promised_date THEN 1 END) * 100.0 / COUNT(*)), 
                            0
                        ) as value,
                        'On-Time Delivery' as label,
                        'logistics' as icon_type,
                        '+2%' as trend
                    FROM shipments 
                    WHERE delivery_date >= DATEADD(month, -1, GETDATE())
                """,
                'revenue_fytd': """
                    SELECT 
                        COALESCE(SUM(revenue), 0) as value,
                        'Revenue (FYTD)' as label,
                        'financial' as icon_type,
                        '+18%' as trend
                    FROM financial_data 
                    WHERE fiscal_year = YEAR(GETDATE())
                """
            }
            
            kpis = []
            for kpi_name, query in kpi_queries.items():
                try:
                    result = self.db.execute_query(query)
                    if not result.empty:
                        row = result.iloc[0]
                        kpi = {
                            'id': kpi_name,
                            'value': self._format_kpi_value(row['value'], kpi_name),
                            'label': row['label'],
                            'icon_type': row['icon_type'],
                            'trend': row['trend']
                        }
                        kpis.append(kpi)
                except Exception as e:
                    logger.warning(f"Failed to fetch KPI {kpi_name}: {e}")
                    # Fallback to sample data
                    kpis.append(self._get_fallback_kpi(kpi_name))
            
            return kpis if kpis else self._get_sample_kpis()
            
        except Exception as e:
            logger.error(f"Error fetching KPI data: {e}")
            return self._get_sample_kpis()
    
    def get_alerts_data(self) -> List[Dict[str, Any]]:
        """Get alerts data for the dashboard"""
        try:
            query = """
                SELECT 
                    title,
                    description,
                    priority,
                    created_date,
                    status
                FROM system_alerts 
                WHERE status = 'active' 
                ORDER BY priority DESC, created_date DESC
                LIMIT 10
            """
            
            result = self.db.execute_query(query)
            
            alerts = []
            for _, row in result.iterrows():
                alert = {
                    'title': row['title'],
                    'description': row['description'],
                    'priority': row['priority'].lower(),
                    'timestamp': row['created_date'].strftime('%H:%M') if pd.notna(row['created_date']) else 'N/A'
                }
                alerts.append(alert)
            
            return alerts if alerts else self._get_sample_alerts()
            
        except Exception as e:
            logger.error(f"Error fetching alerts data: {e}")
            return self._get_sample_alerts()
    
    def get_sales_pipeline_data(self) -> List[Dict[str, Any]]:
        """Get sales pipeline data"""
        try:
            query = """
                SELECT 
                    company_name,
                    contact_person,
                    deal_value,
                    stage,
                    probability,
                    expected_close_date,
                    source
                FROM sales_pipeline 
                WHERE status = 'active'
                ORDER BY deal_value DESC
                LIMIT 20
            """
            
            result = self.db.execute_query(query)
            
            pipeline = []
            for _, row in result.iterrows():
                deal = {
                    'company': row['company_name'],
                    'contact': row['contact_person'],
                    'value': f"${row['deal_value']:,.0f}" if pd.notna(row['deal_value']) else '$0',
                    'stage': row['stage'],
                    'probability': f"{row['probability']}%" if pd.notna(row['probability']) else '0%',
                    'close_date': row['expected_close_date'].strftime('%Y-%m-%d') if pd.notna(row['expected_close_date']) else 'TBD',
                    'source': row['source'] if pd.notna(row['source']) else 'Direct'
                }
                pipeline.append(deal)
            
            return pipeline if pipeline else self._get_sample_pipeline()
            
        except Exception as e:
            logger.error(f"Error fetching sales pipeline data: {e}")
            return self._get_sample_pipeline()
    
    def get_financial_years(self) -> List[Dict[str, Any]]:
        """Get financial year data for time selector"""
        try:
            query = """
                SELECT 
                    FinancialYearName,
                    FinancialYearID,
                    StartDate,
                    EndDate,
                    IsActive
                FROM zFINANCIAL_YEAR 
                ORDER BY StartDate DESC
            """
            
            result = self.db.execute_query(query)
            
            financial_years = []
            for _, row in result.iterrows():
                fy = {
                    'id': row['FinancialYearID'] if pd.notna(row['FinancialYearID']) else None,
                    'name': row['FinancialYearName'] if pd.notna(row['FinancialYearName']) else 'Unknown',
                    'start_date': row['StartDate'].strftime('%Y-%m-%d') if pd.notna(row['StartDate']) else None,
                    'end_date': row['EndDate'].strftime('%Y-%m-%d') if pd.notna(row['EndDate']) else None,
                    'is_active': bool(row['IsActive']) if pd.notna(row['IsActive']) else False
                }
                financial_years.append(fy)
            
            return financial_years if financial_years else self._get_sample_financial_years()
            
        except Exception as e:
            logger.error(f"Error fetching financial years: {e}")
            return self._get_sample_financial_years()

    def get_customer_groups(self) -> List[Dict[str, Any]]:
        """Get customer group data for customer group selector"""
        try:
            query = """
                SELECT 
                    CustomerGroupID,
                    CustomerGroupName,
                    Description,
                    IsActive
                FROM zCustomer_Group 
                WHERE IsActive = 1
                ORDER BY CustomerGroupName ASC
            """
            
            result = self.db.execute_query(query)
            
            customer_groups = []
            for _, row in result.iterrows():
                cg = {
                    'id': row['CustomerGroupID'] if pd.notna(row['CustomerGroupID']) else None,
                    'name': row['CustomerGroupName'] if pd.notna(row['CustomerGroupName']) else 'Unknown',
                    'description': row['Description'] if pd.notna(row['Description']) else '',
                    'is_active': bool(row['IsActive']) if pd.notna(row['IsActive']) else True
                }
                customer_groups.append(cg)
            
            return customer_groups if customer_groups else self._get_sample_customer_groups()
            
        except Exception as e:
            logger.error(f"Error fetching customer groups: {e}")
            return self._get_sample_customer_groups()

    def get_chart_data(self, chart_type: str) -> Dict[str, Any]:
        """Get chart data based on chart type"""
        try:
            if chart_type == 'sales_trend':
                return self._get_sales_trend_data()
            elif chart_type == 'manufacturing_efficiency':
                return self._get_manufacturing_efficiency_data()
            elif chart_type == 'logistics_performance':
                return self._get_logistics_performance_data()
            else:
                return {'error': 'Unknown chart type'}
        except Exception as e:
            logger.error(f"Error fetching chart data for {chart_type}: {e}")
            return {'error': str(e)}
    
    def _get_sales_trend_data(self) -> Dict[str, Any]:
        """Get sales trend chart data"""
        try:
            query = """
                SELECT 
                    DATE_FORMAT(date, '%Y-%m') as month,
                    SUM(amount) as sales
                FROM sales_data 
                WHERE date >= DATEADD(month, -12, GETDATE())
                GROUP BY DATE_FORMAT(date, '%Y-%m')
                ORDER BY month
            """
            
            result = self.db.execute_query(query)
            
            if not result.empty:
                return {
                    'labels': result['month'].tolist(),
                    'data': result['sales'].tolist(),
                    'title': 'Sales Trend (Last 12 Months)'
                }
            else:
                return self._get_sample_chart_data('sales_trend')
                
        except Exception as e:
            logger.warning(f"Failed to fetch sales trend data: {e}")
            return self._get_sample_chart_data('sales_trend')
    
    def _get_manufacturing_efficiency_data(self) -> Dict[str, Any]:
        """Get manufacturing efficiency chart data"""
        try:
            query = """
                SELECT 
                    factory_name,
                    AVG(efficiency_rate) as efficiency
                FROM manufacturing_metrics 
                WHERE date >= DATEADD(month, -1, GETDATE())
                GROUP BY factory_name
                ORDER BY efficiency DESC
            """
            
            result = self.db.execute_query(query)
            
            if not result.empty:
                return {
                    'labels': result['factory_name'].tolist(),
                    'data': result['efficiency'].tolist(),
                    'title': 'Manufacturing Efficiency by Factory'
                }
            else:
                return self._get_sample_chart_data('manufacturing_efficiency')
                
        except Exception as e:
            logger.warning(f"Failed to fetch manufacturing efficiency data: {e}")
            return self._get_sample_chart_data('manufacturing_efficiency')
    
    def _get_logistics_performance_data(self) -> Dict[str, Any]:
        """Get logistics performance chart data"""
        try:
            query = """
                SELECT 
                    region,
                    AVG(delivery_time) as avg_delivery_time,
                    COUNT(*) as shipment_count
                FROM shipments 
                WHERE delivery_date >= DATEADD(month, -1, GETDATE())
                GROUP BY region
                ORDER BY avg_delivery_time
            """
            
            result = self.db.execute_query(query)
            
            if not result.empty:
                return {
                    'labels': result['region'].tolist(),
                    'data': result['avg_delivery_time'].tolist(),
                    'title': 'Average Delivery Time by Region'
                }
            else:
                return self._get_sample_chart_data('logistics_performance')
                
        except Exception as e:
            logger.warning(f"Failed to fetch logistics performance data: {e}")
            return self._get_sample_chart_data('logistics_performance')
    
    def _format_kpi_value(self, value: float, kpi_type: str) -> str:
        """Format KPI values based on type"""
        if kpi_type in ['total_sales', 'pipeline_value', 'revenue_fytd']:
            if value >= 1000000:
                return f"${value/1000000:.1f}M"
            elif value >= 1000:
                return f"${value/1000:.0f}K"
            else:
                return f"${value:.0f}"
        elif kpi_type in ['factory_utilization', 'on_time_delivery']:
            return f"{value:.0f}%"
        else:
            return f"{value:.0f}"
    
    def _get_fallback_kpi(self, kpi_name: str) -> Dict[str, Any]:
        """Get fallback KPI data when database query fails"""
        fallback_kpis = {
            'total_sales': {'id': 'total_sales', 'value': '$2.8M', 'label': 'Total Sales', 'icon_type': 'sales', 'trend': '+15%'},
            'active_prospects': {'id': 'active_prospects', 'value': '247', 'label': 'Active Prospects', 'icon_type': 'sales', 'trend': '+8%'},
            'pipeline_value': {'id': 'pipeline_value', 'value': '$12.5M', 'label': 'Pipeline Value', 'icon_type': 'sales', 'trend': '+23%'},
            'factory_utilization': {'id': 'factory_utilization', 'value': '78%', 'label': 'Factory Utilization', 'icon_type': 'manufacturing', 'trend': '+5%'},
            'on_time_delivery': {'id': 'on_time_delivery', 'value': '94%', 'label': 'On-Time Delivery', 'icon_type': 'logistics', 'trend': '+2%'},
            'revenue_fytd': {'id': 'revenue_fytd', 'value': '$45.2M', 'label': 'Revenue (FYTD)', 'icon_type': 'financial', 'trend': '+18%'}
        }
        return fallback_kpis.get(kpi_name, {'id': kpi_name, 'value': 'N/A', 'label': 'Unknown', 'icon_type': 'sales', 'trend': '0%'})
    
    def _get_sample_kpis(self) -> List[Dict[str, Any]]:
        """Get sample KPI data as fallback"""
        return [
            {'id': 'total_sales', 'value': '$2.8M', 'label': 'Total Sales', 'icon_type': 'sales', 'trend': '+15%'},
            {'id': 'active_prospects', 'value': '247', 'label': 'Active Prospects', 'icon_type': 'sales', 'trend': '+8%'},
            {'id': 'pipeline_value', 'value': '$12.5M', 'label': 'Pipeline Value', 'icon_type': 'sales', 'trend': '+23%'},
            {'id': 'factory_utilization', 'value': '78%', 'label': 'Factory Utilization', 'icon_type': 'manufacturing', 'trend': '+5%'},
            {'id': 'on_time_delivery', 'value': '94%', 'label': 'On-Time Delivery', 'icon_type': 'logistics', 'trend': '+2%'},
            {'id': 'revenue_fytd', 'value': '$45.2M', 'label': 'Revenue (FYTD)', 'icon_type': 'financial', 'trend': '+18%'}
        ]
    
    def _get_sample_alerts(self) -> List[Dict[str, Any]]:
        """Get sample alerts data as fallback"""
        return [
            {'title': 'High Priority Order', 'description': 'Urgent order from key client requires immediate attention', 'priority': 'high', 'timestamp': '14:30'},
            {'title': 'Production Delay', 'description': 'Factory B experiencing 2-hour delay in production schedule', 'priority': 'medium', 'timestamp': '13:45'},
            {'title': 'Inventory Alert', 'description': 'Raw material stock running low for Product Line C', 'priority': 'medium', 'timestamp': '12:15'},
            {'title': 'System Update', 'description': 'Scheduled maintenance completed successfully', 'priority': 'low', 'timestamp': '11:00'}
        ]
    
    def _get_sample_pipeline(self) -> List[Dict[str, Any]]:
        """Get sample pipeline data as fallback"""
        return [
            {'company': 'Global Fashion Inc.', 'contact': 'Sarah Johnson', 'value': '$850,000', 'stage': 'Negotiation', 'probability': '75%', 'close_date': '2024-02-15', 'source': 'Trade Show'},
            {'company': 'European Retail Chain', 'contact': 'Michael Chen', 'value': '$620,000', 'stage': 'Proposal', 'probability': '60%', 'close_date': '2024-02-28', 'source': 'Referral'},
            {'company': 'American Brands LLC', 'contact': 'Lisa Rodriguez', 'value': '$450,000', 'stage': 'Qualified', 'probability': '40%', 'close_date': '2024-03-10', 'source': 'Website'},
            {'company': 'Asian Markets Co.', 'contact': 'David Kim', 'value': '$380,000', 'stage': 'Discovery', 'probability': '25%', 'close_date': '2024-03-20', 'source': 'Cold Call'}
        ]
    
    def _get_sample_financial_years(self) -> List[Dict[str, Any]]:
        """Get sample financial years data as fallback"""
        return [
            {'id': 1, 'name': 'FY 2024-25', 'start_date': '2024-04-01', 'end_date': '2025-03-31', 'is_active': True},
            {'id': 2, 'name': 'FY 2023-24', 'start_date': '2023-04-01', 'end_date': '2024-03-31', 'is_active': False},
            {'id': 3, 'name': 'FY 2022-23', 'start_date': '2022-04-01', 'end_date': '2023-03-31', 'is_active': False},
            {'id': 4, 'name': 'FY 2021-22', 'start_date': '2021-04-01', 'end_date': '2022-03-31', 'is_active': False}
        ]

    def _get_sample_customer_groups(self) -> List[Dict[str, Any]]:
        """Get sample customer groups data as fallback"""
        return [
            {'id': 1, 'name': 'Premium Customers', 'description': 'High-value customers with premium service', 'is_active': True},
            {'id': 2, 'name': 'Standard Customers', 'description': 'Regular customers with standard service', 'is_active': True},
            {'id': 3, 'name': 'Wholesale Partners', 'description': 'Bulk purchase partners and distributors', 'is_active': True},
            {'id': 4, 'name': 'Enterprise Clients', 'description': 'Large enterprise customers with custom solutions', 'is_active': True},
            {'id': 5, 'name': 'Retail Customers', 'description': 'Individual retail customers', 'is_active': True}
        ]

    def _get_sample_chart_data(self, chart_type: str) -> Dict[str, Any]:
        """Get sample chart data as fallback"""
        if chart_type == 'sales_trend':
            return {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'data': [2.1, 2.3, 2.8, 2.5, 3.1, 2.9],
                'title': 'Sales Trend (Last 6 Months)'
            }
        elif chart_type == 'manufacturing_efficiency':
            return {
                'labels': ['Factory A', 'Factory B', 'Factory C', 'Factory D'],
                'data': [85, 78, 92, 88],
                'title': 'Manufacturing Efficiency by Factory'
            }
        elif chart_type == 'logistics_performance':
            return {
                'labels': ['North America', 'Europe', 'Asia', 'South America'],
                'data': [3.2, 4.1, 2.8, 5.5],
                'title': 'Average Delivery Time by Region (Days)'
            }
        else:
            return {'labels': [], 'data': [], 'title': 'No Data Available'}

    def get_countries(self) -> List[Dict[str, Any]]:
        """Get country list from zCountry_Office table"""
        try:
            query = """
                SELECT DISTINCT
                    CountryID,
                    CountryName
                FROM zCountry_Office
                ORDER BY CountryName
            """
            result = self.db.execute_query(query)
            countries: List[Dict[str, Any]] = []
            for _, row in result.iterrows():
                countries.append({
                    'id': int(row['CountryID']) if 'CountryID' in result.columns and pd.notna(row['CountryID']) else None,
                    'name': row['CountryName'] if 'CountryName' in result.columns and pd.notna(row['CountryName']) else 'Unknown'
                })
            return countries if countries else self._get_sample_countries()
        except Exception as e:
            logger.error(f"Error fetching countries: {e}")
            return self._get_sample_countries()

    def _get_sample_countries(self) -> List[Dict[str, Any]]:
        """Fallback country list when database unavailable"""
        return [
            {'id': None, 'name': 'Bangladesh'},
            {'id': None, 'name': 'Türkiye'},
            {'id': None, 'name': 'India'},
            {'id': None, 'name': 'Pakistan'},
            {'id': None, 'name': 'Egypt'}
        ]