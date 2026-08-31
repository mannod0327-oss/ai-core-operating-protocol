# Install, migrate and recover

Python 3.12/3.13 target; standard library only for the installer. No shell installation
scripts downloaded or executed. Read the canonical skill before authorizing installation.

## Explicit target context

The default action is plan (read-only). Workspace scope is the default. The state directory
defaults to a dedicated .ai-core-operating-protocol-v2 directory under the chosen home.
Use --state-dir to choose a separate state directory, never the workspace/home itself.
Destination and state must share a filesystem because atomic snapshot moves use rename.
If your workspace is on another drive from your home, choose --state-dir on that workspace
drive. Plan/install refuse a cross-filesystem configuration before creating installation state.
The volume check uses the nearest existing ancestor; it does not silently migrate old state.

```sh
python installers/install.py codex --scope workspace --workspace ./project --state-dir ./ai-core-state --action plan
python installers/install.py codex --scope workspace --workspace ./project --state-dir ./ai-core-state --action install
python installers/install.py codex --scope workspace --workspace ./project --state-dir ./ai-core-state --action verify
python installers/install.py codex --scope workspace --workspace ./project --state-dir ./ai-core-state --action upgrade
python installers/install.py codex --scope workspace --workspace ./project --state-dir ./ai-core-state --action rollback
python installers/install.py codex --scope workspace --workspace ./project --state-dir ./ai-core-state --action uninstall
python installers/install.py codex --state-dir ./ai-core-state --action list-installs
```

doctor is a read-only plan alias, not a probe of login, tool availability or host discovery.
upgrade uses the install transaction and is a no-op for identical source/version.
rollback requires a previous managed installation; uninstall restores the original collision
snapshot if one exists. list-installs returns only identity/runtime/scope/version from this state.
Missing or inconsistent previous snapshot/record metadata blocks rollback before mutation.

Runtime and scope plus explicit caller paths resolve the destination. Stored destination paths
are checked against that context, never accepted as deletion targets. Shared workspace paths
(Codex/Gemini/Antigravity/generic) intentionally conflict; there is no hidden refcount.
Do not install the same skill using both native and plugin paths without checking host precedence.

## Preservation

Unmanaged collisions are refused unless --replace is explicitly supplied; then the exact
original tree is snapshotted. Changed installed files or user additions block upgrades and
uninstalls. Keep/merge those edits manually after review. No AGENTS.md, CLAUDE.md, GEMINI.md,
authentication file, MCP config or unrelated skill is modified. No bootstrap merge is shipped.

Normal caught transaction errors restore the previous tree and record. Source and staged hashes
are compared before publication. Snapshots are retained even after uninstall; there is no
automatic garbage collection. Separate state and destination locks prevent cooperating
installers from concurrent mutation. Filesystem adversaries able to race/modify the same
directories are outside this local installer trust boundary.

## Migration from RC1

Do not run the old manifest-driven uninstaller. Keep its source, manifest and backups.
Preview RC2 against the exact existing target. An RC1 tree is an unmanaged collision for RC2;
use explicit --replace only after reviewing it. RC2 will retain its original bytes for restoration.
Old RC1 state is not automatically imported or erased.

## Interrupted process / pending journal

A process killed outside normal exception handling can leave a lock, stage or journal.
verify reports pending-recovery; subsequent writes fail closed. This candidate deliberately
does not force-remove locks or replay untrusted journals automatically.

Stop all installer instances. Preserve state, staging trees and destination first. Review the
journal's before/after hashes and snapshot identity against the explicit runtime destination.
Have a maintainer determine which tree is committed before performing any manual restoration.
Do not blindly delete locks, snapshots or records. Automatic crash recovery is NOT implemented.
Report this as a blocker, not a successful install.

## Cloud and mobile

The filesystem installer rejects unknown web/mobile runtime names. Use the host's actual skill
or plugin importer; discovery, enablement and permissions must be checked in that account.
Restart/reload a local host only according to its documentation. Host activation is not verified
by the installer returning “installed”.
