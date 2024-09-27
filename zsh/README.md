# terminal setup

theme of [ubuntu](ubuntu.terminal) from https://github.com/lysyi3m/macos-terminal-themes

just do a

```bash
open ubuntu.terminal
```

and then `toolbar -> shell -> use shell settings as default`.

for (bash) syntax highlighting is just:

```bash
brew install zsh-syntax-highlighting
source $(brew --prefix)/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
```

(with the latter line put in `.zshrc`). (if you want it in vscode, then also add

```json
    "terminal.integrated.defaultProfile.osx": "zsh"
```
to your user settings).

finally, for the font, run

```bash
curl -kL https://raw.githubusercontent.com/cstrap/monaco-font/master/install-font-ubuntu.sh | bash
```

then in terminal go `settings -> profiles -> ubuntu -> font -> monaco`.

