using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Animals
{
    /// <summary>
    /// Represents an animal in the system.
    /// </summary>
    [Serializable]
    public class Animal
    {
        private string _name;
        private int _age;

        /// <summary>Creates a new Animal.</summary>
        public Animal(string name, int age)
        {
            _name = name;
            _age = age;
        }

        /// <summary>Gets or sets the animal's name.</summary>
        public string Name
        {
            get => _name;
            set => _name = value ?? throw new ArgumentNullException(nameof(value));
        }

        public int Age { get; set; }

        /// <summary>Returns a greeting string.</summary>
        public virtual string Speak()
        {
            return $"Hello, I am {_name}";
        }

        [Obsolete("Use Speak() instead")]
        public string OldSpeak() => $"Hi {_name}";

        public bool IsOlderThan(Animal other) => _age > other._age;

        /// <summary>Async fetch of animal data.</summary>
        public async Task<string> FetchDataAsync(
            string endpoint,
            bool useCache = true)
        {
            await Task.Delay(10);
            return endpoint;
        }

        public static Animal FromParts(
            string name,
            int age,
            bool validate = false)
        {
            if (validate && string.IsNullOrEmpty(name))
                throw new ArgumentException("name required");
            return new Animal(name, age);
        }

        // Override for debugging
        public override string ToString() => $"Animal({_name}, {_age})";

        /// <summary>Nested metadata record.</summary>
        public record Metadata(string Source, DateTime CreatedAt);
    }

    /// <summary>Interface for speakable entities.</summary>
    public interface ISpeakable
    {
        string Speak();

        string Shout() => Speak().ToUpper();
    }

    /// <summary>Animal status values.</summary>
    public enum Status
    {
        Active,
        Inactive,
        Archived
    }

    /// <summary>A 2D point struct.</summary>
    public struct Point
    {
        public double X { get; init; }
        public double Y { get; init; }

        public Point(double x, double y) { X = x; Y = y; }

        public double Distance() => Math.Sqrt(X * X + Y * Y);
    }

    /// <summary>Generic container.</summary>
    public class Container<T> where T : class
    {
        private readonly List<T> _items = new();

        public void Add(T item) => _items.Add(item);

        public IEnumerable<T> GetAll() => _items;
    }
}

namespace Animals.Utilities
{
    /// <summary>Static helper methods.</summary>
    public static class AnimalHelper
    {
        public static string Describe(Animal a) => $"{a.Name} age {a.Age}";

        public static IEnumerable<Animal> FilterByAge(
            IEnumerable<Animal> animals,
            int minAge,
            int maxAge)
        {
            foreach (var a in animals)
                if (a.Age >= minAge && a.Age <= maxAge)
                    yield return a;
        }
    }

    /// <summary>Custom attribute for tagging animals.</summary>
    [AttributeUsage(AttributeTargets.Class)]
    public class AnimalTagAttribute : Attribute
    {
        public string Tag { get; }

        public AnimalTagAttribute(string tag)
        {
            Tag = tag;
        }
    }
}
