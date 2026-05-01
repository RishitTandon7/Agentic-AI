# Restart Fix Report

The server was restarting repeatedly likely due to file modifications within the watched directory. When running Flask in debug mode (`debug=True`), any file change triggers a reload.

## Issues Identified & Fixed:

1. **Scraper Log Writing Loop**:
   - `scraper/providers.py` was writing to `scraper_log.txt` on every search.
   - **Fix**: Commented out the file writing block.

2. **Model Cache Updates**:
   - `model_persistence.py` was writing to `model_cache.json` in the root directory.
   - **Fix**: Changed filename to `.model_cache.json` (hidden file) to prevent triggering reloader.

3. **CSV Data Storage**:
   - `storage/csv_store.py` was writing to `data/products.csv` and `data/negotiation_history.csv`.
   - **Fix**: Changed filenames to start with a dot (`.products.csv`, `.negotiation_history.csv`) so they are treated as hidden/ignored files by the reloader.

## Recommended Actions:

- **Manually Restart Server**: Please stop the current server (Ctrl+C) and run `python .\web_app.py` again to ensure all changes are picked up cleanly and the reloader is watching the correct files.
- **Data Migration**: Existing data in `products.csv` and `negotiation_history.csv` will be ignored by the new configuration. If you need to keep it, rename the files:
  ```powershell
  ren data\products.csv data\.products.csv
  ren data\negotiation_history.csv data\.negotiation_history.csv
  ren model_cache.json .model_cache.json
  ```
