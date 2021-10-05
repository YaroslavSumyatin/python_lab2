from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter import simpledialog
import matplotlib
import pandas as pd
from matplotlib import pyplot as plt
from math import log
import re

matplotlib.rc('figure', figsize=(10, 5))
Tk().withdraw()
FILE_PATH = askopenfilename()
MESSAGE = simpledialog.askstring("Input", "Write message!")
print("Your message: ", MESSAGE)
REPLACE_DICTIONARY = {r'[^A-Za-z ]+': ''}
SPACES_DICTIONARY = {r'\s\s+': ' ', r'(?=^|\n)\s': ' '}
STEM_REGULAR_EXPRESSION = {r'ion|s|ive|ed|ing(?= |\n|$)'}
OUTPUT_FOLDER = "output"
STOP_LIST = ["a", "an", "the", "in", "to"]


# i dont can you send it to me
# freemsg hey there darling
# Spook up your mob with a Halloween collection of a logo & pic message plus a free eerie

def format_text(text):
    text.replace(REPLACE_DICTIONARY, regex=True, inplace=True)
    for word in STOP_LIST:
        text.replace(r'(?=\b)' + word + r'(?=\b)', '', regex=True, inplace=True)
    text.replace(SPACES_DICTIONARY, regex=True, inplace=True)


def format_message(text):
    temp = re.sub(r'[^A-Za-z ]+', ' ', text)
    for word in STOP_LIST:
        temp = re.sub(r'(?=\b)' + word + r'(?=\b)', '', temp)
    temp = re.sub(r'\s\s+', ' ', temp)
    return re.sub(r'(?=^|\n)\s', ' ', temp)


def content_length(message):
    return pd.Series(message).str.len().sort_values(ascending=False)


def avg_content_length(messages_length, rows):
    return messages_length.sum() / len(rows)


def get_20_and_normalize(content):
    temp_content = content.head(20)
    temp_content.loc[:, 'count'] /= pd.Series(temp_content['count']).sum()
    return temp_content


df = pd.read_csv(FILE_PATH, encoding="cp1251")
df = df.applymap(lambda s: s.lower() if isinstance(s, str) else s)
format_text(df)
MESSAGE = MESSAGE.lower()
MESSAGE = format_message(MESSAGE)
ham = df[df.v1 == "ham"]
spam = df[df.v1 == "spam"]


def count_words(category):
    return category['v2'].str.split().explode().value_counts()


ham_count_words = count_words(ham)
spam_count_words = count_words(spam)


def p1(category):
    return len(category.index) / len(df.index)


def p2(message, category):
    words = message.split(sep=" ")
    category_words_count = count_words(category)
    temp_p = 1
    none_words = 0
    for w in words:
        word = category_words_count.get(key=w)
        if word is None:
            none_words += 1
    for w in words:
        word = category_words_count.get(key=w)
        word_sum = category_words_count.sum()
        if word is None:
            word = 1
        if none_words > 0:
            word += 1
            word_sum += none_words
        temp_p *= word / word_sum
    return temp_p


def p_result(category):
    return log(p1(category) * p2(MESSAGE, category))


print(p_result(ham))
print(p_result(spam))
if p_result(ham) > p_result(spam):
    print("Message from ham category")
else:
    print("Message from spam category")

ham_count_words = ham_count_words.to_frame().reset_index().rename(columns={'index': 'word', 'v2': 'count'})
spam_count_words = spam_count_words.to_frame().reset_index().rename(columns={'index': 'word', 'v2': 'count'})
ham_words_length = content_length(ham_count_words['word'])
spam_words_length = content_length(spam_count_words['word'])
ham_avg_words_length = avg_content_length(ham_words_length, ham_count_words)
spam_avg_words_length = avg_content_length(spam_words_length, spam_count_words)
ham_words_length = ham_words_length.to_frame().reset_index()
# ham_words_length.drop('index', inplace=True, axis=1)
ham_word_normalize = pd.Series(ham_words_length['word']).max()
ham_words_length.loc[:, 'word'] /= ham_word_normalize
ham_words_length = ham_words_length.sort_values(by=['word']).reset_index()
ham_avg_words_length /= ham_word_normalize
spam_words_length = spam_words_length.to_frame().reset_index()
# spam_words_length.drop('index', inplace=True, axis=1)
spam_word_normalize = pd.Series(spam_words_length['word']).max()
spam_words_length.loc[:, 'word'] /= spam_word_normalize
spam_avg_words_length /= spam_word_normalize
spam_words_length = spam_words_length.sort_values(by=['word']).reset_index()
ham_20_words = get_20_and_normalize(ham_count_words)
spam_20_words = get_20_and_normalize(spam_count_words)

Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
ham_count_words.to_csv(OUTPUT_FOLDER + '/hamCounter.csv', index=False, sep='-')
spam_count_words.to_csv(OUTPUT_FOLDER + '/spamCounter.csv', index=False, sep='-')

ham_message_length = content_length(ham['v2'])
spam_message_length = content_length(spam['v2'])
spam_avg_message_length = avg_content_length(spam_message_length, spam)
ham_avg_message_length = avg_content_length(ham_message_length, ham)
spam_message_length = spam_message_length.to_frame().reset_index()
# spam_message_length.drop('index', inplace=True, axis=1)
spam_message_normalize = pd.Series(spam_message_length['v2']).max()
spam_message_length.loc[:, 'v2'] /= spam_message_normalize
spam_avg_message_length /= spam_message_normalize
ham_message_length = ham_message_length.to_frame().reset_index()
# ham_message_length.drop('index', inplace=True, axis=1)
ham_message_normalize = pd.Series(ham_message_length['v2']).max()
ham_message_length.loc[:, 'v2'] /= ham_message_normalize
ham_avg_message_length /= ham_message_normalize

fig1, (ax1, ax2) = plt.subplots(1, 2)
ax1.set_title("ham")
ax1.bar(ham_20_words['word'], ham_20_words['count'])
ax2.set_title("spam")
ax2.bar(spam_20_words['word'], spam_20_words['count'])
fig1.autofmt_xdate(rotation=45)
fig1.show()
fig1.savefig(OUTPUT_FOLDER + "/20words.png")

fig2, (ax1, ax2) = plt.subplots(1, 2)
ax1.set_title("ham")
ax2.set_title("spam")
ax1.plot(ham_words_length['word'], ham_words_length['level_0'])
ax1.axvline(ham_avg_words_length, color="r")
ax1.legend(["length", "average"])
ax2.plot(spam_words_length['word'], spam_words_length['level_0'])
ax2.axvline(spam_avg_words_length, color="r")
ax2.legend(["length", "average"])
fig2.show()
fig2.savefig(OUTPUT_FOLDER + "/wordsLength.png")

fig3, (ax1, ax2) = plt.subplots(1, 2)
ax1.set_title("ham")
ax2.set_title("spam")
ax1.plot(ham_message_length['v2'])
ax1.axhline(ham_avg_message_length, color="r")
ax1.legend(["length", "average"])
ax2.plot(spam_message_length['v2'])
ax2.axhline(spam_avg_message_length, color="r")
ax2.legend(["length", "average"])
fig3.show()
fig3.savefig(OUTPUT_FOLDER + "/messageLength.png")
