import sys
import re
import urllib.parse
import urllib.request
import os
import requests
from PIL import Image
from io import BytesIO

def extract_doc_id(input_str):
    """Extracts document ID from either a raw string or an ACRIS URL."""
    # If it's a URL, try to parse doc_id query param
    if "doc_id=" in input_str:
        match = re.search(r"doc_id=([A-Za-z0-9]+)", input_str)
        if match:
            return match.group(1)
    # Assume it's already the doc_id if it's alphanumeric and ~16 chars
    return input_str.strip()

def download_document(doc_id, output_dir="."):
    print(f"Starting download process for Document ID: {doc_id}")
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    # Step 1: Hit bandwidth policy page to get initial cookies/session state
    print("Initializing session...")
    try:
        session.get("https://a836-acris.nyc.gov/BandwidthPolicy/ACRIS-BW-POL.html", timeout=10)
    except Exception as e:
        print(f"Warning: Failed to hit bandwidth policy page: {e}")
        
    # Step 2: Fetch DocumentImageView page to extract total pages
    print("Fetching document metadata...")
    view_url = f"https://a836-acris.nyc.gov/DS/DocumentSearch/DocumentImageView?doc_id={doc_id}"
    try:
        response = session.get(view_url, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching document view page: {e}")
        return False
        
    html_content = response.text
    
    # The DocumentImageView page contains an iframe to DocumentImageVtu which has a JSON string in the URL
    # encoded as searchCriteriaStringValue. We look for hid_TotalPages.
    # It might be in the raw text or url-encoded form.
    total_pages = 1
    
    # Decode URL-encoded text to make regex search easier
    decoded_html = urllib.parse.unquote(html_content)
    match = re.search(r'"hid_TotalPages"\s*:\s*(\d+)', decoded_html)
    if match:
        total_pages = int(match.group(1))
        print(f"Found {total_pages} total pages for this document.")
    else:
        print("Warning: Could not determine total pages from metadata. Will try to download at least page 1.")
        
    # Step 3: Download each page and store in memory
    success_count = 0
    images = []
    
    for page in range(1, total_pages + 1):
        image_url = f"https://a836-acris.nyc.gov/DS/DocumentSearch/GetImage?doc_id={doc_id}&page={page}"
        print(f"Downloading page {page}/{total_pages}...")
        
        try:
            img_response = session.get(image_url, timeout=20)
            img_response.raise_for_status()
            
            if "image/" not in img_response.headers.get("Content-Type", ""):
                print(f"Warning: Response doesn't look like an image. Got Content-Type: {img_response.headers.get('Content-Type')}")
                if len(img_response.content) < 5000:
                    print("Received an error page instead of an image.")
                    break
            
            # Open TIFF image from memory
            img = Image.open(BytesIO(img_response.content))
            
            # Convert to RGB (PDF doesn't cleanly support all TIFF modes)
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            images.append(img)
            success_count += 1
            print(f"  -> Page {page} loaded into memory")
            
        except Exception as e:
            print(f"Error downloading or processing page {page}: {e}")
            break
            
    # Step 4: Save all collected images as a single multi-page PDF
    if images:
        pdf_path = os.path.join(output_dir, f"{doc_id}.pdf")
        print(f"\nSaving {len(images)} pages to {pdf_path} ...")
        
        # Save first image with append behavior for the rest
        images[0].save(
            pdf_path, 
            "PDF" ,
            resolution=100.0, 
            save_all=True, 
            append_images=images[1:]
        )
        print("Save complete!")
    
    print(f"\nDownload summary: Successfully downloaded and merged {success_count} out of {total_pages} pages into a PDF.")
    return success_count > 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_acris_document.py <doc_id_or_url>")
        sys.exit(1)
        
    input_val = sys.argv[1]
    doc_id = extract_doc_id(input_val)
    
    if not doc_id:
        print("Error: Could not extract a valid Document ID.")
        sys.exit(1)
        
    download_document(doc_id)
