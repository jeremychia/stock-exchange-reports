from sg import get_sg_sgx_announcements, update_sg_sgx_announcements


def download_announcements():

    # SG
    (
        announcement_list,
        announcement_detail_list,
        announcement_attachment_list,
    ) = get_sg_sgx_announcements()
    update_sg_sgx_announcements(
        announcement_list, announcement_detail_list, announcement_attachment_list
    )
