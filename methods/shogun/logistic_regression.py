'''
  @file logistic_regression.py
  @author Marcus Edel

  Logistic Regression with shogun.
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

import numpy as np
from modshogun import RealFeatures, MulticlassLabels
from modshogun import MulticlassLogisticRegression

'''
This class implements the Logistic Regression benchmark.
'''
class LogisticRegression(object):

  '''
  Create the Logistic Regression benchmark instance.

  @param dataset - Input dataset to perform Logistic Regression on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.z = 0;
    self.model = None

  '''
  Build the model for the Logistic Regression.

  @param data - The train data.
  @param responses - The responses for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, responses):
    # Create and train the classifier.
    model = MulticlassLogisticRegression(self.z, RealFeatures(data.T),
        MulticlassLabels(responses))
    model.train()
    return model

  '''
  Use the shogun libary to implement Logistic Regression.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def LogisticRegressionShogun(self, options):
    def RunLogisticRegressionShogun(q):
      totalTimer = Timer()

      # Load input dataset.
      # If the dataset contains two files then the second file is the test file.
      try:
        if len(self.dataset) > 1:
          testSet = LoadDataset(self.dataset[1])

        # Use the last row of the training set as the responses.
        X, y = SplitTrainData(self.dataset[0])

        # Get the regularization value.
        self.z = re.search("-l (\d+)", options)
        self.z = 0 if not z else int(z.group(1))

        with totalTimer:
          # Perform logistic regression.
          self.model = BuildModel(x, y)
          self.model.train()

          if len(self.dataset) == 2:
            pred = classifier.apply(RealFeatures(testSet.T))
            self.predictions = pred.get_labels()

      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunLogisticRegressionShogun, self.timeout)

  '''
  Perform Logistic Regression. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform Logistic Regression.", self.verbose)

    results = self.LogisticRegressionShogun(options)
    if results < 0:
      return results

    metrics = {'Runtime' : results}

    if len(self.dataset) >= 3:
      # Check if we need to create a model.
      if not self.model:
        trainData, responses = SplitTrainData(self.dataset)
        self.model = self.BuildModel(trainData, responses)

      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, self.predictions)
      AvgAcc = Metrics.AverageAccuracy(confusionMatrix)
      AvgPrec = Metrics.AvgPrecision(confusionMatrix)
      AvgRec = Metrics.AvgRecall(confusionMatrix)
      AvgF = Metrics.AvgFMeasure(confusionMatrix)
      AvgLift = Metrics.LiftMultiClass(confusionMatrix)
      AvgMCC = Metrics.MCCMultiClass(confusionMatrix)
      AvgInformation = Metrics.AvgMPIArray(confusionMatrix, truelabels, self.predictions)
      SimpleMSE = Metrics.SimpleMeanSquaredError(truelabels, self.predictions)
      metric_results = (AvgAcc, AvgPrec, AvgRec, AvgF, AvgLift, AvgMCC, AvgInformation)

      metrics['Avg Accuracy'] = AvgAcc
      metrics['MultiClass Precision'] = AvgPrec
      metrics['MultiClass Recall'] = AvgRec
      metrics['MultiClass FMeasure'] = AvgF
      metrics['MultiClass Lift'] = AvgLift
      metrics['MultiClass MCC'] = AvgMCC
      metrics['MultiClass Information'] = AvgInformation
      metrics['Simple MSE'] = SimpleMSE

    return metrics

