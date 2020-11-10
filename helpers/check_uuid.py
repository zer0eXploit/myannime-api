from uuid import UUID


def valid_uuid4(episode_id):
    '''
    Validate that a UUID string is in fact a valid uuid4.
    '''
    try:
        UUID(episode_id, version=4)
        return True
    except ValueError:
        return False
