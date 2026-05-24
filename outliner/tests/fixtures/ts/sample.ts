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

/** Object-shaped type alias remains a navigational container. */
export type ColorSummary = {
    red: number;
    green: number;
};

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

/** Ambient package-style API declarations. */
declare namespace palette {
    type Level = 0 | 1;

    interface Painter {
        readonly level: Level;
        readonly primary: string
        readonly secondary: string
        readonly formatter:
            | string
            | ((value: string) => string)
        /**
         * fake(value: string): void;
         */
        paint(text: string): string;
        (text: string): string;
        blend(
            foreground: string,
            background: string,
        ): string;
    }

    namespace nested {
        interface Formatter {
            format(value: string): string;
        }
    }
}

declare const palette: palette.Painter & {
    supportsColor: boolean;
};

export declare abstract class AbstractPainter {
    abstract clear(): void
    abstract reset(): void
    abstract draw(): void;
}

declare module "palette-plugin" {
    export function activate(): void;
}

declare global {
    interface Window {
        readonly palette: palette.Painter;
    }
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
        /** Name passed to Animal. */
        name: string,
        /** Age passed to Animal. */
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

// Arrow function assigned to const, included because it is a function value.
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

// Plain value constant, excluded.
export const MAX_ANIMALS = 100;
export const DEFAULT_NAME = "unknown";

// Let function expression, included.
export let helperFn = function(x: number): number {
    return x * 2;
};

// Class expression assigned to const, included.
export const AnonymousCat = class extends Animal {
    meow(): string {
        return "meow";
    }
};
