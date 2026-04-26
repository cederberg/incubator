/**
 * Animal module: types, classes, and functions for managing animals.
 */

import { EventEmitter } from "events";
import type { Readable } from "stream";

// Status enum
export enum Status {
    Active = "active",
    Inactive = "inactive",
    Archived = "archived",
}

/** Type alias for a factory function. */
export type AnimalFactory = (name: string, age: number) => Animal;

/** Interface describing a speakable entity. */
export interface Speakable {
    speak(): string;
    shout?(): string;
}

/** Namespace grouping utility helpers. */
export namespace Utils {
    export function clamp(value: number, min: number, max: number): number {
        return Math.min(Math.max(value, min), max);
    }

    export type Range = { min: number; max: number };
}

/**
 * Animal class with TypeScript decorators and generics.
 */
@injectable()
@logged
export class Animal implements Speakable {
    readonly name: string;
    private age: number;

    constructor(name: string, age: number) {
        this.name = name;
        this.age = age;
    }

    speak(): string {
        return `I am ${this.name}`;
    }

    shout(): string {
        return this.speak().toUpperCase();
    }

    /** Returns whether this animal is older than another. */
    isOlderThan(other: Animal): boolean {
        return this.age > other.age;
    }

    /**
     * Creates an animal from a plain object.
     * Multi-line signature to test merging.
     */
    static fromObject(
        data: { name: string; age: number },
        validate: boolean = true,
    ): Animal | null {
        if (validate && !data.name) return null;
        return new Animal(data.name, data.age);
    }
}

/** Subclass extending Animal. */
export class Dog extends Animal {
    readonly breed: string;

    constructor(
        name: string,
        age: number,
        breed: string,
    ) {
        super(name, age);
        this.breed = breed;
    }

    fetch(
        item: string,
        distance: number = 1.0,
    ): boolean {
        return distance < 10;
    }
}

// Top-level function declaration
export function makeAnimal(name: string, age: number): Animal {
    return new Animal(name, age);
}

/**
 * Async function with generics.
 */
export async function fetchAnimal<T extends Animal>(
    id: string,
    factory: (data: unknown) => T,
): Promise<T | null> {
    return null;
}

// Arrow function assigned to const — included because it's a function value
export const createRegistry = (): Map<string, Animal> => {
    return new Map();
};

// Multi-line arrow function
export const processAnimals = (
    animals: Animal[],
    predicate: (a: Animal) => boolean,
): Animal[] => {
    return animals.filter(predicate);
};

// Plain value constant — excluded
export const MAX_ANIMALS = 100;
export const DEFAULT_NAME = "unknown";

// let function expression — included
export let helperFn = function(x: number): number {
    return x * 2;
};

// Class expression assigned to const — included
export const AnonymousCat = class extends Animal {
    meow(): string {
        return "meow";
    }
};
