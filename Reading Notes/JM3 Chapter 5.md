
# Logistic Regression 

Can be used to classify into two or more classes. 

1. Generative classifier (naive Bayes)
	1. Can be used to create new dog and cat pics
	2. Likelihood means how likely are we to generate this document if we knew it was of class C
2. Discriminative classifier (logistic regression)
	1. Can just tell dogs and cats apart if all dogs are wearing collars, doesn't need to actually produce a dog
	2. Directly computes $P(c|d)$ rather than using likelihood $P(d|c)$ 

Four components of a ML system for classification
1. Feature representation of the input, for each $x^{(i)}$ we have a vector $[x_1... x_n]$ 
2. Classification function that computes $\hat{y}$, the estimated class, with $p(y|x)$-- sigmoid or softmax
3. Objective function to optimize for learning, involving minimizing a loss function to error on training examples. For example, cross-entropy loss function
4. Algorithm for optimizing the objective function, ie stochastic gradient descent

## Sigmoid Function

1. Weights-- number associated with each of the input features, telling you how important that feature is to classification. So "awesome" has a high weight and "awful" has a very negative weight
2. Bias-- the intercept that we add to the weighted inputs
3. $$z = (\sum_{i=1}^{n}w_ix_i) + b$$
4. Or in vector notation, we can write $$z = \mathbf{w} \cdot \mathbf{x} + b$$
5. But nothing guarantees $z$ is between 0 and 1. Weights can be however high. So we pass $z$ through the **sigmoid** function $\sigma(z)$ aka the **logistic function** $$\sigma(z) = \frac{1}{1+ e^{-z}} = \frac{1}{1+ \text{exp}(-z)}$$
6. Takes a real valued number and maps to (0,1)-- nearly linear around 0 and 1 so tends to squash outliers to 0 or 1
7. $P(y=0) = 1 - \sigma(z)$ 
8. $1-\sigma(x) = \sigma(-x)$ 
9. Input to the sigmoid is called the logit (inverse of the sigmoid, log of the odds ratio $\frac{p}{1-p}$)

## Classification with Logistic Regression

1. Decision boundary-- choose class 1 if $P(y=1)|x) > 0.5$ 

### Sentiment Classification
1. Represent each input with some number of features
2. Assume we've already calculated the weights for the features, and the bias
	1. Then plug into $\sigma(\mathbf{w} \cdot \mathbf{x} + b)$ and $1- \sigma(\mathbf{w} \cdot \mathbf{x} + b)$ 
	2. To get $P(y=1|x)$ and $P(y=0|x)$

Other classification tasks and features
1. Any property of the input can be a feature
2. For example, period disambiguation (could be end of sentence or mid-word)
3. Feature interactions, or features that are combinations of other features
4. In classic models, we design the features ourselves based on linguistic knowledge
	1. Or use feature templates, like a bigram template for pairs of words that occur before a period. 
	2. Usually hashed from the string descriptions

Scaling input features
1. Rescale or standardize the features if they have different ranges of values-- **z score**
	1. Basically, find the mean and standard deviation of that feature across all observations, then compute the z-score
	2. $\mu_i = \frac{1}{m}\sum_{j=1}^{m}x_i^{(j)}$
	3. $\sigma_i = \sqrt{\frac{1}{m}\sum_{j=1}^{m}(x_i^{(j)} - \mu_i)^2}$
	4. $x'_i = \frac{x_i - \mu_i}{\sigma_i}$
2. Or we can normalize them to be in range 0 to 1
	1. $x'_i = \frac{x_i - \text{min}(x_i)}{\text{max}(x_i) - \text{min}(x_i)}$

Processing many examples at once
1. Rather than doing a for loop over all the inputs, we can do a matrix operation instead
2. Each row $i$ in the matrix $\mathbf{X}$ is the feature vector of the i-th sample $x^{(i)}$ with dimensions $m \times f$ where $m$ is the number of samples, and $f$ is the number of features per sample
3. $b$ becomes vector $\mathbf{b} = [b,b,b...]$ repeated $m$ times 
4. $\mathbf{\hat{y}} = [\hat{y}^{(1)}... \hat{y}^{(m)}]$ 
5. So then we compute $$\mathbf{y} = \mathbf{Xw} + \mathbf{b}$$
Choosing a classifier
1. Logistic regression has some advantages-- naive bayes depends on conditional independence of the features
2. Naive bayes works better on small datasets and short documents (and it's also quicker and easier since no optimization step)

## Multinomial Logistic Regression 

Also known as softmax regression (or maxent classifier). This is **hard classification** cause it assumes each example belongs to exactly one class. 

Like the sigmoid, the input is $\mathbf{x}$ times a weight vector plus a bias. But now we need a separate weight vector and bias value for each class. 

We use a matrix $\mathbf{W}$ to represent the weights, where each row $k$ in the weight matrix represents the weight vector $w_k$ and has dimensions $K \times f$ where $K$ is the number of classes and $f$ is the number of features.  

$$\mathbf{\hat{y}} = \text{softmax}(\mathbf{Wx} + \mathbf{b})$$
Where $\hat{y}_i = \mathbf{w}_1 \cdot \mathbf{x} + b_1$.

### Features in Multinomial Logistic Regression

Weight for a feature now corresponds to evidence for or against a specific class, so referred to as $f(x,y)$ 

## Learning in Logistic Regression

We want to learn what values of $\mathbf{w}$ and $b$ will make $\hat{y}$ as close as possible to $y$. Requires two metrics:
1. How close the current label $\hat{y}$ is to the gold label
	1. In terms of the distance between the system output and the gold output, which is a loss or cost function 
2. Optimization Algorithm for updating the weights to get closer to $y$ aka minimize the loss function 

## Cross Entropy Loss Function

$L(\hat{y}, y)$ is how much $\hat{y}$ differs from $y$ in the gold label. This function prefers the correct labels of the training data to be more likely-- **conditional maximum likelihood estimation**
1. Choose $w,b$ that maximize the log probability of the true labels on the training data, given the observations $x$. This function is called negative log likelihood loss, or the **cross entropy loss** 

Derivation (for single observation $x$). We want to learn the weights that maximize the probability of the correct label $p(y|x)$
1. Bernoulli distribution, since there are only 2 discrete outcomes
2. Cross entropy loss function $$L_{CE} = -[y\log\sigma(\mathbf{w} \cdot\mathbf{x} + b) + (1-y)\log(1-\sigma(\mathbf{w} \cdot\mathbf{x} + b))]$$
3. Ensures that the probability of the correct answer is maximized implies the incorrect answer is minimized
4. Called the cross entropy loss function because it's the formula for the cross entropy between the true distribution $y$ and our estimated distribution $\hat{y}$ 

## Gradient Descent

Goal is to minimize the loss function $L_{CE}$. We want the parameters (ie weights and bias) which minimize the loss function averaged over all examples $$\hat{\theta} = \text{argmin}_{\theta}\frac{1}{m} \sum_{i=1}^{m} L_{CE}(f(x^{(i)}; \theta), y^{(i)})$$
Basically you want to find where the function's slope is moving most steeply up, and go in the opposite direction. For logistic regression, the loss function is convex, with one global minimum. So we find the gradient of the loss function at the current point, then move in the opposite direction (where the gradient of a function is the vector pointing in the direction of the greatest increase). So like if the slope is negative, we move in the positive x direction if you think of it in two dimensions. 

**Learning rate** $\eta$ tells you how much to move in the gradient direction. $$w^{t+1} = w^t - \eta\frac{d}{dw}L(f(x;w), y)$$ 
Bur we want it in however many dimensions, so instead we take $\nabla L(f(x; \theta), y)$, which is $\frac{\partial}{\partial w_i}L(f(x; \theta),y)$ for all $i$ as a column vector. 

So then the final formula for updating $\theta$ based on the gradient is: $$\theta^{t+1} = \theta^t - \eta \nabla L(f(x;\theta),y)$$
### Gradient for Logistic Regression

What's the gradient of $L_{CE}(\hat{y}, y)$ for one observation vector $x$ is $$\frac{\partial L_{CE}(\hat{y}, y)}{\partial w_j} = [\sigma(\mathbf{w} \cdot \mathbf{x} + b) - y]x_j = (\hat{y} - y) x_j$$
Stochastic Gradient Descent algorithm
1. Stochastic because it chooses a single random example at a time
2. Learning rate $\eta$ is a hyperparameter that must be adjusted-- too low and the algorithm takes too long, too high and it keeps overshooting the correct value
	1. Chosen by algorithm designer rather than learned by the system
3. Basically start from $\theta = 0$ and then calculate the gradient of the loss function when $\theta = 0$ and set the new value of $\theta$ to be the original minus $\eta$ times that gradient. 

Mini-batch training
1. Not always good to train on one example at a time 
2. **Batch training** -- compute the gradient over the entire dataset, which is more accurate but computationally expensive
3. **Mini batch training** -- use a subset of the samples instead, which is more efficient. 
4. Mini batch cross entropy function: gradient is the average of the individual gradients from above $$\frac{\partial \text{Cost}(\hat{y}, y)}{\partial \mathbf{w}} = \frac{1}{m}(\sigma(\mathbf{Xw} + \mathbf{b}) -\mathbf{y})^{\intercal}\mathbf{X}$$
5. 

