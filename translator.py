import requests


class Translator:
    def __init__(self, iam_token: str, folder_id: str) -> None:
        self.__IAM_TOKEN = iam_token
        self.__folder_id = folder_id
        self.__target_language = 'en'

    def translate(self, text_to_translate: str) -> str:
        body = {
            "targetLanguageCode": self.__target_language,
            "texts": text_to_translate,
            "folderId": self.__folder_id,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {0}".format(self.__IAM_TOKEN)
        }

        response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
                                 json=body,
                                 headers=headers)

        return response.json()['translations'][0]['text']


class YandexHelper:
    def __init__(self, ya_auth_token: str) -> None:
        self.__token = ya_auth_token

    def get_IAM_TOKEN(self):
        body = {"yandexPassportOauthToken": f"{self.__token}"}
        response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', json=body)
        return response.json()['iamToken']
