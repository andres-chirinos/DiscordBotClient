import requests, json, pymongo, quart, datetime


class RoleConnection:
    def __init__(
        self,
        app: quart.Quart = None,
        Memoria: pymongo.MongoClient = None,
        client_id=None,
        bot_token: str = None, 
        client_secret: str = None,
        metadata_set: list = None,
        *args,
        **kwargs,
    ):
        self.client_id = client_id or app.config["DISCORD_CLIENT_ID"]
        self.client_secret = client_secret or app.config["DISCORD_CLIENT_SECRET"]
        self.bot_token = bot_token or app.config["DISCORD_BOT_TOKEN"]
        self.collection = Memoria.get_database("master").get_collection("users")
        self.metadata_set = json.loads(metadata_set or app.config["METADATA_SET"])
        super().__init__(*args, **kwargs)

    async def set_role_connection(self, body: list):
        # supported types: number_lt=1, number_gt=2, number_eq=3 number_neq=4, datetime_lt=5, datetime_gt=6, boolean_eq=7, boolean_neq=8
        # You can read more here https://discord.com/developers/docs/resources/application-role-connection-metadata
        url = f"""https://discord.com/api/v10/applications/{self.client_id}/role-connections/metadata"""
        response = requests.put(
            url,
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"""Bot {self.bot_token}""",
            },
        )
        if response.ok:
            return response.json()
        else:
            raise Exception(
                f"Error setting discord metadata: [{response.status_code}] {response.text}"
            )

    async def push_role_connection(self, bot_access_token: str, body: list):
        # GET/PUT /users/@me/applications/:id/role-connection
        url = f"https://discord.com/api/v10/users/@me/applications/{self.client_id}/role-connection"
        data = json.dumps(body)
        response = requests.put(
            url,
            data,
            headers={
                "Authorization": f"Bearer {bot_access_token}",
                "Content-Type": "application/json",
            },
        )
        if response.ok:
            return response.json()
        else:
            raise Exception(
                f"Error putting discord metadata: [{response.status_code}] {response.text}"
            )

    async def get_role_connection(self, bot_access_token: str):
        # GET/PUT /users/@me/applications/:id/role-connection
        url = f"https://discord.com/api/v10/users/@me/applications/{self.client_id}/role-connection"
        response = requests.get(
            url, headers={"Authorization": f"Bearer {bot_access_token}"}
        )
        if response.ok:
            return response.json()
        else:
            raise Exception(
                f"Error getting discord metadata: [{response.status_code}] {response.text}"
            )
    
    async def reflesh_role_connection(self, id:int):
        try:
            bot_tokens = self.collection.find_one({"_id":id})["bot_tokens"]
            body = await self.get_role_data(id)
            return await self.push_role_connection(bot_tokens["access_token"], body)
        except:
            bot_tokens = await self.refresh_token(bot_tokens["refresh_token"])
            self.collection.update_one({"_id":id}, {"bot_tokens": bot_tokens})
            return await self.push_role_connection(bot_tokens["access_token"], body)
        
    async def refresh_token(self, refresh_token: str):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post('%s/oauth2/token' % 'https://discord.com/api', data=data, headers=headers)
        r.raise_for_status()
        return r.json()

    async def _find_clear_data(self, id: int):
        return self.collection.find_one({"_id": id})

    async def create_role_data(self, id: int):
        metadata_dict = {
            item["key"]: (
                0
                if int(item["type"]) >= 1 and int(item["type"]) <= 4
                else datetime.datetime.now().isoformat()
                if int(item["type"]) == 5 or int(item["type"]) == 6
                else False
            )
            for item in self.metadata_set
        }

        self.collection.insert_one(
            {
                "_id": id,
                "platform_name": "Extranjero",
                "platform_username": "Steve",
                "metadata": metadata_dict,
                "tokens": dict()
            }
        )

        return self.collection.find_one({"_id": id})

    async def get_role_data(self, id: int):
        rawdata = await self._find_clear_data(id) or await self.create_role_data(id)
        metadata_set = [x['key'] for x in self.metadata_set]
        return {
            "platform_name": rawdata["platform_name"],
            "platform_username": rawdata["platform_username"],
            "metadata": {
                key: value
                for key, value in rawdata["metadata"].items()
                if key in metadata_set
            },
        }
    