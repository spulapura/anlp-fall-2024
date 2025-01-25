from random import random
from math import log 
from collections import defaultdict
import string 
import numpy as np
from numpy import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

################################### TRAIN ##################################

# In addition to the specified requirements, we've also 
# inserted # symbols to indicate beginning/end of line
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
such that {key = context, value = {key = trigram, value = conditional probability }}

So for example, conditional_dist["in"]["ing"] = P(g|in)

The input is a 1D dictionary mapping key=trigram to value=conditional probability.

The 2D dictionary makes it much faster to access the conditional distributions
of trigrams for a given context, i.e. a contstant-time lookup of the context key,
rather than a linear-time search for all trigrams keys containing that context.
"""
def build_conditional_prob_distribution(distribution):
    conditional_dist = {}
    for key in distribution:
        context = key[0:2]
        if context not in conditional_dist:
            conditional_dist[context] = {}
        conditional_dist[context][key] = distribution[key]
    return conditional_dist

# Build dict mapping each trigram to # of times it occurs
def build_trigram_counts(preprocessed_lines, init_counts):
    tri_counts = dict(init_counts)
    for line in preprocessed_lines:
        for j in range(len(line) - 2):
            trigram = line[j:j+3]
            tri_counts[trigram] += 1
    return tri_counts

# Build dict mapping bigram context to # of times it occurs in tri_counts
def build_context_counts(tri_counts):
    context_counts = defaultdict(int)
    for key in tri_counts:
        context = key[0:2]
        context_counts[context] += tri_counts[key]
    return context_counts

# Use add-alpha smoothing to compute conditional probabilities of each trigram
def add_alpha_smoothing(tri_counts, context_counts, vocab_size, alpha):
    distribution = {}
    for trigram in tri_counts.keys():
        current_count = tri_counts[trigram]
        context = trigram[0:2]
        context_count = context_counts[context]
        distribution[trigram] = (current_count + alpha)/(context_count + vocab_size*alpha)
    return distribution

"""
Given a 2D dictionary of conditional probability distributions (such as the one
returned by build_conditional_prob_distribution) and a document
(preprocessed into a list of valid lines), we compute the average 
perplexity per line for the document. 
"""
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

"""
Given a list of potential alphas, select the alpha value that minimizes
the perplexity of the model built from the given trigram counts,
when evaluated on the given document (preprocessed into a list of valid lines)
"""
def test_alphas(alphas, tri_counts, context_counts, vocab_size, preprocessed_lines):
    perplexities = {}
    for alpha in alphas:
        distribution = add_alpha_smoothing(tri_counts, context_counts, vocab_size, alpha)
        conditional_probs = build_conditional_prob_distribution(distribution)
        perplexities[alpha] = compute_perplexity(conditional_probs, preprocessed_lines)
    min_alpha = min(perplexities, key=perplexities.get)
    return min_alpha, perplexities[min_alpha]

"""
Wraps the entire process of building the model. Given a training set and a dev
set, we calculate the optimal alpha and the corresponding 1D and 2D probability 
distribution dictionaries, such that perplexity is minimized on the dev set
"""
def build_optimized_model(init_trigram_counts, vocab_size, train_set, dev_set):
    #Get trigram counts and context counts for training set
    tri_counts = build_trigram_counts(train_set, init_trigram_counts)
    context_counts = build_context_counts(tri_counts)

    #Test many values of alpha
    alphas = np.arange(0.2, 0, -0.001)
    min_alpha, min_ppl = test_alphas(alphas, tri_counts, context_counts, vocab_size, dev_set)

    #Compute optimized add-alpha distribution
    opt_add_alpha_dist = add_alpha_smoothing(tri_counts, context_counts, vocab_size, min_alpha)
    opt_add_alpha_conditional_probs = build_conditional_prob_distribution(opt_add_alpha_dist)

    #Compute perplexity
    print("opt alpha:" + str(min_alpha))
    print("average PPL:" + str(min_ppl))

    return min_alpha, opt_add_alpha_dist, opt_add_alpha_conditional_probs, min_ppl

#################################### TEST UTILS ##############################

# Returns a list containing the preprocessed lines of the input file
def read_file(filename):
    f = open(filename, encoding="utf-8")
    preprocessed_lines = []
    for line in f:
        preprocessed_line = preprocess_line(line)
        # We discard blank lines and lines with just a period, as they are linguistically uninformative
        if preprocessed_line == "##.#" or "###" in preprocessed_line: 
            continue
        else:
            preprocessed_lines.append(preprocessed_line)
    f.close()
    return preprocessed_lines

"""
First input is a 3D dictionary, where key=language and value=2D conditional probability
dictionary (as returned by build_conditional_prob_distribution).

e.g. conditional_probs_dicts["english"] yields the conditional probabilities
for a model trained on English data, conditional_probs_dicts["german"] yields
the distribution for a model trained on German data, etc. 

Second input is the document to be classified (preprocessed into valid lines).

This function selects the language whose model minimizes the perplexity on 
the input document. 
"""
def classify(conditional_probs_dicts, doc):
    perplexities = {}
    for key in conditional_probs_dicts:
        perplexities[key] = compute_perplexity(conditional_probs_dicts[key], doc)
    return min(perplexities, key=perplexities.get), perplexities

def generate_from_LM(distribution, N):
    context = "##"
    full_doc = "" #In office hours, we were advised not to include the # in our output
    
    conditional_probs = build_conditional_prob_distribution(distribution)

    i = 0
    while(i < N):
        # Fetch probability of each possible trigram in this context
        trigrams = np.array(list(conditional_probs[context].keys()))
        probs = np.array(list(conditional_probs[context].values()))
        probs /= probs.sum() #to resolve slight float rounding issues, we normalize

        # Randomly select a trigram according to its conditional probability
        trigram = random.choice(trigrams, p=probs, size=(1))[0]

        # If the randomly selected trigram ends in a stop character
        # we end the existing line with \n and start a new line
        if(trigram[2] == "#"): 
            full_doc += "\n"
            context = "##"
        
        # Otherwise, we append the newly generated character (ie the final character of the
        # randomly selected trigram) to the doc and advance the context
        else:
            full_doc += trigram[2]
            context = trigram[1:]

        i += 1

    return full_doc

######################## READ ALL DATA FILES ########################

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

#Build initialization dict with all trigrams set to count=0
init_trigram_counts = {}

with open("assignment1-data/model-br.en") as h:
    for line in h:
        key = line[0:3]
        model_br_dist[key] = float(line[4:])
        init_trigram_counts[key] = 0

########################### OPTIMIZE MODELS FOR ALL LANGUAGES #######################

# Vocab size is 30 for all languages, as per our preprocessing function
vocab_size = 30

print("Optimizing English...")
en_alpha, en_dist, en_cond_probs, en_min_ppl = build_optimized_model(dict(init_trigram_counts), vocab_size, en_training, en_dev)

f ='assignment1-data/model.en' 
with open(f, 'w') as outfile:
    for key in en_dist:
        outfile.write(f"{key}   {en_dist[key]}\n")

print("Optimizing German...")
de_alpha, de_dist, de_cond_probs, de_min_ppl = build_optimized_model(dict(init_trigram_counts), vocab_size, de_training, de_dev)

f ='assignment1-data/model.de' 
with open(f, 'w') as outfile:
    for key in de_dist:
        outfile.write(f"{key}   {de_dist[key]}\n")

print("Optimizing Dutch...")
nl_alpha, nl_dist, nl_cond_probs, nl_min_ppl  = build_optimized_model(dict(init_trigram_counts), vocab_size, nl_training, nl_dev)

print("Optimizing Danish...")
da_alpha, da_dist, da_cond_probs, da_min_ppl = build_optimized_model(dict(init_trigram_counts), vocab_size, da_training, da_dev)

print("Optimizing Spanish...")
es_alpha, es_dist, es_cond_probs, es_min_ppl = build_optimized_model(dict(init_trigram_counts), vocab_size, es_training, es_dev)

f ='assignment1-data/model.es' 
with open(f, 'w') as outfile:
    for key in es_dist:
        outfile.write(f"{key}   {es_dist[key]}\n")

print("Optimizing French...")
fr_alpha, fr_dist, fr_cond_probs, fr_min_ppl = build_optimized_model(dict(init_trigram_counts), vocab_size, fr_training, fr_dev)

print("Optimizing Italian...")
it_alpha, it_dist, it_cond_probs, it_min_ppl = build_optimized_model(dict(init_trigram_counts), vocab_size, it_training, it_dev)

print("Optimizing Portuguese...")
pt_alpha, pt_dist, pt_cond_probs, pt_min_ppl = build_optimized_model(dict(init_trigram_counts), vocab_size, pt_training, pt_dev)

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

##################### GENERATE RANDOM SEQUENCES ###########################

print("\nGenerating random sequence (model-br.en)...")
print(generate_from_LM(model_br_dist, 300))

print("\nGenerating random sequence (English)...")
print(generate_from_LM(en_dist, 300))

print("\nGenerating random sequence (German)...")
print(generate_from_LM(de_dist, 300))

print("\nGenerating random sequence (Dutch)...")
print(generate_from_LM(nl_dist, 300))

print("\nGenerating random sequence (Danish)...")
print(generate_from_LM(da_dist, 300))

print("\nGenerating random sequence (Spanish)...")
print(generate_from_LM(es_dist, 300))

print("\nGenerating random sequence (French)...")
print(generate_from_LM(fr_dist, 300))

print("\nGenerating random sequence (Italian)...")
print(generate_from_LM(it_dist, 300))

print("\nGenerating random sequence (Portuguese)...")
print(generate_from_LM(pt_dist, 300))

###################### EVALUATE ALL MODELS PER SENTENCE ####################
num_correct = 0
num_incorrect = 0
print("\nEvaluating on English test set...")
for sent in en_test:
    prediction, perplexities = classify(per_lang_cond_probs, [sent])
    if prediction == "english":
        num_correct += 1
    else:
        num_incorrect += 1
print(f"num_correct = {num_correct}, num_incorrect={num_incorrect}")

num_correct = 0
num_incorrect = 0
print("Evaluating on German test set...")
for sent in de_test:
    prediction, perplexities = classify(per_lang_cond_probs, [sent])
    if prediction == "german":
        num_correct += 1
    else:
        num_incorrect += 1
print(f"num_correct = {num_correct}, num_incorrect={num_incorrect}")

num_correct = 0
num_incorrect = 0
print("Evaluating on Dutch test set...")
for sent in nl_test:
    prediction, perplexities = classify(per_lang_cond_probs, [sent])
    if prediction == "dutch":
        num_correct += 1
    else:
        num_incorrect += 1
print(f"num_correct = {num_correct}, num_incorrect={num_incorrect}")

num_correct = 0
num_incorrect = 0
print("Evaluating on Danish test set...")
for sent in da_test:
    prediction, perplexities = classify(per_lang_cond_probs, [sent])
    if prediction == "danish":
        num_correct += 1
    else:
        num_incorrect += 1
print(f"num_correct = {num_correct}, num_incorrect={num_incorrect}")

num_correct = 0
num_incorrect = 0
print("Evaluating on Spanish test set...")
for sent in es_test:
    prediction, perplexities = classify(per_lang_cond_probs, [sent])
    if prediction == "spanish":
        num_correct += 1
    else:
        num_incorrect += 1
print(f"num_correct = {num_correct}, num_incorrect={num_incorrect}")

num_correct = 0
num_incorrect = 0
print("Evaluating on French test set...")
for sent in fr_test:
    prediction, perplexities = classify(per_lang_cond_probs, [sent])
    if prediction == "french":
        num_correct += 1
    else:
        num_incorrect += 1
print(f"num_correct = {num_correct}, num_incorrect={num_incorrect}")

num_correct = 0
num_incorrect = 0
print("Evaluating on Italian test set...")
for sent in it_test:
    prediction, perplexities = classify(per_lang_cond_probs, [sent])
    if prediction == "italian":
        num_correct += 1
    else:
        num_incorrect += 1
print(f"num_correct = {num_correct}, num_incorrect={num_incorrect}")

num_correct = 0
num_incorrect = 0
print("Evaluating on Portuguese test set...")
for sent in pt_test:
    prediction, perplexities = classify(per_lang_cond_probs, [sent])
    if prediction == "portuguese":
        num_correct += 1
    else:
        num_incorrect += 1
print(f"num_correct = {num_correct}, num_incorrect={num_incorrect}")

################### EVALUATE ALL MODELS PER DOC ######################

num_correct = 0
num_incorrect = 0

#English
prediction, perplexities_en = classify(per_lang_cond_probs, en_test)
if(prediction == "english"):
    num_correct += 1
else:
    num_incorrect += 1

#German
prediction, perplexities_de = classify(per_lang_cond_probs, de_test)
if(prediction == "german"):
    num_correct += 1
else:
    num_incorrect += 1

#Dutch
prediction, perplexities_nl = classify(per_lang_cond_probs, nl_test)
if(prediction == "dutch"):
    num_correct += 1
else:
    num_incorrect += 1

#Danish
prediction, perplexities_da = classify(per_lang_cond_probs, da_test)
if(prediction == "danish"):
    num_correct += 1
else:
    num_incorrect += 1

#Spanish
prediction, perplexities_es = classify(per_lang_cond_probs, es_test)
if(prediction == "spanish"):
    num_correct += 1
else:
    num_incorrect += 1

#French
prediction, perplexities_fr = classify(per_lang_cond_probs, fr_test)
if(prediction == "french"):
    num_correct += 1
else:
    num_incorrect += 1

#Italian
prediction, perplexities_it = classify(per_lang_cond_probs, it_test)
if(prediction == "italian"):
    num_correct += 1
else:
    num_incorrect += 1

#Portuguese
prediction, perplexities_pt = classify(per_lang_cond_probs, pt_test)
if(prediction == "portuguese"):
    num_correct += 1
else:
    num_incorrect += 1

print(f"\nClassifying documents in all languages. num correct: {num_correct}, num incorrect = {num_incorrect}")

prediction, perplexities = classify(per_lang_cond_probs, test)

print (f"\nClassifying the test document. The predicted language is: {prediction.upper()}. The perplexities are {perplexities}")

################### CALCULATE AND VISUALIZE SIMILARITY SCORES ################################

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

columns = ["English", "German", "Dutch", "Danish", "Spanish", "French", "Italian", "Portuguese"]

rows = ["English", "German", "Dutch", "Danish", "Spanish", "French", "Italian", "Portuguese"]

data = np.array([list(similarity_scores[key].values()) for key in similarity_scores])
df = pd.DataFrame(data, columns=columns, index=rows)

print(df)

sns.heatmap(df, annot=True)
plt.tight_layout()
plt.show()