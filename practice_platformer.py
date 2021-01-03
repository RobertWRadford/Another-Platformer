"""
Platformer Game
"""
import math
from typing import Optional
import arcade
import timeit

# Constants

SCREEN_WIDTH = arcade.get_screens()[0].width
SCREEN_HEIGHT = arcade.get_screens()[0].height-50

SCREEN_TITLE = "Platformer"


WIDTH_SCALING = (SCREEN_WIDTH/1000)

#Constants used to scale our sprites from their original size
CHARACTER_SCALING = .45*WIDTH_SCALING
TILE_SCALING = 0.35*WIDTH_SCALING
COIN_SCALING = 0.35*WIDTH_SCALING
TILE_WIDTH = int(44.8*WIDTH_SCALING)

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5*WIDTH_SCALING
UPDATES_PER_FRAME = 5
PLAYER_JUMP_SPEED = 14*WIDTH_SCALING
GRAVITY = 1*WIDTH_SCALING

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = int(SCREEN_WIDTH/3.5)
RIGHT_VIEWPORT_MARGIN = int(SCREEN_WIDTH/3.5)
BOTTOM_VIEWPORT_MARGIN = int(SCREEN_HEIGHT/5.5)
TOP_VIEWPORT_MARGIN = int(SCREEN_HEIGHT/2.5)

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

class PlayerCharacter(arcade.Sprite):
    
    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        self.scale = CHARACTER_SCALING

        # Adjust the collision box. Default includes too much empty space
        # side-to-side. Box is centered at sprite center, (0, 0)

        # --- Load Textures ---

        # Images from Kenney.nl's Asset Pack 3
        main_path = ":resources:images/animated_characters/male_adventurer/maleAdventurer"
        # main_path = ":resources:images/animated_characters/female_person/femalePerson"
        # main_path = ":resources:images/animated_characters/male_person/malePerson"
        # main_path = ":resources:images/animated_characters/female_adventurer/femaleAdventurer"
        # main_path = ":resources:images/animated_characters/zombie/zombie"
        # main_path = ":resources:images/animated_characters/robot/robot"

        # Load textures for idle standing
        self.idle_texture_pair = arcade.load_texture_pair(f"{main_path}_idle.png", hit_box_algorithm='Detailed')
        
        self.texture = self.idle_texture_pair[0]
        self.hit_box = self.texture.hit_box_points

        # Load textures for walking
        self.walk_textures = []
        for i in range(8):
            texture = arcade.load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        self.climbing_textures = [arcade.load_texture_pair(f'{main_path}_climb0.png'), arcade.load_texture_pair(f'{main_path}_climb1.png')]

        self.jumping_texture_pair = arcade.load_texture_pair(f'{main_path}_jump.png')
        self.falling_texture_pair = arcade.load_texture_pair(f'{main_path}_fall.png')

    def update_animation(self, on_ladder, delta_time: float = 1/60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        if on_ladder:
            self.cur_texture += 1
            if self.cur_texture > 1 * (1/delta_time):
                self.cur_texture = 0
            frame = round(self.cur_texture/(1/delta_time))
            direction = self.character_face_direction
            self.texture = self.climbing_textures[int(frame)][direction]
            return

        # check for jumping
        if self.change_y > 0:
            self.texture = self.jumping_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0:
            self.texture = self.falling_texture_pair[self.character_face_direction]
            return

        # Idle animation
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 7 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // UPDATES_PER_FRAME
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]



class InstructionView(arcade.View):

    def __init__(self, level, time=0):
        self.level = level
        self.time = time
        super().__init__()


    def on_show(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.DARK_GREEN)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        hours = 0
        minutes = 0
        seconds = 0
        if self.level == 7:
            hours = int((self.time/60)/60)
            minutes = int((self.time//60)%60)
            seconds = int(self.time%60)

        level_header_text = {
            1: 'Collect All Coins To Move On',
            2: 'Downs and Ups',
            3: 'Chutes and Ladders',
            4: 'Ascension',
            5: 'Gravity Falls',
            6: '360 Ladder Stall No Scope',
            7: 'Congratulations!'
        }
        level_descript_text = {
            1: 'A and D to move left and right, SPACE to jump. R to reset level but keeps time, L to full reset. F to toggle fullscreen.',
            2: 'You have one jump at a time but can jump mid air.',
            3: 'W and S to move up and down a ladder',
            4: 'You\'ve unlocked double jumping!, you now have two jumps per reset.',
            5: 'One cycle is best cycle. If you aren\'t holding a key ladders stop your speed.',
            6: 'Careful ^.^',
            7: f'You beat the game in {hours}:{minutes:02d}:{seconds:02d}.'
        }
        arcade.draw_text(f"Level {self.level}: {level_header_text[self.level]}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.WHITE, font_size=35*WIDTH_SCALING, anchor_x='center')
        arcade.draw_text(f"{level_descript_text[self.level]}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-(75*WIDTH_SCALING), arcade.color.WHITE, font_size=10*WIDTH_SCALING, anchor_x='center')
        arcade.draw_text("Click or press R to advance", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-(150*WIDTH_SCALING), arcade.color.WHITE, font_size=10*WIDTH_SCALING, anchor_x='center')

    def on_key_press(self, key, modifiers):

        if key == arcade.key.R:
            if self.level == 7:
                game_view = InstructionView(1, 0)
                self.window.show_view(game_view)
            game_view = GameView(self.level, self.time)
            game_view.setup(self.level)
            self.window.show_view(game_view)
        elif key == arcade.key.F:
            if self.window.fullscreen:
                self.window.set_fullscreen(fullscreen=False)
            else:
                self.window.set_fullscreen(fullscreen=True)
        elif key == arcade.key.L:
            start_view = InstructionView(1,0)
            self.window.show_view(start_view)
        elif key == arcade.key.ESCAPE:
            self.window.close()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        if self.level == 7:
            game_view = InstructionView(1, 0)
            self.window.show_view(game_view)
        game_view = GameView(self.level, self.time)
        game_view.setup(self.level)
        self.window.show_view(game_view)




class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self, level, time=0):

        # Call the parent class and set up the window
        super().__init__()
        self.window.set_mouse_visible(False)

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.player_list: Optional[arcade.SpriteList] = None
        self.wall_list: Optional[arcade.SpriteList] = None
        self.bullet_list: Optional[arcade.SpriteList] = None
        self.coin_list: Optional[arcade.SpriteList] = None
        # self.scenery_list: Optional[arcade.SpriteList] = None
        self.hazards_list: Optional[arcade.SpriteList] = None
        self.ladders_list: Optional[arcade.SpriteList] = None
        self.moving_platforms_list: Optional[arcade.SpriteList] = None

        # Separate variable that holds the player sprite
        self.player_sprite: Optional[arcade.SpriteList] = None

        # Our physics engine
        self.physics_engine = None

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Keep track of the score
        self.score = 0
        # timer variable
        self.frames = 0
        self.time = time

        #frame calculation
        self.frame_count = 0
        self.fps_start_timer = None
        self.fps = 60
        # self.current_update_rate = 60

        # Where is the right edge of the map?
        self.end_of_map = 0

        # Level
        self.level = level

        # set movement keys
        self.keys_pressed = None
        self.jump_remaining = 2

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin2.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump3.wav")
        self.game_over_sound = arcade.load_sound(":resources:sounds/gameover4.wav")

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self, level):
        """ Set up the game here. Call this function to restart the game. """

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Keep track of the score
        self.score = 0

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.keys_pressed = set()

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = PlayerCharacter()
        self.player_sprite.scale = CHARACTER_SCALING
        if level in [1, 4, 6]:
            self.player_sprite.center_x = TILE_WIDTH
            self.player_sprite.center_y = 2*TILE_WIDTH
        elif level in [2,3,5]:
            self.player_sprite.center_x = 2*TILE_WIDTH
            self.player_sprite.center_y = 3*TILE_WIDTH
        self.player_list.append(self.player_sprite)

        # --- Load in a map from the tiled editor ---

        # Name of map file to load
        map_name = f"maps/map_level_{level}.tmx"
        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Platforms'
        # Name of the layer that has items for pick-up
        coins_layer_name = 'Coins'
        # Name of the layer that has background objects
        scenery_layer_name = 'Scenery'
        # Name of the layer that has hazards objects
        hazards_layer_name = 'Hazards'
        # Name of moving platforms layer
        moving_platforms_layer_name = 'Moving Platforms'
        # Name of ladder layer
        ladders_layer_name = 'Ladders'

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # -- Platforms
        self.wall_list = arcade.tilemap.process_layer(my_map,
                                                      platforms_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)
        # -- Moving Platforms
        self.moving_platforms_list = arcade.tilemap.process_layer(my_map, moving_platforms_layer_name, TILE_SCALING)
        for sprite in self.moving_platforms_list:
            
            sprite.change_x *= WIDTH_SCALING
            sprite.change_y *= WIDTH_SCALING

            if sprite.boundary_right:
                sprite.boundary_right *= TILE_SCALING
            if sprite.boundary_left:
                sprite.boundary_left *= TILE_SCALING
            if sprite.boundary_top:
                sprite.boundary_top *= TILE_SCALING
            if sprite.boundary_bottom:
                sprite.boundary_bottom *= TILE_SCALING
            self.wall_list.append(sprite)
        
        # -- Coins
        self.coin_list = arcade.tilemap.process_layer(my_map, coins_layer_name, TILE_SCALING, use_spatial_hash=True)

        # -- Scenery
        # self.scenery_list = arcade.tilemap.process_layer(my_map, scenery_layer_name, TILE_SCALING, use_spatial_hash=True)

        # -- Hazards
        self.hazards_list = arcade.tilemap.process_layer(my_map, hazards_layer_name, TILE_SCALING, use_spatial_hash=True)

        # -- Ladders
        self.ladders_list = arcade.tilemap.process_layer(my_map, ladders_layer_name, TILE_SCALING, use_spatial_hash=True)

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

                # Create the 'physics engine'; (player, collision tiles, gravity)
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             GRAVITY,
                                                             ladders=self.ladders_list)


    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        # Code to draw the screen goes here

        # Draw our sprites
        self.wall_list.draw()
        self.coin_list.draw()
        # self.scenery_list.draw()
        self.hazards_list.draw()
        self.ladders_list.draw()
        self.player_list.draw()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Coins Remaining: {len(self.coin_list)}"
        arcade.draw_text(score_text, 10*WIDTH_SCALING + self.view_left, 10*(WIDTH_SCALING) + self.view_bottom,
                         arcade.csscolor.WHITE, 18*WIDTH_SCALING)

        hours = int((self.time/60)/60)
        minutes = int((self.time//60)%60)
        seconds = int(self.time%60)

        frames_text = f"Time: {hours}:{minutes:02d}:{seconds:02d}"
        arcade.draw_text(frames_text, 10*WIDTH_SCALING + self.view_left, 30*(WIDTH_SCALING) + self.view_bottom,
                         arcade.csscolor.WHITE, 18*WIDTH_SCALING)

        # Display timings
        # output = f"FPS: {self.fps:.2f}"
        # arcade.draw_text(output, 15*WIDTH_SCALING + self.view_left, SCREEN_HEIGHT - (30*WIDTH_SCALING)+self.view_bottom, arcade.color.WHITE, 18*WIDTH_SCALING)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.keys_pressed.add('W')
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
                self.keys_pressed.add('S')
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
            self.keys_pressed.add('A')
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
            self.keys_pressed.add('D')
        elif key == arcade.key.R:
            self.setup(self.level)
        elif key == arcade.key.L:
            start_view = InstructionView(1,0)
            self.window.show_view(start_view)
        elif key == arcade.key.F:
            if self.window.fullscreen:
                self.window.set_fullscreen(fullscreen=False)
            else:
                self.window.set_fullscreen(fullscreen=True)
        elif key == arcade.key.SPACE:
            if self.jump_remaining:
                self.jump_remaining -= 1
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound, volume=.6)
                self.keys_pressed.add('SP')
        elif key == arcade.key.ESCAPE:
            self.window.close()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.keys_pressed.remove('W')
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.keys_pressed.remove('S')
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.keys_pressed.remove('A')
            if self.player_sprite.change_x == -PLAYER_MOVEMENT_SPEED:
                if 'D' in self.keys_pressed:
                    self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
                else:
                    self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.keys_pressed.remove('D')
            if self.player_sprite.change_x == PLAYER_MOVEMENT_SPEED:
                if 'A' in self.keys_pressed:
                    self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
                else:
                    self.player_sprite.change_x = 0
        elif key == arcade.key.SPACE:
            self.keys_pressed.remove('SP')

    def on_update(self, delta_time):
        """ Movement and game logic """

        # self.time += delta_time
        self.frames += 1
        if self.frames % 45 == 0:
            self.time+=1

        # if self.frame_count%60==0:
        #     self.frame_count = 0
        #     if self.fps_start_timer is not None:
        #         total_time = timeit.default_timer() - self.fps_start_timer
        #         self.fps = 60 / total_time
        #     self.fps_start_timer = timeit.default_timer()
        # self.frame_count+=1

        # if int(self.fps) != int(self.current_update_rate):
        #     if self.fps < 60:
        #         self.current_update_rate = self.fps
        #         self.window.set_update_rate(1/self.current_update_rate)
        #     else:
        #         self.current_update_rate = 60
        #         self.window.set_update_rate(1/self.current_update_rate)


        # Move the player with the physics engine
        # self.player_sprite.change_x *= (60/current_fps)
        # self.player_sprite.change_y *= (60/current_fps)
        self.physics_engine.update()

        if self.physics_engine.is_on_ladder():
            if 'W' in self.keys_pressed and 'SP' not in self.keys_pressed:
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif 'S' in self.keys_pressed and 'SP' not in self.keys_pressed:
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
            elif 'SP' not in self.keys_pressed:
                self.player_sprite.change_y = 0
            else:
                self.player_sprite.change_y = max(self.player_sprite.change_y-GRAVITY, 0)

        if len(self.moving_platforms_list):
            platform, distance = arcade.get_closest_sprite(self.player_sprite, self.moving_platforms_list)
            if (platform.center_y+TILE_WIDTH/2 > self.player_sprite.center_y-TILE_WIDTH > platform.center_y and platform.center_x-(3*TILE_WIDTH)/2 < self.player_sprite.center_x < platform.center_x+(3*TILE_WIDTH)/2):
                if self.level < 4:
                    self.jump_remaining = 1
                else:
                    self.jump_remaining = 2

        if self.physics_engine.is_on_ladder() or self.physics_engine.can_jump():
            if self.level < 4:
                self.jump_remaining = 1
            else:
                self.jump_remaining = 2

        self.wall_list.update()

        for wall in self.moving_platforms_list:

            if wall.boundary_right and wall.right > wall.boundary_right and wall.change_x > 0:
                wall.change_x *= -1
            if wall.boundary_left and wall.left < wall.boundary_left and wall.change_x < 0:
                wall.change_x *= -1
            if wall.boundary_top and wall.top > wall.boundary_top and wall.change_y > 0:
                wall.change_y *= -1
            if wall.boundary_bottom and wall.bottom < wall.boundary_bottom and wall.change_y < 0:
                wall.change_y *= -1

        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list)

        self.player_sprite.update_animation(self.physics_engine.is_on_ladder())
        # if on_moving_platform:
        #     if self.player_sprite.change_x < moving_hit_list[0].change_x:
        #         self.player_sprite.change_x += moving_hit_list[0].change_x
        #     if self.player_sprite.change_y < moving_hit_list[0].change_y:
        #         self.player_sprite.change_y += moving_hit_list[0].change_y

        # Check for collision with hazards
        if arcade.check_for_collision_with_list(self.player_sprite, self.hazards_list):
            arcade.play_sound(self.game_over_sound, volume=.4)
            self.setup(self.level)

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound, volume=.6)
            # Add one to the score
            self.score += 1
            # if self.score == 13:
            if not len(self.coin_list):
                game_view = InstructionView(self.level+1, self.time)
                self.window.show_view(game_view)
                return

        # --- Manage Scrolling ---

        # Track if we need to change the viewport

        changed = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True

        if changed:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)

        # arcade.set_viewport(max(self.player_sprite.center_x - SCREEN_WIDTH/2, 0),
        #                         min(self.player_sprite.center_x + SCREEN_WIDTH/2, SCREEN_WIDTH),
        #                         max(self.player_sprite.center_y - SCREEN_HEIGHT/2, 0),
        #                         min(self.player_sprite.center_y + SCREEN_HEIGHT/2, SCREEN_HEIGHT))

def main():
    """ Main method """
    #Views
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate=1/45)
    window.center_window()
    try:
        start_view = InstructionView(1, 0)
    except:
        window.close()
    window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()