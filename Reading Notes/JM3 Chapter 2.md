
# Words

**Corpora** are computer readable collections of speech or text. 
1. Punctuation critical for word boundaries, some aspects of meaning (questions, quotes, exclamations). Sometimes treated as separate words.
**Utterance** is the spoken correlate of a sentence. It can have **disfluencies**
1. Fragments (broken off partial words)
2. Fillers/filled pauses (um, uh, etc)
3. Sometimes helpful to keep them in transcription

Types vs Instances
1. Types are the total number of distinct words
2. Instances are the total number of running words in the corpus
	1. Still some ambiguity-- for example capitalization could be or not be a different type (in speech recognition it's not a different type, in named entity recognition it definitely is)
Herdan's Law/Heaps Law
1. $|V| = kN^{\beta}$ 
2. Size of vocabulary grows faster than the square root of the size of the corpus

Wordforms vs Lemmas
1. Two different inflections (wordforms) belong to the same lemma
2. Dictionary entries/boldface form-- rough approximation (upper bound) on the number of lemmas (since some lemmas have multiple boldface forms)
3. Often times in NLP we operate on tokens rather than words

# Corpora

NLP algorithms are more useful when they apply crosslinguistically. But algorithms tend to be developed for and tested on English (or other official languages of large industrial nations). 
1. Even English isn't standard-- consider AAVE or code switching contexts
2. Consider genre variation, demographic variation, and time period-- all of these affect the language 

When developing computational models from a corpus, use a Datasheet or Data Statement, specifying such properties as:
1. Motivation (why was the corpus collected, by whom)
2. Situation (context where the corpus was spoken/written)
3. Language variety (including region/dialect)
4. Speaker demographics
5. Collection process (size of data, sampling, consent, preprocessing and metadata)
6. Annotation process (what was the process, who did it, how were they trained, etc)

# Unix Tools for Word Tokenization

Three types of text normalization
1. Tokenization (segmenting of words)
2. Normalizing word formats
3. Sentence segmentation

Unix commands
1. `tr -sc ’A-Za-z’ ’\n’ < sh.tx` to replace every nonalphabetic character with a newline (tr does the replacement, s flag squeezes into one output, c flag complements the pattern string)
2. `tr -sc ’A-Za-z’ ’\n’ < sh.txt | sort | uniq -c` pipes the output into sort and then counts the unique words
3.  `tr -sc ’A-Za-z’ ’\n’ < sh.txt | tr A-Z a-z | sort | uniq -c` will lowercase everything first
4. `tr -sc ’A-Za-z’ ’\n’ < sh.txt | tr A-Z a-z | sort | uniq -c | sort -n -r` will then sort again by frequency (rather than alphabetically), in reverse order
	1. Highest counts to the **function words**

Need more sophisticated tokenization for other languages, although some unix tools can handle unicode characters.

# Word and Subword Tokenization

## Top down (rule based) tokenization

Unix commands above strip punctuation, which we usually want to keep in NLP. Can be useful syntactically/semantically, but also word-internal punctuation like Ph.D. or cap'n, special characters in prices, dates, urls, hashtags, emails

1. Clitics can be expanded by the tokenizer (what're to what are)
2. Named entity recognition might tokenize "New York" or "rock 'n roll" to one token

Penn Treebank tokenization standard separates clitics, keeps hyphenated phrases together, separates out punctuation

Since it's the first step of NLP, tokenization needs to go fast. So usually use a deterministic regex/FSA. 
1. Deal with ambiguities deterministically-- ie apostrophes behave differently as a genitive, a quotation mark, and a clitic like they're

Character based languages with no spaces (ex Chinese)
1. Sometimes it's better to use hanzi (which are morphemes) rather than full words, cause there are too many words, the hanzi are basic units of meaning, and there's ambiguity in the segmentation of words
2. In Japanese and Thai, the characters aren't full units of meaning, so word segmentation is required. 

## Byte-pair Encoding (Bottom-up Tokenization)

Rather than defining tokens as words or characters, we use data to automatically tell what the tokens should be (this is more common in LLMs). 
1. Training and test corpora
2. **Subwords** are tokens smaller than words-- could be arbitrary substrings or meaningful units like morphemes

Two parts to the tokenizer:
1. Token learner-- induces a vocabulary/set of tokens from training data (sometimes segmented by whitespace)
2. Token segmenter takes a raw test corpus sentence and segments it into tokens from the above vocabulary
3. Some examples are byte pair encoding, unigram language modeling, sentencepiece library (generally people use this to refer to ULM)

### Byte Pair Encoding
1. Begins with vocab that's just the individual characters
2. Finds the two symbols that most frequently go together and merges them, adding the merged symbol to the alphabet and replacing the pair with the merge in the corpus
3. Continue until $k$ merges have been performed and $k$ tokens have been added into the vocabulary
4. Generally run word internally rather than across word boundaries
5. Then used to tokenize a test sentence, greedily starting in the order we added the merges to the training vocabulary (so frequency in test data doesn't have an effect)
6. In large datasets, generally every word gets represented by full symbol in the vocab, only rare words represented as sum of parts









