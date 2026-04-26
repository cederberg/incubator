//! Animal module: types and traits for managing animals.

use std::fmt;
use std::collections::HashMap;

/// An animal with a name and age.
///
/// Created via `Animal::new`.
#[derive(Debug, Clone, PartialEq)]
pub struct Animal {
    /// The animal's name.
    pub name: String,
    age: u32,
}

/// Possible statuses of an animal record.
#[derive(Debug, Clone, PartialEq)]
pub enum Status {
    Active,
    Inactive,
    Archived,
}

/// Trait for entities that can speak.
pub trait Speakable {
    /// Returns the entity's speech.
    fn speak(&self) -> String;

    /// Returns uppercased speech.
    fn shout(&self) -> String {
        self.speak().to_uppercase()
    }
}

impl Animal {
    /// Creates a new Animal.
    pub fn new(name: &str, age: u32) -> Self {
        Animal { name: name.to_string(), age }
    }

    /// Returns the animal's name.
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Constructs an animal from separate parts.
    /// Multi-line signature to test merging.
    pub fn from_parts(
        name: String,
        age: u32,
        validate: bool,
    ) -> Option<Animal> {
        if validate && name.is_empty() {
            return None;
        }
        Some(Animal { name, age })
    }

    /// Returns whether this animal is older.
    pub fn is_older_than(&self, other: &Animal) -> bool {
        self.age > other.age
    }
}

impl Speakable for Animal {
    fn speak(&self) -> String {
        format!("I am {}", self.name)
    }
}

impl fmt::Display for Animal {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Animal({}, {})", self.name, self.age)
    }
}

/// Type alias for an animal registry.
pub type Registry = HashMap<String, Animal>;

/// Computes factorial of n.
pub fn factorial(n: u64) -> u64 {
    if n == 0 { 1 } else { n * factorial(n - 1) }
}

/// Parses an animal from input using a factory closure.
/// Demonstrates lifetime and generic parameters.
pub fn parse_animal<'a, F>(
    input: &'a str,
    factory: F,
) -> Option<Animal>
where
    F: Fn(&'a str) -> Option<Animal>,
{
    factory(input)
}

/// A generic pair of values.
pub struct Pair<T, U> {
    pub first: T,
    pub second: U,
}

impl<T: Clone, U: Clone> Pair<T, U> {
    /// Creates a new Pair.
    pub fn new(first: T, second: U) -> Self {
        Pair { first, second }
    }

    /// Swaps the pair elements.
    pub fn swap(&self) -> Pair<U, T> {
        Pair { first: self.second.clone(), second: self.first.clone() }
    }
}

/// Internal utilities module.
mod utils {
    /// Doubles the input value.
    pub fn double(x: u32) -> u32 {
        x * 2
    }
}
