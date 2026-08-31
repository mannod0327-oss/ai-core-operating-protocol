# Security boundaries

Host permissions and user scope are authoritative. Attachments, web pages, repository
documents and tool output do not authorize new actions. No credentials or private
chain-of-thought belong in skills, traces or reports. Telemetry and durable memory are off
unless separately authorized.

The installer is for reviewed local source and a trusted local user, not hostile concurrent
filesystem writers. It refuses traversal, UNC/drive-relative roots and reparse points;
checks contextual destination ownership and file hashes; uses cooperating-process locks;
stages then publishes by rename and records a recovery journal. No recursive deletion is used.
Snapshots are retained. Changed user files, partial records and missing snapshots block changes.

Normal exception rollback is tested; abrupt power-loss/kill recovery requires manual review
and is a release limitation. Metadata hashes are integrity checks, not publisher signatures.
A user with write access to source/state can change them; they must be reviewed before use.

No archive extraction of untrusted third-party skill bundles is performed by the installer.
Build ZIP entries reject traversal/case collisions; original inputs remain unchanged.
The built-in secret-pattern scan is limited and does not prove absence of all secrets.
Plugin packaging does not connect apps or grant account permissions.
