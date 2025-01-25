import sys
from random import random
from random import randrange
from math import log
from collections import defaultdict
import string
import numpy as np
from numpy import random

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
        for j in range(len(line) - 3):
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
        preprocessed_lines.append(preprocess_line(line))
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

def classify(conditional_probs_dicts, sent):
    perplexities = {}
    for key in conditional_probs_dicts:
        perplexities[key] = compute_perplexity(conditional_probs_dicts[key], [sent])
    return min(perplexities, key=perplexities.get)

def classify_doc(conditional_probs_dicts, doc):
    perplexities = {}
    for key in conditional_probs_dicts:
        perplexities[key] = compute_perplexity(conditional_probs_dicts[key], doc)
    return min(perplexities, key=perplexities.get)
    
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
            print("newline")
            full_doc += "\n"
        i += 1

    print(len(full_doc))
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

test = read_file("assignment1-data/test")

#Build distribution for model-br.en
model_br_dist = {}
init_trigram_counts = initialize_trigram_counts()

with open("assignment1-data/model-br.en") as h:
    for line in h:
        key = line[0:3]
        model_br_dist[key] = float(line[4:])

tri_counts = build_trigram_counts(en_training, init_trigram_counts)
context_counts = build_context_counts(tri_counts)


add_alpha_distribution = add_alpha_smoothing(tri_counts, context_counts, vocab_size, 0.05)
add_alpha_conditional_probs = build_conditional_prob_distribution(add_alpha_distribution)

print("OPTIMIZING MODELS IN ALL LANGUAGES")
print("german")
de_alpha, de_dist, de_cond_probs = build_optimized_model(init_trigram_counts, de_training, de_dev)

print("english")
en_alpha, en_dist, en_cond_probs = build_optimized_model(init_trigram_counts, en_training, en_dev)

print("spanish")
es_alpha, es_dist, es_cond_probs = build_optimized_model(init_trigram_counts, es_training, es_dev)

print("\nGENERATE RANDOM SEQUENCES")
print(generate_from_LM(model_br_dist, 300))
print(generate_from_LM(en_dist, 300))
print(generate_from_LM(es_dist, 300))
print(generate_from_LM(de_dist, 300))

print("\nTEST CLASSIFICATION")

per_lang_cond_probs = {
    "english": en_cond_probs,
    "spanish": es_cond_probs,
    "german": de_cond_probs
}

num_correct = 0
num_incorrect = 0

# THESE TECHNICALLY SHOULD BE THE TEST SETS WE RESERVED
# I JUST LEFT IT WITH THE DEV SET FOR NOW JUST IN CASE
for sent in de_dev:
    prediction = classify(per_lang_cond_probs, sent)
    if prediction == "german":
        num_correct += 1
    else:
        num_incorrect += 1

for sent in en_dev:
    prediction = classify(per_lang_cond_probs, sent)
    if prediction == "english":
        num_correct += 1
    else:
        num_incorrect += 1

for sent in es_dev:
    prediction = classify(per_lang_cond_probs, sent)
    if prediction == "spanish":
        num_correct += 1
    else:
        num_incorrect += 1

print(f"\nclassifying given sentences in all languages. num correct: {num_correct}, num incorrect = {num_incorrect}")

i = 0
num_correct = 0
num_incorrect = 0
while(i < 300):
    lang = random.choice(["english", "spanish", "german"])
    if lang == "english":
        seq = generate_from_LM(en_dist, 30)
    elif lang == "spanish":
        seq = generate_from_LM(es_dist, 30)
    else:
        seq = generate_from_LM(de_dist, 30)

    prediction = classify(per_lang_cond_probs, seq)

    if(prediction == lang):
        num_correct += 1
    else:
        num_incorrect += 1
    i += 1

print(f"tested on randomly generated sequences of all languages. num_correct = {num_correct}, num_incorrect = {num_incorrect}")

