from importlib import import_module
import numpy as np
from scipy.linalg import eigh, cholesky
from scipy.stats import norm, describe
from pylab import plot, show, axis, subplot, xlabel, ylabel, grid

nationalpolling = np.array([
    [ 0 ],
    [ 32.1],
    [ 33.6],
    [ 21.6]
])

def model(scenario_name,nationalpolling):

    #Process the national polling figures

    threewayshare = sum(nationalpolling)

    threewaynationalpolling = 100*nationalpolling/threewayshare

    print(threewaynationalpolling)

    logistic_national = -np.log((100/threewaynationalpolling)-1)

    logistic_national[0][0] = 0

    print(logistic_national)

    #import the scenario

    scenario = import_module("scenarios." + scenario_name)

    generalelectionlean = scenario.generalelectionlean
    incumbent = scenario.incumbent
    candidates = scenario.candidates

    #Produce correlated random samples

    method = 'cholesky'

    num_samples = 10000

    r = np.array([
        [  0.485898333, -0.188300172, 0.040127195, 0.248745506],
        [ -0.188300172,  0.230703225,  -0.184160098, -0.074598424],
        [ 0.040127195, -0.184160098,  0.230962944, -0.096268113],
        [ 0.248745506, -0.074598424,  -0.096268113, 0.36021663]
    ])

    x = norm.rvs(size=(4, num_samples))

    c = cholesky(r, lower=True)

    y = np.dot(c, x)

    means = np.array([
        [  -1.55295],
        [ -0.04461],
        [ -0.06348],
        [ 0.11982]
    ])

    y = y + means + generalelectionlean + logistic_national

    y = 100*(1/(1+np.exp(-y)))

    print("y shape", y.shape)

    subplot(2,2,1)
    plot(y[0], y[1], 'b.')
    ylabel('Lab')
    axis('equal')
    grid(True)

    subplot(2,2,3)
    plot(y[0], y[2], 'b.')
    xlabel('Other')
    ylabel('Con')
    axis('equal')
    grid(True)

    subplot(2,2,4)
    plot(y[1], y[2], 'b.')
    xlabel('Lab')
    axis('equal')
    grid(True)

    show()

    #Produce random sample for independent vote consolidation

    number_other = candidates['other']

    if number_other > 0:
        if number_other == 1:
            consolidation = 1
        else:
            consolidation = norm.rvs(size=(1, num_samples))
            consolidation = 0.112692058*consolidation + 0.17333
            consolidation[consolidation<0] = 0
            consolidation = consolidation + 1/number_other
    else:
        consolidation = 0

    first_other = y[0]*consolidation

    #work out party vote shares

    threeparty = 100 - y[0]

    lab_firstround = threeparty*y[1]/(y[1]+y[2]+y[3])
    con_firstround = threeparty*y[2]/(y[1]+y[2]+y[3])
    libdem_firstround = threeparty*y[3]/(y[1]+y[2]+y[3])

    first_other.shape = lab_firstround.shape

    firstround = np.stack((first_other, lab_firstround, con_firstround, libdem_firstround), axis = 1)

    secondround = np.zeros(firstround.shape)

    secondround[np.arange(len(firstround)), np.argmax(firstround, axis=1)] = 1

    print(firstround)

    print(firstround.mean(axis=0))
    print(secondround.mean(axis=0))

    secondroundrandom = norm.rvs(size=(1, num_samples))









model("cambridgeshirepeterborough2021",nationalpolling)
