# -*- coding: utf-8 -*-
"""credit card fraud detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1h-P4GkNTDmIrL4O916M9ZcZytDG6btJl

#Credit card fraud detection algorithm
It is important that credit card companies are able to recognize fraudulent credit card transactions so that customers are not charged for items that they did not purchase.

Content
The dataset contains transactions made by credit cards in September 2013 by European cardholders.
This dataset presents transactions that occurred in two days, where we have 492 frauds out of 284,807 transactions. The dataset is highly unbalanced, the positive class (frauds) account for 0.172% of all transactions.

It contains only numerical input variables which are the result of a PCA transformation. Unfortunately, due to confidentiality issues, we cannot provide the original features and more background information about the data. Features V1, V2, … V28 are the principal components obtained with PCA, the only features which have not been transformed with PCA are 'Time' and 'Amount'. Feature 'Time' contains the seconds elapsed between each transaction and the first transaction in the dataset. The feature 'Amount' is the transaction Amount, this feature can be used for example-dependant cost-sensitive learning. Feature 'Class' is the response variable and it takes value 1 in case of fraud and 0 otherwise.
"""

import numpy as np
import pandas as pd
import sklearn
import scipy
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report,accuracy_score
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from pylab import rcParams
rcParams['figure.figsize'] = 14, 8
RANDOM_SEED = 42
LABELS = ["Normal", "Fraud"]

"""LOAD DATA"""

data = pd.read_csv('creditcard.csv',sep=',')
data.head()
#HERE FOR output class, 1 - indicates fraud and 0- indicates not fraud

data.info()

#to see if there are any null values
data.isnull().values.any()

data.isnull().sum()

"""DEALING MISSING DATA"""

data[data.Amount.isnull()]

data.dropna(how='any',inplace=True)#all a row if any of its values are missing

data.isnull().sum()

"""THE PLOT SHOWS THAT THERE IS DATA IMBALANCE PROBLEM"""

count_classes = pd.value_counts(data['Class'], sort = True)

count_classes.plot(kind = 'bar', rot=0)

plt.title("Transaction Class Distribution")

plt.xticks(range(2), LABELS) 
#xticks( ticks ) sets the x-axis tick values, which are the locations along the x-axis where the tick marks appear

plt.xlabel("Class")

plt.ylabel("Frequency")
#here we can see that the dataset is imbalanced but I am directly applying anomaly detection algorithm

## Get the Fraud and the normal dataset 

fraud = data[data['Class']==1]#value 1 for class is fraud

normal = data[data['Class']==0]#value 0 for class is normal

print(fraud.shape,normal.shape)

fraud.Amount.describe()

fraud.Time

normal.Amount.describe()

f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
f.suptitle('Amount per transaction by class')
bins = 50
ax1.hist(fraud.Amount, bins = bins)
ax1.set_title('Fraud')
ax2.hist(normal.Amount, bins = bins)
ax2.set_title('Normal')
plt.xlabel('Amount ($)')
plt.ylabel('Number of Transactions')
plt.xlim((0, 20000))
plt.yscale('log')
plt.show();
#here you can see that for fraud, the transaction amount is very les
#for normal, the transaction amount is high

# We Will check Do fraudulent transactions occur more often during certain time frame ? Let us find out with a visual representation.

f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
f.suptitle('Time of transaction vs Amount by class')
ax1.scatter(fraud.Time, fraud.Amount)
ax1.set_title('Fraud')
ax2.scatter(normal.Time, normal.Amount)
ax2.set_title('Normal')
plt.xlabel('Time (in Seconds)')
plt.ylabel('Amount')
plt.show()
#this doesnt help us to discover too much

#here, we consider a portion (0.1) of the whole dataset and this is to save time.
data1= data.sample(frac = 0.1,random_state=1)

data1.shape

data.shape

#Determine the number of fraud and valid transactions in the dataset

Fraud = data1[data1['Class']==1]

Valid = data1[data1['Class']==0]

"""CALCULATES OUTLIER FRACTION"""

#You can set the value of the outlier fraction according to your problem and your understanding of the data. In our example, I want to detect 5% observations that are not similar to the rest of the data. So, I'm going to set the value of outlier fraction as 0.05
outlier_fraction = len(Fraud)/float(len(Valid))#this calculates the amount of outliers
print(outlier_fraction)

print("Fraud Cases : {}".format(len(Fraud)))

print("Valid Cases : {}".format(len(Valid)))

## Correlation
#Each cell in the table shows the correlation between two variables
#Values always range between -1 (strong negative relationship) and +1 (strong positive relationship).
import seaborn as sns
#get correlations of each features in dataset
corrmat = data1.corr()
top_corr_features = corrmat.index
plt.figure(figsize=(20,20))
#plot heat map
g=sns.heatmap(data[top_corr_features].corr(),annot=True,cmap="viridis")

#Create independent and Dependent Features
columns = data1.columns.tolist()
# Filter the columns to remove data we do not want 
columns = [c for c in columns if c not in ["Class"]]
# Store the variable we are predicting 
target = "Class"
# Define a random state 
state = np.random.RandomState(42)#random_state parameter is used for initializing the internal random number generator, which will decide the splitting of data into train and test indices. 
X = data1[columns]
Y = data1[target]
X_outliers = state.uniform(low=0, high=1, size=(X.shape[0], X.shape[1]))
# Print the shapes of X & Y
print(X.shape)
print(Y.shape)

"""#CLASSIFIERS USED TO DETECT ANOMALY/ OUTLIERS
#ISOLATION FOREST
Isolation forest is the first anomaly detection algorithm that identifies anomalies using isolation. Similarly to Random Forest, it is built on an ensemble of binary (isolation) trees. It can be scaled up to handle large, high-dimensional datasets.
working:
here the outliers will be splitted initially and outliers will have less score and depending on that we can easily find outliers.
#LOCAL OUTLIER FACTOR (LOF) ALGORITHM
is an unsupervised anomaly detection method which computes the local density deviation of a given data point with respect to its neighbors. It considers as outliers the samples that have a substantially lower density than their neighbors. The local density is estimated by the typical distance at which a point can be "reached" from its neighbors.
#SVM
some other examples are KNN, K-Means,etc
"""

classifiers = {
    "Isolation Forest":IsolationForest(n_estimators=100, max_samples=len(X), 
                                       contamination=outlier_fraction,random_state=state, verbose=0),
    "Local Outlier Factor":LocalOutlierFactor(n_neighbors=20, algorithm='auto', 
                                              leaf_size=30, metric='minkowski',
                                              p=2, metric_params=None, contamination=outlier_fraction),
    "Support Vector Machine":OneClassSVM(kernel='rbf', degree=3, gamma=0.1,nu=0.05, 
                                         max_iter=-1)
   
}
#here, Minkowski distance or Minkowski metric is a metric in a normed vector space which can be considered as a generalization of both the Euclidean distance and the Manhattan distance

type(classifiers)

n_outliers = len(Fraud)
for i, (clf_name,clf) in enumerate(classifiers.items()):
    #Fit the data and tag outliers
    if clf_name == "Local Outlier Factor":
        y_pred = clf.fit_predict(X)
        scores_prediction = clf.negative_outlier_factor_
    elif clf_name == "Support Vector Machine":
        clf.fit(X)
        y_pred = clf.predict(X)
    else:    
        clf.fit(X)
        scores_prediction = clf.decision_function(X)
        y_pred = clf.predict(X)
    #Reshape the prediction values to 0 for Valid transactions , 1 for Fraud transactions
    y_pred[y_pred == 1] = 0
    y_pred[y_pred == -1] = 1
    n_errors = (y_pred != Y).sum()
    # Run Classification Metrics
    print("{}: {}".format(clf_name,n_errors))
    print("Accuracy Score :")
    print(accuracy_score(Y,y_pred))
    print("Classification Report :")
    print(classification_report(Y,y_pred))

"""here we can see isolation forest and local outlier factor aree out performing SVM"""