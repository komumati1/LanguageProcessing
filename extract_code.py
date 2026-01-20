import json

notebook_path = 'd:/mateusz/studia/5_semestr/jezyk_naturalny/LanguageProcessing/notebook.ipynb'

try:
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code':
            print(f"--- Cell {i} ---")
            print("".join(cell['source']))
            print("\n")
except Exception as e:
    print(f"Error reading notebook: {e}")
