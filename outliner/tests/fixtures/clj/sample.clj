;; Clojure sample file for outliner tests.

(ns outliner.sample
  (:require [clojure.string :as str]))

(def max-size 100)

;; A simple greeting function.
(defn greet
  "Returns a greeting string."
  [name]
  (str "Hello, " name "!"))

(defn add
  "Add two numbers."
  [x y]
  (+ x y))

;; Multi-line parameter vector.
(defn complex-fn
  "A function with many parameters."
  [arg1 arg2
   arg3]
  (+ arg1 arg2 arg3))

;; Multi-arity function.
(defn my-fn
  "A multi-arity function."
  ([x] x)
  ([x y] (+ x y))
  ([x y z] (+ x y z)))

(defn- private-fn
  "Private implementation."
  [x]
  (* x x))

(defmacro when-positive
  "Execute body when n is positive."
  [n & body]
  `(when (pos? ~n) ~@body))

(defrecord Person [name age])

(deftype Point [x y]
  Object
  (toString [_]
    (str "(" x ", " y ")")))

(defprotocol Shape
  "A geometric shape."
  (area [this])
  (perimeter [this]))

(defmulti describe :type)
