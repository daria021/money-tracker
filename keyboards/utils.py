def chunk(buttons: list[str]):
    layout = []
    while len(buttons) > 0:
        try:
            layout.append([buttons[0], buttons[1]])
            buttons.pop(0)
            buttons.pop(0)
        except:
            layout.append([buttons[0]])
            buttons.pop(0)
    return layout
