import json

with open('notebook.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
print(f"Code cells: {len(code_cells)}\n")

# Print first 10 code cells to understand the structure
for i, cell in enumerate(code_cells[:15]):
    print(f"\n{'='*60}\nCELL {i}\n{'='*60}")
    print("".join(cell.get('source', [])))
