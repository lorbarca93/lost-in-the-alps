# Czech to English Translation Setup

## Overview

The boudy.info scraper now automatically translates Czech text to English during scraping. This ensures all hut descriptions, access information, and other text fields are in English for better consistency across the database.

## Installation

The translation feature uses the `deep-translator` library. Install it with:

```bash
pip install deep-translator
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## How It Works

### Automatic Translation

The `TextTranslator` class in `src/translator.py` automatically:

1. **Detects Czech text** - Uses Czech characters (á, č, ď, é, etc.) and common Czech words to identify text that needs translation
2. **Translates to English** - Uses Google Translate API (via deep-translator) to translate Czech text
3. **Handles errors gracefully** - If translation fails, returns the original text
4. **Rate limiting** - Includes delays between translations to avoid API rate limits

### Translated Fields

The following fields are automatically translated from Czech to English:

- `description` - Hut descriptions
- `water_source` - Water source information
- `access` - Access/trail information
- `opening_hours` - Opening hours and season information
- `owner` - Owner information (if it contains Czech text)
- `manager` - Manager information (if it contains Czech text)
- `comments` - User comments

### Usage

The translation is **automatic** - no configuration needed! When you run the boudy.info scraper:

```bash
python src/scrapers/scraper_boudy_info.py
```

All Czech text will be automatically translated to English before being saved to the database.

## Example

**Before (Czech):**
```
"Bouda je otevřena celoročně. Voda je k dispozici z nedalekého potoka."
```

**After (English):**
```
"The hut is open year-round. Water is available from a nearby stream."
```

## Technical Details

### Translation Service

- **Service**: Google Translate (via deep-translator)
- **Source Language**: Czech (cs)
- **Target Language**: English (en)
- **Rate Limiting**: 100ms delay between translations
- **Text Limit**: 5000 characters per translation

### Error Handling

- If translation fails, the original Czech text is kept
- If the library is not installed, translation is skipped (with a warning)
- Invalid or empty text is not translated

## Troubleshooting

### Translation Not Working

1. **Check installation:**
   ```bash
   pip list | grep deep-translator
   ```

2. **Check logs:**
   The scraper will log warnings if translation is disabled or fails

3. **Manual test:**
   ```python
   from src.translator import get_translator
   translator = get_translator()
   result = translator.translate("Bouda je otevřena celoročně")
   print(result)  # Should print English translation
   ```

### Rate Limiting Issues

If you encounter rate limiting errors:

- The scraper includes automatic delays (100ms between translations)
- For large batches, you may need to increase the delay in `src/translator.py`
- Consider running scrapers during off-peak hours

## Disabling Translation

If you want to disable translation (keep original Czech text):

1. Comment out the translator initialization in `scraper_boudy_info.py`
2. Or set `self.translator.enabled = False` in the scraper's `__init__` method

## Notes

- Translation adds a small delay to scraping (approximately 100ms per text field)
- The scraper will work without translation installed, but Czech text will remain in Czech
- Translation quality depends on Google Translate's accuracy
- Some proper nouns and technical terms may not translate perfectly

