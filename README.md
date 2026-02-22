# Quant Trading Strategies

A quantitative trading project with Python and C++ modules.

## 📁 Project Structure

```
Quant Trading Strategies/
├── cpp/                    # C++ source files (pybind11 modules)
│   └── moving_average.cpp
├── python/                 # Python scripts
│   ├── get_yfinance_data.py
│   └── rolling_average.py
├── lib/                    # Compiled C++ modules (.so files)
│   └── moving_average.so
├── data/                   # Data files (CSV, Parquet, etc.)
│   ├── AAPL_5m.csv
│   └── AAPL_5m.parquet
├── .venv/                  # Python virtual environment
├── build.sh                # Build script for C++ modules
└── run.sh                  # Run script for Python files
```

## 🚀 Quick Start

### 1. Activate Virtual Environment

```bash
source .venv/bin/activate
```

### 2. Build C++ Modules

```bash
./build.sh
```

This will compile all `.cpp` files in the `cpp/` folder and output `.so` files to `lib/`.

### 3. Run Python Scripts

```bash
./run.sh get_yfinance_data.py
```

Or run directly:

```bash
python3 python/get_yfinance_data.py
```

## 🔨 Building C++ Modules

The `build.sh` script automatically:
- Finds all `.cpp` files in `cpp/` folder
- Compiles them with pybind11
- Outputs `.so` files to `lib/` folder
- Shows build summary

**To add a new C++ module:**
1. Create a new `.cpp` file in `cpp/` folder
2. Run `./build.sh`
3. Import in Python: `import your_module_name`

## 🐍 Using C++ Modules in Python

```python
import sys
import os

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

# Import your C++ module
import moving_average

# Use it
result = moving_average.add(5, 3)
print(result)  # 8
```

## 📦 Dependencies

Install dependencies in the virtual environment:

```bash
source .venv/bin/activate
pip install yfinance mplfinance pyarrow pybind11
```

## 📝 Notes

- All Python scripts should be placed in `python/` folder
- All C++ source files should be placed in `cpp/` folder
- Compiled modules are automatically placed in `lib/` folder
- Data files are saved to `data/` folder
- Use `./run.sh <script.py>` to run Python scripts from project root
- Use `./build.sh` to rebuild all C++ modules

