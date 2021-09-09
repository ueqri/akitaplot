from akitaplot import speedup_plot_base, speedup_base, metrics

grab = {
  "name": "kernelTime",
  "where": "driver",
  "what": "kernel_time"
}

baseline = {
  "displayName": "16 Unified MGPUSim",
  "benchmarks": [
    ("FIR", metrics("example_data/uni/fir-1024000.csv")),
    ("AES", metrics("example_data/uni/aes-6553600.csv")),
    ("KM", metrics("example_data/uni/kmeans-notion.csv")),
    ("MM", metrics("example_data/uni/matrixmultiplication-512-512-512.csv")),
    ("MT", metrics("example_data/uni/matrixtranspose-2560.csv")),
    ("FFT", metrics("example_data/uni/fft-16-5.csv")),
    ("BFS", metrics("example_data/uni/bfs-256000.csv")),
    ("AX", metrics("example_data/uni/atax-4096-4096.csv")),
    ("NW", metrics("example_data/uni/nw-6400.csv")),
    ("RU", metrics("example_data/uni/relu-4096000.csv")),
    ("BG", metrics("example_data/uni/bicg-4096-4096.csv")),
    ("PR", metrics("example_data/uni/pagerank-1024.csv")),
    ("ST", metrics("example_data/uni/stencil2d-256-256-20.csv")),
    ("SV", metrics("example_data/uni/spmv-2560-0_1.csv"))
  ]
}

waferscale = {
  "displayName": "Wafer-Scale",
  "benchmarks": [
    ("FIR", metrics("example_data/akkalat/fir-1024000.csv")),
    ("AES", metrics("example_data/akkalat/aes-6553600.csv")),
    ("KM", metrics("example_data/akkalat/kmeans-notion.csv")),
    ("MM", metrics("example_data/akkalat/matrixmultiplication-512-512-512.csv")),
    ("MT", metrics("example_data/akkalat/matrixtranspose-2560.csv")),
    ("FFT", metrics("example_data/akkalat/fft-16-5.csv")),
    ("BFS", metrics("example_data/akkalat/bfs-256000.csv")),
    ("AX", metrics("example_data/akkalat/atax-4096-4096.csv")),
    ("NW", metrics("example_data/akkalat/nw-6400.csv")),
    ("RU", metrics("example_data/akkalat/relu-4096000.csv")),
    ("BG", metrics("example_data/akkalat/bicg-4096-4096.csv")),
    ("PR", metrics("example_data/akkalat/pagerank-1024.csv")),
    ("ST", metrics("example_data/akkalat/stencil2d-256-256-20.csv")),
    ("SV", metrics("example_data/akkalat/spmv-2560-0_1.csv"))
  ]
}

class speedup_plot(speedup_plot_base):
  def decorate(self):
    # Customize the decorations, e.g. split line, text
    pass

class speedup(speedup_base):
  def transform_plot(self, plot_name, table):
    return speedup_plot(plot_name, table, figure_size=(10, 2))

if __name__ == '__main__':
  s = speedup(grab, [baseline, waferscale])
  s.dump_tables()
