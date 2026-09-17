---
name: nixos-config
description: Manage Sujal's flake-based NixOS system (host "nixos", user "zennie"). Covers configuration.nix, home.nix, flake.nix, hardware-configuration.nix. Use whenever the user asks to add/remove packages, enable or tweak services, edit Hyprland/caelestia/home-manager/oh-my-posh settings, bump or update flake inputs, rebuild/switch/rollback the system, diagnose nixos-rebuild errors, or asks anything involving "nixos config", "flake.nix", "home.nix", "home-manager", "caelestia", or "nixos-rebuild". Trigger even if the user doesn't say "NixOS" explicitly but is clearly editing one of these files.
---

# Sujal's NixOS Config

Flake-based NixOS system. One host (`nixos`), one user (`zennie`). Home-manager is wired
in as a NixOS module (not standalone) — `home.nix` is imported directly from `flake.nix`,
it is not a separate flake.

## File map

| File | Owns |
|---|---|
| `flake.nix` | Inputs (nixpkgs unstable, home-manager, caelestia-shell, caelestia-cli, zen-browser) and the `nixosConfigurations.nixos` output. |
| `configuration.nix` | System-level: boot, networking, locale, display/desktop, audio, users, **system packages**, fonts. |
| `home.nix` | User-level (`zennie`) home-manager config: dotfiles, user programs, shell integrations (currently just `oh-my-posh`). |
| `hardware-configuration.nix` | Machine-generated. **Never hand-edit.** Regenerate with `nixos-generate-config` if hardware changes. |
| `flake.lock` | Pinned input revisions. Don't hand-edit; use `nix flake update`. |

Default location on this machine is `/etc/nixos` unless the user says otherwise — confirm
the actual path before running commands if it's not already established in the session
(they may have it as a git repo elsewhere and symlinked, or a home-manager flake checked
out under `~/nixos-config` or similar).

## Deciding where a change goes

- **System-wide package, service, boot/network/locale setting** → `configuration.nix`.
- **Something scoped to the `zennie` user only** (CLI tool config, shell integration,
  dotfile-managed app) → `home.nix`, via the matching `programs.<x>` or `home.packages`
  module. Prefer `programs.<x>.enable` over raw `home.packages` when home-manager has a
  module for it — it gets you config-file generation for free.
- **New flake input** (another dotfiles repo, another overlay) → `flake.nix`, following
  the existing pattern: add to `inputs`, add `inputs.nixpkgs.follows = "nixpkgs"` unless
  there's a reason not to, thread it through `specialArgs` if `configuration.nix` needs to
  reference the package output directly (see how `caelestia-shell`/`caelestia-cli` are
  done).

## Adding a package

Ask first: system-wide or `zennie`-only?

- System-wide: add to the `with pkgs; [ ... ]` list inside `environment.systemPackages` in
  `configuration.nix`. Note the list currently mixes plain nixpkgs attrs with two flake
  outputs pulled in via a `let zen = inputs.zen-browser.packages.${system}.default; in` —
  follow that pattern for anything else that needs to come from a flake input rather than
  nixpkgs.
- User-only: add to `home.packages` in `home.nix`, or use a `programs.<name>` module if one
  exists in home-manager for it.

Don't touch `hardware-configuration.nix` or `system.stateVersion` for this.

## Rebuilding

```bash
# Standard rebuild + activate, from the flake directory (or pass -I/--flake path explicitly)
sudo nixos-rebuild switch --flake .#nixos

# Build without activating, to check it compiles
sudo nixos-rebuild build --flake .#nixos

# Roll back to the previous generation if switch broke something
sudo nixos-rebuild switch --rollback

# List generations
sudo nix-env --list-generations --profile /nix/var/nix/profiles/system
```

home-manager activates automatically as part of `nixos-rebuild switch` here, since it's
wired in as a NixOS module (`home-manager.users.zennie = import ./home.nix`) — there is no
separate `home-manager switch` step to run.

## Flake input maintenance

```bash
nix flake update                  # update all inputs, rewrite flake.lock
nix flake lock --update-input nixpkgs   # update just one input
nix flake metadata                # inspect current pins
```

After updating, run `nixos-rebuild build` first, not `switch`, in case an update breaks
something — this repo pulls in two inputs from the `caelestia-dots` org that track each
other and nixpkgs, so a nixpkgs bump can require both to move together.

## Formatting

The current files mix tabs and spaces (notably the `environment.systemPackages` list uses
tabs while the rest of the file uses spaces). If asked to clean up formatting, run:

```bash
nix run nixpkgs#nixfmt-rfc-style -- configuration.nix home.nix flake.nix
```

(or `alejandra`/`nixpkgs-fmt` if the user prefers one of those instead — ask if unsure,
don't silently pick a formatter that reformats their whole style).

## Known rough edges in this config — flag, don't silently "fix"

Point these out to the user rather than patching them unasked; they may be intentional or
already handled outside these files:

- `services.displayManager.sddm.enable = false` while `services.desktopManager.plasma6.enable
  = true` and `programs.hyprland.enable = true`, with no other display manager
  (`gdm`, `greetd`, etc.) turned on anywhere in the file. Unless there's a display manager
  or autologin configured outside what's here, this config has no defined way to reach a
  graphical session — worth confirming with the user how they're actually getting to
  Hyprland/Plasma before assuming this is fine.
- `services.pulseaudio.enable = false` with `services.pipewire.pulse.enable = true` is
  correct (pipewire's pulse shim replaces pulseaudio), just flagging it's not a
  contradiction.
- `system.stateVersion = "24.11"` — never change this on an existing install regardless of
  what channel/nixpkgs version is actually running. Changing it does not upgrade anything
  and can affect stateful data schemas.

## Home-manager username mismatch check

`flake.nix` sets `home-manager.users.zennie = import ./home.nix`, and `home.nix` sets
`home.username = "zennie"` / `home.homeDirectory = "/home/zennie"`, and
`configuration.nix` defines `users.users."zennie"`. If the user ever asks to rename the
account or add a second user, all three of these need to move together — a mismatch here
is a common cause of confusing `nixos-rebuild` failures.

## Troubleshooting rebuild failures

1. Read the actual error, not just the last line — Nix errors are often several frames
   deep; the useful info is usually in the first "error:" block, not the trace at the end.
2. If it's an attribute/module error (`attribute 'X' missing`, `The option ... does not
   exist`), check the option actually exists for the pinned nixpkgs/home-manager revision —
   options get renamed between releases. Search https://search.nixos.org/options and
   https://home-manager-options.extranix.com against the input revision in `flake.lock`,
   not the latest docs.
3. If it's a flake input resolution error, check `flake.lock` for the offending input and
   try `nix flake lock --update-input <name>` in isolation before updating everything.
4. If a build fails only after a `flake update`, `git diff flake.lock` to see exactly what
   moved, and bisect by pinning the suspect input back with `nix flake lock --override-input
   <name> github:<owner>/<repo>/<old-rev>`.
