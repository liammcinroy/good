### helpful tips that I often forget otherwise (with this `.vimrc`)

#### builtins

- `gq` to reflow comments and paragraphs and stuff

- `q<register>` to record, `q` to end, `@<register>` to apply (!)

- `gg` top of file, `G` bottom of file

- `g;` to go to previous edit, `g,` forward

- `Ctrl-o` to jump back, `Ctrl-i` to jump forward

- `zf` fold, `vii` select indent

- Ctrl-d, Ctrl-u: page up/down

- visually select and `:terminal <command>` will run that range as stdin to
  `<command>`, displaying it in a new buffer.

- use `Ctrl-o` to return to previous position, `Ctrl-i` to go to the next (but
these are all in the same buffer...).

#### nerdtree, ctrlp, and custom commands

- Ctrl-e: toggle NERDTree

  - when selecting one, `t` to open in new tab

- Ctrl-F

  - t: toggle file search

  - f: enter search phrase

- If using ctrlp and buftabs:

  - Ctrl-p: search files

  - Ctrl-j / Ctrl-k to navigate list (or arrows)

  - Ctrl-h or Ctrl-l: go through buffers

- If using ctrlspace

  - Ctrl-p: search files, no navigation...

    - tab: select

    - Ctrl-w: clear search

  - Ctrl-space: open menu

    - l: list tabs, navigate with j, k

    - b: list bookmarks, create workspaces, etc

    - o: open file opener (doesn't search...)

- visually select and `:Run <command>` will run that range as stdin to
  `<command>`, displaying it in a scratch (?) buffer.

#### py repr plugin

- `:Py` for running whole buffer with inline output. `:Pyc` to clear it.
  `:Pyu` for a range selection.

#### coc plugins

- Ctrl-<space> for CoC completion. navigate with <tab> and <shift>-<tab>

- Ctrl-f for autoformatting (with either CoC or

- go to `gd` definition, `gy` type definition, `gi` implementation 

- select `rn` to rename

