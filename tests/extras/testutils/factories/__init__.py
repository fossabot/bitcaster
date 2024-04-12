from . import base
from .address import AddressFactory  # noqa
from .channel import ChannelFactory  # noqa
from .django_auth import GroupFactory, PermissionFactory  # noqa
from .django_celery_beat import PeriodicTaskFactory  # noqa
from .event import EventFactory  # noqa
from .key import ApiKeyFactory  # noqa
from .log import LogEntryFactory  # noqa
from .message import MessageFactory  # noqa
from .org import (ApplicationFactory, OrganizationFactory,  # noqa
                  ProjectFactory)
from .role import RoleFactory  # noqa
from .subscription import SubscriptionFactory  # noqa
from .user import SuperUserFactory, UserFactory  # noqa
from .validation import ValidationFactory  # noqa


def get_factory_for_model(_model) -> type[base.TAutoRegisterModelFactory]:
    class Meta:
        model = _model

    bases = (base.AutoRegisterModelFactory,)
    if _model in base.factories_registry:
        return base.factories_registry[_model]  # noqa

    return type(f"{_model._meta.model_name}Factory", bases, {"Meta": Meta})  # noqa
