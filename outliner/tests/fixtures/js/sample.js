/**
 * Animal module: JavaScript declarations for parser fixtures.
 */

import { EventEmitter } from "events";

/** Base animal class. */
export class Animal {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }

    speak() {
        return `I am ${this.name}`;
    }
}

/** Subclass extending Animal. */
export class Dog extends Animal {
    constructor(name, breed) {
        super(name);
        this.breed = breed;
    }

    fetch(item) {
        return item.length > 0;
    }
}

// Top-level function declaration
export function makeAnimal(name, age) {
    return new Animal(name, age);
}

/** Arrow function assigned to const. */
export const createRegistry = () => {
    const registry = new Map();
    registry.set("default", new Animal("unknown", 0));
    return registry;
};

// Multi-line arrow function
export const processAnimals = (
    animals,
    predicate,
) => {
    return animals.filter(predicate);
};

// Public single-parameter arrow function.
export const normalizeName = name => name.trim();

// Plain value constant, excluded.
export const MAX_ANIMALS = 100;
export const DEFAULT_NAME = "unknown";

// Let function expression, included.
export let helperFn = function(x) {
    const doubled = x * 2;
    return doubled;
};

// Class expression assigned to const, included.
export const AnonymousCat = class extends Animal {
    meow() {
        return "meow";
    }
};
