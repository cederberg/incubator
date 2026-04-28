#!/usr/bin/env perl
use strict;
use warnings;
use feature 'signatures';
no warnings 'experimental::signatures';

package Animal;

# Constructor for Animal
sub new ($class, %args) {
    return bless {
        name => $args{name} // 'unknown',
        kind => $args{kind} // 'unknown',
    }, $class;
}

# Get the name
sub name ($self) {
    return $self->{name};
}

sub speak ($self) {
    return $self->{name} . ' says hello';
}

sub _helper ($self) {
    return 'secret';
}

package Dog;

use parent -norequire, 'Animal';

# Dog constructor
sub new ($class, $name) {
    return $class->SUPER::new(name => $name, kind => 'dog');
}

sub speak ($self) {
    return $self->{name} . ' says woof';
}

# Fetch an item
sub fetch (
    $self,
    $item,
    $distance = 1.0,
) {
    return length($item) > $distance;
}

package main;

# Create a new animal
sub make_animal ($name, $kind = 'unknown') {
    return Animal->new(name => $name, kind => $kind);
}

1;
