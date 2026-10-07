from pathlib import Path

from absl import app, flags
from cellot.utils import load_config
from cellot.utils.loaders import load_data, load_model
from cellot.transport import transport

FLAGS = flags.FLAGS
flags.DEFINE_string('outdir', '', 'Path to model/experiment directory.')
flags.DEFINE_string('output', '', 'Path to write predicted .h5ad. Defaults to <outdir>/evals_iid_data_space/imputed_full.h5ad.')
flags.DEFINE_string('data', '', 'Path to input .h5ad file (overrides config.data.path).')


def main(argv):
    expdir = Path(FLAGS.outdir)
    config = load_config(expdir / 'config.yaml')

    if FLAGS.data:
        config.data.path = FLAGS.data

    source, model_kwargs = load_data(
        config,
        split_on=[],
        return_as='dataset',
        include_model_kwargs=True,
    )

    model, *_ = load_model(
        config,
        restore=expdir / 'cache' / 'model.pt',
        **model_kwargs,
    )

    predicted = transport(config, model, source)

    outpath = FLAGS.output if FLAGS.output else str(expdir / 'evals_iid_data_space' / 'imputed_full.h5ad')
    predicted.write(outpath)

if __name__ == '__main__':
    app.run(main)
