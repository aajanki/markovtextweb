(defproject markovtextweb "0.1.0"
  :description "Web server that generates random text using Markov chains"
  :url "https://github.com/aajanki/markovtextweb"
  :dependencies [[org.clojure/clojure "1.6.0"]
                 [compojure "1.1.8"]
                 [stencil "0.3.4"]]
  :plugins [[lein-ring "0.8.11"]]
  :ring {:handler markovtextweb.handler/app}
  :profiles
  {:dev {:dependencies [[javax.servlet/servlet-api "2.5"]
                        [ring-mock "0.1.5"]]}})
