"""Test script to validate CSV model functionality"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import from the dedicated model module (no GUI dependency)
from csv_model import CSVDataModel

def test_csv_model():
    """Test the CSV data model"""
    print("Testing CSV Data Model...")

    # Create model
    model = CSVDataModel()
    print("[PASS] Model created")

    # Create new CSV
    model.new_csv(5, 3)
    assert model.row_count == 5, "Row count should be 5"
    assert model.column_count == 3, "Column count should be 3"
    print("[PASS] New CSV created (5 rows, 3 columns)")

    # Test cell operations
    model.set_value(0, 0, "Test")
    assert model.get_value(0, 0) == "Test", "Cell value should be 'Test'"
    print("[PASS] Cell editing works")

    # Test row operations
    initial_rows = model.row_count
    model.add_row()
    assert model.row_count == initial_rows + 1, "Row should be added"
    print("[PASS] Add row works")

    model.delete_row(0)
    assert model.row_count == initial_rows, "Row should be deleted"
    print("[PASS] Delete row works")

    # Test column operations
    initial_cols = model.column_count
    model.add_column(name="New Column")
    assert model.column_count == initial_cols + 1, "Column should be added"
    print("[PASS] Add column works")

    model.delete_column(0)
    assert model.column_count == initial_cols, "Column should be deleted"
    print("[PASS] Delete column works")

    # Test undo/redo
    model.set_value(0, 0, "Before")
    model.set_value(0, 0, "After")
    assert model.get_value(0, 0) == "After"
    model.undo()
    assert model.get_value(0, 0) == "Before", "Undo should work"
    print("[PASS] Undo works")

    model.redo()
    assert model.get_value(0, 0) == "After", "Redo should work"
    print("[PASS] Redo works")

    # Test CSV save/load
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_file = f.name

    model.new_csv(3, 3)
    model.set_value(0, 0, "A")
    model.set_value(1, 1, "B")
    model.set_value(2, 2, "C")

    model.save_csv(temp_file)
    print("[PASS] CSV save works")

    model2 = CSVDataModel()
    model2.load_csv(temp_file)
    assert model2.get_value(0, 0) == "A", "Loaded value should match"
    assert model2.get_value(1, 1) == "B", "Loaded value should match"
    assert model2.get_value(2, 2) == "C", "Loaded value should match"
    print("[PASS] CSV load works")

    # Clean up
    os.unlink(temp_file)

    print("\n*** ALL TESTS PASSED! ***")
    return True

if __name__ == "__main__":
    try:
        test_csv_model()
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
