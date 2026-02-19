from starlette_admin.contrib.sqla import Admin, ModelView

from infra.database import db_helper
from infra.models import (
    UserModel,
    AccountModel,
    HistoryModel,
    GoalModel,
)

admin = Admin(engine=db_helper.engine)

admin.add_view(ModelView(UserModel))
admin.add_view(ModelView(AccountModel))
admin.add_view(ModelView(HistoryModel))
admin.add_view(ModelView(GoalModel))
