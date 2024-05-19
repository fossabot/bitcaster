import uuid

import concurrency.fields
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.postgres.fields
import django.core.files.storage
import django.db.models.deletion
import django.utils.timezone
import strategy_field.fields
from django.conf import settings
from django.contrib.postgres.operations import CreateCollation
from django.db import migrations, models

import bitcaster.models.key
import bitcaster.models.user

# Generated by Django 5.0.4 on 2024-05-18 16:37


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        CreateCollation("case_insensitive", provider="icu", locale="und-u-ks-level2", deterministic=False),
        migrations.CreateModel(
            name="Group",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("auth.group",),
            managers=[
                ("objects", django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", concurrency.fields.IntegerVersionField(default=0, help_text="record revision number")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={"unique": "A user with that username already exists."},
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                        verbose_name="username",
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                ("custom_fields", models.JSONField(blank=True, default=dict)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "permissions": (("bitcaster.lock_system", "Can lock system components"),),
                "abstract": False,
            },
            managers=[
                ("objects", bitcaster.models.user.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Address",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", concurrency.fields.IntegerVersionField(default=0, help_text="record revision number")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("GENERIC", "Generic address"),
                            ("email", "Email"),
                            ("phone", "Phone"),
                            ("account", "Account"),
                        ],
                        default="GENERIC",
                        max_length=10,
                    ),
                ),
                ("value", models.CharField(max_length=255)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="addresses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
                "unique_together": {("user", "name"), ("user", "value")},
            },
        ),
        migrations.CreateModel(
            name="Application",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("locked", models.BooleanField(default=False, help_text="Security lock of project")),
                ("version", concurrency.fields.IntegerVersionField(default=0, help_text="record revision number")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(blank=True, max_length=255)),
                ("active", models.BooleanField(default=True, help_text="Whether the application should be active")),
                (
                    "from_email",
                    models.EmailField(
                        blank=True, default="", help_text="default from address for emails", max_length=254
                    ),
                ),
                (
                    "subject_prefix",
                    models.CharField(
                        default="[Bitcaster] ",
                        help_text="Default prefix for messages supporting subject",
                        max_length=50,
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Owner",
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Channel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("locked", models.BooleanField(default=False, help_text="Security lock of project")),
                ("version", concurrency.fields.IntegerVersionField(default=0, help_text="record revision number")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, verbose_name="Name")),
                ("dispatcher", strategy_field.fields.StrategyField(default="test")),
                ("config", models.JSONField(blank=True, default=dict)),
                (
                    "protocol",
                    models.CharField(
                        choices=[
                            ("PLAINTEXT", "Plaintext"),
                            ("SLACK", "Slack"),
                            ("SMS", "Sms"),
                            ("EMAIL", "Email"),
                            ("WEBPUSH", "Webpush"),
                        ]
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="bitcaster.channel",
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Assignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", concurrency.fields.IntegerVersionField(default=0, help_text="record revision number")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("validated", models.BooleanField(default=False)),
                ("active", models.BooleanField(default=True)),
                ("data", models.JSONField(blank=True, default=dict, null=True)),
                (
                    "address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="assignments", to="bitcaster.address"
                    ),
                ),
                (
                    "channel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="assignments", to="bitcaster.channel"
                    ),
                ),
            ],
            options={
                "verbose_name": "Assignment",
                "verbose_name_plural": "Assignments",
                "unique_together": {("address", "channel")},
            },
        ),
        migrations.CreateModel(
            name="DistributionList",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", concurrency.fields.IntegerVersionField(default=0, help_text="record revision number")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(db_collation="case_insensitive", max_length=255)),
                ("recipients", models.ManyToManyField(to="bitcaster.assignment")),
            ],
            options={
                "verbose_name": "Distribution List",
                "verbose_name_plural": "Distribution Lists",
            },
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("locked", models.BooleanField(default=False, help_text="Security lock of project")),
                ("version", concurrency.fields.IntegerVersionField(default=0, help_text="record revision number")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(blank=True, max_length=255)),
                ("description", models.CharField(blank=True, max_length=255, null=True)),
                ("active", models.BooleanField(default=True)),
                (
                    "newsletter",
                    models.BooleanField(default=False, help_text="Do not customise notifications per single user"),
                ),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="events", to="bitcaster.application"
                    ),
                ),
                ("channels", models.ManyToManyField(blank=True, to="bitcaster.channel")),
            ],
            options={
                "ordering": ("name",),
                "unique_together": {("name", "application"), ("slug", "application")},
            },
        ),
        migrations.CreateModel(
            name="LogMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", concurrency.fields.IntegerVersionField(default=0, help_text="record revision number")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("CRITICAL", "CRITICAL"),
                            ("FATAL", "FATAL"),
                            ("ERROR", "ERROR"),
                            ("WARN", "WARN"),
                            ("WARNING", "WARNING"),
                            ("INFO", "INFO"),
                            ("DEBUG", "DEBUG"),
                            ("NOTSET", "NOTSET"),
                        ],
                        max_length=255,
                    ),
                ),
                ("message", models.TextField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "application",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="bitcaster.application"),
                ),
            ],
            options={
                "verbose_name": "Log Message",
                "verbose_name_plural": "Log Messages",
            },
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", concurrency.fields.IntegerVersionField(default=0, help_text="record revision number")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
                ("payload_filter", models.TextField(blank=True, null=True)),
                ("extra_context", models.JSONField(blank=True, default=dict)),
                (
                    "environments",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(blank=True, max_length=20, null=True),
                        blank=True,
                        help_text="Environments available for project",
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "distribution",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="bitcaster.distributionlist",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to="bitcaster.event"
                    ),
                ),
            ],
            options={
                "verbose_name": "Notification",
                "verbose_name_plural": "Notifications",
            },
        ),
        migrations.CreateModel(
            name="Occurrence",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", concurrency.fields.IntegerVersionField(default=0, help_text="record revision number")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "timestamp",
                    models.DateTimeField(auto_now_add=True, help_text="Timestamp when occurrence has been created."),
                ),
                ("context", models.JSONField(blank=True, default=dict, help_text="Context provided by the sender")),
                (
                    "options",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Options provided by the sender to route linked notifications",
                    ),
                ),
                ("correlation_id", models.UUIDField(blank=True, default=uuid.uuid4, editable=False, null=True)),
                ("recipients", models.IntegerField(default=0, help_text="Total number of recipients")),
                (
                    "newsletter",
                    models.BooleanField(default=False, help_text="Do not customise notifications per single user"),
                ),
                (
                    "data",
                    models.JSONField(default=dict, help_text="Information about the processing (recipients, channels)"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("NEW", "New"), ("PROCESSED", "Processed"), ("FAILED", "Failed")], default="NEW"
                    ),
                ),
                ("attempts", models.IntegerField(default=5)),
                ("event", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="bitcaster.event")),
            ],
            options={
                "ordering": ("timestamp",),
            },
        ),
        migrations.CreateModel(
            name="Organization",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", concurrency.fields.IntegerVersionField(default=0, help_text="record revision number")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(blank=True, max_length=255)),
                (
                    "from_email",
                    models.EmailField(
                        blank=True, default="", help_text="default from address for emails", max_length=254
                    ),
                ),
                (
                    "subject_prefix",
                    models.CharField(
                        default="[Bitcaster] ",
                        help_text="Default prefix for messages supporting subject",
                        max_length=50,
                        verbose_name="Subject Prefix",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="organizations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Owner",
                    ),
                ),
            ],
            options={
                "verbose_name": "Organization",
                "verbose_name_plural": "Organizations",
                "ordering": ("name",),
            },
        ),
        migrations.AddField(
            model_name="channel",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s_set",
                to="bitcaster.organization",
            ),
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("locked", models.BooleanField(default=False, help_text="Security lock of project")),
                ("version", concurrency.fields.IntegerVersionField(default=0, help_text="record revision number")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(blank=True, max_length=255)),
                (
                    "from_email",
                    models.EmailField(
                        blank=True, default="", help_text="default from address for emails", max_length=254
                    ),
                ),
                (
                    "subject_prefix",
                    models.CharField(
                        default="[Bitcaster] ",
                        help_text="Default prefix for messages supporting subject",
                        max_length=50,
                        verbose_name="Subject Prefix",
                    ),
                ),
                (
                    "environments",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(blank=True, max_length=20, null=True),
                        blank=True,
                        help_text="Environments available for project",
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="projects",
                        to="bitcaster.organization",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Owner",
                    ),
                ),
            ],
            options={
                "verbose_name": "Project",
                "verbose_name_plural": "Projects",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", concurrency.fields.IntegerVersionField(default=0, help_text="record revision number")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, verbose_name="Name")),
                (
                    "subject",
                    models.TextField(
                        blank=True, help_text="The subject of the message", null=True, verbose_name="subject"
                    ),
                ),
                (
                    "content",
                    models.TextField(blank=True, help_text="The content of the message", verbose_name="content"),
                ),
                (
                    "html_content",
                    models.TextField(
                        blank=True, help_text="The HTML formatted content of the message", verbose_name="HTML Content"
                    ),
                ),
                (
                    "application",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_set",
                        to="bitcaster.application",
                    ),
                ),
                (
                    "channel",
                    models.ForeignKey(
                        help_text="Channel for which  the message is valid",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="bitcaster.channel",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        blank=True,
                        help_text="Event to which this message belongs",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="bitcaster.event",
                    ),
                ),
                (
                    "notification",
                    models.ForeignKey(
                        blank=True,
                        help_text="Notification to which this message belongs",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="bitcaster.notification",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_set",
                        to="bitcaster.organization",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_set",
                        to="bitcaster.project",
                    ),
                ),
            ],
            options={
                "verbose_name": "Message template",
                "verbose_name_plural": "Message templates",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="MediaFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", concurrency.fields.IntegerVersionField(default=0, help_text="record revision number")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(blank=True, max_length=255)),
                (
                    "image",
                    models.ImageField(
                        height_field="height",
                        storage=django.core.files.storage.FileSystemStorage(),
                        upload_to="",
                        width_field="width",
                    ),
                ),
                ("size", models.PositiveIntegerField(blank=True, default=0)),
                ("width", models.PositiveIntegerField(blank=True, default=0)),
                ("height", models.PositiveIntegerField(blank=True, default=0)),
                ("mime_type", models.CharField(blank=True, default="", max_length=100)),
                ("file_type", models.CharField(blank=True, default="", max_length=100)),
                (
                    "application",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_set",
                        to="bitcaster.application",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_set",
                        to="bitcaster.organization",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_set",
                        to="bitcaster.project",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="distributionlist",
            name="project",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="bitcaster.project"),
        ),
        migrations.AddField(
            model_name="channel",
            name="project",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s_set",
                to="bitcaster.project",
            ),
        ),
        migrations.AddField(
            model_name="application",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="applications", to="bitcaster.project"
            ),
        ),
        migrations.CreateModel(
            name="ApiKey",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", concurrency.fields.IntegerVersionField(default=0, help_text="record revision number")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(db_collation="case_insensitive", max_length=255, verbose_name="Name")),
                ("key", models.CharField(default=bitcaster.models.key.make_token, unique=True, verbose_name="Token")),
                (
                    "grants",
                    bitcaster.models.key.ChoiceArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("FULL_ACCESS", "Full Access"),
                                ("SYSTEM_PING", "Ping"),
                                ("APPLICATION_ADMIN", "Application Admin"),
                                ("EVENT_LIST", "Event list"),
                                ("EVENT_TRIGGER", "Event Trigger"),
                            ],
                            max_length=255,
                        ),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="keys", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "application",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_set",
                        to="bitcaster.application",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_set",
                        to="bitcaster.organization",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_set",
                        to="bitcaster.project",
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="UserRole",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", concurrency.fields.IntegerVersionField(default=0, help_text="record revision number")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="auth.group")),
                (
                    "organization",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="bitcaster.organization"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="roles", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "verbose_name": "User Role",
                "verbose_name_plural": "User Roles",
            },
        ),
        migrations.AddConstraint(
            model_name="notification",
            constraint=models.UniqueConstraint(fields=("event", "name"), name="notification_event_name"),
        ),
        migrations.AlterUniqueTogether(
            name="notification",
            unique_together={("event", "name")},
        ),
        migrations.AddConstraint(
            model_name="occurrence",
            constraint=models.UniqueConstraint(fields=("timestamp", "event"), name="occurrence_unique"),
        ),
        migrations.AddConstraint(
            model_name="organization",
            constraint=models.UniqueConstraint(fields=("slug",), name="org_slug_unique"),
        ),
        migrations.AddConstraint(
            model_name="organization",
            constraint=models.UniqueConstraint(fields=("slug", "owner"), name="owner_slug_unique"),
        ),
        migrations.AlterUniqueTogether(
            name="project",
            unique_together={("organization", "name"), ("organization", "slug")},
        ),
        migrations.AddConstraint(
            model_name="message",
            constraint=models.UniqueConstraint(
                fields=("organization", "project", "application", "name"), name="unique_message_org"
            ),
        ),
        migrations.AddConstraint(
            model_name="message",
            constraint=models.UniqueConstraint(fields=("organization", "project", "name"), name="unique_message_prj"),
        ),
        migrations.AddConstraint(
            model_name="message",
            constraint=models.UniqueConstraint(fields=("organization", "name"), name="unique_message_app"),
        ),
        migrations.AlterUniqueTogether(
            name="mediafile",
            unique_together={
                ("slug", "organization"),
                ("slug", "organization", "project"),
                ("slug", "organization", "project", "application"),
            },
        ),
        migrations.AlterUniqueTogether(
            name="distributionlist",
            unique_together={("name", "project")},
        ),
        migrations.AddConstraint(
            model_name="channel",
            constraint=models.UniqueConstraint(
                condition=models.Q(("project__isnull", True)),
                fields=("organization", "name"),
                name="bitcaster_channel_org_name",
            ),
        ),
        migrations.AddConstraint(
            model_name="channel",
            constraint=models.UniqueConstraint(
                fields=("organization", "project", "name"), name="bitcaster_channel_org_project_app_name"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="channel",
            unique_together={("organization", "name"), ("organization", "project", "name")},
        ),
        migrations.AlterUniqueTogether(
            name="application",
            unique_together={("project", "name"), ("project", "slug")},
        ),
        migrations.AlterUniqueTogether(
            name="apikey",
            unique_together={("name", "user")},
        ),
        migrations.AlterUniqueTogether(
            name="userrole",
            unique_together={("organization", "user", "group")},
        ),
    ]
