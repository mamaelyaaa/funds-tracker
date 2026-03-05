from starlette_admin.contrib.sqla import Admin, ModelView

from infra.database import db_helper
from infra.models import (
    UserModel,
    AccountModel,
    HistoryModel,
    GoalModel,
)

admin = Admin(engine=db_helper.engine)


class BaseAppModelView(ModelView):
    fields_default_sort = [("created_at", True)]
    exclude_fields_from_edit = ["created_at", "updated_at"]
    exclude_fields_from_create = ["created_at", "updated_at"]


class UserView(BaseAppModelView):
    fields = [
        "id",
        "name",
        "created_at",
        "accounts",
        "goals",
    ]

    sortable_fields = ["name", "created_at"]
    exclude_fields_from_create = ["created_at", "accounts", "goals"]


class AccountView(BaseAppModelView):
    fields = [
        "id",
        "user",
        "name",
        "balance",
        "currency",
        "created_at",
        "updated_at",
    ]
    sortable_fields = ["user", "created_at", "updated_at"]


class HistoryView(BaseAppModelView):
    fields = [
        "id",
        "account",
        "balance",
        "delta",
        "is_monthly_closing",
        "created_at",
    ]
    sortable_fields = ["account", "created_at", "updated_at"]


class GoalView(BaseAppModelView):
    fields = [
        "id",
        "user",
        "title",
        "current_amount",
        "target_amount",
        "status",
        "deadline",
        "created_at",
    ]
    sortable_fields = ["user", "status", "created_at", "updated_at"]


admin.add_view(UserView(UserModel))
admin.add_view(AccountView(AccountModel))
admin.add_view(HistoryView(HistoryModel))
admin.add_view(GoalView(GoalModel))
