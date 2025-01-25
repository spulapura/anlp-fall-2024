# N-gram language models

Language models/ LMs assign a probability to each possible next word, and then assign a probability to an entire sentence.

1. Choose the sequence more likely to occur -> correlates with the more grammatical variant
2. **Augmentative and alternative communication**-- selecting words from a menu when you can't speak or sign, word prediction suggests likely next words
3. Central to LLMs 

N-gram Models-- from sequences of n words (like bigram for 2 or trigram for 3)
1. N-gram also means "probabilistic model that can estimate probability of a word given n-1 prev words"

## N-Grams

Want to find the probability $P(w|h)$ where $w$ is a given word (i.e. potentially the next one) and $h$ is the history/sequence of previous words. 

We can't just do relative frequency of "blue" following "the water of Walden Pond is so beautifully..."-- since language is **creative** and we invent new sentences all the time. 

Notation notes:
1. Usually operate on tokens, but ok to think of it in terms of words.
2. $P(X_i = \text{"the"})$ simplified as $P(\text{the})$ 
3. Sequence of $n$ words is $w_1... w_n$ or $w_{1:n}$ . So $w_{1:n-1}$ means $w_1... w_{n-1}$, but can also be written as $w_{<n}$ 
4. Joint probability $P({X_1 = w_1, X_2 = w_2...X_n = w_n})$ we can abbreviate $P(w_1, w_2... w_n)$ 

Chain rule of Probability 
$$P(w_{1:n}) = P(w_1)P(w_2|w_1)P(w_3|w_{1:2})... P(w_n|w_{1:n-1}) 
= \prod_{k=1}^{n}P(w_k|w_{1:k-1})$$

Shows the relationship between the joint probability of a sequence and the conditional probability of a word given the previous word. But we don't know how to compute the exact probability of a word given a previous sequence... language is creative!

### The Markov Assumption
1. We can approximate the history with just the last few words
2. **bigram** model approximates the probability of a word given all previous words... using only the conditional probability of the single preceding word
3. That is $P(w_n|w_{1:n-1}) \approx P(w_n|w_{n-1})$ 
	1. This is called the **Markov assumption**-- Markov models assume we can predict the prob of a future unit without looking too far into the past
	2. Generalize to trigram, then to n-gram
	3. For an N-gram model: $$P(w_n|w_{1:n-1}) \approx P(w_n|w_{n-N+1:n-1})$$
	4. Applying the bigram model to the chain rule: $$P(w_{1:n}) \approx \prod_{k=1}^{n} P(w_k|w_{k-1})$$
### How to estimate probabilities

**Maximum Likelihood Estimation (MLE)** 

Get the counts of each bigram from a corpus, normalize so the counts lie between 0 and 1. $$P(w_n|w_{n-1}) = \frac{C(w_{n-1}w_n)}{\sum_w C(w_{n-1}w)}$$ In other words, count the count of the bigram in question, and normalize by dividing by the count of all the other words following the previous word. We can simplify to: $$P(w_n|w_{n-1}) = \frac{C(w_{n-1}w_n)}{C(w_{n-1})}$$
In other words, the denominator is just the total number of times the previous word has occurred (in any bigram). 

General case (N-gram): $$P(w_n|w_{n-N+1:n-1}) = \frac{C(w_{n-N+1:n-1}w_n)}{C(w_{n-N+1:n-1})}$$
This ratio is called the **relative frequency**. 

Normalization by dividing each sell in the bigram chart by the unigram frequency of the row (i.e. total counts of the previous word). 

Linguistic observations: we can see that a verb is most likely followed by a noun (syntactic information), that the personal assistant task usually receives prompts starting with I, and people ask for Chinese food more than English food (context).

Dealing with scale in large n-gram models
1. Log probabilities-- numerical underflow from multiplying too many probabilities between 0-1, log space means we multiply in linear space (multiply logs by adding them). So we get a number that isn't too small, and then we can convert it back to a probability by exponentiating 
2. Longer context
	1. Need to add pseudo-words when the context goes farther back than the beginning of a sentence/farther forward than the end etc
	2. Infini-gram project-- computing the probabilities as needed at inference time rather than doing huge amounts of pre-computation
	3. Efficiency considerations
## Evaluating Language Models: Training and Test Sets

1. Extrinsic evaluation-- embed the LM into an application and see how the application improves. So for example, evaluate the n-gram models as components of a larger system like ASR or translation
2. Intrinsic evaluation-- quality of the model independent of application.
3. Training set-- used to learn the parameters of the model, ie the corpus where we get the counts that are normalized into probabilities for the n-gram model
4. Test set-- held-out, different set of data (not overlapping the training set) used to evaluate the model. Model is no good if it only works on the training set/no new data
	1. Test set should reflect the use case-- i.e. if it's used for speech recognition on chem lectures, test on chem lectures
	2. General purpose models should be tested on a variety of texts
	3. Can train two different models on the training set and see which is better depending on the performance on the test set
5. Evaluation-- "fitting the test set" just means the model assigns a higher probability to the test set 
6. Don't train on the test set-- we'll assign artificially high probability to a particular sentence if we've already seen it. Causes inaccuracies in perplexity
7. Only test on the test set once-- don't want to be adapting the model to the test set implicitly as we make improvements to get a better performance
8. So instead we use a **devset** where we test on an allocated portion of the training set instead of the actual test set. 
9. Want to choose sets so we have the sufficient statistical power to measure a significant difference between two models in the test set
10. Devset should be drawn from same kind of text as training set.

## Evaluating Language Models: Perplexity

Best model predicts the next word and assigns it probability 1 (totally unsurprised by the result). So better models assign higher probability to the correct result, it's not just a matter of getting it right. 

Don't want to use plain probability, since it gets smaller with a longer text, would rather have a normalized per word metric to compare performance on texts of different lengths. Thus, **perplexity**, or the inverse probability of the test set, normalized by number of words (i.e. per word/per token perplexity). $$\text{perplexity}(W) = P(w_1w_2...w_N)^{-\frac{1}{N}} = \sqrt[N]{\frac{1}{P(w_1w_2...w_N)}} $$
So then using the chain rule: $$\text{perplexity}(W) = \sqrt[N]{\prod_{i=1}^N \frac{1}{P(w_i|w_1...w_{i-1})}}$$
Lower perplexity means a better model. Then, using the Markov assumption from before, we can model for a unigram or a bigram:

$$\text{perplexity}(W) = \sqrt[N]{\sum_{i=1}^N\frac{1}{P(w_i)}}$$
$$\text{perplexity}(W) = \sqrt[N]{\sum_{i=1}^N\frac{1}{P(w_i|w_{i-1})}}$$
May also include EOS or sentence start/end tokens, since the word sequence $W$ is the entire test set. 

Perplexity of two LMs is only comparable if they have identical vocabularies. Intrinsic metrics (perplexity) don't necessarily correlate with extrinsic metrics (ASR engine using that LM), but frequently o. 

### Perplexity as Weighted Average Branching Factor
1. Branching factor = number of possible next words that can follow a given word
2. For a training set where each of the 3 tokens has equal probability, no matter what the test set is, the perplexity will be 3. 
3. But if the probabilities aren't even, the weighted branching factor (aka perplexity) can change 

## Sampling Sentences from a LM

**Sampling** from a distribution means choosing random points according to their likelihood. So for a LM, we generate sentences, choosing them according to the likelihood defined by the model. So we're more likely to generate sentences with high probability according to the model. 

So for a unigram, we just choose each word by randomly selecting a word where each word is weighted by probability.

For bigram, we randomly choose from bigrams starting with the start symbol, then from bigrams starting with the first selected word, then from bigrams starting with the next selected word etc. 

## Generalizing vs Overfitting the Training Set

N gram probabilities get very sparse as N increases. So the tendency to overfit the training set also increases. Also if the model is trained on Shakespeare, it won't do a good job of predicting the WSJ and vice versa. 

Can account for some of this in selecting the training set-- make sure the training set matches the genre of the use case, match the dialect or variety (especially when processing social media). Also, we can run our algorithm on subword tokens (like with the BPE algorithm) so you can account for words you've never seen before. 

## Smoothing, Interpolation, and Backoff

**Zeros** (sequences that appear in the test set but not the training set) are problematic because 1. we underestimate the probability of sequences that MIGHT occur, and 2. the whole sample has probability of 0 if even one sequence is 0. And this happens a lot with sparse data. 

1. Laplace Smoothing
	1. Just add one to all of the counts (so 0 becomes 1, 1 becomes 2, etc)
	2. More useful for classification, but good example to introduce the concept 
	3. Unsmoothed MLE: $$P(w_i) = \frac{c_i}{N}$$
	4. Aka **add-one smoothing** 
	5. We need to add one to both the numerator and the denominator to keep it a probability distribution that adds up to 1: accounts for the extra $|V|$ observations we added to the numerator
	6. Can also use an adjusted count $c^*$ which is easier to compare directly with MLE: $$c^*_i = (c_i + 1) \frac{N}{N+V}$$
	7. Then normalize by $N$ to get the probability $P_i^*$ 
	8. **Discounting**-- thinking of it as lowering nonzero counts to get redistributable probability mass for the zeros
	9. So rather than $c^*$ we refer to discount ratio $d_i = \frac{c_i^*}{c_i}$ 
	10. For bigrams: $$P_{\text{Laplace}}(\frac{C(w_{n-1}w_n) + 1}{\sum_w C(w_{n-1}w) + 1}) = \frac{C(w_{n-1}w_n) + 1}{C(w_{n-1}) + V}$$
	11. Reconstructed counts: $$c^*(w_{n-1}w_n) = \frac{[C(w_{n-1}w_n) + 1] \times C(w_{n-1})}{C(w_{n-1}) + V}$$
	12. Looking at the discount ratio, we see that there's a big change in the counts, which we don't really want. 
2. Add-k smoothing
	1. Move a bit less of the probability mass from the seen to the unseen events, add a fractional value $k$ instead $$P^*_{\text{add-k}}(w_n|w_{n-1}) = \frac{C(w_{n-1w_n}) + k}{C(w_{n-1}) + kV}$$
	2. Need to choose an ideal k-- can do it by optimizing on the devset
	3. Also works better for classification-- not as well for language modeling, generates counts with poor variances, inappropriate discounts
3. Language Model Interpolation
	1. Sometimes using less context can give us more information. For example, if we have a trigram that never appears, we might have seen one of its bigrams or unigrams with high frequency
	2. **Interpolation**-- create a new combined probability based on the unigram, bigram, and trigram probabilities $$\hat{P}(w_n|w_{n-2}w_{n-1}) = \lambda_1P(w_n) + \lambda_2P(w_n|w_{n-1}) + \lambda_3P(w_n|w_{n-2}w_{n-1})$$
	3. Weighted average ($\lambda$s sum to 1)
	4. We can also condition the lambdas on the context? #question No idea what this means
	5. Both simple and conditional linear interpolation learned from held-out corpus, where n-gram probabilities are fixed and then we optimize for lambdas using **EM** algorithm 
4. Stupid Backoff
	1. If we don't have the trigram, we try the bigram, and then the unigram etc
	2. To get a proper probability distribution, should technically discount. But instead we do stupid backoff 
	3. ![[Pasted image 20241003212132.png]]








