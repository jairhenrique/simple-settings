# -*- coding: utf-8 -*-
import pytest

from simple_settings.core import LazySettings
from simple_settings.dynamic_settings import get_dynamic_reader

skip = False
try:
    from redis import StrictRedis
    from simple_settings.dynamic_settings.redis_reader import (
        Reader as RedisReader
    )
except ImportError:
    skip = True


@pytest.mark.skipif(skip, reason='Installed without redis')
class TestDynamicRedisSettings(object):

    @pytest.fixture
    def settings_dict_to_override_by_redis(self):
        return {
            'SIMPLE_SETTINGS': {
                'DYNAMIC_SETTINGS': {'backend': 'redis'}
            },
            'SIMPLE_STRING': 'simple'
        }

    @pytest.yield_fixture
    def redis(self):
        redis = StrictRedis()

        yield redis

        redis.flushall()

    @pytest.fixture
    def reader(self, settings_dict_to_override_by_redis):
        return get_dynamic_reader(settings_dict_to_override_by_redis)

    def test_should_return_an_instance_of_redis_reader(
        self, settings_dict_to_override_by_redis
    ):
        reader = get_dynamic_reader(settings_dict_to_override_by_redis)
        assert isinstance(reader, RedisReader)

    def test_should_override_string_by_redis(self, redis, reader):
        key = 'SIMPLE_STRING'
        expected_setting = 'simple from redis'
        redis.set(key, expected_setting)

        assert reader.get(key) == expected_setting

    def test_should_return_setting_by_redis_or_by_lazy_settings_obj(
        self, redis
    ):
        settings = LazySettings('tests.samples.simple')
        settings.configure(
            SIMPLE_SETTINGS={'DYNAMIC_SETTINGS': {'backend': 'redis'}}
        )

        assert settings.SIMPLE_STRING == 'simple'

        redis.set('SIMPLE_STRING', 'dynamic')
        assert settings.SIMPLE_STRING == 'dynamic'

        redis.delete('SIMPLE_STRING')
        assert settings.SIMPLE_STRING == 'simple'