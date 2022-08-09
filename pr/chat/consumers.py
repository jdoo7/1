from channels.consumer import SyncConsumer,AsyncConsumer
from channels.exceptions import StopConsumer
from time import sleep
import asyncio
import json
from asgiref.sync import async_to_sync
from .models import Chat,Group
class MySyncConsumer(SyncConsumer):

    def websocket_connect(self,event):
        print('Websocket-connected...',event)
        self.group_name=self.scope['url_route']['kwargs']['groupname']
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.send({
            'type':'websocket.accept'
        })

    def websocket_receive(self,event):
        data = json.loads(event['text'])
        group = Group.objects.get(name=self.group_name)
        if self.scope['user'].is_authenticated:
            chat = Chat(content=data['msg'],group=group)
            chat.save()
            data['user'] = self.scope['user'].username
            async_to_sync(self.channel_layer.group_send)(
                self.group_name,{
                'type':'chat.message',
                'message':json.dumps(data)
            })
        else:
            self.send({
                'type':'websocket.send',
                'text':json.dumps({"msg":"login required","user":"unknown"})
            })

    def chat_message(self,event):
        self.send({
            'type':'websocket.send',
            'text':event['message']
        })

    def websocket_disconnect(self,event):
        print('websocket-disconnected...',event)
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        raise StopConsumer()

class MyAsyncConsumer(AsyncConsumer):

    async def websocket_connect(self,event):
        print("websocket-connected...",event)

        await self.send({
            'type':'websocket.accept'
        })

    async def websocket_receive(self,event):
        print("message-received from client...",event)
        print(event['text'])
        for i in range(10):
            await self.send({
                'type':'websocket.send',
                'text': str(i)
            })
            await asyncio.sleep(1)

    async def websocket_disconnect(self,event):
        print("websocket-disconnected...",event)
        raise StopConsumer()