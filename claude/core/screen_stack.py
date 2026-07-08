"""Screen Stack Manager - Handles screen navigation like a mobile app"""
from typing import Optional, Type
import logging

logger = logging.getLogger(__name__)


class ScreenStack:
    """
    Manages a stack of screens with state preservation.
    Screens can be pushed onto the stack and popped off, preserving state.
    """

    def __init__(self):
        self._stack = []
        self._current_screen = None

    @property
    def current_screen(self):
        """Get the current (top) screen"""
        return self._current_screen

    @property
    def depth(self) -> int:
        """Get current stack depth"""
        return len(self._stack)

    def push(self, screen_instance, replace: bool = False):
        """
        Push a new screen onto the stack.

        Args:
            screen_instance: Instance of a screen to push
            replace: If True, replace current screen instead of pushing on top
        """
        # Exit current screen if exists
        if self._current_screen:
            logger.info(f"Exiting screen: {self._current_screen.__class__.__name__}")
            self._current_screen.on_exit()

            if replace and self._stack:
                # Replace the top screen
                self._stack[-1] = screen_instance
                logger.info(f"Replaced screen with: {screen_instance.__class__.__name__}")
            else:
                # Push new screen on top
                self._stack.append(screen_instance)
                logger.info(f"Pushed screen: {screen_instance.__class__.__name__}")
        else:
            # First screen
            self._stack.append(screen_instance)
            logger.info(f"Initial screen: {screen_instance.__class__.__name__}")

        # Set as current and enter
        self._current_screen = screen_instance
        self._current_screen.on_enter()

    def pop(self) -> bool:
        """
        Pop the current screen and return to previous.

        Returns:
            True if screen was popped, False if at root screen
        """
        if len(self._stack) <= 1:
            logger.info("Cannot pop: at root screen")
            return False

        # Exit current screen
        if self._current_screen:
            logger.info(f"Exiting screen: {self._current_screen.__class__.__name__}")
            self._current_screen.on_exit()

        # Remove from stack
        self._stack.pop()

        # Set previous screen as current and re-enter
        self._current_screen = self._stack[-1]
        logger.info(f"Returned to screen: {self._current_screen.__class__.__name__}")
        self._current_screen.on_enter()

        return True

    def pop_to_root(self):
        """Pop all screens except the root"""
        while len(self._stack) > 1:
            self.pop()

    def replace_all(self, screen_instance):
        """Replace entire stack with a single new screen"""
        # Exit all screens
        for screen in self._stack:
            try:
                screen.on_exit()
            except Exception as e:
                logger.error(f"Error exiting screen during replace_all: {e}")

        # Clear stack and set new screen
        self._stack = [screen_instance]
        self._current_screen = screen_instance
        logger.info(f"Replaced entire stack with: {screen_instance.__class__.__name__}")
        self._current_screen.on_enter()

    def peek_previous(self):
        """Peek at the screen below current without popping"""
        if len(self._stack) >= 2:
            return self._stack[-2]
        return None

    def clear(self):
        """Clear all screens from stack"""
        for screen in self._stack:
            try:
                screen.on_exit()
            except Exception as e:
                logger.error(f"Error exiting screen during clear: {e}")

        self._stack = []
        self._current_screen = None
        logger.info("Screen stack cleared")

    def get_stack_info(self) -> str:
        """Get string representation of stack for debugging"""
        screens = [s.__class__.__name__ for s in self._stack]
        return " -> ".join(screens)
