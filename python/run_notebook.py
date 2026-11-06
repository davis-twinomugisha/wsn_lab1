from pathlib import Path
import base64,contextlib,io,json,os
import matplotlib
matplotlib.use('Agg')

def execute_notebook(notebook, cwd):
    cwd=Path(cwd).resolve()
    old=Path.cwd()
    ns={}
    count=0
    os.chdir(cwd)
    try:
        for index,cell in enumerate(notebook['cells']):
            cell.setdefault('id', f'cell-{index:02}')
            if cell['cell_type']!='code':continue
            count+=1
            stream=io.StringIO()
            source=''.join(cell['source']) if isinstance(cell['source'],list) else cell['source']
            with contextlib.redirect_stdout(stream):
                exec(compile(source,f'notebook-cell-{index}','exec'),ns)
            cell['execution_count']=count
            cell['outputs']=[]
            if stream.getvalue():cell['outputs'].append({'output_type':'stream','name':'stdout','text':stream.getvalue()})
            for name in cell.get('metadata',{}).get('figure_outputs',[]):
                p=cwd.parent/'figures'/name
                cell['outputs'].append({'output_type':'display_data','metadata':{},'data':{
                    'image/png':base64.b64encode(p.read_bytes()).decode(),'text/plain':f'Figure: {name}'}})
    finally:os.chdir(old)
    return notebook
