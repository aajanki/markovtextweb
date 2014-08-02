#!/bin/sh

if [ "x$1" = "x" ]; then
    echo "Wordpress export file name missing!"
    exit 1
fi

TOKENIZER_PATH="$( cd "$( dirname "$0" )" && pwd )"

python $TOKENIZER_PATH/wpextract.py "$1"

mkdir -p data
cat posts/* | python $TOKENIZER_PATH/tokenize.py > data/tokens
