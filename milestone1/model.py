import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


data = pd.read_csv("data/news.csv")  


data['label'] = data['label'].str.upper()

X = data["text"]
y = data["label"]


vectorizer = TfidfVectorizer(stop_words="english")
X_vectorized = vectorizer.fit_transform(X)


X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized, y, test_size=0.2, random_state=42
)


model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)


accuracy = accuracy_score(y_test, model.predict(X_test))


with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

with open("accuracy.pkl", "wb") as f:
    pickle.dump(accuracy, f)

print("Model trained successfully!")
print(f"Accuracy: {accuracy * 100:.2f}%")
