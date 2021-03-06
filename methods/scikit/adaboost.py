'''
  @file adaboost.py
  @author Marcus Edel

  AdaBoost classifier with scikit.
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
from sklearn.ensemble import AdaBoostClassifier

'''
This class implements the AdaBoost classifier benchmark.
'''
class ADABOOST(object):

  '''
  Create the AdaBoost classifier benchmark instance.

  @param dataset - Input dataset to perform ADABOOST on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.model = None
    self.n_estimators = 50
    self.learning_rate = 1.0
    self.algorithm = 'SAMME.R'
    self.seed = 0

  '''
  Build the model for the AdaBoost classifier.

  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, labels):
    # Create and train the classifier.
    adaboost = AdaBoostClassifier(n_estimators=self.n_estimators,
                                  learning_rate=self.learning_rate,
                                  algorithm=self.algorithm,
                                  random_state=self.seed)
    adaboost.fit(data, labels)
    return adaboost

  '''
  Use the scikit libary to implement the AdaBoost classifier.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def ADABOOSTScikit(self, options):
    def RunADABOOSTScikit(q):
      totalTimer = Timer()

      Log.Info("Loading dataset", self.verbose)
      trainData, labels = SplitTrainData(self.dataset)
      testData = LoadDataset(self.dataset[1])

      # Get all the parameters.
      e = re.search("-e (\d+)", options)
      l = re.search("-l (\d+)", options)
      a = re.search("-a (\s+)", options)
      s = re.search("-n (\d+)", options)

      self.n_estimators = 50 if not e else int(e.group(1))
      self.learning_rate = 1.0 if not l else float(l.group(1))
      self.algorithm = 'SAMME.R' if not a else str(a.group(1))
      self.seed = 0 if not s else int(s.group(1))

      try:
        with totalTimer:
          self.model = self.BuildModel(trainData, labels)
          # Run AdaBoost classifier on the test dataset.
          self.model.predict(testData)
      except Exception as e:
        Log.Debug(str(e))
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)

      return time

    return timeout(RunADABOOSTScikit, self.timeout)

  '''
  Perform the AdaBoost classifier. If the method has been
  successfully completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform ADABOOST.", self.verbose)

    results = None
    if len(self.dataset) >= 2:
      results = self.ADABOOSTScikit(options)

      if results < 0:
        return results
    else:
      Log.Fatal("This method requires two datasets.")

    # Datastructure to store the results.
    metrics = {'Runtime' : results}

    if len(self.dataset) >= 3:

      # Check if we need to create a model.
      if not self.model:
        trainData, labels = SplitTrainData(self.dataset)
        self.model = self.BuildModel(trainData, labels)

      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])
      predictedlabels = self.model.predict(testData)

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, predictedlabels)
      metrics['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metrics['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metrics['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metrics['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metrics['MSE'] = Metrics.SimpleMeanSquaredError(truelabels, predictedlabels)

    return metrics
