# LibraryManagementSystem
Command-line library system in Python that manages books, borrowers, and lending activity, using core data structures and control flow rather than any external libraries or frameworks

``` text
python-library-system/
│── app.py                  # Main Python CLI application
│── catalog.json            # External book database
│── borrowing_records.txt   # Generated lending activity log
│── obstacles_log.md        # Documentation of technical challenges
│── README.md               # Overview, setup instructions, and usage guide 
```
## Features
- **JSON Data Persistence:** Book catalog is stored and automatically synced with `catalog.json`.
- **Search & Filter:** Case-insensitive search by title or author.
- **Lending Logic:** Tracks borrowed status, assigns borrowers, and calculates due dates.
- **Overdue Tracking:** Detects overdue books using `datetime` comparison.
- **Transaction Logging:** Appends activity records to `borrowing_records.txt`.

## Prerequisites
- Python 3.10 or higher 
