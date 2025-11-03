# pulls TTC data 
import requests
import zipfile
from pathlib import Path
from .config import get_data_directories

# constants 
REQUIRED_FILES = ['stops.txt', 'routes.txt', 'trips.txt', 'stop_times.txt', 'calendar.txt']
BASE_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
PACKAGE_ID = "merged-gtfs-ttc-routes-and-schedules"

def check_gtfs_exists() -> bool:
    """Check if all required GTFS files exist."""
    dirs = get_data_directories()
    gtfs_dir = dirs['gtfs']
    
    for file in REQUIRED_FILES:
        if not (gtfs_dir / file).exists():
            return False
    
    return True

def get_gtfs_download_url() -> str:
    """Get the GTFS download URL from Toronto Open Data API."""
    url = f"{BASE_URL}/api/3/action/package_show"
    params = {"id": PACKAGE_ID}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        package = response.json()
        
        # Find the ZIP resource
        for resource in package["result"]["resources"]:
            if resource["format"].lower() == "zip":
                return resource["url"]
        
        raise ValueError("No ZIP file found in package resources")
    
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to fetch package metadata: {e}")


def download_and_extract_gtfs(download_url: str):
    """Download and extract GTFS data."""
    dirs = get_data_directories(create=True)
    raw_dir = dirs['raw']
    gtfs_dir = dirs['gtfs']
    
    zip_path = raw_dir / "ttc_gtfs.zip"
    
    # Download
    print(f"📥 Downloading GTFS data to {zip_path}...")
    response = requests.get(download_url)
    response.raise_for_status()
    
    with open(zip_path, "wb") as f:
        f.write(response.content)
    print("✅ Download complete")
    
    # Extract
    print(f"📦 Extracting files to {gtfs_dir}...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(gtfs_dir)
        print("✅ Extraction complete. Files extracted:")
        for name in zip_ref.namelist():
            print(f"   - {name}")


def download_gtfs_data():
    """Main function to download GTFS data if needed."""
    
    # Check if data already exists
    if check_gtfs_exists():
        print("✅ GTFS data already exists. Skipping download.")
        return
    
    # Download and extract
    print("📥 GTFS data not found. Downloading...")
    try:
        download_url = get_gtfs_download_url()
        download_and_extract_gtfs(download_url)
        print("🎉 GTFS data successfully downloaded and extracted!")
    except Exception as e:
        print(f"❌ Error downloading GTFS data: {e}")
        raise


if __name__ == "__main__":
    # Run as script: python -m src.download_data
    download_gtfs_data()

