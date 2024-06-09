from bs4 import BeautifulSoup

import requests


class SGXAnnouncements:
    def __init__(
        self, api_url="https://api.sgx.com/financialreports/v1.0", page_size=2000
    ):
        self.api_url = api_url
        self.params = {
            "pagestart": 0,
            "pagesize": page_size,
            "params": "id,companyName,documentDate,securityName,title,url",
        }
        self.results = []
        self.meta = None

    def fetch_data(self):
        while True:
            print(f"pagestart = {self.params['pagestart']}")
            response = requests.get(self.api_url, params=self.params)
            data = response.json()

            if data["data"]:
                self.results.extend(data["data"])
                self.params["pagestart"] += 1
                print(
                    f"Wrote {len(data['data'])} records. Current size of results: {len(self.results)}"
                )
            else:
                break

            if not self.meta:
                self.meta = data["meta"]

        print(
            f"Check meta['totalItems'] == len(results): {self.meta['totalItems']} == {len(self.results)}: {self.meta['totalItems']==len(self.results)}"
        )


class ParseAnnouncementDetails:
    def __init__(self, url):
        self.url = url
        self.soup = self._fetch_and_parse_url(url)
        self.data = {"url": url}

        self.tag_mappings = {
            "Issuer & Securities": {
                "issuer": "Issuer/ Manager",
                "securities": "Securities",
                "is_stapled_security": "Stapled Security",
            },
            "Announcement Details": {
                "announcement_title": "Announcement Title ",
                "broadcast_at": "Date &Time of Broadcast ",
                "status": "Status ",
                "report_type": "Report Type",
                "announcement_reference": "Announcement Reference",
                "submitted_by_name": "Submitted By (Co./ Ind. Name)",
                "submitted_by_designation": "Designation",
                "announcement_description": "Description (Please provide a detailed description of the event in the box below - Refer to the Online help for the format)",
            },
            "Additional Details": {"financial_period_end": "Period Ended"},
        }

    @classmethod
    def _fetch_and_parse_url(self, url):
        response = requests.get(url)
        response.raise_for_status()

        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        return soup

    def _find_section(self, section_name):
        return (
            self.soup.find("h2", string=section_name).find_next_sibling("div")
            if self.soup.find("h2", string=section_name)
            else None
        )

    def _extract_data_from_section(self, section, tag_map):
        extracted_data = {}
        if section:
            for key, tag_name in tag_map.items():
                tag = section.find("dt", string=tag_name)
                if tag:
                    sibling = tag.find_next_sibling("dd")
                    if sibling:
                        extracted_data[key] = sibling.text.strip()
        return extracted_data

    def _parse_attachments_section(self, attachments_section):
        attachment_data = {}
        if attachments_section:
            attachment_list = attachments_section.find_all(
                "a", class_="announcement-attachment"
            )
            if attachment_list:
                attachments = []
                for attachment in attachment_list:
                    attachment_info = {
                        "attachment_name": attachment.text.strip(),
                        "attachment_link": attachment["href"],
                    }
                    attachments.append(attachment_info)
                attachment_data["attachments"] = attachments
        return attachment_data

    def parse(self):
        for section_name, tag_map in self.tag_mappings.items():
            section = self._find_section(section_name)
            self.data.update(self._extract_data_from_section(section, tag_map))

        attachments_section = self._find_section("Attachments")
        self.data.update(self._parse_attachments_section(attachments_section))

        return self.data
