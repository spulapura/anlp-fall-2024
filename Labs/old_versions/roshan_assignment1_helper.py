#Here are some libraries you're likely to use. You might want/need others as well.
import re
import sys
from random import random
from random import choice
from random import shuffle
from math import log
from math import pow
from collections import defaultdict
import string
import numpy as np
from numpy import random
from numpy.random import random_sample

#here we make sure the user provides a training filename when
#calling this program, otherwise exit with a usage error.
if len(sys.argv) != 2:
    print("Usage: ", sys.argv[0], "<training_file>")
    sys.exit(1)

infile = sys.argv[1] #get input argument: the training file

tri_counts=defaultdict(int) #counts of all trigrams in input

#We've also inserted # symbols to indicat BOS/EOS
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

d = {}
tri_counts = {}
with open("assignment1-data/model-br.en") as f:
    for line in f:
        key = line[0:3]
        d[key] = float(line[4:])
        tri_counts[key] = 0

#This bit of code gives an example of how you might extract trigram counts
#from a file, line by line. If you plan to use or modify this code,
#please ensure you understand what it is actually doing, especially at the
#beginning and end of each line. Depending on how you write the rest of
#your program, you may need to modify this code.
preprocessed_lines = []
with open(infile) as f:
    for line in f:
        preprocessed_line = preprocess_line(line) #doesn't do anything yet.
        preprocessed_lines.append(preprocessed_line)
        #print(preprocessed_line)
        for j in range(len(preprocessed_line) - 2):
            trigram = preprocessed_line[j:j+3]
            tri_counts[trigram] += 1



# Some example code that prints out the counts. For small input files
# the counts are easy to look at but for larger files you can redirect
# to an output file (see Lab 1).
# print("Trigram counts in ", infile, ", sorted alphabetically:")
# for trigram in sorted(tri_counts.keys()):
#     print(trigram, ": ", tri_counts[trigram])
# print("Trigram counts in ", infile, ", sorted numerically:")
# for tri_count in sorted(tri_counts.items(), key=lambda x:x[1], reverse = True):
#     print(tri_count[0], ": ", str(tri_count[1]))



def get_conditional_probs(distribution, context):
    d = {}
    for key in distribution.keys():
        if(key[0:2] == context):
            d[key] = distribution[key]
    return d



def generate_from_LM(distribution, N):
    context = "##"
    full_doc = "##"

    i = 0
    while (i < N) :
        conditional_probs = get_conditional_probs(distribution, context)
    
        trigrams = np.array(list(conditional_probs.keys()))
        probs = np.array(list(conditional_probs.values()))
        probs /= probs.sum()

        #TODO: handle cases where the context is not in the dictionary
        trigram = random.choice(trigrams, p=probs, size=(1))[0]
        context = trigram[1:]
        full_doc += trigram[2]

        #Start a new sentence if we've reached the end of a sentence. 
        if(context == ".#"):
            context = "##"
            full_doc += "#"

        i += 1

    return full_doc

#vocabulary size is constant
vocab_size = 30


def get_context_counts(context):
    count = 0
    for key in tri_counts.keys():
        if key[0:2] == context:
            count += tri_counts[key]
    return count 


def add_alpha_smoothing_helper(trigram, alpha):
    current_count = tri_counts[trigram]
    context_count = get_context_counts(trigram[0:2])
    return (current_count + alpha)/(context_count + vocab_size*alpha)



def add_alpha_smoothing(alpha):
    distribution = {}
    for trigram in tri_counts.keys():
        distribution[trigram] = add_alpha_smoothing_helper(trigram, alpha)

    # distribution = {}
    # with open(training_file) as doc:
    #     for line in doc:
    #         preprocessed_line = preprocess_line(line) #doesn't do anything yet.
    #         #print(preprocessed_line)
    #         for j in range(len(preprocessed_line) - 2):
    #             trigram = preprocessed_line[j:j+3]
    #             distribution[trigram] = add_alpha_smoothing_helper(trigram, alpha)

    return distribution


def compute_perplexity(distribution, doc):
    total = 0
    for i in range(len(doc) - 2):
        trigram = doc[i:i+3]
        conditional_probs = get_conditional_probs(distribution, trigram[0:2])
        #print("Trigram: " + trigram + " Conditional prob: " + str(conditional_probs[trigram]))
        total += log(1/(conditional_probs[trigram]), 2)
    #print(total/(len(doc) - 2))
    return total/(len(doc) - 2)


def test_alphas():
    perplexities = {}
    for alpha in np.arange(1, 0, -0.1):
        distribution = add_alpha_smoothing(alpha)
        perplexity = 0
        for line in preprocessed_lines: 
            #print(line)
            perplexity += compute_perplexity(distribution, line)
            #print(perplexity)
        perplexities[alpha] = perplexity 
        print("Perplexity for alpha=" + str(alpha) + " is " + str(perplexities[alpha]))

    return min(perplexities, key=distribution.get)


#testing alphas
# print("Optimal alpha=" + str(test_alphas()))

# add_alpha_dist = add_alpha_smoothing(0.95)
# conditional_probs_test = get_conditional_probs(add_alpha_dist, "ba")
# print("TEST CONDITIONAL PROBS")
# print(conditional_probs_test)
# print(sum(conditional_probs_test.values()))
# compute_perplexity(add_alpha_dist, preprocess_line("I shall therefore reserve the right, if you permit, sir, to give you my own opinion, which, to a great extent, matches your own recommendation regarding what action we might take to combat the oil spillage using Objective 2."))

test_alphas()




#print(generate_from_LM(d, 300))


