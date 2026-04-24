from src.data_manager import DataManager
import os

if __name__ == "__main__":
    dm = DataManager()
    levels = dm.load_custom_levels()
    print(f"Loaded {len(levels)} levels from JSON")
    dm.sync_to_python_config(levels)
    print("levels_config.py updated.")
