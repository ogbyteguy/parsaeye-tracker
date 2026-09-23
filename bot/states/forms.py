from aiogram.fsm.state import State, StatesGroup


class AddActivity(StatesGroup):
    name = State()
    description = State()
    category = State()


class LogActivity(StatesGroup):
    select = State()
    duration = State()
    notes = State()
    feeling = State()


class AdHocActivity(StatesGroup):
    name = State()
    duration = State()
    notes = State()


class DailyPlan(StatesGroup):
    content = State()


class JournalForm(StatesGroup):
    good_things = State()
    bad_things = State()
    learned = State()
    time_wasters = State()
    free_note = State()
    mood = State()


class ExpenseForm(StatesGroup):
    amount = State()
    category = State()
    description = State()
    feeling = State()


class CommitmentForm(StatesGroup):
    title = State()
    amount = State()
    due_date = State()
    type_ = State()


class StudyLog(StatesGroup):
    subject = State()
    book = State()
    pages = State()
    duration = State()
    summary = State()


class HabitForm(StatesGroup):
    name = State()
    emoji = State()


class UserScore(StatesGroup):
    score = State()


class AdminBroadcast(StatesGroup):
    message = State()
