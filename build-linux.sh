#!/bin/bash
pip install -U pyinstaller
pyinstaller --onefile --name tourist-filter ./filter-all-tourists.py 
cp -r ./assets/ ./dist/
mv ./dist ./tourist-filter-linux

tar -cvzf tourist-filter-linux.tgz tourist-filter-linux/
tar -cvzf stack1.tgz stack1/
tar -cvzf stack2.tgz stack2/