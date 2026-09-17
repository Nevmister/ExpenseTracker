import pandas as pd
from pathlib import Path
from datetime import datetime

# Resolve the CSV path relative to this script so file operations are location-safe.
EXPENSES_FILE = Path(__file__).resolve().parent / 'expenses.csv'
# Special user value used to cancel interactive prompts.
CANCEL_VALUE = 'cancel'
# Canonical schema for all expense records.
REQUIRED_COLUMNS = ['id', 'date', 'description', 'amount', 'category']

# Centralized output text used across the application.
PRINT_MESSAGES = {
    'created_csv': "expenses.csv has been created with the specified columns.",
    'valid_columns': "expenses.csv already exists and contains the correct columns.",
    'headers_fixed': "expenses.csv headers were fixed while preserving existing data.",
    'no_changes': "Exiting without making changes to expenses.csv.",
    'file_not_found': "expenses.csv not found.",
    'file_not_created': "expenses.csv was not created.",
    'no_expenses': "No expenses to display.",
    'invalid_group_input': "Invalid input. Please enter 'date' or 'category'.",
    'expense_added': "Expense added with ID {new_id}.",
    'menu_title': "\nMain Menu:",
    'menu_option_1': "1. Display Expenses",
    'menu_option_2': "2. Add Expense",
    'menu_option_3': "3. Group Expenses",
    'menu_option_4': "4. Save Expenses",
    'menu_option_5': "5. Exit",
    'saved_expenses': "Expenses have been saved.",
    'program_exiting': "Exiting program.",
    'invalid_menu_option': "Invalid option. Please enter a number between 1 and 5.",
    'return_to_menu_prompt': "Return to main menu? (yes/no): ",
    'cancel_hint': "Type 'cancel' to return.",
    'operation_cancelled': "Operation cancelled.",
    'invalid_yes_no': "Invalid input. Please enter 'yes' or 'no'.",
    'invalid_date': "Invalid date. Please enter in dd/mm/yyyy format.",
    'invalid_amount': "Invalid amount. Please enter a valid number.",
    'invalid_description': "Invalid description. Please enter a text description (not a number).",
    'invalid_category': "Invalid category. Please enter a text category (not a number).",
    'invalid_empty': "Input cannot be empty. Please try again.",
}


def prompt_with_cancel(prompt_text, validator=None, invalid_message=None):
    """
    Description:
    Prompt the user for input and keep asking until the value is valid or cancelled.
    Parameters:
    - prompt_text: Text shown to the user for input.
    - validator: Optional validation function that returns True for valid input.
    - invalid_message: Optional message displayed when validation fails.
    Returns:
    - A validated string input, or None when the user types cancel.
    Tests:
    - check function returns the entered text when it passes validation.
    - check the cancellation by user is handled and returns None.
    """
    # Keep asking until the user provides valid input or cancels.
    while True:
        user_input = input(prompt_text).strip()
        # Treat the cancellation keyword as an immediate stop signal.
        if user_input.lower() == CANCEL_VALUE:
            print(PRINT_MESSAGES['operation_cancelled'])
            return None
        # Return early when there is no validator or validation passes.
        if validator is None or validator(user_input):
            return user_input
        # Print a validation message when provided.
        if invalid_message:
            print(invalid_message)


def prompt_yes_no(prompt_text):
    """
    Description:
    Prompt the user for a yes or no response with cancellation support.
    Parameters:
    - prompt_text: Text shown to the user when asking for yes/no.
    Returns:
    - The string 'yes' or 'no', or None when the user types cancel.
    Tests:
    - check function returns 'yes' for valid yes input.
    - check the cancellation by user is handled and returns None.
    """
    # Loop until a valid yes/no response (or cancel) is entered.
    while True:
        user_input = input(prompt_text).strip().lower()
        # Support cancellation from yes/no prompts.
        if user_input == CANCEL_VALUE:
            print(PRINT_MESSAGES['operation_cancelled'])
            return None
        # Accept only explicit yes or no values.
        if user_input in ['yes', 'no']:
            return user_input
        # Show feedback for invalid yes/no responses.
        print(PRINT_MESSAGES['invalid_yes_no'])


def is_valid_date(value):
    """
    Description:
    Validate that a string is a date in dd/mm/yyyy format.
    Parameters:
    - value: Input text expected to represent a date.
    Returns:
    - True when the date format is valid, otherwise False.
    Tests:
    - check function returns True for a valid date like 26/02/2026.
    - check function returns False for invalid text or wrong date format.
    """
    # Parse the string using the expected day/month/year format.
    try:
        datetime.strptime(value, "%d/%m/%Y")
        return True
    # Any parse failure means the date format/value is invalid.
    except ValueError:
        return False


def is_valid_amount(value):
    """
    Description:
    Validate that a string can be converted into a non-negative numeric amount.
    Parameters:
    - value: Input text expected to represent a number.
    Returns:
    - True when conversion to float is possible and the value is non-negative, otherwise False.
    Tests:
    - check function returns True for values like 2.60 and 10.
    - check function returns False for negative values like -1.25.
    - check function returns False for non-numeric values like 'abc'.
    """
    # Check numeric convertibility and reject negative values.
    try:
        return float(value) >= 0
    # Non-numeric input is rejected.
    except ValueError:
        return False


def is_valid_description(value):
    """
    Description:
    Validate that description input is textual and not numeric-only.
    Parameters:
    - value: Input text expected to represent an expense description.
    Returns:
    - True when the input contains at least one alphabetic character, otherwise False.
    Tests:
    - check function returns True for values like 'Coffee' and 'Lunch meal'.
    - check function returns False for numeric-only values like '123' or '12.5'.
    """
    # Description should contain at least one letter.
    return any(character.isalpha() for character in value)


def is_valid_category(value):
    """
    Description:
    Validate that category input is textual and not numeric-only.
    Parameters:
    - value: Input text expected to represent a category name.
    Returns:
    - True when the input contains at least one alphabetic character, otherwise False.
    Tests:
    - check function returns True for values like 'Food' and 'Personal Care'.
    - check function returns False for numeric-only values like '123' or '12.5'.
    """
    # Category should contain at least one letter.
    return any(character.isalpha() for character in value)


def prompt_non_empty(prompt_text):
    """
    Description:
    Prompt for input and reject empty values while allowing cancellation.
    Parameters:
    - prompt_text: Text shown to the user for input.
    Returns:
    - A non-empty string, or None when the user types cancel.
    Tests:
    - check function keeps prompting when an empty value is entered.
    - check the cancellation by user is handled and returns None.
    """
    # Reuse the generic prompt handler with a non-empty validation rule.
    return prompt_with_cancel(prompt_text, lambda value: len(value) > 0, PRINT_MESSAGES['invalid_empty'])


def read_expenses_or_none():
    """
    Description:
    Read the expenses CSV file and ask permission to create it when missing.
    Parameters:
    - None.
    Returns:
    - A pandas DataFrame when the file exists or is created, otherwise None.
    Tests:
    - check function returns a DataFrame when expenses.csv exists.
    - check function asks permission and creates expenses.csv when user selects yes.
    """
    # Primary read path when the CSV exists.
    try:
        return pd.read_csv(EXPENSES_FILE)
    # Missing file path: ask the user if a new CSV should be created.
    except FileNotFoundError:
        print(PRINT_MESSAGES['file_not_found'])
        print(PRINT_MESSAGES['cancel_hint'])
        user_input = prompt_yes_no("Do you want to create expenses.csv? (yes/no): ")
        # Create and immediately read the file when the user agrees.
        if user_input == 'yes':
            create_expenses_csv()
            return pd.read_csv(EXPENSES_FILE)
        # Report when user explicitly declines file creation.
        if user_input == 'no':
            print(PRINT_MESSAGES['file_not_created'])
        # Return None for cancel/no so callers can safely short-circuit.
        return None


def create_expenses_csv():
    """
    Description:
    Create a new expenses CSV file with the required column structure.
    Parameters:
    - None.
    Returns:
    - None.
    Tests:
    - check function creates expenses.csv with required columns.
    - check function prints the created file confirmation message.
    """
    # Create an empty DataFrame with the required schema and write it to disk.
    pd.DataFrame(columns=REQUIRED_COLUMNS).to_csv(EXPENSES_FILE, index=False)
    print(PRINT_MESSAGES['created_csv'])


def has_required_columns(expenses_df):
    """
    Description:
    Verify that an expenses DataFrame includes all required column names.
    Parameters:
    - expenses_df: DataFrame to validate for required schema.
    Returns:
    - True when all required columns exist, otherwise False.
    Tests:
    - check function returns True for a DataFrame with all required columns.
    - check function returns False when one or more required columns are missing.
    """
    # Ensure every required schema field exists in the DataFrame.
    return all(column in expenses_df.columns for column in REQUIRED_COLUMNS)


def has_correct_headers(expenses_df):
    """
    Description:
    Validate whether the first expected headers are in the correct order.
    Parameters:
    - expenses_df: DataFrame to validate for canonical header order.
    Returns:
    - True when the leading headers match the required schema, otherwise False.
    Tests:
    - check function returns True when the first headers are id/date/description/amount/category.
    - check function returns False when headers are missing or out of order.
    """
    # Only valid when there are enough columns to compare against the required schema.
    if len(expenses_df.columns) < len(REQUIRED_COLUMNS):
        return False
    # Compare the first expected headers in order.
    return list(expenses_df.columns[:len(REQUIRED_COLUMNS)]) == REQUIRED_COLUMNS


def fix_expenses_csv_headers():
    """
    Description:
    Fix expenses.csv headers to the canonical schema while preserving all row data.
    Parameters:
    - None.
    Returns:
    - None.
    Tests:
    - check function renames first headers to required names and keeps row data unchanged.
    - check function preserves any extra columns by renaming them to extra_column_n.
    """
    # Load current CSV content so only header names are adjusted.
    expenses_df = pd.read_csv(EXPENSES_FILE)
    # Add placeholder columns if the file has fewer than required columns.
    while len(expenses_df.columns) < len(REQUIRED_COLUMNS):
        expenses_df[f"missing_column_{len(expenses_df.columns) + 1}"] = pd.NA
    # Rename headers: required schema first, then stable names for extras.
    extra_count = len(expenses_df.columns) - len(REQUIRED_COLUMNS)
    extra_headers = [f"extra_column_{index}" for index in range(1, extra_count + 1)]
    expenses_df.columns = REQUIRED_COLUMNS + extra_headers
    # Persist repaired headers while keeping all existing row values.
    expenses_df.to_csv(EXPENSES_FILE, index=False)
    print(PRINT_MESSAGES['headers_fixed'])


def check_expenses_csv():
    """
    Description:
    Check whether expenses.csv has correct headers and offer in-place header repair when invalid.
    Parameters:
    - None.
    Returns:
    - None.
    Tests:
    - check function prints valid-columns message when headers are correct.
    - check function repairs headers in place when user selects yes.
    - check the cancellation by user is handled during fix prompt.
    """
    # Read the existing CSV before validating its schema.
    expenses_df = pd.read_csv(EXPENSES_FILE)
    # Exit early when header order and names already match expected schema.
    if has_correct_headers(expenses_df):
        print(PRINT_MESSAGES['valid_columns'])
        return
    # Prompt user to fix headers without replacing existing row data.
    print(PRINT_MESSAGES['cancel_hint'])
    user_input = prompt_yes_no("expenses.csv headers are not correct. Do you want to fix headers while keeping existing data? (yes/no): ")
    # Fix headers in place when user approves.
    if user_input == 'yes':
        fix_expenses_csv_headers()
    # Preserve current file if user declines overwrite.
    elif user_input == 'no':
        print(PRINT_MESSAGES['no_changes'])


def checkFor_expenses_csv():
    """
    Description:
    Ensure expenses.csv exists, and prompt user to create it when it does not.
    Parameters:
    - None.
    Returns:
    - None.
    Tests:
    - check function creates file when user enters yes.
    - check the cancellation by user is handled during create prompt.
    """
    # Attempt to read the CSV and validate schema if it exists.
    try:
        pd.read_csv(EXPENSES_FILE)
        check_expenses_csv()
    # Handle missing CSV by offering to create a new one.
    except FileNotFoundError:
        print(PRINT_MESSAGES['file_not_found'])
        print(PRINT_MESSAGES['cancel_hint'])
        user_input = prompt_yes_no("Do you want to create expenses.csv? (yes/no): ")
        # Create the file when user confirms.
        if user_input == 'yes':
            create_expenses_csv()
        # Inform user when creation is declined.
        elif user_input == 'no':
            print(PRINT_MESSAGES['file_not_created'])


def build_table_lines(column_headers, rows):
    """
    Description:
    Build aligned text lines for a table display from headers and data rows.
    Parameters:
    - column_headers: List of header labels for the table.
    - rows: List of row values to print in columns.
    Returns:
    - A list of strings containing header, divider, and row lines.
    Tests:
    - check function returns a list of aligned table lines.
    - check function output includes header and divider rows.
    """
    # Start width calculation using header lengths.
    widths = [len(header) for header in column_headers]
    # Expand each column width to fit the longest row value.
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(str(value)))
    # Build header and divider lines based on computed widths.
    header_line = " | ".join(column_headers[index].ljust(widths[index]) for index in range(len(column_headers)))
    divider_line = "-+-".join("-" * widths[index] for index in range(len(widths)))
    # Build each data line with left-justified aligned columns.
    data_lines = [" | ".join(str(row[index]).ljust(widths[index]) for index in range(len(row))) for row in rows]
    # Return all render-ready lines in display order.
    return [header_line, divider_line] + data_lines


def print_table(column_headers, rows):
    """
    Description:
    Print a formatted aligned table built from headers and row values.
    Parameters:
    - column_headers: List of column names to display.
    - rows: List of row values to print.
    Returns:
    - None.
    Tests:
    - check function prints each line returned by build_table_lines.
    - check function handles multiple rows without alignment issues.
    """
    # Print each generated table line in sequence.
    for line in build_table_lines(column_headers, rows):
        print(line)


def display_expenses():
    """
    Description:
    Load expenses from CSV and display them in an aligned table format.
    Parameters:
    - None.
    Returns:
    - None.
    Tests:
    - check function prints no-expenses message when file has no rows.
    - check function prints a formatted table when data exists.
    """
    # Attempt to load CSV data; stop if unavailable.
    expenses_df = read_expenses_or_none()
    if expenses_df is None:
        return
    # Handle valid but empty datasets with a friendly message.
    if expenses_df.empty:
        print(PRINT_MESSAGES['no_expenses'])
        return
    # Keep only relevant columns and normalize amount formatting.
    display_df = expenses_df[REQUIRED_COLUMNS].copy()
    display_df['amount'] = pd.to_numeric(display_df['amount'], errors='coerce').fillna(0).map(lambda value: f"{value:.2f}")
    # Render the formatted table to the console.
    print_table(['ID', 'DATE', 'DESCRIPTION', 'AMOUNT', 'CATEGORY'], display_df.astype(str).values.tolist())


def prompt_group_by():
    """
    Description:
    Prompt the user to choose grouping by date or category with cancel support.
    Parameters:
    - None.
    Returns:
    - The selected grouping value in lowercase, or None if cancelled.
    Tests:
    - check function returns 'date' or 'category' for valid user input.
    - check the cancellation by user is handled and returns None.
    """
    # Show cancel guidance before interactive grouping prompt.
    print(PRINT_MESSAGES['cancel_hint'])
    # Accept only date/category input values.
    group_by = prompt_with_cancel(
        "Do you want to group expenses by 'date' or 'category'? (date/category): ",
        validator=lambda value: value.lower() in ['date', 'category'],
        invalid_message=PRINT_MESSAGES['invalid_group_input']
    )
    # Normalize selected group key to lowercase.
    return None if group_by is None else group_by.lower()


def group_expenses():
    """
    Description:
    Group expenses by date or category and print total amounts per group.
    Parameters:
    - None.
    Returns:
    - None.
    Tests:
    - check function prints grouped totals when valid grouping is selected.
    - check the cancellation by user is handled during group selection.
    """
    # Load source data before grouping.
    expenses_df = read_expenses_or_none()
    if expenses_df is None:
        return
    # Nothing to group when file has no rows.
    if expenses_df.empty:
        print(PRINT_MESSAGES['no_expenses'])
        return
    # Ask user for grouping criterion.
    group_by = prompt_group_by()
    if group_by is None:
        return
    # Aggregate totals for the selected group field.
    grouped_expenses = expenses_df.groupby(group_by)['amount'].sum().reset_index()
    grouped_expenses['amount'] = pd.to_numeric(grouped_expenses['amount'], errors='coerce').fillna(0).map(lambda value: f"{value:.2f}")
    # Display grouped totals in table form.
    print_table([group_by.upper(), 'TOTAL AMOUNT'], grouped_expenses.astype(str).values.tolist())


def prompt_new_expense(new_id):
    """
    Description:
    Prompt the user for all new expense fields and build an expense record.
    Parameters:
    - new_id: Numeric ID to assign to the new expense entry.
    Returns:
    - A dictionary containing expense fields, or None if cancelled.
    Tests:
    - check function returns a complete expense dictionary for valid input.
    - check the cancellation by user is handled for any prompted field.
    """
    # Show cancellation hint once before collecting all fields.
    print(PRINT_MESSAGES['cancel_hint'])
    # Collect and validate date first.
    date = prompt_with_cancel("Enter the date of the expense (dd/mm/yyyy): ", is_valid_date, PRINT_MESSAGES['invalid_date'])
    if date is None:
        return None
    # Collect description text and reject numeric-only descriptions.
    description = prompt_with_cancel(
        "Enter a description for the expense: ",
        is_valid_description,
        PRINT_MESSAGES['invalid_description']
    )
    if description is None:
        return None
    # Collect numeric amount.
    amount = prompt_with_cancel("Enter the amount of the expense: ", is_valid_amount, PRINT_MESSAGES['invalid_amount'])
    if amount is None:
        return None
    # Collect category text and reject numeric-only categories.
    category = prompt_with_cancel(
        "Enter the category of the expense: ",
        is_valid_category,
        PRINT_MESSAGES['invalid_category']
    )
    if category is None:
        return None
    # Return a complete expense record dictionary.
    return {'id': new_id, 'date': date, 'description': description, 'amount': amount, 'category': category}


def add_expense():
    """
    Description:
    Add one validated expense entry to the expenses CSV file.
    Parameters:
    - None.
    Returns:
    - None.
    Tests:
    - check function appends one row with a new ID when input is valid.
    - check the cancellation by user is handled without writing a new row.
    """
    # Load current data before appending a new expense.
    expenses_df = read_expenses_or_none()
    if expenses_df is None:
        return
    # Compute next ID from existing numeric IDs (or start at 1).
    new_id = int(pd.to_numeric(expenses_df['id'], errors='coerce').max()) + 1 if not expenses_df.empty else 1
    # Prompt user for a validated expense payload.
    new_expense = prompt_new_expense(new_id)
    if new_expense is None:
        return
    # Append new row and persist to CSV.
    updated_df = pd.concat([expenses_df, pd.DataFrame([new_expense])], ignore_index=True)
    updated_df.to_csv(EXPENSES_FILE, index=False)
    print(PRINT_MESSAGES['expense_added'].format(new_id=new_id))


def save_expenses():
    """
    Description:
    Save the current expenses DataFrame back to the CSV file.
    Parameters:
    - None.
    Returns:
    - None.
    Tests:
    - check function writes expenses.csv and prints saved confirmation.
    - check function handles missing file by printing file-not-found message.
    """
    # Reload data to ensure file exists and data is current.
    expenses_df = read_expenses_or_none()
    if expenses_df is None:
        return
    # Persist DataFrame to CSV and confirm save.
    expenses_df.to_csv(EXPENSES_FILE, index=False)
    print(PRINT_MESSAGES['saved_expenses'])


def return_to_menu_choice():
    """
    Description:
    Ask whether the user wants to return to the main menu.
    Parameters:
    - None.
    Returns:
    - True when user selects yes, otherwise False.
    Tests:
    - check function returns True when user inputs yes.
    - check the cancellation by user is handled and returns False.
    """
    # Convert yes/no prompt result into a boolean continuation flag.
    return prompt_yes_no(PRINT_MESSAGES['return_to_menu_prompt']) == 'yes'


def show_main_menu():
    """
    Description:
    Print the main menu title and all available menu options.
    Parameters:
    - None.
    Returns:
    - None.
    Tests:
    - check function prints all menu option lines in order.
    - check function output includes title and exit option.
    """
    # Print menu title and available numbered options.
    print(PRINT_MESSAGES['menu_title'])
    print(PRINT_MESSAGES['menu_option_1'])
    print(PRINT_MESSAGES['menu_option_2'])
    print(PRINT_MESSAGES['menu_option_3'])
    print(PRINT_MESSAGES['menu_option_4'])
    print(PRINT_MESSAGES['menu_option_5'])


def handle_menu_choice(choice):
    """
    Description:
    Execute the selected menu action and return whether the app should continue.
    Parameters:
    - choice: Menu option entered by the user.
    Returns:
    - True to continue showing the menu, False to exit.
    Tests:
    - check function routes valid choices to the correct action.
    - check function returns False when user chooses the exit option.
    """
    # Route each menu choice to its corresponding feature.
    if choice == '1':
        display_expenses()
    elif choice == '2':
        add_expense()
    elif choice == '3':
        group_expenses()
    elif choice == '4':
        save_expenses()
    elif choice == '5':
        # Exit immediately when user selects option 5.
        print(PRINT_MESSAGES['program_exiting'])
        return False
    else:
        # Keep running when invalid option is entered.
        print(PRINT_MESSAGES['invalid_menu_option'])
        return True
    # Ask whether to return to menu after completing an action.
    if not return_to_menu_choice():
        print(PRINT_MESSAGES['program_exiting'])
        return False
    # Continue showing the menu when user chooses to return.
    return True


def main_menu():
    """
    Description:
    Run the interactive menu loop until a stop condition is returned.
    Parameters:
    - None.
    Returns:
    - None.
    Tests:
    - check function repeatedly shows menu until exit is selected.
    - check invalid menu input is handled and loop continues.
    """
    # Ensure CSV exists and headers are validated before showing the menu.
    checkFor_expenses_csv()
    # Main application loop; stops only when a handler returns False.
    while True:
        show_main_menu()
        # Normalize menu input for consistent branching.
        choice = input("Please select an option (1-5): ").strip().lower()
        if not handle_menu_choice(choice):
            break


if __name__ == "__main__":
    main_menu()