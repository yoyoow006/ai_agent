#!/usr/bin/env python3
"""Offline, read-only preflight for the portable AI workflow installer."""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from typing import Union
import unicodedata


USAGE = """Usage: install-ai-workflow.sh --target <existing-dir> --assistant codex|claude [--dry-run] [--upgrade]

Options:
  --target <existing-dir>       Existing project directory to inspect
  --assistant codex|claude     Install exactly one assistant adapter
  --dry-run                    Print the plan without writing files
  --upgrade                    Upgrade a previous installation via the ledger
  -h, --help                   Show this help
"""


class UsageError(ValueError):
    """The command line does not match the public interface."""


class InputError(ValueError):
    """An input, manifest, or path failed closed."""


class ConflictError(InputError):
    """Existing target content conflicts with the plan."""


class TransactionError(RuntimeError):
    """A write or rollback operation failed without exposing target content."""


@dataclass(frozen=True)
class ManifestEntry:
    path: str
    source_bytes: bytes
    mode: int


@dataclass(frozen=True)
class Manifest:
    schema_version: int
    shared: tuple[ManifestEntry, ...]
    codex: tuple[ManifestEntry, ...]
    claude: tuple[ManifestEntry, ...]


@dataclass(frozen=True)
class PlanItem:
    path: str
    source_bytes: bytes
    mode: int
    action: str
    target_version: tuple[int, int, int, int, int, int] | None = None
    target_mode: int | None = None
    original_bytes: bytes | None = None


@dataclass(frozen=True)
class InstallPlan:
    source_root: Path
    target: Path
    assistant: str
    items: tuple[PlanItem, ...]
    target_binding: tuple[int, int, int]
    directory_bindings: tuple[tuple[str, tuple[int, int, int]], ...]
    upgrade: bool = False


@dataclass(frozen=True)
class InstallResult:
    plan: InstallPlan
    dry_run: bool


@dataclass(frozen=True)
class ParsedArguments:
    target: Path | None
    assistant: str | None
    dry_run: bool
    help_requested: bool
    upgrade: bool = False


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise InputError("manifest contains a duplicate JSON key")
        result[key] = value
    return result


def _directory_flags() -> int:
    return (
        os.O_RDONLY
        | os.O_DIRECTORY
        | os.O_NOFOLLOW
        | getattr(os, "O_CLOEXEC", 0)
    )


def _file_flags() -> int:
    return os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)


def _binding(metadata: os.stat_result) -> tuple[int, int, int]:
    return metadata.st_dev, metadata.st_ino, stat.S_IFMT(metadata.st_mode)


def _file_version(metadata: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        *_binding(metadata),
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _open_relative_directory(
    root_fd: int, components: tuple[str, ...], description: str,
) -> int:
    current_fd = os.dup(root_fd)
    try:
        for component in components:
            next_fd = os.open(component, _directory_flags(), dir_fd=current_fd)
            os.close(current_fd)
            current_fd = next_fd
        result_fd = current_fd
        current_fd = -1
        return result_fd
    except OSError as error:
        raise InputError(f"{description} must be a stable real directory") from error
    finally:
        if current_fd >= 0:
            os.close(current_fd)


def _open_directory_path(path: Path, description: str) -> int:
    absolute = Path(os.path.abspath(os.fspath(path)))
    try:
        root_fd = os.open(absolute.anchor, _directory_flags())
    except OSError as error:
        raise InputError(f"{description} cannot be anchored") from error
    try:
        return _open_relative_directory(root_fd, absolute.parts[1:], description)
    finally:
        os.close(root_fd)


def _same_directory(left_fd: int, right_fd: int) -> bool:
    return _binding(os.fstat(left_fd)) == _binding(os.fstat(right_fd))


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _verify_relative_directory(
    root_fd: int, components: tuple[str, ...], bound_fd: int, description: str,
) -> None:
    reopened_fd = _open_relative_directory(root_fd, components, description)
    try:
        if not _same_directory(bound_fd, reopened_fd):
            raise InputError(f"{description} changed during inspection")
    finally:
        os.close(reopened_fd)


def _verify_directory_path(path: Path, bound_fd: int, description: str) -> None:
    reopened_fd = _open_directory_path(path, description)
    try:
        if not _same_directory(bound_fd, reopened_fd):
            raise InputError(f"{description} changed during inspection")
    finally:
        os.close(reopened_fd)


def _read_regular_at(directory_fd: int, name: str, description: str) -> bytes:
    try:
        descriptor = os.open(name, _file_flags(), dir_fd=directory_fd)
        try:
            before = os.fstat(descriptor)
            if not stat.S_ISREG(before.st_mode):
                raise InputError(f"{description} must be a regular file")
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            after = os.fstat(descriptor)
        finally:
            os.close(descriptor)
    except InputError:
        raise
    except OSError as error:
        raise InputError(f"{description} cannot be read safely") from error
    if _file_version(before) != _file_version(after):
        raise InputError(f"{description} changed during inspection")
    try:
        reopened_fd = os.open(name, _file_flags(), dir_fd=directory_fd)
        try:
            reopened = os.fstat(reopened_fd)
        finally:
            os.close(reopened_fd)
    except OSError as error:
        raise InputError(f"{description} changed during inspection") from error
    if _binding(after) != _binding(reopened):
        raise InputError(f"{description} changed during inspection")
    return b"".join(chunks)


def _read_regular_file(path: Path, description: str) -> bytes:
    parent_fd = _open_directory_path(path.parent, f"{description} parent")
    try:
        content = _read_regular_at(parent_fd, path.name, description)
        _verify_directory_path(path.parent, parent_fd, f"{description} parent")
        return content
    finally:
        os.close(parent_fd)


def _validate_manifest_path(value: object) -> str:
    if type(value) is not str:
        raise InputError("manifest path must be a string")
    if not value or "\0" in value or "\\" in value:
        raise InputError("manifest path is unsafe")
    if any(unicodedata.category(character) == "Cc" for character in value):
        raise InputError("manifest path contains control characters")
    if unicodedata.normalize("NFC", value) != value:
        raise InputError("manifest path must use NFC")
    components = value.split("/")
    if value.startswith("/") or any(component in ("", ".", "..") for component in components):
        raise InputError("manifest path is not a canonical relative path")
    return value


def _load_group(
    asset_root_fd: int, group: str, value: object,
) -> tuple[ManifestEntry, ...]:
    if type(value) is not list:
        raise InputError("manifest group must be a list")
    group_fd = _open_relative_directory(
        asset_root_fd, (group,), "manifest asset group"
    )
    try:
        entries: list[ManifestEntry] = []
        paths: list[str] = []
        for raw_entry in value:
            if type(raw_entry) is not dict or set(raw_entry) != {"path", "mode"}:
                raise InputError("manifest entry has an invalid schema")
            relative_path = _validate_manifest_path(raw_entry["path"])
            raw_mode = raw_entry["mode"]
            if type(raw_mode) is not str or raw_mode not in {"0644", "0755"}:
                raise InputError("manifest entry has an invalid mode")
            path_parts = tuple(relative_path.split("/"))
            parent_parts = path_parts[:-1]
            parent_fd = _open_relative_directory(
                group_fd, parent_parts, "manifest source parent"
            )
            try:
                content = _read_regular_at(
                    parent_fd, path_parts[-1], "manifest source"
                )
                _verify_relative_directory(
                    group_fd, parent_parts, parent_fd, "manifest source parent"
                )
            finally:
                os.close(parent_fd)
            paths.append(relative_path)
            entries.append(ManifestEntry(relative_path, content, int(raw_mode, 8)))
        if paths != sorted(paths, key=os.fsencode) or len(paths) != len(set(paths)):
            raise InputError("manifest paths must be sorted and unique")
        _verify_relative_directory(
            asset_root_fd, (group,), group_fd, "manifest asset group"
        )
        return tuple(entries)
    finally:
        os.close(group_fd)


def load_manifest(asset_root: Path) -> Manifest:
    """Load and deeply validate the explicit asset manifest."""
    asset_root_fd = _open_directory_path(asset_root, "manifest asset root")
    try:
        manifest_bytes = _read_regular_at(asset_root_fd, "manifest.json", "manifest")
        try:
            data = json.loads(
                manifest_bytes.decode("utf-8"), object_pairs_hook=_unique_json_object
            )
        except InputError:
            raise
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise InputError("manifest is not valid UTF-8 JSON") from error
        if type(data) is not dict or set(data) != {
            "schema_version", "shared", "codex", "claude"
        }:
            raise InputError("manifest has an invalid top-level schema")
        if type(data["schema_version"]) is not int or data["schema_version"] != 1:
            raise InputError("manifest schema version is unsupported")
        manifest = Manifest(
            schema_version=1,
            shared=_load_group(asset_root_fd, "shared", data["shared"]),
            codex=_load_group(asset_root_fd, "codex", data["codex"]),
            claude=_load_group(asset_root_fd, "claude", data["claude"]),
        )
        _verify_directory_path(asset_root, asset_root_fd, "manifest asset root")
        return manifest
    finally:
        os.close(asset_root_fd)


def _validated_target(target_input: Path) -> Path:
    raw_target = os.fspath(target_input)
    if not raw_target:
        raise InputError("target is empty")
    if any(unicodedata.category(character) == "Cc" for character in raw_target):
        raise InputError("target path contains control characters")
    raw_path = Path(raw_target)
    if raw_path.is_absolute():
        current = Path(raw_path.anchor)
        components = raw_path.parts[1:]
    else:
        current = Path.cwd()
        components = raw_path.parts
    for component in components:
        if component == ".":
            continue
        if component == "..":
            current = current.parent
            continue
        current = current / component
        try:
            metadata = current.lstat()
        except OSError as error:
            raise InputError("target does not exist") from error
        if stat.S_ISLNK(metadata.st_mode):
            raise InputError("target path contains a symbolic link")
    try:
        resolved = current.resolve(strict=True)
        metadata = resolved.lstat()
    except OSError as error:
        raise InputError("target does not exist") from error
    if not stat.S_ISDIR(metadata.st_mode):
        raise InputError("target must be a directory")
    if any(
        unicodedata.category(character) == "Cc"
        for character in os.fspath(resolved)
    ):
        raise InputError("target path contains control characters")
    return resolved


def _inspect_target_file(target: Path, relative_path: str) -> "bytes | None":
    """Return current target bytes (None when missing) after structural checks."""
    current = target
    components = relative_path.split("/")
    for index, component in enumerate(components):
        current = current / component
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            return None
        except OSError as error:
            raise ConflictError("target path cannot be inspected") from error
        if stat.S_ISLNK(metadata.st_mode):
            raise ConflictError("target path contains a symbolic link")
        if index < len(components) - 1:
            if not stat.S_ISDIR(metadata.st_mode):
                raise ConflictError("target parent is not a directory")
            continue
        if not stat.S_ISREG(metadata.st_mode):
            raise ConflictError("target path is not a regular file")
        return _read_regular_file(current, "target file")
    raise AssertionError("unreachable empty target path")


def _target_action(target: Path, relative_path: str, content: bytes) -> str:
    existing = _inspect_target_file(target, relative_path)
    if existing is None:
        return "create"
    if existing == content:
        return "unchanged"
    raise ConflictError("target file has different content")


def _profile_bytes(assistant: str) -> bytes:
    return (json.dumps(
        {"assistant": assistant, "schema_version": 1},
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n").encode("utf-8")


def _sha256_hex(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


_HEX_DIGITS = frozenset("0123456789abcdef")


def _ledger_bytes(assistant: str, files: dict) -> bytes:
    return (json.dumps(
        {"assistant": assistant, "files": files, "schema_version": 1},
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n").encode("utf-8")


def _valid_ledger_path(path: object) -> bool:
    if not isinstance(path, str) or not path or "\\" in path or "\0" in path:
        return False
    if any(unicodedata.category(character) == "Cc" for character in path):
        return False
    if unicodedata.normalize("NFC", path) != path:
        return False
    if path.startswith("/"):
        return False
    parts = path.split("/")
    return all(part not in {"", ".", ".."} for part in parts)


def _read_profile_assistant(target: Path) -> str | None:
    """Assistant recorded in the validator-owned profile; None when missing."""
    profile_path = target / ".ai" / "assistant-profile.json"
    try:
        metadata = profile_path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(metadata.st_mode):
        raise InputError("assistant profile must be a regular file")
    raw = _read_regular_file(profile_path, "assistant profile")
    try:
        decoded = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_unique_json_object,
        )
    except (UnicodeDecodeError, ValueError) as error:
        raise InputError("assistant profile is not valid JSON") from error
    if not isinstance(decoded, dict):
        raise InputError("assistant profile must be a JSON object")
    if set(decoded) != {"assistant", "schema_version"}:
        raise InputError("assistant profile keys are unsupported")
    if type(decoded["schema_version"]) is not int or decoded["schema_version"] != 1:
        raise InputError("assistant profile schema version is unsupported")
    assistant = decoded["assistant"]
    if assistant not in {"codex", "claude"}:
        raise InputError("assistant profile assistant is invalid")
    return assistant


def _load_ledger(target: Path, expected_assistant: str | None = None) -> dict:
    """Installer ledger files map; a missing ledger means legacy install."""
    ledger_path = target / ".ai" / "installer-ledger.json"
    try:
        metadata = ledger_path.lstat()
    except FileNotFoundError:
        return {}
    if not stat.S_ISREG(metadata.st_mode):
        raise InputError("installer ledger must be a regular file")
    raw = _read_regular_file(ledger_path, "installer ledger")
    try:
        decoded = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_unique_json_object,
        )
    except (UnicodeDecodeError, ValueError) as error:
        raise InputError("installer ledger is not valid JSON") from error
    if not isinstance(decoded, dict):
        raise InputError("installer ledger must be a JSON object")
    if set(decoded) != {"assistant", "files", "schema_version"}:
        raise InputError("installer ledger keys are unsupported")
    if type(decoded["schema_version"]) is not int or decoded["schema_version"] != 1:
        raise InputError("installer ledger schema version is unsupported")
    assistant = decoded["assistant"]
    if assistant not in {"codex", "claude"}:
        raise InputError("installer ledger assistant is invalid")
    if expected_assistant is not None and assistant != expected_assistant:
        raise InputError("installer ledger belongs to a different assistant")
    files = decoded["files"]
    if not isinstance(files, dict):
        raise InputError("installer ledger files must be an object")
    for path, digest in files.items():
        if not _valid_ledger_path(path):
            raise InputError("installer ledger path is invalid")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in _HEX_DIGITS for character in digest)
        ):
            raise InputError("installer ledger digest is invalid")
    return dict(files)


def _gitignore_block(assistant: str) -> bytes:
    return (
        "# >>> portable-ai-workflow installer >>>\n"
        "/.ai-local/\n"
        f"/.{assistant}/sdd/\n"
        "__pycache__/\n"
        "*.py[cod]\n"
        "# <<< portable-ai-workflow installer <<<\n"
    ).encode("utf-8")


def _plan_gitignore(target: Path, assistant: str) -> PlanItem:
    relative_path = ".gitignore"
    target_file = target / relative_path
    block = _gitignore_block(assistant)
    try:
        metadata = target_file.lstat()
    except FileNotFoundError:
        return PlanItem(relative_path, block, 0o644, "create")
    except OSError as error:
        raise ConflictError(".gitignore cannot be inspected") from error
    if not stat.S_ISREG(metadata.st_mode):
        raise ConflictError(".gitignore must be a regular file")
    existing = _read_regular_file(target_file, ".gitignore")
    start_marker = b"# >>> portable-ai-workflow installer >>>"
    end_marker = b"# <<< portable-ai-workflow installer <<<"
    start_count = existing.count(start_marker)
    end_count = existing.count(end_marker)
    if start_count or end_count:
        block_index = existing.find(block)
        block_is_independent = (
            block_index >= 0
            and (block_index == 0 or existing[block_index - 1:block_index] == b"\n")
        )
        if start_count == 1 and end_count == 1 and block_is_independent:
            return PlanItem(
                relative_path, existing, 0o644, "unchanged",
                original_bytes=existing,
            )
        raise ConflictError(".gitignore contains a conflicting managed block")
    if not existing:
        updated = block
    elif existing.endswith(b"\n"):
        updated = existing + b"\n" + block
    else:
        updated = existing + b"\n\n" + block
    return PlanItem(
        relative_path, updated, 0o644, "update", original_bytes=existing,
    )


def _capture_plan_target_state(
    target: Path, items: tuple[PlanItem, ...],
) -> tuple[
    tuple[int, int, int],
    tuple[tuple[str, tuple[int, int, int]], ...],
    tuple[PlanItem, ...],
]:
    root_fd = _open_directory_path(target, "target root")
    directories: dict[str, tuple[int, int, int]] = {
        "": _binding(os.fstat(root_fd))
    }
    captured: list[PlanItem] = []
    try:
        for item in items:
            components = tuple(item.path.split("/"))
            current_fd = os.dup(root_fd)
            missing_parent = False
            try:
                traversed: list[str] = []
                for component in components[:-1]:
                    traversed.append(component)
                    if missing_parent:
                        continue
                    try:
                        metadata = os.stat(
                            component, dir_fd=current_fd, follow_symlinks=False,
                        )
                    except FileNotFoundError:
                        missing_parent = True
                        continue
                    except OSError as error:
                        raise ConflictError("target parent cannot be inspected") from error
                    if not stat.S_ISDIR(metadata.st_mode):
                        raise ConflictError("target parent is not a real directory")
                    next_fd = _open_relative_directory(
                        current_fd, (component,), "target parent",
                    )
                    if _binding(metadata) != _binding(os.fstat(next_fd)):
                        os.close(next_fd)
                        raise ConflictError("target parent changed during inspection")
                    os.close(current_fd)
                    current_fd = next_fd
                    directories["/".join(traversed)] = _binding(metadata)
                version = None
                target_mode = None
                if not missing_parent:
                    try:
                        leaf = os.stat(
                            components[-1], dir_fd=current_fd,
                            follow_symlinks=False,
                        )
                    except FileNotFoundError:
                        leaf = None
                    except OSError as error:
                        raise ConflictError("target leaf cannot be inspected") from error
                    if leaf is not None:
                        if not stat.S_ISREG(leaf.st_mode):
                            raise ConflictError("target leaf is not a regular file")
                        version = _file_version(leaf)
                        target_mode = stat.S_IMODE(leaf.st_mode)
                captured.append(
                    PlanItem(
                        item.path,
                        item.source_bytes,
                        item.mode,
                        item.action,
                        version,
                        target_mode,
                        item.original_bytes,
                    )
                )
            finally:
                os.close(current_fd)
        _verify_directory_path(target, root_fd, "target root")
        return (
            directories[""],
            tuple(sorted(directories.items(), key=lambda entry: os.fsencode(entry[0]))),
            tuple(captured),
        )
    finally:
        os.close(root_fd)


def build_plan(source_root: Path, target_input: Path, assistant: str) -> InstallPlan:
    """Build an immutable, read-only installation plan."""
    if assistant not in {"codex", "claude"}:
        raise InputError("assistant is unsupported")
    try:
        resolved_source = source_root.resolve(strict=True)
    except OSError as error:
        raise InputError("source root does not exist") from error
    target = _validated_target(target_input)
    if target == resolved_source or _is_relative_to(target, resolved_source):
        raise InputError("target is inside the installer source")
    asset_root = resolved_source / "scripts" / "ai-workflow-assets"
    manifest = load_manifest(asset_root)
    selected_entries = (*manifest.shared, *getattr(manifest, assistant))
    selected_paths = [entry.path for entry in selected_entries]
    if len(selected_paths) != len(set(selected_paths)):
        raise InputError("selected manifest paths are not globally unique")

    requested: list[tuple[str, bytes, int]] = [
        (entry.path, entry.source_bytes, entry.mode) for entry in selected_entries
    ]
    install_ledger = {
        entry.path: _sha256_hex(entry.source_bytes) for entry in selected_entries
    }
    requested.append(
        (".ai/assistant-profile.json", _profile_bytes(assistant), 0o644),
    )
    requested.append(
        (".ai/installer-ledger.json", _ledger_bytes(assistant, install_ledger), 0o644),
    )
    paths = [path for path, _content, _mode in requested]
    paths.append(".gitignore")
    if len(paths) != len(set(paths)):
        raise InputError("generated and manifest paths are not unique")
    planned_items = [
        PlanItem(path, content, mode, _target_action(target, path, content))
        for path, content, mode in sorted(requested, key=lambda item: os.fsencode(item[0]))
    ]
    planned_items.append(_plan_gitignore(target, assistant))
    items = tuple(sorted(planned_items, key=lambda item: os.fsencode(item.path)))
    target_binding, directory_bindings, captured_items = _capture_plan_target_state(
        target, items,
    )
    return InstallPlan(
        resolved_source,
        target,
        assistant,
        captured_items,
        target_binding,
        directory_bindings,
    )


def _upgrade_decision(current: "bytes | None", new_bytes: bytes, old_digest: "str | None") -> str:
    """Ledger-driven per-file action; lineage digests come from installed assets."""
    if current is None:
        return "create"
    current_digest = _sha256_hex(current)
    if current_digest == _sha256_hex(new_bytes):
        return "unchanged"
    if old_digest is not None and current_digest == old_digest:
        return "upgrade"
    return "skip"


def build_upgrade_plan(source_root: Path, target_input: Path, assistant: str) -> InstallPlan:
    """Build a ledger-driven upgrade plan that never touches modified target files."""
    if assistant not in {"codex", "claude"}:
        raise InputError("assistant is unsupported")
    try:
        resolved_source = source_root.resolve(strict=True)
    except OSError as error:
        raise InputError("source root does not exist") from error
    target = _validated_target(target_input)
    if target == resolved_source or _is_relative_to(target, resolved_source):
        raise InputError("target is inside the installer source")
    asset_root = resolved_source / "scripts" / "ai-workflow-assets"
    manifest = load_manifest(asset_root)
    selected_entries = (*manifest.shared, *getattr(manifest, assistant))
    selected_paths = [entry.path for entry in selected_entries]
    if len(selected_paths) != len(set(selected_paths)):
        raise InputError("selected manifest paths are not globally unique")

    profile_assistant = _read_profile_assistant(target)
    if profile_assistant is not None and profile_assistant != assistant:
        raise InputError("assistant profile belongs to a different assistant")
    ledger = _load_ledger(target, expected_assistant=assistant)
    selected_set = set(selected_paths)
    new_ledger: dict = {}
    planned_items: list[PlanItem] = []
    for entry in sorted(selected_entries, key=lambda item: os.fsencode(item.path)):
        current = _inspect_target_file(target, entry.path)
        action = _upgrade_decision(
            current, entry.source_bytes, ledger.get(entry.path),
        )
        content = entry.source_bytes if action != "skip" else current
        planned_items.append(
            PlanItem(
                entry.path, content, entry.mode, action,
                original_bytes=current if action == "upgrade" else None,
            ),
        )
        if action == "skip":
            if entry.path in ledger:
                new_ledger[entry.path] = ledger[entry.path]
        else:
            new_ledger[entry.path] = _sha256_hex(entry.source_bytes)
    for path in sorted(ledger, key=os.fsencode):
        if path in selected_set:
            continue
        current = _inspect_target_file(target, path)
        if current is None:
            continue
        if _sha256_hex(current) == ledger[path]:
            planned_items.append(
                PlanItem(path, current, 0o644, "remove", original_bytes=current),
            )
        else:
            planned_items.append(PlanItem(path, current, 0o644, "kept"))
            new_ledger[path] = ledger[path]

    profile_content = _ledger_bytes(assistant, new_ledger)
    current_profile = _inspect_target_file(
        target, ".ai/installer-ledger.json",
    )
    if current_profile is None:
        profile_action = "create"
    elif current_profile == profile_content:
        profile_action = "unchanged"
    else:
        profile_action = "update"
    planned_items.append(
        PlanItem(
            ".ai/installer-ledger.json", profile_content, 0o644, profile_action,
            original_bytes=current_profile
            if profile_action == "update" else None,
        ),
    )
    planned_items.append(_plan_gitignore(target, assistant))
    items = tuple(sorted(planned_items, key=lambda item: os.fsencode(item.path)))
    target_binding, directory_bindings, captured_items = _capture_plan_target_state(
        target, items,
    )
    return InstallPlan(
        resolved_source,
        target,
        assistant,
        captured_items,
        target_binding,
        directory_bindings,
        upgrade=True,
    )


@dataclass
class _CreatedFile:
    parent_fd: int
    name: str
    binding: tuple[int, int, int]
    parent_components: tuple[str, ...]
    armed: bool = False


@dataclass
class _CreatedDirectory:
    parent_fd: int
    name: str
    binding: tuple[int, int, int] | None
    parent_components: tuple[str, ...]
    armed: bool = False


@dataclass
class _RemovedFile:
    parent_fd: int
    name: str
    backup_name: str
    backup_binding: tuple[int, int, int]
    original_size: int
    parent_components: tuple[str, ...]


@dataclass
class _UpdatedFile:
    parent_fd: int
    name: str
    installed_binding: tuple[int, int, int]
    backup_name: str
    original_version: tuple[int, int, int, int, int, int]
    parent_components: tuple[str, ...]


JournalEntry = Union[_CreatedFile, _CreatedDirectory, _UpdatedFile, _RemovedFile]


def _fault_point(_operation: str) -> None:
    """Test seam for deterministic I/O failure injection."""


def _after_revalidation(_plan: InstallPlan) -> None:
    """Test seam for mutations immediately after the full second preflight."""


def _random_temporary_name(name: str) -> str:
    return f".{name}.portable-ai-workflow-{os.urandom(16).hex()}.tmp"


def _renameat2(directory_fd: int, left: str, right: str, flags: int) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    try:
        renameat2 = libc.renameat2
    except AttributeError as error:
        raise OSError("atomic exchange is unavailable") from error
    renameat2.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    )
    renameat2.restype = ctypes.c_int
    if renameat2(
        directory_fd,
        os.fsencode(left),
        directory_fd,
        os.fsencode(right),
        flags,
    ) != 0:
        error_number = ctypes.get_errno()
        raise OSError(error_number, os.strerror(error_number))


def _rename_exchange(directory_fd: int, left: str, right: str) -> None:
    _renameat2(directory_fd, left, right, 2)


def _rename_noreplace(directory_fd: int, left: str, right: str) -> None:
    _renameat2(directory_fd, left, right, 1)


def _planned_directory_bindings(
    plan: InstallPlan,
) -> dict[str, tuple[int, int, int]]:
    return dict(plan.directory_bindings)


def _verify_root(plan: InstallPlan, root_fd: int) -> None:
    if _binding(os.fstat(root_fd)) != plan.target_binding:
        raise ConflictError("target root identity changed")
    _verify_directory_path(plan.target, root_fd, "target root")


def _verify_parent_binding(
    plan: InstallPlan,
    root_fd: int,
    parent_components: tuple[str, ...],
    parent_fd: int,
) -> None:
    _verify_root(plan, root_fd)
    _verify_relative_directory(
        root_fd, parent_components, parent_fd, "target parent",
    )


def _remove_directory_if_bound(
    parent_fd: int, name: str, binding: tuple[int, int, int],
) -> None:
    metadata = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    if not stat.S_ISDIR(metadata.st_mode):
        raise OSError("temporary directory was replaced")
    if _binding(metadata) != binding:
        raise OSError("temporary directory identity changed")
    os.rmdir(name, dir_fd=parent_fd)


def _prepare_temporary_directory(
    parent_fd: int, name: str,
) -> tuple[str, int, tuple[int, int, int], int]:
    temporary_name = _random_temporary_name(name)
    directory_fd = -1
    journal_parent_fd = -1
    created = False
    binding: tuple[int, int, int] | None = None
    try:
        os.mkdir(temporary_name, 0o755, dir_fd=parent_fd)
        created = True
        metadata = os.stat(
            temporary_name, dir_fd=parent_fd, follow_symlinks=False,
        )
        if not stat.S_ISDIR(metadata.st_mode):
            raise OSError("temporary directory is not a directory")
        binding = _binding(metadata)
        directory_fd = os.open(
            temporary_name, _directory_flags(), dir_fd=parent_fd,
        )
        if _binding(os.fstat(directory_fd)) != binding:
            raise OSError("temporary directory identity changed")
        journal_parent_fd = os.dup(parent_fd)
        return temporary_name, directory_fd, binding, journal_parent_fd
    except BaseException as primary:
        cleanup_error = None
        if created and binding is None:
            try:
                recovery_fd = os.open(
                    temporary_name, _directory_flags(), dir_fd=parent_fd,
                )
                try:
                    binding = _binding(os.fstat(recovery_fd))
                finally:
                    os.close(recovery_fd)
            except OSError as error:
                cleanup_error = error
        if created and binding is not None and cleanup_error is None:
            try:
                _remove_directory_if_bound(parent_fd, temporary_name, binding)
            except OSError as error:
                cleanup_error = error
        if journal_parent_fd >= 0:
            os.close(journal_parent_fd)
        if directory_fd >= 0:
            os.close(directory_fd)
        if cleanup_error is not None:
            raise TransactionError(
                "installation failed and rollback failed"
            ) from cleanup_error
        raise primary


def _ensure_parent_directory(
    plan: InstallPlan,
    root_fd: int,
    parent_components: tuple[str, ...],
    journal: list[JournalEntry],
    created_bindings: dict[str, tuple[int, int, int]],
) -> int:
    expected_bindings = _planned_directory_bindings(plan)
    current_fd = os.dup(root_fd)
    traversed: list[str] = []
    try:
        for component in parent_components:
            traversed.append(component)
            relative = "/".join(traversed)
            expected = expected_bindings.get(relative)
            created = created_bindings.get(relative)
            try:
                metadata = os.stat(
                    component, dir_fd=current_fd, follow_symlinks=False,
                )
            except FileNotFoundError:
                if expected is not None or created is not None:
                    raise ConflictError("target parent disappeared during installation")
                try:
                    (
                        temporary_name,
                        next_fd,
                        new_binding,
                        journal_parent_fd,
                    ) = _prepare_temporary_directory(current_fd, component)
                    entry = _CreatedDirectory(
                        journal_parent_fd,
                        component,
                        new_binding,
                        tuple(traversed[:-1]),
                    )
                    journal.append(entry)
                    try:
                        _verify_parent_binding(
                            plan, root_fd, tuple(traversed[:-1]), current_fd,
                        )
                        _rename_noreplace(
                            current_fd, temporary_name, component,
                        )
                        entry.armed = True
                        _verify_parent_binding(
                            plan, root_fd, tuple(traversed), next_fd,
                        )
                    except BaseException as primary:
                        if not entry.armed:
                            try:
                                _remove_directory_if_bound(
                                    current_fd, temporary_name, new_binding,
                                )
                            except OSError as cleanup_error:
                                raise TransactionError(
                                    "installation failed and rollback failed"
                                ) from cleanup_error
                        os.close(next_fd)
                        raise primary
                except (ConflictError, InputError, TransactionError):
                    raise
                except OSError as error:
                    raise TransactionError("installation failed") from error
                created_bindings[relative] = new_binding
            except OSError as error:
                raise ConflictError("target parent cannot be inspected") from error
            else:
                if not stat.S_ISDIR(metadata.st_mode):
                    raise ConflictError("target parent is not a real directory")
                next_fd = _open_relative_directory(
                    current_fd, (component,), "target parent",
                )
                actual = _binding(os.fstat(next_fd))
                if _binding(metadata) != actual:
                    os.close(next_fd)
                    raise ConflictError("target parent changed during installation")
                if expected is not None:
                    required = expected
                elif created is not None:
                    required = created
                else:
                    os.close(next_fd)
                    raise ConflictError("an unplanned target parent appeared")
                if actual != required:
                    os.close(next_fd)
                    raise ConflictError("target parent identity changed")
            os.close(current_fd)
            current_fd = next_fd
            _verify_root(plan, root_fd)
            _verify_relative_directory(
                root_fd, tuple(traversed), current_fd, "target parent",
            )
        result_fd = current_fd
        current_fd = -1
        return result_fd
    finally:
        if current_fd >= 0:
            os.close(current_fd)


def _verify_leaf_before_write(parent_fd: int, item: PlanItem) -> None:
    name = item.path.rsplit("/", 1)[-1]
    try:
        metadata = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        metadata = None
    except OSError as error:
        raise ConflictError("target leaf cannot be inspected") from error
    if item.action == "create":
        if metadata is not None:
            raise ConflictError("an unplanned target leaf appeared")
        return
    if metadata is None or not stat.S_ISREG(metadata.st_mode):
        raise ConflictError("target leaf identity changed")
    if item.target_version is None or _file_version(metadata) != item.target_version:
        raise ConflictError("target leaf identity changed")
    content = _read_regular_at(parent_fd, name, "target leaf")
    expected = (
        item.original_bytes
        if item.action in {"update", "upgrade"}
        else item.source_bytes
    )
    if content != expected:
        raise ConflictError("target leaf content changed")


def _write_all(descriptor: int, content: bytes, inject_faults: bool = True) -> None:
    view = memoryview(content)
    while view:
        if inject_faults:
            _fault_point("write")
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("short write")
        view = view[written:]


def _prepare_temporary_file(
    parent_fd: int, name: str, content: bytes, mode: int,
) -> tuple[str, tuple[int, int, int]]:
    temporary_name = _random_temporary_name(name)
    descriptor = -1
    try:
        _fault_point("open")
        descriptor = os.open(
            temporary_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
            | getattr(os, "O_CLOEXEC", 0),
            0o600,
            dir_fd=parent_fd,
        )
        _write_all(descriptor, content)
        _fault_point("fsync")
        os.fsync(descriptor)
        _fault_point("fchmod")
        os.fchmod(descriptor, mode)
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise OSError("temporary target is not regular")
        return temporary_name, _binding(metadata)
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
            descriptor = -1
        try:
            os.unlink(temporary_name, dir_fd=parent_fd)
        except FileNotFoundError:
            pass
        raise
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _regular_binding_at(
    parent_fd: int, name: str, description: str,
) -> tuple[int, int, int]:
    metadata = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    if not stat.S_ISREG(metadata.st_mode):
        raise OSError(f"{description} is not a regular file")
    return _binding(metadata)


def _binding_at(parent_fd: int, name: str) -> tuple[int, int, int]:
    return _binding(os.stat(name, dir_fd=parent_fd, follow_symlinks=False))


def _restore_unjournaled_update(
    parent_fd: int,
    temporary_name: str,
    target_name: str,
    temporary_binding: tuple[int, int, int],
) -> None:
    temporary_current = _binding_at(parent_fd, temporary_name)
    if temporary_current == temporary_binding:
        return
    target_current = _binding_at(parent_fd, target_name)
    if target_current != temporary_binding:
        raise OSError("atomic update state is indeterminate")
    _rename_exchange(parent_fd, temporary_name, target_name)
    if (
        _binding_at(parent_fd, temporary_name) != temporary_binding
        or _binding_at(parent_fd, target_name) != temporary_current
    ):
        raise OSError("atomic update reversal did not restore bindings")
    os.fsync(parent_fd)


def _unlink_regular_if_bound(
    parent_fd: int, name: str, expected: tuple[int, int, int],
) -> None:
    if _regular_binding_at(parent_fd, name, "temporary target") != expected:
        raise OSError("temporary target identity changed")
    os.unlink(name, dir_fd=parent_fd)


def _remove_created_leaf_if_bound(
    parent_fd: int, name: str, expected: tuple[int, int, int],
) -> None:
    try:
        actual = _binding_at(parent_fd, name)
    except FileNotFoundError:
        return
    if actual != expected:
        raise OSError("created target identity changed")
    os.unlink(name, dir_fd=parent_fd)
    os.fsync(parent_fd)


def _publish_created_file(
    plan: InstallPlan,
    root_fd: int,
    parent_fd: int,
    item: PlanItem,
    journal: list[JournalEntry],
) -> None:
    name = item.path.rsplit("/", 1)[-1]
    parent_components = tuple(item.path.split("/"))[:-1]
    temporary_name, temporary_binding = _prepare_temporary_file(
        parent_fd, name, item.source_bytes, item.mode,
    )
    entry: _CreatedFile | None = None
    try:
        journal_parent_fd = os.dup(parent_fd)
        entry = _CreatedFile(
            journal_parent_fd,
            name,
            temporary_binding,
            parent_components,
        )
        journal.append(entry)
        _verify_leaf_before_write(parent_fd, item)
        _verify_parent_binding(
            plan, root_fd, parent_components, parent_fd,
        )
        _fault_point("publish")
        os.link(
            temporary_name,
            name,
            src_dir_fd=parent_fd,
            dst_dir_fd=parent_fd,
            follow_symlinks=False,
        )
        entry.armed = True
        _verify_parent_binding(
            plan, root_fd, parent_components, parent_fd,
        )
        os.unlink(temporary_name, dir_fd=parent_fd)
        temporary_name = ""
        _fault_point("fsync")
        os.fsync(parent_fd)
    except FileExistsError as error:
        raise ConflictError("an unplanned target leaf appeared") from error
    except BaseException as primary:
        if entry is not None and not entry.armed:
            try:
                _remove_created_leaf_if_bound(
                    parent_fd, name, temporary_binding,
                )
            except OSError as rollback_error:
                raise TransactionError(
                    "installation failed and rollback failed"
                ) from rollback_error
        raise primary
    finally:
        cleanup_during_exception = sys.exc_info()[0] is not None
        if temporary_name:
            try:
                _unlink_regular_if_bound(
                    parent_fd, temporary_name, temporary_binding,
                )
            except OSError as cleanup_error:
                if cleanup_during_exception:
                    raise TransactionError(
                        "installation failed and rollback failed"
                    ) from cleanup_error
                raise


def _publish_updated_file(
    plan: InstallPlan,
    root_fd: int,
    parent_fd: int,
    item: PlanItem,
    journal: list[JournalEntry],
) -> None:
    if (
        item.original_bytes is None
        or item.target_mode is None
        or item.target_version is None
    ):
        raise TransactionError("installation failed")
    name = item.path.rsplit("/", 1)[-1]
    parent_components = tuple(item.path.split("/"))[:-1]
    temporary_name, temporary_binding = _prepare_temporary_file(
        parent_fd, name, item.source_bytes, item.target_mode,
    )
    try:
        _verify_leaf_before_write(parent_fd, item)
        _verify_parent_binding(
            plan, root_fd, parent_components, parent_fd,
        )
        _fault_point("publish")
        _rename_exchange(parent_fd, temporary_name, name)
        original = os.stat(
            temporary_name, dir_fd=parent_fd, follow_symlinks=False,
        )
        original_content = (
            _read_regular_at(parent_fd, temporary_name, "atomic update backup")
            if stat.S_ISREG(original.st_mode)
            else None
        )
        if (
            not stat.S_ISREG(original.st_mode)
            or _binding(original) != item.target_version[:3]
            or original.st_size != item.target_version[3]
            or stat.S_IMODE(original.st_mode) != item.target_mode
            or original_content != item.original_bytes
        ):
            raise ConflictError("target leaf changed before atomic update")
        published = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if _binding(published) != temporary_binding:
            raise OSError("published target identity mismatch")
        journal.append(
            _UpdatedFile(
                os.dup(parent_fd),
                name,
                temporary_binding,
                temporary_name,
                _file_version(original),
                parent_components,
            )
        )
        temporary_name = ""
        _verify_parent_binding(
            plan, root_fd, parent_components, parent_fd,
        )
        _fault_point("fsync")
        os.fsync(parent_fd)
    except BaseException as primary:
        if temporary_name:
            try:
                _restore_unjournaled_update(
                    parent_fd,
                    temporary_name,
                    name,
                    temporary_binding,
                )
            except OSError as rollback_error:
                raise TransactionError(
                    "installation failed and rollback failed"
                ) from rollback_error
        raise primary
    finally:
        cleanup_during_exception = sys.exc_info()[0] is not None
        if temporary_name:
            try:
                _unlink_regular_if_bound(
                    parent_fd, temporary_name, temporary_binding,
                )
            except OSError as cleanup_error:
                if cleanup_during_exception:
                    raise TransactionError(
                        "installation failed and rollback failed"
                    ) from cleanup_error
                raise


def _restore_updated_file(entry: _UpdatedFile) -> None:
    current = os.stat(entry.name, dir_fd=entry.parent_fd, follow_symlinks=False)
    if _binding(current) != entry.installed_binding:
        raise OSError("updated target changed before rollback")
    original = os.stat(
        entry.backup_name, dir_fd=entry.parent_fd, follow_symlinks=False,
    )
    if _file_version(original) != entry.original_version:
        raise OSError("rollback backup identity changed")
    _rename_exchange(entry.parent_fd, entry.backup_name, entry.name)
    os.unlink(entry.backup_name, dir_fd=entry.parent_fd)
    os.fsync(entry.parent_fd)


def _restore_removed_file(entry: _RemovedFile) -> None:
    backup = os.stat(
        entry.backup_name, dir_fd=entry.parent_fd, follow_symlinks=False,
    )
    # rename 可能更新 ctime，备份身份只比对 binding 三元组与大小。
    if (
        _binding(backup) != entry.backup_binding
        or backup.st_size != entry.original_size
    ):
        raise OSError("rollback backup identity changed")
    try:
        os.stat(entry.name, dir_fd=entry.parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        pass
    else:
        raise OSError("removed target reappeared before rollback")
    os.rename(
        entry.backup_name, entry.name,
        src_dir_fd=entry.parent_fd, dst_dir_fd=entry.parent_fd,
    )
    os.fsync(entry.parent_fd)


def _restore_unjournaled_removal(
    parent_fd: int,
    name: str,
    backup_name: str,
    backup_binding: tuple[int, int, int],
    backup_size: int,
) -> None:
    """Return a just-renamed-aside original to its planned path (pre-journal)."""
    backup = os.stat(backup_name, dir_fd=parent_fd, follow_symlinks=False)
    if (
        _binding(backup) != backup_binding
        or backup.st_size != backup_size
    ):
        raise OSError("unjournaled removal backup identity changed")
    try:
        os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        pass
    else:
        raise OSError("removed target reappeared before unjournaled restore")
    os.rename(
        backup_name, name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd,
    )
    os.fsync(parent_fd)


def _publish_removed_file(
    plan: InstallPlan,
    root_fd: int,
    parent_fd: int,
    item: PlanItem,
    journal: list[JournalEntry],
) -> None:
    if (
        item.target_version is None
        or item.target_mode is None
        or item.original_bytes is None
    ):
        raise TransactionError("installation failed")
    name = item.path.rsplit("/", 1)[-1]
    parent_components = tuple(item.path.split("/"))[:-1]
    backup_name = _random_temporary_name(name)
    journalled_fd = -1
    try:
        _verify_leaf_before_write(parent_fd, item)
        _verify_parent_binding(plan, root_fd, parent_components, parent_fd)
        # VQ-01：在 rename 之前取得 journal 所需 fd，避免发布窗口内 dup 失败后原件失位。
        journalled_fd = os.dup(parent_fd)
        _fault_point("publish")
        os.rename(
            name, backup_name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd,
        )
        backup = None
        try:
            backup = os.stat(backup_name, dir_fd=parent_fd, follow_symlinks=False)
            # rename 可能更新 ctime，身份只比对 binding、大小与模式（与 update 同构）。
            if (
                _binding(backup) != item.target_version[:3]
                or backup.st_size != item.target_version[3]
                or stat.S_IMODE(backup.st_mode) != item.target_mode
            ):
                raise ConflictError("target leaf changed before removal")
            journal.append(
                _RemovedFile(
                    journalled_fd,
                    name,
                    backup_name,
                    _binding(backup),
                    backup.st_size,
                    parent_components,
                ),
            )
            journalled_fd = -1
        except BaseException:
            # 入账前失败：把被改名的原件放回原路径，不留失位临时文件。
            try:
                if backup is not None:
                    _restore_unjournaled_removal(
                        parent_fd, name, backup_name,
                        _binding(backup), backup.st_size,
                    )
                else:
                    os.rename(
                        backup_name, name,
                        src_dir_fd=parent_fd, dst_dir_fd=parent_fd,
                    )
                    os.fsync(parent_fd)
            except OSError as rollback_error:
                raise TransactionError(
                    "installation failed and rollback failed"
                ) from rollback_error
            raise
        _verify_parent_binding(plan, root_fd, parent_components, parent_fd)
        _fault_point("fsync")
        os.fsync(parent_fd)
    except BaseException:
        if journalled_fd >= 0:
            try:
                os.close(journalled_fd)
            except OSError:
                pass
        raise


def _rollback_journal(journal: list[JournalEntry]) -> None:
    failures: list[OSError] = []
    for entry in reversed(journal):
        try:
            if isinstance(entry, _UpdatedFile):
                _restore_updated_file(entry)
                continue
            if isinstance(entry, _RemovedFile):
                _restore_removed_file(entry)
                continue
            if not entry.armed:
                continue
            metadata = os.stat(
                entry.name, dir_fd=entry.parent_fd, follow_symlinks=False,
            )
            if _binding(metadata) != entry.binding:
                raise OSError("journal target identity changed")
            if isinstance(entry, _CreatedFile):
                os.unlink(entry.name, dir_fd=entry.parent_fd)
            else:
                os.rmdir(entry.name, dir_fd=entry.parent_fd)
            os.fsync(entry.parent_fd)
        except OSError as error:
            failures.append(error)
    if failures:
        raise OSError("one or more rollback operations failed")


def _close_journal(journal: list[JournalEntry]) -> None:
    for entry in journal:
        try:
            os.close(entry.parent_fd)
        except OSError:
            pass


def _verify_journal_bindings(
    plan: InstallPlan, root_fd: int, journal: list[JournalEntry],
) -> None:
    for entry in journal:
        if isinstance(entry, _RemovedFile):
            _verify_parent_binding(
                plan, root_fd, entry.parent_components, entry.parent_fd,
            )
            try:
                backup = os.stat(
                    entry.backup_name, dir_fd=entry.parent_fd,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                continue
            except OSError as error:
                raise ConflictError("journal target identity changed") from error
            if _binding(backup) != entry.backup_binding:
                raise ConflictError("journal target identity changed")
            continue
        if not isinstance(entry, _UpdatedFile) and not entry.armed:
            continue
        _verify_parent_binding(
            plan, root_fd, entry.parent_components, entry.parent_fd,
        )
        metadata = os.stat(
            entry.name, dir_fd=entry.parent_fd, follow_symlinks=False,
        )
        expected = (
            entry.installed_binding
            if isinstance(entry, _UpdatedFile)
            else entry.binding
        )
        if _binding(metadata) != expected:
            raise ConflictError("journal target identity changed")


def _ensure_update_recovery_backup(
    entry: _UpdatedFile, original_content: bytes, original_mode: int,
) -> None:
    try:
        existing = os.stat(
            entry.backup_name,
            dir_fd=entry.parent_fd,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        existing = None
    if existing is not None and _file_version(existing) == entry.original_version:
        return
    recovery_name, recovery_binding = _prepare_temporary_file(
        entry.parent_fd,
        f"{entry.name}-recovery",
        original_content,
        original_mode,
    )
    recovery = os.stat(
        recovery_name,
        dir_fd=entry.parent_fd,
        follow_symlinks=False,
    )
    if _binding(recovery) != recovery_binding:
        raise OSError("recovery backup identity changed")
    entry.backup_name = recovery_name
    entry.original_version = _file_version(recovery)
    os.fsync(entry.parent_fd)


def _ensure_removed_recovery_backup(
    entry: _RemovedFile, original_content: bytes, original_mode: int,
) -> None:
    try:
        existing = os.stat(
            entry.backup_name,
            dir_fd=entry.parent_fd,
            follow_symlinks=False,
        )
    except FileNotFoundError:
        existing = None
    if (
        existing is not None
        and _binding(existing) == entry.backup_binding
        and existing.st_size == entry.original_size
    ):
        return
    recovery_name, recovery_binding = _prepare_temporary_file(
        entry.parent_fd,
        f"{entry.name}-recovery",
        original_content,
        original_mode,
    )
    recovery = os.stat(
        recovery_name, dir_fd=entry.parent_fd, follow_symlinks=False,
    )
    if _binding(recovery) != recovery_binding:
        raise OSError("recovery backup identity changed")
    entry.backup_name = recovery_name
    entry.backup_binding = recovery_binding
    entry.original_size = recovery.st_size
    os.fsync(entry.parent_fd)


def _ensure_recovery_backup(entry, original_content: bytes, original_mode: int) -> None:
    if isinstance(entry, _UpdatedFile):
        _ensure_update_recovery_backup(entry, original_content, original_mode)
    else:
        _ensure_removed_recovery_backup(entry, original_content, original_mode)


def _commit_journal(
    plan: InstallPlan, root_fd: int, journal: list[JournalEntry],
) -> None:
    _verify_journal_bindings(plan, root_fd, journal)
    updates = [
        entry for entry in journal
        if isinstance(entry, (_UpdatedFile, _RemovedFile))
    ]
    # VQ-02：销毁任何备份前先读出全部备份内容与模式，供部分销毁后的再生恢复。
    prepared: list[tuple[object, bytes, int]] = []
    for entry in updates:
        original = os.stat(
            entry.backup_name,
            dir_fd=entry.parent_fd,
            follow_symlinks=False,
        )
        if isinstance(entry, _UpdatedFile):
            if _file_version(original) != entry.original_version:
                raise OSError("transaction backup identity changed")
        elif (
            _binding(original) != entry.backup_binding
            or original.st_size != entry.original_size
        ):
            raise OSError("transaction backup identity changed")
        original_content = _read_regular_at(
            entry.parent_fd, entry.backup_name, "transaction backup",
        )
        original_mode = stat.S_IMODE(original.st_mode)
        prepared.append((entry, original_content, original_mode))
    destroyed: list[tuple[object, bytes, int]] = []
    for entry, original_content, original_mode in prepared:
        unlinked = False
        try:
            _verify_journal_bindings(plan, root_fd, [entry])
            os.unlink(entry.backup_name, dir_fd=entry.parent_fd)
            unlinked = True
            _verify_journal_bindings(plan, root_fd, [entry])
        except BaseException as primary:
            try:
                for target_entry, content, mode in (
                    destroyed + ([(entry, original_content, original_mode)] if unlinked else [])
                ):
                    _ensure_recovery_backup(target_entry, content, mode)
            except BaseException as rollback_error:
                raise TransactionError(
                    "installation failed and rollback failed"
                ) from rollback_error
            raise primary
        destroyed.append((entry, original_content, original_mode))


def execute_plan(plan: InstallPlan, dry_run: bool = False) -> InstallResult:
    """Execute a fully revalidated plan as one rollback-capable transaction."""
    if dry_run:
        return InstallResult(plan, True)
    builder = build_upgrade_plan if plan.upgrade else build_plan
    refreshed = builder(plan.source_root, plan.target, plan.assistant)
    if refreshed != plan:
        raise ConflictError("installation inputs changed after planning")
    _after_revalidation(plan)
    target_binding, directory_bindings, captured_items = _capture_plan_target_state(
        plan.target, plan.items,
    )
    if (
        target_binding != plan.target_binding
        or directory_bindings != plan.directory_bindings
        or captured_items != plan.items
    ):
        raise ConflictError("installation inputs changed after revalidation")

    root_fd = _open_directory_path(plan.target, "target root")
    journal: list[JournalEntry] = []
    created_bindings: dict[str, tuple[int, int, int]] = {}
    try:
        _verify_root(plan, root_fd)
        for item in plan.items:
            parent_components = tuple(item.path.split("/"))[:-1]
            parent_fd = _ensure_parent_directory(
                plan,
                root_fd,
                parent_components,
                journal,
                created_bindings,
            )
            try:
                _verify_leaf_before_write(parent_fd, item)
                if item.action == "create":
                    _publish_created_file(plan, root_fd, parent_fd, item, journal)
                elif item.action in {"update", "upgrade"}:
                    _publish_updated_file(plan, root_fd, parent_fd, item, journal)
                elif item.action == "remove":
                    _publish_removed_file(plan, root_fd, parent_fd, item, journal)
                elif item.action not in {"unchanged", "skip", "kept"}:
                    raise TransactionError("installation failed")
            finally:
                os.close(parent_fd)
        _commit_journal(plan, root_fd, journal)
        return InstallResult(plan, False)
    except (ConflictError, InputError) as primary:
        if journal:
            try:
                _rollback_journal(journal)
            except OSError as rollback_error:
                raise TransactionError(
                    "installation failed and rollback failed"
                ) from rollback_error
        raise primary
    except TransactionError as primary:
        try:
            _rollback_journal(journal)
        except Exception as rollback_error:
            raise TransactionError(
                "installation failed and rollback failed"
            ) from rollback_error
        raise primary
    except Exception as primary:
        try:
            _rollback_journal(journal)
        except Exception as rollback_error:
            raise TransactionError(
                "installation failed and rollback failed"
            ) from rollback_error
        raise TransactionError("installation failed") from primary
    except BaseException:
        try:
            _rollback_journal(journal)
        except BaseException as rollback_error:
            raise TransactionError(
                "installation failed and rollback failed"
            ) from rollback_error
        raise
    finally:
        _close_journal(journal)
        os.close(root_fd)


def _parse_arguments(argv: list[str]) -> ParsedArguments:
    if argv in (["--help"], ["-h"]):
        return ParsedArguments(None, None, False, True)
    values: dict[str, str] = {}
    dry_run = False
    upgrade = False
    index = 0
    while index < len(argv):
        option = argv[index]
        if option == "--dry-run":
            if dry_run:
                raise UsageError("--dry-run may only be specified once")
            dry_run = True
            index += 1
            continue
        if option == "--upgrade":
            if upgrade:
                raise UsageError("--upgrade may only be specified once")
            upgrade = True
            index += 1
            continue
        if option in {"--target", "--assistant"}:
            if option in values:
                raise UsageError(f"{option} may only be specified once")
            if index + 1 >= len(argv) or argv[index + 1].startswith("--"):
                raise UsageError(f"{option} requires a value")
            values[option] = argv[index + 1]
            index += 2
            continue
        raise UsageError("unknown option or positional argument")
    if set(values) != {"--target", "--assistant"}:
        raise UsageError("--target and --assistant are required")
    if values["--assistant"] not in {"codex", "claude"}:
        raise UsageError("--assistant must be codex or claude")
    return ParsedArguments(
        Path(values["--target"]), values["--assistant"], dry_run, False, upgrade,
    )


def _print_plan(plan: InstallPlan, dry_run: bool) -> None:
    if plan.upgrade:
        labels = {
            "upgrade": "UPGRADED", "unchanged": "UNCHANGED", "create": "CREATED",
            "update": "UPDATED", "skip": "SKIPPED", "remove": "REMOVED",
            "kept": "KEPT",
        }
        notes = {
            "skip": "（目标已修改，保留；请人工比对新版）",
            "kept": "（已移除但目标已修改，保留）",
        }
        counts: dict = {}
        for item in plan.items:
            counts[item.action] = counts.get(item.action, 0) + 1
            note = notes.get(item.action, "")
            print(f"[{labels[item.action]}] {item.path}{note}")
        print(
            f"RESULT assistant={plan.assistant} target={plan.target} "
            f"upgraded={counts.get('upgrade', 0)} "
            f"unchanged={counts.get('unchanged', 0)} "
            f"created={counts.get('create', 0)} "
            f"updated={counts.get('update', 0)} "
            f"skipped={counts.get('skip', 0)} "
            f"removed={counts.get('remove', 0)} "
            f"kept={counts.get('kept', 0)} dry_run={int(dry_run)}"
        )
        return
    labels = {"create": "CREATE", "update": "UPDATE", "unchanged": "UNCHANGED"}
    counts = {"create": 0, "update": 0, "unchanged": 0}
    for item in plan.items:
        counts[item.action] += 1
        print(f"[{labels[item.action]}] {item.path}")
    print(
        f"RESULT assistant={plan.assistant} target={plan.target} "
        f"created={counts['create']} updated={counts['update']} "
        f"unchanged={counts['unchanged']} dry_run={int(dry_run)}"
    )


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    try:
        parsed = _parse_arguments(arguments)
    except UsageError as error:
        print(f"USAGE: {error}", file=sys.stderr)
        return 2
    if parsed.help_requested:
        print(USAGE, end="")
        return 0
    assert parsed.target is not None and parsed.assistant is not None
    source_root = Path(__file__).resolve().parents[2]
    builder = build_upgrade_plan if parsed.upgrade else build_plan
    try:
        plan = builder(source_root, parsed.target, parsed.assistant)
    except ConflictError as error:
        print(f"CONFLICT: {error}", file=sys.stderr)
        return 3
    except InputError as error:
        print(f"UNSAFE: {error}", file=sys.stderr)
        return 3
    except Exception:
        print("ERROR: internal preflight failure", file=sys.stderr)
        return 1
    if parsed.dry_run:
        _print_plan(plan, dry_run=True)
        return 0
    try:
        execute_plan(plan)
    except ConflictError as error:
        print(f"CONFLICT: {error}", file=sys.stderr)
        return 3
    except InputError as error:
        print(f"UNSAFE: {error}", file=sys.stderr)
        return 3
    except TransactionError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    except Exception:
        print("ERROR: internal installation failure", file=sys.stderr)
        return 1
    _print_plan(plan, dry_run=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
