import tempfile
from pathlib import Path
from synthetic.s12_pilot_v1 import workflow

workflow(Path(tempfile.gettempdir()) / 'astra-s12-evidence')
