import time, micropython
from machine import Pin

class Button:
    def __init__(
        self,
        pin_num: int,
        debounce_ms = 30,
        pull: str = "up",
        multi_click_timeout: int = 100
        ):
        """
        Initialize a debounced GPIO button with optional multi-click detection.

        Parameters
        ----------
        pin_num : int
            GPIO pin number connected to the button.
        debounce_ms : int, optional
            Debounce interval in milliseconds. State changes occurring within
            this window are ignored. Default is 30.
        pull : {"up", "down"}, optional
            Internal pull resistor configuration. Determines the electrical
            idle state and active polarity of the button. Default is "up".
        multi_click_timeout : int, optional
            Maximum time interval in milliseconds between consecutive presses
            to be considered part of the same multi-click sequence. Default is 100.

        Raises
        ------
        ValueError
            If `pull` is not one of {"up", "down"}.

        Notes
        -----
        The button uses interrupt-based detection and schedules handlers using
        `micropython.schedule` to ensure safe execution outside IRQ context.
        """
        now = time.ticks_ms()

        pull = pull.lower()
        if pull not in ("up","down"):
            raise ValueError("pull must be either up or down")
        elif pull == "up":
            pull_val = Pin.PULL_UP
            self._active_on = False
        else:
            pull_val = Pin.PULL_DOWN
            self._active_on = True
        
        self.pin = Pin(pin_num, Pin.IN, pull_val)
        self._debounce_ms = debounce_ms

        self._state = self._read_value()
        self._last_change = self._last_press = self._last_release = now
        
        self._pressed_event = self._released_event = False

        # Multi-click
        self._multi_click_timeout = multi_click_timeout
        self._multi_click_count = self._multi_click_helper = 0
        self._multi_click_finalized = True

        self.pin.irq(
            trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,
            handler=lambda _: micropython.schedule(self._irq_handler, 0)
        )
    
    def _read_value(self):
        """
        Read the logical button state.

        Returns
        -------
        bool
            True if the button is currently pressed, False otherwise.

        Notes
        -----
        The returned value accounts for the configured pull direction and
        active polarity.
        """
        value = self.pin.value()
        return value == self._active_on

    def _irq_handler(self, _):
        """
        Interrupt handler for GPIO state changes.

        Parameters
        ----------
        _ : Any
            Unused argument required by `micropython.schedule`.

        Notes
        -----
        Applies debounce filtering and updates internal state. Press and release
        events are recorded, and multi-click tracking is updated when applicable.
        """
        now = time.ticks_ms()
        new_state = self._read_value()

        # Ignore if still in debounce window
        if time.ticks_diff(now, self._last_change) < self._debounce_ms:
            return

        if new_state != self._state:
            self._state = new_state
            self._last_change = now

            if self._state:
                self._pressed_event = True
                self._last_press = now

                self._multi_click_helper += 1
                if self._multi_click_finalized:
                    self._multi_click_initialize()
            else:
                self._released_event = True
                self._last_release = now
    
    # Multi-click logic
    def _multi_click_initialize(self):
        """
        Begin a multi-click detection window.

        Notes
        -----
        Schedules `_multi_click_handler` to determine when the click
        sequence has completed.
        """
        self._multi_click_finalized = False
        micropython.schedule(self._multi_click_handler,0)
    
    def _multi_click_handler(self, _):
        """
        Finalize multi-click detection after timeout.

        Parameters
        ----------
        _ : Any
            Unused argument required by `micropython.schedule`.

        Notes
        -----
        Once no new press is detected within the configured timeout,
        the accumulated click count is finalized and made available
        through `multi_click_count`.
        """
        now = time.ticks_ms()

        if time.ticks_diff(now, self._last_press)<self._multi_click_timeout:
            micropython.schedule(self._multi_click_handler, 0)
            return
        
        self._multi_click_count = self._multi_click_helper
        self._multi_click_helper = 0
        self._multi_click_finalized = True

    # Public API
    @property
    def is_pressed(self) -> bool:
        """
        Current logical state of the button.

        Returns
        -------
        bool
            True if the button is currently pressed, False otherwise.
        """
        return self._state

    def was_pressed(self) -> bool:
        """
        Check whether a press event occurred.

        Returns
        -------
        bool
            True if the button was pressed since the last call to this method,
            False otherwise.

        Notes
        -----
        This method clears the internal pressed event flag when read.
        """
        if self._pressed_event:
            self._pressed_event = False
            return True
        return False

    def was_released(self) -> bool:
        """
        Check whether a release event occurred.

        Returns
        -------
        bool
            True if the button was released since the last call to this method,
            False otherwise.

        Notes
        -----
        This method clears the internal released event flag when read.
        """
        if self._released_event:
            self._released_event = False
            return True
        return False
    
    @property
    def held_time(self):
        """
        Duration the button has been held.

        Returns
        -------
        int
            Time in milliseconds that the button has been continuously pressed.
            Returns 0 if the button is not currently pressed.
        """
        if not self.is_pressed:
            return 0
        
        return time.ticks_diff(time.ticks_ms(),self._last_press)
    
    @property
    def multi_click_count(self) -> int:
        """
        Number of clicks detected in the last completed sequence.

        Returns
        -------
        int
            Number of consecutive presses detected within the configured
            multi-click timeout window. Returns 0 if no completed sequence
            is available.

        Notes
        -----
        Reading this property resets the stored click count to zero.
        """
        count = self._multi_click_count
        self._multi_click_count = 0
        return count