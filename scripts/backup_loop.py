import subprocess
import sys
import time
from pathlib import Path
script = Path(__file__).with_name('backup.py')
while True:
    result = subprocess.run([sys.executable, str(script)])
    time.sleep(86400 if result.returncode == 0 else 3600)
