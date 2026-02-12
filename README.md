# Lighting Assessment - MCC

A comprehensive lighting measurement analysis system for Maui County Code compliance evaluation. This project processes spectral data from Sekonic measurement devices and generates detailed compliance reports with AI-powered summaries.

## Features

- **CSV Processing** (`CSV/blue2csv.py`): Transforms raw measurement CSV files with formula calculations for blue light percentage
- **Image Labeling** (`JPG/labelJPG.py`): Automatically labels fixture images with measurement values
- **Report Generation** (`JPG/SekonicMeasurementReportGenerator.py`):
  - Combines fixture photos, spectral response, CCT images, and measurement data into unified PDFs
  - Generates AI-powered compliance summaries using OpenAI
  - Prepends summaries to merged PDFs for easy review

## Project Structure

```
.
├── CSV/                          # CSV data processing scripts
│   ├── blue2csv.py              # Processes and calculates blue light ratios
│   └── SL_*.csv                 # Measurement data files
├── JPG/                         # Image and PDF generation scripts
│   ├── labelJPG.py              # Labels images with measurement values
│   ├── SekonicMeasurementReportGenerator.py  # Main report generator
│   ├── updated_SL_*.csv         # Processed CSV files
│   └── SL_*.jpg                 # Fixture images
├── FIXTURES/                    # Reference and archive data
├── run_reports.py               # Batch report processor
└── import multiple csv files template.xlsm  # Excel template reference
```

## Prerequisites

- Python 3.8+
- macOS, Linux, or Windows with command-line tools

## Installation

1. **Clone or navigate to the repository:**
   ```bash
   cd "Lighting Assessment - MCC"
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install pandas Pillow reportlab pypdf openai
   ```

4. **Set up OpenAI API key:**
   ```bash
   echo 'OPENAI_API_KEY="sk-..."' > .venv/.env
   chmod 600 .venv/.env
   ```
   *(The key is automatically loaded when you activate the venv)*

## Usage

### Process CSV Data
Transform raw measurement CSV files with blue light calculations:
```bash
cd CSV
python3 blue2csv.py
```

### Label Fixture Images
Add measurement values to fixture photos:
```bash
cd JPG
python3 labelJPG.py
```

### Generate Compliance Reports
Create unified PDFs with AI summaries for all fixtures:
```bash
python3 run_reports.py
```

Output PDFs will be saved as `Merged_<fixture_id>.pdf` in the `JPG/` folder with OpenAI-generated compliance summaries prepended.

## Configuration

### Environment Variables (`.venv/.env`)
- `OPENAI_API_KEY` (required): Your OpenAI API key
- `OPENAI_MODEL` (optional): Model to use for summaries (default: `gpt-4o`)

### Script Parameters
- `labelJPG.py`:
  - `FONT_SIZE`: Text size for image labels (default: 36)
  - `TEXT_COLOR`: Label color (default: "blue")
  - `CELL_LOCATION`: CSV cell for measurement value (default: B3, row 2, col 1)

- `SekonicMeasurementReportGenerator.py`:
  - CSV snippet size: First 60 rows sent to OpenAI (line 103)
  - Summary max tokens: 800 (can be adjusted)

## API Costs

**Estimated cost for batch processing:**
- 28–50 fixtures × 1 API call/fixture = 28–50 requests
- Typical cost: ~$0.05–$0.15 USD for CSV-snippet summaries (gpt-4o model)

*Note: Full-PDF upload currently unsupported by SDK; using CSV snippet fallback.*

## Error Handling

All scripts include robust error handling:
- Missing files: Scripts skip and log warnings
- Font unavailability: Falls back to system default fonts
- OpenAI API errors: Logs error but continues processing
- Missing environment variables: Gracefully degrades (OpenAI disabled)

## File Formats

- **Input CSVs**: Tab-separated or comma-separated measurement data (no headers assumed initially)
- **Input Images**: JPG format, filename pattern: `SL_<13-char-id>_*.jpg`
- **Output**: PDFs with embedded metadata, one summary page + merged report pages

## Troubleshooting

**Import errors (pandas, PIL, etc.)?**
- Activate the venv: `source .venv/bin/activate`
- Reinstall deps: `pip install pandas Pillow reportlab pypdf openai`

**OpenAI rate limits?**
- Check API quota at https://platform.openai.com/account/billing
- Process in smaller batches or add delays between requests

**Fonts not found on Linux/Windows?**
- `labelJPG.py` falls back to system default; edit `font = ImageFont.truetype(...)` path for your OS

## License

Internal project for Maui County Code compliance analysis.

## Contact

For issues or questions, review the script docstrings or check API logs in the output messages.
