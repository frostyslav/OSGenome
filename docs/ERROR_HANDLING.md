# Error Handling Documentation

## Overview

OSGenome includes comprehensive error handling throughout the application to ensure reliability and provide clear feedback when issues occur.

## Error Handling Strategy

### 1. Defensive Programming
- Validate all inputs before processing
- Check file existence and permissions
- Verify data types and formats
- Handle edge cases gracefully

### 2. Graceful Degradation
- Continue processing when possible
- Provide partial results if complete processing fails
- Save progress incrementally

### 3. Clear Error Messages
- Log detailed errors for debugging
- Provide user-friendly messages
- Include context and suggestions for resolution

### 4. Recovery Mechanisms
- Retry logic for network operations
- Exponential backoff for rate-limited requests
- Atomic file operations to prevent corruption

## Error Categories

### File Operations

#### File Not Found
```python
FileNotFoundError: File not found: /path/to/file.txt
```
**Cause:** Specified file doesn't exist
**Solution:** Check file path and ensure file exists

#### Permission Denied
```python
PermissionError: Cannot read file: /path/to/file.txt
```
**Cause:** Insufficient permissions to read/write file
**Solution:** Check file permissions with `ls -la` and adjust with `chmod`

#### File Too Large
```python
ValueError: File too large: 150000000 bytes (max 100000000)
```
**Cause:** File exceeds size limits
**Solution:** Check file size, limits are:
- Uploads: 16MB
- Imports: 100MB
- JSON loads: 500MB

#### Encoding Error
```python
ValueError: File must be UTF-8 encoded
```
**Cause:** File is not UTF-8 encoded
**Solution:** Convert file to UTF-8: `iconv -f ISO-8859-1 -t UTF-8 input.txt > output.txt`

### Network Operations

#### Connection Timeout
```python
Request timeout on attempt 1/3
```
**Cause:** Network request took too long
**Action:** Automatic retry with exponential backoff
**Solution:** Check internet connection

#### Rate Limited (429)
```python
Rate limited (429) on attempt 1/3
```
**Cause:** Too many requests to SNPedia
**Action:** Automatic retry with longer delays
**Solution:** Wait for rate limit to reset (handled automatically)

#### Network Error
```python
Network error for rs123456: [Errno 11001] getaddrinfo failed
```
**Cause:** DNS resolution or network connectivity issue
**Solution:** Check internet connection and DNS settings

### Data Validation

#### Invalid RSid Format
```python
Skipping invalid rsid format: invalid123
```
**Cause:** RSid doesn't start with 'rs' or 'i'
**Action:** Skip invalid entry
**Solution:** Check data file format

#### Invalid Allele
```python
Invalid allele detected, using '-' instead
```
**Cause:** Allele is not A, T, C, G, -, I, or D
**Action:** Replace with '-'
**Solution:** Check data file quality

#### Invalid JSON
```python
Invalid JSON in file results.json: Expecting ',' delimiter
```
**Cause:** Corrupted or malformed JSON file
**Solution:** Delete file and re-run import/crawl

### Application Errors

#### No Data Available
```python
No result_table.json found, starting with empty results
```
**Cause:** Application started before data processing
**Action:** Start with empty dataset
**Solution:** Run data crawler first

#### Missing Required Fields
```python
Bad Request: Missing required fields
```
**Cause:** API request missing required parameters
**Solution:** Check API request format

#### Invalid File Type
```python
Bad Request: Invalid filename or file type
```
**Cause:** File type not in allowed list (.xlsx, .xls)
**Solution:** Use correct file format

## Error Handling by Component

### Flask Application (app.py)

#### Error Handlers
- **400 Bad Request**: Invalid input or missing fields
- **404 Not Found**: Resource doesn't exist
- **413 Request Too Large**: File exceeds size limit
- **500 Internal Server Error**: Unexpected server error

#### Example Response
```json
{
  "error": "Bad Request",
  "message": "Invalid filename or file type"
}
```

### Data Crawler (data_crawler.py)

#### Retry Logic
- **Max Retries**: 3 attempts
- **Retry Delay**: 5 seconds (exponential backoff for rate limits)
- **Request Timeout**: 30 seconds

#### Error Recovery
- Saves progress every 10 requests
- Can resume from last saved state
- Skips problematic entries and continues

#### Example Log
```
INFO: Grabbing data about SNP: rs123456
WARNING: Rate limited (429) on attempt 1/3
INFO: Sleeping for 5 seconds...
INFO: Successfully fetched rs123456
```

### Genome Importer (genome_importer.py)

#### Validation Checks
1. File path validation
2. File existence check
3. File size check (max 100MB)
4. File permissions check
5. Encoding validation (UTF-8)
6. Line count limit (1M lines)
7. RSid format validation
8. Allele validation

#### Error Recovery
- Skips invalid lines
- Continues processing valid data
- Reports statistics at end

### Utilities (utils.py)

#### Atomic File Operations
```python
# Write to temp file first
temp_file = "data.json.tmp"
write_to(temp_file)
# Atomic rename
os.replace(temp_file, "data.json")
```

#### Safe Loading
- Checks file existence
- Validates file size
- Handles JSON decode errors
- Returns empty dict on error

## Logging Levels

### DEBUG
Detailed information for diagnosing problems
```python
logger.debug("Successfully loaded data from results.json")
```

### INFO
Confirmation that things are working as expected
```python
logger.info("Found 20000 SNPs to be mapped to SNPedia")
```

### WARNING
Indication that something unexpected happened
```python
logger.warning("File exceeds 1 million lines, truncating")
```

### ERROR
Serious problem that prevented a function from completing
```python
logger.error("Failed to fetch rs123456 after 3 attempts")
```

## Configuration

### Set Log Level
```bash
# In .env file
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR

# Or environment variable
export LOG_LEVEL=DEBUG
```

### Enable Detailed Logging
```bash
# Development mode shows more details
export FLASK_ENV=development
export FLASK_DEBUG=true
```

## Troubleshooting Guide

### Problem: Application won't start

**Check:**
1. Dependencies installed: `uv sync`
2. Python version: `python --version` (need 3.13+)
3. Port availability: `lsof -i :5000`

**Solution:**
```bash
# Kill process on port
kill -9 $(lsof -t -i:5000)

# Or use different port
export FLASK_RUN_PORT=5001
```

### Problem: Data crawler fails

**Check:**
1. Internet connection: `ping bots.snpedia.com`
2. File permissions: `ls -la data/`
3. Disk space: `df -h`

**Solution:**
```bash
# Create data directory
mkdir -p data

# Fix permissions
chmod 755 data

# Resume from last save
uv run python SNPedia/data_crawler.py -f /path/to/data.txt
```

### Problem: Import fails

**Check:**
1. File format (tab-separated)
2. File encoding (UTF-8)
3. File size (< 100MB)

**Solution:**
```bash
# Check encoding
file -i your_data.txt

# Convert to UTF-8
iconv -f ISO-8859-1 -t UTF-8 input.txt > output.txt

# Check format
head -n 5 your_data.txt
```

### Problem: No data displayed

**Check:**
1. Data files exist: `ls -la data/`
2. Files not empty: `wc -l data/*.json`
3. Valid JSON: `python -m json.tool data/results.json`

**Solution:**
```bash
# Re-run import
uv run python SNPedia/genome_importer.py -f /path/to/data.txt

# Re-run crawler
uv run python SNPedia/data_crawler.py -f /path/to/data.txt

# Check logs
tail -f logs/app.log
```

## Best Practices

### 1. Always Check Logs
```bash
# View recent logs
tail -n 100 logs/app.log

# Follow logs in real-time
tail -f logs/app.log

# Search for errors
grep ERROR logs/app.log
```

### 2. Validate Input Files
```bash
# Check file format
head -n 5 your_data.txt

# Check file size
ls -lh your_data.txt

# Check encoding
file -i your_data.txt
```

### 3. Monitor Progress
```bash
# Watch data directory
watch -n 5 'ls -lh data/'

# Monitor log file
tail -f logs/app.log | grep INFO
```

### 4. Handle Interruptions
- Crawler saves progress every 10 requests
- Safe to interrupt with Ctrl+C
- Resume by running same command again

### 5. Backup Data
```bash
# Backup before major operations
cp -r data data.backup.$(date +%Y%m%d)

# Restore if needed
rm -rf data
mv data.backup.20251202 data
```

## Error Recovery Procedures

### Corrupted JSON Files

```bash
# Remove corrupted files
rm data/results.json
rm data/result_table.json

# Re-run import and crawl
uv run python SNPedia/genome_importer.py -f /path/to/data.txt
uv run python SNPedia/data_crawler.py -f /path/to/data.txt
```

### Incomplete Crawl

```bash
# Check progress
wc -l data/results.json

# Resume crawl (automatically continues from last save)
uv run python SNPedia/data_crawler.py -f /path/to/data.txt
```

### Application Crash

```bash
# Check for zombie processes
ps aux | grep python

# Kill if needed
pkill -f "python.*app.py"

# Restart
uv run python SNPedia/app.py
```

## Support

For additional help:
1. Check logs for detailed error messages
2. Review [SECURITY.md](SECURITY.md) for security-related issues
3. See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for upgrade issues
4. Open an issue on GitHub with:
   - Error message
   - Log output
   - Steps to reproduce
   - System information

## Summary

OSGenome now includes:
- ✅ Comprehensive input validation
- ✅ Automatic retry logic for network operations
- ✅ Graceful error handling and recovery
- ✅ Detailed logging at multiple levels
- ✅ Clear error messages for users
- ✅ Progress saving and resumption
- ✅ Atomic file operations
- ✅ Resource limit enforcement

All errors are logged with context and handled appropriately to ensure the application remains stable and provides useful feedback.
