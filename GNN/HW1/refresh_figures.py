"""Re-render equal-aspect moon figures and update the measured discussion."""
from pathlib import Path
import os, sys
ROOT=Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0,str(ROOT/'.packages'))
os.environ['MPLBACKEND']='module://matplotlib_inline.backend_inline'
os.environ['OMP_NUM_THREADS']='1'
os.environ['OPENBLAS_NUM_THREADS']='1'
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
from traitlets.config import Config
cfg=Config(); cfg.HistoryManager.hist_file=':memory:'
shell=InteractiveShell.instance(config=cfg)
shell.enable_gui=lambda gui:None
shell.run_line_magic('matplotlib','inline')
nb=nbformat.read('generative-baselines.ipynb',4)
nb.cells[9].source=nb.cells[9].source.replace(
    "ax.axis('equal')", "ax.axis('equal')\n            ax.set_aspect('equal', adjustable='box')")

def run(source):
    with capture_output() as captured:
        result=shell.run_cell(source)
    if not result.success: raise RuntimeError(captured.stdout+captured.stderr)
    outputs=[]
    if captured.stdout: outputs.append(nbformat.v4.new_output('stream',name='stdout',text=captured.stdout))
    if captured.stderr: outputs.append(nbformat.v4.new_output('stream',name='stderr',text=captured.stderr))
    for o in captured.outputs:
        outputs.append(nbformat.v4.new_output('display_data',data=o.data,metadata=o.metadata))
    return outputs
run(nb.cells[1].source)
run(nb.cells[3].source)
run(nb.cells[7].source.split('ref, _ =')[0])
run('train_final, _ = make_moons(n_samples=1500, noise=.1, random_state=SEED+9000)')
nb.cells[9].outputs=run(nb.cells[9].source)
addition='''central_means = digit_results.query("kernel == 'se' and factor == 1 and n == 1200")
kde_means = central_means[central_means.family == 'KDE'].groupby('param').mmd.mean()
lines.insert(2, f'At n=1,200, validation SE MMD² for KDE is '
    f'{kde_means.loc[.05]:.5f} at bandwidth 0.05 and '
    f'{kde_means.loc[.4]:.5f} at bandwidth 0.4. The broad bandwidth is clearly '
    'worse on this metric. In contrast, several flexible-model differences '
    'are similar in size to the between-run variation; they do not establish '
    'a reliable fine-grained ranking. More training data does not improve '
    'every observed estimate monotonically, as expected for finite-sample MMD.')
'''
nb.cells[14].source=nb.cells[14].source.replace("display(Markdown('\\n\\n'.join(lines)))",
    addition+"display(Markdown('\\n\\n'.join(lines)))")
run("digit_test_scores=pd.read_csv('digit_test_scores.csv'); digit_results=pd.read_csv('digit_results.csv')")
nb.cells[14].outputs=run(nb.cells[14].source)
nbformat.write(nb,'generative-baselines.ipynb')
print('Updated aspect-ratio figures and measured discussion.')
