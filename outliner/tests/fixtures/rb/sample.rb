#!/usr/bin/env ruby
# frozen_string_literal: true

require 'json'
require_relative './utils'

# A module for animals
module Animals
  VERSION = '1.0'

  # Represents any animal
  class Animal
    attr_accessor :name, :kind
    attr_reader :id

    # @param name [String]
    def initialize(name, kind: 'unknown')
      @name = name
      @kind = kind
      @id = rand(1000)
    end

    # Speak in animal's voice
    def speak
      "#{@name} says hello"
    end

    def display_name
      @name.upcase
    end

    def self.create(name)
      new(name)
    end

    private

    def secret_method
      'secret'
    end
  end

  # A dog
  class Dog < Animal
    def initialize(name)
      super(name, kind: 'dog')
    end

    def speak
      "#{@name} says woof"
    end

    def fetch(
      item,
      distance: 1.0
    )
      item.to_s.length > distance
    end
  end

  def self.make_animal(name, kind = 'unknown')
    Animal.new(name, kind)
  end
end

# Standalone helper
def standalone_helper(x)
  x * 2
end
