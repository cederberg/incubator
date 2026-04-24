// Package sample demonstrates Go outliner fixtures.
package sample

import (
	"context"
	"fmt"
	"io"
)

// MaxRetries is the max retry count.
const MaxRetries = 3

const (
	// StatusOK indicates success.
	StatusOK = 0
	// StatusError indicates failure.
	StatusError = 1
)

// Config holds server configuration.
type Config struct {
	Host string
	Port int
}

// Driver manages server connections.
type Driver struct {
	cfg    *Config
	logger io.Writer
}

// Stringer can produce a string representation.
type Stringer interface {
	String() string
}

// ErrCode is a typed error code.
type ErrCode int

// fetchOption configures a Fetch call.
type fetchOption func()

// New creates a Driver with the given config.
func New(cfg *Config) *Driver {
	return &Driver{cfg: cfg}
}

// StartLogging begins writing logs to f.
func (d *Driver) StartLogging(ctx context.Context, f io.Writer) error {
	d.logger = f
	return nil
}

// Fetch retrieves the value for key with optional opts.
func (d *Driver) Fetch(
	ctx context.Context,
	key string,
	opts ...fetchOption,
) (string, error) {
	return "", nil
}

// String returns the driver string representation.
func (d *Driver) String() string {
	return fmt.Sprintf("Driver(%s:%d)", d.cfg.Host, d.cfg.Port)
}

var globalVar = "hello"

var (
	version = "1.0"
	build   = "dev"
)

// helper multiplies x by two.
func helper(x int) int {
	return x * 2
}
