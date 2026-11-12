# The bench's macOS VM

Runs and review captures happen in throwaway clones of a macOS VM made with [Tart](https://github.com/openai/tart), so a run is Claude on an ordinary Mac: macOS tools, real Chrome, Mac fonts, and WebGL on the GPU through Apple's paravirtual device (Metal). Tested on an M4: the VM's frames are pixel-identical to the host's GPU at 60 fps, where the old Linux container rendered in software at about 11 fps.

Two images, one on top of the other:

- **`tahoe-dev`**: a general-purpose developer Mac, not specific to this project. macOS 26 from `ghcr.io/cirruslabs/macos-tahoe-vanilla`, plus Homebrew (with the Command Line Tools), Node, Python, git, ripgrep and Google Chrome.
- **`ambition-bench`**: a clone of `tahoe-dev` plus the pinned Claude Code and the links that put shared folders at `/work`, `/cfg`, `/plugin`, `/bench`, `/node`, `/examples` and `/review`.

Each run clones `ambition-bench` (copy-on-write, so it costs only what the run writes), boots it headless with its own workspace shared in, and deletes it afterwards. `review` does the same with one clone for all its captures.

## Building them

Needs about 50 GB free while pulling (the image is a 24 GB download and about 28 GB on disk), and 6 GB of memory while a VM runs.

```bash
brew trust openai/tools && brew install openai/tools/tart
tart pull ghcr.io/cirruslabs/macos-tahoe-vanilla:latest
tart clone ghcr.io/cirruslabs/macos-tahoe-vanilla:latest tahoe-dev
tart set tahoe-dev --cpu 4 --memory 6144

# an SSH key for the VMs (the image's login is admin/admin; sudo needs no password)
ssh-keygen -q -t ed25519 -N "" -C tahoe-dev -f ~/.tart/tahoe-dev_ed25519
tart run tahoe-dev --no-graphics &
ssh-copy-id -i ~/.tart/tahoe-dev_ed25519 admin@$(tart ip tahoe-dev)
VM="ssh -i $HOME/.tart/tahoe-dev_ed25519 admin@$(tart ip tahoe-dev)"

$VM 'NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     echo '\''eval "$(/opt/homebrew/bin/brew shellenv)"'\'' >> ~/.zprofile'
$VM 'zsh -lc "brew install node python git ripgrep && brew install --cask google-chrome && brew cleanup -s"'
$VM 'sudo shutdown -h now'

tart clone tahoe-dev ambition-bench
tart run ambition-bench --no-graphics &
VM="ssh -i $HOME/.tart/tahoe-dev_ed25519 admin@$(tart ip ambition-bench)"
$VM 'zsh -lc "npm i -g @anthropic-ai/claude-code@2.1.322"'
$VM 'for d in work cfg plugin bench node examples review; do printf "%s\tVolumes/My Shared Files/%s\n" $d $d; done | sudo tee /etc/synthetic.conf'
$VM 'sudo shutdown -h now'   # the /etc/synthetic.conf links appear on the next boot
```

`ab.py` checks that `ambition-bench` exists and uses the key at `~/.tart/tahoe-dev_ed25519`. When you change the Claude Code version, update `VM_CLAUDE` in `ab.py` to match.

## Gotchas

- Launch Chrome through Playwright's `chrome` channel, not by file path: given a path on macOS, Playwright adds a bare `--use-angle` flag and WebGL comes up disabled. A run inside the VM meets this exactly as it would on a real Mac.
- The image's guest agent didn't answer `tart exec`, so the bench uses SSH.
- macOS allows at most two VMs at once; the bench runs one at a time.
