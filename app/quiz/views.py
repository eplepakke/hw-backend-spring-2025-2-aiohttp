from aiohttp.web_exceptions import HTTPConflict, HTTPNotFound, HTTPBadRequest
from aiohttp_apispec import docs, request_schema, response_schema, querystring_schema

from app.quiz.models import Answer
from app.quiz.schemes import ThemeSchema, ThemeListSchema, QuestionSchema, ListQuestionSchema, ThemeIdSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @docs(tags=['Theme'], summary='Add theme', description='Add theme to database')
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema, 200)
    async def post(self):
        title = self.data['title']
        if await self.store.quizzes.get_theme_by_title(title):
            raise HTTPConflict
        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    @docs(tags=['Theme'], summary='List of themes', description='List of themes from database')
    @response_schema(ThemeListSchema, 200)
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response(data=ThemeListSchema().dump({"themes": themes}))


class QuestionAddView(AuthRequiredMixin, View):
    @docs(tags=['Question'], summary='Add question', description='Add question to database')
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema, 200)
    async def post(self):
        title = self.data['title']
        existing_question = await self.store.quizzes.get_question_by_title(title)
        if existing_question:
            raise HTTPConflict

        theme_id = self.data['theme_id']
        existing_theme = await self.store.quizzes.get_theme_by_id(id_=theme_id)
        if not existing_theme:
            raise HTTPNotFound

        answers = self.data['answers']
        if len(answers) < 2:
            raise HTTPBadRequest

        parsed_answers = []
        correct_answers = []
        for answer in answers:
            answer = Answer(title=answer['title'], is_correct=answer['is_correct'])
            if answer.is_correct and True in correct_answers:
                raise HTTPBadRequest
            correct_answers.append(answer.is_correct)
            parsed_answers.append(answer)

        if not any(correct_answers):
            raise HTTPBadRequest

        question = await self.store.quizzes.create_question(
            title=title,
            theme_id=theme_id,
            answers=parsed_answers,
        )

        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @docs(tags=['Question'], summary='List questions', description='List of questions from database by id (if needed)')
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        questions = await self.store.quizzes.list_questions(
            theme_id=self.data.get("theme_id")
        )
        return json_response(
            data=ListQuestionSchema().dump(
                {
                    "questions": questions,
                }
            )
        )
