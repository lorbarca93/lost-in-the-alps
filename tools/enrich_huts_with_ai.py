"""
AI-Powered Hut History Enrichment Script
==========================================

This script enriches the mountain huts database with historical information
and interesting facts using a LOCAL Large Language Model (Ollama).

Features:
- Uses local LLM (no cloud costs!)
- Searches online for hut information
- Generates historical context
- Resumes from where it left off
- Runs slowly and safely (can run for weeks)
- Detailed logging
- Progress tracking

Requirements:
1. Install Ollama: https://ollama.ai/
2. Pull a model: `ollama pull llama3.2` or `ollama pull mistral`
3. Install Python packages: pip install requests beautifulsoup4

Usage:
    python tools/enrich_huts_with_ai.py
    
    # Or with options:
    python tools/enrich_huts_with_ai.py --model llama3.2 --delay 30 --batch-size 10
"""

import sqlite3
import requests
import json
import time
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# CONFIGURATION
# ============================================================================

DB_PATH = "data/mountain_huts.db"
PROGRESS_FILE = "data/ai_enrichment_progress.json"
LOG_FILE = "logs/ai_enrichment.log"

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"  # or "mistral", "llama2", etc.

# Rate limiting
DEFAULT_DELAY_BETWEEN_HUTS = 30  # seconds
DEFAULT_DELAY_AFTER_ERROR = 60  # seconds
DEFAULT_BATCH_SIZE = 10  # Save progress every N huts


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Setup logging to file and console"""
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('HutEnricher')
    logger.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()


# ============================================================================
# DATABASE SCHEMA UPDATE
# ============================================================================

def update_database_schema():
    """Add AI-generated fields to database if they don't exist"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Add ai_history field
        try:
            cursor.execute("""
                ALTER TABLE mountain_huts 
                ADD COLUMN ai_history TEXT
            """)
            logger.info("Added 'ai_history' column to database")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Add ai_enriched_at field
        try:
            cursor.execute("""
                ALTER TABLE mountain_huts 
                ADD COLUMN ai_enriched_at TIMESTAMP
            """)
            logger.info("Added 'ai_enriched_at' column to database")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Add ai_model_used field
        try:
            cursor.execute("""
                ALTER TABLE mountain_huts 
                ADD COLUMN ai_model_used TEXT
            """)
            logger.info("Added 'ai_model_used' column to database")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        conn.commit()
        conn.close()
        logger.info("Database schema updated successfully")
        
    except Exception as e:
        logger.error(f"Error updating database schema: {e}")
        raise


# ============================================================================
# OLLAMA LLM INTERFACE
# ============================================================================

class OllamaLLM:
    """Interface to local Ollama LLM"""
    
    def __init__(self, model: str = DEFAULT_MODEL, base_url: str = OLLAMA_BASE_URL):
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
    
    def check_connection(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_model(self) -> bool:
        """Check if the specified model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(self.model in m.get('name', '') for m in models)
            return False
        except:
            return False
    
    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> Optional[str]:
        """Generate text using Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=120  # 2 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return None


# ============================================================================
# WEB SEARCH (Simple DuckDuckGo HTML scraping)
# ============================================================================

def search_hut_online(hut_name: str, country: str, altitude: str) -> Optional[str]:
    """
    Search for information about the hut online
    Uses DuckDuckGo HTML (no API key needed)
    """
    try:
        # Build search query
        query = f"{hut_name} mountain hut {country}"
        if altitude and altitude != "N/A":
            query += f" {altitude}m"
        
        # DuckDuckGo HTML search (simple, no API needed)
        search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Extract text snippets from search results
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find result snippets
            snippets = []
            for result in soup.find_all('a', class_='result__snippet'):
                text = result.get_text(strip=True)
                if text and len(text) > 20:
                    snippets.append(text)
            
            if snippets:
                return " | ".join(snippets[:3])  # Top 3 results
        
        return None
        
    except Exception as e:
        logger.warning(f"Search error for {hut_name}: {e}")
        return None


# ============================================================================
# HISTORY GENERATION
# ============================================================================

def generate_hut_history(
    hut: Dict,
    llm: OllamaLLM,
    search_results: Optional[str]
) -> Optional[str]:
    """
    Generate historical information about the hut using LLM
    """
    
    # Build comprehensive prompt
    prompt = f"""You are a mountain historian specializing in Alpine huts and refuges.

Generate a concise, informative historical description (2-3 paragraphs, max 300 words) for this mountain hut:

**Hut Name:** {hut['name']}
**Location:** {hut['country']}, {hut['region'] if hut['region'] else 'Alps'}
**Altitude:** {hut['altitude']}m
**Type:** {hut['hut_type']}
"""

    if search_results:
        prompt += f"\n**Online Information Found:**\n{search_results}\n"
    
    if hut['description'] and hut['description'] != 'N/A' and len(hut['description']) > 10:
        prompt += f"\n**Existing Description:**\n{hut['description']}\n"
    
    prompt += """
**Task:** Write an engaging historical description that includes:
1. When the hut was built (if known, otherwise estimate era)
2. Historical significance or interesting facts
3. Notable features or history of the location
4. Why it's important to hikers/mountaineers

Write in a friendly, informative tone. Focus on history and cultural significance.
If you don't have specific information, provide general historical context about mountain huts in that region and era.

Begin directly with the history (no labels like "History:" or "Description:"):"""

    # Generate using LLM
    history = llm.generate(prompt, max_tokens=400, temperature=0.7)
    
    if history and len(history) > 100:  # Minimum length check
        return history
    
    return None


# ============================================================================
# PROGRESS TRACKING
# ============================================================================

def load_progress() -> Dict:
    """Load progress from file"""
    try:
        if Path(PROGRESS_FILE).exists():
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    
    return {
        'processed_ids': [],
        'last_id': 0,
        'total_processed': 0,
        'total_enriched': 0,
        'started_at': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat()
    }


def save_progress(progress: Dict):
    """Save progress to file"""
    try:
        progress['last_updated'] = datetime.now().isoformat()
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving progress: {e}")


# ============================================================================
# MAIN ENRICHMENT LOGIC
# ============================================================================

def enrich_huts(
    model: str = DEFAULT_MODEL,
    delay: int = DEFAULT_DELAY_BETWEEN_HUTS,
    batch_size: int = DEFAULT_BATCH_SIZE,
    limit: Optional[int] = None
):
    """
    Main function to enrich all huts with AI-generated history
    """
    
    logger.info("="*80)
    logger.info("AI HUT ENRICHMENT STARTED")
    logger.info("="*80)
    logger.info(f"Model: {model}")
    logger.info(f"Delay between huts: {delay} seconds")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Database: {DB_PATH}")
    
    # Initialize LLM
    logger.info("Initializing Ollama LLM...")
    llm = OllamaLLM(model=model)
    
    # Check Ollama connection
    if not llm.check_connection():
        logger.error("❌ Cannot connect to Ollama!")
        logger.error("Please make sure Ollama is running:")
        logger.error("  1. Install from: https://ollama.ai/")
        logger.error("  2. Run: ollama serve")
        return
    
    logger.info("✅ Connected to Ollama")
    
    # Check if model exists
    if not llm.check_model():
        logger.error(f"❌ Model '{model}' not found!")
        logger.error(f"Please pull the model first: ollama pull {model}")
        logger.error("Available models: llama3.2, llama3, mistral, llama2, etc.")
        return
    
    logger.info(f"✅ Model '{model}' is available")
    
    # Update database schema
    logger.info("Updating database schema...")
    update_database_schema()
    
    # Load progress
    progress = load_progress()
    logger.info(f"Previous progress: {progress['total_processed']} huts processed, {progress['total_enriched']} enriched")
    
    # Get huts from database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.cursor()
    
    # Query huts that haven't been enriched yet
    query = """
        SELECT * FROM mountain_huts 
        WHERE (ai_history IS NULL OR ai_history = '')
        AND latitude IS NOT NULL 
        AND longitude IS NOT NULL
        ORDER BY id
    """
    
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    huts = [dict(row) for row in cursor.fetchall()]
    
    total_huts = len(huts)
    logger.info(f"📊 Found {total_huts} huts to enrich")
    
    if total_huts == 0:
        logger.info("✅ All huts are already enriched!")
        conn.close()
        return
    
    # Process each hut
    enriched_count = 0
    error_count = 0
    
    for idx, hut in enumerate(huts, 1):
        hut_id = hut['id']
        hut_name = hut['name']
        
        # Skip if already processed in this session
        if hut_id in progress['processed_ids']:
            continue
        
        logger.info("")
        logger.info(f"[{idx}/{total_huts}] Processing: {hut_name}")
        logger.info(f"  Country: {hut['country']}, Altitude: {hut['altitude']}m")
        
        try:
            # Step 1: Search online for information
            logger.info(f"  🔍 Searching online for information...")
            search_results = search_hut_online(
                hut_name,
                hut['country'] or 'Alps',
                str(hut['altitude']) if hut['altitude'] else ''
            )
            
            if search_results:
                logger.info(f"  ✅ Found online information ({len(search_results)} chars)")
            else:
                logger.info(f"  ⚠️  No online information found, will use general context")
            
            # Small delay after search
            time.sleep(2)
            
            # Step 2: Generate history using LLM
            logger.info(f"  🤖 Generating historical description...")
            history = generate_hut_history(hut, llm, search_results)
            
            if history:
                logger.info(f"  ✅ Generated history ({len(history)} chars)")
                logger.info(f"  Preview: {history[:150]}...")
                
                # Step 3: Update database
                cursor.execute("""
                    UPDATE mountain_huts 
                    SET ai_history = ?,
                        ai_enriched_at = ?,
                        ai_model_used = ?
                    WHERE id = ?
                """, (history, datetime.now(), model, hut_id))
                
                conn.commit()
                enriched_count += 1
                logger.info(f"  💾 Saved to database")
                
            else:
                logger.warning(f"  ⚠️  Failed to generate history")
                error_count += 1
            
            # Update progress
            progress['processed_ids'].append(hut_id)
            progress['last_id'] = hut_id
            progress['total_processed'] += 1
            if history:
                progress['total_enriched'] += 1
            
            # Save progress every batch_size huts
            if idx % batch_size == 0:
                save_progress(progress)
                logger.info(f"  💾 Progress saved ({enriched_count}/{idx} enriched)")
            
            # Rate limiting - wait before next hut
            if idx < total_huts:  # Don't delay after last hut
                logger.info(f"  ⏳ Waiting {delay} seconds before next hut...")
                time.sleep(delay)
            
        except KeyboardInterrupt:
            logger.info("\n⚠️  Interrupted by user. Saving progress...")
            save_progress(progress)
            conn.close()
            logger.info("Progress saved. You can resume later by running the script again.")
            return
            
        except Exception as e:
            logger.error(f"  ❌ Error processing hut: {e}")
            error_count += 1
            logger.info(f"  ⏳ Waiting {DEFAULT_DELAY_AFTER_ERROR} seconds after error...")
            time.sleep(DEFAULT_DELAY_AFTER_ERROR)
    
    # Final save
    save_progress(progress)
    conn.close()
    
    # Summary
    logger.info("")
    logger.info("="*80)
    logger.info("ENRICHMENT COMPLETE!")
    logger.info("="*80)
    logger.info(f"✅ Successfully enriched: {enriched_count} huts")
    logger.info(f"⚠️  Errors: {error_count}")
    logger.info(f"📊 Total processed: {progress['total_processed']}")
    logger.info(f"💾 Progress saved to: {PROGRESS_FILE}")
    logger.info(f"📝 Log saved to: {LOG_FILE}")
    logger.info("="*80)


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Enrich mountain huts database with AI-generated historical information',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default settings (llama3.2, 30s delay)
  python tools/enrich_huts_with_ai.py
  
  # Use different model
  python tools/enrich_huts_with_ai.py --model mistral
  
  # Faster processing (careful!)
  python tools/enrich_huts_with_ai.py --delay 10
  
  # Test on first 5 huts
  python tools/enrich_huts_with_ai.py --limit 5
  
  # Resume after interruption (just run again)
  python tools/enrich_huts_with_ai.py
        """
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default=DEFAULT_MODEL,
        help=f'Ollama model to use (default: {DEFAULT_MODEL})'
    )
    
    parser.add_argument(
        '--delay',
        type=int,
        default=DEFAULT_DELAY_BETWEEN_HUTS,
        help=f'Delay in seconds between huts (default: {DEFAULT_DELAY_BETWEEN_HUTS})'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f'Save progress every N huts (default: {DEFAULT_BATCH_SIZE})'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of huts to process (for testing)'
    )
    
    parser.add_argument(
        '--reset-progress',
        action='store_true',
        help='Reset progress and start from beginning'
    )
    
    args = parser.parse_args()
    
    # Reset progress if requested
    if args.reset_progress:
        if Path(PROGRESS_FILE).exists():
            Path(PROGRESS_FILE).unlink()
            logger.info("Progress reset!")
    
    # Run enrichment
    try:
        enrich_huts(
            model=args.model,
            delay=args.delay,
            batch_size=args.batch_size,
            limit=args.limit
        )
    except KeyboardInterrupt:
        logger.info("\n\nScript interrupted. Progress has been saved.")
        logger.info("Run the script again to resume from where you left off.")


if __name__ == "__main__":
    main()

