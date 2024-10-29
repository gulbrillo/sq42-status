pip install pystray pillow
pip install pypresence

python -m PyInstaller --onefile --windowed --icon=icon.ico --name=SQ42-Status status.py --add-data "icon.png;."