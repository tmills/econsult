# eConsult
The goal of this project is to build systems for segmenting clinical questions to facilitate data mining.
We are building a proprietary dataset (with protected health information) but we will also run on datasets that are publicly available if they contain the annotations we need.

## Installation
Dependencies are listed in pip. python3.6 and pytorch 0.4.1 are minimum requirements for the flair library we depend on. To install flair, you should checkout that repo (https://github.com/zalandoresearch/flair) somewhere else and run:

```pip install -e <flair directory>```

## Pre-processing
### Focus dataset
Download the CHQA dataset: https://lhncbc.nlm.nih.gov/project/consumer-health-question-answering (Question type data) and:

```mkdir chqa```

```python chqa2conll.py <question type xml file> chqa```

This will create a file called focus.conll in the chqa directory. To train the flair models we need to split this into a train, test, and dev set. Here is one way to do so:

```tail -5651 focus.conll > test.txt```

```head -16895 focus.conll > train.txt ```

```head -22499 focus.conll | tail -5604 > dev.txt```

### Question Decomposition dataset
Download the QDE dataset: https://lhncbc.nlm.nih.gov/publication/pub9272 (Question decomposition data) and run:

```unzip <qde zip file download>```

```mkdir qde```

```python qdecomp2conll.py <unzipped qde directory> qde```

This will create a file called qde.conll in the qde directory. To split into train, test, and dev set:

```head -37981 qde.conll > train.txt```

```tail -10891 qde.conll > test.txt```

```tail -16280 qde.conll | head -5389 > dev.txt```

## Training
Without changes, the default script runs a sequence model with glove embeddings. See the flair repo for how to modify the model to run with more sophisticated pre-trained/contextualized embeddings. The first run with any new model may take a while to download the model resources.

```python flair_train_chqa_focus.py chqa```

If you want to run on the chqa dataset, otherwise replace chqa with qde (or whatever directory contains the question decomposition data). 

This script will save its best model in ```resources/taggers/temp/best-model.pt```, as hard-coded in the script. Modify the script to change the file save location.

## Running
This simple script will read lines from standard input and print out tag predictions for each token:

```cat <file-with-lines> | python flair_tag_lines.py <model file>```

