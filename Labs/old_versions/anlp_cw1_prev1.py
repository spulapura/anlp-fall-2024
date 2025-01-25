import sys
from random import random
from random import randrange
from math import log
from collections import defaultdict
import string
import numpy as np
from numpy import random
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


#Vocab size is always 30-- a-z0.# and space
vocab_size = 30


# We've also inserted # symbols to indicate BOS/EOS
def preprocess_line(line):
    preprocessed_line = "##"
    for ch in line:
        if ch in string.ascii_letters:
            preprocessed_line += ch.lower()
        elif ch.isdigit():
            preprocessed_line += "0"
        elif ch == " " or ch == ".":
            preprocessed_line += ch 
    return preprocessed_line + "#"


def initialize_trigram_counts():
    init_trigram_counts = {}
    valid_chars = string.ascii_letters[0:26] + " .#0"
    for ch1 in valid_chars:
        for ch2 in valid_chars:
            for ch3 in valid_chars:
                init_trigram_counts[ch1+ch2+ch3] = 0
    return init_trigram_counts

"""
This function builds a 2D dictionary for conditional probabilites for each context, 
such that {key = context, value = {key = character, value = conditional probability }}

So for example, conditional_dist["in"]["ing"] = P(g|in)
"""
def build_conditional_prob_distribution(distribution):
    conditional_dist = {}
    for key in distribution:
        context = key[0:2]
        if context not in conditional_dist:
            conditional_dist[context] = {}
        conditional_dist[context][key] = distribution[key]
    return conditional_dist

#Build dict mapping trigrams to number of times they occur
def build_trigram_counts(preprocessed_lines, init_counts):
    tri_counts = dict(init_counts)
    for line in preprocessed_lines:
        for j in range(len(line) - 2):
            trigram = line[j:j+3]
            tri_counts[trigram] += 1
    return tri_counts

#Build dict mapping bigram context to # of times it occurs in tri_counts
def build_context_counts(tri_counts):
    context_counts = defaultdict(int)
    for key in tri_counts:
        context = key[0:2]
        context_counts[context] += tri_counts[key]
    return context_counts 

def add_alpha_smoothing(tri_counts, context_counts, vocab_size, alpha):
    distribution = {}
    for trigram in tri_counts.keys():
        current_count = tri_counts[trigram]
        context = trigram[0:2]
        context_count = context_counts[context]
        distribution[trigram] = (current_count + alpha)/(context_count + vocab_size*alpha)
    
    return distribution

def compute_perplexity(conditional_probs, preprocessed_lines):
    perplexity = 0
    for line in preprocessed_lines:
        total = 0
        for i in range(len(line) - 2):
            trigram = line[i:i+3]
            context = trigram[0:2]
            total += log(1/(conditional_probs[context][trigram]), 2)
        perplexity += (total/(len(line) - 2))
    perplexity /= len(preprocessed_lines)
    return perplexity

#For each alpha in the input set
#Builds the distribution and evaluates average PPL on input set of lines
def test_alphas(alphas, tri_counts, context_counts, vocab_size, preprocessed_lines):
    perplexities = {}
    for alpha in alphas:
        distribution = add_alpha_smoothing(tri_counts, context_counts, vocab_size, alpha)
        conditional_probs = build_conditional_prob_distribution(distribution)
        perplexities[alpha] = compute_perplexity(conditional_probs, preprocessed_lines) 
    return min(perplexities, key=perplexities.get)

#Returns a list containing the preprocessed lines of the input file
def read_file(filename):
    f = open(filename)
    preprocessed_lines = []
    for line in f:
        preprocessed_line = preprocess_line(line)
        if preprocessed_line == "##.#" or "###" in preprocessed_line: #FIX LATER
            continue
        else:
            preprocessed_lines.append(preprocessed_line)
    f.close()
    return preprocessed_lines

def build_optimized_model(init_trigram_counts, train_set, dev_set):
    #Get trigram counts and context counts for training set
    tri_counts = build_trigram_counts(train_set, init_trigram_counts)
    context_counts = build_context_counts(tri_counts)

    #Test many values of alpha
    alphas = np.arange(0.2, 0, -0.001)
    min_alpha = test_alphas(alphas, tri_counts, context_counts, vocab_size, dev_set)

    #Compute optimized add-alpha distribution
    opt_add_alpha_dist = add_alpha_smoothing(tri_counts, context_counts, vocab_size, min_alpha)
    opt_add_alpha_conditional_probs = build_conditional_prob_distribution(opt_add_alpha_dist)

    #Compute PPL
    print("opt alpha:" + str(min_alpha))
    print("average PPL:" + str(compute_perplexity(opt_add_alpha_conditional_probs, dev_set)))

    return min_alpha, opt_add_alpha_dist, opt_add_alpha_conditional_probs

def classify(conditional_probs_dicts, doc):
    perplexities = {}
    for key in conditional_probs_dicts:
        perplexities[key] = compute_perplexity(conditional_probs_dicts[key], doc)
    return min(perplexities, key=perplexities.get), perplexities
    
def generate_from_LM(distribution, N):
    context = "##"
    full_doc = "##"

    conditional_probs = build_conditional_prob_distribution(distribution)

    i = 0
    while (i < N) :  
        #This case captures the end of a sentence 
        #We restart from ##
        if context not in conditional_probs:
            context = "##"
            full_doc += "#"
            continue
        
        elif context[1] == "#" and context[0] != "#":
            context = "##"
            full_doc += "##"
            continue

        #Fetch probability of each possible trigram in this context
        trigrams = np.array(list(conditional_probs[context].keys()))
        probs = np.array(list(conditional_probs[context].values()))
        probs /= probs.sum()

        #Randomly select a trigram according to its conditional probability
        trigram = random.choice(trigrams, p=probs, size=(1))[0]
        context = trigram[1:]
        full_doc += trigram[2]

        i += 1

    return full_doc

def generate_from_LM_updated(distribution, N):
    context = "##"
    full_doc = ""

    conditional_probs = build_conditional_prob_distribution(distribution)

    i = 0
    while (i < N) :  
        #This case captures the end of a sentence 
        #We restart from ##
        if context not in conditional_probs:
            context = "##"
            full_doc += "\n"
            i += 1
            continue

        #Fetch probability of each possible trigram in this context
        trigrams = np.array(list(conditional_probs[context].keys()))
        probs = np.array(list(conditional_probs[context].values()))
        probs /= probs.sum()

        #Randomly select a trigram according to its conditional probability
        trigram = random.choice(trigrams, p=probs, size=(1))[0]
        context = trigram[1:]
        if(trigram[2] != "#"): #Per advice in office hours, we do not include # in our character count
            full_doc += trigram[2]
        else:
            full_doc += "\n"
        i += 1
    return full_doc

################################################### MAIN ###########################################################

en_training = read_file("assignment1-data/training_set.en")
en_dev = read_file("assignment1-data/dev_set.en")
en_test = read_file("assignment1-data/test_set.en")

es_training = read_file("assignment1-data/training_set.es")
es_dev = read_file("assignment1-data/dev_set.es")
es_test = read_file("assignment1-data/test_set.es")

de_training = read_file("assignment1-data/training_set.de")
de_dev = read_file("assignment1-data/dev_set.de")
de_test = read_file("assignment1-data/test_set.de")

pt_training = read_file("assignment1-data/training_set.pt")
pt_dev = read_file("assignment1-data/dev_set.pt")
pt_test = read_file("assignment1-data/test_set.pt")

nl_training = read_file("assignment1-data/training_set.nl")
nl_dev = read_file("assignment1-data/dev_set.nl")
nl_test = read_file("assignment1-data/test_set.nl")

fr_training = read_file("assignment1-data/training_set.fr")
fr_dev = read_file("assignment1-data/dev_set.fr")
fr_test = read_file("assignment1-data/test_set.fr")

da_training = read_file("assignment1-data/training_set.da")
da_dev = read_file("assignment1-data/dev_set.da")
da_test = read_file("assignment1-data/test_set.da")

it_training = read_file("assignment1-data/training_set.it")
it_dev = read_file("assignment1-data/dev_set.it")
it_test = read_file("assignment1-data/test_set.it")

test = read_file("assignment1-data/test")

#Build distribution for model-br.en
model_br_dist = {}
#init_trigram_counts = initialize_trigram_counts()

init_trigram_counts = {}

with open("assignment1-data/model-br.en") as h:
    for line in h:
        key = line[0:3]
        model_br_dist[key] = float(line[4:])
        init_trigram_counts[key] = 0

print("OPTIMIZING MODELS IN ALL LANGUAGES")

print("english")
en_alpha, en_dist, en_cond_probs = build_optimized_model(dict(init_trigram_counts), en_training, en_dev)

print("german")
de_alpha, de_dist, de_cond_probs = build_optimized_model(dict(init_trigram_counts), de_training, de_dev)

print("spanish")
es_alpha, es_dist, es_cond_probs = build_optimized_model(dict(init_trigram_counts), es_training, es_dev)

print("portuguese")
pt_alpha, pt_dist, pt_cond_probs = build_optimized_model(dict(init_trigram_counts), pt_training, pt_dev)

print("dutch")
nl_alpha, nl_dist, nl_cond_probs = build_optimized_model(dict(init_trigram_counts), nl_training, nl_dev)

print("french")
fr_alpha, fr_dist, fr_cond_probs = build_optimized_model(dict(init_trigram_counts), fr_training, fr_dev)

print("italian")
it_alpha, it_dist, it_cond_probs = build_optimized_model(dict(init_trigram_counts), it_training, it_dev)

print("danish")
da_alpha, da_dist, da_cond_probs = build_optimized_model(dict(init_trigram_counts), da_training, da_dev)

print("\nGENERATE RANDOM SEQUENCES")
print(generate_from_LM_updated(model_br_dist, 300))
print(generate_from_LM_updated(en_dist, 300))
print(generate_from_LM_updated(es_dist, 300))
print(generate_from_LM_updated(de_dist, 300))

print("\nTEST CLASSIFICATION")

per_lang_cond_probs = {
    "english": en_cond_probs,
    "german": de_cond_probs,
    "dutch": nl_cond_probs,
    "danish": da_cond_probs,
    "spanish": es_cond_probs,
    "french": fr_cond_probs,
    "italian": it_cond_probs,
    "portuguese": pt_cond_probs,
}

num_correct = 0
num_incorrect = 0

# THESE TECHNICALLY SHOULD BE THE TEST SETS WE RESERVED
# I JUST LEFT IT WITH THE DEV SET FOR NOW JUST IN CASE

print("TESTING GERMAN SENTENCES")
for sent in de_dev:
    prediction, perplexities = classify(per_lang_cond_probs, [sent])
    if prediction == "german":
        num_correct += 1
    else:
        num_incorrect += 1
    print(perplexities)

print("TESTING ENGLISH SENTENCES")
for sent in en_dev:
    prediction, perplexities = classify(per_lang_cond_probs, [sent])
    if prediction == "english":
        num_correct += 1
    else:
        num_incorrect += 1
    print(perplexities)

print("TESTING SPANISH SENTENCES")
for sent in es_dev:
    prediction, perplexities = classify(per_lang_cond_probs, [sent])
    if prediction == "spanish":
        num_correct += 1
    else:
        num_incorrect += 1
    print(perplexities)

print("TESTING PORTUGUESE SENTENCES")
for sent in pt_dev:
    prediction, perplexities = classify(per_lang_cond_probs, [sent])
    if prediction == "portuguese":
        num_correct += 1
    else:
        num_incorrect += 1
    print(perplexities)

print(f"\nclassifying sentences in all languages. num correct: {num_correct}, num incorrect = {num_incorrect}")

num_correct = 0
num_incorrect = 0

print("CLASSIFYING ENGLISH FULL DOC")
prediction, perplexities_en = classify(per_lang_cond_probs, en_dev)
if(prediction == "english"):
    num_correct += 1
else:
    num_incorrect += 1
print(perplexities_en)


print("CLASSIFYING SPANISH FULL DOC")
prediction, perplexities_es = classify(per_lang_cond_probs, es_dev)
if(prediction == "spanish"):
    num_correct += 1
else:
    num_incorrect += 1
print(perplexities_es)


print("CLASSIFYING GERMAN FULL DOC")
prediction, perplexities_de = classify(per_lang_cond_probs, de_dev)
if(prediction == "german"):
    num_correct += 1
else:
    num_incorrect += 1
print(perplexities_de)

print("CLASSIFYING PORTUGUESE FULL DOC")
prediction, perplexities_pt = classify(per_lang_cond_probs, pt_dev)
if(prediction == "portuguese"):
    num_correct += 1
else:
    num_incorrect += 1
print(perplexities_pt)

print("CLASSIFYING DUTCH FULL DOC")
prediction, perplexities_nl = classify(per_lang_cond_probs, nl_dev)
if(prediction == "dutch"):
    num_correct += 1
else:
    num_incorrect += 1
print(perplexities_nl)

print("CLASSIFYING FRENCH FULL DOC")
prediction, perplexities_fr = classify(per_lang_cond_probs, fr_dev)
if(prediction == "french"):
    num_correct += 1
else:
    num_incorrect += 1
print(perplexities_fr)

print("CLASSIFYING ITALIAN FULL DOC")
prediction, perplexities_it = classify(per_lang_cond_probs, it_dev)
if(prediction == "italian"):
    num_correct += 1
else:
    num_incorrect += 1
print(perplexities_it)

print("CLASSIFYING DANISH FULL DOC")
prediction, perplexities_da = classify(per_lang_cond_probs, da_dev)
if(prediction == "danish"):
    num_correct += 1
else:
    num_incorrect += 1
print(perplexities_da)

print(f"\nclassifying documents in all languages. num correct: {num_correct}, num incorrect = {num_incorrect}")

prediction, perplexities = classify(per_lang_cond_probs, test)

print (f"\nclassifying the test document. the predicted language is: {prediction}. the perplexities are {perplexities}")

########################### Extension question

similarity_scores = {}

similarity_scores["english"] = {}
for key in perplexities_en:
    similarity_scores["english"][key] = perplexities_en[key] - perplexities_en["english"]

similarity_scores["german"] = {}
for key in perplexities_de:
    similarity_scores["german"][key] = perplexities_de[key] - perplexities_de["german"]

similarity_scores["dutch"] = {}
for key in perplexities_nl:
    similarity_scores["dutch"][key] = perplexities_nl[key] - perplexities_nl["dutch"]

similarity_scores["danish"] = {}
for key in perplexities_da:
    similarity_scores["danish"][key] = perplexities_da[key] - perplexities_da["danish"]

similarity_scores["spanish"] = {}
for key in perplexities_es:
    similarity_scores["spanish"][key] = perplexities_es[key] - perplexities_es["spanish"]

similarity_scores["french"] = {}
for key in perplexities_fr:
    similarity_scores["french"][key] = perplexities_fr[key] - perplexities_fr["french"]

similarity_scores["italian"] = {}
for key in perplexities_it:
    similarity_scores["italian"][key] = perplexities_it[key] - perplexities_it["italian"]

similarity_scores["portuguese"] = {}
for key in perplexities_pt:
    similarity_scores["portuguese"][key] = perplexities_pt[key] - perplexities_pt["portuguese"]


print(similarity_scores)

columns = ["English", "German", "Dutch", "Danish", "Spanish", "French", "Italian", "Portuguese"]

rows = ["English", "German", "Dutch", "Danish", "Spanish", "French", "Italian", "Portuguese"]


data = np.array([list(similarity_scores[key].values()) for key in similarity_scores])
df = pd.DataFrame(data, columns=columns, index=rows)

sns.heatmap(df)
plt.show()

#fig, ax = plt.subplots()

# #create table
# table = ax.table(cellText=data, loc='center', rowLabels=rows, colLabels=columns)

# #modify table
# table.set_fontsize(15)
# table.scale(2,1)
# ax.axis('off')

# #display table
# plt.show()

# i = 0
# num_correct = 0
# num_incorrect = 0
# while(i < 300):
#     lang = random.choice(["english", "spanish", "german"])
#     if lang == "english":
#         seq = preprocess_line(generate_from_LM_updated(en_dist, 30))
#     elif lang == "spanish":
#         seq = preprocess_line(generate_from_LM_updated(es_dist, 30))
#     else:
#         seq = preprocess_line(generate_from_LM_updated(de_dist, 30))

#     prediction = classify(per_lang_cond_probs, [seq])[0]

#     if(prediction == lang):
#         num_correct += 1
#     else:
#         num_incorrect += 1
#     i += 1

# print(f"\nclassifying generated sequences of all languages. num_correct = {num_correct}, num_incorrect = {num_incorrect}")

# #print(f"P(c|ab)={en_cond_probs["ab"]["abc"]}, P(d|bc)={en_cond_probs["bc"]["bcd"]}")

# print(en_cond_probs["ab"]["abc"])
# print(en_cond_probs["bc"]["bcd"])

# print(compute_perplexity(en_cond_probs, ["abcd"]))
# print(compute_perplexity(build_conditional_prob_distribution(model_br_dist), ["abcd"]))



