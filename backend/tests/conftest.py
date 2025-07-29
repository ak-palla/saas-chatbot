# Test configuration for Phase 1 tests
# This file ensures the tests directory is treated as a Python package

import sys
import os

# Add the parent directory to the Python path so tests can import app modules
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Change working directory to backend for relative imports
os.chdir(backend_dir)