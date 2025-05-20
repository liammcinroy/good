Vaguely following
[this guide](https://olafurpg.github.io/metals/docs/editors/vim.html).

- yarn: `curl --compressed -o- -L https://yarnpkg.com/install.sh | bash`

- coursier: `brew install coursier/formulas/coursier`

- install:

```bash
coursier bootstrap \
  --java-opt -Xss4m \
  --java-opt -Xms100m \
  --java-opt -Dmetals.client=coc.nvim \
  org.scalameta:metals_2.13:0.11.12 \
  -r bintray:scalacenter/releases \
  -r sonatype:snapshots \
  -o /usr/local/bin/metals-vim -f
```

- Also in `~/.vim/plugged/coc.nvim` run `yarn install && yarn build`

- Then in vim, just run `:CocInstall`, `:CocEnable`, and `:CocStart`!

- For scala, `:CocInstall coc-metals`

  - if this doesn't work, then it can be useful to add as a plug instead.

- For rust analyzer, then also run `:CocInstall coc-rust-analyzer`.

- For C++, then also run `:CocInstall coc-clangd`.

- For ruff, then `:CocInstall @yaegassy/coc-ruff`

  - if this doesn't work, then it can be useful to add as a plug instead.

- For jedi lsp, then `:CocInstall coc-jedi`

- If you get weird error messages, it's probably some combination of an old
session with a bad recent plug update, or a bad combinations of plugs.

  - or you `brew install node`, and you shouldn't, and should install from
  http://nodejs.org instead.

  - you may need to remove `node_modules` in wherever it's trying to install to
  as well.

- Also vim 9+ is often required for these to work!

