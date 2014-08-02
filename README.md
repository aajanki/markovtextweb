# markovtextweb

Web server that generates random text using Markov chains.

The Markov chain is learned from posts in a Wordpress blog.

## Prerequisites

You will need [Leiningen][1] 1.7.0 or above and [Python][2] 2.7 or
above installed.

[1]: https://github.com/technomancy/leiningen
[2]: https://www.python.org/

## Preprocessing Wordpress input text

Export your Wordpress blog contents into a WordPress eXtended RSS
file. Let's assume that the file is called wordpress.xml.

Generate tokens for the Wordpress export file:

    tokenizer/tokenizer.sh path/to/wordpress.xml

This will create a file data/tokens that the server uses.

## Running

To start a web server for the application, run:

    lein ring server

or

    lein ring uberjar
    java -jar target/markovtextweb-x.y.z-standalone.jar

If the tokens file is not in the default location data/tokens, specify
the path in the environment variable TOKENS_FILE.

## License

MIT License

Copyright © 2014 Antti Ajanki <antti.ajanki@iki.fi>
