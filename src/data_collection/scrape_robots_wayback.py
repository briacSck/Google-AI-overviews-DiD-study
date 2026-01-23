"""
Wayback Machine Robots.txt Scraper

Collects historical robots.txt files and web governance signals from the Internet Archive
for analyzing how sites restrict or permit search engine crawling over time.

This script:
- Queries the Wayback Machine CDX API for snapshots of robots.txt files
- Downloads and parses robots.txt content
- Extracts meta robots tags and X-Robots-Tag headers from homepages
- Handles rate limiting, checkpointing, and error recovery for large-scale scraping

Output schema matches ROBOTS_SCRAPE_SCHEMA defined in schema.py.

Author: Briac Sockalingum
Research context: AI Overviews impact study with Prof. Maximilian Schäfer, IMT Business School
"""

import os
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import random
import json
from requests.exceptions import Timeout, ConnectionError, RequestException


###############################################################################
# UTILITIES
###############################################################################

def ensure_dir_exists(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


###############################################################################
# WAYBACK SNAPSHOT FUNCTIONS
###############################################################################

def get_cdx_snapshots(url, user_agent='ResearchScraper/1.0', limit=None,
                      from_timestamp=None, to_timestamp=None, timeout=30):
    """
    Fetch Wayback Machine snapshots for a given URL using the CDX API.
    
    Args:
        url: Target URL to find snapshots for
        user_agent: User-agent string for API requests
        limit: Maximum number of snapshots to retrieve
        from_timestamp: Start date (format: YYYYMMDDHHMMSS)
        to_timestamp: End date (format: YYYYMMDDHHMMSS)
        timeout: Request timeout in seconds
    
    Returns:
        List of snapshot dictionaries with 'timestamp' and 'original' keys
    """
    api_url = 'https://web.archive.org/cdx/search/cdx'
    params = {
        'url': url,
        'output': 'json',
        'fl': 'timestamp,original',
        'collapse': 'timestamp:8'  # Collapse to daily snapshots
    }

    if limit:
        params['limit'] = limit
    if from_timestamp:
        params['from'] = from_timestamp
    if to_timestamp:
        params['to'] = to_timestamp

    headers = {'User-Agent': user_agent}

    try:
        r = requests.get(api_url, params=params, headers=headers, timeout=timeout)
        r.raise_for_status()
    except Timeout:
        print(f"  CDX API timeout for {url}")
        return []
    except RequestException as e:
        print(f"  CDX API error for {url}: {e}")
        return []

    try:
        results = r.json()
    except Exception as e:
        print(f"  JSON parsing error for {url}: {e}")
        return []

    if len(results) <= 1:
        return []

    keys = results[0]
    snapshots = [dict(zip(keys, entry)) for entry in results[1:]]
    snapshots = [s for s in snapshots if 'timestamp' in s and 'original' in s]

    return snapshots


def download_wayback(url, timestamp, user_agent='ResearchScraper/1.0', timeout=30):
    """
    Download a specific snapshot from the Wayback Machine.
    
    Args:
        url: Original URL to retrieve
        timestamp: Wayback timestamp (YYYYMMDDHHMMSS format)
        user_agent: User-agent for the request
        timeout: Request timeout in seconds
    
    Returns:
        requests.Response object
    """
    archive_url = f'https://web.archive.org/web/{timestamp}id_/{url}'
    headers = {'User-Agent': user_agent}
    return requests.get(archive_url, headers=headers, timeout=timeout)


def parse_robots_txt(text):
    """
    Parse robots.txt content into structured rules.
    
    Args:
        text: Raw robots.txt content
    
    Returns:
        Dictionary mapping user-agents to their rules
    """
    rules = {}
    current_agent = None

    for line in text.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        if line.lower().startswith('user-agent:'):
            current_agent = line.split(':', 1)[1].strip()
            rules[current_agent] = []
        elif current_agent:
            rules[current_agent].append(line)

    return rules


def is_html(text):
    """Check if text content is HTML rather than plain text."""
    try:
        return bool(BeautifulSoup(text, 'html.parser').find())
    except Exception:
        return False


def extract_meta_robots(html_text):
    """Extract meta robots tag content from HTML."""
    try:
        soup = BeautifulSoup(html_text, 'html.parser')
        meta = soup.find('meta', attrs={'name': 'robots'})
        if meta and 'content' in meta.attrs:
            return meta['content'].lower()
    except Exception:
        pass
    return None


def extract_x_robots_tag(headers):
    """Extract X-Robots-Tag from HTTP headers."""
    for key, value in headers.items():
        if key.lower() == 'x-robots-tag':
            return value.lower()
    return None


###############################################################################
# MAIN SCRAPER
###############################################################################

def scrape_robots_and_signals(domain, max_snapshots=50,
                              from_timestamp=None, to_timestamp=None,
                              timeout=30):
    """
    Scrape historical robots.txt and web governance signals for a domain.
    
    This function:
    1. Fetches Wayback snapshots of robots.txt
    2. Downloads and parses each snapshot
    3. Also checks homepage for meta robots and X-Robots-Tag
    
    Args:
        domain: Domain to scrape (e.g., 'example.com')
        max_snapshots: Maximum number of snapshots to process
        from_timestamp: Start date (YYYYMMDDHHMMSS)
        to_timestamp: End date (YYYYMMDDHHMMSS)
        timeout: Request timeout in seconds
    
    Returns:
        pandas DataFrame with schema matching ROBOTS_SCRAPE_SCHEMA
    """
    # Clean and validate domain
    clean_domain = domain.replace('http://', '').replace('https://', '').strip().strip('/')
    if not clean_domain:
        return pd.DataFrame()
    
    robots_url = f'{clean_domain}/robots.txt'
    user_agent = 'ResearchScraper/1.0'

    snapshots = get_cdx_snapshots(
        robots_url,
        user_agent=user_agent,
        limit=max_snapshots,
        from_timestamp=from_timestamp,
        to_timestamp=to_timestamp,
        timeout=timeout
    )

    if not snapshots:
        return pd.DataFrame()

    data = []

    for snap in snapshots:
        timestamp = snap['timestamp']
        original_url = snap['original']

        robots_text = None
        raw_robots_response_text = None
        robots_rules = {}
        robots_content_type = 'unknown'
        meta_robots = None
        x_robots_tag = None
        status_robots = None
        status_home = None
        error_details = None

        try:
            # ------------------ ROBOTS.TXT
            resp_robots = download_wayback(original_url, timestamp, user_agent, timeout)
            status_robots = resp_robots.status_code

            if status_robots == 200:
                raw_robots_response_text = resp_robots.text
                if is_html(raw_robots_response_text):
                    robots_text = "HTML Content (Not robots.txt)"
                    robots_content_type = "HTML_page"
                else:
                    robots_text = raw_robots_response_text
                    robots_rules = parse_robots_txt(robots_text)
                    robots_content_type = "robots.txt"
            else:
                robots_content_type = f"HTTP_Error_{status_robots}"

            # ------------------ HOMEPAGE
            home_url = f'http://{clean_domain}'
            resp_home = download_wayback(home_url, timestamp, user_agent, timeout)
            status_home = resp_home.status_code

            if status_home == 200:
                meta_robots = extract_meta_robots(resp_home.text)
                x_robots_tag = extract_x_robots_tag(resp_home.headers)

        except Timeout:
            error_details = "Timeout"
        except ConnectionError:
            error_details = "ConnectionError"
        except RequestException as e:
            error_details = f"RequestException: {str(e)[:100]}"
        except Exception as e:
            error_details = f"GeneralError: {str(e)[:100]}"

        data.append({
            "domain": domain,
            "timestamp": timestamp,
            "scraped_url": original_url,
            "robots_txt": robots_text,
            "raw_robots_response_text": raw_robots_response_text,
            "robots_content_type": robots_content_type,
            "robots_rules": json.dumps(robots_rules) if robots_rules else None,
            "meta_robots": meta_robots,
            "x_robots_tag": x_robots_tag,
            "status_robots": status_robots,
            "status_home": status_home,
            "error_details": error_details
        })

        time.sleep(2)  # Respectful rate limiting

    return pd.DataFrame(data)


###############################################################################
# BATCH PROCESSING WITH CHECKPOINTING
###############################################################################

def batch_scrape_domains(input_csv_path, output_csv, 
                        checkpoint_file="scraping_checkpoint.txt",
                        error_log_file="scraping_errors.txt",
                        max_snapshots=30,
                        from_timestamp='20220101000000',
                        to_timestamp='20240101000000'):
    """
    Scrape multiple domains from CSV with checkpointing and error recovery.
    
    Args:
        input_csv_path: Path to CSV with 'domain' column
        output_csv: Path to output CSV (will be created/appended)
        checkpoint_file: File to track progress
        error_log_file: File to log errors
        max_snapshots: Max snapshots per domain
        from_timestamp: Start date filter
        to_timestamp: End date filter
    """
    # Read domains
    try:
        domains_df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"ERROR: {input_csv_path} not found")
        return

    if "domain" not in domains_df.columns:
        print("ERROR: 'domain' column missing")
        return

    # Load checkpoint if exists
    start_index = 0
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            try:
                start_index = int(f.read().strip())
                print(f"Resuming from domain index {start_index}")
            except ValueError:
                print("Invalid checkpoint, starting from beginning")

    csv_exists = os.path.exists(output_csv)
    
    success_count = 0
    fail_count = 0
    total_snapshots = 0

    for index, row in domains_df.iterrows():
        if index < start_index:
            continue
            
        domain = str(row["domain"]).strip()
        if domain == "" or pd.isna(domain):
            continue

        print(f"\n### [{index+1}/{len(domains_df)}] Scraping: {domain} ###")

        try:
            df = scrape_robots_and_signals(
                domain, 
                max_snapshots=max_snapshots,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp
            )
            
            if not df.empty:
                df['datetime'] = pd.to_datetime(
                    df['timestamp'],
                    format='%Y%m%d%H%M%S',
                    errors='coerce'
                )
                
                mode = 'a' if csv_exists else 'w'
                with open(output_csv, mode, encoding='utf-8', newline='') as f:
                    df.to_csv(
                        f, 
                        mode=mode,
                        index=False, 
                        header=not csv_exists,
                        encoding='utf-8'
                    )
                csv_exists = True
                total_snapshots += len(df)
                success_count += 1
                print(f"  ✓ Wrote {len(df)} snapshots (Total: {total_snapshots})")
            else:
                print(f"  ⚠ No snapshots found")
                fail_count += 1
                with open(error_log_file, 'a') as err_log:
                    err_log.write(f"{domain}: No snapshots\n")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            fail_count += 1
            with open(error_log_file, 'a') as err_log:
                err_log.write(f"{domain}: {str(e)}\n")

        # Update checkpoint
        with open(checkpoint_file, 'w') as f:
            f.write(str(index + 1))

        time.sleep(10 + random.uniform(0, 5))  # Rate limiting

    print(f"\n>>> Scraping complete!")
    print(f">>> Successful: {success_count}, Failed: {fail_count}")
    print(f">>> Total snapshots: {total_snapshots}")

    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)


if __name__ == "__main__":
    # Example usage (modify paths as needed)
    batch_scrape_domains(
        input_csv_path="data/raw/unique_domains.csv",
        output_csv="data/processed/robots_wayback_analysis.csv"
    )
