(ns markovtextweb.handler
  (:require [compojure.core :refer :all]
            [compojure.handler :as handler]
            [compojure.route :as route]
            [stencil.core :refer :all]
            [markovtextweb.generator :refer [build-transitions make-generator]]
            [clojure.string :as s]
            [ring.util.response :as response]
            [ring.middleware.resource :as resource]
            [ring.middleware.file-info :as file-info]))

(defn generate-random-text [transitions]
  (let [text ((make-generator transitions 100))]
    (map #(hash-map :paragraph %) (s/split text #"\n\n"))))

(defn inject-transitions-middleware [f transitions]
  (fn [request]
    (f (assoc request :transitions transitions))))

(defroutes app-routes
  (GET "/" [:as request] 
     (-> (render-file "templates/main"
         {:quotes (generate-random-text (:transitions request))})
     (response/response)
     (response/content-type "text/html; charset=utf-8")
     (response/header "Cache-Control" "no-cache, no-store, must-revalidate")
     (response/header "Pragma" "no-cache")
     (response/header "Expires" 0)))
  (route/resources "/")
  (route/not-found "Not Found"))

(def app
  (let [tokensfile (or (System/getenv "TOKENS_FILE") "data/tokens")]
    (-> app-routes
        (resource/wrap-resource "public")
        (file-info/wrap-file-info)
        (inject-transitions-middleware (build-transitions 2 tokensfile))
        handler/site)))
