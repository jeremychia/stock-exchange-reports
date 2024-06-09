import os

from announcements import download_announcements

# Set the environment variables for Google Cloud authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./token/gcp_token.json"
os.environ["GOOGLE_CLOUD_PROJECT"] = "stock-exchange-reports"


def run():
    try:
        download_announcements()
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    run()
