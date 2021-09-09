from akitaplot import speedup_plot_base, speedup_base

class speedup_plot(speedup_plot_base):
  def decorate(self):
    # Customize the decorations, e.g. split line, text
    pass

class speedup(speedup_base):
  def transform_plot(self, plot_name, table):
    return speedup_plot(plot_name, table, figure_size=(10, 2))

if __name__ == '__main__':
  s = speedup('./config.yaml')
  s.dump_tables()
