# akitaplot

Akita plot is an easy-to-use performance visualization tool for [akita project](https://gitlab.com/akita), especially for [MGPUSim simulator](https://gitlab.com/akita/mgpusim).

Using akita plot, we can compare the performance of different configurations (i.e. models) running the same set of benchmarks. Based on a flexible configuration scheme, 1) the metrics for analyzing can be collected easily, 2) the benchmark path and options can be set smoothly, 3) the models are also easy to append.

## Usage

1. Copy the example of `config.yaml` to your visualization directory (which will store the analyzing results, e.g. table, plot).

2. Customize the config file: adding the benchmarks details, setting the metric you're interested in, choosing the baseline and optimized models for analyzing.

3. Determine what kind of the data analyzing you prefer, speedup comparing or value displaying.
    * For speedup comparing: we implement a partially-complete class (i.e. example) in akitaplot.py, what you need to do is to override some methods e.g. table.manipulation, plot.decorate to meet your demanding.
    * For other use: you could follow the example of class `speedup_table`, `speedup_plot`, `speedup`, and extending the superclass `table`, `plot`, `workflow` and implement the interfaces.

4. Import the akitaplot.py as a module, then use the least codes to generate your analyzing plots!

