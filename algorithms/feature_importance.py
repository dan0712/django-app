import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.cross_validation import train_test_split
import matplotlib.pyplot as plt
import pandas as pd

def feature_importance_report( idata, response_var):
    ###############################################################################
    # Load data
    y=idata[response_var]
    X=idata.drop[response_var,0]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

    ###############################################################################
    # Fit regression model
    params = {'n_estimators': 500, 'max_depth': 4, 'min_samples_split': 1,
              'learning_rate': 0.01, 'loss': 'ls'}
    clf = GradientBoostingRegressor(**params)

    clf.fit(X_train, y_train)
    mse = mean_squared_error(y_test, clf.predict(X_test))
    print("MSE: %.4f" % mse)

    ###############################################################################
    # Plot feature importance
    feature_importance = clf.feature_importances_
    # make importances relative to max importance
    feature_importance = 100.0 * (feature_importance / feature_importance.max())
    sorted_idx = np.argsort(feature_importance)
    pos = np.arange(sorted_idx.shape[0]) + .5
    plt.subplot(1, 2, 2)
    plt.barh(pos, feature_importance[sorted_idx], align='center')
    #plt.yticks(pos, boston.feature_names[sorted_idx]) (this is for tick naming, will change depending in the code
    plt.xlabel('Relative Importance')
    plt.title('Variable Importance')
    plt.show()

