from pygame import *
import extras, mouse_extras, roads, popups

# Get the monitor size
init()
info = display.Info()
monitor_size = info.current_w, info.current_h

def get_dir():
    import os
    cwd = os.getcwd()

def run():

    # Load settings from 'settings.txt'
    # Requires user input so a nice error message is good
    try:
        file = open('settings.txt', 'r')
        info = dict(eval(file.read()))
        file.close()
    except Exception as error:
        print('Error Loading settings file')
        print(error)
        return

    # Add the monitor size to the info dict
    global monitor_size
    info['monitor_size'] = monitor_size

    # Setup
    clock = time.Clock()

    # game_window_width is the unscaled size, game_surf_width is scaled
    info['window']['game_window_width'] = min(info['window']['size'])
    info['window']['game_surf_width'] = info['window']['game_window_width'] * info['zoom']

    def update_pixel_size(info):
        info['window']['pixel_size'] = info['window']['game_window_width'] / info['window']['game_surf_width'] + 0.5
        return info

    def show_grid_lines(game_window, info):

        for x in range(info['grid_size']):
            x = info['window']['game_scale'] * x
            extras.show_things.append(('line', (50, 0, 0), (int(x), 0), (int(x), int(info['window']['game_surf_width'])), 1))

        for y in range(info['grid_size']):
            y = info['window']['game_scale'] * y
            extras.show_things.append(('line', (50, 0, 0), (0, int(y)), (int(info['window']['game_surf_width']), int(y)), 1))


    def resize_main(info):

        if info['fullscreen']: window_size = info['monitor_size']
        else: window_size = info['window']['size']

        # Window size things
        info['window']['game_window_width'] = min(window_size)
        info['window']['game_surf_width'] = info['window']['game_window_width'] * info['zoom']
        info['window']['game_scale'] = info['window']['game_surf_width'] / info['grid_size']

        # The game window
        info['game_window'] = Surface((info['window']['game_window_width'],) * 2)

        # The actual window
        if info['fullscreen']:

            info['window']['in_use_size'] = info['monitor_size']

            if not info['is_fullscreen']:
                info['main_window'] = display.set_mode(window_size, FULLSCREEN); info['is_fullscreen'] = True

        else:
            info['window']['in_use_size'] = info['window']['size']
            info['main_window'] = display.set_mode(info['window']['size'], RESIZABLE)
            info['is_fullscreen'] = False

        return info

    # Without this pygame will stop
    def event_loop():
        events = event.get()
        for i in events:
            if i.type == QUIT: quit()
        return events

    # Set up
    info = resize_main(info)
    info = update_pixel_size(info)

    # Objects
    road_handler = roads.Handler()

    # Make popups
    popups.all['placing'] = popups.New('placing', image.load('images//popup_icons//road.png'), 'Placing Systems', 0, {
        'Test1': {
            'type': 'button',
            'show_type': 'image',
            'image': image.load('images//popup_icons//test.png'),
        },
        'Test2': {
            'type': 'button',
            'show_type': 'image',
            'image': image.load('images//popup_icons//test.png'),
        }
    })
    popups.update(info)

    # -----------
    #  Game Loop
    # -----------


    while True:

        # dt or delta time is used to make things move at the correct speed when fps changes
        info['dt'] = clock.tick() / 1000

        info['events'] = event_loop()
        mouse_extras.update(info)

        for e in info['events']:

            # Fullscreen
            if e.type == KEYDOWN:
                if e.key == K_F10:

                    # Update screen
                    info['fullscreen'] = abs(info['fullscreen'] - 1)
                    info = resize_main(info)

                if e.key == K_ESCAPE:
                    info['fullscreen'] = 0
                    info = resize_main(info)

                if e.key == K_F2:
                    info['hidden_info'] = abs(int(info['hidden_info'] - 1))

                if e.key == K_F3:
                    info['hidden_items'] = abs(int(info['hidden_items'] - 1))

            # Resize
            if e.type == VIDEORESIZE:
                if not info['fullscreen']:
                    info['window']['size'] = (e.w, e.h)
                    info = resize_main(info)

            # Zoom
            if e.type == MOUSEBUTTONDOWN:
                zoom_speed = 10
                if e.button == 4: info['zoom'] += zoom_speed * info['dt'] * info['zoom'] # Zoom in
                if e.button == 5: info['zoom'] -= zoom_speed * info['dt'] * info['zoom'] # Zoom out

                if e.button == 4 or e.button == 5:
                    info['zoom'] = min(max(0.8, info['zoom']), 1.5)
                    info['window']['game_scale'] = info['window']['game_surf_width'] / info['grid_size']
                    info = resize_main(info)

        # Position of the 'game_window on the main window
        if info['is_fullscreen']: window_size = info['monitor_size']
        else: window_size = info['window']['size']

        # Updatey things (all needed throughout game loop)
        info['window']['pos'] = ((window_size[0] - (info['window']['game_surf_width'])) / 2 + info['offset'][0],
                                 (window_size[1] - (info['window']['game_surf_width'])) / 2 + info['offset'][1])

        # Move
        mouse_buttons = mouse.get_pressed()
        info['mouse_rel'] = mouse.get_rel()

        # Change the offset
        if key.get_pressed()[K_LCTRL] and mouse_buttons[0] or mouse_buttons[1]:
            info['offset'][0] += info['mouse_rel'][0]
            info['offset'][1] += info['mouse_rel'][1]


        info = update_pixel_size(info)

        # Window Background
        info['main_window'].fill(info['window_background'])
        info['game_window'].fill(info['game_background'])

        # Show items
        info['window']['game_surf_width'] = info['window']['game_window_width'] * info['zoom']
        info['game_window'] = transform.scale(info['game_window'], (int(info['window']['game_surf_width']),) * 2)

        # Show grid lines
        if info['hidden_items']: show_grid_lines(info['game_window'], info)

        # Draw lines
        road_handler.draw(info)

        for img in road_handler.update(info): extras.show_things.append(img)
        extras.show_everthing(info)

        # Add the game window to the main
        info['main_window'].blit(info['game_window'], info['window']['pos'])

        # Show popups
        popups.update(info)

        # Show fps
        if info['hidden_info']: extras.fps_counter(info['main_window'])

        # Cool info things
        if info['hidden_info']: extras.show_info(info['main_window'])

        # This sets the name of the window, It is just showing cool info to make sure everythin is a-okay
        display.set_caption(info['window']['name'])

        # Update the screen!
        display.update()

run()
