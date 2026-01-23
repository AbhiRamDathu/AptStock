import pandas as pd
from pathlib import Path
import logging
from io import StringIO

logger = logging.getLogger(__name__)

class SampleDataService:
    """Loads Hyderabad CSV as sample demo data"""
    
    @staticmethod
    def get_sample_csv_data():
        """Load Hyderabad CSV file"""
        try:
            csv_path = Path(__file__).parent.parent / "data" / "Hyderabad_Supermarket_60Days_POS_Data.csv"
            
            if not csv_path.exists():
                logger.error(f"Sample file not found: {csv_path}")
                return None
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            
            logger.info("Sample CSV loaded successfully")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error loading sample CSV: {str(e)}")
            return None
