// sample.swift — comprehensive fixture for outliner tests
import Foundation

// MARK: - Protocols

/// A speakable entity.
protocol Speakable {
    func speak() -> String
    func shout() -> String
}

/// A feedable entity.
protocol Feedable: AnyObject {
    func feed(amount: Double) -> Bool
}

// MARK: - Enums

/// Animal status.
enum Status: String {
    case active = "active"
    case inactive = "inactive"
    case archived
}

// MARK: - Structs

/// A 2D coordinate point.
struct Point {
    var x: Double
    var y: Double

    /// Creates a point with x and y.
    init(x: Double, y: Double) {
        self.x = x
        self.y = y
    }

    /// Computes distance to another point.
    func distance(to other: Point) -> Double {
        let dx = x - other.x
        let dy = y - other.y
        return (dx * dx + dy * dy).squareRoot()
    }

    static func origin() -> Point {
        return Point(x: 0, y: 0)
    }
}

// MARK: - Classes

/// Base animal class.
open class Animal: Speakable, Feedable {
    public let name: String
    private var _age: Int

    /// Designated initialiser.
    public required init(name: String, age: Int) {
        self.name = name
        self._age = age
    }

    deinit {
        print("Animal deallocated")
    }

    open func speak() -> String {
        return "..."
    }

    public func shout() -> String {
        return speak().uppercased()
    }

    @discardableResult
    public func feed(amount: Double) -> Bool {
        return amount > 0
    }

    /// Fetch remote data with a multi-line signature.
    @discardableResult
    public func fetchData(
        from url: URL,
        timeout: TimeInterval = 30.0
    ) async throws -> Data {
        return Data()
    }

    public static func species() -> String {
        return "Unknown"
    }
}

/// A dog subclass.
final class Dog: Animal {
    private let breed: String

    /// Creates a dog with breed.
    init(name: String, age: Int, breed: String) {
        self.breed = breed
        super.init(name: name, age: age)
    }

    override func speak() -> String {
        return "Woof!"
    }
}

// MARK: - Actors

/// Concurrent data store.
@available(macOS 10.15, *)
actor DataStore {
    private var cache: [String: Data] = [:]

    /// Stores a key-value pair.
    func store(key: String, value: Data) {
        cache[key] = value
    }

    func retrieve(key: String) -> Data? {
        return cache[key]
    }
}

// MARK: - Extensions

extension Animal {
    func describe() -> String {
        return "\(name)"
    }
}

extension Dog: CustomStringConvertible {
    var description: String {
        return "Dog(\(name), \(breed))"
    }
}

// MARK: - Free functions

/// Creates a new animal from a dictionary.
func makeAnimal(name: String, kind: String = "unknown") -> Animal {
    return Animal(name: name, age: 0)
}

/// Processes a list of animals with filter and transform.
fileprivate func processAnimals(
    animals: [Animal],
    filter predicate: (Animal) -> Bool,
    transform: @escaping (Animal) -> String
) -> [String] {
    return animals.filter(predicate).map(transform)
}
