# import carla


class Hero(object):
    def __init__(self):
        self.world = None
        self.actor = None
        self.control = None

    def start(self, world):
        self.world = world
        self.actor = self.world.spawn_hero(blueprint_filter=world.args.filter)
        self.actor.set_autopilot(True, world.args.tm_port)

    def tick(self, clock):
        pass

        # Uncomment and modify to control manually, disable autopilot too
        #
        # ctrl = carla.VehicleControl()
        # ctrl.throttle = 0.5
        # ctrl.steer = 0.3
        # self.actor.apply_control(ctrl)

    def destroy(self):
        """Destroy the hero actor when class instance is destroyed"""
        if self.actor is not None:
            self.actor.destroy()
