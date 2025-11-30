#!/usr/bin/env python3
"""
Comprehensive Mock Data Generator for IPMS Legacy System
Generates realistic data with intentional quality issues typical of legacy systems
"""

import csv
import random
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import uuid

# Configuration
NUM_CLIENTS = 500
NUM_PATENTS = 1200
NUM_TRADEMARKS = 800
NUM_COPYRIGHTS = 300
NUM_DEADLINES_PER_MATTER = 3  # Average deadlines per IP matter
NUM_INVOICES = 400
NUM_ASSIGNMENTS = 600
NUM_DOCUMENTS = 2000

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "legacy_csv"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Sample data for realistic generation
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Helen", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Dorothy", "Mark", "Lisa", "Donald", "Sandra",
    "Steven", "Donna", "Paul", "Carol", "Andrew", "Ruth", "Joshua", "Sharon",
    "Kenneth", "Michelle", "Kevin", "Laura", "Brian", "Sarah", "George", "Kimberly",
    "Timothy", "Deborah", "Ronald", "Dorothy", "Jason", "Lisa", "Edward", "Nancy",
    "Jeffrey", "Karen", "Ryan", "Betty", "Jacob", "Helen", "Gary", "Sandra"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy"
]

COMPANY_NAMES = [
    "TechCorp", "InnovaSoft", "DataDyne", "NexGen Solutions", "CyberTech", "InfoSys",
    "GlobalTech", "SmartSystems", "FutureTech", "AdvancedSoft", "TechnoLogic", "DigitalEdge",
    "SystemsPlus", "TechVision", "InnovateCorp", "TechSolutions", "DataFlow", "CyberSoft",
    "TechMaster", "InnovateNow", "TechWorld", "SystemTech", "DataTech", "TechPro",
    "InnovaTech", "TechForce", "SystemCore", "TechLink", "DataCore", "TechBase",
    "InnovateX", "TechStream", "SystemFlow", "TechGrid", "DataGrid", "TechNet",
    "Pharmaceuticals Inc", "Biotech Solutions", "MedDevice Corp", "HealthTech",
    "Manufacturing Co", "Industrial Systems", "Automotive Parts Inc", "Energy Solutions",
    "Chemical Corp", "Materials Inc", "Engineering Solutions", "Construction Tech"
]

CITIES = [
    ("New York", "NY"), ("Los Angeles", "CA"), ("Chicago", "IL"), ("Houston", "TX"),
    ("Phoenix", "AZ"), ("Philadelphia", "PA"), ("San Antonio", "TX"), ("San Diego", "CA"),
    ("Dallas", "TX"), ("San Jose", "CA"), ("Austin", "TX"), ("Jacksonville", "FL"),
    ("Fort Worth", "TX"), ("Columbus", "OH"), ("Charlotte", "NC"), ("San Francisco", "CA"),
    ("Indianapolis", "IN"), ("Seattle", "WA"), ("Denver", "CO"), ("Washington", "DC"),
    ("Boston", "MA"), ("El Paso", "TX"), ("Nashville", "TN"), ("Detroit", "MI"),
    ("Portland", "OR"), ("Oklahoma City", "OK"), ("Las Vegas", "NV"), ("Memphis", "TN"),
    ("Louisville", "KY"), ("Baltimore", "MD"), ("Milwaukee", "WI"), ("Albuquerque", "NM")
]

COUNTRIES = [
    "United States", "USA", "US",  # Inconsistent formats
    "Canada", "CA",
    "United Kingdom", "UK", "GB",
    "Germany", "Deutschland", "DE",
    "France", "FR",
    "Japan", "JP",
    "China", "CN",
    "India", "IN",
    "Australia", "AU",
    "Brazil", "BR"
]

PATENT_TITLES = [
    "Method and System for Data Processing",
    "Wireless Communication Device and Method",
    "Machine Learning Algorithm for Pattern Recognition",
    "Biodegradable Polymer Composition",
    "Solar Cell with Improved Efficiency",
    "Medical Device for Minimally Invasive Surgery",
    "Autonomous Vehicle Navigation System",
    "Battery Technology with Extended Life",
    "Quantum Computing Gate Implementation",
    "Drug Delivery System for Targeted Therapy",
    "Artificial Intelligence for Image Recognition",
    "Renewable Energy Storage Solution",
    "Semiconductor Manufacturing Process",
    "Biotechnology Method for Gene Expression",
    "Advanced Materials for Aerospace Applications",
    "Internet of Things Sensor Network",
    "Cybersecurity Method for Data Protection",
    "Nanotechnology for Electronic Devices",
    "Pharmaceutical Compound for Cancer Treatment",
    "Robotic System for Manufacturing Automation"
]

TRADEMARK_MARKS = [
    "INNOVATECH", "TECHMASTER", "DATASYNC", "CYBERSHIELD", "SMARTFLOW",
    "NEXGEN", "FUTURETECH", "ADVANCEDSYS", "TECHVISION", "INNOVATE",
    "TECHPRO", "SYSTEMCORE", "DATAFLOW", "CYBERTECH", "SMARTSYS",
    "NOVALUX", "TECHSTREAM", "INNOVATEX", "SYSTEMTECH", "DATATECH",
    "ECOPACK", "GREENTECH", "BIOSAFE", "NATURALS", "ORGANIC",
    "MEDTECH", "HEALTHPRO", "CAREPLUS", "WELLNESS", "LIFETEC",
    "AUTOTECH", "SPEEDWAY", "MOTORPRO", "DRIVETEC", "CARTECH"
]

COPYRIGHT_TITLES = [
    "Software Application for Data Management",
    "Educational Course Materials",
    "Marketing Brochure Design",
    "Technical Manual and Documentation",
    "Website Design and Content",
    "Mobile App User Interface",
    "Training Video Series",
    "Corporate Logo and Branding",
    "Product Packaging Design",
    "Instruction Manual",
    "Advertisement Campaign",
    "Software Source Code",
    "Database Schema Design",
    "User Manual",
    "Presentation Materials"
]

TECHNOLOGY_FIELDS = [
    "Computer Science", "Telecommunications", "Biotechnology", "Materials Science",
    "Electronics", "Mechanical Engineering", "Chemical Engineering", "Medical Devices",
    "Pharmaceuticals", "Automotive", "Aerospace", "Energy", "Environmental",
    "Nanotechnology", "Artificial Intelligence", "Robotics", "Semiconductor",
    "Software", "Internet Technology", "Consumer Electronics"
]

NICE_CLASSES = [1, 3, 5, 9, 10, 11, 12, 16, 17, 18, 19, 20, 21, 25, 28, 29, 30, 32, 35, 36, 38, 41, 42, 44, 45]

def random_date(start_year=2018, end_year=2024, format_variation=True):
    """Generate random date with format variations typical of legacy systems"""
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    random_date = start_date + timedelta(days=random_days)
    
    if not format_variation:
        return random_date.strftime('%Y-%m-%d')
    
    # Introduce format variations typical of legacy systems
    formats = [
        '%Y-%m-%d',
        '%m/%d/%Y', 
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%m-%d-%Y',
        '%d-%m-%Y',
        '%B %d, %Y',
        '%d %B %Y',
        '%m/%d/%y',
        '%d/%m/%y'
    ]
    
    # Sometimes return empty or malformed dates
    if random.random() < 0.05:  # 5% chance of bad data
        bad_dates = ['', 'N/A', 'TBD', 'Unknown', '00/00/0000', '1900-01-01']
        return random.choice(bad_dates)
    
    return random_date.strftime(random.choice(formats))

def random_phone():
    """Generate phone number with format variations"""
    formats = [
        '+1-{}-{}-{}',
        '({}) {}-{}',
        '{}.{}.{}',
        '{}-{}-{}',
        '1-{}-{}-{}',
        '+1 {} {} {}',
        '{} {} {}'
    ]
    
    area = random.randint(200, 999)
    exchange = random.randint(200, 999)
    number = random.randint(1000, 9999)
    
    if random.random() < 0.03:  # 3% chance of bad data
        return random.choice(['', 'N/A', 'Unknown', '000-000-0000'])
    
    format_str = random.choice(formats)
    return format_str.format(area, exchange, number)

def generate_clients():
    """Generate client data with quality issues"""
    print("Generating clients...")
    clients = []
    
    for i in range(NUM_CLIENTS):
        client_id = f"CL-{str(i+1).zfill(4)}"
        
        # Randomly choose individual or company
        is_company = random.random() < 0.3
        
        if is_company:
            company_name = random.choice(COMPANY_NAMES)
            if random.random() < 0.5:
                company_name += " " + random.choice(["Inc", "Corp", "LLC", "Ltd"])
            
            client_name = company_name
            first_name = ""
            last_name = ""
            client_type = random.choice(["company", "corporation", ""])  # Sometimes empty
        else:
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            
            # Legacy format: "Last, First" (sometimes inconsistent)
            if random.random() < 0.8:
                client_name = f"{last_name}, {first_name}"
            else:
                client_name = f"{first_name} {last_name}"
            
            company_name = ""
            client_type = random.choice(["individual", "person", ""])
        
        # Contact info with quality issues
        email = ""
        if random.random() < 0.85:  # 15% missing emails
            if is_company:
                email = f"legal@{company_name.lower().replace(' ', '').replace(',', '')}.com"
            else:
                email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            
            # Introduce some email variations and errors
            if random.random() < 0.05:
                email = email.replace('@', '_at_')  # Malformed email
        
        phone = random_phone()
        phone_mobile = random_phone() if random.random() < 0.6 else ""
        
        # Address with inconsistencies
        city, state = random.choice(CITIES)
        address_line1 = f"{random.randint(1, 9999)} {random.choice(['Main', 'Oak', 'First', 'Second', 'Park', 'Washington', 'Lincoln'])} {random.choice(['St', 'Ave', 'Dr', 'Blvd', 'Way'])}"
        address_line2 = f"Suite {random.randint(100, 999)}" if random.random() < 0.3 else ""
        
        postal_code = str(random.randint(10000, 99999))
        country = random.choice(COUNTRIES)
        
        # Sometimes duplicate billing address
        billing_address = ""
        if random.random() < 0.4:
            billing_address = f"{address_line1}, {city}, {state} {postal_code}"
        
        status = random.choice(["active", "Active", "ACTIVE", "inactive", "suspended", ""])
        
        client = {
            'client_id': client_id,
            'client_name': client_name,
            'first_name': first_name,
            'last_name': last_name,
            'company_name': company_name,
            'client_type': client_type,
            'email': email,
            'email_secondary': "",
            'phone': phone,
            'phone_mobile': phone_mobile,
            'fax': random_phone() if random.random() < 0.2 else "",
            'address_line1': address_line1,
            'address_line2': address_line2,
            'city': city,
            'state_province': state,
            'postal_code': postal_code,
            'country': country,
            'billing_address': billing_address,
            'created_on': random_date(2018, 2023),
            'modified_on': random_date(2023, 2024) if random.random() < 0.6 else "",
            'status': status,
            'notes': "Legacy client record" if random.random() < 0.3 else "",
            'credit_limit': round(random.uniform(1000, 50000), 2) if random.random() < 0.7 else "",
            'payment_terms': random.choice(["30 days", "Net 30", "15 days", "COD", ""]) if random.random() < 0.8 else ""
        }
        
        clients.append(client)
    
    # Write to CSV
    with open(OUTPUT_DIR / "clients.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=clients[0].keys())
        writer.writeheader()
        writer.writerows(clients)
    
    print(f"Generated {len(clients)} clients")
    return clients

def generate_patents(clients):
    """Generate patent data with quality issues"""
    print("Generating patents...")
    patents = []
    
    for i in range(NUM_PATENTS):
        patent_id = f"PT-{str(i+1).zfill(4)}"
        client = random.choice(clients)
        
        title = random.choice(PATENT_TITLES)
        # Add some variation to titles
        if random.random() < 0.3:
            title += f" - {random.choice(['Improved', 'Advanced', 'Enhanced', 'Novel', 'Optimized'])}"
        
        abstract = f"This invention relates to {title.lower()}. The method involves innovative approaches to solving technical challenges in the field."
        
        # Inventors (comma-separated, sometimes messy)
        num_inventors = random.randint(1, 4)
        inventors = []
        for _ in range(num_inventors):
            inventor = f"{random.choice(LAST_NAMES)}, {random.choice(FIRST_NAMES)}"
            inventors.append(inventor)
        inventors_str = "; ".join(inventors) if random.random() < 0.6 else ", ".join(inventors)
        
        # Assignees
        assignees = client['client_name'] if random.random() < 0.8 else ""
        
        # Application numbers with variations
        app_number = f"{random.randint(10, 17)}/{random.randint(100000, 999999)}"
        pub_number = f"US{random.randint(20180000000, 20240000000)}" if random.random() < 0.7 else ""
        patent_number = f"US{random.randint(8000000, 12000000)}" if random.random() < 0.4 else ""
        
        filing_date = random_date(2018, 2023)
        priority_date = random_date(2018, 2022) if random.random() < 0.6 else ""
        pub_date = random_date(2019, 2024) if random.random() < 0.7 else ""
        grant_date = random_date(2020, 2024) if random.random() < 0.4 else ""
        expiry_date = random_date(2038, 2044) if random.random() < 0.5 else ""
        
        jurisdiction = random.choice(["US", "USA", "United States", "EP", "Europe", "GB", "DE", "JP", "CN"])
        patent_office = {
            "US": "USPTO", "USA": "USPTO", "United States": "USPTO",
            "EP": "EPO", "Europe": "EPO",
            "GB": "UKIPO", "DE": "DPMA", "JP": "JPO", "CN": "CNIPA"
        }.get(jurisdiction, "USPTO")
        
        status = random.choice(["pending", "granted", "abandoned", "expired", "under examination", "issued"])
        patent_type = random.choice(["utility", "design", "plant", "provisional"])
        tech_field = random.choice(TECHNOLOGY_FIELDS)
        
        # IPC/CPC classes (sometimes messy format)
        ipc_classes = f"G06F {random.randint(1, 21)}/{random.randint(10, 99)}"
        if random.random() < 0.5:
            ipc_classes += f"; H04L {random.randint(1, 29)}/{random.randint(10, 99)}"
        
        cpc_classes = f"G06F {random.randint(1, 21)}/{random.randint(1000, 9999)}"
        
        family_id = f"FAM-{random.randint(100000, 999999)}" if random.random() < 0.6 else ""
        priority_claims = f'{{"country": "{jurisdiction}", "number": "{random.randint(100000, 999999)}", "date": "{priority_date}"}}' if priority_date else ""
        
        examination_status = random.choice(["", "First Action", "Final Rejection", "Allowance", "RCE Filed"])
        annuity_date = random_date(2024, 2026) if random.random() < 0.3 else ""
        
        estimated_cost = round(random.uniform(5000, 50000), 2) if random.random() < 0.8 else ""
        actual_cost = round(random.uniform(3000, 45000), 2) if random.random() < 0.6 else ""
        
        attorney_ref = f"ATT-{random.randint(1000, 9999)}" if random.random() < 0.7 else ""
        internal_ref = f"INT-{random.randint(1000, 9999)}" if random.random() < 0.8 else ""
        
        patent = {
            'patent_id': patent_id,
            'client_id': client['client_id'],
            'title': title,
            'abstract': abstract,
            'inventors': inventors_str,
            'assignees': assignees,
            'application_number': app_number,
            'publication_number': pub_number,
            'patent_number': patent_number,
            'filing_date': filing_date,
            'priority_date': priority_date,
            'publication_date': pub_date,
            'grant_date': grant_date,
            'expiry_date': expiry_date,
            'jurisdiction': jurisdiction,
            'patent_office': patent_office,
            'status': status,
            'patent_type': patent_type,
            'technology_field': tech_field,
            'ipc_classes': ipc_classes,
            'cpc_classes': cpc_classes,
            'family_id': family_id,
            'priority_claims': priority_claims,
            'examination_status': examination_status,
            'annuity_due_date': annuity_date,
            'estimated_cost': estimated_cost,
            'actual_cost': actual_cost,
            'attorney_ref': attorney_ref,
            'internal_ref': internal_ref,
            'created_on': random_date(2018, 2023),
            'modified_on': random_date(2023, 2024) if random.random() < 0.5 else "",
            'notes': "Legacy patent record" if random.random() < 0.2 else ""
        }
        
        patents.append(patent)
    
    # Write to CSV
    with open(OUTPUT_DIR / "patents.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=patents[0].keys())
        writer.writeheader()
        writer.writerows(patents)
    
    print(f"Generated {len(patents)} patents")
    return patents

def generate_trademarks(clients):
    """Generate trademark data with quality issues"""
    print("Generating trademarks...")
    trademarks = []
    
    for i in range(NUM_TRADEMARKS):
        tm_id = f"TM-{str(i+1).zfill(4)}"
        client = random.choice(clients)
        
        mark_text = random.choice(TRADEMARK_MARKS)
        if random.random() < 0.3:
            mark_text += str(random.randint(1, 999))
        
        mark_type = random.choice(["word", "logo", "combined", "design", "composite", ""])
        mark_description = f"Trademark for {mark_text}" if mark_type in ["logo", "combined", "design"] else ""
        
        # Goods and services
        goods_services = random.choice([
            "Computer software and hardware",
            "Pharmaceutical preparations",
            "Clothing and apparel",
            "Food and beverages", 
            "Telecommunications services",
            "Financial services",
            "Educational services",
            "Medical devices",
            "Automotive parts",
            "Construction materials"
        ])
        
        # Nice classes (comma-separated, sometimes messy)
        num_classes = random.randint(1, 3)
        nice_classes = random.sample(NICE_CLASSES, num_classes)
        nice_classes_str = ",".join(map(str, nice_classes))
        if random.random() < 0.3:
            nice_classes_str = nice_classes_str.replace(",", ", ")  # Add spaces sometimes
        
        vienna_classes = f"27.05.01, 26.01.03" if mark_type in ["logo", "combined", "design"] and random.random() < 0.5 else ""
        
        app_number = f"{random.randint(87, 90)}/{random.randint(100000, 999999)}"
        reg_number = f"{random.randint(5000000, 7000000)}" if random.random() < 0.4 else ""
        
        filing_date = random_date(2018, 2023)
        priority_date = random_date(2018, 2022) if random.random() < 0.4 else ""
        pub_date = random_date(2019, 2024) if random.random() < 0.6 else ""
        reg_date = random_date(2020, 2024) if random.random() < 0.4 else ""
        renewal_date = random_date(2025, 2030) if reg_date else ""
        expiry_date = random_date(2028, 2034) if reg_date else ""
        
        jurisdiction = random.choice(["US", "USA", "United States", "EU", "Europe", "GB", "DE", "JP", "CN"])
        tm_office = {
            "US": "USPTO", "USA": "USPTO", "United States": "USPTO",
            "EU": "EUIPO", "Europe": "EUIPO",
            "GB": "UKIPO", "DE": "DPMA", "JP": "JPO", "CN": "CNIPA"
        }.get(jurisdiction, "USPTO")
        
        status = random.choice(["pending", "registered", "opposed", "cancelled", "abandoned", "expired", "published"])
        
        opposition_end = random_date(2024, 2025) if status == "published" and random.random() < 0.3 else ""
        
        use_basis = random.choice(["1(a)", "1(b)", "intent-to-use", "use-in-commerce", ""]) if jurisdiction in ["US", "USA", "United States"] else ""
        first_use = random_date(2015, 2022) if use_basis in ["1(a)", "use-in-commerce"] and random.random() < 0.6 else ""
        first_commerce = random_date(2016, 2023) if first_use and random.random() < 0.8 else ""
        
        estimated_cost = round(random.uniform(1000, 15000), 2) if random.random() < 0.8 else ""
        actual_cost = round(random.uniform(800, 12000), 2) if random.random() < 0.6 else ""
        
        attorney_ref = f"ATT-{random.randint(1000, 9999)}" if random.random() < 0.7 else ""
        internal_ref = f"TM-INT-{random.randint(1000, 9999)}" if random.random() < 0.8 else ""
        
        trademark = {
            'tm_id': tm_id,
            'client_id': client['client_id'],
            'mark_text': mark_text,
            'mark_type': mark_type,
            'mark_description': mark_description,
            'goods_services': goods_services,
            'nice_classes': nice_classes_str,
            'vienna_classes': vienna_classes,
            'application_number': app_number,
            'registration_number': reg_number,
            'filing_date': filing_date,
            'priority_date': priority_date,
            'publication_date': pub_date,
            'registration_date': reg_date,
            'renewal_date': renewal_date,
            'expiry_date': expiry_date,
            'jurisdiction': jurisdiction,
            'trademark_office': tm_office,
            'status': status,
            'opposition_period_end': opposition_end,
            'use_basis': use_basis,
            'first_use_date': first_use,
            'first_use_commerce_date': first_commerce,
            'attorney_ref': attorney_ref,
            'internal_ref': internal_ref,
            'estimated_cost': estimated_cost,
            'actual_cost': actual_cost,
            'created_on': random_date(2018, 2023),
            'modified_on': random_date(2023, 2024) if random.random() < 0.5 else "",
            'notes': "Legacy trademark record" if random.random() < 0.2 else ""
        }
        
        trademarks.append(trademark)
    
    # Write to CSV
    with open(OUTPUT_DIR / "trademarks.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=trademarks[0].keys())
        writer.writeheader()
        writer.writerows(trademarks)
    
    print(f"Generated {len(trademarks)} trademarks")
    return trademarks

def generate_deadlines(clients, patents, trademarks):
    """Generate deadline data"""
    print("Generating deadlines...")
    deadlines = []
    
    all_matters = (
        [('patent', p) for p in patents] +
        [('trademark', t) for t in trademarks]
    )
    
    deadline_id_counter = 1
    
    for matter_type, matter in all_matters:
        # Generate 1-4 deadlines per matter
        num_deadlines = random.randint(1, 4)
        
        for _ in range(num_deadlines):
            deadline_id = f"DL-{str(deadline_id_counter).zfill(4)}"
            deadline_id_counter += 1
            
            if matter_type == 'patent':
                related_id = matter['patent_id']
                client_id = matter['client_id']
                deadline_types = ["renewal", "examination response", "filing", "annuity", "continuation"]
            else:  # trademark
                related_id = matter['tm_id']
                client_id = matter['client_id']
                deadline_types = ["renewal", "opposition response", "statement of use", "declaration", "maintenance"]
            
            deadline_type = random.choice(deadline_types)
            
            # Generate due date based on matter type and current date
            if deadline_type == "renewal":
                due_date = random_date(2024, 2030)
            elif deadline_type in ["examination response", "opposition response"]:
                due_date = random_date(2024, 2025)
            else:
                due_date = random_date(2024, 2027)
            
            description = f"{deadline_type.title()} for {matter_type} {related_id}"
            if deadline_type == "renewal":
                description += " - Fee payment required"
            elif "response" in deadline_type:
                description += " - Response to office action required"
            
            priority = random.choice(["low", "medium", "high", "critical", "urgent", "normal"])
            status = random.choice(["pending", "completed", "overdue", "cancelled"])
            
            reminder_sent = random.choice(["yes", "no", "Y", "N", ""]) if status == "pending" else ""
            completed_date = random_date(2023, 2024) if status == "completed" else ""
            completed_by = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}" if status == "completed" else ""
            
            cost = round(random.uniform(100, 5000), 2) if random.random() < 0.7 else ""
            
            deadline = {
                'deadline_id': deadline_id,
                'related_type': matter_type,
                'related_id': related_id,
                'client_id': client_id,
                'deadline_type': deadline_type,
                'due_date': due_date,
                'description': description,
                'priority': priority,
                'status': status,
                'reminder_sent': reminder_sent,
                'completed_date': completed_date,
                'completed_by': completed_by,
                'cost': cost,
                'internal_notes': "Legacy deadline record" if random.random() < 0.2 else "",
                'created_on': random_date(2018, 2023),
                'modified_on': random_date(2023, 2024) if random.random() < 0.5 else ""
            }
            
            deadlines.append(deadline)
    
    # Write to CSV
    with open(OUTPUT_DIR / "deadlines.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=deadlines[0].keys())
        writer.writeheader()
        writer.writerows(deadlines)
    
    print(f"Generated {len(deadlines)} deadlines")
    return deadlines

def main():
    """Generate all mock data"""
    print("Starting comprehensive mock data generation...")
    print(f"Output directory: {OUTPUT_DIR}")
    
    # Generate data in dependency order
    clients = generate_clients()
    patents = generate_patents(clients)
    trademarks = generate_trademarks(clients)
    deadlines = generate_deadlines(clients, patents, trademarks)
    
    # Generate summary
    summary = {
        'generation_date': datetime.now().isoformat(),
        'counts': {
            'clients': len(clients),
            'patents': len(patents),
            'trademarks': len(trademarks),
            'deadlines': len(deadlines)
        },
        'files_generated': [
            'clients.csv',
            'patents.csv', 
            'trademarks.csv',
            'deadlines.csv'
        ]
    }
    
    with open(OUTPUT_DIR / "generation_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "="*50)
    print("MOCK DATA GENERATION COMPLETE")
    print("="*50)
    print(f"Generated {summary['counts']['clients']} clients")
    print(f"Generated {summary['counts']['patents']} patents")
    print(f"Generated {summary['counts']['trademarks']} trademarks")
    print(f"Generated {summary['counts']['deadlines']} deadlines")
    print(f"Files saved to: {OUTPUT_DIR}")
    print("\nData includes intentional quality issues typical of legacy systems:")
    print("- Inconsistent date formats")
    print("- Varying phone number formats")
    print("- Mixed country name formats")
    print("- Incomplete records")
    print("- Format variations")
    print("\nReady for ETL processing!")

if __name__ == "__main__":
    main()
