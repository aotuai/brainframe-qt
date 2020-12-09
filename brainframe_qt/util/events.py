import threading


def or_events(*events):
    """Or multiple events together. Does not clear the underlying events"""
    or_event = threading.Event()

    def changed():
        if any(e.is_set() for e in events):
            or_event.set()
        else:
            or_event.clear()

    def orify(e, changed_callback):

        def or_set(event_):
            event_.set_()
            event_.changed()

        def or_clear(event_):
            event_.clear_()
            event_.changed()

        e.set_ = e.set
        e.clear_ = e.clear
        e.changed = changed_callback
        e.set = lambda: or_set(e)
        e.clear = lambda: or_clear(e)

    for event in events:
        orify(event, changed)
    changed()
    return or_event
