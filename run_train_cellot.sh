#!/usr/bin/env bash
#SBATCH --partition=cpu,gpu
#SBATCH --mem=16000
#SBATCH --cpus-per-task=4
#SBATCH -e slurm-%A_%a.err
#SBATCH -o slurm-%A_%a.out
#SBATCH --time=7-00:00:00

exec pixi run python scripts/train.py \
    --outdir /data/active/rhornb/cellot/cellot_ave_validation/8_7d \
    --config configs/tasks/4i_embryo_8_7d.yaml \
    --config configs/models/cellot.yaml
