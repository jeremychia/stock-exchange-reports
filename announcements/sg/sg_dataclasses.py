from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Any


@dataclass
class Announcement:
    document_date: str
    security_name: str
    company_name: str
    id: str
    title: str
    url: str

    @classmethod
    def from_api_data(cls, api_data):
        document_date = cls._convert_document_date(api_data["documentDate"])
        return cls(
            document_date=document_date,
            security_name=api_data["securityName"],
            company_name=api_data["companyName"],
            id=api_data["id"],
            title=api_data["title"],
            url=api_data["url"],
        )

    @staticmethod
    def _convert_document_date(timestamp):
        date_obj = datetime.fromtimestamp(timestamp / 1000)
        return date_obj


@dataclass
class AnnouncementAttachments:
    attachment_name: str
    attachment_link: str

    def __post_init__(self):
        self.attachment_link = self._parse_attachment_link()

    def _parse_attachment_link(self) -> str:
        url_prefix = "https://links.sgx.com"
        return url_prefix + self.attachment_link

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnnouncementDetails:
    announcement_id: str = None
    url: str = None
    issuer: str = None
    securities: str = None
    is_stapled_security: str = None
    announcement_title: str = None
    broadcast_at: str = None
    status: str = None
    report_type: str = None
    announcement_reference: str = None
    submitted_by_name: str = None
    submitted_by_designation: str = None
    announcement_description: str = None
    financial_period_end: str = None
    attachments: List[AnnouncementAttachments] = field(default_factory=list)

    def __post_init__(self):
        self.broadcast_at = self._parse_broadcast_at()
        self.financial_period_end = self._parse_financial_period_end()

    def _parse_broadcast_at(self) -> datetime:
        date_time_format = "%d-%b-%Y %H:%M:%S"
        local_time = datetime.strptime(self.broadcast_at, date_time_format)
        utc_time = local_time - timedelta(hours=8)  # Adjusting from GMT+8 to UTC
        return utc_time

    def _parse_financial_period_end(self) -> datetime:
        date_formats = ["%d/%m/%Y", "%d-%b-%Y", "%m/%d/%Y"]
        for date_format in date_formats:
            try:
                return datetime.strptime(self.financial_period_end, date_format).date()
            except ValueError:
                continue
        raise ValueError(
            f"Date format for {self.financial_period_end} is not supported."
        )

    @classmethod
    def from_parsed_data(cls, parsed_data: Dict[str, Any]) -> "AnnouncementDetails":
        attachments_data = parsed_data.pop("attachments", [])
        attachments = [
            AnnouncementAttachments(**attachment_data)
            for attachment_data in attachments_data
        ]
        parsed_data["attachments"] = attachments
        return cls(**parsed_data)

    # removes attachments
    def announcement_details_to_dict(self):
        data = asdict(self)
        data.pop("attachments", None)
        return data

    # there can be more than one attachment per announcement detail
    def attachments_to_dict_list(self):
        attachments_dict = []
        for attachment in self.attachments:
            data = attachment.to_dict()
            data["announcement_reference"] = self.announcement_reference
            data["url"] = self.url
            attachments_dict.append(data)
        return attachments_dict
