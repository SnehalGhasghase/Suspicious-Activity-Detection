# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Executes Keras benchmarks and accuracy tests."""
from __future__ import print_function

import os
import time

from absl import flags

from official.resnet import imagenet_main
from official.resnet.keras import keras_benchmark
from official.resnet.keras import keras_common
from official.resnet.keras import keras_imagenet_main

MIN_TOP_1_ACCURACY = 0.76
MAX_TOP_1_ACCURACY = 0.77

FLAGS = flags.FLAGS


class Resnet50KerasAccuracy(keras_benchmark.KerasBenchmark):
  """Benchmark accuracy tests for ResNet50 in Keras."""

  def __init__(self, output_dir=None, root_data_dir=None, **kwargs):
    """A benchmark class.

    Args:
      output_dir: directory where to output e.g. log files
      root_data_dir: directory under which to look for dataset
      **kwargs: arbitrary named arguments. This is needed to make the
                constructor forward compatible in case PerfZero provides more
                named arguments before updating the constructor.
    """

    flag_methods = [
        keras_common.define_keras_flags, imagenet_main.define_imagenet_flags
    ]

    self.data_dir = os.path.join(root_data_dir, 'imagenet')
    super(Resnet50KerasAccuracy, self).__init__(
        output_dir=output_dir, flag_methods=flag_methods)

  def benchmark_graph_8_gpu(self):
    """Test Keras model with Keras fit/dist_strat and 8 GPUs."""
    self._setup()
    FLAGS.num_gpus = 8
    FLAGS.data_dir = self.data_dir
    FLAGS.batch_size = 128 * 8
    FLAGS.train_epochs = 90
    FLAGS.model_dir = self._get_model_dir('benchmark_graph_8_gpu')
    FLAGS.dtype = 'fp32'
    self._run_and_report_benchmark()

  def benchmark_8_gpu(self):
    """Test Keras model with eager, dist_strat and 8 GPUs."""
    self._setup()
    FLAGS.num_gpus = 8
    FLAGS.data_dir = self.data_dir
    FLAGS.batch_size = 128 * 8
    FLAGS.train_epochs = 90
    FLAGS.model_dir = self._get_model_dir('benchmark_8_gpu')
    FLAGS.dtype = 'fp32'
    FLAGS.enable_eager = True
    # Add some thread tunings to improve performance.
    FLAGS.datasets_num_private_threads = 14
    self._run_and_report_benchmark()

  def _run_and_report_benchmark(self):
    start_time_sec = time.time()
    stats = keras_imagenet_main.run(flags.FLAGS)
    wall_time_sec = time.time() - start_time_sec

    super(Resnet50KerasAccuracy, self)._report_benchmark(
        stats,
        wall_time_sec,
        top_1_min=MIN_TOP_1_ACCURACY,
        top_1_max=MAX_TOP_1_ACCURACY,
        total_batch_size=FLAGS.batch_size,
        log_steps=100)

  def _get_model_dir(self, folder_name):
    return os.path.join(self.output_dir, folder_name)


class Resnet50KerasBenchmarkBase(keras_benchmark.KerasBenchmark):
  """Resnet50 benchmarks."""

  def __init__(self, output_dir=None, default_flags=None):
    flag_methods = [
        keras_common.define_keras_flags, imagenet_main.define_imagenet_flags
    ]

    super(Resnet50KerasBenchmarkBase, self).__init__(
        output_dir=output_dir,
        flag_methods=flag_methods,
        default_flags=default_flags)

  def _run_and_report_benchmark(self):
    start_time_sec = time.time()
    stats = keras_imagenet_main.run(FLAGS)
    wall_time_sec = time.time() - start_time_sec

    super(Resnet50KerasBenchmarkBase, self)._report_benchmark(
        stats,
        wall_time_sec,
        total_batch_size=FLAGS.batch_size,
        log_steps=FLAGS.log_steps)

  def benchmark_1_gpu_no_dist_strat(self):
    """Test Keras model with 1 GPU, no distribution strategy."""
    self._setup()

    FLAGS.num_gpus = 1
    FLAGS.enable_eager = True
    FLAGS.distribution_strategy = 'off'
    FLAGS.model_dir = self._get_model_dir('benchmark_1_gpu_no_dist_strat')
    FLAGS.batch_size = 128
    self._run_and_report_benchmark()

  def benchmark_graph_1_gpu_no_dist_strat(self):
    """Test Keras model in legacy graph mode with 1 GPU, no dist strat."""
    self._setup()

    FLAGS.num_gpus = 1
    FLAGS.enable_eager = False
    FLAGS.distribution_strategy = 'off'
    FLAGS.model_dir = self._get_model_dir('benchmark_graph_1_gpu_no_dist_strat')
    FLAGS.batch_size = 128
    self._run_and_report_benchmark()

  def benchmark_1_gpu(self):
    """Test Keras model with 1 GPU."""
    self._setup()

    FLAGS.num_gpus = 1
    FLAGS.enable_eager = True
    FLAGS.distribution_strategy = 'default'
    FLAGS.model_dir = self._get_model_dir('benchmark_1_gpu')
    FLAGS.batch_size = 128
    self._run_and_report_benchmark()

  def benchmark_xla_1_gpu(self):
    """Test Keras model with XLA and 1 GPU."""
    self._setup()

    FLAGS.num_gpus = 1
    FLAGS.enable_eager = True
    FLAGS.enable_xla = True
    FLAGS.distribution_strategy = 'default'
    FLAGS.model_dir = self._get_model_dir('benchmark_xla_1_gpu')
    FLAGS.batch_size = 128
    self._run_and_report_benchmark()

  def benchmark_graph_1_gpu(self):
    """Test Keras model in legacy graph mode with 1 GPU."""
    self._setup()

    FLAGS.num_gpus = 1
    FLAGS.enable_eager = False
    FLAGS.distribution_strategy = 'default'
    FLAGS.model_dir = self._get_model_dir('benchmark_graph_1_gpu')
    FLAGS.batch_size = 128
    self._run_and_report_benchmark()

  def benchmark_graph_xla_1_gpu(self):
    """Test Keras model in legacy graph mode with XLA and 1 GPU."""
    self._setup()

    FLAGS.num_gpus = 1
    FLAGS.enable_eager = False
    FLAGS.enable_xla = True
    FLAGS.distribution_strategy = 'default'
    FLAGS.model_dir = self._get_model_dir('benchmark_graph_xla_1_gpu')
    FLAGS.batch_size = 128
    self._run_and_report_benchmark()

  def benchmark_8_gpu(self):
    """Test Keras model with 8 GPUs."""
    self._setup()

    FLAGS.num_gpus = 8
    FLAGS.enable_eager = True
    FLAGS.distribution_strategy = 'default'
    FLAGS.model_dir = self._get_model_dir('benchmark_8_gpu')
    FLAGS.batch_size = 128 * 8  # 8 GPUs
    self._run_and_report_benchmark()

  def benchmark_8_gpu_tweaked(self):
    """Test Keras model with manual config tuning and 8 GPUs."""
    self._setup()

    FLAGS.num_gpus = 8
    FLAGS.enable_eager = True
    FLAGS.distribution_strategy = 'default'
    FLAGS.model_dir = self._get_model_dir('benchmark_8_gpu_tweaked')
    FLAGS.batch_size = 128 * 8  # 8 GPUs
    FLAGS.datasets_num_private_threads = 14
    self._run_and_report_benchmark()

  def benchmark_xla_8_gpu(self):
    """Test Keras model with XLA and 8 GPUs."""
    self._setup()

    FLAGS.num_gpus = 8
    FLAGS.enable_eager = True
    FLAGS.enable_xla = True
    FLAGS.distribution_strategy = 'default'
    FLAGS.model_dir = self._get_model_dir('benchmark_xla_8_gpu')
    # TODO(haoyuzhang): Set size to 128 per GPU when multi-GPU XLA OOM is fixed
    FLAGS.batch_size = 64 * 8  # 8 GPUs
    self._run_and_report_benchmark()

  def benchmark_graph_8_gpu(self):
    """Test Keras model in legacy graph mode with 8 GPUs."""
    self._setup()

    FLAGS.num_gpus = 8
    FLAGS.enable_eager = False
    FLAGS.distribution_strategy = 'default'
    FLAGS.model_dir = self._get_model_dir('benchmark_graph_8_gpu')
    FLAGS.batch_size = 128 * 8  # 8 GPUs
    self._run_and_report_benchmark()

  def benchmark_graph_xla_8_gpu(self):
    """Test Keras model in legacy graph mode with XLA and 8 GPUs."""
    self._setup()

    FLAGS.num_gpus = 8
    FLAGS.enable_eager = False
    FLAGS.enable_xla = True
    FLAGS.distribution_strategy = 'default'
    FLAGS.model_dir = self._get_model_dir('benchmark_graph_xla_8_gpu')
    # TODO(haoyuzhang): Set size to 128 per GPU when multi-GPU XLA OOM is fixed
    FLAGS.batch_size = 64 * 8  # 8 GPUs
    self._run_and_report_benchmark()

  def fill_report_object(self, stats):
    super(Resnet50KerasBenchmarkBase, self).fill_report_object(
        stats,
        total_batch_size=FLAGS.batch_size,
        log_steps=FLAGS.log_steps)


class Resnet50KerasBenchmarkSynth(Resnet50KerasBenchmarkBase):
  """Resnet50 synthetic benchmark tests."""

  def __init__(self, output_dir=None, root_data_dir=None, **kwargs):
    def_flags = {}
    def_flags['skip_eval'] = True
    def_flags['use_synthetic_data'] = True
    def_flags['train_steps'] = 110
    def_flags['log_steps'] = 10

    super(Resnet50KerasBenchmarkSynth, self).__init__(
        output_dir=output_dir, default_flags=def_flags)


class Resnet50KerasBenchmarkReal(Resnet50KerasBenchmarkBase):
  """Resnet50 real data benchmark tests."""

  def __init__(self, output_dir=None, root_data_dir=None, **kwargs):
    def_flags = {}
    def_flags['skip_eval'] = True
    def_flags['data_dir'] = os.path.join(root_data_dir, 'imagenet')
    def_flags['train_steps'] = 110
    def_flags['log_steps'] = 10

    super(Resnet50KerasBenchmarkReal, self).__init__(
        output_dir=output_dir, default_flags=def_flags)
