(ns markovtextweb.generator
  (:require [clojure.java.io :as io])
  (:require [clojure.string :as s]))

(defn in?
  "true if seq contains elm"
  [seq elm]
  (some #(= elm %) seq))

(defn build-transitions [k filename]

  (defn deserialize-token [tokenstring]
    (let [[text & attributes] (s/split tokenstring #" ")]
      {:text text
       :value text
       :is-sentence-end (in? attributes "end_sentence")
       :is-paragraph-start (in? attributes "start_paragraph")}))

  (defn context-key [context]
    (s/join " " (map :value context)))

  (defn to-transition-item [window]
    (let [context (butlast window)
          continuation (last window)
          key (context-key context)]
      {key (list continuation)}))

  (defn create-starts [tokens]
    (let [pairs (partition 2 1 tokens)]
      (map second (filter #(:is-paragraph-start (first %)) pairs))))

  (defn create-transitions [tokens k]
    (let [windows (partition (+ k 1) 1 tokens)]
      (apply merge-with into (map to-transition-item windows))))

  (defn create-transition-tables [maxk tokens]
    (map (partial create-transitions tokens) (range 1 (+ maxk 1))))

  (defn load-tokens [filename]
    (with-open [rdr (io/reader filename)]
      (doall (map deserialize-token (line-seq rdr)))))

  (let [tokens (load-tokens filename)]
    {:starts (create-starts tokens)
     :transitions (create-transition-tables k tokens)}))

(defn make-generator [transitions min-words]

  (defn markov-sample [previous-words]
    (if (> (count previous-words) 0)
      (let [transtable (nth (:transitions transitions) (- (count previous-words) 1))
            key (s/join " " previous-words)
            continuations (transtable key)]
        (if (nil? continuations)
          (recur (drop 1 previous-words))
          (rand-nth continuations)))
      (rand-nth (:starts transitions))))

  (defn append-word [text token]
    (if (s/blank? text)
      (:text token)
      (let [separator (if (= (last text) \newline) ""
                          (if (:is-paragraph-start token) "\n\n" " "))]
        (str text separator (:text token)))))

  (defn update-context [max-length old-context token]
    (if (:is-paragraph-start token)
      []
      (vec (take-last max-length (conj old-context (:value token))))))

  (fn []
    (loop [text nil context [] cnt min-words]
      (let [token (markov-sample context)]
        (if (and (<= cnt 0) (:is-paragraph-start token))
          text
          (let [updated-text (append-word text token)
                updated-context (update-context (count (:transitions transitions)) context token)]
            (recur updated-text updated-context (dec cnt))))))))
