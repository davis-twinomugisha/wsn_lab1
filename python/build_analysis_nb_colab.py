from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
n=json.loads((HERE/'analysis_template.json').read_text())
cell=next(c for c in n['cells'] if c['cell_type']=='code')
cell['source']="""from pathlib import Path
from google.colab import files
uploaded=files.upload()
name='sensor_data_light_regimes_720rows.csv'
if name not in uploaded:raise ValueError('Upload the original '+name)
root=Path('/content/wsn_lab1')
(root/'data/raw').mkdir(parents=True,exist_ok=True)
(root/'data/processed').mkdir(exist_ok=True)
(root/'figures').mkdir(exist_ok=True)
(root/'data/raw'/name).write_bytes(uploaded[name])
import os
os.chdir(root)
"""+cell['source']
for c in n['cells']:
 if c['cell_type']=='code':c['outputs']=[];c['execution_count']=None
(HERE/'analysis_colab.ipynb').write_text(json.dumps(n,indent=1))
print('Updated Colab notebook.')
