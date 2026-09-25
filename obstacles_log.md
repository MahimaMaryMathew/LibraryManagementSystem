# Obstacle Log: CLI Library System

### Obstacle 1: Datetime Serialization in JSON (`TypeError`)
- **Issue:** Python's built-in `json.dump()` cannot natively serialize Python `datetime` objects, throwing a `TypeError: Object of type datetime is not JSON serializable` when saving the catalog.
- **Solution:** Formatted `due_date` as an ISO string (`"%Y-%m-%d"`) before writing to `catalog.json`, and parsed string dates back into `datetime` objects using `datetime.strptime()` when loading the JSON file on startup.

### Obstacle 2: Missing External Catalog File (`FileNotFoundError`)
- **Issue:** Decoupling book data into an external `catalog.json` meant the script crashed on initial run if `catalog.json` did not exist in the working directory.
- **Solution:** Implemented `os.path.exists()` checks inside `load_catalog()`. If missing or corrupt, the program catches `IOError` and `json.JSONDecodeError`, initializes a safe empty dictionary (`{}`), and avoids crashing.

### Obstacle 3: Accidental File Overwrites in Logging
- **Issue:** Opening the activity log with standard write mode (`open(filename, "w")`) wiped out historical lending records every time a new CLI session started.
- **Solution:** Switched the file opening mode to append mode (`open(filename, "a")`), allowing transaction logs to accumulate continuously across multiple runs.

### Obstacle 4: Input Whitespace & Case Sensitivity Handling
- **Issue:** User-entered Book IDs like `"b101 "` failed lookups against stored dictionary keys like `"B101"`.
- **Solution:** Standardized user menu input across all CLI prompts using `.strip().upper()` for IDs and `.strip()` for names and search strings.

### Obstacle 5: Tuples and Unpacking in List Operations
- **Issue:** Storing search matches raised `TypeError` when passing multiple items directly to `.append(book_id, info)`.
- **Solution:** Wrapped key-value pairs inside inner parentheses `matches.append((book_id, info))` to pass them as a unified tuple object, making tuple unpacking (`for book_id, info in matches`) seamless during print formatting.
