#!/usr/bin/env python3
"""
Comprehensive transformation utilities for IPMS legacy data migration
Handles data cleaning, normalization, and validation
"""

import re
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from dateutil import parser as dateparser
from datetime import datetime, date
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Comprehensive country mapping
COUNTRY_MAP = {
    "United States": "US", "USA": "US", "US": "US", "United States of America": "US",
    "Canada": "CA", "CA": "CA",
    "United Kingdom": "GB", "UK": "GB", "GB": "GB", "Great Britain": "GB",
    "Germany": "DE", "DE": "DE", "Deutschland": "DE", "Federal Republic of Germany": "DE",
    "France": "FR", "FR": "FR", "République française": "FR",
    "Japan": "JP", "JP": "JP", "Nippon": "JP", "Nihon": "JP",
    "China": "CN", "CN": "CN", "People's Republic of China": "CN", "PRC": "CN",
    "India": "IN", "IN": "IN", "Republic of India": "IN",
    "Australia": "AU", "AU": "AU", "Commonwealth of Australia": "AU",
    "Brazil": "BR", "BR": "BR", "Brasil": "BR", "Federative Republic of Brazil": "BR",
    "Italy": "IT", "IT": "IT", "Italia": "IT",
    "Spain": "ES", "ES": "ES", "España": "ES",
    "Netherlands": "NL", "NL": "NL", "Holland": "NL",
    "Switzerland": "CH", "CH": "CH", "Schweiz": "CH", "Suisse": "CH",
    "Sweden": "SE", "SE": "SE", "Sverige": "SE",
    "South Korea": "KR", "KR": "KR", "Korea": "KR", "Republic of Korea": "KR"
}

# Status normalization mappings
STATUS_MAPPINGS = {
    'patent': {
        'pending': ['pending', 'filed', 'under examination', 'prosecution', 'in prosecution'],
        'granted': ['granted', 'issued', 'patented', 'allowed'],
        'abandoned': ['abandoned', 'withdrawn', 'dismissed'],
        'rejected': ['rejected', 'refused', 'denied'],
        'expired': ['expired', 'lapsed', 'terminated']
    },
    'trademark': {
        'pending': ['pending', 'filed', 'under examination', 'published', 'application'],
        'registered': ['registered', 'registration', 'issued', 'granted'],
        'opposed': ['opposed', 'opposition', 'contested'],
        'cancelled': ['cancelled', 'canceled', 'revoked'],
        'abandoned': ['abandoned', 'withdrawn', 'dismissed'],
        'expired': ['expired', 'lapsed', 'terminated']
    },
    'copyright': {
        'pending': ['pending', 'filed', 'under examination', 'application'],
        'registered': ['registered', 'registration', 'issued', 'granted'],
        'rejected': ['rejected', 'refused', 'denied'],
        'abandoned': ['abandoned', 'withdrawn', 'dismissed']
    }
}

# Priority mappings
PRIORITY_MAP = {
    'low': ['low', 'minor', 'routine'],
    'medium': ['medium', 'normal', 'standard', 'moderate'],
    'high': ['high', 'important', 'urgent'],
    'critical': ['critical', 'emergency', 'immediate', 'asap']
}

def clean_string(value: Any) -> str:
    """Clean and normalize string values"""
    if pd.isna(value) or value is None:
        return ""
    
    # Convert to string and strip whitespace
    cleaned = str(value).strip()
    
    # Remove multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Handle common legacy data issues
    if cleaned.lower() in ['n/a', 'na', 'null', 'none', 'unknown', 'tbd', 'pending']:
        return ""
    
    return cleaned

def iso2(country_raw: str) -> Optional[str]:
    """Convert country name to ISO 2-letter code"""
    if not country_raw:
        return None
    
    country_clean = clean_string(country_raw).strip()
    if not country_clean:
        return None
    
    # Direct lookup
    result = COUNTRY_MAP.get(country_clean)
    if result:
        return result
    
    # Case-insensitive lookup
    for key, value in COUNTRY_MAP.items():
        if key.lower() == country_clean.lower():
            return value
    
    # Partial match for common variations
    country_lower = country_clean.lower()
    if 'united states' in country_lower or 'america' in country_lower:
        return 'US'
    elif 'united kingdom' in country_lower or 'britain' in country_lower:
        return 'GB'
    elif 'germany' in country_lower or 'deutschland' in country_lower:
        return 'DE'
    
    logger.warning(f"Unknown country: {country_raw}")
    return None

def to_date(value: Any, default_format: str = None) -> Optional[str]:
    """Parse various date formats to ISO format"""
    if pd.isna(value) or not value:
        return None
    
    date_str = clean_string(value)
    if not date_str:
        return None
    
    # Handle obviously bad dates
    bad_dates = ['00/00/0000', '1900-01-01', '0000-00-00', '01/01/1900']
    if date_str in bad_dates:
        return None
    
    try:
        # Try parsing with dateutil
        parsed_date = dateparser.parse(date_str, dayfirst=False, yearfirst=False)
        if parsed_date:
            # Validate reasonable date range for IP data
            if 1900 <= parsed_date.year <= 2050:
                return parsed_date.date().isoformat()
            else:
                logger.warning(f"Date out of reasonable range: {date_str}")
                return None
        
    except (ValueError, TypeError, OverflowError) as e:
        logger.warning(f"Failed to parse date '{date_str}': {e}")
    
    return None

def split_name(name: str) -> Dict[str, str]:
    """Split name into first and last name components"""
    if not name:
        return {"first_name": "", "last_name": ""}
    
    name_clean = clean_string(name)
    if not name_clean:
        return {"first_name": "", "last_name": ""}
    
    # Handle "Last, First" format
    if "," in name_clean:
        parts = [p.strip() for p in name_clean.split(",")]
        if len(parts) >= 2:
            return {
                "first_name": parts[1].title(),
                "last_name": parts[0].title()
            }
    
    # Handle "First Last" format
    parts = name_clean.split()
    if len(parts) == 1:
        return {"first_name": "", "last_name": parts[0].title()}
    elif len(parts) == 2:
        return {
            "first_name": parts[0].title(),
            "last_name": parts[1].title()
        }
    elif len(parts) > 2:
        # Assume first word is first name, rest is last name
        return {
            "first_name": parts[0].title(),
            "last_name": " ".join(parts[1:]).title()
        }
    
    return {"first_name": "", "last_name": name_clean.title()}

def parse_classes(value: Any) -> List[int]:
    """Parse Nice classes or other classification numbers"""
    if pd.isna(value) or not value:
        return []
    
    classes_str = clean_string(value)
    if not classes_str:
        return []
    
    # Extract numbers from string
    numbers = []
    # Split by common separators
    parts = re.split(r'[,;\s]+', classes_str)
    
    for part in parts:
        part = part.strip()
        if part.isdigit():
            num = int(part)
            if 1 <= num <= 45:  # Valid Nice class range
                numbers.append(num)
        else:
            # Try to extract numbers from mixed content
            digits = re.findall(r'\d+', part)
            for digit in digits:
                num = int(digit)
                if 1 <= num <= 45:
                    numbers.append(num)
    
    return sorted(list(set(numbers)))  # Remove duplicates and sort

def normalize_status(status: str, entity_type: str) -> str:
    """Normalize status values based on entity type"""
    if not status:
        return 'pending'  # Default status
    
    status_clean = clean_string(status).lower()
    if not status_clean:
        return 'pending'
    
    # Get mappings for entity type
    mappings = STATUS_MAPPINGS.get(entity_type, {})
    
    # Find matching normalized status
    for normalized, variants in mappings.items():
        if status_clean in [v.lower() for v in variants]:
            return normalized
    
    # If no match found, try partial matching
    for normalized, variants in mappings.items():
        for variant in variants:
            if variant.lower() in status_clean or status_clean in variant.lower():
                return normalized
    
    logger.warning(f"Unknown {entity_type} status: {status}")
    return 'pending'

def normalize_priority(priority: str) -> str:
    """Normalize priority values"""
    if not priority:
        return 'medium'  # Default priority
    
    priority_clean = clean_string(priority).lower()
    if not priority_clean:
        return 'medium'
    
    # Find matching normalized priority
    for normalized, variants in PRIORITY_MAP.items():
        if priority_clean in variants:
            return normalized
    
    logger.warning(f"Unknown priority: {priority}")
    return 'medium'

def parse_phone(phone: str) -> str:
    """Clean and normalize phone numbers"""
    if not phone:
        return ""
    
    phone_clean = clean_string(phone)
    if not phone_clean:
        return ""
    
    # Remove common bad values
    bad_phones = ['000-000-0000', '0000000000', 'n/a', 'unknown']
    if phone_clean.lower() in bad_phones:
        return ""
    
    # Extract digits only
    digits = re.sub(r'[^\d]', '', phone_clean)
    
    # Validate length (US format)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    elif len(digits) >= 10:
        # International format
        return f"+{digits}"
    
    # If can't normalize, return cleaned original
    return phone_clean

def parse_email(email: str) -> str:
    """Validate and clean email addresses"""
    if not email:
        return ""
    
    email_clean = clean_string(email).lower()
    if not email_clean:
        return ""
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, email_clean):
        return email_clean
    
    # Try to fix common issues
    if '_at_' in email_clean:
        email_clean = email_clean.replace('_at_', '@')
        if re.match(email_pattern, email_clean):
            return email_clean
    
    logger.warning(f"Invalid email format: {email}")
    return ""

def parse_inventors(inventors_str: str) -> List[Dict[str, str]]:
    """Parse inventor string into structured data"""
    if not inventors_str:
        return []
    
    inventors_clean = clean_string(inventors_str)
    if not inventors_clean:
        return []
    
    # Split by common separators
    inventors = []
    parts = re.split(r'[;|]', inventors_clean)
    
    for part in parts:
        part = part.strip()
        if part:
            name_parts = split_name(part)
            if name_parts['first_name'] or name_parts['last_name']:
                inventors.append(name_parts)
    
    return inventors

def parse_json_field(value: Any) -> Dict[str, Any]:
    """Parse JSON-like string fields"""
    if pd.isna(value) or not value:
        return {}
    
    value_str = clean_string(value)
    if not value_str:
        return {}
    
    try:
        # Try parsing as JSON
        return json.loads(value_str)
    except json.JSONDecodeError:
        # Try to extract key-value pairs manually
        result = {}
        # Look for patterns like key: value or key="value"
        patterns = [
            r'"([^"]+)":\s*"([^"]*)"',
            r'(\w+):\s*"([^"]*)"',
            r'(\w+):\s*([^,}]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, value_str)
            for key, val in matches:
                result[key.strip()] = val.strip()
        
        return result

def calculate_expiry_date(filing_date: str, jurisdiction: str, ip_type: str) -> Optional[str]:
    """Calculate expiry date based on filing date and jurisdiction rules"""
    if not filing_date:
        return None
    
    try:
        filing_dt = datetime.fromisoformat(filing_date)
    except ValueError:
        return None
    
    # Default patent term: 20 years from filing
    if ip_type == 'patent':
        if jurisdiction in ['US', 'EP', 'GB', 'DE', 'JP']:
            expiry_dt = filing_dt.replace(year=filing_dt.year + 20)
        else:
            expiry_dt = filing_dt.replace(year=filing_dt.year + 20)
    
    # Trademark renewal periods vary
    elif ip_type == 'trademark':
        if jurisdiction == 'US':
            expiry_dt = filing_dt.replace(year=filing_dt.year + 10)
        elif jurisdiction in ['EP', 'GB', 'DE']:
            expiry_dt = filing_dt.replace(year=filing_dt.year + 10)
        else:
            expiry_dt = filing_dt.replace(year=filing_dt.year + 10)
    
    # Copyright typically lasts much longer
    elif ip_type == 'copyright':
        expiry_dt = filing_dt.replace(year=filing_dt.year + 95)  # Corporate work
    
    else:
        return None
    
    return expiry_dt.date().isoformat()

def validate_data_quality(df: pd.DataFrame, entity_type: str) -> Dict[str, Any]:
    """Validate data quality and return quality metrics"""
    total_rows = len(df)
    if total_rows == 0:
        return {"total_rows": 0, "quality_score": 0, "issues": []}
    
    issues = []
    quality_metrics = {
        "total_rows": total_rows,
        "complete_records": 0,
        "missing_critical_fields": 0,
        "invalid_dates": 0,
        "invalid_emails": 0,
        "duplicate_records": 0
    }
    
    # Check for duplicates
    if 'external_ref' in df.columns:
        duplicates = df['external_ref'].duplicated().sum()
        quality_metrics["duplicate_records"] = duplicates
        if duplicates > 0:
            issues.append(f"{duplicates} duplicate external references found")
    
    # Entity-specific validation
    if entity_type == 'clients':
        # Check critical fields
        critical_fields = ['client_name', 'email']
        for field in critical_fields:
            if field in df.columns:
                missing = df[field].isna().sum() + (df[field] == "").sum()
                if missing > 0:
                    quality_metrics["missing_critical_fields"] += missing
                    issues.append(f"{missing} records missing {field}")
        
        # Validate emails
        if 'email' in df.columns:
            valid_emails = df['email'].apply(lambda x: bool(parse_email(x)) if x else False).sum()
            invalid_emails = total_rows - valid_emails
            quality_metrics["invalid_emails"] = invalid_emails
            if invalid_emails > 0:
                issues.append(f"{invalid_emails} invalid email addresses")
    
    elif entity_type in ['patents', 'trademarks', 'copyrights']:
        # Check critical fields
        critical_fields = ['title', 'client_id', 'status']
        for field in critical_fields:
            if field in df.columns:
                missing = df[field].isna().sum() + (df[field] == "").sum()
                if missing > 0:
                    quality_metrics["missing_critical_fields"] += missing
                    issues.append(f"{missing} records missing {field}")
        
        # Validate dates
        date_fields = ['filing_date', 'grant_date', 'registration_date']
        for field in date_fields:
            if field in df.columns:
                invalid_dates = df[field].apply(
                    lambda x: to_date(x) is None if x else False
                ).sum()
                quality_metrics["invalid_dates"] += invalid_dates
                if invalid_dates > 0:
                    issues.append(f"{invalid_dates} invalid {field} values")
    
    # Calculate quality score (0-100)
    total_issues = sum([
        quality_metrics["missing_critical_fields"],
        quality_metrics["invalid_dates"],
        quality_metrics["invalid_emails"],
        quality_metrics["duplicate_records"]
    ])
    
    quality_score = max(0, 100 - (total_issues / total_rows * 100))
    quality_metrics["quality_score"] = round(quality_score, 2)
    quality_metrics["issues"] = issues
    
    return quality_metrics

# Legacy function aliases for backward compatibility
def split_name_legacy(name: str) -> str:
    """Legacy function - returns full name string"""
    name_parts = split_name(name)
    if name_parts['first_name'] and name_parts['last_name']:
        return f"{name_parts['first_name']} {name_parts['last_name']}"
    return name_parts['last_name'] or name_parts['first_name']

# Export commonly used functions
__all__ = [
    'clean_string', 'iso2', 'to_date', 'split_name', 'parse_classes',
    'normalize_status', 'normalize_priority', 'parse_phone', 'parse_email',
    'parse_inventors', 'parse_json_field', 'calculate_expiry_date',
    'validate_data_quality', 'split_name_legacy'
]
