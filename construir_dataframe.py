from pymongo import MongoClient
import pandas as pd
import ast
import json
import numpy as np

client = MongoClient("mongodb+srv://leonardocroda:HLF2YMd3f1hf5cdo@classificar-tweets-srtwi.mongodb.net/admin?retryWrites=true&w=majority") # conecta num cliente do MongoDB rodando na sua máquina
db = client['classificar_tweets'] # acessa o banco de dados
collection = db['teste'] # acessa a minha coleção dentro desse banco de dados
all_tweets = list(collection.find({} , {"id": 1,"full_text": 1,"sentimento": 1,"pilares": 1}))
dataset = pd.DataFrame(all_tweets)
def monta_dataframe(all_tweets):

  tweet_dict={}
  tweet_array_string=[]
  tweet_array=[]
  #caso o tweet tenha mais de um assunto, é atribuido ele é adicionado a tweet_dict e o ultimo assunto é removido da coluna 
  def quebrar():
    for tweet in all_tweets:
      if len(tweet["pilares"])>1:
        tweet_dict["id"] = tweet["id"]
        tweet_dict["full_text"]=tweet["full_text"]
        tweet_dict["sentimento"]=tweet["sentimento"]
        tweet_dict["pilares"]=tweet["pilares"][(len(tweet["pilares"])-1)]
        tweet["pilares"].pop()
        tweet_array_string.append(json.dumps(tweet_dict))
  #executa quebrar 7 vezes, pois são 7 assuntos possíveis
  i=0
  while (i < 8):
    quebrar()
    i=i+1
  #quando eu removo os assuntos, no tweet original o tipo do dado continua sendo lista, isso atribui a pilares a string do pilar em si
  for tweet in all_tweets:
    if type(tweet["pilares"]) == list:
      tweet["pilares"]=tweet["pilares"][len(tweet["pilares"])-1]
  # não consegui fazer append do dicionario na lista, por isso transformei o dicionario 
  #em string, esse bloco transforma eles em dicionario novamente, isso é necessário para transformar em dataframe
  for string in tweet_array_string:
    dicionario = ast.literal_eval(string)
    tweet_array.append(dicionario)  
  #junta a lista original com a dos tweets q tinham mais de um assunto
  all_tweets.extend(tweet_array)
  for linha in all_tweets:
    if(linha['pilares'] =='1' or linha['pilares']=='3' or linha['pilares']=='4' ):
      linha['poder_publico']=1
      linha['populacao'] = 0
    else:
      linha['poder_publico']=0
      linha['populacao'] = 1
  #transforma em dataframe
  dataset = pd.DataFrame(all_tweets)
  dataset['sentimento']=dataset['sentimento'].replace({2:np.random.choice([0, 1])})
  dataset.drop('_id', inplace=True, axis=1)
  return dataset
  
dataframe = monta_dataframe(all_tweets)
