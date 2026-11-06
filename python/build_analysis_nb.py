from pathlib import Path
import json
from run_notebook import execute_notebook
HERE=Path(__file__).resolve().parent
notebook=json.loads((HERE/'analysis_template.json').read_text())
execute_notebook(notebook,HERE)
(HERE/'analysis.ipynb').write_text(json.dumps(notebook,indent=1))
print('Updated analysis.ipynb and primary Arduino results.')
