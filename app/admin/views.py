from aiohttp.web_exceptions import HTTPForbidden, HTTPUnauthorized
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import new_session

from app.admin.schemes import AdminSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @docs(tags=['admin'], summary='Login admin', description='Login admin if exists')
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        email = self.data['email']
        password = self.data['password']
        admin = await self.store.admins.get_by_email(email)
        if not admin or not admin.is_password_valid(password):
            raise HTTPForbidden
        admin_data = AdminSchema().dump(admin)
        response = json_response(data=admin_data)
        session = await new_session(request=self.request)
        session['admin'] = admin_data
        return response


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(tags=['admin'], summary='Get admin', description='Get current session admin')
    @response_schema(AdminSchema, 200)
    async def get(self):
        if self.request.admin:
            return json_response(data=AdminSchema().dump(self.request.admin))
        raise HTTPUnauthorized
