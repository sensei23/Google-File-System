import threading


class ChunkLockManager:
    def __init__(self):
        self.locks = {}

    def acquire_lock(self, chunk_id, timeout=None):
        """Acquire a lock on the specified chunk."""
        lock = self.locks.get(chunk_id, threading.Lock())
        if lock.acquire(timeout=timeout):
            self.locks[chunk_id] = lock
            return True
        return False

    def release_lock(self, chunk_id):
        """Release the lock on the specified chunk."""
        lock = self.locks.get(chunk_id)
        if lock is not None and lock.locked():
            lock.release()
            del self.locks[chunk_id]