# Discorn Project

![Build status](https://jenkins.colabois.fr/job/Discorn%20Github/job/Discorn/job/master/badge/icon)

Discorn is an **encrypted and decentralized chatting protocol** based on cryptocurrencies.

# Useful links

* [Latest Discorn Library documentation](https://moriya.zapto.org/docs/discorn/master/)
* [Latest Discorn Protocol documentation](https://moriya.zapto.org/docs/discorn/latex/master/main.pdf)

# Contributing

Contributions are made via GitHub issues and pull requests. [Gitsokyo](https://moriya.zapto.org/gitsokyo/Discorn/Discorn) is now only a mirror.

Fork the project on github then clone your fork.
The project runs Python 3.8.
Dependencies are managed using **Pipenv**.

Development environement :

``` bash
~ git clone <fork url>
~ cd Discorn
~ pipenv sync --dev
```

Building Library Documentation (results are in doc/sphinx_src/build/html/)

``` bash
~ make sphinx
```


Building Protocol Documentation (requires pdflatex, results are in doc/sphinx_src/build/html/)

``` bash
~ make latex
```

Building the UI files (GUI)

``` bash
~ make ui
```

# Using Discorn

Discorn is still in Developpement phase. It is absolutely not usable in any way.

# Python Implementation

## Installation (Pipenv)

``` bash
~ git clone https://moriya.zapto.org/gitsokyo/Discorn/Discorn.git
~ cd Discorn
~ pipenv install
```

## Qt Gui

``` bash
~ make gui && python -m Gui.main
```

Here's how it looks so far.  
![GUI Screenshot](MD-Assets/Wallet.png)

# Why?

Computers bring with them a brand new problem: **It has become hard to get forgotten.**  
Everything one shares with a company over the internet is potentially stored forever.  
Malicious entities such as potential future governments might use such data against part of the population and **endanger democracy**.

We defend a **basic right to privacy** and we are going to claim it no matter what thanks to **cryptography**.

Encrypted and Federated chatting apps exists. The main example is obviously [Matrix](https://matrix.org/)  
However, Federated software is flawed: They are instance based, and running a personnal instance is hard, requires perfoming hardware and requires registering a Domain Name.
About matrix, it leaks several features that makes private alternatives more interesting.

But why Federated ? Let's go fully decentralized.  

**Bitcoin** shows a new way of creating software over the Internet, and beyond.
Its fundamentals are:

* A decentralized consensus (about order of events and current time),
* Incentivising node owners to help secure the network by taking part in the vote.

Such a system can be used for many applications and it has been.

What does the end user win when using Discorn?  
Privacy is the main one.
Discorn is mainly inspired by Discord, as we find that Discord is more or less the way chatting app should look like.
But Discorn is **open-source** and **decentralized**, this means that people will be able to modify Discorn as they wish with no fear of getting banned, and potentially will have more features than Discord.

# How?

Discorn is inspired by Bitcoin, Cryptonote and Discord, so we will use concepts from them.

Discorn will be organised in **Guilds**.  
A Guild is either owned by someone or is fully decentralized.
To each Guild is attached a **Blockchain** and **Cryptocurrency** and a **Database of events**.
The Blockchain's proof of work algorithm is Cryptonight, as we believe cpu-mining is what we should aim for.
