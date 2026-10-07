# [Learning Single-Cell Perturbation Responses using Neural Optimal Transport](https://www.nature.com/articles/s41592-023-01969-x)

**Authors**: Charlotte Bunne\*, Stefan G. Stark\*, Gabriele Gut\*, Jacobo Sarabia Del Castillo, Mitch Levesque, Kjong-Van Lehmann, Lucas Pelkmans, Andreas Krause, Gunnar Rätsch

The Nature Method publication is available [**here**](https://www.nature.com/articles/s41592-023-01969-x).

<p align='center'><img src='assets/overview.png' alt='Overview.' width='100%'> </p>

Understanding and predicting molecular responses in single cells upon chemical, genetic, or mechanical perturbations is a core question in biology. Obtaining single-cell measurements typically requires the cells to be destroyed. This makes learning heterogeneous perturbation responses challenging as we only observe *unpaired* distributions of perturbed or non-perturbed cells. Here we leverage the theory of optimal transport and the recent advent of convex neural architectures to present `CellOT`, a framework for learning the response of individual  cells to a given perturbation by coupling these unpaired distributions. We achieve this alignment with a learned transport map that allows us to infer the treatment responses of unseen untreated cells. `CellOT` outperforms current methods at predicting single-cell drug responses, as profiled by scRNA-seq and a multiplexed protein imaging technology.

This repository contains the `CellOT` method and evaluation scripts to reproduce the results of experiments on predicting single-cell drug responses, as profiled by scRNA-seq and a multiplexed protein imaging technology. Further, we provide experiments on `CellOT`'s generalization performance to unseen settings by (a) predicting the scRNA-seq responses of holdout lupus patients exposed to IFN-beta, and (b) modeling the hematopoietic developmental trajectories of different subpopulations.

### Installation with pixi

The environment can be set up with [pixi](https://pixi.sh), using the `pixi.toml` and `pixi.lock` files in the repository root. Install pixi (if not already available):
```
curl -fsSL https://pixi.sh/install.sh | bash
```
Then, from the repository root, create the environment (this also installs `CellOT` in editable mode):
```
pixi install
```
Commands can be run inside the environment with `pixi run <command>` (e.g., `pixi run python scripts/train.py ...`), or an interactive shell can be opened with `pixi shell`. 

## Datasets
You can download the preprocessed data [here](https://www.research-collection.ethz.ch/handle/20.500.11850/609681).

## Experiments
After downloading the dataset, the CellOT model can be trained via the `scripts/train.py` script. For example, we can train CellOT on 4i data to predict perturbation effects of Cisplatin:
```
python ./scripts/train.py --outdir ./results/4i/drug-cisplatin/model-cellot --config ./configs/tasks/4i.yaml --config ./configs/models/cellot.yaml --config.data.target cisplatin
```
All scripts to reproduce the experiments in the i.i.d. (independent-and-identically-distributed), o.o.s. (out-of-sample), and o.o.d. (out-of-distribution) setting can be found in `scripts/submit`. More details on the method and experiments can be found in the [paper](https://www.nature.com/articles/s41592-023-01969-x).

The training of CellOT on 4i data takes around 3 hours on CPU. Once trained, the model can be evaluated via:
```
python ./scripts/evaluate.py --outdir ./results/4i/drug-cisplatin/model-cellot --setting iid --where data_space
```
The user can hereby choose if the model is evaluated in the `iid` or `ood` setting, and if the metrics are considered in the data or latent space (via the flag `where`). Please note that for 4i data, no o.o.s. or o.o.d. task exists and no embedding is necessary (i.e., evaluation in `data_space`).

### Training with `run_train_cellot.sh`

`run_train_cellot.sh` wraps `scripts/train.py` in the pixi environment and contains `#SBATCH` headers for submission to a SLURM cluster (16 GB memory, 4 CPUs, up to 7 days). Before running, edit the script to set:
- `--outdir`: directory where the trained model (`cache/model.pt`), the resolved `config.yaml`, and logs are written.
- `--config configs/tasks/<task>.yaml`: the task config, which defines the dataset (`data.path`), the feature list (`data.features`), the condition column in `obs` (`data.condition`) and its `source`/`target` values, as well as the train/test split.
- `--config configs/models/cellot.yaml`: the model config (keep as is for CellOT).

For example:
```
exec pixi run python scripts/train.py \
    --outdir /path/to/results/8_7d \
    --config configs/tasks/4i_embryo_8_7d.yaml \
    --config configs/models/cellot.yaml
```
Then submit the job via SLURM:
```
sbatch run_train_cellot.sh
```
or run it directly on the current machine:
```
bash run_train_cellot.sh
```
SLURM logs are written to `slurm-<jobid>_<taskid>.out` / `.err` in the submission directory.

### Prediction

Once a model is trained, `scripts/predict.py` applies the learned transport map to a dataset and writes the predicted cells as an `.h5ad` file:
```
pixi run python scripts/predict.py \
    --outdir /path/to/results/8_7d \
    --data /path/to/new_dataset.h5ad \
    --output /path/to/predictions.h5ad
```
Flags:
- `--outdir` (required): the training output directory; the model is loaded from `<outdir>/cache/model.pt` and the config from `<outdir>/config.yaml`.
- `--data` (optional): input `.h5ad` file to predict on. Defaults to `data.path` from the training config.
- `--output` (optional): path of the predicted `.h5ad`. Defaults to `<outdir>/evals_iid_data_space/imputed_full.h5ad`.

No train/test split is applied: all cells whose condition (`data.condition`) matches the configured `source` or `target` value are transported. The input data must therefore contain this `obs` column with those values, as well as all features listed in `data.features`. The output keeps the input `obs` and `var` annotations, with `X` replaced by the predicted values.

## Citation

In case you found our work useful, please consider citing us:
```
@article{bunne2023learning,
  title={Learning single-cell perturbation responses using neural optimal transport},
  author={Bunne, Charlotte and Stark, Stefan G and Gut, Gabriele and Del Castillo, Jacobo Sarabia and Levesque, Mitch and Lehmann, Kjong-Van and Pelkmans, Lucas and Krause, Andreas and R{\"a}tsch, Gunnar},
  journal={Nature Methods},
  volume={20},
  number={11},
  pages={1759--1768},
  year={2023},
  publisher={Nature Publishing Group US New York}
}
```

## Contact
In case you have questions, please contact us via the Github Issues.
