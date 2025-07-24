"""
Pytest configuration for progress notifications during slow tests.
"""
import pytest
import time
import threading


class ProgressReporter:
    """Manages progress notifications for slow tests."""

    def __init__(self):
        self._active_timers = {}
        self._lock = threading.Lock()

    def notify_user(self, test_name, estimated_seconds=None):
        """Show immediate notification and optional timer for slow tests."""
        if estimated_seconds:
            print(f"\n⏱️  Running {test_name} (estimated {estimated_seconds}s)...")
        else:
            print(f"\n⏱️  Running {test_name}...")

    def notify_slow_test_start(self, test_name, estimated_seconds=None):
        """Alias for notify_user to match test expectations."""
        self.notify_user(test_name, estimated_seconds)

    def start_timer(self, test_id, estimated_seconds):
        """Start a timer for background progress updates."""
        if estimated_seconds < 5:  # Only for tests estimated > 5 seconds
            return

        def progress_update():
            time.sleep(3)  # Wait 3 seconds before first update
            remaining = max(0, estimated_seconds - 3)
            if remaining > 2:
                print(f"⏳ {test_id} still running... (roughly {remaining}s remaining)")

        with self._lock:
            timer = threading.Timer(3.0, progress_update)
            timer.start()
            self._active_timers[test_id] = timer

    def stop_timer(self, test_id):
        """Stop progress timer for a test."""
        with self._lock:
            if test_id in self._active_timers:
                self._active_timers[test_id].cancel()
                del self._active_timers[test_id]

    def cleanup(self):
        """Clean up all active timers."""
        with self._lock:
            for timer in self._active_timers.values():
                timer.cancel()
            self._active_timers.clear()


# Global instance
_progress_reporter = ProgressReporter()


def pytest_sessionfinish(session, exitstatus):
    """Clean up progress timers at session end."""
    _progress_reporter.cleanup()


@pytest.fixture(scope="function")
def notify_user():
    """Provide access to progress reporter in tests."""
    return _progress_reporter
