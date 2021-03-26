# Discorn Project
-----------------
Discorn is an **encrypted and decentralized chatting** protocol based on cryptocurrencies. test

# Table of contents :
* [Why ?](#Why)
* [How ?](#How)
* [Using Discorn](#Using)
* [Python implementation](#PyImplementation)
    * Installation
    * Qt Gui
* [Protocol Documentation](#protocol-doc)
    * [Blockchain documentation](#blockchain-doc)
    * [Peer to Peer communication](#P2P-doc)

# Why ? <a name="user-content-Why"></a>
-------
Computers bring with them a brand new problem : **It has become hard to get forgotten.**  
Everything one shares with a company over the internet is potentially stored forever.  
Malicious entities such as potential future governments might use such data against part of the population and **endanger democracy**.

We defend a **basic right to privacy** and we are going to claim it no matter what thanks to **cryptography**.

Encrypted and Federated chatting apps exists. The main example is obviously [Matrix](https://matrix.org/)  
However, Federated software is flawed : They are instance based, and running a personnal instance is hard, requires perfoming hardware and requires registering a Domain Name.
About matrix, it leaks several features that makes private alternatives more interesting.

But why Federated ? Let's go fully decentralized.  

**Bitcoin** shows a new way of creating software over the Internet, and beyond.
It's fundamentals are :

* A decentralized consensus (about order of events and current time)
* Incentivising node owners to help secure the network by taking part in the vote.

Such a system can be used for many applications and it has been.

What does the end user win when using Discorn ?  
Privacy is the main one.
Discorn is mainly inspired by Discord, as we find that Discord is more or less the way chatting app should look like.
But Discorn is **open-source** and **decentralized** this means that people will be able to mod Discorn as they wish with no fear of getting banned, and potentially will have more features than Discord.

# How ? <a name="user-content-How"></a>
-------
Discorn is inspired by Bitcoin, Cryptonote and Discord, so we will use concepts from them.

Discorn will be organised in **Guilds**.  
A Guild is either owned by someone or is fully decentralized.
To each Guild is attached a **Blockchain** and **Cryptocurrency** and a **Database of events**.
The Blockchain's proof of work algorithm is Cryptonight, as we believe cpu-mining is what we should aim for.


# Using Discorn <a name="user-content-Using"></a>
---------------
Discorn is still in Developpement phase. It is absolutely not usable in any way.

# Python Implementation <a name="user-content-PyImplementation"></a>
----------------------

## Installation (Pipenv)

``` bash
~ git clone https://moriya.zapto.org/gitsokyo/Discorn/Discorn.git
~ cd Discorn
~ pipenv install
```

## Qt Gui
``` bash
~ python -m Gui.main
```

Here's how it looks so far.  
![GUI Screenshot](MD-Assets/Wallet.png)


# Protocol Documentation <a name="user-content-protocol-doc"></a>
------------------------

## Blockchain <a name="user-content-blockchain-doc"></a>

### Block
A block is seperated in header and body to allow for fast chain downloading.  


|Field        |Type                |Description                                                   |Length  |
|-------------|--------------------|--------------------------------------------------------------|--------|
|Version      |big-endian int      |Block version                                                 |1 byte  |
|Timestamp    |big-endian int      |                                                              |4 bytes |
|Corner count |big-endian int      |Number of Corners included                                    |3 bytes |
|Merkle root  |cryptonote-fast-hash|Root hash of Corners mekrle tree                              |32 bytes|
|Previous hash|cryptonote-slow-hash|Hash of previous block                                        |32 bytes|
|Difficulty   |big-endian int      |The calculated difficulty target being used for this block    |4 bytes |
|Nonce        |raw                 |To allow variations of the header and compute different hashes|4 bytes |
|             |                    |                                                              |        |
|             |                    |                                                              |        |
|             |                    |                                                              |        |
|             |                    |                                                              |        |
|Reward corner|Corner              |Special Corner that has outputs without inputs.               |        |
|Corners      |Corner list         |Corners one after the other                                   |        |

### Corner
A Corner is an enveloppe for several kind of payloads (such as Transactions like in Bitcoin)

|Field       |Type          |Description       |Length |
|------------|--------------|------------------|-------|
|Version     |big-endian int|Message version   |2 bytes|
|Payload flag|big-endian int|Payload identifier|2 bytes|
|Payload     |raw           |                  |       |


## Peer to Peer (P2P) Communication: <a name="user-content-P2P-doc"></a>


### Sending Data:
### Message structure:

|Field       |Type          |Description       |Length |
|------------|--------------|------------------|-------|
|Version     |big-endian int|Message version   |2 bytes|
|Payload flag|big-endian int|Payload identifier|2 bytes|
|Payload     |raw           |                  |       |

- #### IPV4
    Connections are made over **TCP**.  
    Messages are **sliced in chunks** of `CHUNK_SIZE=1024` length
    Chunks are sent **one after the other** over the TCP connection following this pattern :

    |Field |Type          |Description                                        |Length |
    |------|--------------|---------------------------------------------------|-------|
    |Length|big-endian int|Chunk length (MSB first) **if not final** or `FFFF`|2 bytes|
    |Data  |raw           |Actual chunk data                                  |       |




## Network Payloads :

### 1 — Ping:
Send a ping request to Peer.  
**Expected behaviour**: Send a pong message with the same `id`.

|Field|Type          |Description|Length |
|-----|--------------|-----------|-------|
|id   |big-endian int|           |2 bytes|

### 2 — Pong:
Respond to a ping request from Peer.  
**Expected behaviour**: None.

|Field|Type          |Description|Length |
|-----|--------------|-----------|-------|
|id   |big-endian int|           |2 bytes|

### 3 — Heartbeat:
Notify a Peer that the sender is still up. (should be sent `BPM` times per minute)  
**Expected behaviour**: Disconnect if no heartbeat was sent for `TIMEOUT/BPM`

|Field|Type          |Description|Length |
|-----|--------------|-----------|-------|

### 4 — Getguild:
Initiate the **Guild Challenge** sequence.  
(remote gives a salt &rarr;
local hashes the guild with the salt &rarr;
remote checks if any of his guilds matches)  
**Expected behaviour**: Send a Sendguildchallenge with the same `id` and a one time salt.

|Field|Type          |Description|Length  |
|-----|--------------|-----------|--------|
|id   |big-endian int|           |2 bytes |

### 5 — Sendguildchallenge:
Sends a salt for the **Guild Challenge** sequence  
**Expected behaviour**: Send a Solveguildchallenge message with a hash of `raw guild+salt`.

|Field|Type          |Description|Length  |
|-----|--------------|-----------|--------|
|id   |big-endian int|           |2 bytes |
|Salt |raw           |Random data|16 bytes|

### 6 — Solveguildchallenge:
Send a hash of `raw guild+salt` from now on, the salted hash will be called RawGuildChallenge  
**Expected behaviour**: Send a Endguildchallenge message

|Field|Type          |Description            |Length  |
|-----|--------------|-----------------------|--------|
|id   |big-endian int|                       |2 bytes |
|Hash |raw           |`raw guild + salt` hash|32 bytes|

### 7 — Endguildchallenge:
Notifies successful or failed challenge.  
**Expected behaviour**: if successful, both Peers should now use the **salted hash** to reference the common Guild and every exchange about that guild should be **AES encrypted with the raw guild hash** (without salt) as a key.

|Field  |Type          |Description    |Length |
|-------|--------------|---------------|-------|
|id     |big-endian int|               |2 bytes|
|Success|big-endian int|0 if successful|1 byte |

### 8 — Newhead \[Guild]
Notifies remote of a new chain head. (Doesn't send the block, just height and hash)

|Field |Type             |Description                        |Length  |
|------|--------------   |-----------------------------------|--------|
|Guild |RawGuildChallenge|One time Guild identifier          |32 bytes|
|      |                 | *Following data is AES encrypted* |        |
|Height|big-endian int   |New head's height                  |4 bytes |
|Hash  |raw              |New head's hash                    |32 bytes|

### 9 — Getblockheader \[Guild]
Ask remote the block header of the given height

|Field |Type          |Description                      |Length  |
|------|--------------|---------------------------------|--------|
|Guild|RawGuildChallenge|One time Guild identifier      |32 bytes|
|      |              |*Following data is AES encrypted*|        |
|Height|big-endian int|Requested height                 |4 bytes |

### 10 — Blockheader \[Guild]
Sends remote a block header.

|Field |Type             |Description                       |Length  |
|------|-----------------|----------------------------------|--------|
|Guild |RawGuildChallenge|One time Guild identifier         |32 bytes|
|      |                 | *Following data is AES encrypted*|        |
|Header|Block Header     |Requested height                  |4 bytes |