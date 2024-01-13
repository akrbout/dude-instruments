from parsel import Selector
from enum import Enum


class SelectorsType(Enum):
    xpath = "xpath"
    css = "css"


class OneTimeSpider:
    _target: dict
    _selectors_type: SelectorsType
    _global_selector: Selector
    results: list[dict]
    is_unzipped: bool

    def __init__(
        self,
        target: dict,
        page_content: str,
        selectors_type: SelectorsType = SelectorsType.xpath,
    ):
        self.results = [{}]
        self._selectors_type = selectors_type
        self._target = target
        self.parse_target(page_content)

    def _parse_field(self, field_selector: str) -> list[str]:
        match self._selectors_type:
            case SelectorsType.xpath:
                return self._global_selector.xpath(field_selector).getall()
            case SelectorsType.css:
                return self._global_selector.css(field_selector).getall()

    def _try_unzip_results(self) -> bool:
        result_lens = set(len(self.results[0][field]) for field in self.results[0])
        if len(result_lens) > 1:
            return False
        results_obj = self.results.pop(0)
        res = []
        for i in range(result_lens.pop()):
            keys = results_obj.keys()
            obj = {k: results_obj[k][i] for k in keys}
            res.append(obj)
        self.results = res
        return True
        # for field in results_obj:
        #     for y, item in enumerate(results_obj[field]):
        #         self.results.insert(y, {field: item})
        # return True

    def parse_target(self, page_content: str) -> None:
        self._global_selector = Selector(text=page_content)
        for field in self._target:
            parsed_field = self._parse_field(self._target[field])
            self.results[0][field] = parsed_field
        self.is_unzipped = self._try_unzip_results()
