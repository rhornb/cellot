from pathlib import Path

import pandas as pd


class Logger:
    def __init__(self, path, max_items=1024):
        self.path = Path(path)
        self.max_items = max_items
        self.loggers = dict()

        self.path.parent.mkdir(exist_ok=True, parents=True)

    def log(self, key, item=None, **kwargs):
        if key not in self.loggers:
            self.loggers[key] = SingleLogger(
                self.path, key, max_items=self.max_items
            )

        logger = self.loggers[key]
        logger.log(item, **kwargs)

    def flush(self):
        for logger in self.loggers.values():
            logger.flush()
        return


class SingleLogger:
    def __init__(self, path, key='scalars', max_items=1024):
        self.path = path
        self.max_items = max_items
        self.key = key

        self.store = list()
        self.curr_step = None
        self.curr_item = dict()

    def _clear_curr_item(self):
        if len(self.curr_item) == 0:
            return

        self.store.append(self.curr_item.copy())
        self.curr_item = dict()

        if len(self.store) > self.max_items:
            self.flush()

        return

    def log(self, item=None, **kwargs):
        item = {} if item is None else item
        kwargs.update(item)
        step = kwargs['step']
        kwargs = {k: float(v) for k, v in kwargs.items()}

        if step != self.curr_step:
            self._clear_curr_item()
            self.curr_step = step

        self.curr_item.update(kwargs)

        return

    def _write(self):
        df = pd.DataFrame(self.store).set_index('step')
        df.to_hdf(self.path, self.key, append=True, format='table')
        return

    def flush(self, key=None):
        self._clear_curr_item()
        self._write()
        self.store = list()


def plot_eval_metric(
    scalars_path, out_path, metric="mmd", stopped_step=None, ylabel=None
):
    """Plot an eval metric logged by `Logger` against training iteration.

    Marks the best (lowest) value and, if given, the early-stopping step.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    df = pd.read_hdf(scalars_path, "eval")
    # resumed runs append to the same table; keep the latest entry per step
    df = df[~df.index.duplicated(keep="last")].sort_index()
    series = df[metric].dropna()
    if series.empty:
        return None

    ink, muted, line = "#1f1f1e", "#6b6b66", "#2a78d6"
    fig, ax = plt.subplots(figsize=(7, 4), dpi=150)
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")

    ax.plot(series.index, series.values, color=line, linewidth=1.5)

    best_step = series.idxmin()
    best = series.loc[best_step]
    ax.scatter(
        [best_step], [best], s=40, color=line, edgecolor="#fcfcfb",
        linewidth=2, zorder=3,
    )
    ax.annotate(
        f"best {best:.4g} @ {int(best_step)}",
        (best_step, best), xytext=(6, -14), textcoords="offset points",
        color=ink, fontsize=9,
    )

    if stopped_step is not None:
        ax.axvline(stopped_step, color=muted, linewidth=1, linestyle="--")
        ax.annotate(
            f"early stop @ {int(stopped_step)}",
            (stopped_step, 1), xycoords=("data", "axes fraction"),
            xytext=(-4, -12), textcoords="offset points",
            ha="right", color=muted, fontsize=9,
        )

    ax.set_xlabel("iteration", color=ink)
    ax.set_ylabel(ylabel or f"eval {metric}", color=ink)
    ax.set_title(f"Eval {metric.upper()} over training", color=ink, loc="left")
    ax.grid(axis="y", color="#e6e5e0", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#c9c8c2")
    ax.tick_params(colors=muted)

    fig.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path
