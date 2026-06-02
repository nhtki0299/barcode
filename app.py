# File này được giữ lại để tương thích với cấu hình Run cũ của IDE.
# Nó sẽ tự động gọi file main.py mới.

import runpy

if __name__ == "__main__":
    runpy.run_module('main', run_name='__main__')
