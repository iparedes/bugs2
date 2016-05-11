import sys, random, pygame
from ocempgui.widgets import Button, Renderer, Constants

# Used to see some action happending in the GUI.
amount = 0
def _count_clicks (b):
    global amount
    amount += 1
    b.text = "Clicked %d times" % amount

# Initialize pygame window
pygame.init ()
screen = pygame.display.set_mode ((200, 200));
screen.fill ((255, 200, 100))

# Create the Renderer to use for the UI elements.
re = Renderer ()

# Bind it to a part of the screen, which it will use to draw the widgets.
# Here we use the complete screen.
re.screen = screen

# Create a button, place it at x=10, y=30, bind a callback to its
# clicking action and add it to the Renderer instance.
button = Button ("Simple Button")
button.topleft = 10, 30
button.connect_signal (Constants.SIG_CLICKED, _count_clicks, button)
re.add_widget (button)

# Some variables we will need in the main loop for drawing a rect.
rnd = None
color = None
cnt = 100

while True:
    events = pygame.event.get ()
    for ev in events:
        if ev.type == pygame.QUIT:
            sys.exit ()
        # We could handle other events separately, too, but do not care.

    # Draw the rectangle on the screen.
    cnt -= 1
    if cnt == 0:
        rnd = (random.randint (0, 5), random.randint (0, 5), \
               random.randint (0, 5))
        color = (rnd[0] * 340) % 255,  (rnd[1] * 122) % 255, \
                (rnd[2] * 278) % 255
        pygame.draw.rect (screen, color, (60, 50, 50, 50))
        cnt = 100

    # Pass all received events to the Renderer. We also could pass only
    # a subset of them, but want it to get all.
    re.distribute_events (*events)

    # Force a refresh of the UI elements as our main screen changed and
    # we want them to be placed upon the changes (look at the
    # intersection with the rectangle).
    re.refresh ()

    # We do not need to flip as it is done in the refresh() method of
    # the Renderer. If we assign just a part of the screen to the
    # Renderer, we would have to, of course.
    # pygame.display.flip ()

    # Do not use 100% CPU.
    pygame.time.delay (15)
