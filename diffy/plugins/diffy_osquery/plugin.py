"""
.. module: diffy.plugins.diffy_osquery.plugin
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import logging
from typing import List
from boto3 import Session

from diffy.config import CONFIG
from diffy.exceptions import BadArguments
from diffy.plugins import diffy_osquery as osquery
from diffy.plugins.bases import PayloadPlugin


logger = logging.getLogger(__name__)


class OSQueryPayloadPlugin(PayloadPlugin):
    title = 'osquery'
    slug = 'osquery-payload'
    description = 'Uses osquery as part of the collection payload.'
    version = osquery.__version__

    author = 'Kevin Glisson'
    author_url = 'https://github.com/netflix/diffy.git'

    def generate(self, incident: str, **kwargs) -> List[str]:
        """Generates the commands that will be run on the host."""
        logger.debug('Generating osquery payload.')
        session = Session()

        # TODO check for existence before deployment
        # we run with these commands with diffy credentials so as to not pollute the on-instance credentials
        creds = session.get_credentials()
        region = kwargs.get('region', CONFIG.get('DIFFY_PAYLOAD_OSQUERY_REGION'))
        key = kwargs.get('key', CONFIG.get('DIFFY_PAYLOAD_OSQUERY_KEY'))

        if not region:
            raise BadArguments('DIFFY_PAYLOAD_OSQUERY_REGION required for use with OSQuery plugin.')

        if not key:
            raise BadArguments('DIFFY_PAYLOAD_OSQUERY_KEY required for use with OSQuery plugin.')

        commands = [
            f'export AWS_ACCESS_KEY_ID={creds.access_key}',
            f'export AWS_SECRET_ACCESS_KEY={creds.secret_key}',
            f'export AWS_SESSION_TOKEN={creds.token}',
            f'cd $(mktemp -d -t binaries-{incident}-`date +%s`-XXXXXX)',
            f'aws s3 --region {region} cp s3://{key} ./latest.tar.bz2 --quiet',
            'tar xvf latest.tar.bz2 &>/dev/null',
        ]

        commands += CONFIG.get('DIFFY_PAYLOAD_OSQUERY_COMMANDS')
        return commands
