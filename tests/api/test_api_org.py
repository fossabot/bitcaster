from typing import TYPE_CHECKING, TypedDict

import pytest
from rest_framework.test import APIClient
from testutils.factories import ApiKeyFactory, ChannelFactory, EventFactory
from testutils.perms import key_grants

from bitcaster.auth.constants import Grant

if TYPE_CHECKING:
    from bitcaster.models import (
        ApiKey,
        Application,
        Channel,
        Event,
        Organization,
        Project,
        User,
    )

    Context = TypedDict(
        "Context",
        {
            "org": Organization,
            "prj": Project,
            "app": Application,
            "event": Event,
            "key": ApiKey,
            "user": User,
            "ch": Channel,
        },
    )

pytestmark = [pytest.mark.api, pytest.mark.django_db]

# WE DO NOT USE REVERSE HERE. WE NEED TO CHECK ENDPOINTS CONTRACTS

org_slug = "org1"
prj_slug = "prj1"
app_slug = "app1"
event_slug = "evt1"


@pytest.fixture()
def client(data) -> APIClient:
    c = APIClient()
    g = key_grants(data["key"], Grant.FULL_ACCESS)
    g.start()
    c.credentials(HTTP_AUTHORIZATION=f"Key {data['key'].key}")
    yield c
    g.stop()


@pytest.fixture()
def data(admin_user, system_objects) -> "Context":

    event: Event = EventFactory(
        application__project__organization__slug=org_slug,
        application__project__slug=prj_slug,
        application__slug=app_slug,
        slug=event_slug,
    )
    key = ApiKeyFactory(
        user=admin_user, grants=[], application=None, project=None, organization=event.application.project.organization
    )
    ch = ChannelFactory(project=event.application.project)
    return {
        "org": event.application.project.organization,
        "prj": event.application.project,
        "app": event.application,
        "event": event,
        "key": key,
        "user": admin_user,
        "ch": ch,
    }


def test_org_detail(client: APIClient, organization: "Organization") -> None:
    url = f"/api/o/{organization.slug}/"
    res = client.get(url)
    data: dict = res.json()
    assert data["slug"] == organization.slug


def test_org_channels(client: APIClient, org_channel: "Channel") -> None:
    # list organization channels
    url = f"/api/o/{org_channel.organization.slug}/c/"
    res = client.get(url)
    data: dict = res.json()
    assert data == [{"name": org_channel.name, "protocol": org_channel.protocol}]


def test_user_list(client: APIClient, org_user: "User") -> None:
    url = f"/api/o/{org_user.organizations.first().slug}/u/"
    res = client.get(url)
    data: list[dict] = res.json()
    ids = [e["id"] for e in data]
    assert ids == [org_user.pk]


def test_user_add_existing(client: APIClient, data: "Context", user: "User") -> None:
    # add exiting user to the organization
    url = f"/api/o/{org_slug}/u/"
    res = client.post(url, {"email": user.email})
    data: dict = res.json()
    assert data["id"] == user.pk


def test_user_add_new(client: APIClient, data: "Context") -> None:
    # create new user and add to the organization
    url = f"/api/o/{org_slug}/u/"
    res = client.post(url, {"email": "user@example.com"})
    data: dict = res.json()
    assert data["email"] == "user@example.com"
