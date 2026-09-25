"""Exercise persistent decisions and local-only API boundaries with a disposable store."""
import json, tempfile, threading, unittest
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from server import make_server, Store

class ReviewDeskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.server,cls.store=make_server(0,Path(cls.tmp.name))
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'
        cls.catalog=cls.get('/api/catalog')
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.tmp.cleanup()
    @classmethod
    def get(cls,path):
        try:
            with urlopen(cls.base+path) as r:return json.load(r)
        except HTTPError as e:
            e.close();raise
    def post(self,payload,**headers):
        h={'Content-Type':'application/json','X-Review-Token':self.catalog['token'],**headers}
        req=Request(self.base+'/api/decision',json.dumps(payload).encode(),h)
        try:
            with urlopen(req) as r:return json.load(r)
        except HTTPError as e:
            e.close();raise
    def payload(self,id='P01'):
        item=next(i for i in self.catalog['items'] if i['id']==id)
        return dict(id=id,fingerprint=item['fingerprint'],revision=0,status='approved',comment='Test review only.',reviewer='Test reviewer')
    def test_1_save_reload_edit_and_export(self):
        p=self.payload();first=self.post(p)
        reloaded=Store(Path(self.tmp.name),self.store.items)
        self.assertEqual(reloaded.read()['decisions']['P01']['comment'],'Test review only.')
        p.update(revision=first['revision'],status='rejected',comment='Reconsider the inference.')
        second=self.post(p);self.assertEqual(second['revision'],2)
        export=self.get('/api/export')
        self.assertEqual(export['decisions']['P01']['status'],'rejected')
        self.assertEqual(len(export['history']),2)
        self.assertEqual(export['decisions']['P01']['item_snapshot']['kind'],'publication')
        self.assertEqual(export['stale_ids'],[])
    def test_2_outdated_tabs_do_not_overwrite(self):
        with self.assertRaises(HTTPError) as err:self.post(self.payload())
        self.assertEqual(err.exception.code,400)
        self.assertEqual(self.store.read()['decisions']['P01']['revision'],2)
    def test_3_invalid_decisions_and_stale_fingerprints(self):
        for updates in [{'fingerprint':'old-version'},{'status':'commented','comment':''},{'status':'publish'},{'id':'invented'}]:
            with self.assertRaises(HTTPError):self.post({**self.payload('P02'),**updates})
        self.assertNotIn('P02',self.store.read()['decisions'])
    def test_4_local_origin_and_session_token(self):
        for h in [{'Origin':'https://untrusted.example'},{'X-Review-Token':'bad'}]:
            with self.assertRaises(HTTPError) as err:self.post(self.payload('P02'),**h)
            self.assertEqual(err.exception.code,403)
    def test_5_catalog_and_original_source(self):
        self.assertEqual(sum(i['kind']=='claim' for i in self.catalog['items']),3715)
        self.assertEqual(sum(i['kind']=='transition' for i in self.catalog['items']),912)
        item=self.get('/api/item?id=C263-09')
        self.assertTrue(item['sources'][0]['hashMatches'])
        self.assertTrue(any('no deleted page was ever re-created' in l['text'] for l in item['sources'][0]['excerpt']))
        self.assertEqual(len(self.get('/api/report?id=C263')['excerpt']),111)
        self.assertTrue(self.get('/api/item?id=T-C276-C098-01')['sources'][1]['hashMatches'])
    def test_6_no_arbitrary_file_reads(self):
        with self.assertRaises(HTTPError) as e:self.get('/api/evidence?id=../../.env')
        self.assertEqual(e.exception.code,404)
        self.assertIn('facts',json.loads(self.get('/api/evidence?id=results%2Fcontested-record-checks.json')['text']))

if __name__=='__main__':unittest.main()
