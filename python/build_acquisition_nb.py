from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
cells=[{'cell_type':'markdown','metadata':{},'source':"""# Data acquisition

The primary submitted CSV has 720 rows and no timestamps. This notebook imports it without
inventing a sampling interval. To collect a new timestamped recording, close Serial Monitor,
then run from the repository root: python python/capture_serial.py --port COM6 --rows 600.
Replace COM6 with the connected serial port. Press reset after capture begins to emit the header.
The command records host_elapsed_s and retains the device counter separately.
Host receipt time includes serial and host scheduling delays, so it is not a sensor hardware timestamp.
The new capture command is provided for future recordings and was not run against a connected board here.
"""},{'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],
'source':"""from pathlib import Path
import pandas as pd
root=Path.cwd() if (Path.cwd()/'data/raw').exists() else Path.cwd().parent
data=pd.read_csv(root/'data/raw/sensor_data_light_regimes_720rows.csv')
print('Loaded',len(data),'supplied records. No timestamps are present.')
print(data.head().to_string(index=False))
"""}]
for i,c in enumerate(cells):c['id']=f'acquisition-{i}'
n={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}},'cells':cells}
(HERE/'acquisition.ipynb').write_text(json.dumps(n,indent=1))
