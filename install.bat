REM try if pip in PATH
pip install . 2> nul || py -m pip install . 2> nul || python -m pip install . 2> nul || python3 -m pip install . 2> nul
