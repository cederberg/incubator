package com.example;

import java.io.IOException;
import java.util.Optional;

/**
 * Represents an animal in the system.
 */
@SuppressWarnings("unused")
public class Animal {

    private final String name;
    private int age;

    /**
     * Creates a new Animal with the given name and age.
     *
     * @param name the animal's name
     * @param age  the animal's age
     */
    public Animal(String name, int age) {
        this.name = name;
        this.age = age;
    }

    /** Returns the animal's name. */
    public String getName() throws IOException {
        return name;
    }

    public int getAge() {
        return age;
    }

    /**
     * Checks whether this animal is older than another.
     */
    public boolean isOlderThan(Animal other) {
        return this.age > other.age;
    }

    @Override
    public String toString() {
        return "Animal(" + name + ", " + age + ")";
    }

    @Deprecated
    public static Animal fromLegacy(String spec) {
        String[] parts = spec.split(":");
        return new Animal(parts[0], Integer.parseInt(parts[1]));
    }

    /**
     * Produces an animal from a list of strings.
     * Multi-line method to test signature merging.
     */
    public static Optional<Animal> fromParts(
            String name,
            int age,
            boolean validate) {
        if (validate && name.isEmpty()) return Optional.empty();
        return Optional.of(new Animal(name, age));
    }

    /** Returns animals grouped by tag; exercises nested-generic signatures. */
    public static Map<String, List<Animal>> groupByTag(
            Map<String, List<Animal>> source,
            boolean deepCopy) {
        return deepCopy ? new java.util.HashMap<>(source) : source;
    }

    // -----------------------------------------------------------------------
    // Nested class
    // -----------------------------------------------------------------------

    /** Metadata associated with an animal record. */
    public static class Metadata {

        private final String source;

        public Metadata(String source) {
            this.source = source;
        }

        public String getSource() {
            synchronized (this) {
                return source;
            }
        }
    }
}

// ---------------------------------------------------------------------------

/** Defines behaviour for a speakable entity. */
public interface Speakable {

    String speak();

    default String shout() {
        return speak().toUpperCase();
    }
}

// ---------------------------------------------------------------------------

/** Possible states of an animal record. */
public enum Status {
    ACTIVE,
    INACTIVE,
    ARCHIVED;

    public boolean isVisible() {
        return this == ACTIVE;
    }
}

// ---------------------------------------------------------------------------

/** Annotation type for tagging animal records. */
public @interface AnimalTag {

    String value() default "";

    int priority() default 0;
}

// ---------------------------------------------------------------------------

/** A 2D point with Euclidean distance. */
public record Point(double x, double y) {

    public double distance() {
        return Math.sqrt(x * x + y * y);
    }
}
