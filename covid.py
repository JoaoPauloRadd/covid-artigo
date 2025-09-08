# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 10:56:33 2020

@author: João Paulo Radd
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv, sys
import math as mt
from datetime import timedelta
#import plotly.graph_objs as go
#import plotly.express as px
from matplotlib import dates as mdates
from collections import Counter, OrderedDict
import datetime
import seaborn as sns
import statistics as stat
#import libcovid
from mpl_toolkits.mplot3d import axes3d
from scipy import stats
#from mapping import Column

#função que gera gráfico das notas
def plotNotas(notas):#para 10
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    soma = 0
    langs=[]
    qtdNotas=[]
    for x in range(1,11):
        langs.append(x)
        for ind in notas.index:
            if(notas[ind]==x):
                soma=soma+1
        qtdNotas.append(soma)
        soma=0
        
    print(langs)
    print(qtdNotas)
    ax.bar(langs,qtdNotas)
    plt.show()
    
#def plotNotas(notas):
#    fig = plt.figure()
#    ax = fig.add_axes([0,0,1,1])
#    soma = 0
#    langs=[]
#    qtdNotas=[]
#    for x in range(1,9):
#        langs.append(x)
#        for ind in notas.index:
#            if(notas[ind]==x):
#                soma=soma+1
#        qtdNotas.append(soma)
#        soma=0
#        
#    print(langs)
#    print(qtdNotas)
#    ax.bar(langs,qtdNotas)
#    plt.show()

#calculo de notas baseado em 10 qustões
def calcNota(dataset, gabarito):# para 10
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
        notas=notas.append({'t1': int(soma), 't2': int(soma2)}, ignore_index=True)

        soma=0
        soma2=0
    
    return notas    

#def calcNota(dataset, gabarito):
#    notas= pd.DataFrame(columns=['t1', 't2'])
#    soma=0
#    soma2=0
#    for ind in dataset.index:
#        for x in range(1,9):
#            if(dataset[str(x)][ind]==gabarito[x-1]):
#                soma=soma+1        
#        for x in range(9,17):
#            if(dataset[str(x)][ind]==gabarito[x-1]):
#                soma2=soma2+1
#        notas=notas.append({'t1': int(soma), 't2': int(soma2)}, ignore_index=True)
#
#        soma=0
#        soma2=0
#    
#    return notas 

#calculo da diferença de notas entre t1 e t2
def varNotas(notas):
    varN = pd.DataFrame(columns=['var','ind'])
    for ind in notas.index:
        if temNivelConh(ind):
            varN= varN.append({'var':float(notas['t2'][ind]-notas['t1'][ind]),
                               'ind':ind}, ignore_index=True)
    return varN


#calcula o conjunto de tempo gasto da(s) atividade(s) onde hi/hf sao as colunas
def calcDeltaTime(dataset, hi, hf, nomeAtividade):
    tempo = pd.DataFrame(columns=[nomeAtividade])
    t1 = timedelta(hours=0, minutes=0)
    t2 = timedelta(hours=0, minutes=0)
    deltaT = timedelta(hours=0, minutes=0)
    t=[]
    for ind in dataset.index:
        t = dataset[hi][ind].split(":")
#        print(t)
        t1 = timedelta(hours=int(t[0]), minutes=int(t[1]))
        t = dataset[hf][ind].split(":")
        t2 = timedelta(hours=int(t[0]), minutes=int(t[1]))
        deltaT = t2-t1
        tempo=tempo.append({nomeAtividade: (deltaT.seconds/60)}, ignore_index=True)
    return tempo

#função para remover outlier (não funciona e não sei pq, mais facil fazer o drop inline)
def removeOutliers(data, outliers):
    data.drop(outliers['out'])
    return data

    
#salva na estrutura de outliers o id do outlier 
def setOutlier(outliers, i):
    for ind in outliers.index:
        if outliers['out'][ind]==i:
            return outliers
    outliers=outliers.append({'out': int(i)}, ignore_index=True)
    return outliers

#encontra outliers baseados na variancia
def findOutlier(data, col, outliers):
    top = stat.mean(data[col]) + stat.variance(data[col])
    button = stat.mean(data[col]) - stat.variance(data[col])
    for ind in data.index:
        if (data[col][ind]<button or data[col][ind]>top):
            outliers=setOutlier(outliers,int(ind))
    return outliers

#encontra outliers baseado no desvio padrão   
def findOutlierByDSV(data, col, outliers):
    top = stat.mean(data[col]) + stat.stdev(data[col])
    button = stat.mean(data[col]) - stat.stdev(data[col])
    for ind in data.index:
        if (data[col][ind]<button or data[col][ind]>top):
            outliers=setOutlier(outliers,int(ind))
    return outliers 


#função que procura outliers para o tempo de pesquisa
def findOutlierPesquisa(data, col, outliers):
    top = stat.mean(data[col]) + 32
    button = stat.mean(data[col]) - stat.stdev(data[col])
    for ind in data.index:
        if (data[col][ind]<button or data[col][ind]>top):
            outliers=setOutlier(outliers,int(ind))
    return outliers    
    
#substitui os 0s que se referiam ao conhecimento que não mudou e alocou a nota de conhecmiento anterior
def normalizanConhecimento(dataset):
    nConhecimento = pd.DataFrame(columns=['nConhecimento1',
                                          'nConhecimento2',
                                          'nConhecimento3',
                                          'nConhecimento4', ])
    nC2aux=0
    for ind in dataset.index:
        if dataset['nConhecimento2'][ind]==0:
            nC2aux=dataset['nConhecimento1'][ind]
            dataset['nConhecimento2'][ind]=nC2aux
        if dataset['nConhecimento3'][ind]==0:
            dataset['nConhecimento3'][ind]=dataset['nConhecimento2'][ind]
        nConhecimento=nConhecimento.append({'nConhecimento1':dataset['nConhecimento1'][ind],
                                          'nConhecimento2':dataset['nConhecimento2'][ind],
                                          'nConhecimento3':dataset['nConhecimento3'][ind],
                                          'nConhecimento4':dataset['nConhecimento4'][ind]},ignore_index=True)
    return nConhecimento

#girando tabela de conhecimento 
def inverteTabela(data):
    col=[]
    newData= pd.DataFrame()
    for ind in data.index:
#        print(ind, dataset['nConhecimento1'][ind],
#              dataset['nConhecimento2'][ind],
#              dataset['nConhecimento3'][ind],
#              dataset['nConhecimento4'][ind])
        col=[dataset['nConhecimento1'][ind],
             dataset['nConhecimento2'][ind],
             dataset['nConhecimento3'][ind],
             dataset['nConhecimento4'][ind]]
        newData[str(ind)]=col
        col=[]
    return newData

#função que conta termos
def getQntTermos(termos):
    qntTermos=pd.DataFrame(columns=["nTermos","nPalavras","index"])
    qntT=0
    qntP=0
    for ind in termos.index:
        q=termos[ind].split(";")
        qntT=len(q)
        for i in range(0,qntT):
            p=q[i].split(" ")
            qntP=qntP+len(p)
#        p=termos[ind].split(" ")
#        qntP=len(p)
        if temNivelConh(ind):
            qntTermos=qntTermos.append({"nTermos":qntT,"nPalavras":qntP,"index":ind},ignore_index=True)
        qntP=0
    return qntTermos
        
#função auxiliar para saber qual termos pertence a base original pelo index
def getPosByIndexTermos(index, data):
    for ind in data.index:
        if data['index'][ind]==index:
            return ind
        
#função auxiliar para saber qual termos pertence a base original pelo index
def getPosByIndexVar(index, data):
    for ind in data.index:
        if data['ind'][ind]==index:
            return ind
#função que fez parte de testes de conjuntos
def temNivelConh(ind):
    return True
    if nConhecimento['nConhecimento3'][ind]!=0:
        return True
    return False
    
#função para ver quantas recorências existem de um termo
def recTermos(termosBusca, termo):
    c=0
    for ind in termosBusca.index:
        string=termosBusca[ind].lower()
        if termo.lower() in string:
            c=c+1
    return c



#def medTeste(notas):
#    soma=0
#    for ind in notas.index:
#        soma=soma+notas[ind]
#    return soma/notas.size
    #mesma coisa q o mean()

#############################################################################
########################CODE##############################
#############################################################################

######################coleta de dados / tratamento


dataCOVID = "covidUTF8-10q.csv"
#separador = ","
#encoding = "cp860"
dataset = pd.read_csv(dataCOVID)
#print(dataset)
#gab p 10
gabarito = ['b','d','e','b','e','b','a','c','c','e','b','a','d','d','e','b','e','c','e','d']
#gabarito = ['b','d','e','b','e','b','c','e','b','d','d','e','b','e','e','d']
notas = calcNota(dataset, gabarito)
#print(notas)
temposT1= calcDeltaTime(dataset,"hit1", "hft1", "t1")
temposTp= calcDeltaTime(dataset,"hiP", "hfP", "tp")
temposT2= calcDeltaTime(dataset,"hiT2", "hfT2", "t2")
temposTT= calcDeltaTime(dataset,"hit1", "hfT2", "tt")
nConhecimento = normalizanConhecimento(dataset)





#### Relação saude/nsaude antes dos outliers

saude= pd.DataFrame(columns=['t1','t2'])
tSAUDE=[0]*9
cSAUDE=0
nsaude= pd.DataFrame(columns=['t1','t2'])
tNSAUDE=[0]*79
cNSAUDE=0

for ind in dataset.index:
    if dataset['trabalhasaude'][ind]==1:
        saude=saude.append({'t1':notas['t1'][ind],'t2':notas['t2'][ind]}, ignore_index=True)
    else:
        nsaude=nsaude.append({'t1':notas['t1'][ind],'t2':notas['t2'][ind]}, ignore_index=True)


comp=pd.DataFrame(columns=['st1','st2','nst1','nst2'])
comp['nst1']=nsaude['t1']
comp['nst2']=nsaude['t2']
comp['st1']=saude['t1']
comp['st2']=saude['t2']
comp.plot.box()





















#######################tratamento outliers

outliers=pd.DataFrame()
outliers.insert(0, "out", [], True)
outliers=findOutlier(notas, 't1',outliers)
print("outlist(t1):",outliers.size)
outliers=findOutlier(notas, 't2',outliers)
print("outlist(t1+t2):",outliers.size)
outliers=findOutlier(temposT1, 't1',outliers)
print("outlist(notas+tempot1):",outliers.size)
outliers=findOutlierPesquisa(temposTp, 'tp',outliers)
print("outlist(notas+tempot1 e tp):",outliers.size)
#outliers=findOutlierByDSV(temposT2, 't2',outliers)
#print("outlist(notas+tempot1+tp+t2):",outliers.size)


dataset= dataset.drop(outliers['out'])
notas= notas.drop(outliers['out'])
temposT1= temposT1.drop(outliers['out'])
temposTp= temposTp.drop(outliers['out'])
temposT2= temposT2.drop(outliers['out'])
temposTT= temposTT.drop(outliers['out'])
nConhecimento = nConhecimento.drop(outliers['out'])

varN = varNotas(notas)



###################### manipulacçãp e resultados

#nConhecimentoInv = inverteTabela(nConhecimento)

print("Média t1:",stat.mean(notas['t1']))
print("Mediana t1:",stat.median(notas['t1']))
print("Variância t1:",stat.variance(notas['t1']))
print("Desvio t1:",stat.stdev(notas['t1']))
print("----------")
print("Média t2:",stat.mean(notas['t2']))
print("Mediana t2:",stat.median(notas['t2']))
print("Variância t2:",stat.variance(notas['t2']))
print("Desvio t2:",stat.stdev(notas['t2']))







plotNotas(notas['t1'])
plotNotas(notas['t2'])
notas.plot.box(vert=False, figsize=(6,3),
               grid=True, positions=[2,1],
               title="Distribuição de notas nos testes")

#print(temposT1)
#print(temposTp)
#print(temposT2)
#
#rel = pd.DataFrame(columns=['tempoDeEstudo','NotasT2'])
#rel['tempoDeEstudo']=temposTp['tp']
#rel['NotasT2']=notas['t2']
#rel.plot.scatter(x='NotasT2', y='tempoDeEstudo')



#
tt=pd.DataFrame(columns=['tt'])
for ind in temposTT.index:
    tt=tt.append({'tt':temposTT['tt'][ind]}, ignore_index=True)
rel = pd.DataFrame()
rel.insert(0, "tempoTotal", temposTT['tt'], True)
rel.insert(1, "Var", varN['var'], True)
rel.plot.scatter(x='Var', y='tempoTotal',c='DarkBlue')
#
termosBusca=dataset["termosBusca"]
qntTermos=getQntTermos(termosBusca)

nq=qntTermos.sort_values(by=['nTermos'])
mT=[0]*90
c=0
auxc=1
auxmQxT=0
for ind in nq.index:
    i=nq['index'][ind]
    if c==nq['nTermos'][ind] and temposTp['tp'][i]!=0:
        
        auxmQxT=auxmQxT+(temposTp['tp'][i])
        auxc=auxc+1
    elif temposTp['tp'][i]!=0:
        mT[c]=auxmQxT/auxc
        c=nq['nTermos'][ind]
        auxc=1
        auxmQxT=auxmQxT+(temposTp['tp'][i])
        auxc=auxc+1
#
mT[c]=auxmQxT/auxc
c=0
        
tpesq=pd.DataFrame(columns=['tp'])
for ind in temposTp.index:
    if temposTp['tp'][ind]==0:
        i=getPosByIndexTermos(ind,nq)
        temposTp['tp'][ind]=mT[nq['nTermos'][i]]
    tpesq=tpesq.append({'tp':temposTp['tp'][ind]}, ignore_index=True)

rel2 = pd.DataFrame()
rel2.insert(0, "tempoDeEstudo", tpesq['tp'], True)
rel2.insert(1, "var", varN['var'], True)
rel2.plot.scatter(x='var', y='tempoDeEstudo',c='DarkBlue')



################################################################################
#########################Dunnig-kruger Effect para 10questões
################################################################################


n1=notas.sort_values(by=['t1'])
qtN1=[0] * 7
c=0
m=0
aux1=[0] * 7
dp1=[0] * 15
c3=0
for ind in n1.index:
    dp1[c3]=n1['t1'][ind]*10
    c=c+1
    c3=c3+1
    m=m+n1['t1'][ind]*10
    if c==1:
        aux1[0]=ind
    if c==15:
        qtN1[1]=m/15
        print("Desvio (real) ponto 1:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        m=0
        aux1[1]=ind
    if c==31:
        qtN1[2]=m/16
        print("Desvio (real) ponto 2:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        m=0
        aux1[2]=ind
    if c==47:
        qtN1[3]=m/16
        print("Desvio (real) ponto 3:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        m=0
        aux1[3]=ind
    if c==63:
        qtN1[4]=m/16
        print("Desvio (real) ponto 4:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        m=0
        aux1[4]=ind
    if c==79:
        qtN1[5]=m/16
        print("Desvio (real) ponto 5:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        m=0
        aux1[5]=ind
    if c==95:
        qtN1[6]=m/16
        print("Desvio (real) ponto 6:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        m=0
        aux1[6]=ind
c=0


mix =[0] * 7
c=0
c2=0
c3=0
dp1=[0] * 15

for ind in n1.index:
    dp1[c3]=(nConhecimento['nConhecimento2'][ind]*2)
    c=c+1
    c3=c3+1
    if c==1:
        mix[0]=nConhecimento['nConhecimento2'].min()*20
    c2=c2+(nConhecimento['nConhecimento2'][ind]*2)
    
    if c==15:
        mix[1]=((c2/15)*10)
        print("Desvio ponto 1:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        c2=0
#        aux1[1]=ind
    if c==31:
        mix[2]=((c2/16)*10)
        print("Desvio ponto 2:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        c2=0
#        aux1[2]=ind
    if c==47:
        mix[3]=((c2/16)*10)
        print("Desvio ponto 3:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        c2=0
#        aux1[3]=ind
    if c==63:
        mix[4]=((c2/16)*10)
        print("Desvio ponto 4:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        c2=0
#        aux1[4]=ind
    if c==79:
        mix[5]=((c2/16)*10)
        print("Desvio ponto 5:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        c2=0
#        aux1[5]=ind
    if c==95:
        mix[6]=((c2/16)*10)
        print("Desvio ponto 6:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        c2=0
#        aux1[6]=ind



v11=[0]*6
v12=[0]*6
for i in range(0,6):
    v11[i]=qtN1[i+1]
    v12[i]=mix[i+1]


DK1 = pd.DataFrame()
DK1['notas t1']=v11
DK1['estimado']=v12
ax=DK1.plot(xticks=DK1.index,grid=True)
ax.set_xticklabels([1,2,3,4,5,6])



n2=notas.sort_values(by=['t2'])
qtN2=[0] * 7
#DK1=
c=0
c3=0
dp1=[0] * 15
aux2=[0] * 7
m=0
for ind in n2.index:
    dp1[c3]=n2['t2'][ind]*10
    c3=c3+1
    c=c+1
    m=m+n2['t2'][ind]*10
    if c==1:
        aux2[0]=ind
    if c==15:
        qtN2[1]=m/15
        print("Desvio (real2) ponto 1:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        m=0
        aux2[1]=ind
    if c==31:
        qtN2[2]=m/16
        print("Desvio (real2) ponto 2:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        m=0
        aux2[2]=ind
    if c==47:
        qtN2[3]=m/16
        print("Desvio (real2) ponto 3:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        m=0
        aux2[3]=ind
    if c==63:
        qtN2[4]=m/16
        print("Desvio (real2) ponto 4:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        m=0
        aux2[4]=ind
    if c==79:
        qtN2[5]=m/16
        print("Desvio (real2) ponto 5:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        m=0
        aux2[5]=ind
    if c==95:
        qtN2[6]=m/16
        print("Desvio (real2) ponto 6:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        m=0
        aux2[6]=ind
c=0

mix2 =[0] * 7
c=0
c2=0
c3=0
dp1=[0] * 15

for ind in n2.index:
    dp1[c3]=(nConhecimento['nConhecimento4'][ind]*2)
    c=c+1
    c3=c3+1
    if c==1:
        mix2[0]=nConhecimento['nConhecimento4'].min()*20
    c2=c2+(nConhecimento['nConhecimento4'][ind]*2)
    
    if c==15:
        mix2[1]=((c2/15)*10)
        print("Desvio ponto 1:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        c2=0
#        aux1[1]=ind
    if c==31:
        mix2[2]=((c2/16)*10)
        print("Desvio 2 ponto 2:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        c2=0
#        aux1[2]=ind
    if c==47:
        mix2[3]=((c2/16)*10)
        print("Desvio 2 ponto 3:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        c2=0
#        aux1[3]=ind
    if c==63:
        mix2[4]=((c2/16)*10)
        print("Desvio 2 ponto 4:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        c2=0
#        aux1[4]=ind
    if c==79:
        mix2[5]=((c2/16)*10)
        print("Desvio 2 ponto 5:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        c2=0
#        aux1[5]=ind
    if c==95:
        mix2[6]=((c2/16)*10)
        print("Desvio 2 ponto 6:",stat.stdev(dp1))
        c3=0
        dp1=[0] * 16
        c2=0
#        aux1[6]=ind





v21=[0]*6
v22=[0]*6
for i in range(0,6):
    v21[i]=qtN2[i+1]
    v22[i]=mix2[i+1]


DK2 = pd.DataFrame()
DK2['notas t2']=v21
DK2['estimado']=v22
ax=DK2.plot(xticks=DK2.index,grid=True)
ax.set_xticklabels([1,2,3,4,5,6])


print("Média t1:",stat.mean(notas['t1']))
print("Desvio t1:",stat.stdev(notas['t1']))
print("Média expectativa pós t1:",stat.mean(nConhecimento['nConhecimento2'])*2)
print("Desvio expectativa pós t1:",stat.stdev(nConhecimento['nConhecimento2'])*2)
print("Média t2:",stat.mean(notas['t2']))
print("Desvio t1:",stat.stdev(notas['t2']))
print("Média expectativa pós t2:",stat.mean(nConhecimento['nConhecimento4'])*2)
print("Desvio expectativa pós t2:",stat.stdev(nConhecimento['nConhecimento4'])*2)

print("Média estimativa1:",stat.mean(v12))
print("Desvio estimativa1:",stat.stdev(v12))
print("Média estimativa2:",stat.mean(v22))
print("Desvio estimativa2:",stat.stdev(v22))



###############################################################################
########################Dunnig-kruger Effect para 8questões
###############################################################################
#
#
#n1=notas.sort_values(by=['t1'])
#qtN1=[0] * 7
#c=0
#m=0
#aux1=[0] * 7
#dp1=[0] * 15
#c3=0
#for ind in n1.index:
#    dp1[c3]=(n1['t1'][ind]) * 100/8
#    c=c+1
#    c3=c3+1
#    m=m+n1['t1'][ind]*100/8
#    if c==1:
#        aux1[0]=ind
#    if c==15:
#        qtN1[1]=m/15
#        print("Desvio (real) ponto 1:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        m=0
#        aux1[1]=ind
#    if c==30:
#        qtN1[2]=m/15
#        print("Desvio (real) ponto 2:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        m=0
#        aux1[2]=ind
#    if c==45:
#        qtN1[3]=m/15
#        print("Desvio (real) ponto 3:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        m=0
#        aux1[3]=ind
#    if c==60:
#        qtN1[4]=m/15
#        print("Desvio (real) ponto 4:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        m=0
#        aux1[4]=ind
#    if c==75:
#        qtN1[5]=m/15
#        print("Desvio (real) ponto 5:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        m=0
#        aux1[5]=ind
#    if c==90:
#        qtN1[6]=m/15
#        print("Desvio (real) ponto 6:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        m=0
#        aux1[6]=ind
#c=0
#
#
#mix =[0] * 7
#c=0
#c2=0
#c3=0
#dp1=[0] * 15
#
#for ind in n1.index:
#    dp1[c3]=(nConhecimento['nConhecimento2'][ind]*2)
#    c=c+1
#    c3=c3+1
#    if c==1:
#        mix[0]=nConhecimento['nConhecimento2'].min()*20
#    c2=c2+(nConhecimento['nConhecimento2'][ind]*2)
#    
#    if c==15:
#        mix[1]=((c2/15)*10)
#        print("Desvio ponto 1:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        c2=0
##        aux1[1]=ind
#    if c==30:
#        mix[2]=((c2/15)*10)
#        print("Desvio ponto 2:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        c2=0
##        aux1[2]=ind
#    if c==45:
#        mix[3]=((c2/15)*10)
#        print("Desvio ponto 3:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        c2=0
##        aux1[3]=ind
#    if c==60:
#        mix[4]=((c2/15)*10)
#        print("Desvio ponto 4:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        c2=0
##        aux1[4]=ind
#    if c==75:
#        mix[5]=((c2/15)*10)
#        print("Desvio ponto 5:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        c2=0
##        aux1[5]=ind
#    if c==90:
#        mix[6]=((c2/15)*10)
#        print("Desvio ponto 6:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        c2=0
##        aux1[6]=ind
#
#
#
#v11=[0]*6
#v12=[0]*6
#for i in range(0,6):
#    v11[i]=qtN1[i+1]
#    v12[i]=mix[i+1]
#
#
#DK1 = pd.DataFrame()
#DK1['notas t1']=v11
#DK1['estimado']=v12
#ax=DK1.plot(xticks=DK1.index,grid=True)
#ax.set_xticklabels([1,2,3,4,5,6])
#
#
#
#n2=notas.sort_values(by=['t2'])
#qtN2=[0] * 7
##DK1=
#c=0
#c3=0
#dp1=[0] * 15
#aux2=[0] * 7
#m=0
#for ind in n2.index:
#    dp1[c3]=n2['t2'][ind]*100/8
#    c3=c3+1
#    c=c+1
#    m=m+n2['t2'][ind]*100/8
#    if c==1:
#        aux2[0]=ind
#    if c==15:
#        qtN2[1]=m/15
#        print("Desvio (real2) ponto 1:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        m=0
#        aux2[1]=ind
#    if c==30:
#        qtN2[2]=m/15
#        print("Desvio (real2) ponto 2:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        m=0
#        aux2[2]=ind
#    if c==45:
#        qtN2[3]=m/15
#        print("Desvio (real2) ponto 3:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        m=0
#        aux2[3]=ind
#    if c==60:
#        qtN2[4]=m/15
#        print("Desvio (real2) ponto 4:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        m=0
#        aux2[4]=ind
#    if c==75:
#        qtN2[5]=m/15
#        print("Desvio (real2) ponto 5:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        m=0
#        aux2[5]=ind
#    if c==90:
#        qtN2[6]=m/15
#        print("Desvio (real2) ponto 6:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        m=0
#        aux2[6]=ind
#c=0
#
#mix2 =[0] * 7
#c=0
#c2=0
#c3=0
#dp1=[0] * 15
#
#for ind in n2.index:
#    dp1[c3]=(nConhecimento['nConhecimento4'][ind]*2)
#    c=c+1
#    c3=c3+1
#    if c==1:
#        mix2[0]=nConhecimento['nConhecimento4'].min()*20
#    c2=c2+(nConhecimento['nConhecimento4'][ind]*2)
#    
#    if c==15:
#        mix2[1]=((c2/15)*10)
#        print("Desvio ponto 1:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        c2=0
##        aux1[1]=ind
#    if c==30:
#        mix2[2]=((c2/15)*10)
#        print("Desvio 2 ponto 2:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        c2=0
##        aux1[2]=ind
#    if c==45:
#        mix2[3]=((c2/15)*10)
#        print("Desvio 2 ponto 3:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        c2=0
##        aux1[3]=ind
#    if c==60:
#        mix2[4]=((c2/15)*10)
#        print("Desvio 2 ponto 4:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        c2=0
##        aux1[4]=ind
#    if c==75:
#        mix2[5]=((c2/15)*10)
#        print("Desvio 2 ponto 5:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        c2=0
##        aux1[5]=ind
#    if c==90:
#        mix2[6]=((c2/15)*10)
#        print("Desvio 2 ponto 6:",stat.stdev(dp1))
#        c3=0
#        dp1=[0] * 15
#        c2=0
##        aux1[6]=ind
#
#
#
#
#
#v21=[0]*6
#v22=[0]*6
#for i in range(0,6):
#    v21[i]=qtN2[i+1]
#    v22[i]=mix2[i+1]
#
#
#DK2 = pd.DataFrame()
#DK2['notas t2']=v21
#DK2['estimado']=v22
#ax=DK2.plot(xticks=DK2.index,grid=True)
#ax.set_xticklabels([1,2,3,4,5,6])
#
#
#print("Média t1:",stat.mean(notas['t1']))
#print("Desvio t1:",stat.stdev(notas['t1']))
#print("Média expectativa pós t1:",stat.mean(nConhecimento['nConhecimento2'])*2)
#print("Desvio expectativa pós t1:",stat.stdev(nConhecimento['nConhecimento2'])*2)
#print("Média t2:",stat.mean(notas['t2']))
#print("Desvio t1:",stat.stdev(notas['t2']))
#print("Média expectativa pós t2:",stat.mean(nConhecimento['nConhecimento4'])*2)
#print("Desvio expectativa pós t1:",stat.stdev(nConhecimento['nConhecimento4'])*2)
#
#print("Média estimativa1:",stat.mean(v12))
#print("Desvio estimativa1:",stat.stdev(v12))
#print("Média estimativa2:",stat.mean(v22))
#print("Desvio estimativa2:",stat.stdev(v22))





#################################Tratando termos de busca



cCOVID=recTermos(termosBusca, "covid")
cCORONA=recTermos(termosBusca, "corona")
cSINTOMAS=recTermos(termosBusca, "sintomas")
cFAKE=recTermos(termosBusca, "fake")
cREMEDIO=recTermos(termosBusca, "REMEDIO")
cMEDICAMENTO=recTermos(termosBusca, "MEDICAMENTO")
cVACINA=recTermos(termosBusca, "vacina")
cMR=cMEDICAMENTO+cREMEDIO
cTRATAMENTO=recTermos(termosBusca, "TRATAMENTO")
cMortes=recTermos(termosBusca, "mort")
cOMS=recTermos(termosBusca, "oms")
cMinisterio=recTermos(termosBusca, "ministerio")
cEUA=recTermos(termosBusca, "eua")
cunidos=recTermos(termosBusca, "unidos")
cCHINA=recTermos(termosBusca, "china")


print("Recorrencia de termos entre os usuários (quantos usaram essas palavras) ")
print("termo covid: ",cCOVID)
print("termo corona: ",cCORONA)
print("termo sintomas: ",cSINTOMAS)
print("termo fake: ",cFAKE)
print("termo remedio: ",cREMEDIO)
print("termo medicamento: ",cMEDICAMENTO)
print("termo vacina: ",cVACINA)
print("termo EUA: ",cEUA)
print("termo Estados Unidos: ",cunidos)
print("termo China: ",cCHINA)
print("termo tratamento: ",cTRATAMENTO)
print("termo relacionados a morte: ",cMortes)
print("termo oms: ",cOMS)
print("termo ministerio(da saude): ",cMinisterio)




tp =tpesq.sort_values(by=['tp'])
v=varN.sort_values(by=['var'])
auxtp=[0]*95
auxnp=[0]*95
auxnt=[0]*95
auxvar=[0]*95
auxQxT=[0]*95

c=0
for ind in v.index:
    auxtp[c]=tpesq['tp'][ind]
    auxnp[c]=qntTermos['nPalavras'][ind]
    auxnt[c]=qntTermos['nTermos'][ind]
    auxvar[c]=varN['var'][ind]
    auxQxT[c]=auxnp[c]/auxtp[c]
#    print(auxnp[c],"---", auxtp[c],"---", auxQxT[c])
    c=c+1






graf=pd.DataFrame()
graf['nT']=auxnt
graf['nP']=auxnp
graf['var']=auxvar
graf['tp']=auxtp
graf['QxT']=auxQxT

graf=pd.DataFrame()
graf['tp']=auxtp
graf['var']=auxvar

################################################################################
#####################Relação especialistas
################################################################################

saude= pd.DataFrame(columns=['t1','t2','ind'])
tSAUDE=[0]*12
cSAUDE=0
tempoSAUDE=[0]*12
varSAUDE=[0]*12
termosSaude=[0]*12
nsaude= pd.DataFrame(columns=['t1','t2','ind'])
tNSAUDE=[0]*83
cNSAUDE=0
tempoNSAUDE=[0]*83
varNSAUDE=[0]*83
termosNSaude=[0]*83

for ind in dataset.index:
    if dataset['trabalhasaude'][ind]==1:
        pos=getPosByIndexTermos(ind,qntTermos)
        tSAUDE[cSAUDE]=qntTermos['nTermos'][pos]
        tempoSAUDE[cSAUDE]=tpesq['tp'][pos]
        varSAUDE[cSAUDE]=varN['var'][pos]
        termosSaude[cSAUDE]=termosBusca[ind]
        cSAUDE=cSAUDE+1
        saude=saude.append({'t1':notas['t1'][ind],'t2':notas['t2'][ind]}, ignore_index=True)
        
    else:
        pos=getPosByIndexTermos(ind,qntTermos)
        tNSAUDE[cNSAUDE]=qntTermos['nTermos'][pos]
        tempoNSAUDE[cNSAUDE]=tpesq['tp'][pos]
        varNSAUDE[cNSAUDE]=varN['var'][pos]
        termosNSaude[cNSAUDE]=termosBusca[ind]
        cNSAUDE=cNSAUDE+1
        nsaude=nsaude.append({'t1':notas['t1'][ind],'t2':notas['t2'][ind]}, ignore_index=True)


comp=pd.DataFrame(columns=['st1','st2','nst1','nst2'])
comp['nst1']=nsaude['t1']
comp['nst2']=nsaude['t2']
comp['st1']=saude['t1']
comp['st2']=saude['t2']
comp.plot.box()

print("Media/stdev de termos por especialista: ",stat.mean(tSAUDE),"/",stat.stdev(tSAUDE))
print("Media/stdev de termos por não especialista: ",stat.mean(tNSAUDE),"/",stat.stdev(tNSAUDE))


#rel3 = pd.DataFrame()
#
#
#
#
#
#rel3.insert(0, "tempoDeEstudo", tpesq['tp'], True)
#rel3.insert(1, "var", varN['var'], True)
#rel3.plot.scatter(x='var', y='tempoDeEstudo',c='DarkBlue')



################################################################################
################################################################################

hashTermos= pd.DataFrame(columns=['t','n'])

#
for ind in varN.index:
    if varN['var'][ind]>0:
        i=varN['ind'][ind]
        q=termosBusca[i].lower().split(';')
        for j in range(0,len(q)):
            if q[j]=="": print(i)
            t=hashTermos['t'].loc[hashTermos['t'] == q[j]]
            if t.index.size > 0:
                r=0
                r=hashTermos['n'][t.index[0]]
                hashTermos['n'][t.index[0]]=r+1
            else:
                hashTermos=hashTermos.append({'t':q[j],
                                              'n':1},
                                              ignore_index=True)



#for i in hashTermos.index: 
#    print(hashTermos['t'][i],": ",hashTermos['n'][i])



hashTermosR= pd.DataFrame(columns=['t','n'])

#
for ind in varN.index:
    if varN['var'][ind]<1:
        i=varN['ind'][ind]
        q=termosBusca[i].lower().split(';')
        for j in range(0,len(q)):
            if q[j]=="": print(i)
            t=hashTermosR['t'].loc[hashTermosR['t'] == q[j]]
            if t.index.size > 0:
                r=0
                r=hashTermosR['n'][t.index[0]]
                hashTermosR['n'][t.index[0]]=r+1
            else:
                hashTermosR=hashTermosR.append({'t':q[j],
                                              'n':1},
                                              ignore_index=True)

#print("TERMOS DO POVO Q PIOROU")
#
#for i in hashTermosR.index: 
#    print(hashTermosR['t'][i],": ",hashTermosR['n'][i])

#################################################################################
#################################################################################

midiaBusca=dataset['tdemidia']


hashM= pd.DataFrame(columns=['t','n'])
hashMB= pd.DataFrame(columns=['t','n'])
hashMR= pd.DataFrame(columns=['t','n'])
ct=0
cb=0
cr=0
#
for ind in varN.index:
    if varN['var'][ind]<1:
        cr=cr+1
        i=varN['ind'][ind]
        q=midiaBusca[i].lower().split('.')
        for j in range(0,len(q)):
            if q[j]=="": print(i)
            t=hashMR['t'].loc[hashMR['t'] == q[j]]
            if t.index.size > 0:
                r=0
                r=hashMR['n'][t.index[0]]
                hashMR['n'][t.index[0]]=r+1
            else:
                hashMR=hashMR.append({'t':q[j],
                                      'n':1}, ignore_index=True)
    else:
        cb=cb+1
        i=varN['ind'][ind]
        q=midiaBusca[i].lower().split('.')
        for j in range(0,len(q)):
            if q[j]=="": print(i)
            t=hashMB['t'].loc[hashMB['t'] == q[j]]
            if t.index.size > 0:
                r=0
                r=hashMB['n'][t.index[0]]
                hashMB['n'][t.index[0]]=r+1
            else:
                hashMB=hashMB.append({'t':q[j],
                                      'n':1}, ignore_index=True)
    ct=ct+1
    for j in range(0,len(q)):
        if q[j]=="": print(i)
        t=hashM['t'].loc[hashM['t'] == q[j]]
        if t.index.size > 0:
            r=0
            r=hashM['n'][t.index[0]]
            hashM['n'][t.index[0]]=r+1
        else:
            hashM=hashM.append({'t':q[j],
                                  'n':1}, ignore_index=True)


for ind in hashMB.index:
    hashMB['n'][ind]=hashMB['n'][ind]*100/cb
for ind in hashM.index:
    hashM['n'][ind]=hashM['n'][ind]*100/ct
for ind in hashMR.index:
    hashMR['n'][ind]=hashMR['n'][ind]*100/cr





h=hashM.sort_values(by=['n'])
h.plot.barh(x='t', y='n', rot=0)

hB=hashMB.sort_values(by=['n'])
hB.plot.barh(x='t', y='n', rot=0)

hR=hashMR.sort_values(by=['n'])
hR.plot.barh(x='t', y='n', rot=0)


prior = dataset['priorM']
b=pd.DataFrame(columns=['v','ind'])
r=pd.DataFrame(columns=['v','ind'])

for ind in prior.index:
    aux=prior[ind].split(";")
    if aux[0]=='3':
        t=getPosByIndexVar(ind,varN)
        if varN['var'][t]<1:
            r=r.append({'v':varN['var'][t],
                        'ind':ind}, ignore_index=True)
        else:
            b=b.append({'v':varN['var'][t],
                        'ind':ind}, ignore_index=True)

                        



b=pd.DataFrame(columns=['v','ind'])
r=pd.DataFrame(columns=['v','ind'])

for ind in prior.index:
    if '3' in prior[ind]:
        t=getPosByIndexVar(ind,varN)
        if varN['var'][t]<1:
            r=r.append({'v':varN['var'][t],
                        'ind':ind}, ignore_index=True)
        else:
            b=b.append({'v':varN['var'][t],
                        'ind':ind}, ignore_index=True)



#xpBB
confiabilidade=dataset['xpBB']
bb=pd.DataFrame(columns=['v','ind'])
rb=pd.DataFrame(columns=['v','ind'])
br=pd.DataFrame(columns=['v','ind'])
rr=pd.DataFrame(columns=['v','ind'])

for ind in confiabilidade.index:
    t=getPosByIndexVar(ind,varN)
    if varN['var'][t]<1 and confiabilidade[ind]==1:
        rb=rb.append({'v':varN['var'][t],
                    'ind':ind}, ignore_index=True)
    elif varN['var'][t]>0 and confiabilidade[ind]==1:
        bb=bb.append({'v':varN['var'][t],
                    'ind':ind}, ignore_index=True)
    elif varN['var'][t]<1 and confiabilidade[ind]==0:
        rr=rr.append({'v':varN['var'][t],
                    'ind':ind}, ignore_index=True)
    elif varN['var'][t]>0 and confiabilidade[ind]==0:
        br=br.append({'v':varN['var'][t],
                    'ind':ind}, ignore_index=True)





escolar=dataset['escolaridade']
hashescolar= pd.DataFrame(columns=['e','n'])

for ind in escolar.index:
    q=escolar[ind].lower()
    
    t=hashescolar['e'].loc[hashescolar['e'] == q]
    if t.index.size > 0:
        r=0
        r=hashescolar['n'][t.index[0]]
        hashescolar['n'][t.index[0]]=r+1
    else:
        hashescolar=hashescolar.append({'e':q,
                                        'n':1},
                    ignore_index=True)







for ind in hashescolar.index:
    hashescolar['n'][ind]=hashescolar['n'][ind]*100/ct

h=hashescolar.sort_values(by=['n'])
h.plot.barh(x='e', y='n', rot=0)



idade=dataset['idade']
hashidade= pd.DataFrame(columns=['e','n'])

for ind in idade.index:
    q=str(idade[ind])
    
    t=hashidade['e'].loc[hashidade['e'] == int(q)]
    if t.index.size > 0:
        r=0
        r=hashidade['n'][t.index[0]]
        hashidade['n'][t.index[0]]=r+1
    else:
        hashidade=hashidade.append({'e':int(q),
                                        'n':1},
                    ignore_index=True)







for ind in hashidade.index:
    hashidade['n'][ind]=hashidade['n'][ind]*100/ct

h=hashidade.sort_values(by=['e'])
h.plot.barh(x='e', y='n', rot=0)
h.plot.box(x='n', y='e', rot=45, vert=False, 
           figsize=(5,2), title="Distribuição de idade", grid=True)


print("Pearson e Spearman",
      graf.tp.corr(graf['var'], method="pearson"),
      graf.tp.corr(graf['var'], method="spearman"),
      stats.spearmanr(graf['tp'],graf['var']))



hashTermosSaude= pd.DataFrame(columns=['t','n'])

#
for ind in range(0,len(termosSaude)):
    q=termosSaude[ind].lower().split(';')
    for j in range(0,len(q)):
        if q[j]=="": print(i)
        t=hashTermosSaude['t'].loc[hashTermosSaude['t'] == q[j]]
        if t.index.size > 0:
            r=0
            r=hashTermosSaude['n'][t.index[0]]
            hashTermosSaude['n'][t.index[0]]=r+1
        else:
            hashTermosSaude=hashTermosSaude.append({'t':q[j],
                                          'n':1},
                                          ignore_index=True)



for i in hashTermosSaude.index: 
    print(hashTermosSaude['t'][i],": ",hashTermosSaude['n'][i])


hashTermosNSaude= pd.DataFrame(columns=['t','n','ind'])

#
for ind in range(0,len(termosNSaude)):
    q=termosNSaude[ind].lower().split(';')
    for j in range(0,len(q)):
        if q[j]=="": print(i)
        t=hashTermosNSaude['t'].loc[hashTermosNSaude['t'] == q[j]]
        if t.index.size > 0:
            r=0
            r=hashTermosNSaude['n'][t.index[0]]
            hashTermosNSaude['n'][t.index[0]]=r+1
        else:
            hashTermosNSaude=hashTermosNSaude.append({'t':q[j],
                                          'n':1,
                                          'ind':ind},
                                          ignore_index=True)



for i in hashTermosNSaude.index: 
    print(hashTermosNSaude['t'][i],": ",hashTermosNSaude['n'][i])


hashMS= pd.DataFrame(columns=['t','n'])
hashMNS= pd.DataFrame(columns=['t','n'])


cs=0
cns=0
for ind in dataset.index:
    if dataset['trabalhasaude'][ind]==1:
        cs=cs+1
        i=ind
        q=midiaBusca[i].lower().split('.')
        for j in range(0,len(q)):
            if q[j]=="": print(i)
            t=hashMS['t'].loc[hashMS['t'] == q[j]]
            if t.index.size > 0:
                r=0
                r=hashMS['n'][t.index[0]]
                hashMS['n'][t.index[0]]=r+1
            else:
                hashMS=hashMS.append({'t':q[j],
                                      'n':1}, ignore_index=True)
    else:
        cns=cns+1
        i=ind
        q=midiaBusca[i].lower().split('.')
        for j in range(0,len(q)):
            if q[j]=="": print(i)
            t=hashMNS['t'].loc[hashMNS['t'] == q[j]]
            if t.index.size > 0:
                r=0
                r=hashMNS['n'][t.index[0]]
                hashMNS['n'][t.index[0]]=r+1
            else:
                hashMNS=hashMNS.append({'t':q[j],
                                      'n':1}, ignore_index=True)


for ind in hashMS.index:
    hashMS['n'][ind]=hashMS['n'][ind]*100/cs
for ind in hashMNS.index:
    hashMNS['n'][ind]=hashMNS['n'][ind]*100/cns

h=hashMS.sort_values(by=['n'])
h.plot.barh(x='t', y='n', rot=0)

h=hashMNS.sort_values(by=['n'])
h.plot.barh(x='t', y='n', rot=0)






