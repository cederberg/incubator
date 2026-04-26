#include <string>
#include <vector>
#include <memory>

#define UNUSED(x) ((void)(x))

namespace geometry {

struct Vec2 {
    double x;
    double y;
};

double vec2_dot(const Vec2& a, const Vec2& b);
double vec2_length(const Vec2& v);

/* Base class for all shapes. */
class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;
    virtual std::string describe() const;
    static int instance_count();

protected:
    std::string label_;
};

class Circle : public Shape {
public:
    explicit Circle(double radius);
    double area() const override;
    double radius() const;

private:
    double radius_;
};

enum class Direction {
    North,
    South,
    East,
    West
};

template<typename T>
T max_val(T a, T b) {
    return a > b ? a : b;
}

template<typename T>
class Stack {
public:
    void push(const T& item);
    T pop();
    bool empty() const;

private:
    std::vector<T> data_;
};

} // namespace geometry
