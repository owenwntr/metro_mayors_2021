from importlib import import_module
import numpy as np
from scipy.linalg import cholesky
from scipy.stats import norm, describe, t, expon
from pylab import plot, show, axis, subplot, xlabel, ylabel, grid
import matplotlib.pyplot as plt
import pandas as pd

nationalpolling = np.array([
    [ 35.3],
    [ 42.5],
    [ 7.2]
])

#incumbenteffect = 0

def election_model(scenario_name,nationalpolling, incumbenteffect):

    #Process the national polling figures

    threewayshare = sum(nationalpolling)

    threewaynationalpolling = 100*nationalpolling/threewayshare

    logistic_national = -np.log((100/threewaynationalpolling)-1)

    logistic_national[0][0] = 0

    #import the scenario

    scenario = import_module("scenarios." + scenario_name)

    generalelectionlean = scenario.generalelectionlean
    incumbent = scenario.incumbent
    candidates = scenario.candidates

    #Produce correlated random samples

    method = 'cholesky'

    num_samples = 100000

    r = np.array([
        [ 0.230703225,  -0.184160098, -0.074598424],
        [ -0.184160098,  0.230962944, -0.096268113],
        [ -0.074598424,  -0.096268113, 0.36021663]
    ])

    x = t.rvs(size=(3, num_samples), df=12)

    c = cholesky(r, lower=True)

    y = np.dot(c, x)

    means = np.array([
        [ -0.04461],
        [ -0.06348],
        [ 0.11982]
    ])

    y = y + means + generalelectionlean + logistic_national

    y = 100*(1/(1+np.exp(-y)))

    #subplot(2,2,1)
    #plot(y[0], y[1], 'b.')
    #ylabel('Con')
    #axis('equal')
    #grid(True)

    #subplot(2,2,3)
    #plot(y[0], y[2], 'b.')
    #xlabel('Lab')
    #ylabel('LibDem')
    #axis('equal')
    #grid(True)

    #subplot(2,2,4)
    #plot(y[1], y[2], 'b.')
    #xlabel('Con')
    #axis('equal')
    #grid(True)

    #show()

    #Produce random sample for independent vote consolidation

    number_other = candidates['other']

    if number_other > 0:
        if number_other == 1:
            consolidation = 1
        else:
            consolidation = t.rvs(size=(1, num_samples), df=12, loc = 0.17333, scale = 0.112692058)
            consolidation[consolidation<0] = 0
            consolidation = consolidation + 1/number_other
    else:
        consolidation = 0

    if number_other > 0:
        otherscombined_mean = 3.3285*np.log(number_other) + 14.276
        otherscombined = expon.rvs(size=(1, num_samples), scale = otherscombined_mean)
    else:
        otherscombined = np.zeros(shape=(1,num_samples))

    first_other = otherscombined*consolidation

    #work out party vote shares

    threeparty = 100 - otherscombined[0]

    if candidates['libdem']==0:
        lab_firstround = threeparty*y[0]/(y[0]+y[1])
        con_firstround = threeparty*y[1]/(y[0]+y[1])
        libdem_firstround = y[2]*0
    else:
        lab_firstround = threeparty*y[0]/(y[0]+y[1]+y[2])
        con_firstround = threeparty*y[1]/(y[0]+y[1]+y[2])
        libdem_firstround = threeparty*y[2]/(y[0]+y[1]+y[2])

    first_other.shape = lab_firstround.shape

    firstround_stack = np.stack((first_other, lab_firstround, con_firstround, libdem_firstround), axis = 1).transpose()

    if incumbent == "lab":
        firstround_stack[1] = firstround_stack[1] + incumbenteffect
        firstround_stack[0] = firstround_stack[0] - incumbenteffect*(firstround_stack[0]/(100-firstround_stack[1]))
        firstround_stack[2] = firstround_stack[2] - incumbenteffect*(firstround_stack[2]/(100-firstround_stack[1]))
        firstround_stack[3] = firstround_stack[3] - incumbenteffect*(firstround_stack[3]/(100-firstround_stack[1]))
    if incumbent == "con":
        firstround_stack[1] = firstround_stack[1] - incumbenteffect*(firstround_stack[1]/(100-firstround_stack[2]))
        firstround_stack[0] = firstround_stack[0] - incumbenteffect*(firstround_stack[0]/(100-firstround_stack[2]))
        firstround_stack[2] = firstround_stack[2] + incumbenteffect
        firstround_stack[3] = firstround_stack[3] - incumbenteffect*(firstround_stack[3]/(100-firstround_stack[2]))

    firstround = firstround_stack.transpose()

    secondround = np.zeros(firstround.shape)

    temp = firstround.argsort()
    firstround_ranks = np.arange(len(firstround))[temp.argsort()]

    #print(firstround.mean(axis=0))
    #print(firstround_ranks.mean(axis=0))

    winner_firstround = np.zeros(shape=firstround_ranks.shape)
    winner_firstround[firstround_ranks==3] = 1

    #print(winner_firstround.mean(axis=0))

    secondroundrandom = t.rvs(size=(1, num_samples),df=12)

    secondround_logistic_share = 0.255688006 + (secondroundrandom*0.428517842)

    secondround_gain_share = 100*(1/(1+np.exp(-secondround_logistic_share)))

    #print(secondround_gain_share)
    #print(describe(secondround_gain_share,axis=1))

    losers_sum = 100-firstround[firstround_ranks==3]-firstround[firstround_ranks==2]

    firstround_winner_gain = secondround_gain_share*losers_sum/100

    firstround_second_gain = (100-secondround_gain_share)*losers_sum/100

    secondround = np.zeros(firstround_ranks.shape)

    first_secondround_share = firstround[firstround_ranks==3] + firstround_winner_gain
    second_secondround_share = firstround[firstround_ranks==2] + firstround_second_gain

    secondround[firstround_ranks==3] = first_secondround_share[0]
    secondround[firstround_ranks==2] = second_secondround_share[0]

    temp2 = secondround.argsort()
    secondround_ranks = np.arange(len(secondround))[temp2.argsort()]

    winner_secondround = np.zeros(shape=secondround_ranks.shape)
    winner_secondround[secondround_ranks==3] = 1

    #print(scenario_name)
    #print(firstround.mean(axis=0))
    #print(winner_secondround.mean(axis=0))

    firstround_RESULT = firstround.mean(axis=0)
    win_probability = winner_secondround.mean(axis=0)

    results = [scenario_name, incumbenteffect, firstround_RESULT, win_probability]

    concatenated = np.concatenate(results, axis=None)

    concatenated.shape = (1,10)

    return concatenated

    #secondround[firstround_ranks==2] = firstround[firstround_ranks==2] + firstround_second_gain

    #print(secondround)

columns = ["election", "incumbenteffect", "first_other", "lab", "con", "libdem", "winprob_other",
            "winprob_lab", "winprob_con", "winprob_libdem"]

scenarios2021 = ["cambridgeshirepeterborough2021", "greatermanchester2021",
                    "liverpool2021", "london2021", "teesvalley2021",
                    "westmidlands2021", "westofengland2021","westyorkshire2021"]

results_array = np.array([["election","incumbenteffect","first_other",
                            "lab","con","libdem","winprob_other","winprob_lab",
                            "winprob_con","winprob_libdem"]])

for scenario in scenarios2021:
    for i in range(150):
        if i >0:
            result = election_model(scenario,nationalpolling, incumbenteffect = i/10)
        else:
            result = election_model(scenario,nationalpolling, incumbenteffect = i)
        results_array = np.concatenate([results_array,result], axis=0)

results_df = pd.DataFrame(results_array, columns = columns)

results_df.to_csv("results.csv")
