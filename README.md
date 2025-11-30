# Legacy → Modern IPMS Simulator

A comprehensive **Intellectual Property Management System (IPMS)** that demonstrates the complete migration from legacy systems to modern architectures. This project showcases real-world ETL processes, data quality management, and modern web application development.

## 🚀 Project Overview

This IPMS simulator provides a complete solution for managing intellectual property portfolios, including:

- **Patents** - Utility, design, and plant patents with full lifecycle management
- **Trademarks** - Word marks, logos, and combined marks with Nice classification
- **Copyrights** - Literary, artistic, and software works
- **Deadlines** - Renewal dates, response deadlines, and maintenance requirements
- **Clients** - Individual and corporate client management
- **Billing** - Invoice generation and payment tracking

## 🏗️ System Architecture

### Legacy System (Source)
- **Database**: MySQL with denormalized, legacy schema
- **Data Quality**: Intentional inconsistencies and quality issues
- **Format Issues**: Mixed date formats, varying country codes, incomplete records

### Modern System (Target)
- **Database**: PostgreSQL with properly normalized schema
- **Data Types**: Modern data types with proper constraints
- **Integrity**: Full referential integrity and business rules
- **Performance**: Optimized indexes and query performance

### ETL Pipeline
- **Extract**: CSV-based extraction (simulating database reads)
- **Transform**: Comprehensive data cleaning and normalization
- **Load**: Validated data insertion with conflict resolution
- **Validate**: Multi-level validation with quality scoring

## 🛠️ Features

### Data Management
- ✅ **Mock Data Generation** - Realistic test data with quality issues
- ✅ **Data Validation** - Comprehensive quality assessment
- ✅ **ETL Pipeline** - Complete transformation workflow
- ✅ **Schema Migration** - Legacy to modern database conversion

### Web Interface
- ✅ **Modern UI** - Bootstrap-based responsive interface
- ✅ **Dashboard** - System overview and key metrics
- ✅ **Client Management** - Complete client lifecycle
- ✅ **IP Portfolio** - Patents and trademarks management
- ✅ **Deadline Tracking** - Critical date management
- ✅ **Migration Control** - ETL process monitoring

### API Endpoints
- ✅ **RESTful API** - Complete CRUD operations
- ✅ **Data Export** - JSON/CSV export capabilities
- ✅ **Real-time Updates** - Live system statistics
- ✅ **Validation API** - Data quality assessment

### Reporting & Analytics
- ✅ **Quality Metrics** - Data quality scoring
- ✅ **Portfolio Analytics** - IP portfolio insights
- ✅ **Migration Reports** - ETL process tracking
- ✅ **Visual Charts** - Interactive data visualization

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker (optional, for database containers)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd legacy_to_modern_ipms_simulator
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate mock data**
   ```bash
   python etl/generate_mock_data.py
   ```

5. **Run data validation**
   ```bash
   python etl/validate.py
   ```

6. **Start the web application**
   ```bash
   cd app
   python main.py
   ```

7. **Access the application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs
   - Alternative API Docs: http://localhost:8000/api/redoc

### Using Docker (Optional)

1. **Start database containers**
   ```bash
   docker compose up -d
   ```

2. **Access database tools**
   - Adminer: http://localhost:8080
   - PostgreSQL: localhost:5432
   - MySQL: localhost:3306

## 📊 Data Overview

The system generates realistic mock data including:

- **500 Clients** - Mix of individuals and companies
- **1,200 Patents** - Various statuses and jurisdictions
- **800 Trademarks** - Different mark types and classes
- **5,000+ Deadlines** - Renewal and response deadlines

### Data Quality Issues (Intentional)
- Inconsistent date formats (MM/DD/YYYY, DD/MM/YYYY, etc.)
- Varying phone number formats
- Mixed country name formats (US, USA, United States)
- Missing email addresses (~15% of clients)
- Invalid data entries (~5% across all entities)

## 🔍 Validation System

The comprehensive validation system checks:

### Schema Validation
- Data type compliance
- Required field validation
- Format consistency
- Constraint adherence

### Business Rule Validation
- Filing dates before grant dates
- Valid Nice classification numbers
- Proper client references
- Logical status transitions

### Data Quality Metrics
- Completeness scoring
- Accuracy assessment
- Consistency evaluation
- Overall quality scoring (0-100%)

## 🔄 ETL Pipeline

### Transformation Process
1. **Data Extraction** - Read from legacy CSV files
2. **Data Cleaning** - Normalize formats and fix inconsistencies
3. **Data Validation** - Apply business rules and constraints
4. **Data Loading** - Insert into modern schema with conflict resolution
5. **Quality Assessment** - Generate quality reports

### Transformation Features
- Country code standardization (ISO 2-letter codes)
- Date format normalization (ISO 8601)
- Phone number formatting
- Email validation and cleanup
- Name parsing and standardization
- Classification number validation

## 🌐 Web Interface

### Dashboard
- System overview and key metrics
- Data quality visualization
- Quick action buttons
- Recent activity log

### Client Management
- Complete client directory
- Advanced search and filtering
- Client profile management
- IP portfolio summaries

### Patent Portfolio
- Patent listing with status tracking
- Filing date and jurisdiction management
- Inventor and assignee tracking
- Technology classification

### Trademark Portfolio
- Mark management with Nice classifications
- Status tracking and renewal management
- Goods and services descriptions
- Opposition and registration tracking

### Deadline Management
- Critical date tracking
- Urgency-based prioritization
- Automatic deadline calculation
- Reminder system integration

### Migration Control
- ETL process monitoring
- Progress tracking with real-time updates
- Migration history and reporting
- Dry-run capabilities

### Validation Reports
- Comprehensive quality assessment
- Issue identification and categorization
- Historical validation tracking
- Detailed error reporting

## 📈 Reporting & Analytics

### Quality Metrics
- Overall system quality score
- Entity-specific quality ratings
- Issue categorization and counting
- Trend analysis over time

### Portfolio Analytics
- Patent status distribution
- Trademark class analysis
- Deadline urgency breakdown
- Client portfolio summaries

### Migration Reports
- ETL process performance
- Data transformation statistics
- Error rates and resolution
- Processing time analysis

## 🔧 Technical Details

### Technology Stack
- **Backend**: Python, FastAPI, SQLAlchemy
- **Frontend**: HTML5, Bootstrap 5, JavaScript, Chart.js
- **Databases**: PostgreSQL (modern), MySQL (legacy)
- **Data Processing**: Pandas, NumPy
- **Validation**: Pandera, Pydantic
- **Testing**: Pytest
- **Containerization**: Docker, Docker Compose

### Database Schema

#### Legacy MySQL Schema
- Denormalized tables with quality issues
- Inconsistent data types and formats
- Missing constraints and relationships
- Text-based date storage

#### Modern PostgreSQL Schema
- Properly normalized with referential integrity
- Modern data types (JSONB, arrays, proper dates)
- Full-text search capabilities
- Performance optimizations

### API Architecture
- RESTful design principles
- JSON-based data exchange
- Comprehensive error handling
- Real-time data updates
- Pagination and filtering

## 🧪 Testing

### Running Tests
```bash
pytest -v
```

### Test Coverage
- Data transformation utilities
- Validation logic
- API endpoints
- Business rule enforcement

## 📝 Configuration

### Environment Variables
- `TARGET_DB_URL` - PostgreSQL connection string
- `LEGACY_DB_URL` - MySQL connection string (optional)
- `LOG_LEVEL` - Application logging level

### Data Generation Configuration
Modify `etl/generate_mock_data.py`:
- `NUM_CLIENTS` - Number of clients to generate
- `NUM_PATENTS` - Number of patents to generate
- `NUM_TRADEMARKS` - Number of trademarks to generate

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Use Cases

### For Learning
- ETL pipeline development
- Data quality management
- Web application architecture
- Database schema design
- API development

### For Demonstration
- Legacy system modernization
- Data migration strategies
- Quality assessment techniques
- Modern web interfaces
- Real-time monitoring

### For IP Law Firms
- Portfolio management concepts
- Deadline tracking systems
- Client management workflows
- Reporting and analytics

## 🔮 Future Enhancements

- Real database connectivity (MySQL ↔ PostgreSQL)
- Advanced reporting with custom queries
- Email notification system for deadlines
- Document management integration
- Multi-tenant architecture
- Advanced search with Elasticsearch
- Mobile-responsive design improvements
- Real-time collaboration features

## 📞 Support

For questions, issues, or contributions:
- Create an issue in the repository
- Check the documentation in `/docs`
- Review the API documentation at `/api/docs`

---

**Built with ❤️ by Arhaan Girdhar
