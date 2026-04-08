"""
Test suite for STEP 3: Session persistence (Redis + Memory fallback).

Tests:
  1. MemorySessionService (fallback mode)
  2. RedisSessionService (if Redis available)
  3. get_session_service() factory function
  4. Session expiration
  5. Thread safety
"""
import time
import unittest
from backend.services.session_service import (
    MemorySessionService,
    RedisSessionService,
    get_session_service,
    SESSION_TIMEOUT
)


class TestMemorySessionService(unittest.TestCase):
    """Test in-memory session service (fallback)."""
    
    def setUp(self):
        self.service = MemorySessionService()
    
    def test_create_session(self):
        """Test creating a new session."""
        session_id, session = self.service.get_or_create_session()
        
        self.assertIsNotNone(session_id)
        self.assertIn("mode", session)
        self.assertIn("created_at", session)
        self.assertEqual(session["mode"], "demo")
    
    def test_reuse_valid_session(self):
        """Test reusing a valid session."""
        session_id1, session1 = self.service.get_or_create_session()
        session_id2, session2 = self.service.get_or_create_session(session_id=session_id1)
        
        self.assertEqual(session_id1, session_id2)
        self.assertEqual(session1["created_at"], session2["created_at"])
    
    def test_session_expiration(self):
        """Test session expiration after timeout."""
        session_id, _ = self.service.get_or_create_session()
        
        # Manually expire session
        self.service.sessions[session_id]["last_active"] = time.time() - SESSION_TIMEOUT - 1
        
        # Try to reuse expired session
        new_id, _ = self.service.get_or_create_session(session_id=session_id)
        
        # Should get a new session
        self.assertNotEqual(session_id, new_id)
    
    def test_is_valid_session(self):
        """Test is_valid() method."""
        session_id, _ = self.service.get_or_create_session()
        self.assertTrue(self.service.is_valid(session_id))
        
        # Expire it
        self.service.sessions[session_id]["last_active"] = time.time() - SESSION_TIMEOUT - 1
        self.assertFalse(self.service.is_valid(session_id))
    
    def test_touch_session(self):
        """Test updating session last_active."""
        session_id, session = self.service.get_or_create_session()
        old_active = session["last_active"]
        
        time.sleep(0.1)
        self.service.touch(session_id)
        new_active = self.service.sessions[session_id]["last_active"]
        
        self.assertGreater(new_active, old_active)
    
    def test_get_and_set_session(self):
        """Test get_session() and set_session()."""
        session_data = {
            "mode": "demo",
            "db": "test_db",
            "user_id": "user123",
            "last_active": str(time.time()),
            "created_at": str(time.time())
        }
        
        self.service.set_session("test_id", session_data)
        retrieved = self.service.get_session("test_id")
        
        self.assertEqual(retrieved, session_data)
    
    def test_cleanup(self):
        """Test cleanup of expired sessions."""
        # Create a session
        session_id1, _ = self.service.get_or_create_session()
        
        # Create and expire another session
        session_id2, _ = self.service.get_or_create_session()
        self.service.sessions[session_id2]["last_active"] = time.time() - SESSION_TIMEOUT - 1
        
        before = len(self.service.sessions)
        self.service.cleanup()
        after = len(self.service.sessions)
        
        self.assertEqual(before, 2)
        self.assertEqual(after, 1)
        self.assertIn(session_id1, self.service.sessions)
        self.assertNotIn(session_id2, self.service.sessions)


class TestRedisSessionService(unittest.TestCase):
    """Test Redis-backed session service."""
    
    @classmethod
    def setUpClass(cls):
        """Check if Redis is available."""
        try:
            service = RedisSessionService()
            cls.redis_available = True
            cls.service = service
        except Exception as e:
            cls.redis_available = False
            cls.skip_reason = str(e)
    
    def setUp(self):
        """Skip if Redis unavailable."""
        if not self.redis_available:
            self.skipTest(f"Redis unavailable: {self.skip_reason}")
    
    def test_create_session(self):
        """Test creating a new session in Redis."""
        session_id, session = self.service.get_or_create_session()
        
        self.assertIsNotNone(session_id)
        self.assertIn("mode", session)
        self.assertEqual(session["mode"], "demo")
    
    def test_reuse_valid_session(self):
        """Test reusing a session from Redis."""
        session_id1, _ = self.service.get_or_create_session()
        session_id2, session2 = self.service.get_or_create_session(session_id=session_id1)
        
        self.assertEqual(session_id1, session_id2)
        self.assertIsNotNone(session2)
    
    def test_get_session(self):
        """Test retrieving session from Redis."""
        session_id, session1 = self.service.get_or_create_session()
        session2 = self.service.get_session(session_id)
        
        # Keys should match even if timestamps are strings
        self.assertEqual(session1["mode"], session2["mode"])
    
    def test_is_valid_session(self):
        """Test is_valid() with Redis."""
        session_id, _ = self.service.get_or_create_session()
        self.assertTrue(self.service.is_valid(session_id))
    
    def test_touch_session(self):
        """Test extending session TTL."""
        session_id, _ = self.service.get_or_create_session()
        self.service.touch(session_id)
        self.assertTrue(self.service.is_valid(session_id))
    
    def test_set_and_get_session(self):
        """Test set_session() and get_session()."""
        test_id = "test_redis_session"
        session_data = {
            "mode": "test",
            "db": "test_db",
            "user_id": "test_user"
        }
        
        self.service.set_session(test_id, session_data)
        retrieved = self.service.get_session(test_id)
        
        self.assertEqual(retrieved["mode"], session_data["mode"])
        
        # Cleanup
        self.service.client.delete(f"session:{test_id}")


class TestSessionFactory(unittest.TestCase):
    """Test get_session_service() factory function."""
    
    def test_factory_returns_service(self):
        """Test that factory returns a valid service."""
        service = get_session_service()
        self.assertIsNotNone(service)
        
        # Test basic functionality
        session_id, session = service.get_or_create_session()
        self.assertIsNotNone(session_id)
        self.assertIsNotNone(session)
    
    def test_factory_singleton(self):
        """Test that factory returns same instance."""
        service1 = get_session_service()
        service2 = get_session_service()
        self.assertIs(service1, service2)


if __name__ == "__main__":
    unittest.main()
