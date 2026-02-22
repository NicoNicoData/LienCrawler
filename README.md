# NYC ACRIS Lien Crawler

This project provides tools to search for and download documents from the NYC Department of Finance ACRIS (Automated City Register Information System) website.

## Setup

It is recommended to use a Python virtual environment to manage dependencies.

1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   ```

2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Playwright browsers (required for `search_bbl.py`):
   ```bash
   playwright install chromium
   ```

## Usage

### 1. `search_bbl.py`

This script searches the ACRIS database by Borough, Block, and Lot (BBL) and outputs a list of associated documents in CSV format.

**Usage:**
```bash
python search_bbl.py <borough> <block> <lot> [property_name]
```

**Arguments:**
- `borough`: The borough name or ID (e.g., "MANHATTAN", "1", "BROOKLYN").
- `block`: The block number.
- `lot`: The lot number.
- `[property_name]`: (Optional) A custom property name to include in the output. If omitted, defaults to `{borough}-{block}-{lot}`.

**Example:**
```bash
python search_bbl.py BROOKLYN 1234 56 "My Building"
```

**Output Format:**
Outputs CSV data to standard output with columns:
`PropertyName, DocumentType, DocumentId, DocumentLink`


### 2. `download_acris_document.py`

This script downloads all pages of a specific document from ACRIS and merges them into a single multi-page PDF.

**Usage:**
```bash
python download_acris_document.py <doc_id_or_url>
```

**Arguments:**
- `<doc_id_or_url>`: Either the raw 16-character alphanumeric document ID, or a full ACRIS `DocumentImageView` URL containing `doc_id=...`.

**Example:**
```bash
# Using Document ID directly
python download_acris_document.py 2007011000550001

# Using a URL
python download_acris_document.py "https://a836-acris.nyc.gov/DS/DocumentSearch/DocumentImageView?doc_id=2007011000550001"
```

The script will save the resulting PDF in the current directory as `<DocumentId>.pdf`.
