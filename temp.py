import sys
from pathlib import Path

arg = sys.argv[1]
fullPath = Path(arg)
fileName = fullPath.stem
fileWithExt = fullPath.name
path = fullPath.parent

print(fullPath, fileName, fileWithExt, path)