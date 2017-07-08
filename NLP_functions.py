import nltk
import string
from sklearn.feature_extraction.text import TfidfVectorizer
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
    
def similarity(text1, text2):
    #returns cosine similarity value between two bodies of text using tfidf
    vect = TfidfVectorizer(min_df=1)
    tfidf = vect.fit_transform([text1, text2])
    return (tfidf * tfidf.T).A[0,1]

print similarity("hello I'm David, and I love my little bunny \n asdf fuck this code", "hello I'm Juwon, and I love my big bear")
print similarity(simplifyText("hello I'm David, and I love my little bunny"), simplifyText("hello I'm Juwon, and I love my big bear"))
print simplifyText("hello I'm David, I was born on the best day of the best month because i'm the best of them all!")
