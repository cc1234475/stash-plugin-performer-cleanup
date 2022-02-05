import os
import sys
import json

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import log

dir_path = os.path.dirname(os.path.realpath(__file__))


def main():
    input = None

    if len(sys.argv) < 2:
        input =json.loads(sys.stdin.read())
        log.LogDebug("Raw input: %s" % json.dumps(input))
    else:
        log.LogDebug("Using command line inputs")
        mode = sys.argv[1]
        log.LogDebug("Command line inputs: {}".format(sys.argv[1:]))

        input = {}
        input["args"] = {"mode": mode}
        input["server_connection"] = {"Scheme": "http", "Port": 9999}

    output = {}
    run(input, output)

    out = json.dumps(output)
    print(out + "\n")


def run(input, output):
    modeArg = input["args"]["mode"]
    try:
        if modeArg == "" or modeArg == "cleanup":
            client = StashInterface(input["server_connection"])
            cleanupPerformers(client)
    except Exception as e:
        raise

    output["output"] = "ok"


def cleanupPerformers(client):
    for i in range(0, 200):
        q = """{
    findScenes(scene_filter: {organized: false}, filter: {per_page: 250, page: %s}){
        scenes{
            id
            performers{
                id
                name
            }
        }
    }
}
    """ % i
        data = client._callGraphQL(q)
        if not data['findScenes']['scenes']:
            break

        for scene in data['findScenes']['scenes']:
            performers = scene['performers']
            to_remove = []
            for p in performers:
                for n in performers:
                    if p['name'].lower() != n['name'].lower() and p['name'].lower() in n['name'].lower():
                        to_remove.append(p['id'])

            if to_remove:
                print([p['id'] for p in performers if p['id'] not in to_remove])
                client.update_scene({'id': scene['id'], 'performer_ids': [p['id'] for p in performers if p['id'] not in to_remove]})


mutate_scene_query= """mutation sceneUpdate($input: SceneUpdateInput!){
  sceneUpdate(input: $input){
    id
  }
}"""


class StashInterface:
    port = ""
    url = ""
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Connection": "keep-alive",
        "DNT": "1",
    }

    def __init__(self, conn):
        self._conn = conn
        self.ignore_ssl_warnings = True
        self.server = conn["Scheme"] + "://localhost:" + str(conn["Port"])
        self.url = self.server + "/graphql"
        self.auth_token = None
        if "SessionCookie" in self._conn:
            self.auth_token = self._conn["SessionCookie"]["Value"]

    def _callGraphQL(self, query, variables=None):
        json = {}
        json["query"] = query
        if variables != None:
            json["variables"] = variables

        if self.auth_token:
            response = requests.post(
                self.url,
                json=json,
                headers=self.headers,
                cookies={"session": self.auth_token},
                verify=not self.ignore_ssl_warnings,
            )
        else:
            response = requests.post(
                self.url,
                json=json,
                headers=self.headers,
                verify=not self.ignore_ssl_warnings,
            )

        log.LogInfo(str(response.status_code))

        if response.status_code == 200:
            result = response.json()
            log.LogInfo(str(result))
            if result.get("error", None):
                for error in result["error"]["errors"]:
                    raise Exception("GraphQL error: {}".format(error))
            if result.get("data", None):
                return result.get("data")
        else:
            raise Exception(
                "GraphQL query failed:{} - {}. Query: {}. Variables: {}".format(
                    response.status_code, response.content, query, variables
                )
            )

    def update_scene(self, data):
        return  self._callGraphQL(mutate_scene_query, {"input": data})


main()
