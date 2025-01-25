import sys
from random import random
from math import log
from collections import defaultdict
import string
import numpy as np
from numpy import random


#Here we make sure the user provides a training filename when
#calling this program, otherwise exit with a usage error.
if len(sys.argv) != 2:
    print("Usage: ", sys.argv[0], "<training_file>")
    sys.exit(1)

infile = sys.argv[1] #get input argument: the training file


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


def build_trigram_counts(preprocessed_lines, init_counts):
    print(init_counts)
    tri_counts = init_counts
    for line in preprocessed_lines:
        for j in range(len(line) - 3):
            trigram = line[j:j+3]
            tri_counts[trigram] += 1
            if(trigram == "ree"):
                print(line)
    return tri_counts

#Build dict mapping context to # of times it occurs in tri_counts
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
    return perplexity

def test_alphas(alphas, tri_counts, context_counts, vocab_size, preprocessed_lines):
    perplexities = {}
    for alpha in alphas:
        distribution = add_alpha_smoothing(tri_counts, context_counts, vocab_size, alpha)
        conditional_probs = build_conditional_prob_distribution(distribution)
        perplexities[alpha] = compute_perplexity(conditional_probs, preprocessed_lines) 
        print("Perplexity for alpha=" + str(alpha) + " is " + str(perplexities[alpha]))
    return min(perplexities, key=perplexities.get)

###### Main #######

#vocabulary size is constant
vocab_size = 30

#Preprocess and store each line from the training set (running with input file partition training_set.en)
en_preprocessed_lines = []
with open("assignment1-data/training_set.en") as f:
    for line in f:
        preprocessed_line = preprocess_line(line) 
        en_preprocessed_lines.append(preprocessed_line)

es_preprocessed_lines = []
with open("assignment1-data/training_set.es") as f:
    for line in f:
        preprocessed_line = preprocess_line(line) 
        es_preprocessed_lines.append(preprocessed_line)

de_preprocessed_lines = []
with open("assignment1-data/training_set.de") as f:
    for line in f:
        preprocessed_line = preprocess_line(line) 
        de_preprocessed_lines.append(preprocessed_line)

#Preprocess and store each line from the dev set
en_devset_preprocessed_lines = []
with open("assignment1-data/dev_set.en") as g:
    for line in g:
        preprocessed_line = preprocess_line(line)
        en_devset_preprocessed_lines.append(preprocessed_line)

es_devset_preprocessed_lines = []
with open("assignment1-data/dev_set.es") as g:
    for line in g:
        preprocessed_line = preprocess_line(line)
        es_devset_preprocessed_lines.append(preprocessed_line)

de_devset_preprocessed_lines = []
with open("assignment1-data/dev_set.de") as g:
    for line in g:
        preprocessed_line = preprocess_line(line)
        de_devset_preprocessed_lines.append(preprocessed_line)

#Build distribution for model-br.en
model_br_dist = {}
init_trigram_counts = {}
with open("assignment1-data/model-br.en") as h:
    for line in h:
        key = line[0:3]
        model_br_dist[key] = float(line[4:])
        init_trigram_counts[key] = 0


#Create conditional probability distribution for model-br.en
model_br_conditional_dist = build_conditional_prob_distribution(model_br_dist)

#Generate a random sequence of length 300 according to model-br.en
#print(generate_from_LM(model_br_dist, 300))

#Get trigram counts and context counts for training set
en_trigram_counts = build_trigram_counts(en_preprocessed_lines, init_trigram_counts)
en_context_counts = build_context_counts(en_trigram_counts)

es_trigram_counts = build_trigram_counts(es_preprocessed_lines, init_trigram_counts)
es_context_counts = build_context_counts(es_trigram_counts)

de_trigram_counts = build_trigram_counts(de_preprocessed_lines, init_trigram_counts)
de_context_counts = build_context_counts(de_trigram_counts)

#Calculate add alpha distribution and conditional probabilities 
# add_alpha_distribution = add_alpha_smoothing(trigram_counts, context_counts, vocab_size, 0.05)
# add_alpha_conditional_probs = build_conditional_prob_distribution(add_alpha_distribution)

#Test many values of alpha
alphas = np.arange(0.05, 0.07, 0.001)
min_alpha_en = test_alphas(alphas, en_trigram_counts, en_context_counts, vocab_size, en_devset_preprocessed_lines)
print("Min alpha English=" + str(min_alpha_en))

alphas = np.arange(1, 0, -0.01)
min_alpha_es = test_alphas(alphas, es_trigram_counts, es_context_counts, vocab_size, es_devset_preprocessed_lines)
print("Min alpha Spanish=" + str(min_alpha_es))

alphas = np.arange(1, 0, -0.01)
min_alpha_de = test_alphas(alphas, de_trigram_counts, de_context_counts, vocab_size, de_devset_preprocessed_lines)
print("Min alpha German=" + str(min_alpha_en))


#Compute optimized add-alpha distribution
en_opt_add_alpha_dist = add_alpha_smoothing(en_trigram_counts, en_context_counts, vocab_size, min_alpha_en)
en_opt_add_alpha_conditional_probs = build_conditional_prob_distribution(en_opt_add_alpha_dist)

es_opt_add_alpha_dist = add_alpha_smoothing(es_trigram_counts, es_context_counts, vocab_size, min_alpha_es)
es_opt_add_alpha_conditional_probs = build_conditional_prob_distribution(es_opt_add_alpha_dist)

de_opt_add_alpha_dist = add_alpha_smoothing(de_trigram_counts, de_context_counts, vocab_size, min_alpha_de)
de_opt_add_alpha_conditional_probs = build_conditional_prob_distribution(de_opt_add_alpha_dist)

# test_dummy_string = "rec"

# test_add_alpha_dist = add_alpha_smoothing(trigram_counts, context_counts, 30, 1)
# test_add_alpha_conditional_probs = build_conditional_prob_distribution(test_add_alpha_dist)
# # print(test_add_alpha_dist)
# # print("CONDITIONAL PROBS FOR RE")
# # print(test_add_alpha_conditional_probs["re"])


# total_count = 0
# for trigram in trigram_counts:
#     if trigram[0:2] == "re":
#         print("trigram: " + trigram + " count " + str(trigram_counts[trigram]))
#         total_count += trigram_counts[trigram]
# print(total_count)



#Compare perplexities per language

print("PERPLEXITY ON ENGLISH DEV SET")
print(compute_perplexity(en_opt_add_alpha_conditional_probs, en_devset_preprocessed_lines))
print(compute_perplexity(es_opt_add_alpha_conditional_probs, en_devset_preprocessed_lines))
print(compute_perplexity(de_opt_add_alpha_conditional_probs, en_devset_preprocessed_lines))

print("PERPLEXITY ON SPANISH DEV SET")
print(compute_perplexity(en_opt_add_alpha_conditional_probs, es_devset_preprocessed_lines))
print(compute_perplexity(es_opt_add_alpha_conditional_probs, es_devset_preprocessed_lines))
print(compute_perplexity(de_opt_add_alpha_conditional_probs, es_devset_preprocessed_lines))

print("PERPLEXITY ON GERMAN DEV SET")
print(compute_perplexity(en_opt_add_alpha_conditional_probs, de_devset_preprocessed_lines))
print(compute_perplexity(es_opt_add_alpha_conditional_probs, de_devset_preprocessed_lines))
print(compute_perplexity(de_opt_add_alpha_conditional_probs, de_devset_preprocessed_lines))


#print(compute_perplexity(model_br_conditional_dist, devset_preprocessed_lines))

# test_line = "##abcde#"
# for i in range(len(test_line) - 2):
#     context = test_line[i:i+2]
#     trigram = test_line[i:i+3]
#     print("Iteration " + str(i))
#     print(trigram)
#     print(context)
#     print(opt_add_alpha_conditional_probs[context][trigram])

# print("Perplexity: " + str(compute_perplexity(opt_add_alpha_conditional_probs, [test_line])))

#print(opt_add_alpha_conditional_probs["##"])

#Generate a random sequence of length 300 according to our add-alpha smoothing model
#print(generate_from_LM(opt_add_alpha_dist, 300))
