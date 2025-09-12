from api import ROBOT_API


class ESA_ROBOT(ROBOT_API):

    def __init__(self, host, id, env, port_conns):
        # super().__init__(host=host, id=id, keys=get_frame_keys(KEY_CONF), env=env)
        super().__init__(ip=host, id=id, env=env, port_conn=port_conns)
        self.data_status = {}
        self.connected = False
        self.time_circle = 1

    async def connect_to_robot(self):
        try:
            for key in self.port_conns:
                self.register_callback(key, self.on_response)
            await self.init_connections()

        except Exception as e:
            print(f"Error When connected to the robot:{str(e)}")
