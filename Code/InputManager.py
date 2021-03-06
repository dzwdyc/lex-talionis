try:
    import configuration as cf
    import Engine
except ImportError:
    from . import configuration as cf
    from . import Engine

class InputManager(object):
    def __init__(self):
        self.init_joystick()

        self.buttons = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'START', 'SELECT', 'BACK', 'AUX', 'INFO']
        self.hard_buttons = self.buttons[4:] # these buttons cause state to change

        self.update_key_map()

        # Build up and down button checker
        self.keys_pressed = {}
        self.joys_pressed = {}
        for button in self.buttons:
            self.keys_pressed[button] = False
            self.joys_pressed[button] = False

        self.update_joystick_config()

        self.key_up_events = []
        self.key_down_events = []

        self.unavailable_button = None

    # Set joystick information. 
    # The joystick needs to be plugged in before this method is called (see main() method) 
    def init_joystick(self):
        if Engine.joystick_avail():
            joystick = Engine.get_joystick()
            joystick.init()
            self.joystick = joystick
            self.joystick_name = joystick.get_name()
        else:
            self.joystick = None
            self.joystick_name = None
        print(self.joystick_name)

    # button is a string of the designation in the list above 
    def is_pressed(self, button):
        return self.keys_pressed[button] or self.joys_pressed[button]

    def update(self):
        self.update_key_map()
        self.update_joystick_config()

    def update_key_map(self):
        self.key_map = {}
        self.key_map['UP'] = cf.OPTIONS['key_UP']
        self.key_map['LEFT'] = cf.OPTIONS['key_LEFT']
        self.key_map['RIGHT'] = cf.OPTIONS['key_RIGHT']
        self.key_map['DOWN'] = cf.OPTIONS['key_DOWN']
        self.key_map['SELECT'] = cf.OPTIONS['key_SELECT']
        self.key_map['START'] = cf.OPTIONS['key_START']
        self.key_map['BACK'] = cf.OPTIONS['key_BACK']
        self.key_map['AUX'] = cf.OPTIONS['key_AUX']
        self.key_map['INFO'] = cf.OPTIONS['key_INFO']

        self.map_keys = {v: k for k, v in self.key_map.items()}

    def update_joystick_config(self):
        self.joystick_config = {}
        # Don't use [('is_button', 6), ('is_button', 7)] # Select/Start, since they fire up events even when pressed 
        self.joystick_config['SELECT'] = [('is_button', 0)] # A
        self.joystick_config['BACK'] = [('is_button', 1)] # B
        self.joystick_config['START'] = [('is_button', 3)] # Y
        self.joystick_config['INFO'] = [('is_button', 5)] # RB
        self.joystick_config['AUX'] = [('is_button', 4)] # LB
        # hat
        self.joystick_config['LEFT'] = [('is_hat', 0, 'x', -1)]
        self.joystick_config['RIGHT'] = [('is_hat', 0, 'x', 1)]
        self.joystick_config['UP'] = [('is_hat', 0, 'y', 1)]
        self.joystick_config['DOWN'] = [('is_hat', 0, 'y', -1)]

    def process_input(self, eventList, all_keys=False):
        self.key_up_events = []
        self.key_down_events = []
        # Check keyboard
        for event in eventList:
            # Check keys
            if event.type == Engine.KEYUP or event.type == Engine.KEYDOWN:
                button = self.map_keys.get(event.key)
                key_up = event.type == Engine.KEYUP
                # print(button, key_up)
                if button:
                    self.keys_pressed[button] = not key_up
                    if key_up:
                        self.key_up_events.append(button)
                    else:
                        self.key_down_events.append(button)
                elif all_keys and event.type == Engine.KEYUP:
                    self.unavailable_button = event.key
                    return 'NEW'

        # Check game pad
        if self.joystick:
            self.handle_joystick()

        # Return the correct event for this frame -- Gives priority to later inputs...
        # Remove reversed to give priority to earlier inputs
        for button in reversed(self.key_up_events):
            if button in self.hard_buttons:
                return button
        if self.key_up_events:
            return self.key_up_events[-1]

        # self.print_key_pressed()
        
    def handle_joystick(self):
        for button in self.buttons:
            configs = self.joystick_config.get(button)
            if configs:
                for config in configs:
                    # If the button behaves like a normal button
                    if config[0] == 'is_button':
                        pushed = self.joystick.get_button(config[1])
                        # If the state changed
                        if pushed != self.joys_pressed[button]:
                            self.joys_pressed[button] = pushed
                            if not pushed:
                                self.key_up_events.append(button)

                    # if the button is configured to a hat direction... 
                    elif config[0] == 'is_hat':
                        status = self.joystick.get_hat(config[1])
                        if config[2] == 'x': # Which axis
                            amount = status[0]
                        else:
                            amount = status[1]
                        pushed = amount == config[3]
                        if pushed != self.joys_pressed[button]:
                            self.joys_pressed[button] = pushed
                            if not pushed:
                                self.key_up_events.append(button)

    def print_key_pressed(self):
        for key, value in self.keys_pressed.items():
            if value:
                print('Key Down', key)
        for joy, value in self.joys_pressed.items():
            if value:
                print('Joy Down', joy)

class FluidScroll(object):
    def __init__(self, speed=64, slow_speed=3):
        self.moveLeft = False
        self.moveRight = False
        self.moveUp = False
        self.moveDown = False
        self.left_update, self.right_update, self.up_update, self.down_update = 0, 0, 0, 0
        self.fast_speed = speed
        self.slow_speed = speed*slow_speed if slow_speed else speed
        self.move_counter = 0

    def update(self, gameStateObj):
        if gameStateObj.input_manager.is_pressed('LEFT') or 'LEFT' in gameStateObj.input_manager.key_down_events:
            self.moveRight = False
            self.moveLeft = True
        else:
            self.moveLeft = False

        if gameStateObj.input_manager.is_pressed('RIGHT') or 'RIGHT' in gameStateObj.input_manager.key_down_events:
            self.moveLeft = False
            self.moveRight = True
        else:
            self.moveRight = False

        if gameStateObj.input_manager.is_pressed('UP') or 'UP' in gameStateObj.input_manager.key_down_events:
            self.moveDown = False
            self.moveUp = True
        else:
            self.moveUp = False

        if gameStateObj.input_manager.is_pressed('DOWN') or 'DOWN' in gameStateObj.input_manager.key_down_events:
            self.moveUp = False
            self.moveDown = True
        else:
            self.moveDown = False

        if 'LEFT' in gameStateObj.input_manager.key_down_events:
            self.left_update = 0
        if 'RIGHT' in gameStateObj.input_manager.key_down_events:
            self.right_update = 0
        if 'DOWN' in gameStateObj.input_manager.key_down_events:
            self.down_update = 0
        if 'UP' in gameStateObj.input_manager.key_down_events:
            self.up_update = 0

        if any(direction in gameStateObj.input_manager.key_down_events for direction in ('LEFT', 'RIGHT', 'UP', 'DOWN')):
            self.move_counter = 0
            return True
        return False

    def get_directions(self):
        directions = []
        currentTime = Engine.get_time()
        if self.move_counter >= 2:
            speed = self.fast_speed
        else:
            speed = self.slow_speed
        
        if self.moveLeft and currentTime - self.left_update > speed:
            directions.append('LEFT')
            # self.set_all_updates(currentTime)
        if self.moveRight and currentTime - self.right_update > speed:
            directions.append('RIGHT')
            # self.set_all_updates(currentTime)
        if self.moveDown and currentTime - self.down_update > speed:
            directions.append('DOWN')
            # self.set_all_updates(currentTime)
        if self.moveUp and currentTime - self.up_update > speed:
            directions.append('UP')
            # self.set_all_updates(currentTime)

        if directions:
            self.set_all_updates(currentTime)
            self.move_counter += 1
        elif not (self.moveLeft or self.moveRight or self.moveUp or self.moveDown):
            self.move_counter = 0
        return directions

    def update_speed(self, speed=64, slow_speed=3):
        self.fast_speed = speed
        self.slow_speed = speed*slow_speed

    def set_all_updates(self, time):
        self.left_update = time
        self.right_update = time
        self.down_update = time
        self.up_update = time
