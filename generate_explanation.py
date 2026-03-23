import numpy as np
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

# Load trained LSTM model
model = load_model("text_generator_model.h5")

# Load tokenizer
with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

# Load max_seq_len
with open("max_seq_len.pkl", "rb") as f:
    max_seq_len = pickle.load(f)


def generate_text(seed_text, next_words):

    for _ in range(next_words):

        token_list = tokenizer.texts_to_sequences([seed_text])[0]

        token_list = pad_sequences(
            [token_list],
            maxlen=max_seq_len - 1,
            padding="pre"
        )

        predicted = model.predict(token_list, verbose=0)

        predicted_word = ""

        for word, index in tokenizer.word_index.items():
            if index == predicted.argmax():
                predicted_word = word
                break

        seed_text += " " + predicted_word

    return seed_text


def generate_explanation(risk_score):

    if risk_score == "High Risk":
        seed = "High debt ratio increases the risk"

    elif risk_score == "Medium Risk":
        seed = "Moderate financial risk detected"

    else:
        seed = "Low financial risk detected"

    return generate_text(seed, 15)