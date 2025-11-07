# Project Incubator

A project for experiments, tools and research.


## git-uptodate

A tool to prints branch, stash, and working tree status for one or
more repositories. Install into `~/.local` like so:

```bash
mkdir -p ~/.local/bin ~/.local/share/man/man1
cp bin/git-uptodate ~/.local/bin/
cp man/git-uptodate.1 ~/.local/share/man/man1/
```

Update your `PATH`/`MANPATH` if needed in `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
export MANPATH="$HOME/.local/share/man:$MANPATH"
```
