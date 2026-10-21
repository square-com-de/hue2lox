"""Blocked bridge refreshes must not serialize local mutations or republish stale state."""
import threading
import unittest
from unittest.mock import patch
import dashboard

class DashboardConcurrencyTests(unittest.TestCase):
    def test_invalidation_is_prompt_and_stale_refresh_is_discarded(self):
        dashboard.invalidate()
        started=threading.Event();release=threading.Event();invalidated=threading.Event();errors=[]
        registry={'schema_version':1,'bridges':[{'id':'fixture','enabled':True,'lights':[{'id':'lamp','name':'Before'}]}]}
        def blocked(bridge):
            started.set()
            if not release.wait(3):raise RuntimeError('test did not release bridge')
            return {}
        def refresh():
            try:dashboard.overview()
            except ValueError as error:errors.append(str(error))
        with patch('dashboard.read_registry',return_value=registry),patch('dashboard.saved_miniserver',return_value=None),patch('dashboard.read_bridge_statuses',side_effect=blocked):
            worker=threading.Thread(target=refresh);worker.start()
            try:
                self.assertTrue(started.wait(1))
                def mutate():
                    dashboard.invalidate();invalidated.set()
                mutation=threading.Thread(target=mutate);mutation.start()
                self.assertTrue(invalidated.wait(.5),'local invalidation waited on network')
            finally:
                release.set();worker.join(3)
                if 'mutation' in locals():mutation.join(3)
            self.assertFalse(worker.is_alive())
            self.assertIsNone(dashboard.CACHE)
            self.assertEqual(errors,['overview changed during refresh; retry'])
            registry['bridges'][0]['lights'][0]['name']='After'
            result=dashboard.overview()
            self.assertEqual(result['bridges'][0]['lights'][0]['name'],'After')
            self.assertIs(result,dashboard.CACHE)
        dashboard.invalidate()

    def test_parallel_readers_share_one_refresh(self):
        dashboard.invalidate();barrier=threading.Barrier(5);results=[]
        def read():
            barrier.wait();results.append(dashboard.overview())
        registry={'schema_version':1,'bridges':[]}
        with patch('dashboard.read_registry',return_value=registry) as read_registry,patch('dashboard.saved_miniserver',return_value=None):
            workers=[threading.Thread(target=read) for _ in range(4)]
            for worker in workers:worker.start()
            barrier.wait()
            for worker in workers:worker.join(2)
            self.assertEqual(len(results),4);read_registry.assert_called_once()
            self.assertTrue(all(r is results[0] for r in results))
        dashboard.invalidate()
