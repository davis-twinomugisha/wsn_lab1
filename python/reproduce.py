from pathlib import Path
import json,runpy,os,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
old=Path.cwd()
os.chdir(HERE)
try:
 runpy.run_path(str(HERE/'build_analysis_nb.py'),run_name='__main__')
 runpy.run_path(str(HERE/'build_analysis_nb_colab.py'),run_name='__main__')
 runpy.run_path(str(HERE/'build_calibration_nb.py'),run_name='__main__')
 from run_notebook import execute_notebook
 n=json.loads((HERE/'calibration.ipynb').read_text())
 n['cells'][-1].setdefault('metadata',{})['figure_outputs']=['calibration_fit.png']
 execute_notebook(n,HERE)
 (HERE/'calibration.ipynb').write_text(json.dumps(n,indent=1))
finally:os.chdir(old)
print('Reproduced primary analysis, five plots, calibration fit and notebooks.')
