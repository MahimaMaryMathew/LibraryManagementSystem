import json
import os
from datetime import datetime, timedelta

CATALOG_FILE = "catalog.json"
RECORDS_FILE = "borrowing_records.txt"
STANDARD_LOAN_DAYS = 21

borrow_history = []

def load_catalog():
    """Loads library catalog from external JSON file. Returns empty dict if missing."""
    if not os.path.exists(CATALOG_FILE):
        print(f"Notice: '{CATALOG_FILE}' not found. Starting with an empty catalog.")
        return {}
    
    try:
        with open(CATALOG_FILE, "r") as file:
            data = json.load(file)
            
            # Convert ISO string dates back into datetime objects for date arithmetic
            for book_id, info in data.items():
                if info.get("due_date"):
                    info["due_date"] = datetime.strptime(info["due_date"], "%Y-%m-%d")
            return data
            
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not read '{CATALOG_FILE}' ({e}). Starting with empty catalog.")
        return {}


def save_catalog(catalog):
    """Saves current catalog state back to catalog.json."""
    serializable_catalog = {}
    
    for book_id, info in catalog.items():
        serializable_catalog[book_id] = {
            "title": info["title"],
            "author": info["author"],
            "is_available": info["is_available"],
            "borrower": info["borrower"],
            "due_date": info["due_date"].strftime("%Y-%m-%d") if isinstance(info["due_date"], datetime) else info["due_date"]
        }
        
    try:
        with open(CATALOG_FILE, "w") as file:
            json.dump(serializable_catalog, file, indent=4)
    except IOError as e:
        print(f"Error saving to {CATALOG_FILE}: {e}")



library_catalog = load_catalog()



def add_book(book_id, title, author):
    """Adds a new book and syncs immediately to JSON."""
    if book_id in library_catalog:
        print(f"\nError: Book ID '{book_id}' already exists.")
        return False
    
    library_catalog[book_id] = {
        "title": title,
        "author": author,
        "is_available": True,
        "borrower": None,
        "due_date": None
    }
    
    save_catalog(library_catalog)
    print(f"\nSuccess: Added '{title}' by {author} [ID: {book_id}]. Saved to {CATALOG_FILE}.")
    return True


def search_books(query):
    """Searches catalog by title or author."""
    query_lower = query.lower()
    matches = []
    
    for book_id, info in library_catalog.items():
        if query_lower in info["title"].lower() or query_lower in info["author"].lower():
            matches.append((book_id, info))
            
    if not matches:
        print(f"\nNo books found matching '{query}'.")
        return
    
    print(f"\nSearch Results for '{query}':")
    for book_id, info in matches:
        status = "Available" if info["is_available"] else f"Borrowed by {info['borrower']}"
        print(f"- [{book_id}] {info['title']} by {info['author']} ({status})")


def borrow_book(book_id, borrower_name):
    """Handles borrowing logic, sets due date, and updates JSON."""
    if book_id not in library_catalog:
        print(f"\nError: Book ID '{book_id}' not found in catalog.")
        return
    
    book = library_catalog[book_id]
    
    if not book["is_available"]:
        print(f"\nUnavailable: '{book['title']}' is currently checked out by {book['borrower']}.")
        return
    
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=STANDARD_LOAN_DAYS)
    
    book["is_available"] = False
    book["borrower"] = borrower_name
    book["due_date"] = due_date
    
    record = {
        "action": "BORROW",
        "book_id": book_id,
        "title": book['title'],
        "borrower": borrower_name,
        "date": borrow_date.strftime("%Y-%m-%d %H:%M:%S"),
        "due_date": due_date.strftime("%Y-%m-%d")
    }
    borrow_history.append(record)
    
    save_catalog(library_catalog)
    print(f"\nSuccess: '{book['title']}' checked out to {borrower_name}. Due Date: {due_date.strftime('%Y-%m-%d')}.")


def return_book(book_id):
    """Handles returning a book and updates JSON."""
    if book_id not in library_catalog:
        print(f"\nError: Book ID '{book_id}' not found.")
        return
        
    book = library_catalog[book_id]
    
    if book["is_available"]:
        print(f"\nError: '{book['title']}' is not currently borrowed.")
        return
    
    borrower = book["borrower"]
    book["is_available"] = True
    book["borrower"] = None
    book["due_date"] = None
    
    record = {
        "action": "RETURN",
        "book_id": book_id,
        "title": book['title'],
        "borrower": borrower,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "due_date": "N/A"
    }
    borrow_history.append(record)
    
    save_catalog(library_catalog)
    print(f"\nSuccess: '{book['title']}' has been returned by {borrower}.")


def check_overdue_books():
    """Identifies and displays all overdue books."""
    today = datetime.now()
    overdue_found = False
    
    print("\n--- Overdue Books Report ---")
    for book_id, info in library_catalog.items():
        if not info["is_available"] and info["due_date"]:
            if today > info["due_date"]:
                overdue_found = True
                days_overdue = (today - info["due_date"]).days
                print(f"OVERDUE: [{book_id}] '{info['title']}' | Borrower: {info['borrower']} | "
                      f"Due Date: {info['due_date'].strftime('%Y-%m-%d')} ({days_overdue} days late)")
                
    if not overdue_found:
        print("No overdue books found.")


def generate_summary():
    """Displays high-level statistics about the catalog."""
    total_books = len(library_catalog)
    borrowed_books = sum(1 for b in library_catalog.values() if not b["is_available"])
    available_books = total_books - borrowed_books
    
    print("\n==========================================")
    print("         LIBRARY SYSTEM SUMMARY           ")
    print("==========================================")
    print(f"Total Books in Catalog : {total_books}")
    print(f"Available Books        : {available_books}")
    print(f"Currently Borrowed     : {borrowed_books}")
    print("==========================================\n")



def save_records_to_file(filename=RECORDS_FILE):
    """Appends session transaction logs to borrowing_records.txt."""
    if not borrow_history:
        print("\nNo new activity to save in log file.")
        return

    try:
        with open(filename, "a") as file:  # 'a' appends to keep history across sessions
            for log in borrow_history:
                line = f"[{log['date']}] {log['action']} - Book ID: {log['book_id']} ('{log['title']}') | User: {log['borrower']} | Due: {log['due_date']}\n"
                file.write(line)
                
        print(f"\nActivity log successfully saved to '{filename}'.")
    except IOError as e:
        print(f"Failed to write log file: {e}")

def display_menu():
    print("\n" + "=" * 40)
    print("     LIBRARY MANAGEMENT SYSTEM MENU     ")
    print("=" * 40)
    print("1. Search Books")
    print("2. Borrow a Book")
    print("3. Return a Book")
    print("4. Add a New Book")
    print("5. View Overdue Books")
    print("6. View Library Summary")
    print("7. Save Activity Log & Exit")
    print("=" * 40)


if __name__ == "__main__":
    while True:
        display_menu()
        choice = input("Enter your choice (1-7): ").strip()
        
        match choice:
            case "1":
                query = input("Enter search keyword (title/author): ").strip()
                if query:
                    search_books(query)
                else:
                    print("Search query cannot be empty.")

            case "2":
                book_id = input("Enter Book ID to borrow: ").strip().upper()
                borrower = input("Enter Borrower Name: ").strip()
                if book_id and borrower:
                    borrow_book(book_id, borrower)
                else:
                    print("Book ID and Borrower Name are required.")

            case "3":
                book_id = input("Enter Book ID to return: ").strip().upper()
                if book_id:
                    return_book(book_id)
                else:
                    print("Book ID is required.")

            case "4":
                book_id = input("Enter New Book ID (e.g., B105): ").strip().upper()
                title = input("Enter Book Title: ").strip()
                author = input("Enter Book Author: ").strip()
                if book_id and title and author:
                    add_book(book_id, title, author)
                else:
                    print("All fields (ID, Title, Author) are required.")

            case "5":
                check_overdue_books()

            case "6":
                generate_summary()

            case "7":
                save_records_to_file()
                print("Exiting system. Goodbye!")
                break

            case _:
                print("Invalid selection. Please enter a number from 1 to 7.")
