# Words and Transducers

Not every plural works like "woodchuck" does, for example goose to geese, peccary to peccaries, fish to fish. 
1. Orthographic rules for spelling changes like peccaries
2. Morphological rules for different ways of forming the plural, like fish and geese

Morphological parsing is breaking down a word into composite morphemes (parsing in general is breaking down an input into some sort of linguistic structure). The input form is called the surface form.

We can't just store all the different variants of the same word in a dictionary and parse by lookup. But these (**productive**) suffices apply to all or most words of a given category, including new words introduced to the dictionary. So it's better to encode these rules using a **finite state transducer**. 

For information retrieval, we might not need to know that foxes is plural but just that it relates to fox. So in that case we do **stemming** (stripping the ending) using an algo called **Porter stemmer**. 

**Lemmatization** is finding the common lemma between words, for example mapping sang and sung to sing. 

**Tokenization/word segmentation** is the task of separating words out from running text. In English it's often but not always by spaces. 

**Minimum Edit Distance** tells us how similar two words are orthographically, which can for example be used in spelling correction. It's an alternative to morphological parsing to compare how similar 2 words are orthographically. 

## Survey of English Morphology 

**Morpheme** is the minimal meaning-bearing unit of language. For example fox contains one morpheme, and foxes contains 2 (fox, plus the plural marker). Two main types:
1. Stems-- main meaning
2. Affixes (prefixes, suffixes, infixes, circumfixes)
	1. One word can have many affixes
	2. Agglutinative languages tend to stack many affixes
3. Four ways to combine morphemes to create words
	1. Inflection-- combining a stem with a morpheme to create a word in the same class as the stem, with some syntactic function like agreement
	2. Derivation-- combine a stem with a morpheme to create a word of a different class. For example computer (noun) to computerize (verb) to computerization (noun again)
	3. Compounding-- combination of stems, for example dog and house to doghouse
	4. Cliticization-- combination of a stem with a **clitic**, which behaves syntactically as a word but is reduced in form and attached to another word (I've from I + have)
## Inflectional Morphology

English has pretty limited morphology.
1. Nouns have two types of inflection: 
	1. Plural suffix
		1. Can be regular or irregular 
		2. -s normally, -es after certain sounds
		3. Orthographic change from y to -ies
	2. Possessive suffix
		1. Written 's for regular singular nouns and plurals that don't end in -s (ie children)
		2. Usually written with lone apostrophe for names in -s -z and regular plurals
2. Verbs have more complicated inflection than nouns in English
	1. Main verbs, modals, primary verbs (be, do, have)
	2. Regular verbs all have the same inflections to indicate the same things (stem, -s 3rd person ending, -ing participle, -ed past participle)
		1. Productive, ie automatically includes new words that enter the language (ie fax, faxes, faxing, faxed)
	3. Irregular verbs often have 5 forms but can have as many as 8(be) and as few as 3 (cut, hit). Not as many in number, but they are frequently used verbs. 
	4. Some basic uses:
		1. the first principle part is used for infinitives and simple present outside of 3sing
		2. the second is used for 3sing pres
		3. the third is also used for gerunds and progressive tenses
		4. the fourth is used in perfects and passives
	5. In addition to matching of suffixes to stems, need to also capture spelling changes at morpheme boundaries, for example doubling of consonant (beg to begging and begged), addition of k to c (picnic to picnicking), dropping of silent e (merge to merging), and -es replacing -s in various contexts, y to ies 
	6. English verb inflection is still pretty simple! Compare for example to all the endings in Spanish
## Derivational Morphology

English has pretty complex derivational morphology compared to other languages (unlike it's inflectional morphology).

1. Nominalization-- formation of nouns, usually from verbs or adjectives (computerization, apointee, killer, fuzziness)
2. Adjectives can also be formed from nouns and verbs (computational, embraceable, clueless)
3. In English, tends to be less productive (for example only -ize verbs can take -ation)
4. Subtle differences between nominalizing suffixes (sincerity vs sincereness)

## Cliticization

Clitics preceding a word are proclitics, following a word are enclitics. 
1. English clitics are usually aux verbs (am to 'm, are to 're, is to 's, will to 'll, have to 've, has to 's, had to 'd, would to 'd)
2. Ambiguous! Some of them can mean different original words
3. English clitics are easy cause of the apostrophe. Not so in other languages like Hebrew and Arabic (which do definite articles with a proclitic)

## Non-Concatenative Morphology

Not all languages just put the morphemes together in order. For example Tagalog infixation intermingles the morphemes. 

**Templatic/root-and-pattern** morphology common in Semitic languages. ie Hebrew has LMD for "learn" then lamad for past tense, limed for taught, lumad for "was taught" ie you fit the consonants into the consonant-vowel pattern for the particular grammatical form.

## Agreement 

In English, the subject and verb must agree in number. In many other languages, there is must be agreement of grammatical gender. Sometimes when there's too many we call them noun classes instead of genders. Gender is sometimes marked on a noun, other times it's lexical information that you just have to know. 

# Finite State Morphological Parsing

Parsing takes a surface word and pulls out the stem and assorted morphological **features** that give you additional info about the stem. 

Sometimes there's an ambiguous morphological parse. At this point we just get every valid one.

How to build a parser:
1. Lexicon: list of stems and affixes and info about them (ie is it a noun or verb stem)
2. Morphotactics: Model of morpheme ordering that explains which classes of morphemes follow which other ones in a word
3. Orthographic/spelling rules: spelling changes when two morphemes combine (ie cities from citys)

# Construction of a Finite-State Lexicon 

Simplest lexicon would have every word in the language. This is impractical (too many words, new ones being added), so instead store stems and affixes, and then morphotactics telling us how to put them together. 

Morphotactics represented with FSA, where each arc is a category of morphemes (reg-noun, plural-s, irreg-pl-noun etc). 
1. Nouns: reg-noun, irreg-pl-noun, irreg-sg-noun, pl-affix
2. verbs: reg-verb-stem, irreg-verb-stem, irreg-past-stem, past-ed, past-part-ed, pres-part-ing, 3sg-s
3. Derivational morphology more complex-- for example we can't have an un- arc on every adjective FSA cause you can't be unbig
4. So there's only a transition with adj-root-1 (adjectives that can take un and ly) and adj-root-2 (other adjectives) get rejected

Morphological recognition: problem of determining if input string of letters makes up legit English word. 
1. Plug sub-lexicon into each morphotactic FSA, essentially expand it out with the letters of each morpheme
## Finite State Transducers

FST is a finite automaton that maps two sets of symbols, ie a two-tape FSA. Enhanced because it shows the relation between sets of strings.
1. Recognizer-- accepts if stringpair input is in the stringpair language
2. Generator-- outputs a pair of strings in the language
3. Translator-- reads input string, outputs another
4. Relater-- computes relations between sets

For morphology, we use it as a translator from strings of letters to strings of morphemes.

Formal definition:
1. $Q$ a finite set of $N$ states $q_0... q_{n-1}$ 
2. $\Sigma$ finite set corresponding to input alphabet
3. $\Delta$ finite set corresponding to output alphabet
4. $q_0 \in Q$ the start state
5. $F \subseteq Q$ the set of final states
6. $\delta(q,w)$ the transition function or matrix between states. So given $q \in Q$ and $w \in \Sigma^*$, returns a set of new states $Q' \in Q$ . So $\delta$ is a function from $Q \times \Sigma^* \to 2^Q$ (which is the number of possible subsets) 
7. $\sigma(q,w)$ the output function giving the set of possible output strings for each state and input. Given a state $q \in Q$ and string $w \in \Sigma^*$, then $\sigma(q,w)$ gives a set of output strings, each a string $o \in \Delta^*$. Thus $\sigma$ is a function $Q \times \Sigma^* \to 2^{\Delta^*}$

FSAs are isomorphic to regular languages, FSTs are isomorphic to regular relations-- sets of pairs of strings.
1. Closed under union
2. In general not closed under difference, complementation or intersections
3. Two additional properties
	1. Inversion of $T$, $(T^{-1})$, simply switches the input and output labels. 
	2. Composition, if $T_1$ is a transducer from $I_1$ to $O_1$ and $T_2$ is a transducer from $O_1$ to $O_2$ , then $T_1 \circ T_2$ maps from $I_1$ to $O_2$ 

Inversion is useful cause it's easy to switch from a parser to a generator. 

Composition is useful cause you can replace two transducers in series with one more complex transducer.

1. Projection of FST is the FSA produced by just one side of the relation (upper/first, then lower/second)

## Sequential Transducers and Determinism

Nondeterministic FSTs, like NFSAs, require search algorithms which are slow. But not every FST can be turned deterministic like FSAs can. 

Sequential transducers-- subtype of transducers that are deterministic on input. Epsilons can be in the output string but not the input. Only one symbol in the input alphabet can label a transition out of a given state. #question What does it mean to be $2^{\Delta^*}$

But anyways, the inverse of the sequential transducer isn't necessarily sequential, cause the output doesn't have to be unique for every transition.

1. Subsequential transducer generates additional output strings at the final states (concatenated onto the output produced so far). But with no additional input/the input computations have terminated.
2. Important because they are way more efficient than the nondeterministic equivalents.
	1. But they can't handle ambiguity... 
3. p-subsequential transducer allows $p \geq 1$ final output strings to be associated with the final state. Which allows for a finite amount of ambiguity
	1. Many (but not all) morphological rules can be p-subsequentialized

# FSTs for Morphological Parsing

Finite state morphology represents a word as a correspondence between lexical level (concatenation of morphemes) and surface level (letters/spelling).
1. Upper tape= lexical
2. Lower tape = surface 
3. **Two level morphology**-- each arc has a single symbol from each alphabet
	1. Combine $\Sigma$ and $\Delta$ into a single alphabet $\Sigma'$ so then $\Sigma' \subseteq \Sigma \times \Delta$. $\Sigma$ and $\Delta$ bay also include $\epsilon$ 
	2. Pairs of symbols in $\Sigma'$ are called **feasible pairs** 
	3. Symbols often map to themselves, called **default pairs**
4. Note, ^ represents morpheme boundary and \# represents word boundary. 
	1. **Intermediate** tapes show morpheme boundary markers in the output/surface tape
# Transducers and Orthographic Rules

Need to deal with spelling/orthographic rules as well. Take input (simple concatenation of morphemes) and give output as correctly spelled surface word.
1. fox+N+Pl -> fox^s# -> foxes

$\epsilon \to e/\{x, s, z\} \hat{} s\#$      

1. This basically means, replace $\epsilon$ with $e$ between x/s/z at a morpheme boundary and s at a word boundary
2. Replacing the $\epsilon$ is basically inserting something since it's an empty transition


The key for an orthographic rule is to only make that specified change, allowing all other strings to pass through unchanged (ie we'd only see $\epsilon : e$ where we'd expect the e to be inserted for a plural).

Make sure to work through the example. 

![[Pasted image 20240917200832.png]]
$q_0$ is the initial state and contains all the letters besides the specified ones, the beginning/end of word symbols, and $\epsilon$. You go to $q_1$ once you see one of z, s, x. You progress to $q_2$ at the morpheme boundary, stay where you are if another z, s, x, and return to start on anything else (cause then it's not a plural). At $q_2$ if you place the s from the lexical structure into the surface structure right away, you get sent to $q_5$, which has no valid transition for the last symbol #, so you fail. So you have to take instead the $\epsilon$ route, which inserts e into the surface structure and brings you to $q_3$, which has a valid transition for the final s in $q_4$, which sends you on the word end to valid accepting state $q_1$. 

