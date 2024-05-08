from typing import Dict, List, Optional

from main.error_messages import ErrorMessages


class ResponseFormatViewMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._errors: List[Dict[str, str]] = []

    def _add_message(
        self, message_list, code: str, text: str, details: Optional[str] = None
    ) -> None:
        message_list.append({"code": code, "text": text, "details": details})

    def add_error(self, error: ErrorMessages, details: Optional[str] = None) -> None:
        self._add_message(
            message_list=self._errors,
            code=error.name,
            text=error.value,
            details=details,
        )

    def add_custom_error(
        self, code: str, text: str, details: Optional[str] = None
    ) -> None:
        self._add_message(
            message_list=self._errors, code=code, text=text, details=details
        )

    def get_errors(self) -> List[Dict[str, str]]:
        return self._errors
