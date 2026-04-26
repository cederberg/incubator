#include <stdio.h>
#include <math.h>
#include <string.h>

#define PI 3.14159265358979
#define SQUARE(x) ((x) * (x))
#define MAX(a, b) ((a) > (b) ? (a) : (b))

/* A simple 2D point. */
struct Point {
    double x;
    double y;
};

enum Color {
    RED,
    GREEN,
    BLUE
};

/* Compute Euclidean distance between two points. */
double distance(struct Point a, struct Point b) {
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    return sqrt(SQUARE(dx) + SQUARE(dy));
}

/* Clamp value to [min_val, max_val]. */
static int clamp(int value, int min_val, int max_val) {
    if (value < min_val) return min_val;
    if (value > max_val) return max_val;
    return value;
}

/* Format a message into the given buffer.
 * Returns the number of bytes written. */
int format_message(
    const char *fmt,
    int code,
    char *out,
    int out_size) {
    return snprintf(out, out_size, fmt, code);
}

int main(int argc, char *argv[]) {
    struct Point p1 = {0.0, 0.0};
    struct Point p2 = {3.0, 4.0};
    printf("distance: %f\n", distance(p1, p2));
    return 0;
}
