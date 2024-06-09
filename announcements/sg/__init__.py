import pandas as pd
import pandas_gbq

from sg_dataclasses import Announcement, AnnouncementDetails
from sg_sgx_announcements import SGXAnnouncements, ParseAnnouncementDetails


def get_sg_sgx_announcements():

    sgx_data_fetcher = SGXAnnouncements()
    sgx_data_fetcher.fetch_data()

    announcement_list = []
    announcement_detail_list = []
    announcement_attachment_list = []

    for result in sgx_data_fetcher.results:

        # announcement information, which has links to the details
        announcement = Announcement.from_api_data(result)

        # announcement detail information
        announcement_detail_data = ParseAnnouncementDetails(announcement.url).parse()
        announcement_details = AnnouncementDetails.from_parsed_data(
            announcement_detail_data
        )

        # append information
        announcement_list.append(announcement.__dict__)
        announcement_detail_list.append(
            announcement_details.announcement_details_to_dict()
        )
        announcement_attachment_list.extend(
            announcement_details.attachments_to_dict_list()
        )

    return announcement_list, announcement_detail_list, announcement_attachment_list


def update_sg_sgx_announcements(
    announcement_list, announcement_detail_list, announcement_attachment_list
):

    print(f"Adding {len(announcement_list)} rows to sg_sgx.announcements")
    pandas_gbq.to_gbq(
        dataframe=pd.DataFrame(announcement_list),
        destination_table="sg_sgx.announcements",
        project_id="stock-exchange-reports",
        if_exists="append",
    )

    print(f"Adding {len(announcement_detail_list)} rows to sg_sgx.announcement_details")
    df = pd.DataFrame(announcement_detail_list)
    df["financial_period_end"] = df["financial_period_end"].astype("str")

    pandas_gbq.to_gbq(
        dataframe=df,
        destination_table="sg_sgx.announcement_details",
        project_id="stock-exchange-reports",
        if_exists="append",
    )

    print(
        f"Adding {len(announcement_attachment_list)} rows to sg_sgx.announcement_attachments"
    )
    pandas_gbq.to_gbq(
        dataframe=pd.DataFrame(announcement_attachment_list),
        destination_table="sg_sgx.announcement_attachments",
        project_id="stock-exchange-reports",
        if_exists="append",
    )

    return 0
