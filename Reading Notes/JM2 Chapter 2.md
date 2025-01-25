# Regular Expressions, Tokenization, Edit Distance

Early chatbot ELIZA mimics Rogerian psychotherapist by pattern matching input phrases into suitable outputs.
1. Regular expressions extract strings from documents
2. Text normalization to convert text to convenient, standard form
	1. Tokenizing words from running text
	2. May also need to tokenize emojis and hashtags
	3. Harder in languages without spaces between words
3. Lemmatization to determine if words have the same root
	1. Stemming-- strips suffix from word
4. Sentence segmentation
5. Edit distance is how similar two strings are based on the number of edits to transform one to the other (insertion, deletion, substitution)
## Regular Expressions

Used in Unix tools like grep and editors like vim and emacs, but particularly useful for search text, ie a pattern to match and a corpus to search. For example grep takes in a regex and returns every line of the input doc that matches that expression.

Can return all matches, or just the first one. Many variants, we'll use the extended version. 

## Regular Expression Patterns

1. Concatenation of characters in sequence. i.e. to search for *woodchuck* we just type /woodchuck/
	1. Single character or a sequence
	2. Case sensitive
2. Disjunction \[Ww] matches either w or W
3. Range \[2-5] matches any one of 2, 3, 4, 5
4. Square brackets with caret at the beginning \[^A-Z] specify what a single character cannot be
	1. So the above would match the first single character that's not a capital letter
5. ? matches the previous character or nothing
	1. /woodchucks?/ matches woodchuck or woodchucks
6. Kleene * matches zero or more occurrences of the previous character or expression 
	1. /a*/ empty string or any number of a's
	2. /\[0-9]\[0-9]\*/ matches an integer (with at least one digit)
		1. Use Kleene + instead to match one or more 
7. Wildcard /./ matches any single character (besides carriage return)
	1. wildcard used with kleene star to match any string of characters 
8. Anchors anchor a regex to particular places in the string
	1. ^ matches start of line
	2. $ matches end of line
	3. \\b matches word boundary 
		1. \\bthe\\b matches the but not other
		2. it doesn't have to be a space, for example it'll match after anything not a letter, underscore, or digit
	4. \\B matches non word-boundary
## Disjunction, Grouping, and Precedence

1. Disjunction operator /cat|dog/ matches "cat" or "dog"
2. Sequences take precedence over pipe
	1. /guppy|ies/ matches "guppy" or "ies" rather than "gupp" + ("y" or "ies")
	2. So we do /gupp(y|ies)/ so everything in the parens is treated like one character to the surrounding operators
3. Kleene* unlike | applies by default to a single character rather than a sequence. 
	1. /Column [0-9]+ \*/ matches Column and one or more digits and then any number of spaces
	2. /(Column [0-9]+ \*)\*/ matches any number of "Column # " with any number of spaces between (ie any number of the previous expression)
4. Operator Precedence Hierarchy 

		1. Parentheses ()
		2. Counters * + ? {}
		3. Sequences and anchors 
		4. Disjunction |
6. Greedy-- always match largest string that fits the pattern
	1. Can enforce non-greedy matching with ?
		1. \*?  and +? match as little as possible
## A Simple Example

Match the word "the" : /the/ won't work because it won't get "The" at the beginning of a sentence. /\[tT]he/ won't work because it'll match the embedded in other words (like "other"). So we specify word boundary on either side /\\b\[tT]he\\b/. 

That only words when we don't want underscores or numbers as word boundaries. But what if we do want "the123" to match. So we remove alphabets on either side: /\[^a-zA-Z]\[tT]he\[^a-zA-Z]/.

But that won't match the at the beginning of a line cause the first grouping forces a (non alphabetic) character before it. So we specify we want either the beginning of a line or a non-alphabetic character, and the same at the end.

/(^|\[^a-zA-Z])\[tT]he(\[^a-zA-Z]|$)/

1. Increase precision by removing false positives
2. Increase recall by minimizing false negatives
## More Operators
1. Aliases for common ranges 
	1. \\d any digit
	2. \\D any nondigit
	3. \\w any alphanumeric_
	4. \\W any non alphanumeric_
	5. \\s any whitespace
	6. \\S any non whitespace
2. {3} specifies three of the previous character or expression
	1. Can also come in ranges i.e. {n,m} from n to m occurrences of the previous char or expression
	2. {n,} at least n
	3. {,m} at most m
3. Escape special characters with backslash
4. tab and newline with \\t and \\n
## A More Complex Example

"At least 6 GHz and 500GB of disk space for less than $100"

1. Match the price 
	1. Dollar sign doesn't have to be escaped at the beginning of the expression
	2. Want dollar format and dollar/cent format
	3. Limit the dollars to less than 100
	4. /(ˆ|\W)$[0-9]{0,3}(\.[0-9][0-9])?\b/ 
## Substitution, Capture Groups, ELIZA

1. Substitutions allow a string characterized by a regex to be replaced by another
	1. s/colour/color/
2. Number operator refers back to particular subpart of the matched pattern, a capture group
	1. s/([0-9]+)/<\1>/
	2. Places the matched number in brackets
	3. /the (.*)er they were, the \1er they will be/ 
	4. the 1 is replaced by whatever matches the first capture
3. Every time you use a capture group, the match is stored in a numbered register
	1. /the (.*)er they (.*), the \1er we \2/
	2. Capture groups numbered in the order they appear
4. Sometimes we have a noncapturing group/ just want the parens for order of operations
	1. /(?:some|a few) (people|cats) like some \1/
	2. So people|cats goes into the 1
5. ELIZA is just a cascade of regex substitutions
	1. ie. "I am depressed" -> "You are depressed"
	2. Then matching and replacing other patterns

![[Pasted image 20240915013252.png]]
## Lookahead Assertions

Sometimes we need to look ahead to see if a pattern matches without advancing the pointer to where we are in the text. That way we can deal with the pattern if it occurs, but if it doesn't then check for something else instead. 
1. Zero width
2. (?=pattern) is true if the pattern occurs
3. (?!pattern) is true if the pattern does not occur
4. Easy to rule out a special case initially while parsing a complex pattern
# Finite State Automata

Regex is one way of describing a Finite State Automaton (FSA). Any regex can be implemented as an FSA, and every FSA as a regex. FSA, regex, and regular grammars are all ways of describing regular languages, which are a type of formal language. 

## Use FSA to Recognize Sheeptalk

Automaton recognizes a set of strings (for example, all the different sheeptalk strings). Represented as a graph of nodes and arcs, representing states and letters/state transitions. 
1. Start state q0
2. Final state or accepting state, represented with double circle in graph
3. Transitions represented by arcs labeled with letters

Imagine the input string on a tape of cells, with one symbol on each cell. The machine starts at q0, and then if the current symbol on the tape matches an arc out of the current state, advance the tape by 1 cell and advance to the next state of the machine, until we run out of input. At that point, accept the string if in the final state, and reject it otherwise. 

Can also be represented in a state transition table, with rows for each state and columns for each transition, so that the cell at \[state]\[transition] contains the state you move to from your original state via that transition. So in the sheeptalk machine \[0]\[b] brings you to state 1, \[1]\[a] brings you to state 2, etc. If the symbol isn't a valid transition, the cell contains a null.

Formal definition of FSA:
1. $Q = q_0, q_1... q_n$, a finite set of N states
2. $\sum$ , a finite input alphabet of symbols
3. $q_0$ the start state
4. $F$ the set of final states such that $F \subseteq Q$
5. $\delta(q,i)$ the transition function or transition matrix between states, represented by the state transition table. That is, given $q \in Q$ and $i \in \Sigma$, $\delta(q,i) = q' \in Q$. So $\delta$ is a relation from $Q \times \Sigma \to Q$ 

Deterministic algorithm has no choice points-- there is only one thing to do for every input. 

First, a deterministic algorithm for whether an automaton will accept a string (pseudocode)

```
def d_recognize(tape, table):
	index = 0
	curr_state = 0
	while(index < len(tape)):
		if(len(table[curr_state][tape[index]]) == 0):
			return False
		else:
			curr_state = table[curr_state][tape[index]]
			index += 1
	if (curr_state == accept_index):
		return True
	else:
		return False
```

Basically we iterate over the input, checking if each subsequent letter constitutes a valid state transition, reject if there are no valid transitions, and then once the entire input has been traversed, accept or reject if it is/isn't in an accept state.

We can also create a fail state/sink state in the automaton, just so we always have somewhere to go. 

## Formal Languages

A formal language is a set of strings, where each string is composed of symbols from a finite set called an alphabet. In the sheep example, $\Sigma = \{a, b, !\}$. 

A model that can both generate and recognize all and only the strings of a formal language acts as the definition of that formal language. 

Given a model $m$, we use $L(m)$ to mean the formal language characterized by $m$. So for the sheeptalk, $L(m) = \{baa!, baaa!, baaaa!, baaaaa!...\}$. 

The automaton can represent an infinite set in closed form. 

Natural languages and formal languages are not the same, formal languages can represent many other things. But generative grammar attempts to formally define all the possible strings in a natural language. 

## Nondeterministic FSAs 

NFSAs differ from DFSAs in that there may be multiple options for a state transition for a given symbol. For example, in sheeptalk, we might define $a$ arc out of $q_2$ to go to either $q_3$ or back to $q_2$. 

NFSAs, might also have $\epsilon$ transitions, which are state transitions that do not advance the input tape (or indeed, even look at the input pointer). This is nondeterministic because we don't know whether to advance to the next character or follow the $\epsilon$ transition. 

Different ways of dealing with nondeterminism:
1. Backup: mark the input and automaton state at every decision point. That way we can back up and choose a different path if the current one fails
2. Lookahead: look ahead in the input to choose which path 
3. Parallelism: Look at all possible paths simultaneously at the choice point
Nondeterministic algorithm:

```
#returns accept(True) or reject(False)
def nd_recognize(tape, machine):
	agenda = {(initial state of machine, tape[0])}
	curr_search_state = agenda.pop()
	while true:
		if(accept_state(curr_seach_state)):
			return True
		else:
			agenda = agenda + gen_new_states(curr_search_state)
		if (len(agenda) == 0):
			return False
		else:
			curr_search_state = agenda.pop()

#returns set of search states
def gen_new_states(curr_state):
	curr_node = curr_state.node
	index = curr_state.tape_index
	return all (table[curr_node][e], index) and all (table[curr_node][tape[index]], index+1)

def accept_state(search_state):
	curr_node = curr_state.node
	index = curr_state.tape_index
	if (index + 1 = len(tape) and curr_node == machine.acceptState):
		return True
	else:
		return False

```


Essentially the algorithm is, we create a stack of search states, where each search state has the machine state and the index of the tape. As we pop off each state, we check if it is an accepted state. If not, we generate all the possible transitions, which we push to the queue as a tuple of the new machine state and the new tape index. If there aren't any more, we reject. Otherwise, we pop off the next state and proceed until we've reached an accept state. 

Doesn't have to be a stack-- we can do a BFS/FIFO implementation with a queue instead. But that's more space intensive generally. Both of these implementations might hit an infinite loop. We'd rather use dynamic programming or A* for more complicated problems.

All NFSAs can be written as DFSAs (often with many more states), which essentially unwraps the parallel algorithm (rather than the backtracking algorithm).

# Regular Languages and FSAs

Class of languages definable by regex is the same class of languages characterizable by FSAs (EXCEPT MEMORY!!). These are called regular languages. Formal definition:
1. $\emptyset$ is a regular language
2. $\forall a \in \Sigma \cup \epsilon, \{a\}$ is a regular language
3. If $L_1$ and $L_2$ are regular languages, then so are:
	1. $L_1 \cdot L_2 = \{xy| x \in L_1, y \in L_2\}$, the concatenation of $L_1$ and $L_2$ 
	2. $L_1 \cup L_2$, the union or disjunction of $L_1$ and $L_2$
	3. $L_1^*$, the Kleene closure of $L_1$
Where $\Sigma$ is the set of symbols, $\epsilon$ is the empty string, and $\emptyset$ is the empty set. 

Every regex can be written as one of these 3 operations (for example \[wW\] is just an extension of the pipe disjunction)

Regular languages are also closed under the following operations
1. Intersection-- the language containing strings that are in both $L_1$ and $L_2$
2. Difference-- the language consisting of strings that are in $L_1$ that aren't in $L_2$
3. Complementation-- the set of all strings that aren't in $L_1$ 
4. Reversal-- the set of all strings that are the reverse of the strings in $L_1$

Proof of equivalence between regex and FSA is in two parts.
1. Automaton can be built for every regex
	1. Base case (no operators)-- $\emptyset, \epsilon, a \in \Sigma$ 
	2. Induction-- each of the three regex primitive operations can be represented with an automaton
		1. Concatenation-- point the final state of FSA1 to the initial state of FSA2
		2. Closure-- create new final and initial state connected to the original ones by $\epsilon$-transition, connect the original final states back to the original initial states by $\epsilon$-transitions, then put a direct link from the new initial state to the new final state by $\epsilon$-transition, which is the 0 length possibility. (Kleene+ wouldn't need that part) 
		3. Union-- Add a new initial state $q_0'$ and add $\epsilon$ transitions from it to the former initial states of the two machines to be joined. (Possibly also the same for the final states? check on this)
2. Regex can be built for every automaton