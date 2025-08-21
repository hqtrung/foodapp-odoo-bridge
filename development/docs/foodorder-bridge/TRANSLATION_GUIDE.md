# Vietnamese Restaurant Menu Translation Workflow Guide

This guide explains how to use the `translate_menu.py` script to automate your restaurant menu translations using Vertex AI Gemini 2.0 Flash.

## 🚀 Quick Start

```bash
# Translate to all supported languages
python translate_menu.py

# Translate to specific languages only
python translate_menu.py --languages en,fr,es
```

## 📋 Command Options

### Basic Usage
```bash
python translate_menu.py [OPTIONS]
```

### Available Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--languages` | `-l` | Target languages (comma-separated) | `--languages en,fr,es` |
| `--reload` | `-r` | Force reload from Odoo before translation | `--reload` |
| `--batch-size` | `-b` | Items per batch (default: 20) | `--batch-size 10` |
| `--dry-run` | `-d` | Test without making changes | `--dry-run` |
| `--report` | `-R` | Generate detailed JSON report | `--report` |
| `--force` | `-f` | Save even if validation fails | `--force` |
| `--verbose` | `-v` | Enable detailed logging | `--verbose` |

### Supported Languages

The script supports all languages configured in your system:
- `vi` - Vietnamese (source language)
- `en` - English
- `fr` - French
- `it` - Italian  
- `es` - Spanish
- `zh` - Chinese (Simplified)
- `zh-TW` - Chinese (Traditional)
- `th` - Thai
- `ja` - Japanese

## 📝 Usage Examples

### 1. Basic Translation (All Languages)
```bash
python translate_menu.py
```
Translates all products to all supported languages using Vertex AI.

### 2. Specific Languages
```bash
python translate_menu.py --languages en,fr
```
Translates only to English and French.

### 3. Force Reload from Odoo
```bash
python translate_menu.py --reload --languages en
```
Reloads product data from Odoo first, then translates to English.

### 4. Test Run (No Changes)
```bash
python translate_menu.py --dry-run --report
```
Simulates the translation process and generates a report without making changes.

### 5. Custom Batch Size
```bash
python translate_menu.py --batch-size 10 --languages en,fr,es
```
Processes translations in smaller batches (useful for API rate limiting).

### 6. Detailed Logging
```bash
python translate_menu.py --verbose --languages en
```
Shows detailed processing information and API calls.

### 7. Force Save Despite Validation Errors
```bash
python translate_menu.py --force --languages en
```
Saves translations even if some validation checks fail.

## 🔍 Understanding the Output

The script provides colored console output showing:

- **🔧 Service Initialization**: Connection to Odoo, Vertex AI, and Firestore
- **📦 Product Loading**: Number of products and categories loaded
- **🌐 Translation Progress**: Real-time batch processing updates
- **✅ Validation Results**: Quality checks on translations
- **💾 Save Operations**: File cache and Firestore updates
- **📊 Final Report**: Statistics and sample translations

## 📊 Reports

### Console Report
Always shows:
- Total products processed
- Translation coverage by language
- Sample translations
- Processing statistics

### JSON Report (with `--report`)
Creates a timestamped file like `translation_report_20250820_234257.json` containing:
- Complete statistics
- All product translations
- Detailed metadata
- Processing timestamps

## 🚨 Error Handling

The script includes robust error handling:

- **Automatic Retry**: Failed API calls are retried with exponential backoff
- **Fallback System**: Falls back to Google Translate if Vertex AI fails
- **Validation Checks**: Ensures product codes are preserved
- **Safe Backup**: Creates backups before overwriting data

## 🔧 Troubleshooting

### Common Issues

1. **"No translation service available"**
   - Check your Google Cloud credentials
   - Verify Vertex AI API is enabled
   - Ensure GOOGLE_CLOUD_PROJECT is set

2. **"Translation validation failed"**
   - Some translations may be missing product codes
   - Use `--force` to save anyway or fix manually

3. **"Batch translation failed"**
   - Try smaller batch size with `--batch-size 5`
   - Check API quotas and rate limits

4. **"Import errors"**
   - Make sure you're in the project directory
   - Verify all dependencies are installed

### Getting Help

```bash
python translate_menu.py --help
```

## 💡 Best Practices

1. **Start Small**: Test with `--dry-run` first
2. **Use Specific Languages**: Only translate what you need
3. **Monitor Logs**: Use `--verbose` to understand what's happening
4. **Regular Updates**: Run weekly to keep translations fresh
5. **Backup First**: The script creates backups, but extra safety doesn't hurt

## 🎯 Workflow Steps

The script follows this workflow:

1. **Initialize Services** → Connect to Odoo, Vertex AI, Firestore
2. **Load Products** → Get current menu data (optionally reload from Odoo)
3. **Process Languages** → Translate to each target language in batches
4. **Validate Results** → Check translation quality and completeness
5. **Save Translations** → Update file cache and sync to Firestore
6. **Generate Report** → Show statistics and sample translations

## 📈 Performance Tips

- **Batch Size**: 20-25 items per batch is optimal for Gemini 2.0
- **Language Order**: Process high-priority languages first
- **Caching**: Translations are cached for 7 days to avoid redundant API calls
- **Timing**: Run during off-peak hours to ensure best API performance

## 🌟 Translation Quality Features

- **Context Awareness**: Gemini understands Vietnamese restaurant context
- **Code Preservation**: Product codes (A1, B2, C3) are maintained exactly
- **Cultural Sensitivity**: "Banh Mi" kept for international recognition
- **Culinary Accuracy**: Vietnamese food terms properly translated
- **Consistency**: Same translation style across all products

---

*This translation workflow is powered by Vertex AI Gemini 2.0 Flash and integrates seamlessly with your existing Vietnamese restaurant system.*