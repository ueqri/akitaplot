# akitaplot

Akita plot is an easy-to-use performance visualization tool for [akita project](https://gitlab.com/akita), especially for [MGPUSim simulator](https://gitlab.com/akita/mgpusim).

Using akita plot, we could compare the performance of different configurations (i.e. models) running the same set of benchmarks.

And Based on a flexible configuration scheme, 1) the metrics for analyzing can be collected easily, 2) the benchmark path and options can be set smoothly, 3) the models are also easy to append.

## Usage

1. Copy the example of `config.yaml` to your visualization directory (which will store the analyzing results, e.g. tables and plots).

2. Customize the config file: adding the benchmarks details, setting the metric we're interested in, choosing the baseline and optimized models for analyzing.

3. Determine the kind of the data analyzing, **speedup comparing** or **raw data visualization**.
    * For **speedup comparing**: we've implemented a partially-complete class as example in akitaplot.py, so just override some methods e.g. `speedup_plot_base.decorate()` to meet your demanding.
    * For **other use**: just follow the example of class `speedup_table`, `speedup_plot`, `speedup`, extend only three superclass `table`, `plot`, `workflow` and implement those interfaces.

4. Import the akitaplot.py as a module, then use the least codes to generate your analyzing plots!

