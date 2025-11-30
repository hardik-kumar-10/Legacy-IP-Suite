#!/usr/bin/env python3
"""
Comprehensive Data Validation System for IPMS
Validates data quality, business rules, and referential integrity
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime, date

from transform_utils import (
    validate_data_quality, to_date, iso2, parse_email, 
    parse_phone, normalize_status, parse_classes
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "legacy_csv"
VALIDATION_REPORT_DIR = ROOT / "data" / "validation_reports"
VALIDATION_REPORT_DIR.mkdir(parents=True, exist_ok=True)

class IPMSDataValidator:
    """Comprehensive data validator for IPMS migration"""
    
    def __init__(self):
        self.validation_results = {}
        self.errors = []
        self.warnings = []
    
    def validate_file(self, file_path: Path, entity_type: str) -> Dict[str, Any]:
        """Validate a single CSV file"""
        logger.info(f"Validating {entity_type} data from {file_path}")
        
        if not file_path.exists():
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            return {
                "entity_type": entity_type,
                "file_path": str(file_path),
                "status": "error",
                "error": error_msg,
                "quality_score": 0
            }
        
        try:
            # Load data
            df = pd.read_csv(file_path)
            
            # Basic data quality validation
            quality_metrics = validate_data_quality(df, entity_type)
            
            # Business rule validation
            business_validation = self._validate_business_rules(df, entity_type)
            
            # Referential integrity validation
            ref_validation = self._validate_referential_integrity(df, entity_type)
            
            # Combine results
            validation_result = {
                "entity_type": entity_type,
                "file_path": str(file_path),
                "status": "success",
                "record_count": len(df),
                "quality_metrics": quality_metrics,
                "business_validation": business_validation,
                "referential_validation": ref_validation,
                "overall_score": self._calculate_overall_score(quality_metrics, business_validation)
            }
            
            logger.info(f"Validation complete for {entity_type}. Overall score: {validation_result['overall_score']}")
            return validation_result
            
        except Exception as e:
            error_msg = f"Error validating {entity_type}: {str(e)}"
            logger.error(error_msg)
            return {
                "entity_type": entity_type,
                "file_path": str(file_path),
                "status": "error",
                "error": error_msg,
                "quality_score": 0
            }
    
    def _validate_business_rules(self, df: pd.DataFrame, entity_type: str) -> Dict[str, Any]:
        """Validate business-specific rules"""
        errors = []
        warnings = []
        
        if entity_type == "clients":
            errors.extend(self._validate_client_business_rules(df))
        elif entity_type == "patents":
            errors.extend(self._validate_patent_business_rules(df))
        elif entity_type == "trademarks":
            errors.extend(self._validate_trademark_business_rules(df))
        elif entity_type == "deadlines":
            errors.extend(self._validate_deadline_business_rules(df))
        
        return {
            "status": "completed",
            "errors": errors,
            "warnings": warnings,
            "rules_checked": len(errors) + len(warnings)
        }
    
    def _validate_client_business_rules(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Validate client-specific business rules"""
        errors = []
        
        # Rule: Email format validation for non-empty emails
        for idx, row in df.iterrows():
            email = row.get('email', '')
            if email and not parse_email(email):
                errors.append({
                    "rule": "Email format validation",
                    "record_id": row.get('client_id', idx),
                    "message": f"Invalid email format: {email}"
                })
        
        return errors
    
    def _validate_patent_business_rules(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Validate patent-specific business rules"""
        errors = []
        
        # Rule: Filing date should be before grant date
        for idx, row in df.iterrows():
            filing_date = to_date(row.get('filing_date'))
            grant_date = to_date(row.get('grant_date'))
            
            if filing_date and grant_date:
                if filing_date > grant_date:
                    errors.append({
                        "rule": "Filing date before grant date",
                        "record_id": row.get('patent_id', idx),
                        "message": f"Filing date ({filing_date}) is after grant date ({grant_date})"
                    })
        
        return errors
    
    def _validate_trademark_business_rules(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Validate trademark-specific business rules"""
        errors = []
        
        # Rule: Nice classes should be valid
        for idx, row in df.iterrows():
            nice_classes = row.get('nice_classes', '')
            if nice_classes:
                classes = parse_classes(nice_classes)
                if not classes:
                    errors.append({
                        "rule": "Valid Nice classes required",
                        "record_id": row.get('tm_id', idx),
                        "message": f"Invalid Nice classes: {nice_classes}"
                    })
        
        return errors
    
    def _validate_deadline_business_rules(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Validate deadline-specific business rules"""
        errors = []
        
        # Rule: Due date should be in the future for pending deadlines
        current_date = date.today().isoformat()
        pending_deadlines = df[df['status'].str.lower() == 'pending']
        
        for idx, row in pending_deadlines.iterrows():
            due_date = to_date(row.get('due_date'))
            if due_date and due_date < current_date:
                errors.append({
                    "rule": "Pending deadline due date validation",
                    "record_id": row.get('deadline_id', idx),
                    "message": f"Pending deadline has past due date: {due_date}"
                })
        
        return errors
    
    def _validate_referential_integrity(self, df: pd.DataFrame, entity_type: str) -> Dict[str, Any]:
        """Validate referential integrity between entities"""
        errors = []
        warnings = []
        
        # Load all client IDs for reference checking
        clients_file = DATA_DIR / "clients.csv"
        if clients_file.exists():
            clients_df = pd.read_csv(clients_file)
            valid_client_ids = set(clients_df['client_id'].astype(str))
            
            # Check client_id references
            if 'client_id' in df.columns:
                invalid_client_refs = df[~df['client_id'].isin(valid_client_ids)]
                for idx, row in invalid_client_refs.iterrows():
                    errors.append({
                        "rule": "Valid client reference",
                        "record_id": row.get(f"{entity_type[:-1]}_id", idx),
                        "message": f"Invalid client_id reference: {row['client_id']}"
                    })
        
        return {
            "status": "completed",
            "errors": errors,
            "warnings": warnings,
            "references_checked": len(df) if 'client_id' in df.columns else 0
        }
    
    def _calculate_overall_score(self, quality_metrics: Dict, business_validation: Dict) -> float:
        """Calculate overall validation score"""
        quality_score = quality_metrics.get('quality_score', 0)
        
        # Business rules score
        business_score = 100
        business_errors = len(business_validation.get('errors', []))
        if business_errors > 0:
            business_score = max(0, 100 - (business_errors * 5))
        
        # Weighted average
        overall_score = (quality_score * 0.7 + business_score * 0.3)
        return round(overall_score, 2)
    
    def validate_all(self) -> Dict[str, Any]:
        """Validate all data files"""
        logger.info("Starting comprehensive data validation")
        
        files_to_validate = [
            ("clients.csv", "clients"),
            ("patents.csv", "patents"),
            ("trademarks.csv", "trademarks"),
            ("deadlines.csv", "deadlines")
        ]
        
        results = {}
        overall_scores = []
        
        for filename, entity_type in files_to_validate:
            file_path = DATA_DIR / filename
            result = self.validate_file(file_path, entity_type)
            results[entity_type] = result
            
            if result.get('overall_score'):
                overall_scores.append(result['overall_score'])
        
        # Calculate overall system score
        system_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        
        validation_summary = {
            "validation_timestamp": datetime.now().isoformat(),
            "system_quality_score": round(system_score, 2),
            "entities_validated": len(results),
            "results": results
        }
        
        # Save validation report
        self._save_validation_report(validation_summary)
        
        logger.info(f"Validation complete. System quality score: {system_score}")
        return validation_summary
    
    def _save_validation_report(self, validation_summary: Dict[str, Any]):
        """Save validation report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = VALIDATION_REPORT_DIR / f"validation_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(validation_summary, f, indent=2, default=str)
        
        logger.info(f"Validation report saved to {report_file}")

def main():
    """Run comprehensive data validation"""
    print("IPMS Data Validation System")
    print("=" * 50)
    
    validator = IPMSDataValidator()
    
    try:
        validation_results = validator.validate_all()
        
        print(f"\nValidation Results:")
        print(f"System Quality Score: {validation_results['system_quality_score']}/100")
        print(f"Entities Validated: {validation_results['entities_validated']}")
        
        print(f"\nDetailed Results:")
        for entity_type, result in validation_results['results'].items():
            print(f"\n{entity_type.upper()}:")
            print(f"  Status: {result.get('status', 'unknown')}")
            print(f"  Records: {result.get('record_count', 0)}")
            
            if 'overall_score' in result:
                print(f"  Quality Score: {result['overall_score']}/100")
            
            # Show quality metrics
            quality = result.get('quality_metrics', {})
            if quality:
                print(f"  Data Quality Issues:")
                for issue in quality.get('issues', []):
                    print(f"    - {issue}")
            
            # Show business rule errors
            business = result.get('business_validation', {})
            if business and business.get('errors'):
                print(f"  Business Rule Violations:")
                for error in business['errors'][:5]:  # Show first 5
                    print(f"    - {error.get('message', 'Unknown error')}")
                if len(business['errors']) > 5:
                    print(f"    ... and {len(business['errors']) - 5} more")
        
        print(f"\nValidation report saved to: {VALIDATION_REPORT_DIR}")
        
        # Return exit code based on quality score
        if validation_results['system_quality_score'] >= 90:
            print("\n✅ Data quality is EXCELLENT")
            return 0
        elif validation_results['system_quality_score'] >= 70:
            print("\n⚠️  Data quality is GOOD but has some issues")
            return 1
        else:
            print("\n❌ Data quality is POOR - significant issues found")
            return 2
            
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        print(f"\n❌ Validation failed: {e}")
        return 3

if __name__ == "__main__":
    exit(main())
