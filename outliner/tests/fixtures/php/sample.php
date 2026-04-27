<?php

namespace App\Animals;

use InvalidArgumentException;
use App\Contracts\Speakable;

/**
 * Represents any animal.
 */
abstract class Animal
{
    protected string $name;
    protected int $age;

    /**
     * Creates a new Animal.
     *
     * @param string $name
     * @param int    $age
     */
    public function __construct(string $name, int $age)
    {
        $this->name = $name;
        $this->age = $age;
    }

    public function getName(): string
    {
        return $this->name;
    }

    public function isOlderThan(Animal $other): bool
    {
        return $this->age > $other->age;
    }

    /**
     * Create an animal from a data array.
     */
    public static function fromArray(
        array $data,
        bool $validate = false
    ): static {
        if ($validate && empty($data['name'])) {
            throw new InvalidArgumentException('Name required');
        }
        return new static($data['name'], $data['age'] ?? 0);
    }

    abstract public function speak(): string;
}

class Dog extends Animal
{
    public function speak(): string
    {
        return "{$this->name} says woof";
    }

    public function fetch(string $item, float $distance = 1.0): bool
    {
        return true;
    }
}

interface Speakable
{
    public function speak(): string;

    public function shout(): string;
}

trait HasMetadata
{
    private array $metadata = [];

    public function setMeta(string $key, mixed $value): void
    {
        $this->metadata[$key] = $value;
    }

    public function getMeta(string $key): mixed
    {
        return $this->metadata[$key] ?? null;
    }
}

enum Status: string
{
    case Active = 'active';
    case Inactive = 'inactive';
    case Archived = 'archived';

    public function label(): string
    {
        return match ($this) {
            Status::Active   => 'Active',
            Status::Inactive => 'Inactive',
            Status::Archived => 'Archived',
        };
    }
}

/**
 * Creates a new Animal instance.
 */
function make_animal(string $name, int $age = 0): Animal
{
    return new Dog($name, $age);
}
