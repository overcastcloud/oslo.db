#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
import os

from oslo_db._i18n import _LE
from oslo_db.sqlalchemy import migration
from oslo_db.sqlalchemy.migration_cli import ext_base


LOG = logging.getLogger(__name__)


class MigrateExtension(ext_base.MigrationExtensionBase):
    """Extension to provide sqlalchemy-migrate features.

    :param migration_config: Stores specific configuration for migrations
    :type migration_config: dict
    """

    order = 1

    def __init__(self, engine, migration_config):
        self.engine = engine
        self.repository = migration_config.get('migration_repo_path', '')
        self.init_version = migration_config.get('init_version', 0)

    @property
    def enabled(self):
        return os.path.exists(self.repository)

    def upgrade(self, version):
        version = None if version == 'head' else version
        return migration.db_sync(
            self.engine, self.repository, version,
            init_version=self.init_version)

    def downgrade(self, version):
        try:
            # version for migrate should be valid int - else skip
            if version in ('base', None):
                version = self.init_version
            version = int(version)
            return migration.db_sync(
                self.engine, self.repository, version,
                init_version=self.init_version)
        except ValueError:
            LOG.error(
                _LE('Migration number for migrate plugin must be valid '
                    'integer or empty, if you want to downgrade '
                    'to initial state')
            )
            raise

    def version(self):
        return migration.db_version(
            self.engine, self.repository, init_version=self.init_version)
