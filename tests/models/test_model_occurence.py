from typing import TYPE_CHECKING, TypedDict
from unittest.mock import Mock

import pytest

if TYPE_CHECKING:
    from bitcaster.models import Notification, Occurrence

    Context = TypedDict(
        "Context",
        {"occurence": Occurrence, "notification": Notification},
    )


@pytest.fixture
def context(occurrence: "Occurrence", user) -> "Context":
    from testutils.factories import (
        ChannelFactory,
        NotificationFactory,
        ValidationFactory,
    )

    notification = NotificationFactory(event__channels=[ChannelFactory()], payload_filter="foo=='bar'")
    validation = ValidationFactory(channel=notification.event.channels.first())
    notification.distribution.recipients.add(validation)

    return {"validation": validation, "notification": notification}


@pytest.mark.parametrize(
    "payload, notified_count",
    [pytest.param({"foo": "bar"}, 1, id="matched"), pytest.param({"foo": "dummy"}, 0, id="unmatched")],
)
def test_model_occurrence_filter(payload, notified_count, context: "Context", monkeypatch):
    monkeypatch.setattr("bitcaster.models.notification.Notification.notify_to_channel", mock := Mock())

    occurrence = context["notification"].event.trigger(payload)
    occurrence.process()

    assert mock.call_count == notified_count
    occurrence.refresh_from_db()

    if notified_count == 1:
        assert occurrence.data == {
            "delivered": [context["validation"].id],
            "recipients": [[context["validation"].address.value, context["validation"].channel.name]],
        }


def test_model_occurrence_no_notifications(occurrence: "Occurrence", monkeypatch):
    monkeypatch.setattr("bitcaster.models.notification.Notification.get_context", mock := Mock())
    assert occurrence.process() is True
    assert mock.called is False


def test_str(occurrence: "Occurrence"):
    assert str(occurrence)
