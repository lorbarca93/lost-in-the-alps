# AI-Powered Hut History Enrichment Guide

## 🤖 Overview

This guide explains how to use AI to automatically enrich your mountain huts database with historical information, interesting facts, and cultural context.

**What it does:**
- Searches online for information about each hut
- Uses a LOCAL AI model (runs on your computer, no cloud costs!)
- Generates 2-3 paragraphs of historical context
- Adds it to the database
- Displays it beautifully in the hut detail sidebar

**Time:** Can run for days/weeks. Processes one hut every 30 seconds (configurable).

---

## 📋 Prerequisites

### 1. Install Ollama (Local AI Engine)

**Windows:**
1. Download from: https://ollama.ai/download/windows
2. Run the installer
3. Ollama will start automatically

**macOS:**
```bash
brew install ollama
ollama serve  # Start the service
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve  # Start the service
```

### 2. Download an AI Model

Open a new terminal and run:

```bash
# Recommended: Small, fast, good quality (2GB)
ollama pull llama3.2

# Alternative: Larger, better quality (4GB)
ollama pull llama3

# Alternative: Fast, efficient (4GB)
ollama pull mistral
```

**Model comparison:**
- `llama3.2` (2GB) - Fast, good for most users ✅ **Recommended**
- `llama3` (4.7GB) - Better quality, slower
- `mistral` (4.1GB) - Very good balance
- `llama2` (3.8GB) - Older but reliable

### 3. Install Python Dependencies

```bash
# Make sure you're in the project directory
cd C:\Users\loren\Downloads\lostinthealps

# Activate virtual environment (if you use one)
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Linux/Mac

# Install required packages
pip install requests beautifulsoup4
```

---

## 🚀 Quick Start

### Test Run (First 5 huts)

```bash
python tools/enrich_huts_with_ai.py --limit 5
```

This will:
1. ✅ Check Ollama connection
2. ✅ Verify the AI model is available
3. ✅ Process first 5 huts
4. ✅ Show you what it generates

### Full Run (All Huts)

```bash
python tools/enrich_huts_with_ai.py
```

Default settings:
- **Model:** llama3.2
- **Delay:** 30 seconds between huts
- **Batch save:** Every 10 huts
- **Can be interrupted** and resumed anytime!

---

## ⚙️ Configuration Options

### Use a Different Model

```bash
python tools/enrich_huts_with_ai.py --model mistral
```

### Faster Processing (15 second delay)

```bash
python tools/enrich_huts_with_ai.py --delay 15
```

### Slower Processing (1 minute delay)

```bash
python tools/enrich_huts_with_ai.py --delay 60
```

### Save Progress More Often

```bash
python tools/enrich_huts_with_ai.py --batch-size 5
```

### Combine Options

```bash
python tools/enrich_huts_with_ai.py --model llama3 --delay 20 --batch-size 20
```

---

## 🎯 Usage Scenarios

### Scenario 1: Run Overnight

```bash
# Start with slower processing
python tools/enrich_huts_with_ai.py --delay 45

# Let it run while you sleep
# Press Ctrl+C when you wake up to stop safely
```

### Scenario 2: Run When Computer is Idle

```bash
# Windows: Run in background
start /B python tools/enrich_huts_with_ai.py

# Linux/Mac: Run in background
nohup python tools/enrich_huts_with_ai.py &
```

### Scenario 3: Run for 2 Weeks

```bash
# Just let it run! It will process all huts eventually
python tools/enrich_huts_with_ai.py --delay 60

# With 7,472 huts at 60 seconds each:
# 7,472 huts × 60 seconds = 124.5 hours = ~5 days
```

### Scenario 4: Resume After Interruption

```bash
# Just run the same command again!
python tools/enrich_huts_with_ai.py

# It will automatically skip already-processed huts
```

---

## 📊 Monitoring Progress

### Check Log File

```bash
# Windows
type logs\ai_enrichment.log | more

# Linux/Mac
tail -f logs/ai_enrichment.log
```

### Check Progress File

```bash
# Windows
type data\ai_enrichment_progress.json

# Linux/Mac
cat data/ai_enrichment_progress.json
```

### Statistics

The log file shows:
- ✅ Huts successfully enriched
- ⚠️ Huts with errors
- 📊 Overall progress
- ⏱️ Timestamp for each hut

---

## 🛠️ Troubleshooting

### "Cannot connect to Ollama"

**Problem:** Ollama is not running

**Solution:**
```bash
# Check if Ollama is running
ollama list

# If not, start it:
# Windows: Open Ollama app from Start menu
# Linux/Mac: ollama serve
```

### "Model 'llama3.2' not found"

**Problem:** Model not downloaded

**Solution:**
```bash
ollama pull llama3.2
```

### Script is Too Slow

**Solution:** Decrease delay
```bash
python tools/enrich_huts_with_ai.py --delay 10
```

### Script is Using Too Much CPU

**Solution:** Increase delay or use smaller model
```bash
python tools/enrich_huts_with_ai.py --delay 60 --model llama3.2
```

### Want to Start Over

**Solution:** Reset progress
```bash
python tools/enrich_huts_with_ai.py --reset-progress
```

---

## 📖 How It Works

### Step 1: Search Online
The script searches DuckDuckGo for information about each hut:
- Hut name + location
- Historical information
- Relevant facts

### Step 2: AI Processing
Ollama (running locally on your PC) reads the search results and generates:
- Historical context (when was it built?)
- Cultural significance
- Interesting facts
- Why it's important to hikers

### Step 3: Database Update
The generated history is saved to:
- `ai_history` column in database
- `ai_enriched_at` timestamp
- `ai_model_used` (which model was used)

### Step 4: Display
The frontend automatically shows the history in a beautiful blue box:
- 📖 "History & Background" section
- Appears before the description
- Marked as "AI-generated historical context"

---

## 🎨 Frontend Display

Once enriched, huts will show:

```
┌─────────────────────────────────────────┐
│ 📖 History & Background                 │
│                                          │
│ The Rifugio Example was built in 1927   │
│ by the Italian Alpine Club. Originally  │
│ constructed as a refuge for climbers... │
│                                          │
│ ✨ AI-generated historical context       │
└─────────────────────────────────────────┘
```

**Styling:**
- Gradient blue background
- Border on the left
- Professional, readable font
- Stands out from regular description

---

## 📈 Performance

### Processing Time

| Huts | Delay | Total Time |
|------|-------|------------|
| 100  | 30s   | 50 minutes |
| 500  | 30s   | 4 hours    |
| 1000 | 30s   | 8 hours    |
| 7472 | 30s   | 62 hours   |
| 7472 | 60s   | 124 hours  |

### Resource Usage

- **CPU:** Moderate when processing, idle during delays
- **RAM:** ~500MB-2GB (depends on model)
- **Disk:** Minimal (just database updates)
- **Network:** Light (only searches, not LLM)

---

## 🔒 Privacy & Costs

### ✅ **100% Local AI**
- Ollama runs on YOUR computer
- No data sent to OpenAI, Claude, etc.
- No API costs!
- No rate limits

### 🔍 **Online Search**
- Uses DuckDuckGo HTML search (public, no API key)
- Only searches hut name + location
- Minimal data transfer

---

## 📝 Example Output

**Input:**
- Name: Rifugio Lagazuoi
- Country: Italy
- Altitude: 2752m

**AI-Generated History:**
```
Rifugio Lagazuoi stands as a testament to both natural beauty and 
historical significance in the Dolomites. Built in 1965, this refuge 
replaced an earlier structure destroyed during World War I, when the 
area was the site of intense mountain warfare between Italian and 
Austro-Hungarian forces.

The current building sits near the famous Lagazuoi tunnels, an 
extraordinary network of passages carved by Italian troops through 
the mountain. Today, hikers can explore these historic galleries, 
making the refuge not just a resting point but a gateway to living 
history.

Popular among mountaineers and history enthusiasts alike, Rifugio 
Lagazuoi offers panoramic views of the Dolomites and serves as a 
base for numerous hiking and via ferrata routes. Its strategic 
location at 2,752 meters makes it an essential stop on the 
Alta Via 1, one of the most famous long-distance trails in the Alps.
```

---

## 🎯 Best Practices

### 1. **Start Small**
Test with `--limit 5` first to see the quality

### 2. **Choose Your Speed**
- Fast (15s): Good network, fast PC
- Medium (30s): **Recommended for most users**
- Slow (60s): Overnight runs, older PCs

### 3. **Monitor Initially**
Watch the first 10-20 huts to ensure quality

### 4. **Let It Run**
Once you're happy, let it run unattended
- It saves progress regularly
- Safe to interrupt anytime
- Resumes automatically

### 5. **Check Results**
After processing some huts:
```bash
# Export to JSON
python website/api/export_huts.py

# View in browser
# Open http://localhost:8080 and click on enriched huts
```

---

## 🚀 After Enrichment

### Update Website Data

```bash
# 1. Export enriched data to JSON
python website/api/export_huts.py

# 2. Copy to website (if needed)
Copy-Item data\huts_data.json website\huts_data.json

# 3. Regenerate map
python tools/create_ultra_simple_map.py
Copy-Item mountain_huts_map.html website\
```

### Verify in Browser

1. Start server: `python -m http.server 8080` (in website folder)
2. Open: `http://localhost:8080/mountain_huts_map.html`
3. Click on enriched huts
4. Scroll down to see "📖 History & Background"

---

## 💡 Tips & Tricks

### Pause and Resume
```bash
# Press Ctrl+C to pause
# Run same command to resume - progress is saved!
```

### Check What's Left
```python
python
>>> import sqlite3
>>> conn = sqlite3.connect('data/mountain_huts.db')
>>> cursor = conn.cursor()
>>> cursor.execute("SELECT COUNT(*) FROM mountain_huts WHERE ai_history IS NULL")
>>> print(f"Remaining: {cursor.fetchone()[0]} huts")
```

### Quality Control
After processing, manually review a few huts:
- If quality is poor, try a different model
- If too generic, the search might not be finding info
- If factually wrong, it's making up info (normal for AI, can edit manually)

### Manual Editing
You can always edit the AI-generated history:
1. Open `data/mountain_huts.db` in DB Browser for SQLite
2. Find the hut
3. Edit the `ai_history` field
4. Re-export with `python website/api/export_huts.py`

---

## 🎉 Success!

Once complete, you'll have:
- ✅ Rich historical context for thousands of huts
- ✅ Professional, engaging descriptions
- ✅ Better user experience
- ✅ More valuable database
- ✅ All done locally, no costs!

**Enjoy your enriched mountain huts database!** 🏔️📖✨

---

## 📞 Support

For issues:
1. Check the log file: `logs/ai_enrichment.log`
2. Verify Ollama is running: `ollama list`
3. Test the model: `ollama run llama3.2 "Hello"`
4. Reset and try again: `--reset-progress`

Happy enriching! 🚀

