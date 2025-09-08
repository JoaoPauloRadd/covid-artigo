# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 21:15:13 2020

@author: João Paulo Radd
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv, sys
import math as mt
#import plotly.graph_objs as go
#import plotly.express as px
from matplotlib import dates as mdates
from collections import Counter, OrderedDict
import datetime
import seaborn as sns

def somaNota(dataset, gabarito):
    notas= pd.DataFrame(columns=['t1', 't2'])
    soma=0
    soma2=0
    for ind in dataset.index:
        for x in range(1,11):
            if(dataset[str(x)][ind]==gabarito[x-1]):
                soma=soma+1        
        for x in range(11,21):
            if(dataset[str(x)][ind]==gabarito[x-1]):
                soma2=soma2+1
        notas=notas.append({'t1': soma, 't2': soma2}, ignore_index=True)

        soma=0
        soma2=0
    
    return notas


