from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from sqlalchemy import create_engine
import json
import pandas as pd

import nltk
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords

from timeit import default_timer as timer


def simplifyText(text):
    #removes punctuation, stopwords, and changes all words to lowercase
    text = text.translate(None, string.punctuation).lower()
    word_list = nltk.word_tokenize(text)
    filtered_text = [word for word in word_list if word not in stopwords.words('english')]
    
    #Lemmatizes the words (returns word stems)
    lemma = nltk.wordnet.WordNetLemmatizer()
    result = ""
    for word in filtered_text:
        result += lemma.lemmatize(word) + " "
    return result
    
def similarity(text1, text2):
    #returns cosine similarity value between two bodies of text using tfidf
    vect = TfidfVectorizer(min_df=1)
    tfidf = vect.fit_transform([text1, text2])
    return (tfidf * tfidf.T).A[0,1]

##################################### FUNCTIONS ARE ABOVE HERE #####################################



engine = create_engine("mysql+mysqlconnector://root:@localhost:3306/finhack", echo=False)

app = Flask(__name__)
api = Api(app)

class DB_Null(Resource):
    def get(self):        
        return {"number" : "0"}

class DB_Param_Search(Resource):
    def get(self):        
        start = timer()

        #takes in get queries titled ("limit, resultnum, search")
        parser = reqparse.RequestParser()
        parser.add_argument("limit", type=int)
        parser.add_argument("resultnum", type=int)
        parser.add_argument("search")
        args = parser.parse_args()
        limit = args.get("limit")  
        resultnum = args.get("resultnum")  
        search = args.get("search")

        #stems search query and removes stop words
        refinedSearch = simplifyText(str(search))
        print "search query: " + refinedSearch    
        #import mysql table into datafram
        data = pd.read_sql("SELECT number, simple_abstract FROM test LIMIT 0, %d"%limit, engine)  
        #add a new column for cosine_similarity 
        data["cosine_similarity"] = 0.0

        end = timer()
        print "dataframe created: " + str(end - start)
        
        #loop through rows        
        for i in range (0, limit):            
            similarity_result = similarity(data.get_value(i, "simple_abstract"), refinedSearch)
            #if similarity is negligible, set patent number to 0 (used for cleaning later)
            if similarity_result <= 0.05:
                data.set_value(i, "number", 0)
            #else add the similarity value to the new column (used for sorting later)         
            else:
                data.set_value(i, "cosine_similarity", similarity_result)    
        
        end = timer()
        print "dataframe values calculated: " + str(end - start)

        #remove non-matching rows
        data = data[data.number != 0]
        #remove simple_abstract column (we don't need this anymore)
        data = data.drop("simple_abstract", axis=1)
        #sort rows by similarity values in descending order
        data = data.sort_values(by="cosine_similarity", ascending=0)
        #drop the cosine_similarity column (we already sorted)
        data = data.drop("cosine_similarity", axis=1)        
        #limits rowcount to top n results
        if len(data.index) > resultnum:
            data = data[:resultnum] 
        #add a new column for the patent urls
        data["url"] = ""
        #fill the url column with appropriate values
        for i in data.index:
            data.set_value(i, "url", "http://www.freepatentsonline.com/" + str(data.get_value(i, "number")) + ".html")
        #print data.get_value(x, "number")
        end = timer()
        print "dataframe cleaned: " + str(end - start)
        #return final dataframe as json     
        result = data.to_json(orient="records")        
        return json.loads(result)


class DB_Limit_Search(Resource):
    def get(self, resultnum, limit, search):    
        start = timer()
        #stems search query and removes stop words
        refinedSearch = simplifyText(str(search))
        print "search query: " + refinedSearch    
        #import mysql table into datafram
        data = pd.read_sql("SELECT number, simple_abstract FROM test LIMIT 0, %d"%limit, engine)  
        #add a new column for cosine_similarity 
        data["cosine_similarity"] = 0.0

        end = timer()
        print "dataframe created: " + str(end - start)
        
        #loop through rows        
        for i in range (0, limit):            
            similarity_result = similarity(data.get_value(i, "simple_abstract"), refinedSearch)
            #if similarity is negligible, set patent number to 0 (used for cleaning later)
            if similarity_result <= 0.05:
                data.set_value(i, "number", 0)
            #else add the similarity value to the new column (used for sorting later)         
            else:
                data.set_value(i, "cosine_similarity", similarity_result)    
        
        end = timer()
        print "dataframe values calculated: " + str(end - start)

        #remove non-matching rows
        data = data[data.number != 0]
        #remove simple_abstract column (we don't need this anymore)
        data = data.drop("simple_abstract", axis=1)
        #sort rows by similarity values in descending order
        data = data.sort_values(by="cosine_similarity", ascending=0)
        #drop the cosine_similarity column (we already sorted)
        data = data.drop("cosine_similarity", axis=1)        
        #limits rowcount to top n results
        if len(data.index) > resultnum:
            data = data[:resultnum] 
        #add a new column for the patent urls
        data["url"] = ""
        #fill the url column with appropriate values
        for i in data.index:
            data.set_value(i, "url", "http://www.freepatentsonline.com/" + str(data.get_value(i, "number")) + ".html")
        #print data.get_value(x, "number")
        end = timer()
        print "dataframe cleaned: " + str(end - start)
        #return final dataframe as json     
        result = data.to_json(orient="records")        
        return json.loads(result)

class DB_List(Resource):
    def get(self,number):
        data = pd.read_sql("SELECT type, number, date, title, kind, simple_abstract FROM test LIMIT %d"%number, engine)
        result = data.to_json(orient="records")
        return result

class Test(Resource):
    def get(self):
        result = {'number': '0'}
        return result
 
api.add_resource(DB_Null, '/search')
api.add_resource(DB_Param_Search, '/getsearch')
api.add_resource(DB_Limit_Search, '/search/<int:resultnum>/<int:limit>/<string:search>')
api.add_resource(DB_List,'/list/<int:number>')
api.add_resource(Test, '/')

if __name__ == '__main__':
     app.run()



