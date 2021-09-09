import yaml, csv
import string
import os, sys, platform
import colorama
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns

def check_path_exists(path, errmsg):
  if not os.path.exists(path):
    print(str(path) + " is not existed! " + errmsg)
    sys.exit(0)
  return True

def get_expanded_abspath(path):
  # 1. expand ~ in path to absolute home directory
  # 2. normalize the path format, e.g. /path/to/dir// -> /path/to/dir
  return os.path.abspath(os.path.expanduser(path))

def print_green_prompt(msg):
  print(colorama.Fore.GREEN + colorama.Style.BRIGHT + msg + 
        colorama.Style.RESET_ALL)

def check_csv_valid(path):
  try:
    with open(path, newline='') as f:
      content = f.read()
      # isprintable does not allow newlines, printable does not allow umlauts.
      if not all([c in string.printable or c.isprintable() for c in content]):
        return False
      dialect = csv.Sniffer().sniff(content)
      return True
  except csv.Error:
    # could not get a csv dialect -> probably not a csv.
    return False

# Load config YAML and organize models and benchmarks lists
class config:
  def __init__(self, config_path = './config.yaml'):
    # Declaring the variables as instance members, not class members
    self.models = []
    self.benchmarks = []
    self.grabs = []
    self.__raw_benchmarks = []
    self.__raw_config = []
    self.modelID = {}

    check_path_exists(config_path, "Please provide the configuration file!")

    with open(config_path, 'r', encoding='utf-8') as stream:
      try:
        yaml_str = yaml.safe_load(stream)
      except yaml.YAMLError as exc:
        print(exc)

    self.__raw_config = yaml_str['config']
    self.__raw_benchmarks = yaml_str['benchmarks']

    self.__generate_models_config()
    self.__generate_benchmarks_config()
    self.__generate_grabs_config()

    # print(self.models)

  def __generate_models_config(self):
    model_idx = 0

    # Baseline item
    prefix = get_expanded_abspath(self.__raw_config['baseline']['pathPrefix'])
    check_path_exists(prefix, "Please provide a valid path prefix of baseline!")
    baseline_display_name = self.__raw_config['baseline']['displayName']
    self.models.append({
      'name': 'baseline', 
      'displayName': baseline_display_name,
      'pathPrefix': prefix + '/' # build the full path prefix header
    })
    self.modelID['baseline'] = model_idx
    self.modelID[baseline_display_name] = model_idx
    model_idx += 1

    # Optimizations items
    for name, conf in self.__raw_config['optimizations'].items():
      prefix = get_expanded_abspath(conf['pathPrefix'])
      check_path_exists(prefix, "Please provide a valid path prefix of " +
        name + "!")
      self.models.append({
        'name': name,
        'displayName': conf['displayName'],
        'pathPrefix': prefix + '/' # build the full path prefix header
      })
      self.modelID[name] = self.modelID[conf['displayName']] = model_idx
      model_idx += 1

  def __generate_benchmarks_config(self):
    # TODO: add more configurable options for benchmarks
    for name, conf in self.__raw_benchmarks.items():
      self.benchmarks.append({
        'name': name,
        'displayName': conf['displayName'],
        'path': conf['buildInplace']['path'],
        'options': conf['buildInplace']['options']
      })
    # print(self.benchmarks)
  
  def __generate_grabs_config(self):
    for name, conf in self.__raw_config['grabs'].items():
      self.grabs.append({
        'name': name,
        'where': conf['where'],
        'what': conf['what']
      })
    # print(self.grabs)

  def get_baseline_config(self):
    return self.models[0]

  def yield_benchmark_of_model(self, model_name):
    for b in self.benchmarks:
      b_name = b['name']
      prefix = self.models[self.modelID[model_name]]['pathPrefix']
      suffix = self.__raw_benchmarks[b_name]['path']
      combine = prefix + suffix
      check_path_exists(combine, "Please check the combination of model " + 
        model_name + " prefix path and benchmark " + b_name + " prefix path!")
      # yield the tuple(benchmark_display_name, path, options)
      yield (b['displayName'], combine, b['options'])

  def get_benchmark_options(self, benchmark_name):
    return self.__raw_benchmarks[benchmark_name]


# Build and run benchmark with certain options and generate metrics csv
class runner:
  def __init__(self, path, options):
    check_path_exists(path, "Please provide the right benchmark path!")
    cwd = os.getcwd()
    os.chdir(path)

    exe_name = os.path.basename(path)
    os_cmd = self.runner_command(exe_name, options)

    try:
      if os.system(os_cmd) != 0:
          raise Exception("Something wrong exists in the runner command " + 
            os_cmd + '!')
    except:
      print("Command does not work!")

    check_path_exists('metrics.csv', "metrics.csv not generated by benchmark.")
    self.metrics_csv_abspath = os.path.abspath('metrics.csv')
    os.chdir(cwd)
  
  def metrics_csv(self):
    return self.metrics_csv_abspath
  
  def __str__(self):
    return str(self.metrics_csv())
  
  # Override it if needed, setting the runner command for each workload
  def runner_command(self, exe_name, options):
    os_name = platform.system()
    if os_name == 'Linux' or os_name == 'Darwin':
      return "go build && ./" + exe_name + ' ' + options
    elif os_name == 'Windows':
      return "go build && " + exe_name + '.exe ' + options


class metrics:
  def __init__(self, path):
    check_path_exists(path, "Please provide the right metrics path!")
    if not check_csv_valid(path):
      print(str(path) + "is not a valid csv file! Please provide the right " +
      "csv format file for class metrics.")
      sys.exit(0)
    self.path = path
    
  def __str__(self):
    return str(self.path)


# Append benchmark and build each model column for table
class model:
  def __init__(self, name:str, where:str, what:str):
    self.name, self.where, self.what = name, where, what
    self.df = pd.DataFrame()
    self.df[name] = ''
  
  def __repr__(self) -> str: 
    return self.df

  def __query(self, csv_path):
    # Attention to the initial whitespaces of csv entities
    csv = pd.read_csv(csv_path, index_col=0, skipinitialspace=True, sep=r',')
    select = csv[(csv['where'] == self.where) & (csv['what'] == self.what)]
    # print(selected['value'].dtypes) => float64
    return np.float64(select['value'])

  def append_benchmark(self, benchmark_name, csv_path):
    # Whether to use display name or config name, 
    # consider the yield function in class config
    self.df.loc[benchmark_name] = self.__query(csv_path)


class table:
  def __init__(self, title, dfs_of_models):
    self.title = title
    self.origin = pd.concat(dfs_of_models, axis=1, join='outer')
    self.downstream = pd.DataFrame()
    
    self.manipulation()

  def __repr__(self):
    return "\nOriginal table:\n{}\n\nDownstream table:\n{}".format(self.origin, 
            self.downstream)

  # Must be overridden, manipulating from self.origin to self.downstream
  def manipulation(self):
    raise NotImplementedError
  
  def data(self):
    return self.downstream

  # Must be overridden, providing a list of the benchmarks' display order 
  def benchmarks_order(self):
    raise NotImplementedError

  def default_benchmarks_order(self):
    # print("Index order: ", self.origin.index.tolist())
    return self.origin.index.tolist()

  def model_labels(self):
    return self.origin.columns.tolist()

  def columns_to_draw(self):
    # tuple(Benchmark, Configuration, Target)
    return tuple(self.downstream.columns.tolist())
  
  def get_baseline_name(self):
    # Make sure baseline locates at index 0
    return self.model_labels()[0]

  def dump_origin_to_csv(self, dump_file_name):
    self.origin.to_csv(dump_file_name)

  def dump_downstream_to_csv(self, dump_file_name):
    self.downstream.to_csv(dump_file_name)

class plot:
  # plot config can be overridden in derivative class
  font_scale = 2.0
  legend_column_spacing = 0.6
  legend_loc = 10
  legend_bbox_to_anchor = (0.5, 1.15)

  def __init__(self, plot_name, table, figure_size=(10, 2)):
    self.plot_name = plot_name
    self.label_num = len(table.model_labels())
    self.x_axis_order = table.benchmarks_order()

    x, hue, y = table.columns_to_draw()

    matplotlib.rc('text', usetex=False)
    sns.set_context('paper', font_scale=self.font_scale)
    sns.set_style('whitegrid')

    fig, self.ax = plt.subplots(figsize=figure_size)
    sns.barplot(data=table.data(), 
                x=x, hue=hue, y=y, 
                order=self.x_axis_order, 
                palette=self.custom_palette(),
                ec='k', ax=self.ax)
    handles, labels = self.ax.get_legend_handles_labels()
    labels = table.model_labels()
    self.ax.legend(handles, 
                  labels, 
                  frameon=False,
                  fancybox=None,
                  columnspacing=self.legend_column_spacing,
                  facecolor=None, 
                  edgecolor=None, 
                  bbox_to_anchor=self.legend_bbox_to_anchor, 
                  loc=self.legend_loc, 
                  ncol=len(labels))
    self.decorate()

    self.called_plot_show = False
    self.__view_and_save()

  def custom_palette(self):
    norm = mcolors.TwoSlopeNorm(vmin=0., vcenter=(self.label_num/2.0),
                                vmax=self.label_num)
    colors = reversed([plt.cm.Blues(norm(c)) for c in range(self.label_num)])
    return colors

  # Shouldn't be called outside the class
  def __view_and_save(self):
    # plt.show() clears the whole thing, so anything 
    # afterwards will happen on a new empty figure
    if self.called_plot_show == True:
      return 
    
    self.called_plot_show = True
    self.__output()
    plt.show()
    plt.close()

  # Shouldn't be called outside the class
  def __output(self):
    plt.savefig(self.plot_name + '.pdf', bbox_inches='tight')
    plt.savefig(self.plot_name + '.png', dpi=600, bbox_inches='tight')
  
  # Override it if needed, just use the self.ax directly
  def decorate(self):
    pass


class workflow:
  def __init__(self, grab, models):
    self.models = models
    self.table = self.__generate_table(grab)
    self.grab_plot = self.__generate_plot(grab['name'], self.table)

  def __generate_table(self, grab):
    model_dateframes = []
    for each_model in self.models:
      m = model(each_model['displayName'], grab['where'], grab['what'])
      for b_name, csv_path in each_model['benchmarks']:
        m.append_benchmark(b_name, str(csv_path))

      model_dateframes.append(m.df)
      print(m.df)
    return self.transform_table(grab['name'], model_dateframes)
  
  def __generate_plot(self, plot_name, table):
    return self.transform_plot(plot_name, table)

  def dump_tables(self):
    for (t, g) in zip(self.grab_tables, self.conf.grabs):
      t.dump_origin_to_csv(g['name'] + '_origin.csv')
      t.dump_downstream_to_csv(g['name'] + '_downstream.csv')
  
  # Override it if needed, based on the derivative class of table
  def transform_table(self, table_name, model_dateframes):
    return table(table_name, model_dateframes)
  
  # Override it if needed, based on the derivative class of plot
  def transform_plot(self, plot_name, table):
    p = plot(plot_name, table)
    p.preview()
    return p


class config_workflow:
  def __init__(self, config_path):
    self.conf = config(config_path)
    self.grab_tables = [self.__generate_table(g) for g in self.conf.grabs]
    self.grab_plots = []
    for (t, g) in zip(self.grab_tables, self.conf.grabs):
      self.grab_plots.append(self.__generate_plot(g['name'], t))

  def __generate_table(self, grab):
    model_dateframes = []
    for each_model in self.conf.models:
      m = model(each_model['displayName'], grab['where'], grab['what'])
      for b_name, path, options in self.conf.yield_benchmark_of_model(m.name):
        print_green_prompt("Build [{}: {}] ...".format(m.name, b_name))
        csv_path = runner(path, options).metrics_csv()
        m.append_benchmark(b_name, csv_path)

      model_dateframes.append(m.df)
      print(m.df)
    return self.transform_table(grab['name'], model_dateframes)
  
  def __generate_plot(self, plot_name, table):
    return self.transform_plot(plot_name, table)

  def dump_tables(self):
    for (t, g) in zip(self.grab_tables, self.conf.grabs):
      t.dump_origin_to_csv(g['name'] + '_origin.csv')
      t.dump_downstream_to_csv(g['name'] + '_downstream.csv')
  
  # Override it if needed, based on the derivative class of table
  def transform_table(self, table_name, model_dateframes):
    return table(table_name, model_dateframes)
  
  # Override it if needed, based on the derivative class of plot
  def transform_plot(self, plot_name, table):
    p = plot(plot_name, table)
    p.preview()
    return p


class speedup_table_base(table):
  def manipulation(self):
    self.downstream = self.origin.copy()

    bl = self.get_baseline_name()
    model_labels = self.model_labels()
    # Make sure baseline locates at index 0
    for m_name in reversed(model_labels):
      self.downstream[m_name] = self.downstream[bl] / self.downstream[m_name]

    bm = 'Benchmark'
    self.downstream[bm] = self.downstream.index
    self.downstream = self.downstream.melt(id_vars=[bm], 
                                           value_vars=model_labels)
    self.downstream[bm] = self.downstream[bm].str.upper()
    self.downstream.columns = ['Benchmark', 'Configuration', 'Speedup']

    print(self)

  def benchmarks_order(self):
    return self.default_benchmarks_order()


class speedup_plot_base(plot):
  font_scale = 2.0
  def decorate(self):
    pass


class speedup_base(workflow):
  def transform_table(self, table_name, dfs_for_table):
    return speedup_table_base(table_name, dfs_for_table)
  
  def transform_plot(self, plot_name, table):
    return speedup_plot_base(plot_name, table, figure_size=(10, 2))


class config_speedup_base(config_workflow):
  def transform_table(self, table_name, dfs_for_table):
    return speedup_table_base(table_name, dfs_for_table)
  
  def transform_plot(self, plot_name, table):
    return speedup_plot_base(plot_name, table, figure_size=(10, 2))


# if __name__ == '__main__':
#   s = speedup('./config.yaml')
#   s.dump_tables()
