### helpful tips that I often forget otherwise (with this `.vimrc`)

#### builtins

- `gq` to reflow comments and paragraphs and stuff

- `gg` top of file, `G` bottom of file, `zf`, `vii`

- Ctrl-d, Ctrl-u: page up/down

- visually select and `:terminal <command>` will run that range as stdin to
  `<command>`, displaying it in a new buffer.

- use `Ctrl-o` to return to previous position, `Ctrl-i` to go to the next (but
these are all in the same buffer...).

#### nerdtree and custom commands

- Ctrl-e: toggle NERDTree

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

