import requests
import base64
from config.config import settings

API_URL = settings.API_URL
API_KEY = settings.API_KEY


class HashtopolisUserApi:

    @staticmethod
    def _request(data):
        """
        Return response
        :param data: API data
        :return: None or response.json()
        """
        try:
            response = requests.post(API_URL, json=data)
        except (requests.RequestException, requests.ConnectionError, requests.HTTPError, requests.URLRequired) as err:
            print(err)
            return None
        if response.json().get('response') == 'ERROR':
            print(response.json().get('message'))
            return None
        return response.json()

    def set_active(self, agent_id: int, active: bool):
        """
        Set active or inactive agent
        :param agent_id: agent id
        :param active: True or False
        :return: response or None
        response example:
        {'section': 'agent', 'request': 'setActive', 'response': 'OK'}
        """
        data = {
            "section": "agent",
            "request": "setActive",
            "active": active,
            "agentId": agent_id,
            "accessKey": API_KEY
        }
        return self._request(data)

    def task_info(self, task_id):
        """
        Return task info
        :param task_id: task id
        :return: response or None
        response example:
        {'section': 'task', 'request': 'getTask', 'response': 'OK', 'taskId': 33119, 'name': '4_ulm_001_my.rule',
        'attack': '#HL# 4_ULM_001.txt -r my.rule -w3', 'chunksize': 600, 'color': '', 'benchmarkType': 'speed',
        'statusTimer': 5, 'priority': 0, 'isCpuOnly': False, 'isSmall': False, 'skipKeyspace': 0, 'keyspace': 1868227,
        'dispatched': 1868227, 'hashlistId': 4334, 'imageUrl': 'http://45.12.19.80/api/taskimg.php?task=33119',
        'usePreprocessor': False, 'preprocessorId': 0, 'preprocessorCommand': '',
        'files': [{'fileId': 4, 'filename': '4_ULM_001.txt', 'size': 18237746},
        {'fileId': 11, 'filename': 'my.rule', 'size': 42}],
        'speed': 0, 'searched': 1868227, 'chunkIds': [50830], 'agents': [], 'isComplete': True, 'workPossible': True}
        """
        data = {
            "section": "task",
            "request": "getTask",
            "taskId": task_id,
            "accessKey": API_KEY
        }
        return self._request(data)

    def create_hash_list(self, hash_list_name, is_salted: bool, format: int, hash_type: int, hashes):
        """
        Create hash list
        :param hash_list_name: hash list name
        :param is_salted: Is salted: True or False
        :param format: Format hash: 0 or 1
        :param hash_type: Hash type
        :param hashes: Hashes
        :return: response or None
        response example:
        {"section": "hashlist",
        "request": "createHashlist",
        "response": "OK",
        "hashlistId": 101}
        """
        hashes = base64.b64encode(hashes)
        hashes = hashes.decode('UTF-8')
        data = {
            "section": "hashlist",
            "request": "createHashlist",
            "name": hash_list_name,
            "isSalted": is_salted,
            "isSecret": True,
            "isHexSalt": False,
            "separator": ":",
            "format": format,
            "hashtypeId": hash_type,
            "accessGroupId": 1,
            "data": hashes,
            "useBrain": False,
            "brainFeatures": 0,
            "accessKey": API_KEY
        }
        return self._request(data)

    def run_super_task(self, hash_list_id, super_task_id):
        """
        Create a super task out of a configured preconfigured task collection
        :param hash_list_id: hash list id
        :param super_task_id: super task id
        :return: response or None
        response example:
        {"section": "task",
        "request": "runSupertask",
        "response": "OK"}
        """
        data = {
            "section": "task",
            "request": "runSupertask",
            "hashlistId": hash_list_id,
            "supertaskId": super_task_id,
            "crackerVersionId": 1,
            "accessKey": API_KEY,
        }
        return self._request(data)

    def set_supertask_priority(self, super_task_id, super_task_priority):
        """
        Set the priority for a supertask.
        :param super_task_id: super task id
        :param super_task_priority: super task priority
        :return: response or None
        response example:
        {"section": "task",
        "request": "setSupertaskPriority",
        "response": "OK"}
        """
        data = {
            "section": "task",
            "request": "setSupertaskPriority",
            "supertaskId": super_task_id,
            "supertaskPriority": super_task_priority,
            "accessKey": API_KEY
        }
        return self._request(data)
