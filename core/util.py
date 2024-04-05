import time
from flask import request
from collections import deque
from flask import g
from core.fn import hash_sha256
from logging import getLogger
call_history = {}

logger = getLogger(__name__)




def parse_rate_limit(rate_limit):
    """ convert rate limt into max_calls, time_frame

    Args:
        rate_limit (str): accespt rate limi in string format like 10/1m and return max_calls, time_frame
    """
    max_calls, time_frame = rate_limit.split('/')
    time_frame = convert_human_to_seconds(time_frame)
    return int(max_calls), time_frame


def convert_human_to_seconds(human_time):
    """ cpnvert human time to seconds

    Args:
        human_time (str): accept human time in string format end with s,m,h,d
    """
    if human_time.endswith('s'):
        return 1
    elif human_time.endswith('m'):
        return 60
    elif human_time.endswith('h'):
        return 3600
    elif human_time.endswith('d'):
        return 86400
    else:
        return int(human_time)


def convert_seconds_to_human(seconds):
    """ convert seconds to human readable format"""
    if seconds < 60:
        return f'{seconds} seconds'
    elif seconds < 3600:
        minutes = seconds / 60
        return f'{minutes} minutes'
    elif seconds < 86400:
        hours = seconds / 3600
        return f'{hours} hours'
    else:
        days = seconds / 86400
        return f'{days} days'

def rate_limited(limits: list = ['15/s']):
    """ratelimt decorator

    Args:
        limits (list, optional): accept ratelimit string add larger limits at first. Defaults to ['15/s'].
    """
    def decorator(handler):
        def wrapper(*args, **kwargs):
            logger.warning("rate_limited")
            logger.warning(limits)
            for limit in limits:
                max_calls, time_frame = parse_rate_limit(limit)
                id = request.remote_addr
                token_info = g.get('oidc_token_info')
                if (token_info is not None):
                    logger.warning("token_info found")
                    token_info.get('sub')
                    if (token_info.get('sub') is not None):
                        id = token_info.get('sub')
                    realm_access = token_info.get('realm_access', {})
                    roles = realm_access.get('roles', [])
                    if('master' in roles):
                        logger.warning("master role detected skiping rate limit.")
                        return handler(*args, **kwargs)
                id = hash_sha256(id + request.path +
                                 request.method + str(time_frame))
                if id not in call_history:
                    call_history[id] = deque()

                queue = call_history[id]
                current_time = time.time()

                while len(queue) > 0 and current_time - queue[0] > time_frame:
                    queue.popleft()

                if len(queue) >= max_calls:
                    time_passed = current_time - queue[0]
                    time_to_wait = int(time_frame - time_passed)
                    error_message = {
                        "code": 429,
                        "name": "Rate limit exceeded",
                        "description": f'Rate limit exceeded. Please try again after {convert_seconds_to_human(time_to_wait)}.',
                    }
                    logger.warning(error_message)
                    return error_message, 429

                queue.append(current_time)

            return handler(*args, **kwargs)
        # Renaming the function name:
        wrapper.__name__ = handler.__name__
        return wrapper

    return decorator
