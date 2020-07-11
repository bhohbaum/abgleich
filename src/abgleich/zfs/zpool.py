# -*- coding: utf-8 -*-

"""

ABGLEICH
zfs sync tool
https://github.com/pleiszenburg/abgleich

    src/abgleich/zfs/zpool.py: ZFS zpool

    Copyright (C) 2019-2020 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/pleiszenburg/abgleich/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import typing

from tabulate import tabulate
import typeguard

from .abc import DatasetABC, ZpoolABC
from .dataset import Dataset
from ..command import Command
from ..io import colorize, humanize_size

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typeguard.typechecked
class Zpool(ZpoolABC):

    def __init__(
        self, datasets: typing.List[DatasetABC], side: str, config: typing.Dict,
    ):

        self._datasets = datasets
        self._side = side
        self._config = config

    @property
    def datasets(self) -> typing.Generator[DatasetABC, None, None]:

        return (dataset for dataset in self._datasets)

    def print_table(self, color: bool = True):

        table = []
        for dataset in self._datasets:
            table.append([
                colorize(dataset.name, "white"),
                humanize_size(dataset['used'].value, add_color=True),
                humanize_size(dataset['referenced'].value, add_color=True),
                f'{dataset["compressratio"].value:.02f}',
            ])
            for snapshot in dataset.snapshots:
                table.append([
                    '- ' + colorize(snapshot.name, "grey"),
                    humanize_size(snapshot['used'].value, add_color=True),
                    humanize_size(snapshot['referenced'].value, add_color=True),
                    f'{snapshot["compressratio"].value:.02f}',
                ])

        print(tabulate(
            table,
            headers=("NAME", "USED", "REFER", "compressratio"),
            tablefmt="github",
            colalign=("left", "right", "right", "decimal"),
            ))

    @classmethod
    def from_config(cls, side: str, config: typing.Dict) -> ZpoolABC:

        output, _ = Command.on_side(["zfs", "list", "-H", "-p"], side, config).run()

        return cls(
            datasets = [
                Dataset.from_line(line, side, config)
                for line in output.split('\n')
                if len(line.strip()) > 0
                ],
            side = side,
            config = config,
            )
