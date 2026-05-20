from markitdown import MarkItDown
import sys

try:
    m = MarkItDown()
    result = m.convert(sys.argv[1])
    print('Convert OK')
    print('First 500 chars:', result[:500])
except Exception as e:
    print(f'Error: {e}')
