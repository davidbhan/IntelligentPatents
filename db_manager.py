'''
1. Run the following command in mysql to create the table properly (change tbname as needed):
CREATE TABLE patents
(
    id INT unsigned,
    type VARCHAR(15),
    number INT unsigned,
    country VARCHAR(15),
    date DATE,
    abstract LONGTEXT,
    title TEXT,
    kind VARCHAR(10),
    num_claims INT unsigned,
    filename VARCHAR(100)
);

2. Run the following line to import patent.tsv into the table just created(change file directory, dbname and tablename as needed):
LOAD DATA LOCAL INFILE '/Users/davidbhan/Desktop/patent.tsv' INTO TABLE finhack.patents LINES TERMINATED BY '\r\n'; 

3. Run the following line in the mysql server to add a new column for the simple_abstract:
ALTER TABLE patents ADD simple_abstract LONGTEXT AFTER filename;

4. Run the following line in mysql to remove the first line of title data
DELETE FROM patents WHERE country = country LIMIT 1;
'''

#for working with mysql and dataframes
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine

#for working with text analysis
import nltk
import string
from nltk.corpus import stopwords

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

#database and table names
dbname = "finhack"
tbname = "patents"

#change address as ncessary
engine = create_engine("mysql+mysqlconnector://root:@localhost:3306/" + dbname, echo=False)
print "database connection established."

#num of rows after following instructions should be 6215172
#num = pd.read_sql("SELECT COUNT(*) FROM " + tbname , engine)
#num = 6215172

#imports the entire table into a dataframe
#data = pd.read_sql_table(tbname, engine, columns=["type", "number", "date", "abstract", "title", "kind", "simple_abstract"], chunksize=1000)
#print "dataframe created."


totalrows = 0
for i in range(0, 6215172,100):
    #imports the first n rows into a dataframe
    data = pd.read_sql("SELECT type, number, date, abstract, title, kind, simple_abstract FROM patents LIMIT " + str(i) + ", 100", engine)

    #Iterates through all rows, and fills in the simple_abstract column   
    rownum = 0
    for row in data.itertuples():
        data.set_value(rownum, "simple_abstract", simplifyText(str(data.iloc[rownum, 3])))
        rownum += 1
        totalrows += 1
        if totalrows % 1000 == 0:
            print totalrows

    #appends the table with the current dataframe
    data.to_sql("test", engine, if_exists="append", index=False)

print "PROCESS COMPLETE"


