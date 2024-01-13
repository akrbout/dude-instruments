from parsel import Selector
from enum import Enum


class SelectorsType(Enum):
    xpath = "xpath"
    css = "css"


class OneTimeSpider:
    _target: dict
    _selectors_type: SelectorsType
    result: dict

    def __init__(
        self,
        target: dict,
        page_content: str,
        selectors_type: SelectorsType = SelectorsType.xpath,
    ):
        self._selectors_type = selectors_type
        selector = Selector(text=page_content)
        self.result = self.parse_target(selector=selector, target=target)

    def _parse_field(self, field_type: str, field_selector: str, selector: Selector):
        match field_type:
            case "array":
                return (
                    selector.xpath(field_selector).getall()
                    if self._selectors_type == SelectorsType.xpath
                    else selector.css(field_selector).getall()
                )
            case "string":
                return (
                    selector.xpath(field_selector).get()
                    if self._selectors_type == SelectorsType.xpath
                    else selector.css(field_selector).get()
                )

    def parse_target(self, selector: Selector, target: dict | list) -> dict:
        result = {}
        for field in target:
            value = target[field]
            if isinstance(value, dict):
                parent_object: str | None = value.get("_parent_object", None)
                if not parent_object:
                    raise Exception(f"'_parent_object' field is required for included item '{field}'")
                value.pop("_parent_object")
                parent_selector = (
                    selector.xpath(parent_object)
                    if self._selectors_type == SelectorsType.xpath
                    else selector.css(parent_object)
                )
                result[field]: list[dict] = []
                for obj in parent_selector:
                    parsed_object = self.parse_target(selector=obj, target=value)
                    result[field].append(parsed_object)
            if isinstance(value, list):
                parsed_field = self._parse_field(
                    field_type=value[1],
                    field_selector=value[0],
                    selector=selector,
                )
                result[field] = parsed_field
        return result
