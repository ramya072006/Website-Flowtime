"""Tasks Page Object — FlowTime /tasks route."""

from selenium.webdriver.common.by import By
from .base_page import BasePage
from automation.config import routes


class TasksPage(BasePage):
    """Page Object for the Tasks management page."""

    PAGE_HEADING    = (By.XPATH, '//*[contains(text(),"Task") or contains(text(),"task")]')
    ADD_TASK_BTN    = (By.XPATH, '//button[contains(text(),"Add") or contains(text(),"New") or contains(text(),"Create") or contains(@aria-label,"add")]')
    TASK_LIST       = (By.CSS_SELECTOR, '[class*="task-list"], [class*="tasklist"], ul[class*="task"], [class*="task-item"]')
    TASK_ITEMS      = (By.CSS_SELECTOR, '[class*="task-item"], [class*="task-card"], li[class*="task"]')
    SEARCH_INPUT    = (By.CSS_SELECTOR, 'input[placeholder*="Search"], input[placeholder*="search"]')
    FILTER_BTN      = (By.XPATH, '//button[contains(text(),"Filter") or contains(@aria-label,"filter")]')
    SORT_BTN        = (By.XPATH, '//button[contains(text(),"Sort")]')
    EMPTY_STATE     = (By.XPATH, '//*[contains(text(),"No tasks") or contains(text(),"empty")]')
    TASK_DIALOG     = (By.CSS_SELECTOR, '[role="dialog"], [class*="modal"]')
    TASK_TITLE_INPUT = (By.CSS_SELECTOR, '[placeholder*="title"], [placeholder*="Title"], input[id*="title"]')
    SAVE_BTN        = (By.XPATH, '//button[contains(text(),"Save") or contains(text(),"Create")]')
    CANCEL_BTN      = (By.XPATH, '//button[contains(text(),"Cancel")]')
    DELETE_BTN      = (By.XPATH, '//button[contains(text(),"Delete") or contains(@aria-label,"delete")]')
    COMPLETE_BTN    = (By.CSS_SELECTOR, '[type="checkbox"], button[aria-label*="complete"]')
    PRIORITY_SELECT = (By.CSS_SELECTOR, 'select[name*="priority"], button[id*="priority"]')

    def open(self):
        self.navigate_to(routes.TASKS)
        return self

    def click_add_task(self):
        self.click(self.ADD_TASK_BTN)
        return self

    def is_task_dialog_open(self) -> bool:
        return self.is_present(self.TASK_DIALOG, 5)

    def enter_task_title(self, title: str):
        self.type(self.TASK_TITLE_INPUT, title)
        return self

    def click_save(self):
        self.click(self.SAVE_BTN)
        return self

    def click_cancel(self):
        self.click(self.CANCEL_BTN)
        return self

    def search_tasks(self, query: str):
        self.type(self.SEARCH_INPUT, query)
        return self

    def get_task_count(self) -> int:
        try:
            return len(self.find_all(self.TASK_ITEMS))
        except Exception:
            return 0

    def is_empty_state_shown(self) -> bool:
        return self.is_present(self.EMPTY_STATE, 5)

    def is_page_loaded(self) -> bool:
        return (self.is_displayed(self.PAGE_HEADING, 10) or
                self.is_displayed(self.ADD_TASK_BTN, 10))
