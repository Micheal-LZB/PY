import os, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
os.environ['PYTHONPATH'] = str(ROOT/'.packages') + os.pathsep + os.environ.get('PYTHONPATH','')
os.environ['MPLBACKEND'] = 'module://matplotlib_inline.backend_inline'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
from traitlets.config import Config
nb = nbformat.read('generative-baselines.ipynb', as_version=4)
# Execute using the same IPython cell machinery without starting a separate
# network-bound Jupyter kernel (unavailable in this desktop environment).
cfg = Config()
cfg.HistoryManager.hist_file = ':memory:'
shell = InteractiveShell.instance(config=cfg)
shell.enable_gui = lambda gui: None
shell.run_line_magic('matplotlib', 'inline')
count = 0
try:
    for index, cell in enumerate(nb.cells):
        if cell.cell_type != 'code': continue
        count += 1
        print(f'Executing cell {index+1}/{len(nb.cells)} at {time.strftime("%H:%M:%S")}', flush=True)
        with capture_output() as captured:
            result = shell.run_cell(cell.source, store_history=True)
        outputs=[]
        if captured.stdout:
            outputs.append(nbformat.v4.new_output('stream', name='stdout', text=captured.stdout))
        if captured.stderr:
            outputs.append(nbformat.v4.new_output('stream', name='stderr', text=captured.stderr))
        for rich in captured.outputs:
            outputs.append(nbformat.v4.new_output('display_data', data=rich.data, metadata=rich.metadata))
        cell.outputs, cell.execution_count = outputs, count
        nbformat.write(nb, 'generative-baselines.ipynb')
        if not result.success:
            raise RuntimeError(captured.stdout + captured.stderr + str(result.error_in_exec))
finally:
    nbformat.write(nb, 'generative-baselines.ipynb')
print('All cells executed successfully.', flush=True)
