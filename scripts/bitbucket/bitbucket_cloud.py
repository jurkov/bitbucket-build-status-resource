from bitbucket import BitbucketDriver, BitbucketOAuth, request_access_token
from concourse import ConcourseResource, MissingSourceException
from requests.auth import HTTPBasicAuth


class BitbucketCloudDriver(BitbucketDriver, ConcourseResource):
    def __init__(self, config, debug):
        ConcourseResource.__init__(self, config)
        self.debug = debug
        self.repository = self.source(
            'repository',
            self.source(
                'repo',
                '{owner}/{repository}'.format(
                    owner=self.source(
                        'owner',
                        self.source('bitbucket_username', '')
                    ),
                    repository=self.source(
                        'repository_name',
                        self.param('repo', '')
                    )
                )
            )
        )
        self.client_id = self.source('client_id', '')
        self.cliend_secret = self.source('client_secret', self.source('secret', ''))

        if self.repository == '' or self.repository == '/':
            raise MissingSourceException('repository')

    def get_post_url(self, commit_hash):
        return 'https://api.bitbucket.org/2.0/repositories/{repository}/commit/{commit}/statuses/build'.format(
            repository=self.repository,
            commit=str(commit_hash)
        )

    def get_request_options(self):
        if self.client_id != '' and self.client_secret != '':
            access_token = request_access_token(self.client_id, self.client_secret, False)

            return {
                'auth': BitbucketOAuth(access_token)
            }
        elif self.username != '' and self.password != '':
            return {
                'auth': HTTPBasicAuth(self.username, self.password)
            }
        else:
            if self.client_id == '':
                raise MissingSourceException

            if self.client_secret == '':
                raise MissingSourceException

            exit(1)

    def get_valid_response_status(self):
        return [200, 201]
