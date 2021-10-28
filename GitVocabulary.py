import csv, shutil, string, mlconjug
import requests, pluralizefr, time, tkinter as tk
from bs4 import BeautifulSoup
from tkinter import filedialog
from tkinter import ttk

TIMECODE = time.strftime("%Y%m%d-%H%M%S")
CONJUGATIONS = ("past", "present", "future", "subjunctive", "imperfect", "conditional")

def add(output, word, meanings):
    with open (output, "a+") as output_file:
        output_csv = csv.writer(output_file)
        if type(meanings[0]) != str and len(meanings[0]) > 1:
            english = ", ".join(meanings[0])
        else:
            english = meanings[0][0]
        print(word)
        output_csv.writerow([word, english, meanings[1]])
        
def make_card(output, word):
    url = "https://en.wiktionary.org/wiki/"+word
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    french = soup.find(id="French")
    try:
        etymology = french.find_next("p").get_text()[0:-1]
        translation = french.find_next("ol").get_text().split("\n")
    except:
        etymology = "not_found"
        translation = "not_found"

    # checking for verbs
    words_in_translation = translation[0].split()
    if any(item in CONJUGATIONS for item in words_in_translation):
        for verb_check in words_in_translation:
            if mlconjug.PyVerbiste.ConjugManager(language="fr").is_valid_verb(verb_check):
                make_card(output, verb_check)
                return 0

    # striping of prefixes
    if word[0:2] in ("m'", "t'", "s'", "l'", "j'", "d'", "n'"):
        make_card(output, word[2:])
        return 0
        
    # changing feminine to macsculine
    if translation[0][0:20] == "feminine singular of":
        make_card(output, translation[0][21:])
        return 0

    # changing plural to singular
    if etymology == "not_found" or "plural" in translation[0].split():
        if pluralizefr.singularize(word) != word:
            make_card(output, pluralizefr.singularize(word))
        return 0
    add(output, word, [translation, etymology])

def out_path_maker(path):
    start = False
    new_path = ""
    for symbol in path[::-1]:
        if symbol == "/":
            start = True
        if start == True:
            new_path += symbol
    new_path = new_path[::-1]+"out"+TIMECODE+".txt"
    return(new_path)


def process(filename, title):

    with open(filename, "r") as file:
        titles = map(lambda x: x.split('(')[0], file.readlines()[0::5])
        file.seek(0)
        words = file.readlines()[3::5]
        taged_words = list(zip(words, titles))
        selected_words = [x[0] for x in taged_words if x[1] == title]
        print(selected_words)


    # sort and culitvate words
    new_words = []
    for word in selected_words:
        new_word = word[:-1].lower()
        while new_word[-1] in string.punctuation:
            new_word = new_word[0:-1]
        if new_word[0] in string.punctuation:
            new_word = new_word[1:]    
        new_words.append(new_word)

    # iterate over all words
    for word in new_words:
        make_card(out_path_maker(filename), word)


def browseFiles():
    filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("Text files",
                                                        "*.txt*"),))
    #output = out_path_maker(filename)

    with open(filename, "r") as file:
        #words = file.readlines()[3::5]
        titles = file.readlines()[0::5]
        books = list(dict.fromkeys(map(lambda title: title.split('(')[0], titles)))[::-1]

    #choose_book = tk.Tk()
    window.config(bg='black')
    window.geometry("400x600")

    dropdown = ttk.Combobox(window, values=books)
    dropdown.pack()

    process_button = tk.Button(window, text = "Process", 
                            command = lambda : process(filename, dropdown.get()))
    process_button.pack()

    window.mainloop()

window = tk.Tk()
window.configure(bg = 'black')  
      
button_explore = tk.Button(window,text = "Browse Files", command = lambda : browseFiles())
button_explore.pack()

window.mainloop()

        