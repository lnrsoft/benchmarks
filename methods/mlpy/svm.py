'''
  @file svm.py
  @author Marcus Edel

  Support vector machines with mlpy.
'''

import os
import sys
import inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

#Import the metrics definitions path.
metrics_folder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../metrics")))
if metrics_folder not in sys.path:
  sys.path.insert(0, metrics_folder)

from log import *
from timer import *
from definitions import *
from misc import *

import numpy as np
from mlpy import LibSvm

'''
This class implements the Support vector machines benchmark.
'''
class SVM(object):

  '''
  Create the Support vector machines benchmark instance.

  @param dataset - Input dataset to perform SVM on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.model = None
    self.kernel = 'rbf'
    self.C = 1.0
    self.gamma = 0.0

  '''
  Build the model for the Support vector machines.

  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, labels):
    # Create and train the classifier.
    svm = LibSvm(kernel_type=self.kernel,
                 C=self.C,
                 gamma=self.gamma)
    svm.learn(data, labels)
    return svm

  '''
  Use the mlpy libary to implement the Support vector machines.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def SVMMlpy(self, options):
    def RunSVMMlpy(q):
      totalTimer = Timer()

      Log.Info("Loading dataset", self.verbose)
      trainData, labels = SplitTrainData(self.dataset)
      testData = LoadDataset(self.dataset[1])

      k = re.search("-k (\s+)", options)
      c = re.search("-c (\d+)", options)
      g = re.search("-g (\d+)", options)

      self.kernel = 'rbf' if not k else str(k.group(1))
      self.C = 1.0 if not c else float(c.group(1))
      self.gamma = 0.0 if not g else float(g.group(1))

      try:
        with totalTimer:
          self.model = self.BuildModel(trainData, labels)
          # Run Support vector machines on the test dataset.
          self.model.pred(testData)
      except Exception as e:
        Log.Debug(str(e))
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)

      return time

    return timeout(RunSVMMlpy, self.timeout)

  '''
  Perform the Support vector machines. If the method has been
  successfully completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunTiming(self, options):
    Log.Info("Perform SVM.", self.verbose)

    if len(self.dataset) >= 2:
      return self.SVMMlpy(options)
    else:
      Log.Fatal("This method requires two datasets.")

  def RunMetrics(self, options):
    if len(self.dataset) >= 3:

      # Check if we need to create a model.
      if not self.model:
        trainData, labels = SplitTrainData(self.dataset)
        self.model = self.BuildModel(trainData, labels)

      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])

      predictedlabels = self.model.pred(testData)

      # Datastructure to store the results.
      metrics = {}

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, predictedlabels)
      metrics['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metrics['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metrics['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metrics['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metrics['MSE'] = Metrics.SimpleMeanSquaredError(truelabels, predictedlabels)
      return metrics
    else:
      Log.Fatal("This method requires three datasets.")
