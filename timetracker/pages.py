import re
import logging
from datetime import date
from typing import Dict
from tzlocal import get_localzone

from requests import Session
from bs4 import BeautifulSoup
from dateparser import parse


BASE_URL = "https://timetracker.bairesdev.com"
logger = logging.getLogger(__name__)


class Page:
    def __init__(self, session: Session, content: str):
        self._session: Session = session
        self._content = content
        self._soup: BeautifulSoup = BeautifulSoup(content, "html.parser")

    @staticmethod
    def session() -> Session:
        session = Session()
        # session.verify = False
        session.headers.update(
            {
                "Host": "timetracker.bairesdev.com",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
                "Origin": "http://timetracker.bairesdev.com",
                "Referer": "http://timetracker.bairesdev.com/",
            }
        )
        return session

    def _hidden_value(self, name: str):
        element = self._soup.find("input", {"name": name})
        if not element:
            return ""
        return element.get("value", "")

    def _option_value(self, name: str, label: str) -> str:
        select = self._soup.find("select", {"name": name})
        if not select:
            raise ValueError(f'"{name}" is not available')
        options = select.findAll("option")
        available = {
            option.text: option.get("value") for option in options if option.text
        }
        if label not in available:
            raise KeyError(f'"{label}" not found in {set(available.keys())}')
        return available[label]


class NewTimeForm(Page):
    DATE_FIELD = "ctl00$ContentPlaceHolder$txtFrom"
    PROJECT_FIELD = "ctl00$ContentPlaceHolder$idProyectoDropDownList"
    HOURS_FIELD = "ctl00$ContentPlaceHolder$TiempoTextBox"
    CATEGORY_FIELD = (
        "ctl00$ContentPlaceHolder$idCategoriaTareaXCargoLaboralDropDownList"
    )
    TASK_FIELD = "ctl00$ContentPlaceHolder$idTareaXCargoLaboralDownList"
    COMMENT_FIELD = "ctl00$ContentPlaceHolder$CommentsTextBox"
    FOCAL_FIELD = "ctl00$ContentPlaceHolder$idFocalPointClientDropDownList"

    @staticmethod
    def _grab_secret(content: str, name: str) -> str:
        match = re.search(rf"hiddenField\|{name}\|([\w*/*\+*=*]*)", content)
        if match is None or not match.groups():
            return ""
        return match.groups()[0]

    def set_project(self, project: str):
        value = self._option_value(self.PROJECT_FIELD, project)
        args = {
            "ctl00$ContentPlaceHolder$ScriptManager": f"ctl00$ContentPlaceHolder$UpdatePanel1|{self.PROJECT_FIELD}",
            "__VIEWSTATE": self._hidden_value("__VIEWSTATE"),
            "__VIEWSTATEGENERATOR": self._hidden_value("__VIEWSTATEGENERATOR"),
            "__EVENTVALIDATION": self._hidden_value("__EVENTVALIDATION"),
            self.DATE_FIELD: date.today().strftime(r"%d/%m/%Y"),
            self.PROJECT_FIELD: value,
            self.HOURS_FIELD: "",
            self.CATEGORY_FIELD: "",
            self.TASK_FIELD: "",
            self.COMMENT_FIELD: "",
            self.FOCAL_FIELD: "",
            "__ASYNCPOST": "true",
        }
        response = self._session.post(f"{BASE_URL}/TimeTrackerAdd.aspx", data=args)
        response.raise_for_status()
        secrets = {
            name: self._grab_secret(response.content.decode(), name)
            for name in [
                "__EVENTTARGET",
                "__EVENTARGUMENT",
                "__LASTFOCUS",
                "__VIEWSTATE",
                "__VIEWSTATEGENERATOR",
                "__EVENTVALIDATION",
            ]
        }
        secrets[self.PROJECT_FIELD] = value
        return WithSecrets(self._session, self._content, secrets)


class WithSecrets(NewTimeForm):
    def __init__(self, session: Session, content: str, secrets: Dict):
        super().__init__(session, content)
        self._secrets = secrets

    def _grab_tasks(self, content: str) -> Dict[str, str]:
        _, interested = content.split(self.TASK_FIELD, maxsplit=2)
        interested, _ = interested.split(self.COMMENT_FIELD, maxsplit=2)
        options = re.findall(r'<option value="(.*)">(.*)</option>', interested)
        return {label: value for value, label in options}

    def _grab_focals(self, content: str) -> Dict[str, str]:
        _, interested = content.split(self.FOCAL_FIELD, maxsplit=2)
        options = re.findall(r'<option value="(.*)">(.*)</option>', interested)
        return {label: value for value, label in options}

    def set_task_category(self, category: str):
        value = self._option_value(self.CATEGORY_FIELD, category)
        args = {
            "ctl00$ContentPlaceHolder$ScriptManager": f"ctl00$ContentPlaceHolder$UpdatePanel1|{self.CATEGORY_FIELD}",
            self.DATE_FIELD: date.today().strftime(r"%d/%m/%Y"),
            self.HOURS_FIELD: "",
            self.CATEGORY_FIELD: value,
            self.TASK_FIELD: "",
            self.COMMENT_FIELD: "",
            self.FOCAL_FIELD: "",
            **self._secrets,
            "__ASYNCPOST": "true",
        }
        response = self._session.post(f"{BASE_URL}/TimeTrackerAdd.aspx", data=args)
        response.raise_for_status()
        secrets = {
            name: self._grab_secret(response.content.decode(), name)
            for name in [
                "__EVENTTARGET",
                "__EVENTARGUMENT",
                "__LASTFOCUS",
                "__VIEWSTATE",
                "__VIEWSTATEGENERATOR",
                "__EVENTVALIDATION",
            ]
        }
        return ReadyToLoad(
            self._session,
            self._content,
            {**self._secrets, **secrets, self.CATEGORY_FIELD: value},
            self._grab_tasks(response.content.decode()),
            self._grab_focals(response.content.decode()),
        )


class ReadyToLoad(WithSecrets):
    def __init__(
        self, session: Session, content: str, secrets: Dict, tasks: Dict, focals: Dict
    ):
        super().__init__(session, content, secrets)
        self._secrets = secrets
        self._tasks = tasks
        self._focals = focals

    def load(
        self,
        *,
        date: str,
        task: str,
        hours: str,
        comment: str,
        focal: str,
    ):
        logger.info("loading...")
        parsed_date = parse(
            date,
            date_formats=[r"%d/%m/%Y"],
            settings={"TIMEZONE": get_localzone().zone},
        )
        logger.info("date: %s", parsed_date)
        if not parsed_date:
            raise ValueError(f'"{date}" is an invalid date literal')
        if task not in self._tasks:
            raise ValueError(f'"{task}" not found in: {list(self._tasks.keys())}')
        if focal not in self._focals:
            raise ValueError(f'"{focal}" not found in: {list(self._focals.keys())}')
        parsed_hours = float(hours)
        args = {
            self.DATE_FIELD: parsed_date.strftime(r"%d/%m/%Y"),
            self.HOURS_FIELD: f"{parsed_hours:0.2f}",
            self.TASK_FIELD: self._tasks[task],
            self.COMMENT_FIELD: comment,
            self.FOCAL_FIELD: self._focals[focal],
            "ctl00$ContentPlaceHolder$btnAceptar": "Accept",
            **self._secrets,
        }
        response = self._session.post(f"{BASE_URL}/TimeTrackerAdd.aspx", data=args)
        response.raise_for_status()
        return self


class ListPage(Page):
    def new_loader(self):
        response = self._session.get(f"{BASE_URL}/TimeTrackerAdd.aspx")
        response.raise_for_status()
        return NewTimeForm(self._session, response.content.decode())

    def ready(
        self,
        *,
        project,
        category,
    ):
        return self.new_loader().set_project(project).set_task_category(category)


class LoginPage(Page):
    @classmethod
    def visit(cls, session: Session):
        content = session.get(BASE_URL).content.decode()
        return cls(session, content)

    def login(self, username, password):
        args = {
            "ctl00$ContentPlaceHolder$UserNameTextBox": username,
            "ctl00$ContentPlaceHolder$PasswordTextBox": password,
            "ctl00$ContentPlaceHolder$LoginButton": "Login",
            "__VIEWSTATE": self._hidden_value("__VIEWSTATE"),
            "__VIEWSTATEGENERATOR": self._hidden_value("__VIEWSTATEGENERATOR"),
            "__EVENTVALIDATION": self._hidden_value("__EVENTVALIDATION"),
        }
        response = self._session.post(BASE_URL, data=args)
        response.raise_for_status()
        return ListPage(self._session, response.content.decode())


class TimeTrackerPage:
    @staticmethod
    def start() -> LoginPage:
        return LoginPage.visit(LoginPage.session())
