package animals

import scala.collection.mutable
import scala.util.Try

/** Base trait for all animals. */
trait Animal {
  /** Name */
  def name: String

  /** Speak */
  def speak(): String

  /** Greet with count */
  def greet(
      message: String,
      times: Int = 1,
  ): String = {
    (1 to times).map(_ => s"$message ${speak()}").mkString(", ")
  }
}

/** A playful dog. */
class Dog(
    val name: String,
    val breed: String,
) extends Animal {
  /** Bark */
  def speak(): String = "Woof"

  /** Fetch an item from a distance */
  def fetch(
      item: String,
      distance: Double = 1.0,
  ): Boolean = {
    println(s"$name fetches $item from ${distance}m")
    distance <= 10.0
  }
}

/** Cat as a case class */
case class Cat(name: String, indoor: Boolean = true) extends Animal {
  def speak(): String = "Meow"
}

/** Cat companion object */
object Cat {
  // Convenience factory
  def fromName(name: String): Cat = Cat(name)
}

/** Sealed shape hierarchy */
sealed abstract class Shape

case class Circle(radius: Double) extends Shape

case class Rectangle(width: Double, height: Double) extends Shape

/** Shape utilities */
object ShapeUtils {
  def area(shape: Shape): Double = shape match {
    case Circle(r)       => Math.PI * r * r
    case Rectangle(w, h) => w * h
  }
}

// Type alias
type AnimalMap = Map[String, Animal]

// Scala 3 extension
extension (s: String) {
  def shout: String = s.toUpperCase + "!"
  def whisper: String = s.toLowerCase + "..."
}

// Scala 3 given
given animalOrdering: Ordering[Cat] = Ordering.by(_.name)
