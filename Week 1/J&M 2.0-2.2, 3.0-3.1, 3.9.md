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
	1. /Column [0-9]+ \*/ matches Column and one number and then any number of spaces
	2. /(Column [0-9]+ \*)\*/ matches any number of "Column # " with any number of spaces between (ie any number of the previous expression)
4. Operator Precedence Heirarchy
		1. Parentheses ()
		2. Counters * + ? {}
		3. Sequences and anchors 
		4. Disjunction |
5. Greedy-- always match largest string that fits the pattern
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
## Words
