const std = @import("std");
const math = @import("std").math;

/// Maximum number of items.
const MAX_ITEMS: usize = 100;
const APP_NAME = "MyApp";

/// Base animal type.
const Animal = struct {
    name: []const u8,
    kind: Kind,

    /// Initialise an animal.
    pub fn init(name: []const u8, kind: Kind) Animal {
        return .{ .name = name, .kind = kind };
    }

    /// Return the display name.
    pub fn displayName(self: *const Animal) []const u8 {
        return self.name;
    }

    /// Greet with optional times.
    pub fn greet(
        self: *const Animal,
        greeting: []const u8,
        times: usize,
    ) !void {
        _ = self;
        _ = greeting;
        _ = times;
    }
};

/// Kinds of animals.
const Kind = enum {
    dog,
    cat,
    bird,
};

/// Tagged union of actions.
const Action = union(enum) {
    speak: []const u8,
    sleep: u32,
    eat,
};

// Creates a new animal
pub fn makeAnimal(name: []const u8, kind: Kind) Animal {
    return Animal.init(name, kind);
}

/// Fetch animal data.
pub fn fetchAnimal(
    allocator: std.mem.Allocator,
    url: []const u8,
) !Animal {
    _ = allocator;
    _ = url;
    return makeAnimal("Unknown", .dog);
}

fn helper(x: u32) u32 {
    return x * 2;
}
