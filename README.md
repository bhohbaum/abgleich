# ABGLEICH

## SYNOPSIS

`abgleich` is a simple ZFS sync tool. It displays source and target ZFS zpool, dataset and snapshot trees. It creates meaningful snapshots only if datasets have actually been changed. It compares a source zpool tree to a target, backup zpool tree. It pushes backups from a source to a target. It cleanes up older snapshots on the source side if they are present on the target side. It runs on a command line and produces nice, user-friendly, human-readable, colorized output. It also includes a GUI.

## CLI EXAMPLE

![demo](https://github.com/pleiszenburg/abgleich/blob/master/docs/demo.png?raw=true "demo")

## GUI EXAMPLE

| snap | backup | cleanup |
|:----:|:------:|:-------:|
| ![snap](https://github.com/pleiszenburg/abgleich/blob/master/docs/demo_gui01.png?raw=true "snap") | ![backup](https://github.com/pleiszenburg/abgleich/blob/master/docs/demo_gui02.png?raw=true "backup") | ![cleanup](https://github.com/pleiszenburg/abgleich/blob/master/docs/demo_gui03.png?raw=true "cleanup") |

## INSTALLATION

The base CLI tool can be installed as follows:

```bash
pip install -vU abgleich
```

An installation also including a GUI can be triggered by running:

```bash
pip install -vU abgleich[gui]
```

Requires [CPython](https://en.wikipedia.org/wiki/CPython) 3.6 or later, a [Unix shell](https://en.wikipedia.org/wiki/Unix_shell) and [ssh](https://en.wikipedia.org/wiki/Secure_Shell). GUI support requires [Qt5](https://en.wikipedia.org/wiki/Qt_(software)) in addition. Tested with [OpenZFS](https://en.wikipedia.org/wiki/OpenZFS) 0.8.x on Linux.

`abgleich`, CPython and the Unix shell must only be installed on one of the involved systems. Any remote system will be contacted via ssh and provided with direct ZFS commands.

## INITIALIZATION

All actions involving a remote host assume that `ssh` with public key authentication instead of passwords is correctly configured and working.

Let's assume that everything in `source_tank/data` and below should be synced with `target_tank/some_backup/data`. `source_tank` and `target_tank` are zpools. `data` is the "prefix" for the source zpool, `some_backup/data` is the corresponding "prefix" for the target zpool. For `abgleich` to work, `source_tank/data` and `target_tank/some_backup` must exist. `target_tank/some_backup/data` must not exist. The latter will be created by `abgleich`. It is highly recommended to set the mountpoint of `target_tank/some_backup` to `none` before running `abgleich` for the first time.

Rights to run the following commands are required:

| command        | source | target |
|----------------|:------:|:------:|
| `zfs list`     |    x   |    x   |
| `zfs get`      |    x   |    x   |
| `zfs snapshot` |    x   |        |
| `zfs send`     |    x   |        |
| `zfs receive`  |        |    x   |
| `zfs destroy`  |    x   |        |

### `config.yaml`

Complete example configuration file:

```yaml
source:
    zpool: tank_ssd
    prefix:
    host: localhost
    user:
target:
    zpool: tank_hdd
    prefix: BACKUP_SOMEMACHINE
    host: bigdata
    user: zfsadmin
include_root: yes
keep_snapshots: 2
always_changed: no
written_threshold: 1048576
check_diff: yes
suffix: _backup
digits: 2
ignore:
    - home/user/CACHE
    - home/user/CCACHE
ssh:
    compression: no
    cipher: aes256-gcm@openssh.com
```

The prefix can be empty on either side. If a `host` is set to `localhost`, the `user` field can be left empty. Both source and target can be remote hosts or localhost at the same time. `include_root` indicates whether `{zpool}{/{prefix}}` should be  included in all operations. `keep_snapshots` is an integer and must be greater or equal to `1`. It specifies the number of snapshots that are kept per dataset on the source side when a cleanup operation is triggered. `suffix` contains the name suffix for new snapshots. Setting `always_changed` to `yes` causes `abgleich` to beliefe that all datasets have always changed since the last snapshot, completely ignoring what ZFS actually reports. No diff will be produced & checked for values of `written` lower than `written_threshold`. Checking diffs can be completely deactivated by setting `check_diff` to `no`. `digits` specifies how many digits are used for a decimal number describing the n-th snapshot per dataset per day as part of the name of new snapshots. `ignore` lists stuff underneath the `prefix` which will be ignored by this tool, i.e. no snapshots, backups or cleanups. `ssh` allows to fine-tune the speed of backups. In fast local networks, it is best to set `compression` to `no` because the compression is usually slowing down the transfer. However, for low-bandwidth transmissions, it makes sense to set it to `yes`. For significantly better speed in fast local networks, make sure that both the source and the target system support a common cipher, which is accelerated by [AES-NI](https://en.wikipedia.org/wiki/AES_instruction_set) on both ends.

## USAGE

All potentially changing or destructive actions are listed in detail before the user is asked to confirm them. None of the commands listed below create, change or destroy a zpool, dataset or snapshot on their own without the user's explicit consent.

### `abgleich tree config.yaml [source|target]`

Show ZFS tree with snapshots, disk space and compression ratio. Append `source` or `target` (optional).

### `abgleich snap config.yaml`

Determine which datasets on the source side have been changed since last snapshot. Generate snapshots on the source side where applicable.

### `abgleich compare config.yaml`

Compare source ZFS tree with target ZFS tree. See what is missing where.

### `abgleich backup config.yaml`

Send (new) datasets and new snapshots from source to target.

### `abgleich cleanup config.yaml`

Cleanup older local snapshots on source side if they are present on both sides. Of those snapshots present on both sides, keep at least `keep_snapshots` number of snapshots on source side.

### `abgleich wizard config.yaml`

Runs a sequence of `snap`, `backup` and `cleanup` in a wizard GUI. This command is only available if `abgleich` was installed with GUI support.

## SPEED

`abgleich` uses Python's [type hints](https://docs.python.org/3/library/typing.html) and enforces them with [typeguard](https://github.com/agronholm/typeguard) at runtime. It furthermore makes countless assertions.

The enforcement of types and assertions can be controlled through the `PYTHONOPTIMIZE` environment variable. If set to `0` (the implicit default value), all checks are activated. `abgleich` will run slow. For safety, this mode is highly recommended. For significantly higher speed, all type checks and most assertions can be deactivated by setting `PYTHONOPTIMIZE` to `1` or `2`, e.g. `PYTHONOPTIMIZE=1 abgleich tree config.yaml`. This is not recommended. You may want to check if another tool or configuration has altered this environment variable by running `echo $PYTHONOPTIMIZE`.
