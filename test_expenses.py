import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import Expenses as expenses


def write_expenses_csv(file_path, rows):
    pd.DataFrame(rows, columns=expenses.REQUIRED_COLUMNS).to_csv(file_path, index=False)


class TestExpenses(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = Path(self.temp_dir.name) / "expenses.csv"
        self.original_expenses_file = expenses.EXPENSES_FILE
        expenses.EXPENSES_FILE = self.csv_path

    def tearDown(self):
        expenses.EXPENSES_FILE = self.original_expenses_file
        self.temp_dir.cleanup()

    def test_prompt_with_cancel_returns_valid_text(self):
        with patch("builtins.input", side_effect=["hello"]):
            result = expenses.prompt_with_cancel("Prompt: ", validator=lambda value: len(value) > 0)
        self.assertEqual(result, "hello")

    def test_prompt_with_cancel_handles_cancel(self):
        with patch("builtins.input", side_effect=["cancel"]), io.StringIO() as output, redirect_stdout(output):
            result = expenses.prompt_with_cancel("Prompt: ")
            printed = output.getvalue()
        self.assertIsNone(result)
        self.assertIn(expenses.PRINT_MESSAGES["operation_cancelled"], printed)

    def test_prompt_yes_no_returns_yes(self):
        with patch("builtins.input", side_effect=["yes"]):
            self.assertEqual(expenses.prompt_yes_no("Continue? "), "yes")

    def test_prompt_yes_no_handles_cancel(self):
        with patch("builtins.input", side_effect=["cancel"]):
            self.assertIsNone(expenses.prompt_yes_no("Continue? "))

    def test_is_valid_date_true_and_false(self):
        self.assertTrue(expenses.is_valid_date("26/02/2026"))
        self.assertFalse(expenses.is_valid_date("2026-02-26"))

    def test_is_valid_amount_true_and_false(self):
        self.assertTrue(expenses.is_valid_amount("2.60"))
        self.assertFalse(expenses.is_valid_amount("-2.60"))
        self.assertFalse(expenses.is_valid_amount("abc"))

    def test_is_valid_description_true_and_false(self):
        self.assertTrue(expenses.is_valid_description("Coffee"))
        self.assertTrue(expenses.is_valid_description("Lunch meal"))
        self.assertFalse(expenses.is_valid_description("123"))
        self.assertFalse(expenses.is_valid_description("12.5"))

    def test_is_valid_category_true_and_false(self):
        self.assertTrue(expenses.is_valid_category("Food"))
        self.assertTrue(expenses.is_valid_category("Personal Care"))
        self.assertFalse(expenses.is_valid_category("123"))
        self.assertFalse(expenses.is_valid_category("12.5"))

    def test_prompt_non_empty_reprompts_empty(self):
        with patch("builtins.input", side_effect=["", "Groceries"]):
            self.assertEqual(expenses.prompt_non_empty("Description: "), "Groceries")

    def test_prompt_non_empty_handles_cancel(self):
        with patch("builtins.input", side_effect=["cancel"]):
            self.assertIsNone(expenses.prompt_non_empty("Description: "))

    def test_read_expenses_or_none_returns_dataframe_when_exists(self):
        write_expenses_csv(self.csv_path, [[1, "26/02/2026", "Coffee", 3.50, "Food"]])
        result = expenses.read_expenses_or_none()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)

    def test_read_expenses_or_none_creates_file_on_yes(self):
        with patch("builtins.input", side_effect=["yes"]):
            result = expenses.read_expenses_or_none()
        self.assertTrue(self.csv_path.exists())
        self.assertEqual(list(result.columns), expenses.REQUIRED_COLUMNS)

    def test_create_expenses_csv_creates_columns(self):
        expenses.create_expenses_csv()
        created_df = pd.read_csv(self.csv_path)
        self.assertEqual(list(created_df.columns), expenses.REQUIRED_COLUMNS)

    def test_has_required_columns_true_and_false(self):
        valid_df = pd.DataFrame(columns=expenses.REQUIRED_COLUMNS)
        invalid_df = pd.DataFrame(columns=["id", "date", "description", "amount"])
        self.assertTrue(expenses.has_required_columns(valid_df))
        self.assertFalse(expenses.has_required_columns(invalid_df))

    def test_has_correct_headers_true_and_false(self):
        valid_df = pd.DataFrame(columns=expenses.REQUIRED_COLUMNS)
        wrong_order_df = pd.DataFrame(columns=["date", "id", "description", "amount", "category"])
        self.assertTrue(expenses.has_correct_headers(valid_df))
        self.assertFalse(expenses.has_correct_headers(wrong_order_df))

    def test_fix_expenses_csv_headers_preserves_existing_data(self):
        pd.DataFrame(
            [[1, "26/02/2026", "Coffee", 3.50, "Food"]],
            columns=["col1", "col2", "col3", "col4", "col5"],
        ).to_csv(self.csv_path, index=False)
        expenses.fix_expenses_csv_headers()
        fixed_df = pd.read_csv(self.csv_path)
        self.assertEqual(list(fixed_df.columns), expenses.REQUIRED_COLUMNS)
        self.assertEqual(str(fixed_df.iloc[0]["description"]), "Coffee")

    def test_check_expenses_csv_prints_valid_message(self):
        write_expenses_csv(self.csv_path, [[1, "26/02/2026", "Coffee", 3.50, "Food"]])
        with io.StringIO() as output, redirect_stdout(output):
            expenses.check_expenses_csv()
            printed = output.getvalue()
        self.assertIn(expenses.PRINT_MESSAGES["valid_columns"], printed)

    def test_check_expenses_csv_handles_cancel_on_fix_prompt(self):
        pd.DataFrame(columns=["a", "b"]).to_csv(self.csv_path, index=False)
        with patch("builtins.input", side_effect=["cancel"]):
            expenses.check_expenses_csv()
        self.assertTrue(self.csv_path.exists())

    def test_check_expenses_csv_fixes_headers_on_yes(self):
        pd.DataFrame(
            [[1, "26/02/2026", "Coffee", 3.50, "Food"]],
            columns=["a", "b", "c", "d", "e"],
        ).to_csv(self.csv_path, index=False)
        with patch("builtins.input", side_effect=["yes"]):
            expenses.check_expenses_csv()
        fixed_df = pd.read_csv(self.csv_path)
        self.assertEqual(list(fixed_df.columns), expenses.REQUIRED_COLUMNS)
        self.assertEqual(str(fixed_df.iloc[0]["description"]), "Coffee")

    def test_checkFor_expenses_csv_creates_file_on_yes(self):
        with patch("builtins.input", side_effect=["yes"]):
            expenses.checkFor_expenses_csv()
        self.assertTrue(self.csv_path.exists())

    def test_checkFor_expenses_csv_handles_cancel(self):
        with patch("builtins.input", side_effect=["cancel"]):
            expenses.checkFor_expenses_csv()
        self.assertFalse(self.csv_path.exists())

    def test_build_table_lines_returns_table_lines(self):
        lines = expenses.build_table_lines(["A", "B"], [[1, 2], [10, 20]])
        self.assertIsInstance(lines, list)
        self.assertEqual(len(lines), 4)
        self.assertIn("A", lines[0])

    def test_print_table_outputs_lines(self):
        with io.StringIO() as output, redirect_stdout(output):
            expenses.print_table(["A", "B"], [[1, 2]])
            printed = output.getvalue()
        self.assertIn("A", printed)
        self.assertIn("1", printed)

    def test_display_expenses_prints_no_expenses_for_empty_file(self):
        write_expenses_csv(self.csv_path, [])
        with io.StringIO() as output, redirect_stdout(output):
            expenses.display_expenses()
            printed = output.getvalue()
        self.assertIn(expenses.PRINT_MESSAGES["no_expenses"], printed)

    def test_display_expenses_prints_formatted_table(self):
        write_expenses_csv(self.csv_path, [[1, "26/02/2026", "Coffee", 3.50, "Food"]])
        with io.StringIO() as output, redirect_stdout(output):
            expenses.display_expenses()
            printed = output.getvalue()
        self.assertIn("ID", printed)
        self.assertIn("Coffee", printed)

    def test_prompt_group_by_returns_valid_value(self):
        with patch("builtins.input", side_effect=["date"]):
            self.assertEqual(expenses.prompt_group_by(), "date")

    def test_prompt_group_by_handles_cancel(self):
        with patch("builtins.input", side_effect=["cancel"]):
            self.assertIsNone(expenses.prompt_group_by())

    def test_group_expenses_prints_grouped_totals(self):
        write_expenses_csv(
            self.csv_path,
            [[1, "26/02/2026", "Coffee", 3.50, "Food"], [2, "26/02/2026", "Lunch", 6.50, "Food"]],
        )
        with patch("builtins.input", side_effect=["category"]), io.StringIO() as output, redirect_stdout(output):
            expenses.group_expenses()
            printed = output.getvalue()
        self.assertIn("CATEGORY", printed)
        self.assertIn("10.00", printed)

    def test_group_expenses_handles_cancel(self):
        write_expenses_csv(self.csv_path, [[1, "26/02/2026", "Coffee", 3.50, "Food"]])
        with patch("builtins.input", side_effect=["cancel"]), io.StringIO() as output, redirect_stdout(output):
            expenses.group_expenses()
            printed = output.getvalue()
        self.assertIn(expenses.PRINT_MESSAGES["operation_cancelled"], printed)

    def test_prompt_new_expense_returns_complete_dict(self):
        with patch("builtins.input", side_effect=["26/02/2026", "Cookies", "2.60", "Food"]):
            result = expenses.prompt_new_expense(5)
        self.assertEqual(result["id"], 5)
        self.assertEqual(result["description"], "Cookies")

    def test_prompt_new_expense_reprompts_invalid_numeric_category(self):
        with patch("builtins.input", side_effect=["26/02/2026", "Cookies", "2.60", "123", "Food"]):
            result = expenses.prompt_new_expense(5)
        self.assertEqual(result["category"], "Food")

    def test_prompt_new_expense_reprompts_invalid_numeric_description(self):
        with patch("builtins.input", side_effect=["26/02/2026", "123", "Cookies", "2.60", "Food"]):
            result = expenses.prompt_new_expense(5)
        self.assertEqual(result["description"], "Cookies")

    def test_prompt_new_expense_handles_cancel(self):
        with patch("builtins.input", side_effect=["cancel"]):
            self.assertIsNone(expenses.prompt_new_expense(5))

    def test_add_expense_appends_row_with_new_id(self):
        write_expenses_csv(self.csv_path, [[1, "25/02/2026", "Coffee", 3.50, "Food"]])
        with patch("builtins.input", side_effect=["26/02/2026", "Cookies", "2.60", "Food"]):
            expenses.add_expense()
        updated_df = pd.read_csv(self.csv_path)
        self.assertEqual(len(updated_df), 2)
        self.assertEqual(int(updated_df.iloc[-1]["id"]), 2)

    def test_add_expense_handles_cancel_without_write(self):
        write_expenses_csv(self.csv_path, [[1, "25/02/2026", "Coffee", 3.50, "Food"]])
        with patch("builtins.input", side_effect=["cancel"]):
            expenses.add_expense()
        updated_df = pd.read_csv(self.csv_path)
        self.assertEqual(len(updated_df), 1)

    def test_save_expenses_writes_file_and_prints_message(self):
        write_expenses_csv(self.csv_path, [[1, "26/02/2026", "Coffee", 3.50, "Food"]])
        with io.StringIO() as output, redirect_stdout(output):
            expenses.save_expenses()
            printed = output.getvalue()
        self.assertIn(expenses.PRINT_MESSAGES["saved_expenses"], printed)

    def test_save_expenses_handles_missing_file(self):
        with patch("builtins.input", side_effect=["no"]), io.StringIO() as output, redirect_stdout(output):
            expenses.save_expenses()
            printed = output.getvalue()
        self.assertIn(expenses.PRINT_MESSAGES["file_not_found"], printed)

    def test_return_to_menu_choice_true_on_yes(self):
        with patch("builtins.input", side_effect=["yes"]):
            self.assertTrue(expenses.return_to_menu_choice())

    def test_return_to_menu_choice_false_on_cancel(self):
        with patch("builtins.input", side_effect=["cancel"]):
            self.assertFalse(expenses.return_to_menu_choice())

    def test_show_main_menu_prints_all_options(self):
        with io.StringIO() as output, redirect_stdout(output):
            expenses.show_main_menu()
            printed = output.getvalue()
        self.assertIn(expenses.PRINT_MESSAGES["menu_title"], printed)
        self.assertIn(expenses.PRINT_MESSAGES["menu_option_5"], printed)

    def test_handle_menu_choice_routes_valid_choice(self):
        called = {"add": False}
        with patch.object(expenses, "add_expense", lambda: called.__setitem__("add", True)):
            with patch.object(expenses, "return_to_menu_choice", lambda: True):
                result = expenses.handle_menu_choice("2")
        self.assertTrue(called["add"])
        self.assertTrue(result)

    def test_handle_menu_choice_returns_false_on_exit(self):
        with io.StringIO() as output, redirect_stdout(output):
            result = expenses.handle_menu_choice("5")
            printed = output.getvalue()
        self.assertFalse(result)
        self.assertIn(expenses.PRINT_MESSAGES["program_exiting"], printed)

    def test_main_menu_loops_until_handle_returns_false(self):
        calls = {"show": 0, "choices": []}

        def fake_show():
            calls["show"] += 1

        def fake_handle(choice):
            calls["choices"].append(choice)
            return choice != "5"

        with patch("builtins.input", side_effect=["1", "5"]):
            with patch.object(expenses, "show_main_menu", fake_show):
                with patch.object(expenses, "handle_menu_choice", fake_handle):
                    with patch.object(expenses, "checkFor_expenses_csv", lambda: None):
                        expenses.main_menu()

        self.assertEqual(calls["show"], 2)
        self.assertEqual(calls["choices"], ["1", "5"])


if __name__ == "__main__":
    unittest.main()
