# Modelling 2021 Metro Mayor elections in England

Modelling 2021 Metro Mayor elections in England

The model.py file includes a function (election_model) which takes the arguments scenario_name, nationalpolling and incumbenteffect.

Scenario name can be any of the following elections, entered as a string:

- cambridgeshirepeterborough2017
- cambridgeshirepeterborough2021
- greatermanchester2017
- greatermanchester2021
- london2000
- london2004
- london2008
- london2012
- london2016
- london2021
- liverpool2017
- liverpool2021
- northoftyne2019
- sheffield2018
- teesvalley2017
- teesvalley2021
- westmidlands2017
- westmidlands2021
- westofengland2017
- westofengland2021
- westyorkshire2021

National polling should be entered as a numpy array shape (3,1) with current national polling levels for Labour, the Conservatives and the Liberal Democrats (in that order).

The incumbent effect should be a float representing the effect of incumbency on that candidate's vote share.

